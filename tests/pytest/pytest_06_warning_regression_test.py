from __future__ import annotations

from pathlib import Path

from tests.support.pytest_pipeline_support import (
    load_script_module,
    load_workflow_text,
)


def test_workflow_uses_node24_native_action_majors() -> None:
    workflow_text = load_workflow_text()

    expected_versions = [
        "actions/checkout@v5",
        "actions/setup-python@v6",
        "actions/cache@v5",
        "actions/upload-artifact@v6",
        "actions/download-artifact@v7",
        "actions/create-github-app-token@v2",
    ]
    removed_versions = [
        "actions/checkout@v4",
        "actions/setup-python@v5",
        "actions/cache@v4",
        "actions/upload-artifact@v4",
        "actions/download-artifact@v4",
        "actions/upload-pages-artifact@v3",
        "actions/upload-pages-artifact@v4",
        "actions/configure-pages@v5",
        "actions/deploy-pages@v4",
    ]

    for action_ref in expected_versions:
        assert action_ref in workflow_text
    for action_ref in removed_versions:
        assert action_ref not in workflow_text

    assert "Publish GitHub Pages branch mirror" in workflow_text
    assert "GH_PAGES_BRANCH: gh-pages" in workflow_text
    assert "git worktree add" in workflow_text
    assert "openwrt-docs4ai/corpus" in workflow_text
    assert "openwrt-docs4ai/openwrt-docs4ai.github.io" in workflow_text
    assert "release-inputs/pages-include" in workflow_text
    assert "Build dated distribution ZIP" in workflow_text
    assert "gh release upload" in workflow_text
    assert "--clobber" in workflow_text


def test_assemble_references_shards_oversized_modules() -> None:
    assemble = load_script_module(
        "assemble_references_warning_contract",
        "openwrt-docs4ai-05a-assemble-references.py",
    )

    layout = assemble.build_reference_layout(
        "wiki",
        [
            {"token_count": 60_000, "body_text": "# One"},
            {"token_count": 55_000, "body_text": "# Two"},
            {"token_count": 30_000, "body_text": "# Three"},
        ],
        token_limit=100_000,
    )

    assert layout["sharded"] is True
    assert layout["total_token_count"] == 145_000
    assert [part["part_number"] for part in layout["parts"]] == [1, 2]
    assert [part["token_count"] for part in layout["parts"]] == [60_000, 85_000]
    assert assemble.release_part_filename(1) == "bundled-reference.part-01.md"


def test_validate_known_dockerman_ucode_false_positive_is_exact() -> None:
    validate = load_script_module(
        "validator_known_ucode_false_positive",
        "openwrt-docs4ai-08-validate-output.py",
    )

    rel_path = (
        "L2-semantic/luci-examples/"
        "example_app-luci-app-dockerman-root-usr-share-rpcd-ucode-docker-rpc-uc.md"
    )

    assert validate.is_known_ucode_false_positive(
        rel_path,
        "Syntax error: return must be inside function body",
    )
    assert not validate.is_known_ucode_false_positive(
        rel_path,
        "Syntax error: unexpected token",
    )
    assert not validate.is_known_ucode_false_positive(
        "L2-semantic/luci-examples/other.md",
        "Syntax error: return must be inside function body",
    )


