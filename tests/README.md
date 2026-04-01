# Tests

This directory holds the executable suites and implementation-level runner
scripts that back the canonical operator surface in
[tools/testing/README.md](../tools/testing/README.md).
Only `tests/pytest/` and `tests/smoke/` contain runnable test code. Everything
else under `tests/` is support material, committed sample data, durable
artifacts, or planning notes.

## Layout

| Path | Purpose |
| --- | --- |
| `tests/pytest/` | Focused pytest suites for helper logic, workflow contracts, fixture routing, corpus sanity, and wiki scraper behavior |
| `tests/smoke/` | Maintained smoke runners that exercise the local pipeline without pytest discovery |
| `tests/support/` | Shared helpers used by pytest modules, smoke scripts, and root-level runner scripts |
| `tests/sample-inputs/` | Small committed repro inputs used by the fixture-backed smoke path |
| `tests/artifacts/` | Intentionally committed test artifacts that are useful to inspect in Git history |
| `tests/proposals/` | Historical and draft test planning material |
| `tests/run_pytest.py` | Maintained focused pytest entry point |
| `tests/run_smoke.py` | Maintained serial smoke entry point |
| `tests/run_smoke_and_pytest.py` | Maintained sequential validation runner |
| `tests/run_smoke_and_pytest_parallel.py` | Supported two-lane runner: one pytest lane plus one smoke lane |
| `tests/check_linting.py` | Read-only Ruff format/check, Pyright, and actionlint review runner |

## Recommended Commands

```powershell
python tools/testing/run_default_validation.py
python tools/testing/run_default_validation.py --run-ai --keep-temp
python tools/testing/run_source_validation.py
python tools/testing/run_targeted_pytest.py -k wiki -q
python tools/testing/run_targeted_smoke.py --include-extractors
```

Use the wrappers in `tools/testing/` for normal maintenance. They keep the public
command menu small while still delegating to the maintained runners in this
directory.

## Direct Entry Points

Use the underlying runners here when you need implementation-level control such
as `--result-root` or when you want to bypass the smaller operator-facing menu.
Run the underlying test files directly when you need a narrower proof.

```powershell
python tests/check_linting.py --strict
python tests/run_pytest.py -k wiki -q
python tests/run_smoke.py --include-extractors
python tests/run_smoke_and_pytest.py --run-ai --keep-temp
python -m pytest tests/pytest/pytest_04_wiki_scraper_test.py -q
python -m pytest tests/pytest/pytest_03_wiki_corpus_sanity_test.py -s -q
python tests/smoke/smoke_00_post_extract_pipeline.py --keep-temp
python tests/smoke/smoke_01_full_local_pipeline.py --include-extractors
python tests/smoke/smoke_02_ai_store_contract.py
```

The smoke scripts are intentionally named `smoke_...` so pytest will not collect
them by mistake.

## Result Bundles

The maintained runners write durable bundles under `tmp/ci/`:

| Runner | Default bundle root |
| --- | --- |
| `tests/run_pytest.py` | `tmp/ci/pytest/<timestamp>/` |
| `tests/run_smoke.py` | `tmp/ci/smoke/<timestamp>/` |
| `tests/run_smoke_and_pytest.py` | `tmp/ci/local-validation/<timestamp>/` |
| `tests/run_smoke_and_pytest_parallel.py` | `tmp/ci/local-validation-parallel/<timestamp>/` |
| `tests/check_linting.py` | `tmp/ci/lint-review/<timestamp>/` locally, `tmp/ci/lint-review/current/` in `validate_source` |

Each bundle contains per-stage text logs and a `summary.json` file.
When lint review fails, inspect `summary.json` first before raw console output.

`tools/testing/run_default_validation.py` intentionally produces two maintained
bundles by delegation:

- `tmp/ci/lint-review/<timestamp>/`
- `tmp/ci/local-validation/<timestamp>/`

## Parallel Rules

- Supported: one pytest lane and one smoke lane running together through `tests/run_smoke_and_pytest_parallel.py`.
- Unsupported: running multiple smoke scripts against the same worktree at once.
- Unsupported: launching duplicate full-local smoke runners in parallel.
- Unsupported: treating the smoke stages as order-independent. They are still maintained as a serial lane.