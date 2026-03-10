import argparse
import os
import tempfile

from smoke_support import (
    POST_EXTRACT_PIPELINE,
    PROJECT_ROOT,
    assert_fixture_outputs,
    build_env,
    get_local_log_path,
    run_named_script,
    seed_ai_cache,
    seed_l1_fixtures,
)


def main():
    parser = argparse.ArgumentParser(description="Deterministic v12 local smoke test")
    parser.add_argument("--keep-temp", action="store_true", help="Keep the temporary directory after completion")
    parser.add_argument("--run-ai", action="store_true", help="Enable the optional AI stage")
    parser.add_argument("--only", type=str, default=None, help="Run only a single script identifier such as 03, 05c, or 06")
    args = parser.parse_args()

    log_file = get_local_log_path("smoke-test-log.txt")
    if os.path.exists(log_file):
        os.remove(log_file)

    base_tmp = os.path.join(PROJECT_ROOT, "tmp")
    os.makedirs(base_tmp, exist_ok=True)

    temp_dir_obj = tempfile.TemporaryDirectory(prefix="fixture-smoke-", dir=base_tmp)
    temp_dir = temp_dir_obj.name
    workdir = temp_dir
    outdir = os.path.join(temp_dir, "out")
    os.makedirs(outdir, exist_ok=True)

    print(f"Starting deterministic v12 smoke test. Logging to {log_file}")
    print(f"WORKDIR={workdir}")
    print(f"OUTDIR={outdir}")

    try:
        seed_l1_fixtures(workdir)
        extra_env = None
        if args.run_ai:
            cache_path = os.path.join(temp_dir, "ai-summaries-cache.json")
            seed_ai_cache(cache_path)
            extra_env = {"AI_CACHE_PATH": cache_path}
        env = build_env(workdir, outdir, run_ai=args.run_ai, extra_env=extra_env)

        scripts = [script for script in POST_EXTRACT_PIPELINE if args.only in script] if args.only else list(POST_EXTRACT_PIPELINE)
        if not args.run_ai:
            scripts = [script for script in scripts if "04-generate-ai-summaries" not in script]

        for script in scripts:
            extra_args = ["--warn-only"] if script.endswith("08-validate-output.py") else []
            result = run_named_script(script, env, PROJECT_ROOT, log_file=log_file, extra_args=extra_args)
            print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="")
            if result.returncode != 0:
                raise SystemExit(result.returncode)

        if args.only is None:
            assert_fixture_outputs(outdir, expect_ai=args.run_ai)
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
