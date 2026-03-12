# Pipeline Stage Alignment Report

Recorded: 2026-03-10

## Recovered Context

This report reconstructs the implementation work that was originally tracked in chat state, `/memories/session/plan.md`, and repository memory.

The recovered plan had two parts:

1. Apply Plan A Option B, the moderate logical stage-family rename:
   - keep whole numbers as dependency boundaries
   - use lettered siblings for same-stage post-L2 builders
   - rename the late-stage scripts so the visible order matches the real DAG
2. Apply Plan B, the conservative high-confidence bug-fix set:
   - provenance integrity and provenance fallback
   - extractor timeout and fallback hardening
   - changelog baseline-path and legacy-baseline safety
   - curated example warning visibility

The same recovered plan also explicitly deferred:

- the extreme A3 descriptive rename campaign
- Mermaid publication/injection work
- signature inventory schema expansion for module metadata
- escalation of curated example partial read failures to hard failure
- broader validator expansion beyond the targeted fixes

## What Landed

### Stage-family rename and workflow alignment

The following late-stage scripts were renamed to reflect the real stage boundaries:

- `05-assemble-references.py` -> `05a-assemble-references.py`
- `06b-generate-agents-md.py` -> `05b-generate-agents-and-readme.py`
- `06c-generate-ide-schemas.py` -> `05c-generate-ucode-ide-schemas.py`
- `06d-generate-changelog.py` -> `05d-generate-api-drift-changelog.py`
- `06a-generate-llms-txt.py` -> `06-generate-llm-routing-indexes.py`
- `07-generate-index-html.py` -> `07-generate-web-index.py`
- `08-validate.py` -> `08-validate-output.py`

The workflow in `.github/workflows/openwrt-docs4ai-00-pipeline.yml` was updated to call those names explicitly and to make the late-stage boundaries visible:

- `05a` assembles publishable references
- `05b` through `05d` generate publication companion outputs
- `06` generates LLM routing indexes
- `07` generates the web landing page
- `08` validates publishable output

The local smoke harness and direct smoke runners were updated to match the new names.

### Conservative bug fixes

The following high-confidence fixes landed:

- Added `lib/repo_manifest.py` as the shared provenance helper.
- `01-clone-repos.py` now treats commit lookup failure or invalid hash output as fatal instead of silently accepting bad values.
- `03-normalize-semantic.py` now reads commit provenance from `repo-manifest.json` when commit environment variables are absent.
- `06-generate-llm-routing-indexes.py` now does the same manifest-backed provenance fallback for version strings.
- `02b-scrape-ucode.py` now uses bounded `jsdoc2md` execution with timeout handling.
- `02c-scrape-jsdoc.py` now uses bounded `jsdoc2md` execution on both code paths and rejects fallback stdout on non-zero exit.
- `02e-scrape-example-packages.py` now surfaces curated example read failures as warnings with counts instead of silently swallowing them.
- `05d-generate-api-drift-changelog.py` now resolves the baseline path independently of the current working directory and suppresses fabricated module drift sections for legacy baselines that lack module metadata.

### Test and documentation updates

The following supporting surfaces were updated:

- `tests/pytest/pytest_00_pipeline_units_test.py` gained targeted regressions for provenance fallback, invalid commit hash handling, `02c` fallback behavior, and legacy changelog baseline behavior.
- `tests/support/smoke_pipeline_support.py`, `tests/smoke/smoke_00_post_extract_pipeline.py`, and `tests/smoke/smoke_01_full_local_pipeline.py` now exercise the renamed pipeline and no longer mask provenance fallback by seeding fake commit environment variables.
- `DEVELOPMENT.md` and `docs/ARCHITECTURE.md` now document the whole-number boundary and stage-family sibling rule.
- `docs/specs/v12/v12-bug-log.md` now records the newly verified local fixes and keeps the deferred Dockerman warning policy explicit.

## Verification Timeline

### Local verification

The renamed and hardened pipeline was verified locally with:

- `python tests/run_pytest.py`
- `python tests/smoke/smoke_00_post_extract_pipeline.py`
- `python tests/smoke/smoke_01_full_local_pipeline.py`
- `python tests/smoke/smoke_00_post_extract_pipeline.py --run-ai`

Those local checks passed before the hosted rerun.

### First remote failure after rename-only push

An intermediate push produced commit `bafae081f640775d5394228bbf4f05de59b576a7` with message `asdasd`.

That commit renamed the late-stage scripts on disk, but it did not include the workflow update or the supporting hardening changes. GitHub Actions run `22900793543` failed in the `process` job because the committed workflow still called the deleted old script names, starting with:

- `python .github/scripts/openwrt-docs4ai-05-assemble-references.py`

This failure was important because it proved the rename refactor had been split across commits in an unsafe way.

### Final remote success

The missing alignment and hardening work was then committed as:

- commit `70cc0f0ec086c37c572ac1d03b16cf9c96172d0a`
- message: `fix: align renamed pipeline stages`

That commit updated the workflow, landed the conservative bug fixes, updated the smoke harness, and refreshed the active technical docs.

GitHub Actions run `22901356504` on that commit completed successfully.

Hosted result summary:

- `initialize`: success
- all `extract` matrix jobs: success
- `process`: success
- `deploy`: success

This is the first fully verified remote run for the renamed late-stage contract.

## Repo Hygiene State After The Alignment Pass

The repo hygiene plan also progressed during this work:

- active smoke helpers now write to `tmp/logs/`
- ad hoc comparison bundles belong under `tmp/reports/`
- the remaining tracked `tests` smoke logs and tracked `lib/__pycache__/` files are cleanup targets so they stop appearing in `git status`

One caution remains in repository memory: the tracked file `.github/scripts/__pycache__/openwrt-docs4ai-04-generate-summaries.cpython-313.pyc` should not be removed blindly in broad cache cleanup passes, because it is currently tracked in the repository.

## Deferred Work

The following items remain intentionally deferred:

- extreme A3 descriptive renaming beyond the moderate stage-family schema
- Mermaid publication/injection work
- explicit module metadata expansion in `signature-inventory.json`
- escalation of partial curated example read failures to hard failure
- broader validation expansion beyond the targeted fixes already landed
- the remaining Dockerman standalone `ucode` warning, which stays a truthful soft warning pending stronger runtime evidence

## Outcome

The recovered plan was implemented to completion.

The important results are:

- the late-stage filenames now match the intended logical stage-family schema
- the workflow and local smoke paths use the same names
- the conservative provenance, timeout, fallback, changelog, and warning-visibility fixes landed
- the implementation was verified locally
- one remote integration failure exposed an incomplete push and was corrected
- the final GitHub Actions run passed on the hosted runner

This report is intended to replace the lost chat-only progress record with a durable repository artifact.