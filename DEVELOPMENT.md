# Development Guide

## Purpose

This file is the maintainer quick start for local development. The current engineering priority is to keep the Windows development path and the sequential smoke-test path reliable while preserving the now-verified GitHub Actions publication flow.

## Prerequisites

| Tool | Version | Purpose |
| --- | --- | --- |
| Python | 3.11+ | All pipeline scripts and local tests |
| Node.js | 20+ | `jsdoc-to-markdown` and JavaScript syntax checks |
| pandoc | 3.0+ | Wiki conversion |
| git | 2.25+ | Repo cloning and versioned refactors |
| jsdoc-to-markdown | current npm release | API doc extraction |

## Quick Start on Windows

```powershell
pip install -r .github/scripts/requirements.txt
npm install -g jsdoc-to-markdown
winget install --id JohnMacFarlane.Pandoc
```

After dependencies are installed, use the local tests in `tests/` rather than relying on GitHub Actions behavior.

## Recommended Local Commands

```powershell
python tests/run_pytest.py
python tests/run_smoke.py
python tests/run_smoke.py --run-ai
python tests/run_smoke.py --include-extractors
python tests/run_smoke_and_pytest.py
python tests/run_smoke_and_pytest.py --run-ai --keep-temp
python tests/run_smoke_and_pytest_parallel.py
python tests/check_linting.py
python tools/manage_ai_store.py --option review
python tools/manage_ai_store.py --option full --keep-scratch
```

The `--run-ai` path is cache-backed for local verification, so it can validate the placement and mutation behavior of script `04` without requiring a live model token.

For real AI-summary generation, use `python tools/manage_ai_store.py --option review` or the detailed scratch-first workflow in [docs/specs/v12/ai-summary-operations-runbook.md](docs/specs/v12/ai-summary-operations-runbook.md). Do not treat `--run-ai` as proof of live API generation or permanent AI-store promotion.

For one-off terminal invocations, either activate `.venv` once before testing or call the workspace interpreter directly via `C:/Users/MC/Documents/AirSentinel/openwrt-docs4ai-v12-copilot/.venv/Scripts/python.exe`. Do not assume the system `python` on `PATH` is the repo interpreter.

## Validation Runners

The maintained local validation surface is now Python-first and cross-platform.
See `tests/README.md` for the full layout and direct entry points.

- `tests/run_pytest.py` runs the focused suites in `tests/pytest/` and forwards any extra CLI arguments to pytest.
- `tests/run_smoke.py` runs the maintained smoke lane in serial order. It supports `--run-ai`, `--keep-temp`, `--include-extractors`, the individual `--skip-*` switches, and `--result-root`.
- `tests/run_smoke_and_pytest.py` is the maintained one-command sequential validation path. It runs the focused pytest lane first, then the enabled smoke stages, and writes per-stage logs plus `summary.json` under `tmp/ci/local-validation/`.
- `tests/run_smoke_and_pytest_parallel.py` runs one pytest lane and one smoke lane in parallel. Use it only for that supported split; do not treat it as permission to run multiple smoke scripts concurrently.
- `tests/check_linting.py` performs a read-only Ruff, strict Pyright, and actionlint review and writes its bundle under `tmp/ci/lint-review/`.

These runners are intentionally local-first. Remote GitHub Actions validation still depends on a pushed commit and the run-pinning procedure in `CI Operations`.

## Terminal Testing Discipline

When validating this project from the terminal, prefer deterministic, bounded commands over ad hoc shell control flow.

