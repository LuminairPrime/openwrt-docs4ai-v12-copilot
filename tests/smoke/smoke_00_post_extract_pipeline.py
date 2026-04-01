# ruff: noqa: E402

import argparse
import os
from pathlib import Path
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.support.smoke_pipeline_support import (
    POST_EXTRACT_PIPELINE,
    PROJECT_ROOT,
    assert_fixture_outputs,
    build_env,
    get_local_log_path,
    run_named_script,
    select_pipeline_scripts,
    seed_ai_cache,
    seed_l1_fixtures,
)  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Deterministic v12 local smoke test")
    parser.add_argument("--keep-temp", action="store_true", help="Keep the temporary directory after completion")
    parser.add_argument("--run-ai", action="store_true", help="Enable the optional AI stage")
    parser.add_argument(
        "--only",
        type=str,
        default=None,
        help="Run only a stage id, stage family, or script name such as 03, 05, 05c, or 06",
    )
    args = parser.parse_args()

    log_file = get_local_log_path("smoke-00-post-extract-pipeline-log.txt")
    if os.path.exists(log_file):
        os.remove(log_file)

    pipeline = list(POST_EXTRACT_PIPELINE)
    if not args.run_ai:
        pipeline = [script for script in pipeline if "04-generate-ai-summaries" not in script]

    try:
        scripts = select_pipeline_scripts(pipeline, args.only)
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}")

    base_tmp = os.path.join(PROJECT_ROOT, "tmp")
    os.makedirs(base_tmp, exist_ok=True)

    temp_dir_obj = tempfile.TemporaryDirectory(prefix="fixture-smoke-", dir=base_tmp)
    temp_dir = temp_dir_obj.name
    workdir = os.path.join(temp_dir, "downloads")
    processed_dir = os.path.join(temp_dir, "processed")
    outdir = os.path.join(temp_dir, "staged")
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)

    print(f"Starting deterministic v12 smoke test. Logging to {log_file}")
    print(f"WORKDIR={workdir}")
    print(f"PROCESSED_DIR={processed_dir}")
    print(f"OUTDIR={outdir}")

    try:
        seed_l1_fixtures(workdir, processed_dir)
        extra_env = None
        if args.run_ai:
            cache_path = os.path.join(temp_dir, "ai-summaries-cache.json")
            seed_ai_cache(cache_path)
            extra_env = {"AI_CACHE_PATH": cache_path}
        env = build_env(
            workdir,
            outdir,
            run_ai=args.run_ai,
            extra_env=extra_env,
            processed_dir=processed_dir,
            pipeline_run_dir=temp_dir,
        )

        for script in scripts:
            extra_args = ["--warn-only"] if script.endswith("08-validate-output.py") else []
            result = run_named_script(script, env, PROJECT_ROOT, log_file=log_file, extra_args=extra_args)
            print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="")
            if result.returncode != 0:
                raise SystemExit(result.returncode)

        if args.only is None:
            assert_fixture_outputs(outdir, processed_dir, expect_ai=args.run_ai)
        print("Deterministic smoke test completed successfully.")
    finally:
        if args.keep_temp:
            print(f"Temporary files preserved at: {temp_dir}")
            if hasattr(temp_dir_obj, "_finalizer") and temp_dir_obj._finalizer:
                temp_dir_obj._finalizer.detach()
        else:
            temp_dir_obj.cleanup()


if __name__ == "__main__":
    main()
