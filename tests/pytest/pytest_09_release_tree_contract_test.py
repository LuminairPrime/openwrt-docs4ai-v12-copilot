from __future__ import annotations

from pathlib import Path

from tests.support.pytest_pipeline_support import load_script_module


MODULES = ["procd", "uci", "ucode", "wiki"]


def build_release_tree(outdir: Path, validate, modules: list[str] | None = None) -> Path:
    modules = modules or MODULES
    release_tree = outdir / Path(validate.config.RELEASE_TREE_DIR).name
    release_tree.mkdir(parents=True, exist_ok=True)

    llms_entries = "\n".join(
        f"- [{module}](./{module}/llms.txt): {module} entry (~10 tokens)"
        for module in modules
    )
    release_tree.joinpath("llms.txt").write_text(
        "# openwrt-docs4ai - LLM Routing Index\n\n"
        "## Modules\n\n"
        f"{llms_entries}\n\n"
        + ("routing-contract\n" * 40),
        encoding="utf-8",
    )
    release_tree.joinpath("llms-full.txt").write_text(
        "# openwrt-docs4ai - Complete Flat Catalog\n\n"
        f"{llms_entries}\n",
        encoding="utf-8",
    )
    release_tree.joinpath("README.md").write_text(
        "# Release Tree\n\nUse the module routers to navigate the published corpus.\n",
        encoding="utf-8",
    )
    release_tree.joinpath("AGENTS.md").write_text(
        "# Agents\n\nStart with llms.txt, then read each module map.\n",
        encoding="utf-8",
    )
    release_tree.joinpath("index.html").write_text(
        """
<!DOCTYPE html>
<html lang="en">
<body>
  <a href="README.md">./README.md</a>
  <a href="llms.txt">./llms.txt</a>
  <a href="llms-full.txt">./llms-full.txt</a>
</body>
</html>
""".strip(),
        encoding="utf-8",
    )

    for module in modules:
        module_dir = release_tree / module
        chunked_dir = module_dir / validate.config.MODULE_CHUNKED_REF_DIRNAME
        chunked_dir.mkdir(parents=True, exist_ok=True)
        module_dir.joinpath("llms.txt").write_text(
            "\n".join(
                [
                    f"# {module} module",
                    "> **Total Context:** ~10 tokens",
                    "",
                    "## Recommended Entry Points",
                    "",
                    f"- [map.md](./{validate.config.MODULE_MAP_FILENAME}): map (~1 tokens, l3-map)",
                    f"- [bundled-reference.md](./{validate.config.MODULE_BUNDLED_REF_FILENAME}): bundled (~1 tokens, l4-bundled)",
                    "",
                    "## Source Documents",
                    "",
                    f"- [topic.md](./{validate.config.MODULE_CHUNKED_REF_DIRNAME}/topic.md): topic (~1 tokens, l2-source)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        module_dir.joinpath(validate.config.MODULE_MAP_FILENAME).write_text(
            f"# {module} Navigation Map\n\nSee ./chunked-reference/topic.md.\n",
            encoding="utf-8",
        )
        module_dir.joinpath(validate.config.MODULE_BUNDLED_REF_FILENAME).write_text(
            f"# {module} Bundled Reference\n\nBroad context for {module}.\n",
            encoding="utf-8",
        )
        chunked_dir.joinpath("topic.md").write_text(
            f"# {module} Topic\n\nTargeted content for {module}.\n",
            encoding="utf-8",
        )

    return release_tree


def test_validate_release_tree_contract_accepts_minimal_release_tree(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_RELEASE_TREE", "true")
    validate = load_script_module(
        "validator_release_tree_contract_ok",
        "openwrt-docs4ai-08-validate-output.py",
    )

    build_release_tree(tmp_path, validate)

    hard_failures: list[str] = []
    validate.validate_release_tree_contract(
        str(tmp_path),
        hard_failures.append,
        lambda _message: None,
    )

    assert hard_failures == []


def test_validate_release_tree_contract_rejects_legacy_contract_leaks(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_RELEASE_TREE", "true")
    validate = load_script_module(
        "validator_release_tree_contract_legacy",
        "openwrt-docs4ai-08-validate-output.py",
    )

    release_tree = build_release_tree(tmp_path, validate, modules=MODULES[:3])
    release_tree.joinpath("README.md").write_text(
        "# Release Tree\n\nLegacy root: openwrt-condensed-docs\n",
        encoding="utf-8",
    )
    (release_tree / "ucode" / "ucode-skeleton.md").write_text(
        "# legacy skeleton\n",
        encoding="utf-8",
    )
    chunked_dir = release_tree / "ucode" / validate.config.MODULE_CHUNKED_REF_DIRNAME
    for path in chunked_dir.glob("*.md"):
        path.unlink()

    hard_failures: list[str] = []
    validate.validate_release_tree_contract(
        str(tmp_path),
        hard_failures.append,
        lambda _message: None,
    )

    assert any("expected at least 4 module directories" in failure for failure in hard_failures)
    assert any("legacy file names" in failure for failure in hard_failures)
    assert any("leaks legacy name" in failure for failure in hard_failures)
    assert any("chunked-reference is empty" in failure for failure in hard_failures)


def test_validate_index_html_contract_ignores_release_and_support_trees(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENABLE_RELEASE_TREE", "true")
    validate = load_script_module(
        "validator_release_tree_index_html_scope",
        "openwrt-docs4ai-08-validate-output.py",
    )

    for name in ["README.md", "AGENTS.md", "llms.txt", "llms-full.txt"]:
        (tmp_path / name).write_text(f"# {name}\n", encoding="utf-8")

    (tmp_path / "index.html").write_text(
        """
<!DOCTYPE html>
<html lang="en">
<body>
  <a href="README.md">./openwrt-condensed-docs/README.md</a>
  <a href="AGENTS.md">./openwrt-condensed-docs/AGENTS.md</a>
  <a href="llms.txt">./openwrt-condensed-docs/llms.txt</a>
  <a href="llms-full.txt">./openwrt-condensed-docs/llms-full.txt</a>
  <a href="index.html">./openwrt-condensed-docs/index.html</a>
</body>
</html>
""".strip(),
        encoding="utf-8",
    )

    release_tree = tmp_path / Path(validate.config.RELEASE_TREE_DIR).name
    release_tree.mkdir(parents=True)
    (release_tree / "llms.txt").write_text("# release-tree router\n", encoding="utf-8")

    support_tree = tmp_path / Path(validate.config.SUPPORT_TREE_DIR).name
    (support_tree / "telemetry").mkdir(parents=True)
    (support_tree / "telemetry" / "CHANGES.md").write_text(
        "# changes\n",
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.validate_index_html_contract(str(tmp_path), hard_failures.append)

    assert hard_failures == []


def test_release_tree_module_rewrite_updates_visible_router_labels() -> None:
    release_tree = load_script_module(
        "release_tree_module_rewrite_labels",
        "openwrt-docs4ai-05e-assemble-release-tree.py",
    )

    content = "\n".join(
        [
            "# procd",
            "- [procd-skeleton.md](./procd-skeleton.md)",
            "- [procd-complete-reference.md](./procd-complete-reference.md)",
            "- [procd.d.ts](./procd.d.ts)",
        ]
    )

    updated = release_tree.rewrite_module_text(content, "procd")

    assert "procd-skeleton.md" not in updated
    assert "procd-complete-reference.md" not in updated
    assert "[map.md](./map.md)" in updated
    assert "[bundled-reference.md](./bundled-reference.md)" in updated
    assert "[types/procd.d.ts](./types/procd.d.ts)" in updated


def test_build_release_tree_index_html_reflects_release_layout(tmp_path: Path) -> None:
    release_tree = load_script_module(
        "release_tree_index_html_builder",
        "openwrt-docs4ai-05e-assemble-release-tree.py",
    )

    root = tmp_path / "release-tree"
    (root / "procd" / release_tree.config.MODULE_CHUNKED_REF_DIRNAME).mkdir(parents=True)
    (root / "procd" / release_tree.config.MODULE_TYPES_DIRNAME).mkdir(parents=True)

    for name in ["README.md", "llms.txt", "llms-full.txt", "AGENTS.md"]:
        (root / name).write_text(f"# {name}\n", encoding="utf-8")

    (root / "procd" / "llms.txt").write_text("# procd\n", encoding="utf-8")
    (root / "procd" / release_tree.config.MODULE_MAP_FILENAME).write_text(
        "# map\n",
        encoding="utf-8",
    )
    (root / "procd" / release_tree.config.MODULE_BUNDLED_REF_FILENAME).write_text(
        "# bundled\n",
        encoding="utf-8",
    )
    (root / "procd" / release_tree.config.MODULE_CHUNKED_REF_DIRNAME / "topic.md").write_text(
        "# topic\n",
        encoding="utf-8",
    )
    (root / "procd" / release_tree.config.MODULE_TYPES_DIRNAME / "procd.d.ts").write_text(
        "export {};\n",
        encoding="utf-8",
    )

    html = release_tree.build_release_tree_index_html(root, ["procd"])

    assert "openwrt-condensed-docs" not in html
    assert "L1-raw" not in html
    assert "L2-semantic" not in html
    assert "./README.md" in html
    assert "./procd/map.md" in html
    assert "./procd/bundled-reference.md" in html
    assert "./procd/chunked-reference/topic.md" in html


def test_release_include_overlay_copies_files_into_release_tree(tmp_path: Path) -> None:
    release_tree = load_script_module(
        "release_tree_include_overlay",
        "openwrt-docs4ai-05e-assemble-release-tree.py",
    )

    release_root = tmp_path / "release-tree"
    release_root.mkdir(parents=True)
    release_root.joinpath("README.md").write_text("# generated\n", encoding="utf-8")

    include_root = tmp_path / "release-include"
    include_root.joinpath("nested").mkdir(parents=True)
    include_root.joinpath("README.md").write_text("# overlaid\n", encoding="utf-8")
    include_root.joinpath("nested", "marker.txt").write_text(
        "overlay marker\n",
        encoding="utf-8",
    )

    copied = release_tree.apply_release_include_overlay(
        str(release_root),
        str(include_root),
    )

    assert copied == ["README.md", "nested/marker.txt"]
    assert release_root.joinpath("README.md").read_text(encoding="utf-8") == "# overlaid\n"
    assert (
        release_root.joinpath("nested", "marker.txt").read_text(encoding="utf-8")
        == "overlay marker\n"
    )