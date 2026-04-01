# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.support.runner_support import (
    build_smoke_stages,
    build_summary,
    ensure_result_dir,
    results_success,
    run_stage_specs,
    write_json,
)  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the maintained smoke suite")
    parser.add_argument("--run-ai", action="store_true", help="Enable the cache-backed local AI path where supported")
    parser.add_argument("--keep-temp", action="store_true", help="Preserve temporary smoke output trees")
    parser.add_argument(
        "--include-extractors", action="store_true", help="Include 01 and 02* in the full local smoke runner"
    )
    parser.add_argument(
        "--skip-post-extract", action="store_true", help="Skip the deterministic post-extract smoke runner"
    )
    parser.add_argument("--skip-full-local", action="store_true", help="Skip the sequential full local smoke runner")
    parser.add_argument("--skip-ai-store", action="store_true", help="Skip the AI store contract smoke runner")
    parser.add_argument("--result-root", type=str, default=None, help="Optional output directory override")
    args = parser.parse_args()

    stages = build_smoke_stages(
        run_ai=args.run_ai,
        keep_temp=args.keep_temp,
        include_extractors=args.include_extractors,
        include_post_extract=not args.skip_post_extract,
        include_full_local=not args.skip_full_local,
        include_ai_store=not args.skip_ai_store,
    )
    if not stages:
        raise SystemExit("Nothing to do. Leave at least one smoke stage enabled.")

    result_dir = ensure_result_dir("smoke", args.result_root)
    results = run_stage_specs(stages, result_dir)
    write_json(
        result_dir / "summary.json",
        build_summary(
            results,
            kind="smoke",
            run_ai=args.run_ai,
            keep_temp=args.keep_temp,
            include_extractors=args.include_extractors,
        ),
    )
    return 0 if results_success(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
