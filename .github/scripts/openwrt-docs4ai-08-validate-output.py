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
from urllib.parse import unquote

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
HTML_HREF_RE = re.compile(
    r'<a\b[^>]*\bhref=["\']([^"\']+)["\']',
    re.IGNORECASE,
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
KNOWN_UCODE_FALSE_POSITIVES = {
    (
        "L2-semantic/luci-examples/example_app-luci-app-dockerman-root-usr-share-rpcd-ucode-docker-rpc-uc.md",
        "return must be inside function body",
    ),
}


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


def summarize_paths(paths, limit=5):
    """Return a short comma-separated preview for failure messages."""
    preview = list(paths[:limit])
    if len(paths) > limit:
        preview.append(f"... (+{len(paths) - limit} more)")
    return ", ".join(preview)


def expected_publish_links(outdir):
    """Return the set of files that the HTML mirror index must expose."""
    links = set()
    excluded_dirs = {
        os.path.basename(config.RELEASE_TREE_DIR),
        os.path.basename(config.SUPPORT_TREE_DIR),
    }

    for root, _dirs, files in os.walk(outdir):
        if excluded_dirs:
            _dirs[:] = [name for name in _dirs if name not in excluded_dirs]
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), outdir).replace("\\", "/")
            links.add(rel)
    return links


def expected_release_publish_links(release_tree_dir):
    """Return the set of files that the release-tree HTML index must expose."""
    links = set()
    for root, _dirs, files in os.walk(release_tree_dir):
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), release_tree_dir)
            links.add(rel.replace("\\", "/"))
    return links


def normalize_html_href(href):
    """Normalize a local HTML href into an OUTDIR-relative path."""
    target = href.split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "/")):
        return None
    normalized = os.path.normpath(unquote(target)).replace("\\", "/")
    if normalized in {"", "."}:
        return None
    if normalized == ".." or normalized.startswith("../"):
        return normalized
    return normalized.lstrip("./")


def validate_index_html_contract(outdir, hard_fail):
    """Ensure index.html mirrors the published filesystem tree."""
    path = os.path.join(outdir, "index.html")
    if not os.path.isfile(path):
        return

    content = open(path, "r", encoding="utf-8").read()
    if "./openwrt-condensed-docs/" not in content:
        hard_fail("index.html missing the mirrored display-path prefix")

    actual_links = {
        normalized
        for href in HTML_HREF_RE.findall(content)
        if (normalized := normalize_html_href(href)) is not None
    }
    expected_links = expected_publish_links(outdir)

    missing_links = sorted(expected_links - actual_links)
    if missing_links:
        hard_fail(
            "index.html missing mirrored publish links: "
            f"{summarize_paths(missing_links)}"
        )

    unexpected_links = sorted(actual_links - expected_links)
    if unexpected_links:
        hard_fail(
            "index.html contains hrefs outside the publish tree: "
            f"{summarize_paths(unexpected_links)}"
        )


def validate_release_index_html_contract(release_tree_dir, hard_fail):
    """Ensure release-tree/index.html mirrors the direct release filesystem."""
    path = os.path.join(release_tree_dir, "index.html")
    if not os.path.isfile(path):
        return

    content = open(path, "r", encoding="utf-8").read()
    if "./openwrt-condensed-docs/" in content:
        hard_fail("release-tree index.html leaks the legacy display-path prefix")

    actual_links = {
        normalized
        for href in HTML_HREF_RE.findall(content)
        if (normalized := normalize_html_href(href)) is not None
    }
    expected_links = expected_release_publish_links(release_tree_dir)

    missing_links = sorted(expected_links - actual_links)
    if missing_links:
        hard_fail(
            "release-tree index.html missing mirrored publish links: "
            f"{summarize_paths(missing_links)}"
        )

    unexpected_links = sorted(actual_links - expected_links)
    if unexpected_links:
        hard_fail(
            "release-tree index.html contains hrefs outside the publish tree: "
            f"{summarize_paths(unexpected_links)}"
        )


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


