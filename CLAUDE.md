# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Does

**openwrt-docs4ai** is a documentation production pipeline — not an application runtime. It collects OpenWrt documentation from multiple upstream sources (wiki, git repos, authored cookbook content, and APIs), normalizes it through a staged layer model (L0→L1→L2→L3/L4), and publishes compact outputs for humans, IDE tooling, and LLM workflows. GitHub Actions is the verified remote execution path; Windows is the primary local development environment. The active output model is the V6 release-tree contract, which separates publishable output from internal pipeline artifacts and deploys to external distribution targets.

## Prerequisites

```powershell
pip install -r .github/scripts/requirements.txt
npm install -g jsdoc-to-markdown
winget install --id JohnMacFarlane.Pandoc
```

Use the workspace interpreter directly when needed: `.venv/Scripts/python.exe`. Do not assume the system `python` on PATH is the repo interpreter.

## Local Validation Commands

Run the smallest proof first, then expand:

```powershell
python tests/run_pytest.py                              # focused pytest suites
python tests/run_smoke.py                               # serial smoke lane
python tests/run_smoke_and_pytest.py                    # preferred full local validation
python tests/run_smoke_and_pytest.py --run-ai --keep-temp
python tests/run_smoke_and_pytest_parallel.py           # parallel pytest + smoke
python tests/check_linting.py                           # Ruff + strict Pyright + actionlint

python tools/manage_ai_store.py --option review         # AI store review (no promotion)
python tools/manage_ai_store.py --option full --keep-scratch
```

`--run-ai` is cache-backed for regression proof only — it does not generate real AI summaries or promote to the AI store. Results land under `tmp/ci/`.

## Cookbook Regeneration Guardrail

Do not assume a cookbook-only source edit is isolated just because the authored files live under `content/cookbook-source/`.

- A local rerun through `03` and `05a` can dirty or truncate unrelated generated trees under `staging/`, `release-tree/`, and `support-tree/` when the working tree is already partial.
- For cookbook authoring fixes, prefer the smallest proof first. If cookbook outputs are already present and only root routing surfaces need refresh, restore unrelated generated paths from `HEAD` and rerun only `06 -> 07 -> 08` after preserving the cookbook slice.
- If validation starts failing on unrelated modules after a cookbook-only rerun, restore non-cookbook generated paths instead of editing unrelated generated content.

## Running a Single Test

```powershell
python tests/run_pytest.py tests/pytest/pytest_01_workflow_contract_test.py
python tests/run_pytest.py -k "test_name_pattern"
```

## Review Discipline

This repository is a documentation production pipeline, not a long-running user-facing application. Most regressions are recoverable and show up quickly in execution-time evidence: focused pytest failures, deterministic smoke failures, Ruff or Pyright diagnostics, actionlint errors, and GitHub Actions summary artifacts.

- Prefer the cheapest proof that can fail: focused pytest, deterministic smoke, `tests/check_linting.py`, then pinned CI artifact triage.
- Treat reviewer agents as optional spot-checks, not the primary safety mechanism.
- For most changes, use at most one reviewer-style pass. Do not stack `code-reviewer` and `python-reviewer` by default on the same diff.
- If a bug can be reproduced from runtime evidence or CI artifacts, fix from that evidence instead of spending extra tokens on repeated speculative review rounds.
- Re-run reviewer agents only after a substantial redesign or when local and CI evidence is still ambiguous.

## CI Operations

Always pin to your commit SHA — a successful deploy triggers a bot commit (`docs: auto-update YYYY-MM-DD`) that starts a new "latest" run.

```powershell
git rev-parse HEAD
gh run list --workflow "openwrt-docs4ai-pipeline" --limit 20 --json databaseId,headSha,status,conclusion,url
gh run watch <run_id> --exit-status --interval 15

# After completion — triage artifacts before raw logs
gh run download <run_id> -n pipeline-summary -D tmp/ci/pipeline-summary
gh run download <run_id> -n extract-summary -D tmp/ci/extract-summary
gh run view <run_id> --log-failed                       # only if artifacts don't explain it
```

## Architecture: Layer Model

| Layer | Location | Purpose | Lifetime |
| ----- | -------- | ------- | -------- |
| L0 | `tmp/repo-*` | Upstream source clones | Ephemeral |
| L1 | `L1-raw/{module}/` | Raw normalized markdown + `.meta.json` sidecars | Generated |
| L2 | `L2-semantic/{module}/` | Semantic markdown + YAML frontmatter + cross-links | Generated |
| L3/L4 | `release-tree/{module}/` | Published references, maps, routing indexes, and IDE surfaces | Published |

Pipeline scripts generate into `staging/` (the default `OUTDIR`, gitignored). Tests read from `staging/` to validate fresh output. CI generates into `staging/`, then publishes `staging/release-tree/` to external distribution targets and mirrors the full tree to `gh-pages` for test preview.

There is no tracked publish root in the source repository. External publication ships the `release-tree/` subtree as the direct-root `release-tree/` layout. `tmp/` is ephemeral scratch, never authoritative.

