"""Shared tree-sync logic for output staging and promotion.

This module owns the file-tree mutation semantics used by the pipeline's
promote, mirror, and overlay operations. It is intentionally narrow — stage 08
remains the authoritative contract validator. This module only enforces path
safety and a lightweight shape check before allowing a tree sync.

All public functions are cross-platform (Windows and Linux). They use pathlib
and shutil throughout. No subprocess or shell utility calls are made.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Generated-root shape specification
#
# Keep in sync with:
#   - the staging-contract required_paths in the workflow
#     (.github/workflows/openwrt-docs4ai-00-pipeline.yml lines 728-758)
#   - stage 08 validate_release_tree_contract()
#
# This list is a strict subset of what stage 08 checks. It is intentionally
# minimal — enough to prove the tree is a plausible complete generated output.
# ---------------------------------------------------------------------------

GENERATED_ROOT_REQUIRED_FILES: list[str] = [
    "AGENTS.md",
    "README.md",
    "llms.txt",
    "llms-full.txt",
    "index.html",
    "repo-manifest.json",
    "cross-link-registry.json",
    "release-tree/llms.txt",
    "release-tree/index.html",
    "release-tree/AGENTS.md",
    "release-tree/README.md",
    "support-tree/manifests/repo-manifest.json",
    "support-tree/manifests/cross-link-registry.json",
    "support-tree/telemetry/CHANGES.md",
    "support-tree/telemetry/changelog.json",
    "support-tree/telemetry/signature-inventory.json",
]

GENERATED_ROOT_REQUIRED_DIRS: list[str] = [
    "L1-raw",
    "L2-semantic",
    "release-tree",
    "support-tree",
]

# Minimum number of module subdirectories expected under release-tree/
RELEASE_TREE_MIN_MODULES: int = 4


# ---------------------------------------------------------------------------
# Path utilities
# ---------------------------------------------------------------------------


def resolve_tree(path: str | Path) -> Path:
    """Resolve and normalise *path* for safe tree operations.

    Raises ValueError if the path string is empty.
    Does not require the path to exist (callers that need existence checks
    should do so explicitly after calling this function).
    """
    path = Path(path)
    if not str(path).strip():
        raise ValueError("path must not be empty")
    return path.resolve()


def assert_safe_tree_sync(source: Path, destination: Path) -> None:
    """Validate that *source* and *destination* are safe for a tree sync.

    Raises ValueError in any of the following cases:
    - source and destination resolve to the same path
    - source is inside destination
    - destination is inside source
    """
    # Resolve to absolute paths for accurate comparison
    src = source.resolve()
    dst = destination.resolve()

    if src == dst:
        raise ValueError(
            f"source and destination resolve to the same path: {src}"
        )

    # Check containment in both directions using Path.is_relative_to
    # (available from Python 3.9; fallback for older via str comparison)
    try:
        if src.is_relative_to(dst):
            raise ValueError(
                f"source {src} is inside destination {dst}; "
                "this would cause recursive sync"
            )
        if dst.is_relative_to(src):
            raise ValueError(
                f"destination {dst} is inside source {src}; "
                "this would overwrite the source tree"
            )
    except AttributeError:
        # Python < 3.9 fallback
        src_str = str(src)
        dst_str = str(dst)
        sep = "/"

        def _is_relative(child: str, parent: str) -> bool:
            parent_with_sep = parent.rstrip(sep) + sep
            return child.rstrip(sep) + sep == parent_with_sep or child.startswith(
                parent_with_sep
            )

        if _is_relative(src_str, dst_str):
            raise ValueError(
                f"source {src} is inside destination {dst}; "
                "this would cause recursive sync"
            )
        if _is_relative(dst_str, src_str):
            raise ValueError(
                f"destination {dst} is inside source {src}; "
                "this would overwrite the source tree"
            )


# ---------------------------------------------------------------------------
# Shape validation
# ---------------------------------------------------------------------------


def validate_generated_root(source: Path) -> list[str]:
    """Validate that *source* has the minimum required shape for promotion.

    Returns a list of error description strings. An empty list means the tree
    passes the shape check. The caller decides whether to abort or warn.

    This is intentionally a lightweight check — not a full contract validation.
    Stage 08 owns the authoritative validation gate.
    """
    errors: list[str] = []
    root = source.resolve()

    if not root.exists():
        return [f"source does not exist: {root}"]

    # Check required files exist and are non-empty
    for rel_path in GENERATED_ROOT_REQUIRED_FILES:
        full_path = root / rel_path
        if not full_path.exists():
            errors.append(f"required file missing: {rel_path}")
        elif not full_path.is_file():
            errors.append(f"required file path is not a file: {rel_path}")
        elif full_path.stat().st_size == 0:
            errors.append(f"required file is empty: {rel_path}")

    # Check required directories exist and are non-empty
    for rel_dir in GENERATED_ROOT_REQUIRED_DIRS:
        full_path = root / rel_dir
        if not full_path.exists():
            errors.append(f"required directory missing: {rel_dir}")
        elif not full_path.is_dir():
            errors.append(f"required directory path is not a directory: {rel_dir}")
        elif not any(full_path.iterdir()):
            errors.append(f"required directory is empty: {rel_dir}")

    # Check release-tree module count
    release_tree = root / "release-tree"
    if release_tree.is_dir():
        module_dirs = [p for p in release_tree.iterdir() if p.is_dir()]
        if len(module_dirs) < RELEASE_TREE_MIN_MODULES:
            errors.append(
                f"release-tree has {len(module_dirs)} module directories; "
                f"expected at least {RELEASE_TREE_MIN_MODULES}"
            )

    return errors


# ---------------------------------------------------------------------------
# Core tree sync
# ---------------------------------------------------------------------------


def sync_tree(
    source: Path,
    destination: Path,
    *,
    delete_extraneous: bool,
    exclude_names: set[str] | None = None,
) -> int:
    """Mirror *source* tree into *destination* tree.

    Parameters
    ----------
    source:
        The tree to read from. Must exist.
    destination:
        The tree to write into. Created if it does not exist.
    delete_extraneous:
        When True, files and directories in *destination* that are not present
        in *source* (and are not excluded) are deleted after copying. This
        implements rsync ``--delete`` semantics.
        When False, only addition and update operations are performed — nothing
        in *destination* is deleted. This implements additive overlay semantics.
    exclude_names:
        A set of entry names (not paths) to exclude at every depth. A name like
        ``.git`` will exclude any directory or file named ``.git`` anywhere in
        the tree. This matches ``rsync --exclude=".git"`` semantics.

    Returns
    -------
    int
        The number of files copied or updated.
    """
    if exclude_names is None:
        exclude_names = set()

    source = source.resolve()
    destination = destination.resolve()

    # Build destination root if it does not exist
    destination.mkdir(parents=True, exist_ok=True)

    copied = _sync_recursive(source, destination, exclude_names, delete_extraneous)
    return copied


def _sync_recursive(
    src_dir: Path,
    dst_dir: Path,
    exclude_names: set[str],
    delete_extraneous: bool,
) -> int:
    """Recursive implementation of sync_tree. Returns file copy count."""
    copied = 0

    # Build the set of source entry names for extraneous-deletion tracking
    src_entries: dict[str, Path] = {}
    for entry in sorted(src_dir.iterdir()):
        if entry.name in exclude_names:
            print(
                f"[output_sync] skipping excluded entry: {entry.relative_to(src_dir.parent)}",
                file=sys.stderr,
            )
            continue
        if entry.is_symlink():
            print(
                f"[output_sync] warning: skipping symlink: {entry}",
                file=sys.stderr,
            )
            continue
        src_entries[entry.name] = entry

    dst_dir.mkdir(parents=True, exist_ok=True)

    # Copy / update files and recurse into directories
    for name, src_entry in sorted(src_entries.items()):
        dst_entry = dst_dir / name

        if src_entry.is_dir():
            dst_entry.mkdir(exist_ok=True)
            copied += _sync_recursive(src_entry, dst_entry, exclude_names, delete_extraneous)
        elif src_entry.is_file():
            if _needs_copy(src_entry, dst_entry):
                shutil.copy2(src_entry, dst_entry)
                copied += 1

    # Delete extraneous destination entries when requested
    if delete_extraneous:
        for dst_entry in sorted(dst_dir.iterdir()):
            if dst_entry.name in exclude_names:
                # Never delete excluded names
                continue
            if dst_entry.name not in src_entries:
                if dst_entry.is_dir():
                    shutil.rmtree(dst_entry)
                else:
                    dst_entry.unlink()

    return copied


def _needs_copy(src: Path, dst: Path) -> bool:
    """Return True if *src* should be copied to *dst*.

    A copy is needed when:
    - *dst* does not exist, or
    - *dst* differs from *src* in size or modification time.

    Only modification time is compared because creation time is not reliably
    preserved on Linux (D9: shutil.copy2 preserves mtime cross-platform;
    ctime is OS-specific and not tested).
    """
    if not dst.exists():
        return True
    src_stat = src.stat()
    dst_stat = dst.stat()
    if src_stat.st_size != dst_stat.st_size:
        return True
    # Compare mtime with 2-second tolerance to handle FAT filesystem rounding
    # Use a 0.01s tolerance to absorb floating-point rounding while still
    # detecting sub-second mtime changes on NTFS and ext4. The 2-second
    # FAT32 rounding does not apply here — this pipeline runs on NTFS and Linux
    # where mtime resolution is ≤ 100ns.
    if abs(src_stat.st_mtime - dst_stat.st_mtime) > 0.01:
        return True
    return False
