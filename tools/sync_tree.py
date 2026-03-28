"""CLI entry point for tree sync operations.

Usage
-----
Promote a generated scratch tree into the tracked publish tree (with shape
preflight):

    python tools/sync_tree.py promote-generated --src staging --dest openwrt-condensed-docs

Mirror a tree into a destination (equivalent to rsync -a --delete):

    python tools/sync_tree.py mirror-tree --src <path> --dest <path> [--exclude .git]

Additive overlay (equivalent to rsync -a without --delete):

    python tools/sync_tree.py overlay-tree --src <path> --dest <path>

Exit codes
----------
0   success
1   validation failure, unsafe path, or any operational error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running this script directly from the repo root without installing the
# lib package: insert lib/ onto the path if needed.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from lib.output_sync import (  # noqa: E402
    assert_safe_tree_sync,
    resolve_tree,
    sync_tree,
    validate_generated_root,
)


def _cmd_promote_generated(args: argparse.Namespace) -> int:
    """Promote a validated generated scratch tree into the tracked publish tree."""
    try:
        source = resolve_tree(args.src)
        destination = resolve_tree(args.dest)
    except ValueError as exc:
        print(f"[sync_tree] ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        assert_safe_tree_sync(source, destination)
    except ValueError as exc:
        print(f"[sync_tree] ERROR: unsafe paths: {exc}", file=sys.stderr)
        return 1

    errors = validate_generated_root(source)
    if errors:
        print("[sync_tree] ERROR: source tree failed shape check:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    try:
        n = sync_tree(source, destination, delete_extraneous=True)
    except Exception as exc:
        print(f"[sync_tree] ERROR: sync failed: {exc}", file=sys.stderr)
        return 1

    print(f"[sync_tree] Promoted {n} files from {source} to {destination}")
    return 0


def _cmd_mirror_tree(args: argparse.Namespace) -> int:
    """Mirror source tree into destination, deleting extraneous destination files."""
    try:
        source = resolve_tree(args.src)
        destination = resolve_tree(args.dest)
    except ValueError as exc:
        print(f"[sync_tree] ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        assert_safe_tree_sync(source, destination)
    except ValueError as exc:
        print(f"[sync_tree] ERROR: unsafe paths: {exc}", file=sys.stderr)
        return 1

    exclude_names = set(args.exclude) if args.exclude else None

    try:
        n = sync_tree(
            source,
            destination,
            delete_extraneous=True,
            exclude_names=exclude_names,
        )
    except Exception as exc:
        print(f"[sync_tree] ERROR: sync failed: {exc}", file=sys.stderr)
        return 1

    print(f"[sync_tree] Mirrored {n} files from {source} to {destination}")
    return 0


def _cmd_overlay_tree(args: argparse.Namespace) -> int:
    """Additive overlay: copy source files on top of destination without deleting anything."""
    try:
        source = resolve_tree(args.src)
        destination = resolve_tree(args.dest)
    except ValueError as exc:
        print(f"[sync_tree] ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        assert_safe_tree_sync(source, destination)
    except ValueError as exc:
        print(f"[sync_tree] ERROR: unsafe paths: {exc}", file=sys.stderr)
        return 1

    try:
        n = sync_tree(source, destination, delete_extraneous=False)
    except Exception as exc:
        print(f"[sync_tree] ERROR: sync failed: {exc}", file=sys.stderr)
        return 1

    print(f"[sync_tree] Overlaid {n} files from {source} onto {destination}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sync_tree",
        description="Tree sync utility for pipeline output staging and promotion.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # promote-generated
    p_promote = subparsers.add_parser(
        "promote-generated",
        help="Validate and promote a generated scratch tree into the tracked publish tree.",
    )
    p_promote.add_argument("--src", required=True, help="Source generated tree path.")
    p_promote.add_argument("--dest", required=True, help="Destination tracked publish path.")
    p_promote.set_defaults(func=_cmd_promote_generated)

    # mirror-tree
    p_mirror = subparsers.add_parser(
        "mirror-tree",
        help="Mirror source tree into destination, deleting extraneous files.",
    )
    p_mirror.add_argument("--src", required=True, help="Source tree path.")
    p_mirror.add_argument("--dest", required=True, help="Destination tree path.")
    p_mirror.add_argument(
        "--exclude",
        action="append",
        metavar="NAME",
        help="Entry name to exclude at all depths (repeatable). Example: --exclude .git",
    )
    p_mirror.set_defaults(func=_cmd_mirror_tree)

    # overlay-tree
    p_overlay = subparsers.add_parser(
        "overlay-tree",
        help="Additive overlay: copy source files onto destination without deleting.",
    )
    p_overlay.add_argument("--src", required=True, help="Source overlay tree path.")
    p_overlay.add_argument("--dest", required=True, help="Destination tree path.")
    p_overlay.set_defaults(func=_cmd_overlay_tree)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
