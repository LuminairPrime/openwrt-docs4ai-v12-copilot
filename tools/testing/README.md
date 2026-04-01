# Testing Commands

This directory is the canonical operator surface for local validation. It exists
to keep the day-to-day command menu small for humans and AI agents.

The rule is simple:

- keep the executable suites in `tests/`
- keep the operator-facing command choices in `tools/testing/`

The wrappers in this directory delegate to the maintained implementation-level
runner scripts under [tests/README.md](../../tests/README.md).

## Default Commands

### Normal local proof

```powershell
python tools/testing/run_default_validation.py
```

This is the normal local validation command for most changes. It runs strict
source validation first and then the maintained sequential local validation
runner.

Optional modes:

```powershell
python tools/testing/run_default_validation.py --run-ai --keep-temp
python tools/testing/run_default_validation.py --include-extractors
```

### Source validation only

```powershell
python tools/testing/run_source_validation.py
```

Use this when the change is clearly in formatting, linting, typing, or workflow
gate behavior.

### Targeted pytest diagnosis

```powershell
python tools/testing/run_targeted_pytest.py tests/pytest/pytest_01_workflow_contract_test.py -q
python tools/testing/run_targeted_pytest.py -k routing -q
```

Use this only when you are intentionally narrowing a failure inside the focused
pytest suites.

### Targeted smoke diagnosis

```powershell
python tools/testing/run_targeted_smoke.py
python tools/testing/run_targeted_smoke.py --include-extractors
```

Use this only when you are isolating smoke-lane behavior.

## What The Wrappers Call

| Wrapper | Delegates to | Purpose |
| --- | --- | --- |
| `run_default_validation.py` | `tests/check_linting.py --strict`, then `tests/run_smoke_and_pytest.py` | Normal local proof |
| `run_source_validation.py` | `tests/check_linting.py --strict` | Source gate only |
| `run_targeted_pytest.py` | `tests/run_pytest.py` | Focused pytest diagnosis |
| `run_targeted_smoke.py` | `tests/run_smoke.py` | Smoke diagnosis |

## Advanced Control

If you need implementation-level flags such as `--result-root`, or if you need
to invoke a specific underlying runner directly, use the scripts documented in
[tests/README.md](../../tests/README.md).

That is an advanced path. The normal operator path should stay on the wrappers
in this directory.