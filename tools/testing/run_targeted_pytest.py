from __future__ import annotations

import argparse

from _common import run_repo_python


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Forward a targeted diagnostic invocation to tests/run_pytest.py.",
        epilog="Examples: python tools/testing/run_targeted_pytest.py tests/pytest/pytest_01_workflow_contract_test.py -q",
    )


def main() -> int:
    parser = build_parser()
    _, passthrough_args = parser.parse_known_args()
    return run_repo_python("tests/run_pytest.py", passthrough_args)


if __name__ == "__main__":
    raise SystemExit(main())
