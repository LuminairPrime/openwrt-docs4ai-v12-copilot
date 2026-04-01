from __future__ import annotations

import argparse

from _common import run_repo_python


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the canonical local validation flow: strict source validation, then sequential local validation.",
    )
    parser.add_argument(
        "--run-ai",
        action="store_true",
        help="Pass through the cache-backed AI regression mode to the sequential local validation runner.",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files created by the sequential local validation runner.",
    )
    parser.add_argument(
        "--include-extractors",
        action="store_true",
        help="Include the broader extractor path in the sequential local validation runner.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    print("[tools/testing] Running strict source validation")
    exit_code = run_repo_python("tests/check_linting.py", ["--strict"])
    if exit_code != 0:
        return exit_code

    local_validation_args: list[str] = []
    if args.run_ai:
        local_validation_args.append("--run-ai")
    if args.keep_temp:
        local_validation_args.append("--keep-temp")
    if args.include_extractors:
        local_validation_args.append("--include-extractors")

    print("[tools/testing] Running sequential local validation")
    return run_repo_python("tests/run_smoke_and_pytest.py", local_validation_args)


if __name__ == "__main__":
    raise SystemExit(main())