1. Start in the repo root with the workspace virtual environment active, or use the explicit `.venv` interpreter path when running a single isolated command.
2. Run the smallest proof first: `python tests/run_pytest.py`, then `python tests/run_smoke.py`, then remote workflow validation.
3. When you want the full preferred local progression in one command, use `python tests/run_smoke_and_pytest.py` instead of rebuilding the sequence ad hoc.
4. Keep one purpose per command. Prefer a direct command invocation over inline retry loops or multi-purpose shell snippets.
5. Capture durable local evidence when it matters, typically under `tests/test-results-*.txt` or `tmp/ci/`, so reruns can be compared without re-reading terminal scrollback.
6. For GitHub Actions validation, pin the run to the pushed commit SHA, identify the matching `databaseId`, and wait on that exact run with `gh run watch <run_id> --exit-status --interval 15`.
7. After the run finishes, inspect `pipeline-summary`, `process-summary`, and `extract-summary` artifacts before opening raw failed-job logs.
8. Avoid open-ended polling loops, mid-run log scraping, and assumptions about "the latest run". They create noisy output and make it easy to validate the wrong workflow run.

## Pre-Change Checklist

Before editing pipeline scripts, generated outputs, or workflow behavior:

1. Decide whether the change affects maintainer docs, generated-corpus contracts, workflow execution, or only local tests.
2. Read this file, `docs/ARCHITECTURE.md`, `docs/specs/v12/schema-definitions.md`, and `docs/specs/v12/execution-map.md` before changing numbered scripts or the workflow.
3. If the change touches scripts `05b` through `08`, inspect the currently generated AI-facing outputs first: `openwrt-condensed-docs/llms.txt`, `openwrt-condensed-docs/llms-full.txt`, `openwrt-condensed-docs/AGENTS.md`, and at least one representative `openwrt-condensed-docs/{module}/llms.txt`.
4. If the change touches `.github/workflows/openwrt-docs4ai-00-pipeline.yml`, map the intended behavior to a specific trigger path: push on `main`, monthly schedule, or `workflow_dispatch` with explicit inputs.
5. Run the smallest local proof first. Only use remote GitHub Actions runs after local validation passes.

## Dual-Role LLM Surfaces

This repository has two LLM-relevant surfaces and they should not be conflated:

- The source repository is the implementation and maintainer-doc surface. Its authoritative docs live under `docs/`, `README.md`, and `DEVELOPMENT.md`.
- The generated corpus under `openwrt-condensed-docs/` is the published AI navigation surface consumed by downstream tools and models.

The strict routing contract for generated `llms.txt`, `llms-full.txt`, module `llms.txt`, and `AGENTS.md` lives in `docs/specs/v12/schema-definitions.md`.

A source-repo root `llms.txt` remains intentionally out of scope for the current maintenance tranche. Do not create one opportunistically while working on generated output behavior.

## Repository Rules

- `openwrt-condensed-docs/` is the stable generated output root.
- `tmp/` is ephemeral and never authoritative.
- `L1-raw` and `L2-semantic` are the standard intermediate layer names.
- Script numbering denotes stage families and dependency boundaries. Letter suffixes denote sibling scripts inside the same stage family.
- A bare stage id such as `04` cannot coexist with `04a`, `04b`, or other lettered siblings. A stage is either singular or lettered, never both.
- Non-pipeline support tools belong outside the numbered stage surface, under `tools/`.
- Local smoke runs may still execute the lettered scripts sequentially.
- Local-only references that are out of scope for this repo (for example third-party bug notes) should stay under `tmp/legacy-backup/` so they remain durable locally and gitignored.

## Script Families

| Script | Role |
| --- | --- |
| `openwrt-docs4ai-01-clone-repos.py` | Prepare L0 source inputs and manifests |
| `openwrt-docs4ai-02a` through `02h` | Source-specific extraction into L1 |
| `openwrt-docs4ai-03-normalize-semantic.py` | L1 to L2 normalization and promotion |
| `openwrt-docs4ai-04-generate-ai-summaries.py` | Optional AI summary enrichment |
| `openwrt-docs4ai-05a-assemble-references.py` | Assemble publishable L3 skeletons and L4 monoliths |
| `openwrt-docs4ai-05b-generate-agents-and-readme.py` | Generate AGENTS.md and the root generated README |
| `openwrt-docs4ai-05c-generate-ucode-ide-schemas.py` | Generate ucode IDE schema output |
| `openwrt-docs4ai-05d-generate-api-drift-changelog.py` | Generate API drift telemetry against the baseline inventory |
| `openwrt-docs4ai-06-generate-llm-routing-indexes.py` | Generate llms.txt, llms-full.txt, and module routing indexes |
| `openwrt-docs4ai-07-generate-web-index.py` | HTML landing page generation |
| `openwrt-docs4ai-08-validate-output.py` | Whole-output validation gate |

