# Repo Hygiene Plan

Recorded: 2026-03-10

## Status On 2026-03-10

- The stage-family rename and conservative hardening pass completed and was verified both locally and on GitHub Actions.
- Rolling smoke helpers now write active logs under `tmp/logs/`, not under `tests/`.
- Historical tracked smoke logs under `tests/` and tracked `lib/__pycache__/` files are being removed so future local runs stay out of Git history.
- A durable implementation report for the rename, bug-fix, and verification pass lives in `docs/plans/v12/pipeline-stage-alignment-report-2026-03-10.md`.

## Goals

- Keep local scratch output out of `tests/` and the repo root.
- Keep the current Windows local workflow and GitHub Actions workflow working without path churn.
- Make it obvious which folders are authoritative, which are committed, and which are disposable.

## Workspace Map

| Path | Keep in git? | What belongs here | What does not belong here |
| --- | --- | --- | --- |
| `.github/scripts/` | Yes | Live pipeline code | Scratch experiments, one-off copies |
| `.github/workflows/` | Yes | Live CI orchestration | Local-only helper commands or notes |
| `lib/` | Yes | Shared Python helpers | Throwaway utilities used once |
| `tests/` | Yes | Real tests, fixtures, intentionally committed test helpers | Rolling logs, temp outputs, ad hoc result dumps |
| `tests/fixtures/` | Yes | Small durable repro inputs | Generated run output |
| `docs/plans/v12/` | Yes | Maintainer plans, review notes, hygiene docs | Large generated comparisons |
| `openwrt-condensed-docs/` | Yes | Intended published output tree | Scratch rewrites, temporary comparisons |
| `tmp/` | No | Local scratch space, temp runs, logs, review bundles, copied snapshots | Anything you expect to publish or review in Git history |
| `tmp/logs/` | No | Rolling smoke logs, terminal captures, step-by-step debug logs | Committed test evidence |
| `tmp/reports/` | No | Before/after comparisons, local review bundles, AI scratch reports | Durable project documentation |
| `tmp/scratch/` | No | Experimental copies of docs or scripts | Finalized files |
| `staging/` | No | CI promotion output only | Manual working files |
| `ai-summaries-cache.json` | Yes, for now | Current workflow cache contract | Random local JSON notes |

## Authoritative Names And Contracts

| Name | Current meaning | Keep as-is in first pass? |
| --- | --- | --- |
| `tmp/` | Local and CI scratch/work area (`WORKDIR`) | Yes |
| `staging/` | CI promotion output (`OUTDIR` in Actions) | Yes |
| `openwrt-condensed-docs/` | Stable generated and published output root | Yes |
| `ai-summaries-cache.json` | Current repo-root AI cache file used by the workflow | Yes |

These names are already wired into the workflow, the architecture docs, and the local developer docs. Renaming them now would create needless churn.

## Where To Work

| Task | Work here |
| --- | --- |
| Change live pipeline behavior | `.github/scripts/` and `lib/` |
| Change CI behavior | `.github/workflows/` |
| Add a new committed regression test | `tests/` |
| Add a tiny reusable test input | `tests/fixtures/` |
| Write a maintainer note or plan you want in Git history | `docs/plans/v12/` |
| Inspect the current publishable output | `openwrt-condensed-docs/` |
| Run local smoke tests and keep logs | `tmp/logs/` |
| Save a one-off comparison bundle or model review | `tmp/reports/<date>-<topic>/` |
| Copy files around for experiments | `tmp/scratch/` |

Short rule: if the file is not part of the product, the tests, or the maintainer docs, it belongs under `tmp/`.

## First-Pass Hygiene Changes

The first-pass repo cleanup should stay conservative:

1. Move rolling smoke logs out of `tests/` and into `tmp/logs/`.
2. Ignore Python bytecode and pytest caches.
3. Ignore ad hoc local result bundles such as `tests/comprehensive-test-results-*`.
4. Leave `tmp/`, `staging/`, `openwrt-condensed-docs/`, and `ai-summaries-cache.json` in place.

This pass is about reducing noise, not redesigning the pipeline layout.

## Local Working Rules

1. Do not put rolling logs in `tests/`.
2. Do not put ad hoc comparison folders in `tests/`.
3. Do not drop local cache files into the repo root unless they are already part of the workflow contract.
4. If you are comparing old and new generated docs, copy both versions into `tmp/reports/` and diff there.
5. If you want a note or plan to survive and be reviewable on GitHub, put it in `docs/plans/v12/`, not `tmp/`.

## PowerShell Cleanup For Current Local Noise

Create the local-only folders once:

```powershell
New-Item -ItemType Directory -Force tmp\logs | Out-Null
New-Item -ItemType Directory -Force tmp\reports | Out-Null
New-Item -ItemType Directory -Force tmp\scratch | Out-Null
```

Move an existing ad hoc result bundle out of `tests/` if you want to keep it locally but not track it:

```powershell
Move-Item -Force tests\comprehensive-test-results-3-10 tmp\reports\2026-03-10-comprehensive-test-results
```

Clean local Python cache noise:

```powershell
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -File -Include *.pyc,*.pyo | Remove-Item -Force -ErrorAction SilentlyContinue
```

## What Not To Move In This Pass

| Path | Why not move it yet |
| --- | --- |
| `tmp/` | Already documented as the ephemeral work area across local and CI paths |
| `staging/` | Explicitly used by the GitHub Actions promotion flow |
| `openwrt-condensed-docs/` | This is the stable publish root and current Pages source contract |
| `ai-summaries-cache.json` | The workflow and script `04` already treat this repo-root file as the default cache contract |

## Wiki Residue Policy

Do not do a blanket search-and-replace pass on the remaining wiki residue.

| Residue family | Example shape | Current policy | Reason |
| --- | --- | --- | --- |
| Note markers | `:!:` | Keep for now; later convert only with a line-aware rule | Some are clear note prefixes, but they also appear embedded in dense prose and tables |
| Color/status tokens | `@lightgreen:`, `@yellow:`, `@pink:` | Keep for now; later normalize only inside known table/status contexts | Blind deletion loses state labels that still carry meaning |
| Layout placeholders | `:::` | Leave alone until there is a table-aware transform | In current L2 these often act as structural cells, not mere noise |
| Legacy pseudo-links | `commit>?...` | Leave alone until there is a dedicated converter | The parameters vary, so blind replacement will create bad links |
| Pagequery and image-macro residue | `/pagequery>* ...` | Leave alone until there is a pagequery-specific rule | These need parser logic, not text deletion |
| Unknown markers | `:?:`, `???` | Leave alone unless a source-specific rule is added | They still carry uncertainty or placeholder meaning |

## Safe Normalization Bar

A residue family is only safe to normalize when all three conditions are true:

1. The pattern is structurally identifiable.
2. The replacement preserves meaning rather than just hiding noise.
3. A regression test exists for both the good conversion case and the must-not-touch case.

Until then, prefer readable tolerated residue over a broad replacement that damages meaning.

## Immediate Outcome Expected From This Plan

- Local smoke runs write their logs under `tmp/logs/`.
- Python cache noise stops polluting `git status`.
- Large ad hoc local review bundles stop appearing under `tests/` by default.
- The repo keeps its current Windows and GitHub Actions path contracts intact.