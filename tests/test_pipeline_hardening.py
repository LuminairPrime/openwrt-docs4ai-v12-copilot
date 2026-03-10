import importlib.util
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".github" / "scripts"
WIKI_L2_DIR = PROJECT_ROOT / "openwrt-condensed-docs" / "L2-semantic" / "wiki"

WIKI_ARTIFACT_PATTERNS = {
    "wrap": re.compile(r"(?:\\<|&lt;|<)\s*/?wrap\b", re.IGNORECASE),
    "color": re.compile(r"(?:\\<|&lt;|<)\s*/?color\b", re.IGNORECASE),
    "html_table": re.compile(r"<table|<tr\b|<td\b|<th\b", re.IGNORECASE),
}


def load_script_module(module_name, script_name):
    script_path = SCRIPTS_DIR / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def summarize_wiki_l2_corpus(corpus_dir):
    files = sorted(corpus_dir.glob("*.md"))
    summary = {
        "files": len(files),
        "wrap_files": 0,
        "wrap_occurrences": 0,
        "color_files": 0,
        "color_occurrences": 0,
        "html_table_files": 0,
        "html_table_occurrences": 0,
        "duplicate_lead_heading_files": 0,
    }

    for markdown_file in files:
        content = markdown_file.read_text(encoding="utf-8")
        for key, pattern in WIKI_ARTIFACT_PATTERNS.items():
            matches = pattern.findall(content)
            if matches:
                summary[f"{key}_files"] += 1
                summary[f"{key}_occurrences"] += len(matches)
        if has_duplicate_lead_heading(content):
            summary["duplicate_lead_heading_files"] += 1

    return summary


def has_duplicate_lead_heading(content):
    top_heading = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            top_heading = stripped[2:].strip().casefold()
            continue
        if stripped.startswith("## "):
            return stripped[3:].strip().casefold() == top_heading
        return False
    return False


def classify_wiki_l2_sanity(summary):
    if summary["files"] < 80:
        return "abnormal"
    if summary["duplicate_lead_heading_files"] > 0:
        return "abnormal"
    if summary["wrap_files"] > 25:
        return "abnormal"
    if summary["color_files"] > 12:
        return "abnormal"
    if summary["html_table_files"] > 15:
        return "abnormal"
    if summary["wrap_files"] or summary["color_files"] or summary["html_table_files"]:
        return "bounded-stale"
    return "clean"


def test_ucode_normalize_fenced_blocks_classifies_shell_json_and_pseudocode():
    ucode = load_script_module("ucode_scraper", "openwrt-docs4ai-02b-scrape-ucode.py")

    markdown = (
        "```\n"
        "$ echo hello\n"
        "```\n\n"
        "```\n"
        "{\n"
        '  "name": "demo"\n'
        "}\n"
        "```\n\n"
        "```\n"
        "listener(…)\n"
        "```\n"
    )

    normalized = ucode.normalize_fenced_blocks(markdown, "ucode")

    assert "```bash" in normalized
    assert "```json" in normalized
    assert "```text" in normalized


def test_ucode_fix_known_issues_rewrites_nl80211_named_const_import():
    ucode = load_script_module("ucode_scraper_fixups", "openwrt-docs4ai-02b-scrape-ucode.py")

    source = (
        "import { error, request, listener, waitfor, const } from 'nl80211';\n"
        "let response = request(cmd);\n"
        "let wifiListener = listener(mask);\n"
        "let event = waitfor(wifiListener);\n"
        "return const.NL80211_CMD_GET_INTERFACE;\n"
    )

    fixed = ucode.fix_known_ucode_example_issues(source)

    assert "import * as nl80211 from 'nl80211';" in fixed
    assert "nl80211.request(cmd)" in fixed
    assert "nl80211.listener(mask)" in fixed
    assert "nl80211.waitfor(wifiListener)" in fixed
    assert "nl80211.const.NL80211_CMD_GET_INTERFACE" in fixed


def test_clean_wiki_semantic_content_strips_wrap_color_and_duplicate_rows():
    normalize = load_script_module("normalize_semantic", "openwrt-docs4ai-03-normalize-semantic.py")

    raw = (
        "# The Bootloader\n\n"
        "\\<WRAP round tip\\> Being firmware, \\<color red\\>**bootloader code matters**\\</color\\>.\\</WRAP\\>\n\n"
        "<table>\n"
        "<tbody>\n"
        "<tr class=\"odd\">\n"
        "<td>A</td>\n"
        "</tr>\n"
        "<tr class=\"odd\">\n"
        "<td>A</td>\n"
        "</tr>\n"
        "</tbody>\n"
        "</table>\n"
    )

    cleaned = normalize.clean_wiki_semantic_content("The Bootloader", raw)

    assert "WRAP" not in cleaned
    assert "color red" not in cleaned
    assert "**bootloader code matters**" in cleaned
    assert cleaned.count('<tr class="odd">') == 1


def test_clean_wiki_semantic_content_removes_immediate_duplicate_heading():
    normalize = load_script_module("normalize_semantic_headings", "openwrt-docs4ai-03-normalize-semantic.py")

    raw = "# Adding new elements to LuCI\n\n## Adding new elements to LuCI\n\nBody text.\n"

    cleaned = normalize.clean_wiki_semantic_content("Adding new elements to LuCI", raw)

    assert cleaned.count("Adding new elements to LuCI") == 1
    assert "Body text." in cleaned


def test_validate_extract_markdown_code_blocks_handles_indented_fences():
    validate = load_script_module("validator_module", "openwrt-docs4ai-08-validate.py")

    markdown = (
        "- Example block:\n\n"
        "    ```ucode\n"
        "    export default 1;\n"
        "    ```\n"
    )

    blocks = validate.extract_markdown_code_blocks(markdown)

    assert blocks == [("ucode", "export default 1;")]


def test_validate_extract_ucode_imports_supports_multiple_import_forms():
    validate = load_script_module("validator_imports", "openwrt-docs4ai-08-validate.py")

    code = (
        "import * as nl from 'nl80211';\n"
        "import { readfile } from 'fs';\n"
        "import 'uloop';\n"
    )

    imports = validate.extract_ucode_imports(code)

    assert imports == ["fs", "nl80211", "uloop"]


def test_wiki_l2_committed_corpus_sanity_snapshot():
    assert WIKI_L2_DIR.exists(), f"Missing committed wiki corpus: {WIKI_L2_DIR}"

    summary = summarize_wiki_l2_corpus(WIKI_L2_DIR)
    status = classify_wiki_l2_sanity(summary)

    print(
        "[sanity] wiki-l2 "
        f"status={status} "
        f"files={summary['files']} "
        f"wrap={summary['wrap_files']}/{summary['wrap_occurrences']} "
        f"color={summary['color_files']}/{summary['color_occurrences']} "
        f"html_table={summary['html_table_files']}/{summary['html_table_occurrences']} "
        f"duplicate_lead_heading={summary['duplicate_lead_heading_files']}"
    )

    assert status != "abnormal"
    assert summary["duplicate_lead_heading_files"] == 0