## Local Tests

- `tests/pytest/` contains the focused pytest suites for import-safe helpers, workflow contracts, fixture routing, corpus sanity, and wiki scraper behavior.
- `tests/smoke/` contains the direct smoke runners; use `python tests/run_smoke.py` for the maintained serial sequence.
- `tests/check_linting.py` produces read-only local review bundles for Ruff, strict Pyright, and actionlint.

These entry points are maintained as first-class engineering assets. Use `tests/README.md` when you need the exact folder contract or runner/output mapping.

## AI Summary Operations

Real AI-summary work is intentionally AI-store first and scratch first.

- `data/base/` and `data/override/` are the authoritative AI-summary surfaces.
- `openwrt-condensed-docs/` is downstream generated evidence.
- The permanent workflow lives in [docs/specs/v12/ai-summary-operations-runbook.md](docs/specs/v12/ai-summary-operations-runbook.md).
- The only numbered AI stage is `.github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py`.
- Script `04` performs its own library-backed preflight against the selected AI store before applying or generating summaries.
- The maintained one-command helper is `tools/manage_ai_store.py`.
- `--option review` prepares scratch data, runs script `04`, then runs the same library-backed validation and audit checks against the scratch store.
- `--option promote` copies reviewed scratch JSON into `data/base/` and immediately reruns validation and audit against the permanent store.
- `--option full` runs the full review-plus-promotion path and can remove scratch data automatically unless `--keep-scratch` is set.

Use the cache-backed smoke paths for regression proof, and use the runbook plus `tools/manage_ai_store.py` for real generation, review, and promotion.

## Remote Publish Policy

- The workflow builds generated artifacts into `staging/` first and only promotes them in the `deploy` job.
- Hosted extraction now runs `02a` in parallel with `01`, while `02b` through `02h` remain clone-gated.
- On push, schedule, and manual runs, the deploy job syncs `staging/` into `openwrt-condensed-docs/` with `rsync -a --delete`.
- If the promoted tree changed, GitHub Actions writes a bot-authored commit in the form `docs: v12 auto-update YYYY-MM-DD`.
- GitHub Pages publishes a `public/` copy of staging that excludes `L1-raw` and `L2-semantic`.
- Workflow diagnostics now include `extract-summary`, `process-summary`, and `pipeline-summary` artifacts for first-stop triage.
- Avoid hand-editing generated outputs if the next workflow run is expected to republish them.

## Workflow Triggers And Manual Inputs

- `push` runs only on `main` and follows the normal publish path.
- `schedule` runs on the first day of each month at `13:00 UTC`.
- `workflow_dispatch` exists for targeted verification and controlled reruns.
- Manual dispatch supports four inputs: `skip_wiki`, `skip_buildroot`, `skip_ai`, and `max_ai_files`.
- Manual dispatch can target a specific ref. Use `gh workflow run "openwrt-docs4ai-00-pipeline.yml" --ref <branch>` when you need remote proof for a non-`main` branch.
- Treat `workflow_dispatch` as the preferred remote test path for pipeline changes because it makes the intended skip knobs explicit in run history.

## Dependency Policy

