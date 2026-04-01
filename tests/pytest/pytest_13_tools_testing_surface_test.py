from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


def test_tools_testing_entrypoints_exist() -> None:
    expected_files = [
        "tools/testing/README.md",
        "tools/testing/run_default_validation.py",
        "tools/testing/run_source_validation.py",
        "tools/testing/run_targeted_pytest.py",
        "tools/testing/run_targeted_smoke.py",
    ]

    for relative_path in expected_files:
        assert (PROJECT_ROOT / relative_path).is_file(), relative_path


def test_tools_testing_readme_documents_canonical_commands() -> None:
    readme_text = (PROJECT_ROOT / "tools/testing/README.md").read_text(encoding="utf-8")

    assert "python tools/testing/run_default_validation.py" in readme_text
    assert "python tools/testing/run_source_validation.py" in readme_text
    assert "python tools/testing/run_targeted_pytest.py" in readme_text
    assert "python tools/testing/run_targeted_smoke.py" in readme_text
    assert "keep the executable suites in `tests/`" in readme_text


def test_source_validation_covers_tools_testing() -> None:
    lint_runner_text = (PROJECT_ROOT / "tests/check_linting.py").read_text(encoding="utf-8")
    pyright_config = json.loads((PROJECT_ROOT / "pyrightconfig.strict.json").read_text(encoding="utf-8"))

    assert '"tools/testing"' in lint_runner_text
    assert "tools/testing" in pyright_config["include"]


def test_tools_testing_scripts_expose_help() -> None:
    expected_wrappers = [
        "tools/testing/run_default_validation.py",
        "tools/testing/run_source_validation.py",
        "tools/testing/run_targeted_pytest.py",
        "tools/testing/run_targeted_smoke.py",
    ]

    for relative_path in expected_wrappers:
        completed = subprocess.run(
            [str(REPO_PYTHON), str(PROJECT_ROOT / relative_path), "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, relative_path
        assert "usage:" in completed.stdout.lower(), relative_path


def test_tools_testing_wrappers_lock_the_delegation_contract() -> None:
    expected_snippets = {
        "tools/testing/run_default_validation.py": [
            'run_repo_python("tests/check_linting.py", ["--strict"])',
            'run_repo_python("tests/run_smoke_and_pytest.py", local_validation_args)',
            'local_validation_args.append("--run-ai")',
            'local_validation_args.append("--keep-temp")',
            'local_validation_args.append("--include-extractors")',
        ],
        "tools/testing/run_source_validation.py": [
            'run_repo_python("tests/check_linting.py", ["--strict"])',
        ],
        "tools/testing/run_targeted_pytest.py": [
            'run_repo_python("tests/run_pytest.py", passthrough_args)',
        ],
        "tools/testing/run_targeted_smoke.py": [
            'run_repo_python("tests/run_smoke.py", passthrough_args)',
        ],
    }

    for relative_path, snippets in expected_snippets.items():
        wrapper_text = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in wrapper_text, f"{relative_path}: missing {snippet}"
