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
python tests/00-smoke-test.py
python tests/00-smoke-test.py --run-ai
python tests/openwrt-docs4ai-00-smoke-test.py
python tests/openwrt-docs4ai-00-smoke-test.py --run-ai
```

The `--run-ai` path is cache-backed for local verification, so it can validate the placement and mutation behavior of script `04` without requiring a live model token.

## Repository Rules

- `openwrt-condensed-docs/` is the stable generated output root.
- `tmp/` is ephemeral and never authoritative.
- `L1-raw` and `L2-semantic` are the standard intermediate layer names.
- Script numbering denotes run order. Letter suffixes denote scripts that are parallelizable in deployment.
- Local smoke runs may still execute the lettered scripts sequentially.

## Script Families

| Script | Role |
| --- | --- |
| `openwrt-docs4ai-01-clone-repos.py` | Prepare L0 source inputs and manifests |
| `openwrt-docs4ai-02a` through `02h` | Source-specific extraction into L1 |
| `openwrt-docs4ai-03-normalize-semantic.py` | L1 to L2 normalization and promotion |
| `openwrt-docs4ai-04-generate-ai-summaries.py` | Optional AI summary enrichment |
| `openwrt-docs4ai-05-assemble-references.py` | L3 skeleton and L4 monolith assembly |
| `openwrt-docs4ai-06a` through `06d` | Maps, agent guidance, IDE schemas, telemetry |
| `openwrt-docs4ai-07-generate-index-html.py` | HTML landing page generation |
| `openwrt-docs4ai-08-validate.py` | Whole-output validation gate |

## Local Tests

- `tests/00-smoke-test.py` is the deterministic fixture-heavy smoke path.
- `tests/openwrt-docs4ai-00-smoke-test.py` is the sequential local runner intended to exercise the numbered scripts more directly.

During the current stabilization pass, these test entry points are being repaired and treated as first-class engineering assets.

## Remote Publish Policy

- The workflow builds generated artifacts into `staging/` first and only promotes them in the `deploy` job.
- On push, schedule, and manual runs, the deploy job syncs `staging/` into `openwrt-condensed-docs/` with `rsync -a --delete`.
- If the promoted tree changed, GitHub Actions writes a bot-authored commit in the form `docs: v12 auto-update YYYY-MM-DD`.
- GitHub Pages publishes a `public/` copy of staging that excludes `L1-raw` and `L2-semantic`.
- Avoid hand-editing generated outputs if the next workflow run is expected to republish them.

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `WORKDIR` | `tmp` | Scratch area for cloned repos and intermediate layers |
| `OUTDIR` | `openwrt-condensed-docs` | Stable output root for generated artifacts |
| `SKIP_WIKI` | `false` | Skip wiki extraction |
| `SKIP_AI` | `true` | Disable optional AI enrichment by default |
| `WIKI_MAX_PAGES` | `300` | Limit wiki traversal depth |
| `MAX_AI_FILES` | `40` | Limit local or remote AI summary volume |
| `VALIDATE_MODE` | `hard` | Validation severity mode |
| `GITHUB_TOKEN` | empty | Remote-only integrations and telemetry fallback retrieval |
| `LOCAL_DEV_TOKEN` | empty | Local override token for optional AI enrichment |

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
[04] SKIP: AI enrichment disabled
[08] FAIL: missing llms.txt
```

## Windows Notes

- Windows is a required development environment for this project.
- Path logic must remain cross-platform, but local development is the first validation target.
- A small number of Linux-only checks may exist later for remote workflow validation, but they must be documented explicitly.

## Current Focus

The immediate engineering focus is:

1. keep local and remote verification green while leaving the remaining dockerman warning as a truthful deferred soft warning
2. finish validating the bounded L2 wiki cleanup against regenerated real outputs
3. only add corpus-level QA or telemetry if the maintenance cost is justified by clear payoff for this pipeline
