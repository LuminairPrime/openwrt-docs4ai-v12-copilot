import re

import pytest

from pipeline_test_support import (
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


def test_only_deploy_job_elevates_pages_permissions():
    workflow = load_workflow_yaml()
    jobs = workflow["jobs"]

    assert jobs["deploy"]["permissions"] == {
        "contents": "write",
        "pages": "write",
        "id-token": "write",
    }

    for job_name, job_config in jobs.items():
        if job_name == "deploy":
            continue
        assert "permissions" not in job_config