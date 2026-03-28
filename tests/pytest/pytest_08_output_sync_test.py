"""Tests for lib/output_sync.py (output staging and promotion logic).

All 23 test cases specified in plan-005-unified-output-staging-and-promotion-01.md.
Uses tmp_path for fully isolated temporary directories — never touches the real
repo-root openwrt-condensed-docs/ or staging/.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

from lib.output_sync import (
    GENERATED_ROOT_REQUIRED_DIRS,
    GENERATED_ROOT_REQUIRED_FILES,
    RELEASE_TREE_MIN_MODULES,
    assert_safe_tree_sync,
    sync_tree,
    validate_generated_root,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SYNC_TREE_CLI = Path(__file__).resolve().parent.parent.parent / "tools" / "sync_tree.py"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run tools/sync_tree.py CLI and return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(SYNC_TREE_CLI), *args],
        capture_output=True,
        text=True,
    )


def _build_complete_fixture(root: Path) -> None:
    """Seed *root* with a tree that satisfies all shape requirements."""
    root.mkdir(parents=True, exist_ok=True)

    # Required files
    for rel in GENERATED_ROOT_REQUIRED_FILES:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"fixture content for {rel}\n", encoding="utf-8")

    # Required dirs (ensure non-empty beyond what required-files already cover)
    for rel_dir in GENERATED_ROOT_REQUIRED_DIRS:
        d = root / rel_dir
        d.mkdir(parents=True, exist_ok=True)
        # Ensure the dir has at least one entry
        placeholder = d / ".keep"
        if not any(d.iterdir()):
            placeholder.write_text("", encoding="utf-8")

    # release-tree needs at least RELEASE_TREE_MIN_MODULES module subdirs
    release_tree = root / "release-tree"
    for i in range(RELEASE_TREE_MIN_MODULES):
        module = release_tree / f"module-{i:02d}"
        module.mkdir(exist_ok=True)
        (module / "llms.txt").write_text(f"module {i}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Path safety tests (1-4)
# ---------------------------------------------------------------------------


def test_assert_safe_rejects_identical_paths(tmp_path: Path) -> None:
    d = tmp_path / "tree"
    d.mkdir()
    with pytest.raises(ValueError, match="same path"):
        assert_safe_tree_sync(d, d)


def test_assert_safe_rejects_source_inside_destination(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    child = parent / "child"
    parent.mkdir()
    child.mkdir()
    with pytest.raises(ValueError, match="inside destination"):
        assert_safe_tree_sync(child, parent)


def test_assert_safe_rejects_destination_inside_source(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    child = parent / "child"
    parent.mkdir()
    child.mkdir()
    with pytest.raises(ValueError, match="inside source"):
        assert_safe_tree_sync(parent, child)


def test_assert_safe_accepts_sibling_paths(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    # Should not raise
    assert_safe_tree_sync(a, b)


# ---------------------------------------------------------------------------
# Shape validation tests (5-9)
# ---------------------------------------------------------------------------


def test_validate_generated_root_passes_complete_tree(tmp_path: Path) -> None:
    root = tmp_path / "src"
    _build_complete_fixture(root)
    errors = validate_generated_root(root)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_validate_generated_root_fails_missing_file(tmp_path: Path) -> None:
    root = tmp_path / "src"
    _build_complete_fixture(root)
    (root / "llms.txt").unlink()
    errors = validate_generated_root(root)
    assert any("llms.txt" in e for e in errors), f"Expected llms.txt error, got: {errors}"


def test_validate_generated_root_fails_empty_file(tmp_path: Path) -> None:
    root = tmp_path / "src"
    _build_complete_fixture(root)
    (root / "llms.txt").write_bytes(b"")
    errors = validate_generated_root(root)
    assert any("llms.txt" in e and "empty" in e for e in errors), (
        f"Expected empty file error for llms.txt, got: {errors}"
    )


def test_validate_generated_root_fails_missing_directory(tmp_path: Path) -> None:
    root = tmp_path / "src"
    _build_complete_fixture(root)
    # Remove and recreate release-tree as file to break the dir check
    import shutil as _shutil
    _shutil.rmtree(root / "release-tree")
    errors = validate_generated_root(root)
    assert any("release-tree" in e for e in errors), (
        f"Expected release-tree error, got: {errors}"
    )


def test_validate_generated_root_fails_insufficient_release_modules(tmp_path: Path) -> None:
    root = tmp_path / "src"
    _build_complete_fixture(root)
    # Remove all but 2 module dirs from release-tree
    release_tree = root / "release-tree"
    module_dirs = sorted(p for p in release_tree.iterdir() if p.is_dir())
    import shutil as _shutil
    for d in module_dirs[2:]:
        _shutil.rmtree(d)
    errors = validate_generated_root(root)
    assert any("module" in e or "release-tree" in e for e in errors), (
        f"Expected module count error, got: {errors}"
    )


# ---------------------------------------------------------------------------
# Mirror tests (10-15)
# ---------------------------------------------------------------------------


def test_sync_tree_mirrors_files(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "a.txt").write_text("hello", encoding="utf-8")
    (src / "sub").mkdir()
    (src / "sub" / "b.txt").write_text("world", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)

    assert (dst / "a.txt").read_text(encoding="utf-8") == "hello"
    assert (dst / "sub" / "b.txt").read_text(encoding="utf-8") == "world"


def test_sync_tree_deletes_extraneous_files(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "keep.txt").write_text("keep", encoding="utf-8")
    (dst / "extra.txt").write_text("extra", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)

    assert (dst / "keep.txt").exists()
    assert not (dst / "extra.txt").exists()


def test_sync_tree_preserves_extraneous_when_disabled(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "new.txt").write_text("new", encoding="utf-8")
    (dst / "existing.txt").write_text("existing", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=False)

    assert (dst / "new.txt").exists()
    assert (dst / "existing.txt").exists()


def test_sync_tree_excludes_named_entries(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "file.txt").write_text("content", encoding="utf-8")
    (dst / ".git").mkdir()
    (dst / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True, exclude_names={".git"})

    assert (dst / ".git").exists(), ".git dir should be preserved (excluded)"
    assert (dst / "file.txt").exists()


def test_sync_tree_creates_destination_if_missing(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "does" / "not" / "exist"
    src.mkdir()
    (src / "file.txt").write_text("hi", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)

    assert dst.is_dir()
    assert (dst / "file.txt").exists()


def test_sync_tree_updates_changed_files(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "file.txt").write_text("v1", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)
    assert (dst / "file.txt").read_text(encoding="utf-8") == "v1"

    # Modify the source file — ensure mtime advances
    time.sleep(0.05)
    (src / "file.txt").write_text("v2", encoding="utf-8")
    # Touch to guarantee mtime change
    src_path = src / "file.txt"
    src_path.touch()

    sync_tree(src, dst, delete_extraneous=True)
    assert (dst / "file.txt").read_text(encoding="utf-8") == "v2"


# ---------------------------------------------------------------------------
# Overlay tests (16-17)
# ---------------------------------------------------------------------------


def test_overlay_preserves_existing_destination_files(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "b.txt").write_text("from src", encoding="utf-8")
    (dst / "a.txt").write_text("from dst", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=False)

    assert (dst / "a.txt").read_text(encoding="utf-8") == "from dst"
    assert (dst / "b.txt").read_text(encoding="utf-8") == "from src"


def test_overlay_updates_existing_files_from_source(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (dst / "file.txt").write_text("old", encoding="utf-8")

    # Ensure mtime of src file is newer
    time.sleep(0.05)
    (src / "file.txt").write_text("new", encoding="utf-8")
    (src / "file.txt").touch()

    sync_tree(src, dst, delete_extraneous=False)

    assert (dst / "file.txt").read_text(encoding="utf-8") == "new"


# ---------------------------------------------------------------------------
# CLI tests (18-21)
# ---------------------------------------------------------------------------


def test_cli_promote_generated_exits_zero_on_success(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    _build_complete_fixture(src)

    result = _run_cli("promote-generated", "--src", str(src), "--dest", str(dst))

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert dst.is_dir()
    assert (dst / "llms.txt").exists()


def test_cli_promote_generated_exits_one_on_shape_failure(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    dst.mkdir()
    # Incomplete tree — only create one file
    src.mkdir()
    (src / "README.md").write_text("incomplete", encoding="utf-8")

    result = _run_cli("promote-generated", "--src", str(src), "--dest", str(dst))

    assert result.returncode == 1
    # Destination should not have been modified
    assert not (dst / "README.md").exists()


def test_cli_mirror_tree_with_exclude(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "file.txt").write_text("content", encoding="utf-8")
    (dst / ".git").mkdir()
    (dst / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    result = _run_cli(
        "mirror-tree", "--src", str(src), "--dest", str(dst), "--exclude", ".git"
    )

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert (dst / ".git").exists(), ".git should be preserved when excluded"
    assert (dst / "file.txt").exists()


def test_cli_overlay_tree_preserves_destination(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "overlay.txt").write_text("overlay", encoding="utf-8")
    (dst / "existing.txt").write_text("keep", encoding="utf-8")

    result = _run_cli("overlay-tree", "--src", str(src), "--dest", str(dst))

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert (dst / "overlay.txt").exists()
    assert (dst / "existing.txt").read_text(encoding="utf-8") == "keep"


# ---------------------------------------------------------------------------
# Edge case tests (22-23)
# ---------------------------------------------------------------------------


def test_sync_tree_handles_empty_source(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (dst / "old.txt").write_text("should be removed", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)

    assert not (dst / "old.txt").exists()
    assert dst.is_dir()


def test_sync_tree_handles_nested_directories(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    deep = src / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "deep.txt").write_text("deep content", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)

    assert (dst / "a" / "b" / "c" / "deep.txt").read_text(encoding="utf-8") == "deep content"


# ---------------------------------------------------------------------------
# End-to-end promote cycle test
# ---------------------------------------------------------------------------


def test_end_to_end_promote_cycle(tmp_path: Path) -> None:
    """Full generate → validate → promote cycle in isolation.

    1. Creates an isolated scratch tree satisfying the shape spec.
    2. Pre-populates the publish tree with an extra file.
    3. Invokes CLI promote-generated as a subprocess.
    4. Asserts exit code 0.
    5. Asserts all required files exist in the publish tree.
    6. Asserts the extraneous pre-populated file is gone after promotion.
    """
    scratch = tmp_path / "scratch"
    publish = tmp_path / "publish"

    # Seed scratch with a complete valid fixture tree
    _build_complete_fixture(scratch)

    # Pre-populate publish with an extraneous file that should be deleted
    publish.mkdir()
    (publish / "stale-artifact.txt").write_text("should be deleted", encoding="utf-8")

    result = _run_cli("promote-generated", "--src", str(scratch), "--dest", str(publish))

    assert result.returncode == 0, (
        f"promote-generated failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    # All required files must exist in the publish tree
    for rel in GENERATED_ROOT_REQUIRED_FILES:
        assert (publish / rel).exists(), f"Missing required file after promote: {rel}"

    # The extraneous pre-populated file must be gone
    assert not (publish / "stale-artifact.txt").exists(), (
        "extraneous file was not removed during promote"
    )
