import json
from types import SimpleNamespace

import pytest

from pipeline_test_support import load_script_module


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
    ucode = load_script_module(
        "ucode_scraper_fixups", "openwrt-docs4ai-02b-scrape-ucode.py"
    )

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
    normalize = load_script_module(
        "normalize_semantic", "openwrt-docs4ai-03-normalize-semantic.py"
    )

    raw = (
        "# The Bootloader\n\n"
        "\\<WRAP round tip\\> Being firmware, \\<color red\\>**bootloader code matters**\\</color\\>.\\</WRAP\\>\n\n"
        "<table>\n"
        "<thead><tr><th>Name</th><th>Meaning</th></tr></thead>\n"
        "<tbody>\n"
        "<tr class=\"odd\"><td>A</td><td>alpha</td></tr>\n"
        "<tr class=\"odd\"><td>A</td><td>alpha</td></tr>\n"
        "</tbody>\n"
        "</table>\n"
    )

    cleaned = normalize.clean_wiki_semantic_content("The Bootloader", raw)

    assert "WRAP" not in cleaned
    assert "color red" not in cleaned
    assert "**bootloader code matters**" in cleaned
    assert "<table" not in cleaned
    assert "| Name | Meaning |" in cleaned
    assert cleaned.count("| A | alpha |") == 1


def test_clean_wiki_semantic_content_removes_immediate_duplicate_heading():
    normalize = load_script_module(
        "normalize_semantic_headings", "openwrt-docs4ai-03-normalize-semantic.py"
    )

    raw = "# Adding new elements to LuCI\n\n## Adding new elements to LuCI\n\nBody text.\n"

    cleaned = normalize.clean_wiki_semantic_content("Adding new elements to LuCI", raw)

    assert cleaned.count("Adding new elements to LuCI") == 1
    assert "Body text." in cleaned


def test_clean_wiki_semantic_content_strips_sortable_and_converts_data_table():
    normalize = load_script_module(
        "normalize_semantic_sortable", "openwrt-docs4ai-03-normalize-semantic.py"
    )

    raw = (
        "# odhcpd\n\n"
        "\\<sortable\\>\n\n"
        "<table>\n"
        "<thead><tr><th>Name</th><th>Type</th><th>Description</th></tr></thead>\n"
        "<tbody>\n"
        "<tr><td><code>ra</code></td><td>string</td><td>Router Advert service.<br />Use <code>server</code> or <code>relay</code>.</td></tr>\n"
        "</tbody>\n"
        "</table>\n"
    )

    cleaned = normalize.clean_wiki_semantic_content("odhcpd", raw)

    assert "sortable" not in cleaned.casefold()
    assert "<table" not in cleaned
    assert "| Name | Type | Description |" in cleaned
    assert "Router Advert service.; Use `server` or `relay`." in cleaned


def test_clean_wiki_semantic_content_converts_callout_table_to_admonition():
    normalize = load_script_module(
        "normalize_semantic_callout", "openwrt-docs4ai-03-normalize-semantic.py"
    )

    raw = (
        "# Hotplug -- Legacy\n\n"
        "<table>\n"
        "<tbody>\n"
        "<tr>\n"
        "<td><img src=\"/meta/icons/tango/48px-outdated.svg.png\" alt=\"48px-outdated.svg.png\" /></td>\n"
        "<td>See the <a href=\"/docs/guide-user/base-system/hotplug\">Hotplug article</a> for information on the current approach.<br /><br />The daemon was replaced with <a href=\"/docs/techref/procd\">procd</a>.</td>\n"
        "</tr>\n"
        "</tbody>\n"
        "</table>\n"
    )

    cleaned = normalize.clean_wiki_semantic_content("Hotplug -- Legacy", raw)

    assert "<table" not in cleaned
    assert "> [!WARNING]" in cleaned
    assert "[Hotplug article](/docs/guide-user/base-system/hotplug)" in cleaned
    assert "[procd](/docs/techref/procd)" in cleaned


