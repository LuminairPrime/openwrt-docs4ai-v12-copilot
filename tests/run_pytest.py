from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.support.runner_support import (
    build_pytest_stage,
    build_summary,
    ensure_result_dir,
    results_success,
    run_stage_specs,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the focused pytest suite")
    parser.add_argument("--result-root", type=str, default=None, help="Optional output directory override")
    args, extra_pytest_args = parser.parse_known_args()

    result_dir = ensure_result_dir("pytest", args.result_root)
    results = run_stage_specs([build_pytest_stage(extra_pytest_args)], result_dir)
    write_json(result_dir / "summary.json", build_summary(results, kind="pytest"))
    return 0 if results_success(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
