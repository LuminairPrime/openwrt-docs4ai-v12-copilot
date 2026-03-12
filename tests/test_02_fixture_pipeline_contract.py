from pathlib import Path

from smoke_support import assert_fixture_outputs, build_env, run_named_script, seed_l1_fixtures

from pipeline_test_support import PROJECT_ROOT, load_script_module


ROUTING_PIPELINE = [
    "openwrt-docs4ai-03-normalize-semantic.py",
    "openwrt-docs4ai-05a-assemble-references.py",
    "openwrt-docs4ai-05b-generate-agents-and-readme.py",
    "openwrt-docs4ai-05c-generate-ucode-ide-schemas.py",
    "openwrt-docs4ai-05d-generate-api-drift-changelog.py",
    "openwrt-docs4ai-06-generate-llm-routing-indexes.py",
    "openwrt-docs4ai-07-generate-web-index.py",
    "openwrt-docs4ai-08-validate-output.py",
]


def run_fixture_pipeline(tmp_path):
    workdir = tmp_path / "work"
    outdir = tmp_path / "out"
    workdir.mkdir()
    outdir.mkdir()

    seed_l1_fixtures(str(workdir))
    env = build_env(str(workdir), str(outdir), run_ai=False)

    for script in ROUTING_PIPELINE:
        result = run_named_script(script, env, str(PROJECT_ROOT))
        assert result.returncode == 0, result.stderr or result.stdout

    return outdir


def test_fixture_pipeline_generates_structured_llm_routing_outputs(tmp_path):
    outdir = run_fixture_pipeline(tmp_path)

    assert_fixture_outputs(str(outdir), expect_ai=False)

    root_llms = (outdir / "llms.txt").read_text(encoding="utf-8")
    assert "./ucode/llms.txt" in root_llms
    assert "./procd/llms.txt" in root_llms

    module_llms = (outdir / "ucode" / "llms.txt").read_text(encoding="utf-8")
    assert "## Recommended Entry Points" in module_llms
    assert "## Tooling Surfaces" in module_llms
    assert "## Source Documents" in module_llms

    llms_full = (outdir / "llms-full.txt").read_text(encoding="utf-8")
    assert "./AGENTS.md" in llms_full
    assert "./README.md" in llms_full
    assert "./ucode/ucode.d.ts" in llms_full
    assert "./L2-semantic/wiki/wiki_page-service-events.md" in llms_full


def test_validator_rejects_module_indexes_missing_source_documents(tmp_path):
    outdir = run_fixture_pipeline(tmp_path)
    broken_index = outdir / "ucode" / "llms.txt"
    broken_index.write_text(
        broken_index.read_text(encoding="utf-8").replace(
            "- [c_source-api-fs.md](../L2-semantic/ucode/c_source-api-fs.md)",
            "- [c_source-api-fs.md](./missing.md)",
            1,
        ),
        encoding="utf-8",
    )

    validate = load_script_module(
        "validator_fixture_contract", "openwrt-docs4ai-08-validate-output.py"
    )
    _, hard_failures, _ = validate.validate_outdir(str(outdir))

    assert any("Module llms.txt missing L2 source entries for ucode" in failure for failure in hard_failures)