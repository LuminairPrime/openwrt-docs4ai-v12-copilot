from pathlib import Path

from lib import partial_rerun_guard
from tests.support.pytest_pipeline_support import load_script_module


def write_l2_fixture(module_dir: Path) -> None:
    module_dir.mkdir(parents=True, exist_ok=True)
    (module_dir / "sample.md").write_text(
        "---\n"
        "title: Sample\n"
        "description: Sample fixture\n"
        "origin_type: authored\n"
        "token_count: 1\n"
        "last_pipeline_run: 2026-03-28\n"
        "---\n\n"
        "# Sample\n\n"
        "Body text.\n",
        encoding="utf-8",
    )


def test_partial_rerun_guard_detects_strict_subset(tmp_path: Path) -> None:
    existing_root = tmp_path / "existing"
    (existing_root / "cookbook").mkdir(parents=True)
    (existing_root / "wiki").mkdir()

    missing_modules = partial_rerun_guard.find_missing_modules_for_partial_rerun(
        {"cookbook"},
        str(existing_root),
    )

    assert missing_modules == ["wiki"]


def test_partial_rerun_guard_allows_equal_or_empty_existing(tmp_path: Path) -> None:
    existing_root = tmp_path / "existing"
    existing_root.mkdir()
    assert partial_rerun_guard.find_missing_modules_for_partial_rerun({"cookbook"}, str(existing_root)) == []

    (existing_root / "cookbook").mkdir()
    assert partial_rerun_guard.find_missing_modules_for_partial_rerun({"cookbook"}, str(existing_root)) == []
    assert partial_rerun_guard.find_missing_modules_for_partial_rerun({"cookbook", "wiki"}, str(existing_root)) == []


def test_partial_rerun_guard_blocks_empty_incoming_against_existing(tmp_path: Path) -> None:
    existing_root = tmp_path / "existing"
    (existing_root / "wiki").mkdir(parents=True)

    missing_modules = partial_rerun_guard.find_missing_modules_for_partial_rerun(
        set(),
        str(existing_root),
    )

    assert missing_modules == ["wiki"]


def test_stage03_promotion_blocks_partial_rerun_before_clobber(tmp_path: Path, monkeypatch) -> None:
    stage03 = load_script_module("normalize_semantic_partial_guard", "openwrt-docs4ai-03-normalize-semantic.py")

    l1_dir = tmp_path / "work" / "L1-raw"
    l2_dir = tmp_path / "work" / "L2-semantic"
    processed_dir = tmp_path / "processed"

    (l1_dir / "cookbook").mkdir(parents=True)
    (l2_dir / "cookbook").mkdir(parents=True)
    (processed_dir / "L1-raw" / "cookbook").mkdir(parents=True)
    (processed_dir / "L1-raw" / "wiki").mkdir()
    (processed_dir / "L2-semantic" / "cookbook").mkdir(parents=True)
    (processed_dir / "L2-semantic" / "wiki").mkdir()

    monkeypatch.setattr(stage03, "L1_DIR", str(l1_dir))
    monkeypatch.setattr(stage03, "L2_DIR", str(l2_dir))
    monkeypatch.setattr(stage03.config, "PROCESSED_DIR", str(processed_dir))

    exit_code = stage03.main([])

    assert exit_code == 1
    assert (processed_dir / "L1-raw" / "wiki").is_dir()
    assert (processed_dir / "L2-semantic" / "wiki").is_dir()


def test_stage05a_rebuild_blocks_partial_rerun_before_clobber(tmp_path: Path, monkeypatch) -> None:
    stage05a = load_script_module("assemble_references_partial_guard", "openwrt-docs4ai-05a-assemble-references.py")

    outdir = tmp_path / "out"
    l2_dir = outdir / "L2-semantic"
    release_tree_dir = outdir / "release-tree"

    write_l2_fixture(l2_dir / "cookbook")
    (release_tree_dir / "cookbook").mkdir(parents=True)
    (release_tree_dir / "wiki").mkdir()

    monkeypatch.setattr(stage05a, "OUTDIR", str(outdir))
    monkeypatch.setattr(stage05a, "L2_DIR", str(l2_dir))
    monkeypatch.setattr(stage05a, "RELEASE_TREE_DIR", str(release_tree_dir))

    exit_code = stage05a.main([])

    assert exit_code == 1
    assert (release_tree_dir / "wiki").is_dir()
