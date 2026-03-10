"""
openwrt-docs4ai-00-smoke-test.py

Purpose  : Sequential local smoke runner for the numbered pipeline scripts.
Flags    : --keep-temp         keep the temp tree for inspection
           --run-ai            include the optional AI stage
           --include-extractors run 01 and 02* before the fixture-backed stages
           --only <id>         run only scripts matching a partial identifier such as 03, 05c, or 06
Outputs  : Appends step logs to tmp/logs/openwrt-docs4ai-00-smoke-test-log.txt
Notes    : Default mode is fixture-backed and offline-friendly. The extractor path is optional.
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import time

from smoke_support import (
    FULL_PIPELINE,
    POST_EXTRACT_PIPELINE,
    PROJECT_ROOT,
    assert_fixture_outputs,
    build_env,
    get_local_log_path,
    run_named_script,
    seed_ai_cache,
    seed_l1_fixtures,
)

LOG_FILE = get_local_log_path("openwrt-docs4ai-00-smoke-test-log.txt")


def parse_args():
    parser = argparse.ArgumentParser(description="Sequential local smoke runner for openwrt-docs4ai")
    parser.add_argument("--keep-temp", action="store_true", help="Keep the temp directory after completion")
    parser.add_argument("--run-ai", action="store_true", help="Include the optional AI stage")
    parser.add_argument("--include-extractors", action="store_true", help="Run 01 and 02* before the fixture-backed processing stages")
    parser.add_argument("--only", type=str, default=None, help="Run only scripts matching a partial identifier such as 03, 05c, or 06")
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("openwrt-docs4ai Sequential Smoke Test")
    print("=" * 60)

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Time: {ts}")
    print(f"Keep temp: {args.keep_temp}")
    print(f"Run AI: {args.run_ai}")
    print(f"Include extractors: {args.include_extractors}")
    print()

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    base_tmp = os.path.join(PROJECT_ROOT, "tmp")
    os.makedirs(base_tmp, exist_ok=True)

    temp_dir = tempfile.mkdtemp(prefix="smoke-test-", dir=base_tmp)
    work_dir = os.path.join(temp_dir, "work")
    out_dir = os.path.join(temp_dir, "openwrt-condensed-docs")
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Temp dir: {temp_dir}")
    print(f"WORKDIR:  {work_dir}")
    print(f"OUTDIR:   {out_dir}")
    print()

    seed_l1_fixtures(work_dir)
    extra_env = None
    if args.run_ai:
        cache_path = os.path.join(temp_dir, "ai-summaries-cache.json")
        seed_ai_cache(cache_path)
        extra_env = {"AI_CACHE_PATH": cache_path}
    env = build_env(work_dir, out_dir, run_ai=args.run_ai, extra_env=extra_env)

    pipeline = list(FULL_PIPELINE if args.include_extractors else POST_EXTRACT_PIPELINE)
    if not args.run_ai:
        pipeline = [script for script in pipeline if "04-generate-ai-summaries" not in script]
    if args.only:
        pipeline = [script for script in pipeline if args.only in script]

    results = []
    total_start = time.time()

    for index, script in enumerate(pipeline, start=1):
        extra_args = ["--warn-only"] if script.endswith("08-validate-output.py") else []
        print(f"[{index:2d}/{len(pipeline)}] {script:45s} ... ", end="", flush=True)
        start = time.time()
        try:
            result = run_named_script(script, env, PROJECT_ROOT, log_file=LOG_FILE, extra_args=extra_args)
            duration = time.time() - start
            if result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    print(f"\n  {line}", end="")
            if result.stderr.strip():
                for line in result.stderr.strip().splitlines():
                    print(f"\n  STDERR: {line}", end="")
            status = "PASS" if result.returncode == 0 else "FAIL"
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            status = "TIMEOUT"
        except Exception as exc:
            duration = time.time() - start
            print(f"\n  ERROR: {exc}", end="")
            status = "ERROR"

        print(f" {status} ({duration:.1f}s)")
        results.append((script, status, duration))

    total_time = time.time() - total_start

    overall = "PASS"
    if args.only is None:
        try:
            assert_fixture_outputs(out_dir, expect_ai=args.run_ai)
        except AssertionError as exc:
            overall = "FAIL"
            results.append(("fixture assertions", "FAIL", 0.0))
            print(f"\nFixture assertions failed: {exc}")

    if any(status != "PASS" for _, status, _ in results):
        overall = "FAIL"

    print()
    print("=" * 60)
    print("Results:")
    print("-" * 60)
    for script, status, duration in results:
        print(f"  {script:45s} {status:8s} ({duration:.1f}s)")
    print("-" * 60)
    print(f"  Overall: {overall} in {total_time:.1f}s")
    print("=" * 60)

    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(f"\n{ts} | {overall} | {total_time:.0f}s\n")

    if args.keep_temp:
        print(f"\nTemp directory preserved: {temp_dir}")
        print(f"  Output: {out_dir}")
    else:
        print("\nCleaning up temp directory...")
        shutil.rmtree(temp_dir, ignore_errors=True)

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