def test_clean_wiki_semantic_content_converts_wide_layout_table_to_tsv():
    normalize = load_script_module(
        "normalize_semantic_tsv", "openwrt-docs4ai-03-normalize-semantic.py"
    )

    raw = (
        "# The OpenWrt Flash Layout\n\n"
        "<table>\n"
        "<thead><tr><th>Layer0</th><th>Layer1</th><th>Layer2</th><th>Layer3</th><th>Layer4</th></tr></thead>\n"
        "<tbody>\n"
        "<tr><td>raw flash</td><td>bootloader<br />partition</td><td>firmware</td><td><code>rootfs</code><br />mounted: <code>/rom</code></td><td>OverlayFS</td></tr>\n"
        "</tbody>\n"
        "</table>\n"
    )

    cleaned = normalize.clean_wiki_semantic_content("The OpenWrt Flash Layout", raw)

    assert "<table" not in cleaned
    assert "```tsv" in cleaned
    assert "Layer0\tLayer1\tLayer2\tLayer3\tLayer4" in cleaned


def test_clean_wiki_semantic_content_converts_footnotes_and_inline_html():
    normalize = load_script_module(
        "normalize_semantic_footnotes", "openwrt-docs4ai-03-normalize-semantic.py"
    )

    raw = (
        "# Architecture\n\n"
        "Raw NOR flash is <u>error-free</u><a href=\"#fn1\" class=\"footnote-ref\" id=\"fnref1\"><sup>1</sup></a>.\n\n"
        "<aside id=\"footnotes\" class=\"footnotes footnotes-end-of-document\">\n"
        "<ol>\n"
        "<li id=\"fn1\">Vendor claim. <a href=\"#fnref1\" class=\"footnote-back\">↩︎</a></li>\n"
        "</ol>\n"
        "</aside>\n"
    )

    cleaned = normalize.clean_wiki_semantic_content("Architecture", raw)

    assert "<aside" not in cleaned
    assert "<u>" not in cleaned
    assert "**error-free**[^1]" in cleaned
    assert "[^1]: Vendor claim." in cleaned


def test_clean_wiki_semantic_content_preserves_unsupported_table_shape():
    normalize = load_script_module(
        "normalize_semantic_preserve", "openwrt-docs4ai-03-normalize-semantic.py"
    )

    raw = (
        "# Preserved Table\n\n"
        "<table>\n"
        "<tbody>\n"
        "<tr><td rowspan=\"2\">A</td><td>B</td></tr>\n"
        "<tr><td>C</td></tr>\n"
        "</tbody>\n"
        "</table>\n"
    )

    cleaned = normalize.clean_wiki_semantic_content("Preserved Table", raw)

    assert "<table" in cleaned
    assert 'rowspan="2"' in cleaned


def test_validate_extract_markdown_code_blocks_handles_indented_fences():
    validate = load_script_module(
        "validator_module", "openwrt-docs4ai-08-validate-output.py"
    )

    markdown = (
        "- Example block:\n\n"
        "    ```ucode\n"
        "    export default 1;\n"
        "    ```\n"
    )

    blocks = validate.extract_markdown_code_blocks(markdown)

    assert blocks == [("ucode", "export default 1;")]


def test_validate_extract_ucode_imports_supports_multiple_import_forms():
    validate = load_script_module(
        "validator_imports", "openwrt-docs4ai-08-validate-output.py"
    )

    code = (
        "import * as nl from 'nl80211';\n"
        "import { readfile } from 'fs';\n"
        "import 'uloop';\n"
    )

    imports = validate.extract_ucode_imports(code)

    assert imports == ["fs", "nl80211", "uloop"]


def test_validate_strip_fenced_code_blocks_preserves_prose():
    validate = load_script_module(
        "validator_strip_fences", "openwrt-docs4ai-08-validate-output.py"
    )

    content = "Intro\n\n```javascript\nconsole.log('hi');\n```\n\nOutro\n"

    stripped = validate.strip_fenced_code_blocks(content)

    assert "console.log" not in stripped
    assert "Intro" in stripped
    assert "Outro" in stripped