def test_validate_routing_requires_sharded_part_links(tmp_path: Path) -> None:
    validate = load_script_module(
        "validator_sharded_reference_contract",
        "openwrt-docs4ai-08-validate-output.py",
    )

    release_tree_dir = tmp_path
    module_dir = release_tree_dir / "wiki"
    chunked_dir = module_dir / validate.config.MODULE_CHUNKED_REF_DIRNAME
    module_dir.mkdir(parents=True)
    chunked_dir.mkdir(parents=True)

    (chunked_dir / "sample.md").write_text(
        "---\ntoken_count: 10\n---\n# Sample\n\nBody text.\n",
        encoding="utf-8",
    )
    (module_dir / validate.config.MODULE_MAP_FILENAME).write_text(
        "# map\n",
        encoding="utf-8",
    )
    (module_dir / validate.config.MODULE_BUNDLED_REF_FILENAME).write_text(
        "# complete reference index\n",
        encoding="utf-8",
    )
    (module_dir / "bundled-reference.part-01.md").write_text(
        "# complete reference part 1\n",
        encoding="utf-8",
    )
    (module_dir / "llms.txt").write_text(
        "\n".join(
            [
                "# wiki module",
                "> Example wiki module",
                "> **Total Context:** ~10 tokens",
                "",
                "## Recommended Entry Points",
                "",
                "- [map.md](./map.md): map (~1 tokens, l3-map)",
                "- [bundled-reference.md](./bundled-reference.md): index (~1 tokens, l4-bundled)",
                "",
                "## Source Documents",
                "",
                "- [sample.md](./chunked-reference/sample.md): sample (~1 tokens, l2-source)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (release_tree_dir / "llms-full.txt").write_text(
        "\n".join(
            [
                "# openwrt-docs4ai - Complete Flat Catalog",
                "",
                "- [wiki/llms.txt](./wiki/llms.txt): module index (~1 tokens, l3-module-index)",
                "- [map.md](./wiki/map.md): map (~1 tokens, l3-map)",
                "- [bundled-reference.md](./wiki/bundled-reference.md): index (~1 tokens, l4-bundled)",
                "- [sample.md](./wiki/chunked-reference/sample.md): sample (~1 tokens, l2-source)",
                "",
            ]
        ),
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.validate_release_module_llms_contract(
        str(release_tree_dir),
        ["wiki"],
        hard_failures.append,
        lambda _message: None,
    )
    validate.validate_release_llms_full_contract(
        str(release_tree_dir),
        ["wiki"],
        hard_failures.append,
        lambda _message: None,
    )

    assert any(
        "bundled-reference.part-01.md" in failure for failure in hard_failures
    )


def test_validate_index_html_requires_full_publish_mirror(tmp_path: Path) -> None:
    validate = load_script_module(
        "validator_index_html_mirror_contract",
        "openwrt-docs4ai-08-validate-output.py",
    )

    release_tree_dir = tmp_path
    (release_tree_dir / "README.md").write_text("# README\n", encoding="utf-8")
    (release_tree_dir / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (release_tree_dir / "llms.txt").write_text(
        "# openwrt-docs4ai - LLM Routing Index\n\n"
        "[llms-full.txt](./llms-full.txt)\n\n"
        "## Modules\n\n"
        "- [wiki](./wiki/llms.txt): wiki entry (~1 tokens)\n",
        encoding="utf-8",
    )
    (release_tree_dir / "llms-full.txt").write_text(
        "# openwrt-docs4ai - Complete Flat Catalog\n\n"
        "- [README.md](./README.md): readme (~1 tokens)\n"
        "- [wiki/llms.txt](./wiki/llms.txt): module index (~1 tokens)\n",
        encoding="utf-8",
    )
    (release_tree_dir / "wiki").mkdir()
    (release_tree_dir / "wiki" / "llms.txt").write_text(
        "# wiki module\n"
        "> **Total Context:** ~1 tokens\n\n"
        "## Source Documents\n\n"
        "- [topic.md](./chunked-reference/topic.md): topic (~1 tokens, l2-source)\n",
        encoding="utf-8",
    )
    (release_tree_dir / "index.html").write_text(
        """
<!DOCTYPE html>
<html lang="en">
<body>
  <a href="README.md">./README.md</a>
</body>
</html>
""".strip(),
        encoding="utf-8",
    )

    hard_failures: list[str] = []
    validate.validate_release_index_html_contract(
        str(release_tree_dir),
        hard_failures.append,
    )

    assert any(
        "release-tree index.html missing mirrored publish links" in failure
        for failure in hard_failures
    )