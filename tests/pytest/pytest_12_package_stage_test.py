from __future__ import annotations

import re
import zipfile
from pathlib import Path

from tests.support.pytest_pipeline_support import load_script_module


def _seed_release_tree(release_tree: Path) -> None:
    release_tree.mkdir(parents=True, exist_ok=True)
    (release_tree / "README.md").write_text("readme\n", encoding="utf-8")
    (release_tree / "ucode").mkdir(parents=True, exist_ok=True)
    (release_tree / "ucode" / "llms.txt").write_text("ucode\n", encoding="utf-8")


def test_build_package_creates_one_local_zip_with_run_suffix(tmp_path: Path) -> None:
    stage09 = load_script_module("stage09_packages", "openwrt-docs4ai-09-build-packages.py")
    release_tree = tmp_path / "release-tree"
    packages_dir = tmp_path / "packages"
    _seed_release_tree(release_tree)

    zip_path = stage09.build_package(
        release_tree,
        packages_dir,
        zip_root_dir="openwrt-docs4ai",
        pipeline_run_dir="tmp/pipeline-20260328-1200UTC-7f3c",
        ci=False,
    )

    assert re.fullmatch(r"openwrt-docs4ai-\d{4}-\d{2}-\d{2}-7f3c\.zip", zip_path.name)
    assert zip_path.stat().st_size > 0
    assert sorted(packages_dir.glob("*.zip")) == [zip_path]

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())

    assert "openwrt-docs4ai/README.md" in names
    assert "openwrt-docs4ai/ucode/llms.txt" in names


def test_build_package_uses_ci_filename_without_suffix(tmp_path: Path) -> None:
    stage09 = load_script_module("stage09_packages_ci", "openwrt-docs4ai-09-build-packages.py")
    release_tree = tmp_path / "release-tree"
    packages_dir = tmp_path / "packages"
    _seed_release_tree(release_tree)

    zip_path = stage09.build_package(
        release_tree,
        packages_dir,
        zip_root_dir="openwrt-docs4ai",
        pipeline_run_dir="tmp/pipeline-ci",
        ci=True,
    )

    assert re.fullmatch(r"openwrt-docs4ai-\d{4}-\d{2}-\d{2}\.zip", zip_path.name)
    assert zip_path.stat().st_size > 0