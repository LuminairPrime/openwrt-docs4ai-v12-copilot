# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Does

**openwrt-docs4ai** is a documentation production pipeline — not an application runtime. It collects OpenWrt documentation from multiple upstream sources (wiki, git repos, APIs), normalizes it through a staged layer model (L0→L1→L2→L3/L4), and publishes compact outputs for humans, IDE tooling, and LLM workflows. GitHub Actions is the verified remote execution path; Windows is the primary local development environment. The active output model is the V5a release-tree contract, which separates publishable output from internal pipeline artifacts and deploys to external distribution targets.

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

## Running a Single Test

```powershell
python tests/run_pytest.py tests/pytest/pytest_01_workflow_contract_test.py
python tests/run_pytest.py -k "test_name_pattern"
```

## CI Operations

Always pin to your commit SHA — a successful deploy triggers a bot commit (`docs: v12 auto-update YYYY-MM-DD`) that starts a new "latest" run.

```powershell
git rev-parse HEAD
gh run list --workflow "openwrt-docs4ai pipeline (v12)" --limit 20 --json databaseId,headSha,status,conclusion,url
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

`openwrt-condensed-docs/` is the **stable internal output root** — never hand-edit it if a workflow run will overwrite it. Local and CI runs materialize the public contract under `openwrt-condensed-docs/release-tree/`, and external publication ships that subtree as the direct-root `release-tree/` layout. `tmp/` is ephemeral scratch, never authoritative.

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
| `06-generate-llm-routing-indexes.py` | L3 | `llms.txt`, `llms-full.txt`, per-module `llms.txt` |
| `07-generate-web-index.py` | L3 | Root and release-tree `index.html`, release overlays, and support-tree materialization |
| `08-validate-output.py` | — | Whole-output validation gate |

Shared Python libraries live in `lib/` (`config.py`, `ai_store.py`, `ai_enrichment.py`, etc.). Non-numbered maintainer tools live in `tools/`.

## Architecture: Two LLM Surfaces

This repo has two distinct LLM-relevant surfaces — do not conflate them:

- **Source repo** (`docs/`, `DEVELOPMENT.md`, `README.md`): Maintainer docs and implementation.
- **Generated corpus** (`openwrt-condensed-docs/release-tree/` locally, `release-tree/` externally): Published AI navigation surface consumed by downstream tools. Routing contracts defined in `docs/specs/v12/schema-definitions.md`.

The `openwrt-condensed-docs` name is internal-only and must never appear in any public path.

A source-repo root `llms.txt` is intentionally out of scope. Do not create one.

## Pre-Change Checklist

Before editing numbered scripts or the workflow:

1. Read `docs/ARCHITECTURE.md`, `docs/specs/v12/schema-definitions.md`, and `docs/specs/v12/execution-map.md`.
2. For `05b`–`08` changes: inspect current `openwrt-condensed-docs/llms.txt`, `llms-full.txt`, and `AGENTS.md` first.
3. For workflow changes: map the change to a specific trigger path (push/schedule/dispatch).

## Key Conventions

- **Logging prefix:** `[02a] OK: scraped 15 pages` / `[08] FAIL: missing llms.txt`
- **Intermediate names:** `L1-raw` and `L2-semantic` — no leading dots, no hidden dirs (Windows compat)
- **New extractors:** write only to `WORKDIR/L1-raw/{module}/`, use shared helper for `.meta.json` sidecars, update tests and `docs/ARCHITECTURE.md`
- **Dependencies:** Keep `requirements.txt` as a small direct list; do not pin by default
- **Docs cross-links:** Use relative Markdown links, not inline code spans, for navigational references
- **Public contract:** `release-tree/` is the only publishable layout; `support-tree/` is internal-only support state.

## Known Deferred Items

- `luci-app-dockerman` ucode validation warning (`REMOTE-008`): intentionally kept soft (truthful signal).
- Mermaid template promotion: deferred until a concrete consumer exists.
- `signature-inventory.json` module metadata: current `05d` fix suppresses false drift; richer schema is deferred.
- V5a release-tree rollout is complete. Use `docs/specs/v12/release-tree-contract.md` for the live contract and `docs/specs/v12/feature-flag-contract.md` only for rollout history.

## Key Reference Files

- `DEVELOPMENT.md` — full maintainer quick-start and CI operations detail
- `docs/ARCHITECTURE.md` — durable architecture and naming contract
- `docs/specs/v12/schema-definitions.md` — generated corpus filesystem and data contracts
- `docs/specs/v12/execution-map.md` — stage dependency map
- `docs/specs/v12/ai-summary-operations-runbook.md` — AI store workflow
- `tests/README.md` — test folder contract and runner/output mapping
- `docs/specs/v12/release-tree-contract.md` — V5a public output contract
- `docs/specs/v12/feature-flag-contract.md` — retired rollout history for the removed feature flag
- `docs/plans/v12/public-distribution-mirror-plan-2026-03-15-V5a.md` — V5a implementation plan
