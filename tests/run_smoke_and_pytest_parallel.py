from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.support.runner_support import (
    build_pytest_stage,
    build_smoke_stages,
    build_summary,
    ensure_result_dir,
    results_success,
    run_stage_specs,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the pytest lane and smoke lane in parallel")
    parser.add_argument("--run-ai", action="store_true", help="Enable the cache-backed local AI path where supported")
    parser.add_argument("--keep-temp", action="store_true", help="Preserve temporary smoke output trees")
    parser.add_argument("--include-extractors", action="store_true", help="Include 01 and 02* in the full local smoke runner")
    parser.add_argument("--skip-pytest", action="store_true", help="Skip the focused pytest lane")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip the smoke lane")
    parser.add_argument("--skip-post-extract", action="store_true", help="Skip the deterministic post-extract smoke runner")
    parser.add_argument("--skip-full-local", action="store_true", help="Skip the sequential full local smoke runner")
    parser.add_argument("--skip-ai-store", action="store_true", help="Skip the AI store contract smoke runner")
    parser.add_argument("--result-root", type=str, default=None, help="Optional output directory override")
    args, extra_pytest_args = parser.parse_known_args()

    lanes: dict[str, list[Any]] = {}
    if not args.skip_pytest:
        lanes["pytest"] = [build_pytest_stage(extra_pytest_args)]
    if not args.skip_smoke:
        smoke_stages = build_smoke_stages(
            run_ai=args.run_ai,
            keep_temp=args.keep_temp,
            include_extractors=args.include_extractors,
            include_post_extract=not args.skip_post_extract,
            include_full_local=not args.skip_full_local,
            include_ai_store=not args.skip_ai_store,
        )
        if smoke_stages:
            lanes["smoke"] = smoke_stages

    if not lanes:
        raise SystemExit("Nothing to do. Leave at least one lane enabled.")

    result_dir = ensure_result_dir("local-validation-parallel", args.result_root)
    lane_payloads: dict[str, dict[str, Any]] = {}
    lane_lock = threading.Lock()

    def _run_lane(lane_name: str, stage_specs: list[Any]) -> None:
        lane_dir = result_dir / f"{lane_name}-lane"
        lane_dir.mkdir(parents=True, exist_ok=True)
        print(f"Starting {lane_name} lane")
        results = run_stage_specs(stage_specs, lane_dir)
        payload = build_summary(results, kind=f"{lane_name}-lane")
        payload["success"] = results_success(results)
        write_json(lane_dir / "summary.json", payload)
        with lane_lock:
            lane_payloads[lane_name] = payload

    threads = [
        threading.Thread(target=_run_lane, args=(lane_name, stage_specs), daemon=False)
        for lane_name, stage_specs in lanes.items()
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    success = bool(lane_payloads) and all(payload["success"] for payload in lane_payloads.values())
    write_json(
        result_dir / "summary.json",
        {
            "generated_at": build_summary([])["generated_at"],
            "kind": "local-validation-parallel",
            "success": success,
            "lanes": lane_payloads,
        },
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