- `.github/scripts/requirements.txt` is intentionally kept as a small direct dependency list rather than a blanket fully pinned lockfile.
- Add new direct dependencies only when they materially simplify the pipeline or improve output reliability.
- Do not add exact pins by default. Pin or lock only after verifying a concrete reproducibility or breakage problem.
- When a dependency-related failure appears, record the exact failing version in the investigation notes and then decide whether targeted pinning is justified.
- Keep local and CI bootstrap lightweight enough that a low-touch maintainer can rebuild the environment without a separate dependency-management project.

## Optional Workflow Linting

If you edit `.github/workflows/openwrt-docs4ai-00-pipeline.yml`, run `actionlint` locally when it is available on your machine. This is intentionally optional and is not a mandatory bootstrap dependency for the repo.

## CI Operations

### Waiting for a GitHub Actions run and reading its logs

This pipeline runs CI frequently. Follow the procedure below every time you push a commit and need to verify the result. Do not improvise — the anti-pattern list below is based on real mistakes that have caused wasted debug cycles in this project.

**Best method: pin-then-triage**

**Phase A — wait for the right run to complete**

1. Capture the exact commit SHA you pushed:

   ```powershell
   git rev-parse HEAD
   ```

2. List recent workflow runs and find the one that matches that SHA (never assume "latest" is yours — a deploy auto-update commit may have started a newer run):

   ```powershell
   gh run list --workflow "openwrt-docs4ai pipeline (v12)" --limit 20 --json databaseId,headSha,status,conclusion,url
   ```

3. Copy the `databaseId` of the matching entry and wait on that specific run with a bounded poll interval:

   ```powershell
   gh run watch <run_id> --exit-status --interval 15
   ```

   `--exit-status` returns exit code 1 on failure so the caller detects it without manual logic. `--interval 15` polls every 15 seconds. Block here until it exits — do not proceed to Phase B while the run is still in progress.

**Phase B — triage from summary artifacts before opening raw logs**

4. Download and inspect the structured pipeline summary artifact first:

   ```powershell
   gh run download <run_id> -n pipeline-summary -D tmp/ci/pipeline-summary
   Get-Content tmp/ci/pipeline-summary/*.json | ConvertFrom-Json
   ```

5. If that implicates a specific extractor, also pull the per-extractor status bundle:

   ```powershell
   gh run download <run_id> -n extract-summary -D tmp/ci/extract-summary
   ```

6. Only if the summary artifacts indicate a failure you still cannot explain structurally, open raw failed-job logs:

   ```powershell
   gh run view <run_id> --log-failed
   ```

Quick whole-run status check:

```powershell
gh run view <run_id> --json jobs,conclusion,url
```

### Things to avoid when waiting for CI

- **Do not poll "the latest run"** — always pin to the SHA of your push. After a successful deploy the workflow writes a bot-authored `docs: v12 auto-update YYYY-MM-DD` commit which triggers a new run; the "latest" ID is no longer yours.
- **Do not run an open-ended polling loop** — an unbounded `while ($true)` loop in a chat session consumes tokens, hides intermediate output, and looks like an infinite hang to both the user and the model. Always use `gh run watch` with `--interval` instead.
- **Do not pull full logs before the run finishes** — logs are noisy and incomplete mid-run; wait for `gh run watch` to exit cleanly before any log inspection.
- **Do not skip the artifact triage phase** — `pipeline-summary`, `process-summary`, and `extract-summary` exist precisely to avoid log forensics; read them first and fall back to raw logs only for unexplained failures.
- **Do not assume a deploy auto-commit is your commit** — verify by checking `headSha` on the run, not by run order.

## Environment Variables

Defaults below are the direct local defaults from `lib/config.py` and the local
AI tooling. The hosted workflow overrides `WORKDIR` and `OUTDIR`, and manual
dispatch exposes `skip_ai=false` by default.

