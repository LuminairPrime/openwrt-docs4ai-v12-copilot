from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = PROJECT_ROOT / "tests"


def _resolve_repo_python() -> Path:
    if os.name == "nt":
        candidates = [PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"]
    else:
        candidates = [PROJECT_ROOT / ".venv" / "bin" / "python"]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return Path(sys.executable)


REPO_PYTHON = _resolve_repo_python()

PYTEST_TARGETS = [
    Path("tests/pytest/pytest_00_pipeline_units_test.py"),
    Path("tests/pytest/pytest_01_workflow_contract_test.py"),
    Path("tests/pytest/pytest_02_fixture_pipeline_contract_test.py"),
    Path("tests/pytest/pytest_03_wiki_corpus_sanity_test.py"),
    Path("tests/pytest/pytest_04_wiki_scraper_test.py"),
]

SMOKE_SCRIPTS = {
    "post_extract": Path("tests/smoke/smoke_00_post_extract_pipeline.py"),
    "full_local": Path("tests/smoke/smoke_01_full_local_pipeline.py"),
    "ai_store": Path("tests/smoke/smoke_02_ai_store_contract.py"),
}


@dataclass(frozen=True)
class StageSpec:
    label: str
    slug: str
    command: list[str]


@dataclass
class StageResult:
    index: int
    label: str
    slug: str
    command: list[str]
    log_file: str
    exit_code: int
    status: str
    duration_seconds: float


def ensure_result_dir(bundle_name: str, result_root: str | None = None) -> Path:
    if result_root:
        candidate = Path(result_root)
        resolved = candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        resolved = PROJECT_ROOT / "tmp" / "ci" / bundle_name / timestamp

    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def build_pytest_stage(extra_pytest_args: Sequence[str] | None = None) -> StageSpec:
    pytest_args = list(extra_pytest_args or [])
    if not pytest_args:
        pytest_args = ["-q"]

    command = [
        str(REPO_PYTHON),
        "-m",
        "pytest",
        *(path.as_posix() for path in PYTEST_TARGETS),
        *pytest_args,
    ]
    return StageSpec(
        label="Focused pytest suites",
        slug="pytest",
        command=command,
    )


def build_smoke_stages(
    *,
    run_ai: bool = False,
    keep_temp: bool = False,
    include_extractors: bool = False,
    include_post_extract: bool = True,
    include_full_local: bool = True,
    include_ai_store: bool = True,
) -> list[StageSpec]:
    stages: list[StageSpec] = []
    common_args: list[str] = []

    if run_ai:
        common_args.append("--run-ai")
    if keep_temp:
        common_args.append("--keep-temp")

    if include_post_extract:
        stages.append(
            StageSpec(
                label="Deterministic post-extract smoke",
                slug="smoke-00-post-extract",
                command=[
                    str(REPO_PYTHON),
                    SMOKE_SCRIPTS["post_extract"].as_posix(),
                    *common_args,
                ],
            )
        )

    if include_full_local:
        full_local_args = list(common_args)
        if include_extractors:
            full_local_args.append("--include-extractors")
        stages.append(
            StageSpec(
                label="Sequential full local smoke",
                slug="smoke-01-full-local",
                command=[
                    str(REPO_PYTHON),
                    SMOKE_SCRIPTS["full_local"].as_posix(),
                    *full_local_args,
                ],
            )
        )

    if include_ai_store:
        stages.append(
            StageSpec(
                label="AI store contract smoke",
                slug="smoke-02-ai-store",
                command=[
                    str(REPO_PYTHON),
                    SMOKE_SCRIPTS["ai_store"].as_posix(),
                ],
            )
        )

    return stages


def run_stage_specs(
    stage_specs: Sequence[StageSpec],
    result_dir: Path,
    *,
    start_index: int = 1,
    stop_on_failure: bool = True,
) -> list[StageResult]:
    results: list[StageResult] = []

    for offset, spec in enumerate(stage_specs):
        index = start_index + offset
        log_file = result_dir / f"{index:02d}-{spec.slug}.txt"
        print(f"[{index}] {spec.label}")
        print(f"    Log: {log_file}")

        started = time.time()
        completed = subprocess.run(
            spec.command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        duration_seconds = round(time.time() - started, 1)
        status = "PASS" if completed.returncode == 0 else "FAIL"

        log_body = (
            f"COMMAND: {' '.join(spec.command)}\n\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}\n"
            f"EXIT CODE: {completed.returncode}\n"
        )
        log_file.write_text(log_body, encoding="utf-8")

        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        print(f"    Result: {status} ({duration_seconds:.1f}s)")

        results.append(
            StageResult(
                index=index,
                label=spec.label,
                slug=spec.slug,
                command=spec.command,
                log_file=str(log_file),
                exit_code=completed.returncode,
                status=status,
                duration_seconds=duration_seconds,
            )
        )

        if stop_on_failure and completed.returncode != 0:
            break

    return results


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_summary(results: Sequence[StageResult], **extra: Any) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python": str(REPO_PYTHON),
        "results": [asdict(result) for result in results],
        **extra,
    }


def results_success(results: Sequence[StageResult]) -> bool:
    return bool(results) and all(result.exit_code == 0 for result in results)
