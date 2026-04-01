from tests.support.pytest_pipeline_support import PROJECT_ROOT, load_script_module
from tests.support.smoke_pipeline_support import (
    assert_fixture_outputs,
    build_env,
    run_named_script,
    seed_l1_fixtures,
)


ROUTING_PIPELINE = [
    "openwrt-docs4ai-03-normalize-semantic.py",
    "openwrt-docs4ai-05a-assemble-references.py",
    "openwrt-docs4ai-05b-generate-agents-and-readme.py",
    "openwrt-docs4ai-05c-generate-ucode-ide-schemas.py",
    "openwrt-docs4ai-05d-generate-api-drift-changelog.py",
    "openwrt-docs4ai-06-generate-llm-routing-indexes.py",
    "openwrt-docs4ai-07-generate-web-index.py",
    "openwrt-docs4ai-08-validate-output.py",
    "openwrt-docs4ai-09-build-packages.py",
]


def run_fixture_pipeline(tmp_path):
    workdir = tmp_path / "downloads"
    processed_dir = tmp_path / "processed"
    outdir = tmp_path / "staged"
    workdir.mkdir()
    processed_dir.mkdir()
    outdir.mkdir()

    seed_l1_fixtures(str(workdir), str(processed_dir))
    env = build_env(
        str(workdir),
        str(outdir),
        run_ai=False,
        processed_dir=str(processed_dir),
        pipeline_run_dir=str(tmp_path),
    )

    for script in ROUTING_PIPELINE:
        result = run_named_script(script, env, str(PROJECT_ROOT))
        assert result.returncode == 0, result.stderr or result.stdout

    return outdir, processed_dir


def test_fixture_pipeline_generates_structured_llm_routing_outputs(tmp_path):
    outdir, processed_dir = run_fixture_pipeline(tmp_path)
    publish_dir = outdir / "release-tree"

    assert_fixture_outputs(str(outdir), str(processed_dir), expect_ai=False)

    root_llms = (publish_dir / "llms.txt").read_text(encoding="utf-8")
    assert "./ucode/llms.txt" in root_llms
    assert "./procd/llms.txt" in root_llms

    module_llms = (publish_dir / "ucode" / "llms.txt").read_text(encoding="utf-8")
    assert "## Recommended Entry Points" in module_llms
    assert "## Tooling Surfaces" in module_llms
    assert "## Source Documents" in module_llms

    llms_full = (publish_dir / "llms-full.txt").read_text(encoding="utf-8")
    assert "./AGENTS.md" in llms_full
    assert "./README.md" in llms_full
    assert "./ucode/types/ucode.d.ts" in llms_full
    assert "./wiki/chunked-reference/wiki_page-service-events.md" in llms_full


def test_validator_rejects_module_indexes_missing_source_documents(tmp_path):
    outdir, _processed_dir = run_fixture_pipeline(tmp_path)
    publish_dir = outdir / "release-tree"
    broken_index = publish_dir / "ucode" / "llms.txt"
    broken_index.write_text(
        broken_index.read_text(encoding="utf-8").replace(
            "- [c_source-api-fs.md](./chunked-reference/c_source-api-fs.md)",
            "- [c_source-api-fs.md](./missing.md)",
            1,
        ),
        encoding="utf-8",
    )

    validate = load_script_module("validator_fixture_contract", "openwrt-docs4ai-08-validate-output.py")
    hard_failures: list[str] = []
    validate.validate_release_tree_contract(
        str(outdir),
        hard_failures.append,
        lambda _message: None,
    )

    assert any("release-tree module llms.txt missing source entries for ucode" in failure for failure in hard_failures)