| Variable | Default | Purpose |
| --- | --- | --- |
| `WORKDIR` | `tmp` | Scratch area for cloned repos and intermediate layers |
| `OUTDIR` | `openwrt-condensed-docs` | Stable output root for generated artifacts |
| `SKIP_WIKI` | `false` | Skip wiki extraction |
| `SKIP_AI` | `true` | Disable optional AI enrichment by default |
| `WRITE_AI` | `true` | Allow script `04` to create missing base records when AI is enabled |
| `WIKI_MAX_PAGES` | `300` | Limit wiki traversal depth |
| `MAX_AI_FILES` | `40` | Limit local or remote AI summary volume |
| `VALIDATE_MODE` | `hard` | Validation severity mode |
| `GITHUB_TOKEN` | empty | Remote-only integrations and telemetry fallback retrieval |
| `LOCAL_DEV_TOKEN` | empty | Local override token for optional AI enrichment |
| `AI_DATA_BASE_DIR` | `data/base` | Base AI summary store root |
| `AI_DATA_OVERRIDE_DIR` | `data/override` | Override AI summary store root |

## Documentation And Reporting Conventions

- Use relative Markdown links for navigational cross-references between maintainer documents and generated outputs.
- When a file or path reference is meant to be opened by the reader, prefer a Markdown link instead of an inline code span.
- Keep inline code for commands, environment variables, symbol names, filenames used as literals, and short syntax fragments.
- Do not inject or rewrite cross-links inside code fences or inline code spans.

## Adding or Changing a Scraper

If a new extractor is added or a current extractor is materially changed:

1. Keep it in `.github/scripts/` with the numbered naming convention.
2. Make sure it writes only to `WORKDIR/L1-raw/{module}/`.
3. Write `.meta.json` sidecars through shared helper logic instead of ad hoc metadata code.
4. Update the deterministic tests and the sequential smoke runner.
5. Update `docs/ARCHITECTURE.md` and active v12 specs if the contract changed.

## Logging Convention

Scripts should emit concise line-buffered messages using the numbered prefix convention, for example:

```text
[02a] OK: scraped 15 pages
[05d] INFO: Baseline lacks module metadata; suppressing module drift sections
[04] SKIP: AI enrichment disabled
[08] FAIL: missing llms.txt
```

## Deferred Bugs

- `luci-app-dockerman` still produces one truthful non-blocking standalone `ucode` validation warning in `docker_rpc.uc`. Keep it soft until a higher-fidelity LuCI runtime validation context exists.
- Mermaid template promotion is still deferred. The repository has Mermaid source templates, but the exact publication targets and insertion rules are not constrained tightly enough to inject diagrams automatically without risking incorrect output.

## Deferred Features

- Extreme A3 renaming remains deferred. If revisited, prefer fully descriptive stage-prefixed or category-first filenames only after the current moderate stage-family contract is stable across the workflow, tests, and docs.
- `signature-inventory.json` still does not emit explicit module metadata. The current `05d` fix suppresses false module drift against legacy baselines; richer schema expansion remains a later compatibility decision.
- Curated example extraction still warns on partial read failures instead of failing the run. Hard-failing partial omissions is deferred until the curated app and file inventory is formalized.
- Broader validation coverage beyond the current targeted fixes is deferred until the renamed stage contract and baseline expectations are stable.

## Windows Notes

- Windows is a required development environment for this project.
- Path logic must remain cross-platform, but local development is the first validation target.
- A small number of Linux-only checks may exist later for remote workflow validation, but they must be documented explicitly.

## Current Focus

The pipeline reached a stable, fully-tested state on 2026-03-11. All stabilization phases are complete.

Ongoing monitored items:

1. The `luci-app-dockerman` ucode warning (`REMOTE-008`) remains a deferred soft warning — intentionally preserved as a truthful signal, not suppressed.
2. Mermaid diagram template promotion remains deferred until a concrete consumer exists.

The pipeline is otherwise healthy: local tests pass, CI runs succeed with 0 hard failures, and published outputs are generated and committed correctly on every run. When returning to active development, run `python tests/run_pytest.py` locally first, then use `python tests/run_smoke_and_pytest.py` before following the CI Operations procedure above.
