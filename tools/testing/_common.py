from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_repo_python() -> Path:
    candidates = [
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "bin" / "python",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return Path(sys.executable)


REPO_PYTHON = _resolve_repo_python()


def run_repo_python(script_path: str, script_args: Sequence[str] | None = None) -> int:
    command = [str(REPO_PYTHON), script_path, *(script_args or [])]
    completed = subprocess.run(command, cwd=str(PROJECT_ROOT))
    return completed.returncode
