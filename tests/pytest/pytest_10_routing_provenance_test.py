"""
pytest_10_routing_provenance_test.py

Tests for Phase 11 (A5 Routing Metadata + A6 Visible Provenance Headers):
  - Stage 06: choose_short_description prefers routing_summary
  - Stage 06: routing_priority sorting of L2 entries
  - Stage 05a: append_skeleton_lines prefers routing_summary
  - Stage 05a: build_provenance_block generates correct output
  - Stage 05a: copy_release_chunked_pages injects provenance headers into chunked files
  - Stage 05a: L2 files do NOT contain visible provenance blocks
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.pytest_pipeline_support import OUTDIR, PROJECT_ROOT, load_script_module


# ---------------------------------------------------------------------------
# Stage 06 — choose_short_description prefers routing_summary (A5)
# ---------------------------------------------------------------------------

def test_choose_short_description_prefers_routing_summary() -> None:
    """routing_summary is used first, before ai_summary and description."""
    stage06 = load_script_module("stage06_routing_summary", "openwrt-docs4ai-06-generate-llm-routing-indexes.py")

    frontmatter = {
        "routing_summary": "Curated routing summary.",
        "ai_summary": "AI summary.",
        "description": "Author description.",
    }
    result = stage06.choose_short_description(frontmatter, "Body text.")
    assert result == "Curated routing summary."


def test_choose_short_description_falls_back_to_ai_summary_when_no_routing_summary() -> None:
    """Falls back to ai_summary when routing_summary is absent."""
    stage06 = load_script_module("stage06_no_routing_summary", "openwrt-docs4ai-06-generate-llm-routing-indexes.py")

    frontmatter = {
        "ai_summary": "AI summary.",
        "description": "Author description.",
    }
    result = stage06.choose_short_description(frontmatter, "Body text.")
    assert result == "AI summary."


def test_choose_short_description_falls_back_to_description() -> None:
    """Falls back to description when neither routing_summary nor ai_summary are present."""
    stage06 = load_script_module("stage06_description_fallback", "openwrt-docs4ai-06-generate-llm-routing-indexes.py")

    frontmatter = {"description": "Author description."}
    result = stage06.choose_short_description(frontmatter, "Body text.")
    assert result == "Author description."


def test_choose_short_description_falls_back_to_body() -> None:
    """Falls back to body text when no explicit description fields are present."""
    stage06 = load_script_module("stage06_body_fallback", "openwrt-docs4ai-06-generate-llm-routing-indexes.py")

    frontmatter = {}
    result = stage06.choose_short_description(frontmatter, "This is the body sentence. And more.")
    assert result == "This is the body sentence."


# ---------------------------------------------------------------------------
# Stage 05a — append_skeleton_lines prefers routing_summary (A5)
# ---------------------------------------------------------------------------

def test_append_skeleton_lines_prefers_routing_summary() -> None:
    """append_skeleton_lines uses routing_summary when present, even if ai_summary exists."""
    stage05a = load_script_module("stage05a_skeleton_routing", "openwrt-docs4ai-05a-assemble-references.py")

    lines: list[str] = []
    frontmatter = {
        "routing_summary": "Curated routing summary for map.",
        "ai_summary": "AI generated summary.",
    }
    stage05a.append_skeleton_lines(lines, frontmatter, "# Some heading\n")
    assert any("Curated routing summary for map." in line for line in lines)
    assert not any("AI generated summary." in line for line in lines)


def test_append_skeleton_lines_falls_back_to_ai_summary() -> None:
    """Falls back to ai_summary when no routing_summary is present."""
    stage05a = load_script_module("stage05a_skeleton_ai_summary", "openwrt-docs4ai-05a-assemble-references.py")

    lines: list[str] = []
    frontmatter = {"ai_summary": "AI summary text."}
    stage05a.append_skeleton_lines(lines, frontmatter, "# Some heading\n")
    assert any("AI summary text." in line for line in lines)


def test_append_skeleton_lines_falls_back_to_description() -> None:
    """Falls back to description when routing_summary and ai_summary are absent."""
    stage05a = load_script_module("stage05a_skeleton_description", "openwrt-docs4ai-05a-assemble-references.py")

    lines: list[str] = []
    frontmatter = {"description": "Author description text."}
    stage05a.append_skeleton_lines(lines, frontmatter, "# Some heading\n")
    assert any("Author description text." in line for line in lines)


# ---------------------------------------------------------------------------
# Stage 05a — build_provenance_block (A6)
# ---------------------------------------------------------------------------

def test_build_provenance_block_with_source_url() -> None:
    """Provenance block includes Source, Kind, and Normalized lines when source_url is present."""
    stage05a = load_script_module("stage05a_provenance_url", "openwrt-docs4ai-05a-assemble-references.py")

    frontmatter = {
        "origin_type": "wiki_page",
        "source_url": "https://openwrt.org/docs/guide-user/introduction",
        "last_pipeline_run": "2026-03-22T00:00:00Z",
    }
    block = stage05a.build_provenance_block(frontmatter, "2026-03-22T12:00:00")
    assert "> **Source:**" in block
    assert "https://openwrt.org/docs/guide-user/introduction" in block
    assert "> **Kind:** wiki_page" in block
    assert "scraped" in block
    assert "> **Normalized:** 2026-03-22" in block


def test_build_provenance_block_omits_source_when_no_url() -> None:
    """Provenance block omits Source line when source_url is absent (no fabrication)."""
    stage05a = load_script_module("stage05a_provenance_no_url", "openwrt-docs4ai-05a-assemble-references.py")

    frontmatter = {
        "origin_type": "authored",
        "last_pipeline_run": "2026-03-22",
    }
    block = stage05a.build_provenance_block(frontmatter, "2026-03-22")
    assert "> **Source:**" not in block
    assert "> **Kind:** authored" in block
    assert "hand-authored" in block
    assert "> **Normalized:** 2026-03-22" in block


def test_build_provenance_block_includes_commit_when_present() -> None:
    """Provenance block includes Commit hash for git-backed origin types."""
    stage05a = load_script_module("stage05a_provenance_commit", "openwrt-docs4ai-05a-assemble-references.py")

    frontmatter = {
        "origin_type": "js_source",
        "source_url": "https://github.com/openwrt/luci/blob/abc1234/foo.js",
        "source_commit": "abc1234",
        "last_pipeline_run": "2026-03-22",
    }
    block = stage05a.build_provenance_block(frontmatter, "2026-03-22")
    assert "**Commit:** abc1234" in block


def test_build_provenance_block_authored_has_no_commit() -> None:
    """Authored origin has no source_commit in the provenance block."""
    stage05a = load_script_module("stage05a_provenance_authored", "openwrt-docs4ai-05a-assemble-references.py")

    frontmatter = {
        "origin_type": "authored",
        "last_pipeline_run": "2026-03-22",
    }
    block = stage05a.build_provenance_block(frontmatter, "2026-03-22")
    assert "**Commit:**" not in block


# ---------------------------------------------------------------------------
# Stage 05a — copy_release_chunked_pages injects provenance (A6)
# ---------------------------------------------------------------------------

def test_copy_release_chunked_pages_injects_provenance_header(tmp_path: Path) -> None:
    """copy_release_chunked_pages writes a visible provenance block after the frontmatter."""
    stage05a = load_script_module("stage05a_chunked_provenance", "openwrt-docs4ai-05a-assemble-references.py")

    # Set up a fake out_mod_dir and an L2 source file
    out_mod_dir = tmp_path / "mymodule"
    out_mod_dir.mkdir()
    l2_file = tmp_path / "mymodule_page-intro.md"
    l2_file.write_text(
        "---\n"
        "title: Intro\n"
        "module: mymodule\n"
        "origin_type: wiki_page\n"
        "source_url: https://openwrt.org/docs/intro\n"
        "last_pipeline_run: '2026-03-22'\n"
        "---\n"
        "\n"
        "# Introduction\n\n"
        "This is the intro page.\n",
        encoding="utf-8",
    )

    stage05a.copy_release_chunked_pages([str(l2_file)], str(out_mod_dir), "2026-03-22T00:00:00")

    chunked_dir = out_mod_dir / stage05a.config.MODULE_CHUNKED_REF_DIRNAME
    output_file = chunked_dir / l2_file.name
    assert output_file.exists()

    text = output_file.read_text(encoding="utf-8")
    assert "> **Kind:** wiki_page" in text
    assert "> **Normalized:** 2026-03-22" in text
    assert "> **Source:**" in text
    # Frontmatter must still be present
    assert text.startswith("---\n")


def test_copy_release_chunked_pages_no_fabricated_url_when_source_absent(tmp_path: Path) -> None:
    """Provenance block omits Source line when source_url absent — no URL fabrication."""
    stage05a = load_script_module("stage05a_chunked_no_url", "openwrt-docs4ai-05a-assemble-references.py")

    out_mod_dir = tmp_path / "cookbook"
    out_mod_dir.mkdir()
    l2_file = tmp_path / "cookbook_guide-intro.md"
    l2_file.write_text(
        "---\n"
        "title: Guide Intro\n"
        "module: cookbook\n"
        "origin_type: authored\n"
        "last_pipeline_run: '2026-03-22'\n"
        "---\n"
        "\n"
        "# Guide Intro\n\nHand-authored page.\n",
        encoding="utf-8",
    )

    stage05a.copy_release_chunked_pages([str(l2_file)], str(out_mod_dir), "2026-03-22T00:00:00")

    chunked_dir = out_mod_dir / stage05a.config.MODULE_CHUNKED_REF_DIRNAME
    output_file = chunked_dir / l2_file.name
    text = output_file.read_text(encoding="utf-8")

    # No fabricated URL
    assert "> **Source:** http" not in text
    assert "hand-authored" in text


def test_l2_files_do_not_contain_provenance_block() -> None:
    """L2 source files must not contain the visible provenance block (it is only in release output)."""
    l2_dir = OUTDIR / "L2-semantic"
    if not l2_dir.is_dir():
        pytest.skip(f"no pipeline output at {l2_dir}")

    l2_files = list(l2_dir.rglob("*.md"))[:20]  # Sample first 20
    for fpath in l2_files:
        content = fpath.read_text(encoding="utf-8")
        assert "> **Normalized:**" not in content, (
            f"L2 file contains visible provenance block (should be release-only): {fpath.relative_to(PROJECT_ROOT)}"
        )
        assert "> **Kind:**" not in content, (
            f"L2 file contains visible provenance block: {fpath.relative_to(PROJECT_ROOT)}"
        )