## Architecture: Pipeline Stage Flow

Scripts in `.github/scripts/` execute in numbered order. Letter suffixes (e.g., `05a`, `05b`) are siblings in the same stage family. A bare stage id (e.g., `04`) cannot coexist with lettered siblings.

| Script | Stage | Role |
| ------ | ----- | ---- |
| `01-clone-repos.py` | L0 | Shallow-clone ucode, luci, openwrt repos; emit `repo-manifest.json` |
| `02a-scrape-wiki.py` | L1 | Wiki extraction (runs in parallel with `01` on CI) |
| `02b` – `02h` | L1 | Source-specific extractors (clone-gated); each writes to `L1-raw/{module}/` |
| `03-normalize-semantic.py` | L2 | Add YAML frontmatter, cross-links, token counts |
| `04-generate-ai-summaries.py` | L2 | Optional AI enrichment; reads/writes `data/base/` AI store |
| `05a-assemble-references.py` | L4 | Build internal references plus release-tree bundled references and maps |
| `05b-generate-agents-and-readme.py` | L3 | Generate `AGENTS.md` and root `README.md` for the corpus |
| `05c-generate-ucode-ide-schemas.py` | L3 | TypeScript `.d.ts` IDE schemas |
| `05d-generate-api-drift-changelog.py` | L5 | API drift telemetry vs. signature baseline |
| `05e-generate-luci-dts.py` | L3 | LuCI TypeScript `.d.ts` IDE schemas |
| `06-generate-llm-routing-indexes.py` | L3 | `llms.txt`, `llms-full.txt`, per-module `llms.txt` |
| `07-generate-web-index.py` | L3 | Root and release-tree `index.html`, release overlays, and support-tree materialization |
| `08-validate-output.py` | — | Whole-output validation gate |

Shared Python libraries live in `lib/` (`config.py`, `ai_store.py`, `ai_enrichment.py`, etc.). Non-numbered maintainer tools live in `tools/`.

## Architecture: Two LLM Surfaces

This repo has two distinct LLM-relevant surfaces — do not conflate them:

- **Source repo** (`docs/`, `DEVELOPMENT.md`, `README.md`): Maintainer docs and implementation.
- **Generated corpus** (`staging/release-tree/` locally, `release-tree/` externally): Published AI navigation surface consumed by downstream tools. Routing contracts defined in `docs/specs/schema-definitions.md`.

The source repository does not track generated output. All generated content lives in `staging/` (gitignored) or external distribution targets.

A source-repo root `llms.txt` is intentionally out of scope. Do not create one.

## Pre-Change Checklist

Before editing numbered scripts or the workflow:

1. Read `docs/ARCHITECTURE.md`, `docs/specs/schema-definitions.md`, and `docs/specs/pipeline-stage-catalog.md`.
2. For `05b`–`08` changes: inspect current `staging/llms.txt`, `staging/llms-full.txt`, and `staging/AGENTS.md` first (generate fresh output if needed).
3. For workflow changes: map the change to a specific trigger path (push/schedule/dispatch).

## Key Conventions

- **Logging prefix:** `[02a] OK: scraped 15 pages` / `[08] FAIL: missing llms.txt`
- **Intermediate names:** `L1-raw` and `L2-semantic` — no leading dots, no hidden dirs (Windows compat)
- **New extractors:** write only to `WORKDIR/L1-raw/{module}/`, use shared helper for `.meta.json` sidecars, update tests and `docs/ARCHITECTURE.md`
- **Dependencies:** Keep `requirements.txt` as a small direct list; do not pin by default
- **Docs cross-links:** Use relative Markdown links, not inline code spans, for navigational references
- **Public contract:** `release-tree/` is the only publishable layout; `support-tree/` is internal-only support state.
- **Review budget:** optimize for fast local proof and CI artifact triage before invoking expensive reviewer agents.

## Known Deferred Items

- `luci-app-dockerman` ucode validation warning (`REMOTE-008`): intentionally kept soft (truthful signal).
- Mermaid template promotion: deferred until a concrete consumer exists.
- `signature-inventory.json` module metadata: current `05d` fix suppresses false drift; richer schema is deferred.
- The live public contract is `docs/specs/release-tree-contract.md`. Archived V12 rollout material remains under `docs/archive/v12/specs/` for history only.

## Key Reference Files

- `DEVELOPMENT.md` — full maintainer quick-start and CI operations detail
- `docs/ARCHITECTURE.md` — durable architecture and naming contract
- `docs/specs/schema-definitions.md` — generated corpus filesystem and data contracts
- `docs/specs/pipeline-stage-catalog.md` — stage ordering and rerun guidance
- `docs/guides/runbook-ai-summary-operations.md` — AI store workflow
- `tests/README.md` — test folder contract and runner/output mapping
- `docs/specs/release-tree-contract.md` — live public output contract
- `docs/archive/v12/specs/feature-flag-contract.md` — retired rollout history for the removed feature flag
- `docs/archive/v12/plans/public-distribution-mirror-plan-2026-03-15-V5a.md` — archived V5a implementation plan
