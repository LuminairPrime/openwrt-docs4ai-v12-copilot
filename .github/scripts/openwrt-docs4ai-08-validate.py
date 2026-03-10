"""
Purpose: Strict CI/CD gatekeeper validating all documentation layers.
Phase: Validation
Layers: L1, L2, L3, L4, L5
Inputs: OUTDIR/
Outputs: Validation report to stdout
Environment Variables: OUTDIR, VALIDATE_MODE (hard/soft)
Dependencies: lib.config, pyyaml
Notes: Implements hard fails for 0-byte files, broken links, malformed YAML, and 404 HTML.
       Soft warnings for AST issues and token overflows.
"""

import os
import re
import yaml
import glob
import sys
import subprocess
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

RELATIVE_MD_LINK_RE = re.compile(
    r'\[[^\]\n]+\]\(((?!https?:\/\/|mailto:|[a-z0-9]+:)[^)\s]+?\.md(?:#[^)\s]+)?)\)',
    re.IGNORECASE,
)
UCODE_IMPORT_RE = re.compile(
    r"^\s*import(?:\s+(?:\*\s+as\s+[A-Za-z_][\w$]*|\{[^}]+\}|[A-Za-z_][\w$]*)(?:\s*,\s*(?:\{[^}]+\}|\*\s+as\s+[A-Za-z_][\w$]*))?\s+from)?\s+['\"]([^'\"]+)['\"]\s*;",
    re.MULTILINE,
)
UCODE_EXPORT_RE = re.compile(r'^\s*export\b', re.MULTILINE)
CODE_FENCE_START_RE = re.compile(r'^(\s*)```(javascript|ucode|js|uc)\s*$')
CODE_FENCE_END_RE = re.compile(r'^(\s*)```\s*$')


def extract_ucode_imports(code):
    return sorted(set(UCODE_IMPORT_RE.findall(code)))


def extract_markdown_code_blocks(content):
    blocks = []
    lines = content.splitlines()
    in_fence = False
    fence_indent = ''
    fence_language = ''
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
            fence_indent = ''
            fence_language = ''
            block_lines = []
            continue

        if fence_indent and line.startswith(fence_indent):
            block_lines.append(line[len(fence_indent):])
        else:
            block_lines.append(line)

    return blocks


def validate_outdir(outdir):
    hard_failures = []
    soft_warnings = []

    def hard_fail(msg):
        hard_failures.append(msg)
        print(f"[08] FAIL: {msg}")

    def soft_warn(msg):
        soft_warnings.append(msg)
        print(f"[08] WARN: {msg}")

    core_files = ["llms.txt", "llms-full.txt", "AGENTS.md", "README.md", "index.html"]
    for file_name in core_files:
        if not os.path.isfile(os.path.join(outdir, file_name)):
            hard_fail(f"Missing core L3 file: {file_name}")

    import json

    registry_path = os.path.join(outdir, "cross-link-registry.json")
    if os.path.isfile(registry_path):
        try:
            with open(registry_path, "r", encoding="utf-8") as file:
                reg = json.load(file)
            if "symbols" not in reg or "pipeline_date" not in reg:
                hard_fail("cross-link-registry.json missing core fields ('symbols', 'pipeline_date')")
        except Exception as exc:
            hard_fail(f"Could not parse cross-link-registry.json: {exc}")

    html_error_markers = [
        "<!DOCTYPE", "<html", "404 Not Found", "Access Denied", "captcha",
        "cloudflare", "captcha-delivery", "Just a moment...", "Checking your browser",
        "Rate limit exceeded", "Service Temporarily Unavailable"
    ]
    max_file_size_mb = 2.0

    all_md = glob.glob(os.path.join(outdir, "**", "*.md"), recursive=True)
    checked_count = 0
    skipped_ucode_ast_files = {}

    for fpath in all_md:
        rel = os.path.relpath(fpath, outdir)
        checked_count += 1

        f_size = os.path.getsize(fpath)
        if f_size == 0:
            hard_fail(f"0-byte file detected: {rel}")
            continue

        size_mb = f_size / (1024 * 1024)
        if size_mb > max_file_size_mb:
            hard_fail(f"Oversized file ({size_mb:.1f}MB): {rel}")
            continue

        try:
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()
        except UnicodeDecodeError:
            hard_fail(f"Non-UTF-8 content: {rel}")
            continue

        has_structural = "<!DOCTYPE" in content or "<html" in content
        if has_structural:
            for marker in html_error_markers:
                if marker in content[:500]:
                    hard_fail(f"HTML error/leak detected ({marker}): {rel}")
                    break

        if "L2-semantic" in rel:
            if not content.startswith("---"):
                hard_fail(f"Missing YAML frontmatter in L2: {rel}")
            else:
                try:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        yaml_data = yaml.safe_load(parts[1])
                        required = ["title", "module", "origin_type", "token_count", "version"]
                        for field in required:
                            if field not in yaml_data:
                                hard_fail(f"L2 YAML missing required field '{field}': {rel}")
                except Exception as exc:
                    hard_fail(f"Malformed YAML in L2: {rel} ({exc})")

            if '<a name="' in content:
                soft_warn(f"Raw HTML anchor tag leaked into L2: {rel}")

    for fpath in all_md:
        if "L2-semantic" not in fpath:
            continue

        rel_dir = os.path.dirname(fpath)
        with open(fpath, "r", encoding="utf-8") as file:
            content = file.read()

        for match in RELATIVE_MD_LINK_RE.finditer(content):
            link = match.group(1)
            target_file = link.split("#", 1)[0]
            target_path = os.path.normpath(os.path.join(rel_dir, target_file))
            if not os.path.isfile(target_path):
                hard_fail(f"Broken relative link in {os.path.relpath(fpath, outdir)}: {link}")

    full_txt_path = os.path.join(outdir, "llms-full.txt")
    if os.path.isfile(full_txt_path):
        with open(full_txt_path, "r", encoding="utf-8") as file:
            full_index = file.read()

        for fpath in all_md:
            if "L2-semantic" not in fpath:
                continue
            fname = os.path.basename(fpath)
            if fname not in full_index:
                soft_warn(f"L2 file missing from llms-full.txt index: {fname}")

    js_binary = shutil.which("node")
    ucode_binary = shutil.which("ucode")

    def check_ast(code, lang, rel_path):
        if lang == "javascript" and js_binary:
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w", encoding="utf-8") as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            res = subprocess.run([js_binary, "--check", tmp_path], capture_output=True, text=True)
            os.unlink(tmp_path)
            if res.returncode != 0:
                soft_warn(f"JS Syntax Error in {rel_path}: {res.stderr.strip()}")
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

            res = run_ucode_check(compile_flags)
            if (
                res.returncode != 0
                and "module" not in compile_flags
                and "return must be inside function body" in res.stderr
            ):
                res = run_ucode_check(["module", *compile_flags])

            os.unlink(tmp_path)
            if res.returncode != 0:
                soft_warn(f"uCode Syntax Error in {rel_path}: {res.stderr.strip()}")

    if js_binary or ucode_binary:
        for fpath in all_md:
            if "L2-semantic" not in fpath:
                continue
            rel = os.path.relpath(fpath, outdir)
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()

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

    print(f"\n[08] ----------------------------------------------")
    print(f"[08] Validation Results")
    print(f"[08]   Files Checked: {checked_count}")
    print(f"[08]   Hard Failures: {len(hard_failures)}")
    print(f"[08]   Soft Warnings: {len(soft_warnings)}")
    print(f"[08] ----------------------------------------------")

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
