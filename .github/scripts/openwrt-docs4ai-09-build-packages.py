"""
Purpose: Build staged distribution packages from the release-tree output.
Phase: Packaging
Layers: Staged packages
Inputs: OUTDIR/release-tree
Outputs: OUTDIR/packages/openwrt-docs4ai-YYYY-MM-DD(-suffix).zip
Environment Variables: DIST_ZIP_ROOT_DIR, CI
Dependencies: lib.config
Notes: Local runs keep a per-run suffix to avoid same-day collisions.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import zipfile
from pathlib import Path


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config


RUN_SUFFIX_RE = re.compile(r"^[0-9a-f]{4}$")
DIST_ZIP_ROOT_DIR = os.environ.get("DIST_ZIP_ROOT_DIR", "openwrt-docs4ai")


def resolve_ci_mode(explicit_ci: bool) -> bool:
    """Return True when CI naming should be used for the package filename."""
    if explicit_ci:
        return True
    return os.environ.get("CI", "").strip().lower() == "true"


def build_package_name(*, ci: bool, pipeline_run_dir: str, zip_root_dir: str) -> str:
    """Return the output zip filename for the current execution context."""
    date_stamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    if ci:
        return f"{zip_root_dir}-{date_stamp}.zip"

    run_name = Path(pipeline_run_dir).name.lower()
    suffix = run_name.rsplit("-", 1)[-1]
    if not RUN_SUFFIX_RE.fullmatch(suffix):
        suffix = re.sub(r"[^0-9a-z]+", "-", run_name).strip("-") or "local"
    return f"{zip_root_dir}-{date_stamp}-{suffix}.zip"


def remove_existing_packages(packages_dir: Path) -> None:
    """Delete existing zip artifacts so each run leaves exactly one package."""
    for existing_zip in sorted(packages_dir.glob("*.zip")):
        existing_zip.unlink()


def build_package(
    release_tree_dir: Path,
    packages_dir: Path,
    *,
    zip_root_dir: str,
    pipeline_run_dir: str,
    ci: bool,
) -> Path:
    """Create one zip package rooted at *zip_root_dir* from *release_tree_dir*."""
    if not release_tree_dir.is_dir():
        raise FileNotFoundError(f"release-tree missing: {release_tree_dir}")

    release_files = [path for path in sorted(release_tree_dir.rglob("*")) if path.is_file()]
    if not release_files:
        raise RuntimeError(f"release-tree has no files to package: {release_tree_dir}")

    packages_dir.mkdir(parents=True, exist_ok=True)
    remove_existing_packages(packages_dir)

    zip_name = build_package_name(
        ci=ci,
        pipeline_run_dir=pipeline_run_dir,
        zip_root_dir=zip_root_dir,
    )
    zip_path = packages_dir / zip_name
    temp_zip_path = packages_dir / f"{zip_name}.tmp"

    with zipfile.ZipFile(temp_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in release_files:
            archive_path = Path(zip_root_dir) / file_path.relative_to(release_tree_dir)
            archive.write(file_path, archive_path.as_posix())

    os.replace(temp_zip_path, zip_path)

    if zip_path.stat().st_size == 0:
        raise RuntimeError(f"package was created empty: {zip_path}")

    return zip_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the package builder."""
    parser = argparse.ArgumentParser(description="Build staged distribution packages.")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Use CI naming without the local run suffix.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Build the staged distribution zip package."""
    args = parse_args(argv)
    config.ensure_dirs()
    ci_mode = resolve_ci_mode(args.ci)

    try:
        zip_path = build_package(
            Path(config.RELEASE_TREE_DIR),
            Path(config.PACKAGES_DIR),
            zip_root_dir=DIST_ZIP_ROOT_DIR,
            pipeline_run_dir=config.PIPELINE_RUN_DIR,
            ci=ci_mode,
        )
    except Exception as exc:
        print(f"[09] FAIL: {exc}")
        return 1

    print(f"[09] OK: built {zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