def expected_release_module_names(release_tree_dir):
    if not os.path.isdir(release_tree_dir):
        return []
    return sorted(
        name
        for name in os.listdir(release_tree_dir)
        if os.path.isdir(os.path.join(release_tree_dir, name))
        and os.path.isfile(os.path.join(release_tree_dir, name, "llms.txt"))
    )


def relative_file_set(root_dir):
    if not os.path.isdir(root_dir):
        return set()
    return {
        os.path.relpath(os.path.join(root, file_name), root_dir).replace("\\", "/")
        for root, _dirs, files in os.walk(root_dir)
        for file_name in files
    }


def validate_mirrored_tree(source_dir, mirror_dir, label, hard_fail):
    if not os.path.isdir(source_dir):
        hard_fail(f"missing staged source directory for support-tree mirror: {label}")
        return

    source_files = relative_file_set(source_dir)
    mirror_files = relative_file_set(mirror_dir)

    missing_files = sorted(source_files - mirror_files)
    extra_files = sorted(mirror_files - source_files)
    if missing_files:
        hard_fail(
            f"support-tree {label} missing mirrored files: {summarize_paths(missing_files)}"
        )
    if extra_files:
        hard_fail(
            f"support-tree {label} contains unexpected files: {summarize_paths(extra_files)}"
        )

    for rel_path in sorted(source_files & mirror_files):
        source_path = os.path.join(source_dir, rel_path)
        mirror_path = os.path.join(mirror_dir, rel_path)
        with open(source_path, "rb") as source_handle:
            source_bytes = source_handle.read()
        with open(mirror_path, "rb") as mirror_handle:
            mirror_bytes = mirror_handle.read()
        if source_bytes != mirror_bytes:
            hard_fail(f"support-tree {label} content mismatch: {rel_path}")


def validate_mirrored_file(source_path, mirror_path, label, hard_fail):
    if not os.path.isfile(source_path):
        hard_fail(f"missing staged source file for support-tree mirror: {label}")
        return
    if not os.path.isfile(mirror_path):
        hard_fail(f"support-tree missing mirrored file: {label}")
        return

    with open(source_path, "rb") as source_handle:
        source_bytes = source_handle.read()
    with open(mirror_path, "rb") as mirror_handle:
        mirror_bytes = mirror_handle.read()
    if source_bytes != mirror_bytes:
        hard_fail(f"support-tree content mismatch: {label}")


