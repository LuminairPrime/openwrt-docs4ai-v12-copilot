"""
Purpose: Strict CI/CD gatekeeper validating all documentation layers.
Phase: Validation
Layers: L1, L2, L3, L4, L5
Inputs: OUTDIR/
Outputs: Validation report to stdout
Environment Variables: OUTDIR, VALIDATE_MODE (hard/soft)
Dependencies: lib.config, pyyaml
Notes: Implements hard fails for 0-byte files, broken links, malformed YAML,
       missing routing entries, and leaked error HTML. Soft warnings remain for
       AST issues and residual cleanup signals that are useful but non-blocking.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

RELATIVE_MD_LINK_RE = re.compile(
    r"\[[^\]\n]+\]\(((?!https?:\/\/|mailto:|[a-z0-9]+:)[^)\s]+?\.md(?:#[^)\s]+)?)\)",
    re.IGNORECASE,
)
LLMS_ENTRY_RE = re.compile(
    r"^- \[(?P<label>[^\]\n]+)\]\((?P<link>[^)\n]+)\): (?P<tail>.+)$",
    re.MULTILINE,
)
UCODE_IMPORT_RE = re.compile(
    r"^\s*import(?:\s+(?:\*\s+as\s+[A-Za-z_][\w$]*|\{[^}]+\}|[A-Za-z_][\w$]*)(?:\s*,\s*(?:\{[^}]+\}|\*\s+as\s+[A-Za-z_][\w$]*))?\s+from)?\s+['\"]([^'\"]+)['\"]\s*;",
    re.MULTILINE,
)
UCODE_EXPORT_RE = re.compile(r"^\s*export\b", re.MULTILINE)
CODE_FENCE_START_RE = re.compile(r"^(\s*)```(javascript|ucode|js|uc)\s*$")
CODE_FENCE_END_RE = re.compile(r"^(\s*)```\s*$")
FENCED_BLOCK_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
WIKI_RESIDUAL_HTML_PATTERNS = {
    "raw html table": re.compile(r"<table\b|<tr\b|<td\b|<th\b", re.IGNORECASE),
    "sortable tag": re.compile(r"(?:\\?<\s*\/?sortable\b[^>]*\\?>|&lt;\/?sortable\b[^&]*&gt;)", re.IGNORECASE),
    "footnote aside": re.compile(r"<aside\b[^>]*\bfootnotes\b", re.IGNORECASE),
}
PLACEHOLDER_DESCRIPTIONS = {"description unavailable.", "no description"}


def extract_ucode_imports(code):
    return sorted(set(UCODE_IMPORT_RE.findall(code)))


def extract_markdown_code_blocks(content):
    blocks = []
    lines = content.splitlines()
    in_fence = False
    fence_indent = ""
    fence_language = ""
    block_lines = []

    for line in lines:
        if not in_fence:
            match = CODE_FENCE_START_RE.match(line)
            if not match:
                continue

            in_fence = True
            fence_indent = match.group(1)
            fence_language = match.group(2)
            block_lines = []
            continue

        match = CODE_FENCE_END_RE.match(line)
        if match and match.group(1) == fence_indent:
            blocks.append((fence_language, "\n".join(block_lines)))
            in_fence = False
            fence_indent = ""
            fence_language = ""
            block_lines = []
            continue

        if fence_indent and line.startswith(fence_indent):
            block_lines.append(line[len(fence_indent):])
        else:
            block_lines.append(line)

    return blocks


def strip_fenced_code_blocks(content):
    return FENCED_BLOCK_RE.sub("", content)


def parse_llms_entries(content):
    return [match.groupdict() for match in LLMS_ENTRY_RE.finditer(content)]


def expected_module_names(outdir):
    l2_root = os.path.join(outdir, "L2-semantic")
    if not os.path.isdir(l2_root):
        return []
    return sorted(
        name
        for name in os.listdir(l2_root)
        if os.path.isdir(os.path.join(l2_root, name))
        and glob.glob(os.path.join(l2_root, name, "*.md"))
    )


def warn_on_placeholder_descriptions(entries, source_label, soft_warn):
    for entry in entries:
        tail = entry.get("tail", "").casefold()
        for placeholder in PLACEHOLDER_DESCRIPTIONS:
            if placeholder in tail:
                soft_warn(f"Placeholder description in {source_label}: {entry.get('link', '')}")
                break


def validate_root_llms_contract(outdir, modules, hard_fail, soft_warn):
    path = os.path.join(outdir, "llms.txt")
    if not os.path.isfile(path):
        return

    content = open(path, "r", encoding="utf-8").read()
    if not content.startswith("# openwrt-docs4ai - LLM Routing Index"):
        hard_fail("Root llms.txt missing the expected routing-index title")
    if "[llms-full.txt](./llms-full.txt)" not in content:
        hard_fail("Root llms.txt missing the flat-catalog link")

    entries = parse_llms_entries(content)
    if not entries:
        hard_fail("Root llms.txt contains no parseable routing entries")
        return

    expected_module_links = {f"./{module}/llms.txt" for module in modules}
    actual_module_links = {
        entry["link"]
        for entry in entries
        if entry["link"].endswith("/llms.txt") and entry["link"] != "./llms-full.txt"
    }

    missing = sorted(expected_module_links - actual_module_links)
    if missing:
        hard_fail(f"Root llms.txt missing module routing entries: {', '.join(missing)}")

    warn_on_placeholder_descriptions(entries, "root llms.txt", soft_warn)


def validate_module_llms_contract(outdir, modules, hard_fail, soft_warn):
    for module in modules:
        module_dir = os.path.join(outdir, module)
        module_index_path = os.path.join(module_dir, "llms.txt")
        if not os.path.isfile(module_index_path):
            hard_fail(f"Missing module llms.txt: {module}/llms.txt")
            continue

        content = open(module_index_path, "r", encoding="utf-8").read()
        if not content.startswith(f"# {module} module"):
            hard_fail(f"Module llms.txt has unexpected title: {module}/llms.txt")
        if "> **Total Context:**" not in content:
            hard_fail(f"Module llms.txt missing total-context banner: {module}/llms.txt")
        if "## Source Documents" not in content:
            hard_fail(f"Module llms.txt missing Source Documents section: {module}/llms.txt")

        entries = parse_llms_entries(content)
        if not entries:
            hard_fail(f"Module llms.txt contains no parseable entries: {module}/llms.txt")
            continue

        actual_links = {entry["link"] for entry in entries}
        expected_source_links = {
            f"../L2-semantic/{module}/{os.path.basename(path)}"
            for path in glob.glob(os.path.join(outdir, "L2-semantic", module, "*.md"))
        }
        missing_source_links = sorted(expected_source_links - actual_links)
        if missing_source_links:
            hard_fail(
                f"Module llms.txt missing L2 source entries for {module}: {', '.join(missing_source_links)}"
            )

        recommended_expected = []
        for suffix in [f"{module}-skeleton.md", f"{module}-complete-reference.md"]:
            candidate = os.path.join(module_dir, suffix)
            if os.path.isfile(candidate):
                recommended_expected.append(f"./{suffix}")

        if recommended_expected and "## Recommended Entry Points" not in content:
            hard_fail(f"Module llms.txt missing Recommended Entry Points section: {module}/llms.txt")

        missing_recommended = sorted(link for link in recommended_expected if link not in actual_links)
        if missing_recommended:
            hard_fail(
                f"Module llms.txt missing recommended entry points for {module}: {', '.join(missing_recommended)}"
            )

        tooling_expected = [
            f"./{os.path.basename(path)}"
            for path in glob.glob(os.path.join(module_dir, "*.d.ts"))
        ]
        if tooling_expected and "## Tooling Surfaces" not in content:
            hard_fail(f"Module llms.txt missing Tooling Surfaces section: {module}/llms.txt")

        missing_tooling = sorted(link for link in tooling_expected if link not in actual_links)
        if missing_tooling:
            hard_fail(
                f"Module llms.txt missing tooling-surface entries for {module}: {', '.join(missing_tooling)}"
            )

        warn_on_placeholder_descriptions(entries, f"{module}/llms.txt", soft_warn)


def validate_llms_full_contract(outdir, modules, hard_fail, soft_warn):
    path = os.path.join(outdir, "llms-full.txt")
    if not os.path.isfile(path):
        return

    content = open(path, "r", encoding="utf-8").read()
    if not content.startswith("# openwrt-docs4ai - Complete Flat Catalog"):
        hard_fail("llms-full.txt missing the expected flat-catalog title")

    entries = parse_llms_entries(content)
    if not entries:
        hard_fail("llms-full.txt contains no parseable catalog entries")
        return

    actual_links = [entry["link"] for entry in entries]
    if len(actual_links) != len(set(actual_links)):
        hard_fail("llms-full.txt contains duplicate catalog links")

    expected_links = set()
    for root_name in ["AGENTS.md", "README.md"]:
        if os.path.isfile(os.path.join(outdir, root_name)):
            expected_links.add(f"./{root_name}")

    for module in modules:
        expected_links.add(f"./{module}/llms.txt")

        module_dir = os.path.join(outdir, module)
        for pattern in [f"{module}-skeleton.md", f"{module}-complete-reference.md", "*.d.ts"]:
            if "*" in pattern:
                for match in glob.glob(os.path.join(module_dir, pattern)):
                    expected_links.add(f"./{module}/{os.path.basename(match)}")
            else:
                candidate = os.path.join(module_dir, pattern)
                if os.path.isfile(candidate):
                    expected_links.add(f"./{module}/{pattern}")

        for l2_path in glob.glob(os.path.join(outdir, "L2-semantic", module, "*.md")):
            expected_links.add(f"./L2-semantic/{module}/{os.path.basename(l2_path)}")

    missing_links = sorted(expected_links - set(actual_links))
    if missing_links:
        hard_fail(f"llms-full.txt missing catalog entries: {', '.join(missing_links)}")

    warn_on_placeholder_descriptions(entries, "llms-full.txt", soft_warn)


def validate_agents_contract(outdir, hard_fail):
    path = os.path.join(outdir, "AGENTS.md")
    if not os.path.isfile(path):
        return

    content = open(path, "r", encoding="utf-8").read()
    required_markers = [
        "llms.txt",
        "llms-full.txt",
        "[module]/llms.txt",
        "*-skeleton.md",
        "*-complete-reference.md",
        "*.d.ts",
    ]
    missing = [marker for marker in required_markers if marker not in content]
    if missing:
        hard_fail(f"AGENTS.md missing routing guidance markers: {', '.join(missing)}")


def validate_outdir(outdir):
    hard_failures = []
    soft_warnings = []

    def hard_fail(message):
        hard_failures.append(message)
        print(f"[08] FAIL: {message}")

    def soft_warn(message):
        soft_warnings.append(message)
        print(f"[08] WARN: {message}")

    core_files = ["llms.txt", "llms-full.txt", "AGENTS.md", "README.md", "index.html"]
    for file_name in core_files:
        if not os.path.isfile(os.path.join(outdir, file_name)):
            hard_fail(f"Missing core L3 file: {file_name}")

    import json

    registry_path = os.path.join(outdir, "cross-link-registry.json")
    if os.path.isfile(registry_path):
        try:
            with open(registry_path, "r", encoding="utf-8") as handle:
                registry = json.load(handle)
            if "symbols" not in registry or "pipeline_date" not in registry:
                hard_fail("cross-link-registry.json missing core fields ('symbols', 'pipeline_date')")
        except Exception as exc:
            hard_fail(f"Could not parse cross-link-registry.json: {exc}")

    html_error_markers = [
        "<!DOCTYPE",
        "<html",
        "404 Not Found",
        "Access Denied",
        "captcha",
        "cloudflare",
        "captcha-delivery",
        "Just a moment...",
        "Checking your browser",
        "Rate limit exceeded",
        "Service Temporarily Unavailable",
    ]
    max_file_size_mb = 2.0

    all_md = glob.glob(os.path.join(outdir, "**", "*.md"), recursive=True)
    checked_count = 0
    skipped_ucode_ast_files = {}

    for fpath in all_md:
        rel = os.path.relpath(fpath, outdir)
        checked_count += 1

        file_size = os.path.getsize(fpath)
        if file_size == 0:
            hard_fail(f"0-byte file detected: {rel}")
            continue

        size_mb = file_size / (1024 * 1024)
        if size_mb > max_file_size_mb:
            hard_fail(f"Oversized file ({size_mb:.1f}MB): {rel}")
            continue

        try:
            with open(fpath, "r", encoding="utf-8") as handle:
                content = handle.read()
        except UnicodeDecodeError:
            hard_fail(f"Non-UTF-8 content: {rel}")
            continue

        has_structural_html = "<!DOCTYPE" in content or "<html" in content
        if has_structural_html:
            for marker in html_error_markers:
                if marker in content[:500]:
                    hard_fail(f"HTML error/leak detected ({marker}): {rel}")
                    break

        rel_normalized = rel.replace("\\", "/")
        if rel_normalized.startswith("L2-semantic/"):
            if not content.startswith("---"):
                hard_fail(f"Missing YAML frontmatter in L2: {rel}")
            else:
                try:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        yaml_data = yaml.safe_load(parts[1]) or {}
                        required_fields = ["title", "module", "origin_type", "token_count", "version"]
                        for field in required_fields:
                            if field not in yaml_data:
                                hard_fail(f"L2 YAML missing required field '{field}': {rel}")
                except Exception as exc:
                    hard_fail(f"Malformed YAML in L2: {rel} ({exc})")

            if '<a name="' in content:
                soft_warn(f"Raw HTML anchor tag leaked into L2: {rel}")

            if rel_normalized.startswith("L2-semantic/wiki/"):
                wiki_scan_content = strip_fenced_code_blocks(content)
                for label, pattern in WIKI_RESIDUAL_HTML_PATTERNS.items():
                    if pattern.search(wiki_scan_content):
                        soft_warn(f"Residual wiki HTML ({label}) leaked into L2: {rel}")

    for fpath in all_md:
        rel = os.path.relpath(fpath, outdir)
        rel_dir = os.path.dirname(fpath)
        with open(fpath, "r", encoding="utf-8") as handle:
            content = handle.read()

        for match in RELATIVE_MD_LINK_RE.finditer(content):
            link = match.group(1)
            target_file = link.split("#", 1)[0]
            target_path = os.path.normpath(os.path.join(rel_dir, target_file))
            if not os.path.isfile(target_path):
                hard_fail(f"Broken relative link in {rel}: {link}")

    modules = expected_module_names(outdir)
    validate_root_llms_contract(outdir, modules, hard_fail, soft_warn)
    validate_module_llms_contract(outdir, modules, hard_fail, soft_warn)
    validate_llms_full_contract(outdir, modules, hard_fail, soft_warn)
    validate_agents_contract(outdir, hard_fail)

    js_binary = shutil.which("node")
    ucode_binary = shutil.which("ucode")

    def check_ast(code, lang, rel_path):
        if lang == "javascript" and js_binary:
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w", encoding="utf-8") as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            result = subprocess.run([js_binary, "--check", tmp_path], capture_output=True, text=True)
            os.unlink(tmp_path)
            if result.returncode != 0:
                soft_warn(f"JS Syntax Error in {rel_path}: {result.stderr.strip()}")
        elif lang == "ucode" and ucode_binary:
            with tempfile.NamedTemporaryFile(suffix=".uc", delete=False, mode="w", encoding="utf-8") as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            compile_flags = []
            if UCODE_EXPORT_RE.search(code):
                compile_flags.append("module")
            compile_flags.extend(f"dynlink={module}" for module in extract_ucode_imports(code))

            def run_ucode_check(flags):
                compile_arg = "-c"
                if flags:
                    compile_arg += "," + ",".join(flags)
                return subprocess.run([ucode_binary, compile_arg, tmp_path], capture_output=True, text=True)

            result = run_ucode_check(compile_flags)
            if (
                result.returncode != 0
                and "module" not in compile_flags
                and "return must be inside function body" in result.stderr
            ):
                result = run_ucode_check(["module", *compile_flags])

            os.unlink(tmp_path)
            if result.returncode != 0:
                soft_warn(f"uCode Syntax Error in {rel_path}: {result.stderr.strip()}")

    if js_binary or ucode_binary:
        for fpath in all_md:
            rel = os.path.relpath(fpath, outdir)
            if "L2-semantic" not in rel:
                continue

            with open(fpath, "r", encoding="utf-8") as handle:
                content = handle.read()

            blocks = extract_markdown_code_blocks(content)
            for lang, code in blocks:
                normalized_lang = "javascript" if lang in ["js", "javascript"] else "ucode"
                if normalized_lang == "ucode" and not ucode_binary:
                    skipped_ucode_ast_files[rel] = skipped_ucode_ast_files.get(rel, 0) + 1
                    continue
                check_ast(code, normalized_lang, rel)

    if skipped_ucode_ast_files:
        skipped_blocks = sum(skipped_ucode_ast_files.values())
        soft_warn(
            "uCode syntax validation skipped for "
            f"{skipped_blocks} code block(s) across {len(skipped_ucode_ast_files)} file(s): "
            "'ucode' binary not found in PATH"
        )

    return checked_count, hard_failures, soft_warnings


def main(argv=None):
    argv = argv or sys.argv[1:]
    outdir = os.environ.get("OUTDIR", config.OUTDIR)
    validate_mode = os.environ.get("VALIDATE_MODE", "hard").lower()
    if "--warn-only" in argv:
        validate_mode = "soft"

    print(f"[08] Security & Quality Validation ({outdir}) [Mode: {validate_mode}]")
    checked_count, hard_failures, soft_warnings = validate_outdir(outdir)

    print("\n[08] ----------------------------------------------")
    print("[08] Validation Results")
    print(f"[08]   Files Checked: {checked_count}")
    print(f"[08]   Hard Failures: {len(hard_failures)}")
    print(f"[08]   Soft Warnings: {len(soft_warnings)}")
    print("[08] ----------------------------------------------")

    if hard_failures:
        print("\n[08] BLOCKING FAILURES:")
        for failure in hard_failures:
            print(f"  X {failure}")

        if validate_mode == "hard":
            return 1
        print("[08] INFO: Continuing despite failures due to VALIDATE_MODE=soft")

    if soft_warnings:
        print("\n[08] NON-BLOCKING WARNINGS:")
        for warning in soft_warnings:
            print(f"  ! {warning}")

    print("\n[08] Validation pass complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())