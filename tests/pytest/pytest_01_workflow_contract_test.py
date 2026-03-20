import ast
import re
import textwrap

import pytest

from tests.support.pytest_pipeline_support import (
    SCRIPTS_DIR,
    WORKFLOW_PATH,
    collect_workflow_script_invocations,
    get_workflow_job_block,
    load_smoke_support_module,
    load_workflow_yaml,
)


def test_smoke_selector_rejects_unknown_stage_id():
    smoke = load_smoke_support_module("smoke_support_unknown_selector")

    with pytest.raises(ValueError, match="does-not-exist"):
        smoke.select_pipeline_scripts(smoke.POST_EXTRACT_PIPELINE, "does-not-exist")


def test_smoke_selector_supports_stage_family_selector():
    smoke = load_smoke_support_module("smoke_support_stage_family")

    selected = smoke.select_pipeline_scripts(smoke.POST_EXTRACT_PIPELINE, "05")

    assert selected == [
        "openwrt-docs4ai-05a-assemble-references.py",
        "openwrt-docs4ai-05b-generate-agents-and-readme.py",
        "openwrt-docs4ai-05c-generate-ucode-ide-schemas.py",
        "openwrt-docs4ai-05d-generate-api-drift-changelog.py",
    ]


def test_full_pipeline_registry_matches_files_on_disk():
    smoke = load_smoke_support_module("smoke_support_registry")

    missing = [
        script for script in smoke.FULL_PIPELINE if not (SCRIPTS_DIR / script).is_file()
    ]

    assert missing == []


def test_full_pipeline_matches_workflow_invocations():
    smoke = load_smoke_support_module("smoke_support_workflow")
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow_scripts = collect_workflow_script_invocations(workflow_text)

    assert workflow_scripts == set(smoke.FULL_PIPELINE)


def test_extract_wiki_runs_without_initialize_dependency():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    wiki_block = get_workflow_job_block(workflow_text, "extract_wiki")

    assert re.search(r"^\s+needs:\s", wiki_block, flags=re.MULTILINE) is None


def test_process_waits_for_extract_and_extract_wiki():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    process_block = get_workflow_job_block(workflow_text, "process")

    assert "needs: [extract, extract_wiki]" in process_block


def test_process_uses_single_numbered_ai_stage_after_normalize():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    process_block = get_workflow_job_block(workflow_text, "process")

    assert "Detect committed AI store changes" not in process_block
    assert "Validate committed AI store against staged L2 (04b)" not in process_block
    assert "Audit committed AI store coverage (04a)" not in process_block
    assert "python .github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py" in process_block


def test_extract_matrix_fail_fast_is_disabled():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    extract_block = get_workflow_job_block(workflow_text, "extract")

    assert "fail-fast: false" in extract_block


def test_extract_contract_and_summary_artifacts_exist():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "extract-status-${{ matrix.script }}" in workflow_text
    assert "extract-status-02a-scrape-wiki.py" in workflow_text
    assert "name: extract-summary" in workflow_text
    assert "name: pipeline-summary" in workflow_text


def test_workflow_defaults_to_read_only_contents_permission():
    workflow = load_workflow_yaml()

    assert workflow["permissions"] == {"contents": "read"}


def test_only_deploy_job_elevates_contents_write_permissions():
    workflow = load_workflow_yaml()
    jobs = workflow["jobs"]

    assert jobs["deploy"]["permissions"] == {"contents": "write"}

    for job_name, job_config in jobs.items():
        if job_name == "deploy":
            continue
        assert "permissions" not in job_config


def test_deploy_serializes_publication_targets():
    workflow = load_workflow_yaml()
    deploy = workflow["jobs"]["deploy"]

    assert deploy["concurrency"] == {
        "group": "openwrt-docs4ai-deploy",
        "cancel-in-progress": False,
    }


def test_external_distribution_is_gated_to_main_and_secrets():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    deploy_block = get_workflow_job_block(workflow_text, "deploy")

    assert "Determine external distribution eligibility" in deploy_block
    assert 'refs/heads/main' in deploy_block
    assert "DIST_APP_ID_PRESENT" in deploy_block
    assert "DIST_APP_PRIVATE_KEY_PRESENT" in deploy_block


def test_external_distribution_runs_after_source_pages_mirror():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    deploy_block = get_workflow_job_block(workflow_text, "deploy")

    source_pages_index = deploy_block.index("Publish GitHub Pages branch mirror")
    external_distribution_index = deploy_block.index(
        "Determine external distribution eligibility"
    )

    assert source_pages_index < external_distribution_index


def test_process_summary_depends_on_validate_output_outcome():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    process_block = get_workflow_job_block(workflow_text, "process")

    assert "- name: Validate published output (08)" in process_block
    assert "id: validate_output" in process_block
    assert "- name: Validate staging contract and build process summary" in process_block
    assert "VALIDATE_OUTPUT_OUTCOME" not in process_block
    assert "if: ${{ always() }}" in process_block
    assert 'validate_output_outcome = "${{ steps.validate_output.outcome }}" or "unknown"' in process_block
    assert '"contract_ok": (not missing) and validate_output_outcome == "success"' in process_block
    assert 'payload["stage_timings"] = stage_timings' in process_block
    assert '(summary_dir / "process-summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")' in process_block
    assert process_block.index("- name: Validate published output (08)") < process_block.index(
        "- name: Validate staging contract and build process summary"
    )
    assert process_block.index('payload["stage_timings"] = stage_timings') < process_block.index(
        '(summary_dir / "process-summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")'
    )

    heredoc_match = re.search(
        r"python - <<'PY'\n(?P<body>.*?)\n\s+PY",
        process_block,
        flags=re.DOTALL,
    )
    assert heredoc_match is not None
    ast.parse(textwrap.dedent(heredoc_match.group("body")))


def test_pipeline_summary_reports_validate_output_outcome():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    pipeline_summary_block = get_workflow_job_block(workflow_text, "pipeline_summary")

    assert "process_summary.get('validate_output_outcome', 'unknown')" in pipeline_summary_block
    assert "- validate_output_outcome:" in pipeline_summary_block