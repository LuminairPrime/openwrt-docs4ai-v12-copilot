"""Tests for lib.output_sync.py tree sync behavior.

These tests cover safe path handling, mirror semantics, overlay semantics,
CLI wiring, and deletion behavior. They use tmp_path throughout and never
touch the real workspace output trees.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

from lib.output_sync import (
    assert_safe_tree_sync,
    resolve_tree,
    sync_tree,
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


def _write_files(root: Path, files: dict[str, str]) -> None:
    """Create *files* under *root* using relative path keys."""
    root.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _create_directory_symlink(link_path: Path, target_path: Path) -> None:
    """Create a directory symlink or skip when the platform disallows it."""
    try:
        link_path.symlink_to(target_path, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlinks unsupported in this environment: {exc}")


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
# Mirror tests (5-10)
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
# Overlay tests (11-12)
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
# CLI tests (13-16)
# ---------------------------------------------------------------------------


def test_cli_mirror_tree_exits_zero_on_success(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    _write_files(src, {"llms.txt": "hello\n", "release-tree/index.html": "<html></html>\n"})

    result = _run_cli("mirror-tree", "--src", str(src), "--dest", str(dst))

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert dst.is_dir()
    assert (dst / "llms.txt").exists()


def test_cli_mirror_tree_exits_one_on_missing_source(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    dst.mkdir()

    result = _run_cli("mirror-tree", "--src", str(src), "--dest", str(dst))

    assert result.returncode == 1
    assert "source does not exist" in result.stderr


def test_cli_mirror_tree_with_exclude(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "file.txt").write_text("content", encoding="utf-8")
    (dst / ".git").mkdir()
    (dst / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    result = _run_cli("mirror-tree", "--src", str(src), "--dest", str(dst), "--exclude", ".git")

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
# Edge case tests (17-18)
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


def test_end_to_end_mirror_cycle(tmp_path: Path) -> None:
    """Mirror a source tree into a destination and prune stale entries."""
    scratch = tmp_path / "scratch"
    publish = tmp_path / "publish"

    _write_files(
        scratch,
        {
            "AGENTS.md": "agents\n",
            "release-tree/index.html": "<html></html>\n",
            "support-tree/manifests/repo-manifest.json": "{}\n",
        },
    )

    publish.mkdir()
    (publish / "stale-artifact.txt").write_text("should be deleted", encoding="utf-8")

    result = _run_cli("mirror-tree", "--src", str(scratch), "--dest", str(publish))

    assert result.returncode == 0, f"mirror-tree failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert (publish / "AGENTS.md").exists()
    assert (publish / "release-tree" / "index.html").exists()
    assert not (publish / "stale-artifact.txt").exists()


# ---------------------------------------------------------------------------
# Regression tests (19-24)
# ---------------------------------------------------------------------------


def test_resolve_tree_rejects_empty_string() -> None:
    """Finding 2: resolve_tree('') must raise, not resolve to cwd."""
    with pytest.raises(ValueError, match="empty"):
        resolve_tree("")


def test_resolve_tree_rejects_whitespace_only_string() -> None:
    with pytest.raises(ValueError, match="empty"):
        resolve_tree("   ")


def test_sync_tree_does_not_create_destination_on_missing_source(tmp_path: Path) -> None:
    """Finding 3: missing source must not leave destination created on disk."""
    src = tmp_path / "no-such-dir"
    dst = tmp_path / "should-not-exist"

    with pytest.raises(FileNotFoundError):
        sync_tree(src, dst, delete_extraneous=True)

    assert not dst.exists(), "destination was created despite missing source"


def test_sync_tree_replaces_directory_with_file(tmp_path: Path) -> None:
    """Finding 1: when source has a file and destination has a directory
    with the same name, the directory must be replaced by the file."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    # Source: item is a file
    (src / "item").write_text("I am a file", encoding="utf-8")

    # Destination: item is a directory with children
    (dst / "item").mkdir()
    (dst / "item" / "old.txt").write_text("leftover", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)

    assert (dst / "item").is_file(), "directory was not replaced by file"
    assert (dst / "item").read_text(encoding="utf-8") == "I am a file"


def test_sync_tree_replaces_file_with_directory(tmp_path: Path) -> None:
    """Finding 1 inverse: when source has a directory and destination has a
    file with the same name, the file must be replaced by the directory."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    # Source: item is a directory with a child
    (src / "item").mkdir()
    (src / "item" / "child.txt").write_text("child content", encoding="utf-8")

    # Destination: item is a file
    (dst / "item").write_text("I am a file that should be replaced", encoding="utf-8")

    sync_tree(src, dst, delete_extraneous=True)

    assert (dst / "item").is_dir(), "file was not replaced by directory"
    assert (dst / "item" / "child.txt").read_text(encoding="utf-8") == "child content"


def test_sync_tree_deletes_directory_symlink_without_touching_target(tmp_path: Path) -> None:
    """Extraneous directory symlinks should be removed without deleting targets."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    target = tmp_path / "target"

    src.mkdir()
    dst.mkdir()
    target.mkdir()
    (target / "keep.txt").write_text("keep", encoding="utf-8")

    link = dst / "linked-dir"
    _create_directory_symlink(link, target)

    sync_tree(src, dst, delete_extraneous=True)

    assert not link.exists(), "symlink should be removed from destination"
    assert target.is_dir(), "symlink target directory should remain"
    assert (target / "keep.txt").read_text(encoding="utf-8") == "keep"
