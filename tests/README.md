# Tests

This directory holds the maintained local validation surface for the repository.
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
| `tests/check_linting.py` | Read-only Ruff, Pyright, and actionlint review runner |

## Recommended Commands

```powershell
python tests/run_pytest.py
python tests/run_smoke.py
python tests/run_smoke.py --run-ai --include-extractors
python tests/run_smoke_and_pytest.py
python tests/run_smoke_and_pytest.py --run-ai --keep-temp
python tests/run_smoke_and_pytest_parallel.py
python tests/check_linting.py
```

All root-level Python runners accept `--result-root` if you want to override the
default output directory. `tests/run_pytest.py` forwards any extra arguments to
pytest, so commands such as `python tests/run_pytest.py -k wiki -q` are valid.

## Direct Entry Points

Use the root-level runners for normal maintenance. Run the underlying test files
directly when you need a narrower proof.

```powershell
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
| `tests/check_linting.py` | `tmp/ci/lint-review/<timestamp>/` |

Each bundle contains per-stage text logs and a `summary.json` file.

## Parallel Rules

- Supported: one pytest lane and one smoke lane running together through `tests/run_smoke_and_pytest_parallel.py`.
- Unsupported: running multiple smoke scripts against the same worktree at once.
- Unsupported: launching duplicate full-local smoke runners in parallel.
- Unsupported: treating the smoke stages as order-independent. They are still maintained as a serial lane.