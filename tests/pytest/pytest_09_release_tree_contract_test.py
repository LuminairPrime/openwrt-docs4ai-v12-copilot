from __future__ import annotations

from pathlib import Path

from tests.support.pytest_pipeline_support import load_script_module


MODULES = ["procd", "uci", "ucode", "wiki"]


def build_release_tree(outdir: Path, validate, modules: list[str] | None = None) -> Path:
    modules = modules or MODULES
    release_tree = outdir / Path(validate.config.RELEASE_TREE_DIR).name
    release_tree.mkdir(parents=True, exist_ok=True)

    llms_full_entries = [
        "- [README.md](./README.md): release readme (~10 tokens, l3-root)",
        "- [AGENTS.md](./AGENTS.md): agent routing (~10 tokens, l3-root)",
    ]
    html_links = [
        '<a href="README.md">./README.md</a>',
        '<a href="AGENTS.md">./AGENTS.md</a>',
        '<a href="llms.txt">./llms.txt</a>',
        '<a href="llms-full.txt">./llms-full.txt</a>',
        '<a href="index.html">./index.html</a>',
    ]
    llms_entries = "\n".join(
        f"- [{module}](./{module}/llms.txt): {module} entry (~10 tokens)"
        for module in modules
    )
    release_tree.joinpath("llms.txt").write_text(
        "# openwrt-docs4ai - LLM Routing Index\n\n"
        "[llms-full.txt](./llms-full.txt)\n\n"
        "## Modules\n\n"
        f"{llms_entries}\n\n"
        + ("routing-contract\n" * 40),
        encoding="utf-8",
    )
    release_tree.joinpath("README.md").write_text(
        "# Release Tree\n\nUse the module routers to navigate the published corpus.\n",
        encoding="utf-8",
    )
    release_tree.joinpath("AGENTS.md").write_text(
        "# Agents\n\n"
        "Start with llms.txt and llms-full.txt, then read [module]/llms.txt for map.md, "
        "bundled-reference.md, chunked-reference/, and types/*.d.ts.\n",
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
        llms_full_entries.extend(
            [
                f"- [llms.txt](./{module}/llms.txt): module router (~10 tokens, l3-module-index)",
                f"- [map.md](./{module}/map.md): navigation map (~10 tokens, l3-map)",
                f"- [bundled-reference.md](./{module}/bundled-reference.md): bundled reference (~10 tokens, l4-bundled)",
                f"- [topic.md](./{module}/chunked-reference/topic.md): topic page (~10 tokens, l2-source)",
            ]
        )
        html_links.extend(
            [
                f'<a href="{module}/llms.txt">./{module}/llms.txt</a>',
                f'<a href="{module}/map.md">./{module}/map.md</a>',
                f'<a href="{module}/bundled-reference.md">./{module}/bundled-reference.md</a>',
                f'<a href="{module}/chunked-reference/topic.md">./{module}/chunked-reference/topic.md</a>',
            ]
        )

    llms_full_content = "\n".join(llms_full_entries)
    release_tree.joinpath("llms-full.txt").write_text(
        "# openwrt-docs4ai - Complete Flat Catalog\n\n"
        f"{llms_full_content}\n",
        encoding="utf-8",
    )
    release_tree.joinpath("index.html").write_text(
        "\n".join(
            [
                "<!DOCTYPE html>",
                '<html lang="en">',
                "<body>",
                *[f"  {link}" for link in html_links],
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )

    return release_tree


def seed_support_tree_sources(outdir: Path) -> None:
    l1_raw = outdir / "L1-raw" / "ucode"
    l2_semantic = outdir / "L2-semantic" / "wiki"
    l1_raw.mkdir(parents=True, exist_ok=True)
    l2_semantic.mkdir(parents=True, exist_ok=True)

    l1_raw.joinpath("c_source-api-fs.md").write_text("# raw\n", encoding="utf-8")
    l1_raw.joinpath("c_source-api-fs.meta.json").write_text("{}\n", encoding="utf-8")
    l2_semantic.joinpath("wiki_page-service-events.md").write_text(
        "---\ntitle: wiki\nmodule: wiki\norigin_type: wiki\ntoken_count: 1\nsource_commit: abc1234\n---\n",
        encoding="utf-8",
    )
    outdir.joinpath("cross-link-registry.json").write_text("{}\n", encoding="utf-8")
    outdir.joinpath("repo-manifest.json").write_text("{}\n", encoding="utf-8")
    outdir.joinpath("CHANGES.md").write_text("# changes\n", encoding="utf-8")
    outdir.joinpath("changelog.json").write_text("{}\n", encoding="utf-8")
    outdir.joinpath("signature-inventory.json").write_text("{}\n", encoding="utf-8")


def build_support_tree(outdir: Path, validate) -> Path:
    seed_support_tree_sources(outdir)

    support_tree = outdir / Path(validate.config.SUPPORT_TREE_DIR).name
    (support_tree / "raw" / "ucode").mkdir(parents=True, exist_ok=True)
    (support_tree / "semantic-pages" / "wiki").mkdir(parents=True, exist_ok=True)
    (support_tree / "manifests").mkdir(parents=True, exist_ok=True)
    (support_tree / "telemetry").mkdir(parents=True, exist_ok=True)

    (support_tree / "raw" / "ucode" / "c_source-api-fs.md").write_text(
        "# raw\n",
        encoding="utf-8",
    )
    (support_tree / "raw" / "ucode" / "c_source-api-fs.meta.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    (support_tree / "semantic-pages" / "wiki" / "wiki_page-service-events.md").write_text(
        "---\ntitle: wiki\nmodule: wiki\norigin_type: wiki\ntoken_count: 1\nsource_commit: abc1234\n---\n",
        encoding="utf-8",
    )
    (support_tree / "manifests" / "cross-link-registry.json").write_text("{}\n", encoding="utf-8")
    (support_tree / "manifests" / "repo-manifest.json").write_text("{}\n", encoding="utf-8")
    (support_tree / "telemetry" / "CHANGES.md").write_text("# changes\n", encoding="utf-8")
    (support_tree / "telemetry" / "changelog.json").write_text("{}\n", encoding="utf-8")
    (support_tree / "telemetry" / "signature-inventory.json").write_text("{}\n", encoding="utf-8")
    return support_tree


def test_validate_release_tree_contract_accepts_minimal_release_tree(
    tmp_path: Path,
) -> None:
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


def test_validate_support_tree_contract_rejects_mirror_mismatch(tmp_path: Path) -> None:
    validate = load_script_module(
        "validator_support_tree_contract_mismatch",
        "openwrt-docs4ai-08-validate-output.py",
    )
    outdir = tmp_path / "out"
    outdir.mkdir()

    build_support_tree(outdir, validate)
    (outdir / "L1-raw" / "ucode" / "extra.md").write_text("# extra\n", encoding="utf-8")

    hard_failures: list[str] = []
    validate.validate_support_tree_contract(outdir, hard_failures.append, lambda _msg: None)

    assert any("support-tree raw/ missing mirrored files" in failure for failure in hard_failures)


def test_validate_support_tree_contract_rejects_manifest_content_mismatch(tmp_path: Path) -> None:
    validate = load_script_module(
        "validator_support_tree_contract_manifest_mismatch",
        "openwrt-docs4ai-08-validate-output.py",
    )
    outdir = tmp_path / "out"
    outdir.mkdir()

    support_tree = build_support_tree(outdir, validate)
    (support_tree / "manifests" / "cross-link-registry.json").write_text(
        '{"stale": true}\n',
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.validate_support_tree_contract(outdir, hard_failures.append, lambda _msg: None)

    assert any("support-tree content mismatch: manifests/cross-link-registry.json" in failure for failure in hard_failures)


def test_validate_release_tree_contract_rejects_legacy_contract_leaks(
    tmp_path: Path,
) -> None:
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


def test_validate_support_tree_contract_accepts_materialized_support_tree(tmp_path: Path) -> None:
    validate = load_script_module(
        "validator_support_tree_contract_ok",
        "openwrt-docs4ai-08-validate-output.py",
    )
    outdir = tmp_path / "out"
    outdir.mkdir()

    build_support_tree(outdir, validate)

    hard_failures: list[str] = []
    validate.validate_support_tree_contract(outdir, hard_failures.append, lambda _msg: None)

    assert hard_failures == []


def test_copy_support_tree_materializes_validator_compatible_support_tree(
    tmp_path: Path,
) -> None:
    release_tree_index = load_script_module(
        "support_tree_materializer",
        "openwrt-docs4ai-07-generate-web-index.py",
    )
    validate = load_script_module(
        "support_tree_materializer_validator",
        "openwrt-docs4ai-08-validate-output.py",
    )
    outdir = tmp_path / "out"
    outdir.mkdir()

    seed_support_tree_sources(outdir)

    support_tree = outdir / Path(validate.config.SUPPORT_TREE_DIR).name
    release_tree_index.copy_support_tree(outdir=outdir, support_tree_dir=support_tree)

    hard_failures: list[str] = []
    validate.validate_support_tree_contract(outdir, hard_failures.append, lambda _msg: None)

    assert hard_failures == []
    assert support_tree.joinpath("manifests", "cross-link-registry.json").read_text(
        encoding="utf-8"
    ) == "{}\n"
    assert support_tree.joinpath("telemetry", "signature-inventory.json").read_text(
        encoding="utf-8"
    ) == "{}\n"


def test_validate_release_tree_contract_requires_module_set_match(tmp_path: Path) -> None:
    validate = load_script_module(
        "validator_release_tree_contract_module_set",
        "openwrt-docs4ai-08-validate-output.py",
    )

    for module in MODULES:
        module_dir = tmp_path / "L2-semantic" / module
        module_dir.mkdir(parents=True, exist_ok=True)
        module_dir.joinpath("topic.md").write_text("# topic\n", encoding="utf-8")

    build_release_tree(tmp_path, validate, modules=["procd", "uci", "ucode", "bogus"])

    hard_failures: list[str] = []
    validate.validate_release_tree_contract(
        str(tmp_path),
        hard_failures.append,
        lambda _message: None,
    )

    assert any("release-tree module set mismatch" in failure for failure in hard_failures)


def test_validate_index_html_contract_ignores_release_and_support_trees(
    tmp_path: Path,
) -> None:
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

def test_build_release_tree_index_html_reflects_release_layout(tmp_path: Path) -> None:
    release_tree_index = load_script_module(
        "release_tree_index_html_builder",
        "openwrt-docs4ai-07-generate-web-index.py",
    )

    root = tmp_path / "release-tree"
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME).mkdir(parents=True)
    (root / "procd" / release_tree_index.config.MODULE_TYPES_DIRNAME).mkdir(parents=True)

    for name in ["README.md", "llms.txt", "llms-full.txt", "AGENTS.md"]:
        (root / name).write_text(f"# {name}\n", encoding="utf-8")

    (root / "procd" / "llms.txt").write_text("# procd\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_MAP_FILENAME).write_text(
        "# map\n",
        encoding="utf-8",
    )
    (root / "procd" / release_tree_index.config.MODULE_BUNDLED_REF_FILENAME).write_text(
        "# bundled\n",
        encoding="utf-8",
    )
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME / "topic.md").write_text(
        "# topic\n",
        encoding="utf-8",
    )
    (root / "procd" / release_tree_index.config.MODULE_TYPES_DIRNAME / "procd.d.ts").write_text(
        "export {};\n",
        encoding="utf-8",
    )

    html = release_tree_index.build_release_tree_html(root)

    assert "openwrt-condensed-docs" not in html
    assert "L1-raw" not in html
    assert "L2-semantic" not in html
    assert "./README.md" in html
    assert "./procd/map.md" in html
    assert "./procd/bundled-reference.md" in html
    assert "./procd/chunked-reference/topic.md" in html


def test_release_include_overlay_copies_files_into_release_tree(tmp_path: Path) -> None:
    release_tree_index = load_script_module(
        "release_tree_include_overlay",
        "openwrt-docs4ai-07-generate-web-index.py",
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

    copied = release_tree_index.apply_release_include_overlay(
        str(release_root),
        str(include_root),
    )

    assert sorted(copied) == ["README.md", "nested/marker.txt"]
    assert release_root.joinpath("README.md").read_text(encoding="utf-8") == "# overlaid\n"
    assert (
        release_root.joinpath("nested", "marker.txt").read_text(encoding="utf-8")
        == "overlay marker\n"
    )


def test_finalize_release_tree_indexes_additive_overlay_files(tmp_path: Path) -> None:
    release_tree_index = load_script_module(
        "release_tree_finalize_overlay_indexing",
        "openwrt-docs4ai-07-generate-web-index.py",
    )
    validate = load_script_module(
        "release_tree_finalize_overlay_indexing_validator",
        "openwrt-docs4ai-08-validate-output.py",
    )

    root = tmp_path / "release-tree"
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME).mkdir(parents=True)
    for name in ["README.md", "llms.txt", "llms-full.txt", "AGENTS.md"]:
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "procd" / "llms.txt").write_text("# procd\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_MAP_FILENAME).write_text("# map\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_BUNDLED_REF_FILENAME).write_text("# bundled\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME / "topic.md").write_text("# topic\n", encoding="utf-8")
    root.joinpath("index.html").write_text("<html>stale</html>\n", encoding="utf-8")

    include_root = tmp_path / "release-include"
    include_root.joinpath("extras").mkdir(parents=True)
    include_root.joinpath("extras", "marker.txt").write_text("overlay marker\n", encoding="utf-8")

    copied = release_tree_index.finalize_release_tree(root, include_root)

    hard_failures: list[str] = []
    validate.validate_release_index_html_contract(str(root), hard_failures.append)

    assert copied == ["extras/marker.txt"]
    assert hard_failures == []
    assert './extras/marker.txt' in root.joinpath("index.html").read_text(encoding="utf-8")


def test_finalize_release_tree_rebuilds_stale_index_without_overlay(tmp_path: Path) -> None:
    release_tree_index = load_script_module(
        "release_tree_finalize_regeneration",
        "openwrt-docs4ai-07-generate-web-index.py",
    )
    validate = load_script_module(
        "release_tree_finalize_regeneration_validator",
        "openwrt-docs4ai-08-validate-output.py",
    )

    root = tmp_path / "release-tree"
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME).mkdir(parents=True)
    for name in ["README.md", "llms.txt", "llms-full.txt", "AGENTS.md"]:
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "procd" / "llms.txt").write_text("# procd\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_MAP_FILENAME).write_text("# map\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_BUNDLED_REF_FILENAME).write_text("# bundled\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME / "topic.md").write_text("# topic\n", encoding="utf-8")
    stale_index = "<html>stale index</html>\n"
    root.joinpath("index.html").write_text(stale_index, encoding="utf-8")

    copied = release_tree_index.finalize_release_tree(root, tmp_path / "missing-overlay")

    hard_failures: list[str] = []
    validate.validate_release_index_html_contract(str(root), hard_failures.append)

    rendered_index = root.joinpath("index.html").read_text(encoding="utf-8")
    assert copied == []
    assert hard_failures == []
    assert rendered_index != stale_index
    assert "./procd/map.md" in rendered_index


def test_release_overlay_can_override_generated_release_index(tmp_path: Path) -> None:
    release_tree_index = load_script_module(
        "release_tree_overlay_precedence",
        "openwrt-docs4ai-07-generate-web-index.py",
    )

    root = tmp_path / "release-tree"
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME).mkdir(parents=True)
    for name in ["README.md", "llms.txt", "llms-full.txt", "AGENTS.md"]:
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "procd" / "llms.txt").write_text("# procd\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_MAP_FILENAME).write_text("# map\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_BUNDLED_REF_FILENAME).write_text("# bundled\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME / "topic.md").write_text("# topic\n", encoding="utf-8")

    include_root = tmp_path / "release-include"
    include_root.mkdir()
    include_root.joinpath("index.html").write_text("<html>overlay index</html>\n", encoding="utf-8")

    release_tree_index.finalize_release_tree(root, include_root)

    assert (root / "index.html").read_text(encoding="utf-8") == "<html>overlay index</html>\n"


def test_release_overlay_index_rejects_parent_directory_links(tmp_path: Path) -> None:
    release_tree_index = load_script_module(
        "release_tree_overlay_parent_escape",
        "openwrt-docs4ai-07-generate-web-index.py",
    )
    validate = load_script_module(
        "release_tree_overlay_parent_escape_validator",
        "openwrt-docs4ai-08-validate-output.py",
    )

    root = tmp_path / "release-tree"
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME).mkdir(parents=True)
    for name in ["README.md", "llms.txt", "llms-full.txt", "AGENTS.md"]:
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "procd" / "llms.txt").write_text("# procd\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_MAP_FILENAME).write_text("# map\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_BUNDLED_REF_FILENAME).write_text("# bundled\n", encoding="utf-8")
    (root / "procd" / release_tree_index.config.MODULE_CHUNKED_REF_DIRNAME / "topic.md").write_text("# topic\n", encoding="utf-8")

    include_root = tmp_path / "release-include"
    include_root.mkdir()
    include_root.joinpath("index.html").write_text(
        '<html><body><a href="../README.md">../README.md</a></body></html>\n',
        encoding="utf-8",
    )

    release_tree_index.finalize_release_tree(root, include_root)

    hard_failures: list[str] = []
    validate.validate_release_index_html_contract(str(root), hard_failures.append)

    assert any("contains hrefs outside the publish tree" in failure for failure in hard_failures)
    assert any("../README.md" in failure for failure in hard_failures)


def test_check_dead_links_reports_broken_relative_link(tmp_path: Path) -> None:
    validate = load_script_module(
        "check_dead_links_broken",
        "openwrt-docs4ai-08-validate-output.py",
    )

    release_tree = tmp_path / "release-tree"
    release_tree.mkdir(parents=True)
    release_tree.joinpath("page.md").write_text(
        "# Page\n\nSee [missing](./nonexistent.md).\n",
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.check_dead_links(str(release_tree), hard_failures.append)

    assert any("Broken relative link" in f and "nonexistent.md" in f for f in hard_failures)


def test_check_dead_links_passes_valid_relative_link(tmp_path: Path) -> None:
    validate = load_script_module(
        "check_dead_links_valid",
        "openwrt-docs4ai-08-validate-output.py",
    )

    release_tree = tmp_path / "release-tree"
    release_tree.mkdir(parents=True)
    release_tree.joinpath("target.md").write_text("# Target\n", encoding="utf-8")
    release_tree.joinpath("page.md").write_text(
        "# Page\n\nSee [target](./target.md).\n",
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.check_dead_links(str(release_tree), hard_failures.append)

    assert hard_failures == []


def test_check_dead_links_skips_external_and_anchor_links(tmp_path: Path) -> None:
    validate = load_script_module(
        "check_dead_links_skip_external",
        "openwrt-docs4ai-08-validate-output.py",
    )

    release_tree = tmp_path / "release-tree"
    release_tree.mkdir(parents=True)
    # External links and anchor-only links should not trigger failures
    release_tree.joinpath("page.md").write_text(
        "# Page\n\n"
        "See [external](https://openwrt.org/docs/guide.md).\n"
        "See [anchor](#section).\n",
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.check_dead_links(str(release_tree), hard_failures.append)

    assert hard_failures == []


def test_validate_release_tree_contract_rejects_broken_relative_link(tmp_path: Path) -> None:
    validate = load_script_module(
        "validator_release_tree_broken_link",
        "openwrt-docs4ai-08-validate-output.py",
    )

    release_tree = build_release_tree(tmp_path, validate)
    # Inject a broken link into the ucode map
    (release_tree / "ucode" / validate.config.MODULE_MAP_FILENAME).write_text(
        "# ucode Map\n\nSee [missing page](./chunked-reference/does-not-exist.md).\n",
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.validate_release_tree_contract(
        str(tmp_path),
        hard_failures.append,
        lambda _message: None,
    )

    assert any("Broken relative link" in f and "does-not-exist.md" in f for f in hard_failures)


# ---------------------------------------------------------------------------
# A8 — Source exclusion tests (Phase 10)
# ---------------------------------------------------------------------------

def test_source_exclusions_should_exclude_returns_true_for_policy_entry() -> None:
    """should_exclude returns True for a slug listed in config/source-exclusions.yml."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from lib import source_exclusions  # noqa: PLC0415
    # Reload to pick up any reset from other tests
    assert source_exclusions.should_exclude("wiki", "guide-developer-luci") is True
    assert source_exclusions.should_exclude("wiki", "techref-hotplug-legacy") is True
    assert source_exclusions.should_exclude("wiki", "guide-developer-20-xx-major-changes") is True


def test_source_exclusions_should_exclude_returns_false_for_non_excluded_slug() -> None:
    """should_exclude returns False for a slug that is not in the policy."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from lib import source_exclusions  # noqa: PLC0415
    assert source_exclusions.should_exclude("wiki", "guide-developer-helloworld") is False
    assert source_exclusions.should_exclude("wiki", "") is False


def test_source_exclusions_get_exclusion_reason_returns_string_for_excluded() -> None:
    """get_exclusion_reason returns a non-empty string for an excluded slug."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from lib import source_exclusions  # noqa: PLC0415
    reason = source_exclusions.get_exclusion_reason("wiki", "guide-developer-luci")
    assert reason is not None
    assert len(reason) > 0


def test_source_exclusions_get_exclusion_reason_returns_none_for_non_excluded() -> None:
    """get_exclusion_reason returns None for a slug not in policy."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from lib import source_exclusions  # noqa: PLC0415
    assert source_exclusions.get_exclusion_reason("wiki", "guide-user-beginners") is None


def test_source_exclusions_get_all_exclusions_returns_three_entries() -> None:
    """get_all_exclusions returns exactly the 3 seed entries."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from lib import source_exclusions  # noqa: PLC0415
    entries = source_exclusions.get_all_exclusions()
    assert len(entries) == 3
    sources = {e["source"] for e in entries}
    assert sources == {"wiki"}