def validate_release_tree_contract(outdir, hard_fail, soft_warn):
    release_tree_name = os.path.basename(config.RELEASE_TREE_DIR)
    support_tree_name = os.path.basename(config.SUPPORT_TREE_DIR)
    release_tree_dir = os.path.join(outdir, release_tree_name)
    if not os.path.isdir(release_tree_dir):
        hard_fail(f"Release tree not present: {release_tree_name}")
        return

    required_root_files = ["README.md", "AGENTS.md", "llms.txt", "llms-full.txt", "index.html"]
    for file_name in required_root_files:
        path = os.path.join(release_tree_dir, file_name)
        if not os.path.isfile(path):
            hard_fail(f"release-tree missing root file: {release_tree_name}/{file_name}")

    root_llms_path = os.path.join(release_tree_dir, "llms.txt")
    if os.path.isfile(root_llms_path) and os.path.getsize(root_llms_path) <= 512:
        hard_fail("release-tree root llms.txt is unexpectedly small")

    expected_modules = expected_module_names(outdir)
    modules = expected_release_module_names(release_tree_dir)
    if len(modules) < 4:
        hard_fail(f"release-tree expected at least 4 module directories, found {len(modules)}")
    if expected_modules and modules != expected_modules:
        missing_modules = sorted(set(expected_modules) - set(modules))
        extra_modules = sorted(set(modules) - set(expected_modules))
        details = []
        if missing_modules:
            details.append(f"missing: {', '.join(missing_modules)}")
        if extra_modules:
            details.append(f"unexpected: {', '.join(extra_modules)}")
        hard_fail(f"release-tree module set mismatch ({'; '.join(details)})")

    legacy_dir_hits = []
    legacy_file_hits = []
    support_only_file_hits = []
    support_only_files = {
        "cross-link-registry.json",
        "repo-manifest.json",
        "CHANGES.md",
        "changelog.json",
        "signature-inventory.json",
    }
    for root, dirs, files in os.walk(release_tree_dir):
        for dir_name in dirs:
            if dir_name in {"L1-raw", "L2-semantic", "openwrt-condensed-docs", support_tree_name}:
                rel = os.path.relpath(os.path.join(root, dir_name), release_tree_dir)
                legacy_dir_hits.append(rel.replace("\\", "/"))
        for file_name in files:
            if file_name.endswith("-skeleton.md") or file_name.endswith("-complete-reference.md"):
                rel = os.path.relpath(os.path.join(root, file_name), release_tree_dir)
                legacy_file_hits.append(rel.replace("\\", "/"))
            if file_name in support_only_files:
                rel = os.path.relpath(os.path.join(root, file_name), release_tree_dir)
                support_only_file_hits.append(rel.replace("\\", "/"))

    if legacy_dir_hits:
        hard_fail(
            "release-tree contains legacy path names: "
            f"{summarize_paths(sorted(legacy_dir_hits))}"
        )
    if legacy_file_hits:
        hard_fail(
            "release-tree contains legacy file names: "
            f"{summarize_paths(sorted(legacy_file_hits))}"
        )
    if support_only_file_hits:
        hard_fail(
            "release-tree contains support-only artifacts: "
            f"{summarize_paths(sorted(support_only_file_hits))}"
        )

    for file_name in required_root_files:
        path = os.path.join(release_tree_dir, file_name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
        if "openwrt-condensed-docs" in content:
            hard_fail(f"release-tree root file leaks legacy name: {release_tree_name}/{file_name}")

    for module in modules:
        module_dir = os.path.join(release_tree_dir, module)
        required_module_paths = [
            ("llms.txt", os.path.isfile),
            (config.MODULE_MAP_FILENAME, os.path.isfile),
            (config.MODULE_BUNDLED_REF_FILENAME, os.path.isfile),
            (config.MODULE_CHUNKED_REF_DIRNAME, os.path.isdir),
        ]
        for name, predicate in required_module_paths:
            path = os.path.join(module_dir, name)
            if not predicate(path):
                hard_fail(f"release-tree missing module path: {module}/{name}")

        chunked_dir = os.path.join(module_dir, config.MODULE_CHUNKED_REF_DIRNAME)
        if os.path.isdir(chunked_dir) and not glob.glob(os.path.join(chunked_dir, "*.md")):
            hard_fail(
                "release-tree chunked-reference is empty: "
                f"{module}/{config.MODULE_CHUNKED_REF_DIRNAME}"
            )

        module_llms_path = os.path.join(module_dir, "llms.txt")
        if os.path.isfile(module_llms_path):
            with open(module_llms_path, "r", encoding="utf-8") as handle:
                content = handle.read()
            legacy_markers = [
                f"{module}-skeleton.md",
                f"{module}-complete-reference.md",
                f"../L2-semantic/{module}/",
            ]
            leaked = [marker for marker in legacy_markers if marker in content]
            if leaked:
                hard_fail(
                    f"release-tree module llms.txt leaks legacy links for {module}: "
                    f"{', '.join(leaked)}"
                )

    validate_root_llms_contract(release_tree_dir, modules, hard_fail, soft_warn)
    validate_release_module_llms_contract(
        release_tree_dir,
        modules,
        hard_fail,
        soft_warn,
    )
    validate_release_llms_full_contract(
        release_tree_dir,
        modules,
        hard_fail,
        soft_warn,
    )
    validate_release_agents_contract(release_tree_dir, hard_fail)
    validate_release_index_html_contract(release_tree_dir, hard_fail)


def validate_support_tree_contract(outdir, hard_fail, soft_warn):
    support_tree_name = os.path.basename(config.SUPPORT_TREE_DIR)
    support_tree_dir = os.path.join(outdir, support_tree_name)
    if not os.path.isdir(support_tree_dir):
        hard_fail(f"Support tree not present: {support_tree_name}")
        return

    required_dirs = ["raw", "semantic-pages", "manifests", "telemetry"]
    for dir_name in required_dirs:
        path = os.path.join(support_tree_dir, dir_name)
        if not os.path.isdir(path):
            hard_fail(f"support-tree missing directory: {support_tree_name}/{dir_name}")

    raw_dir = os.path.join(support_tree_dir, "raw")
    staged_raw_dir = os.path.join(outdir, "L1-raw")
    if os.path.isdir(raw_dir):
        raw_docs = glob.glob(os.path.join(raw_dir, "**", "*.md"), recursive=True)
        if not raw_docs:
            hard_fail("support-tree raw/ contains no markdown files")
    validate_mirrored_tree(staged_raw_dir, raw_dir, "raw/", hard_fail)

    semantic_dir = os.path.join(support_tree_dir, "semantic-pages")
    staged_semantic_dir = os.path.join(outdir, "L2-semantic")
    if os.path.isdir(semantic_dir):
        semantic_docs = glob.glob(os.path.join(semantic_dir, "**", "*.md"), recursive=True)
        if not semantic_docs:
            hard_fail("support-tree semantic-pages/ contains no markdown files")
    validate_mirrored_tree(staged_semantic_dir, semantic_dir, "semantic-pages/", hard_fail)

    required_manifest_files = ["cross-link-registry.json", "repo-manifest.json"]

    for file_name in required_manifest_files:
        path = os.path.join(support_tree_dir, "manifests", file_name)
        if not os.path.isfile(path):
            hard_fail(f"support-tree missing manifest file: {support_tree_name}/manifests/{file_name}")
        validate_mirrored_file(
            os.path.join(outdir, file_name),
            path,
            f"manifests/{file_name}",
            hard_fail,
        )

    required_telemetry_files = ["CHANGES.md", "changelog.json", "signature-inventory.json"]
    for file_name in required_telemetry_files:
        support_path = os.path.join(support_tree_dir, "telemetry", file_name)
        if not os.path.isfile(support_path):
            hard_fail(f"support-tree missing telemetry file: {support_tree_name}/telemetry/{file_name}")
        validate_mirrored_file(
            os.path.join(outdir, file_name),
            support_path,
            f"telemetry/{file_name}",
            hard_fail,
        )


def warn_on_placeholder_descriptions(entries, source_label, soft_warn):
    for entry in entries:
        tail = entry.get("tail", "").casefold()
        for placeholder in PLACEHOLDER_DESCRIPTIONS:
            if placeholder in tail:
                soft_warn(f"Placeholder description in {source_label}: {entry.get('link', '')}")
                break


def is_known_ucode_false_positive(rel_path, stderr_text):
    """Return True for one exact upstream ucode AST false positive we accept."""
    normalized_path = rel_path.replace("\\", "/")
    normalized_stderr = (stderr_text or "").strip()
    for expected_path, expected_fragment in KNOWN_UCODE_FALSE_POSITIVES:
        if normalized_path == expected_path and expected_fragment in normalized_stderr:
            return True
    return False


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
        for match in glob.glob(
            os.path.join(module_dir, f"{module}-complete-reference.part-*.md")
        ):
            recommended_expected.append(f"./{os.path.basename(match)}")

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


def validate_release_module_llms_contract(
    release_tree_dir,
    modules,
    hard_fail,
    soft_warn,
):
    for module in modules:
        module_dir = os.path.join(release_tree_dir, module)
        module_index_path = os.path.join(module_dir, "llms.txt")
        if not os.path.isfile(module_index_path):
            hard_fail(f"Missing release-tree module llms.txt: {module}/llms.txt")
            continue

        content = open(module_index_path, "r", encoding="utf-8").read()
        if not content.startswith(f"# {module} module"):
            hard_fail(
                f"release-tree module llms.txt has unexpected title: {module}/llms.txt"
            )
        if "> **Total Context:**" not in content:
            hard_fail(
                f"release-tree module llms.txt missing total-context banner: {module}/llms.txt"
            )
        if "## Source Documents" not in content:
            hard_fail(
                f"release-tree module llms.txt missing Source Documents section: {module}/llms.txt"
            )

        entries = parse_llms_entries(content)
        if not entries:
            hard_fail(
                f"release-tree module llms.txt contains no parseable entries: {module}/llms.txt"
            )
            continue

        actual_links = {entry["link"] for entry in entries}
        expected_source_links = {
            f"./{config.MODULE_CHUNKED_REF_DIRNAME}/{os.path.basename(path)}"
            for path in glob.glob(
                os.path.join(
                    module_dir,
                    config.MODULE_CHUNKED_REF_DIRNAME,
                    "*.md",
                )
            )
        }
        missing_source_links = sorted(expected_source_links - actual_links)
        if missing_source_links:
            hard_fail(
                "release-tree module llms.txt missing source entries for "
                f"{module}: {', '.join(missing_source_links)}"
            )

        recommended_expected = []
        for file_name in [
            config.MODULE_MAP_FILENAME,
            config.MODULE_BUNDLED_REF_FILENAME,
        ]:
            candidate = os.path.join(module_dir, file_name)
            if os.path.isfile(candidate):
                recommended_expected.append(f"./{file_name}")
        for match in glob.glob(
            os.path.join(
                module_dir,
                config.MODULE_BUNDLED_REF_FILENAME.removesuffix(".md") + ".part-*.md",
            )
        ):
            recommended_expected.append(f"./{os.path.basename(match)}")

        if recommended_expected and "## Recommended Entry Points" not in content:
            hard_fail(
                "release-tree module llms.txt missing Recommended Entry Points "
                f"section: {module}/llms.txt"
            )

        missing_recommended = sorted(
            link for link in recommended_expected if link not in actual_links
        )
        if missing_recommended:
            hard_fail(
                "release-tree module llms.txt missing recommended entry points "
                f"for {module}: {', '.join(missing_recommended)}"
            )

        tooling_expected = [
            f"./{config.MODULE_TYPES_DIRNAME}/{os.path.basename(path)}"
            for path in glob.glob(
                os.path.join(
                    module_dir,
                    config.MODULE_TYPES_DIRNAME,
                    "*.d.ts",
                )
            )
        ]
        if tooling_expected and "## Tooling Surfaces" not in content:
            hard_fail(
                f"release-tree module llms.txt missing Tooling Surfaces section: {module}/llms.txt"
            )

        missing_tooling = sorted(
            link for link in tooling_expected if link not in actual_links
        )
        if missing_tooling:
            hard_fail(
                "release-tree module llms.txt missing tooling-surface entries "
                f"for {module}: {', '.join(missing_tooling)}"
            )

        warn_on_placeholder_descriptions(
            entries,
            f"release-tree/{module}/llms.txt",
            soft_warn,
        )


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

        for match in glob.glob(
            os.path.join(module_dir, f"{module}-complete-reference.part-*.md")
        ):
            expected_links.add(f"./{module}/{os.path.basename(match)}")

        for l2_path in glob.glob(os.path.join(outdir, "L2-semantic", module, "*.md")):
            expected_links.add(f"./L2-semantic/{module}/{os.path.basename(l2_path)}")

    missing_links = sorted(expected_links - set(actual_links))
    if missing_links:
        hard_fail(f"llms-full.txt missing catalog entries: {', '.join(missing_links)}")

    warn_on_placeholder_descriptions(entries, "llms-full.txt", soft_warn)


def validate_release_llms_full_contract(
    release_tree_dir,
    modules,
    hard_fail,
    soft_warn,
):
    path = os.path.join(release_tree_dir, "llms-full.txt")
    if not os.path.isfile(path):
        return

    content = open(path, "r", encoding="utf-8").read()
    if not content.startswith("# openwrt-docs4ai - Complete Flat Catalog"):
        hard_fail("release-tree llms-full.txt missing the expected flat-catalog title")

    entries = parse_llms_entries(content)
    if not entries:
        hard_fail("release-tree llms-full.txt contains no parseable catalog entries")
        return

    actual_links = [entry["link"] for entry in entries]
    if len(actual_links) != len(set(actual_links)):
        hard_fail("release-tree llms-full.txt contains duplicate catalog links")

    expected_links = set()
    for root_name in ["AGENTS.md", "README.md"]:
        if os.path.isfile(os.path.join(release_tree_dir, root_name)):
            expected_links.add(f"./{root_name}")

    for module in modules:
        expected_links.add(f"./{module}/llms.txt")

        module_dir = os.path.join(release_tree_dir, module)
        for file_name in [
            config.MODULE_MAP_FILENAME,
            config.MODULE_BUNDLED_REF_FILENAME,
        ]:
            candidate = os.path.join(module_dir, file_name)
            if os.path.isfile(candidate):
                expected_links.add(f"./{module}/{file_name}")

        for match in glob.glob(
            os.path.join(
                module_dir,
                config.MODULE_BUNDLED_REF_FILENAME.removesuffix(".md") + ".part-*.md",
            )
        ):
            expected_links.add(f"./{module}/{os.path.basename(match)}")

        for match in glob.glob(
            os.path.join(
                module_dir,
                config.MODULE_TYPES_DIRNAME,
                "*.d.ts",
            )
        ):
            expected_links.add(
                f"./{module}/{config.MODULE_TYPES_DIRNAME}/{os.path.basename(match)}"
            )

        for chunk_path in glob.glob(
            os.path.join(
                module_dir,
                config.MODULE_CHUNKED_REF_DIRNAME,
                "*.md",
            )
        ):
            expected_links.add(
                f"./{module}/{config.MODULE_CHUNKED_REF_DIRNAME}/{os.path.basename(chunk_path)}"
            )

    missing_links = sorted(expected_links - set(actual_links))
    if missing_links:
        hard_fail(
            "release-tree llms-full.txt missing catalog entries: "
            f"{', '.join(missing_links)}"
        )

    warn_on_placeholder_descriptions(
        entries,
        "release-tree/llms-full.txt",
        soft_warn,
    )


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


def validate_release_agents_contract(release_tree_dir, hard_fail):
    path = os.path.join(release_tree_dir, "AGENTS.md")
    if not os.path.isfile(path):
        return

    content = open(path, "r", encoding="utf-8").read()
    required_markers = [
        "llms.txt",
        "llms-full.txt",
        "[module]/llms.txt",
        config.MODULE_MAP_FILENAME,
        config.MODULE_BUNDLED_REF_FILENAME,
        f"{config.MODULE_CHUNKED_REF_DIRNAME}/",
        f"{config.MODULE_TYPES_DIRNAME}/*.d.ts",
    ]
    missing = [marker for marker in required_markers if marker not in content]
    if missing:
        hard_fail(
            "release-tree AGENTS.md missing routing guidance markers: "
            f"{', '.join(missing)}"
        )


def validate_outdir(outdir):
    hard_failures = []
    soft_warnings = []

    def hard_fail(message):
        hard_failures.append(message)
        print(f"[08] FAIL: {message}")

    def soft_warn(message):
        soft_warnings.append(message)
        print(f"[08] WARN: {message}")

    core_files = [
        "llms.txt",
        "llms-full.txt",
        "AGENTS.md",
        "README.md",
        "index.html",
        "repo-manifest.json",
        "cross-link-registry.json",
        "signature-inventory.json",
        "CHANGES.md",
        "changelog.json",
    ]
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
    validate_index_html_contract(outdir, hard_fail)
    validate_support_tree_contract(outdir, hard_fail, soft_warn)
    validate_release_tree_contract(outdir, hard_fail, soft_warn)

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
                if is_known_ucode_false_positive(rel_path, result.stderr):
                    return
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