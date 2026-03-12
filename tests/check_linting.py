from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.support.runner_support import REPO_PYTHON, ensure_result_dir


def _tool_path_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(REPO_PYTHON.parent) + os.pathsep + env.get("PATH", "")
    return env


def _resolve_tool_command(tool_name: str, module_name: str | None = None) -> list[str] | None:
    env = _tool_path_env()
    executable = shutil.which(tool_name, path=env["PATH"])
    if executable:
        return [executable]

    if module_name is None:
        return None

    probe = subprocess.run(
        [str(REPO_PYTHON), "-m", module_name, "--version"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    if probe.returncode == 0:
        return [str(REPO_PYTHON), "-m", module_name]

    return None


def _run_check(
    *,
    index: int,
    name: str,
    command: list[str] | None,
    args: list[str],
    result_dir: Path,
) -> dict[str, Any]:
    log_file = result_dir / f"{index:02d}-{name}.txt"

    if command is None:
        log_file.write_text(f"{name} is unavailable on this machine.\n", encoding="utf-8")
        return {
            "name": name,
            "status": "unavailable",
            "command": None,
            "log_file": str(log_file),
            "exit_code": None,
        }

    full_command = [*command, *args]
    completed = subprocess.run(
        full_command,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=_tool_path_env(),
    )
    log_body = (
        f"COMMAND: {' '.join(full_command)}\n\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}\n"
        f"EXIT CODE: {completed.returncode}\n"
    )
    log_file.write_text(log_body, encoding="utf-8")
    status = "clean" if completed.returncode == 0 else "issues"
    return {
        "name": name,
        "status": status,
        "command": full_command,
        "log_file": str(log_file),
        "exit_code": completed.returncode,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run read-only source hygiene checks")
    parser.add_argument("--result-root", type=str, default=None, help="Optional output directory override")
    args = parser.parse_args()

    result_dir = ensure_result_dir("lint-review", args.result_root)
    checks = [
        (1, "ruff", _resolve_tool_command("ruff", "ruff"), ["check", ".github/scripts", "lib", "tests"]),
        (2, "pyright", _resolve_tool_command("pyright", "pyright"), ["--project", "pyrightconfig.strict.json"]),
        (3, "actionlint", _resolve_tool_command("actionlint"), [".github/workflows/openwrt-docs4ai-00-pipeline.yml"]),
    ]

    results = [
        _run_check(index=index, name=name, command=command, args=tool_args, result_dir=result_dir)
        for index, name, command, tool_args in checks
    ]

    overall_status = "clean"
    if any(result["status"] == "issues" for result in results):
        overall_status = "issues"
    elif any(result["status"] == "unavailable" for result in results):
        overall_status = "clean-with-skips"

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kind": "lint-review",
        "python": str(REPO_PYTHON),
        "status": overall_status,
        "results": results,
    }
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Lint review written to {result_dir}")
    return 1 if overall_status == "issues" else 0


if __name__ == "__main__":
    raise SystemExit(main())