def test_clone_repos_get_commit_rejects_invalid_hash(monkeypatch):
    clone = load_script_module(
        "clone_repos_invalid_hash", "openwrt-docs4ai-01-clone-repos.py"
    )

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="openwrt-test\n", stderr="")

    monkeypatch.setattr(clone.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="Invalid commit for repo-openwrt"):
        clone.get_commit("repo-openwrt")


def test_normalize_resolve_pipeline_commits_reads_manifest_when_env_missing(
    tmp_path, monkeypatch
):
    normalize = load_script_module(
        "normalize_semantic_manifest", "openwrt-docs4ai-03-normalize-semantic.py"
    )
    manifest_path = tmp_path / "repo-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "openwrt": "1111111",
                "luci": "2222222",
                "ucode": "3333333",
                "timestamp": "2026-03-09T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    for key in ["OPENWRT_COMMIT", "LUCI_COMMIT", "UCODE_COMMIT"]:
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setattr(normalize.config, "REPO_MANIFEST_PATH", str(manifest_path))
    monkeypatch.setattr(normalize.config, "OUTDIR", str(tmp_path / "out"))

    commits = normalize.resolve_pipeline_commits()

    assert commits["openwrt-core"] == "1111111"
    assert commits["procd"] == "1111111"
    assert commits["luci"] == "2222222"
    assert commits["ucode"] == "3333333"


def test_llm_routing_build_version_string_reads_manifest_when_env_missing(
    tmp_path, monkeypatch
):
    llms = load_script_module(
        "llm_routing_manifest", "openwrt-docs4ai-06-generate-llm-routing-indexes.py"
    )
    manifest_path = tmp_path / "repo-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "openwrt": "1111111",
                "luci": "2222222",
                "ucode": "3333333",
                "timestamp": "2026-03-09T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(llms.config, "REPO_MANIFEST_PATH", str(manifest_path))
    monkeypatch.setattr(llms, "OUTDIR", str(tmp_path / "out"))

    version_str, missing, resolved_manifest = llms.build_version_string(
        {"OPENWRT_COMMIT": None, "LUCI_COMMIT": None, "UCODE_COMMIT": None}
    )

    assert set(missing) == {"OPENWRT_COMMIT", "LUCI_COMMIT", "UCODE_COMMIT"}
    assert resolved_manifest == str(manifest_path)
    assert "openwrt/openwrt@1111111" in version_str
    assert "openwrt/luci@2222222" in version_str
    assert "jow-/ucode@3333333" in version_str


def test_jsdoc_fallback_requires_zero_exit_code():
    jsdoc = load_script_module("luci_jsdoc_fallback", "openwrt-docs4ai-02c-scrape-jsdoc.py")

    assert jsdoc.fallback_has_usable_output(SimpleNamespace(returncode=1, stdout="docs")) is False
    assert jsdoc.fallback_has_usable_output(SimpleNamespace(returncode=0, stdout="")) is False
    assert jsdoc.fallback_has_usable_output(SimpleNamespace(returncode=0, stdout="docs")) is True


def test_api_drift_legacy_baseline_suppresses_module_diff(tmp_path):
    changelog = load_script_module(
        "api_drift_legacy_baseline", "openwrt-docs4ai-05d-generate-api-drift-changelog.py"
    )
    baseline_path = tmp_path / "signature-inventory.json"
    baseline_path.write_text(
        json.dumps(
            {
                "generated": "2026-03-09T00:00:00Z",
                "signatures": {"uci.get": "uci.get()"},
            }
        ),
        encoding="utf-8",
    )

    signatures, modules = changelog.load_baseline_inventory(baseline_path)
    added_mods, removed_mods = changelog.compute_module_drift(["uci", "ucode"], modules)
    markdown = "\n".join(changelog.build_changes_markdown([], [], [], added_mods, removed_mods))

    assert signatures == {"uci.get": "uci.get()"}
    assert modules is None
    assert added_mods == []
    assert removed_mods == []
    assert "## New Modules" not in markdown