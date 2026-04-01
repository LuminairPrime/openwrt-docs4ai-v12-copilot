from __future__ import annotations

import argparse

from _common import run_repo_python


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Run the strict local source-validation gate backed by tests/check_linting.py.",
    )


def main() -> int:
    build_parser().parse_args()
    return run_repo_python("tests/check_linting.py", ["--strict"])


if __name__ == "__main__":
    raise SystemExit(main())
