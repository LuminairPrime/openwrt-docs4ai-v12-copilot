# openwrt-docs4ai Architecture

## Purpose

This repository is a documentation production pipeline, not an application runtime. Its job is to collect OpenWrt documentation from multiple upstream sources, normalize it into stable intermediate layers, and publish compact outputs that are useful to humans, IDE tooling, and LLM workflows.

The primary engineering goal for the current stage is maintainable correctness on Windows with verified remote publication behavior. Local validation remains the first gate, and GitHub Actions is now a confirmed verification and deployment layer rather than an unproven future target.

## Repository Zones

| Path | Role | Notes |
| --- | --- | --- |
| `.github/scripts/` | Numbered pipeline scripts | `00` is workflow orchestration, `01` through `08` are ordered pipeline stages. Letter suffixes indicate scripts that are parallelizable in deployment. |
| `.github/workflows/` | GitHub Actions workflows | Remote execution only. Current stabilization work does not assume GitHub behavior is already verified. |
| `lib/` | Shared Python support code | Shared config, file writing, extraction helpers, and other reusable logic. |
| `tests/` | Local deterministic tests and smoke runners | Local verification is required before remote workflow testing. |
| `docs/specs/v12/` | Active v12 technical specifications | These are the current engineering references. |
| `docs/archive/v12/` | Archived planning and review material | Historical context only. Not authoritative for implementation. |
| `openwrt-condensed-docs/` | Published output root | Stable output tree for generated artifacts and local inspection. |
| `tmp/` | Ephemeral working area | Never authoritative. Safe to delete between runs. |
| `templates/` | Static content templates | Only keep templates that are actually consumed by the live pipeline. |

## Layer Model

| Layer | Meaning | Primary Location | Persistence |
| --- | --- | --- | --- |
| `L0` | Untouched upstream source inputs | `tmp/repo-*` | Ephemeral |
| `L1` | Raw normalized markdown plus sidecar metadata | `tmp/L1-raw/` during build, optionally copied to `openwrt-condensed-docs/L1-raw/` for inspection | Generated |
| `L2` | Semantic markdown with YAML frontmatter and cross-links | `tmp/L2-semantic/` during build, optionally copied to `openwrt-condensed-docs/L2-semantic/` for inspection | Generated |
| `L3` | Navigational and operational outputs | `openwrt-condensed-docs/` and module subdirectories | Published |
| `L4` | Monolithic reference files | `openwrt-condensed-docs/{module}/` | Published |
| `L5` | Telemetry and drift outputs | `openwrt-condensed-docs/` | Published |

## Naming Conventions

### Script numbering

- `00` denotes orchestration or workflow entry points.
- `01` through `08` denote the sequential execution order.
- A letter suffix such as `06a` or `06d` denotes scripts that can run in parallel in deployment.
- Local smoke tests may still run all scripts sequentially for simplicity and debuggability.

### Directory names

- Use `L1-raw` and `L2-semantic` without leading dots.
- Avoid hidden directory naming for active pipeline outputs because the current project targets Windows development and public GitHub use.
- Use lowercase, hyphenated filenames for human-authored specs in `docs/specs/v12/`.

### Output philosophy

- `openwrt-condensed-docs/` is the stable output root for generated documentation.
- `docs/` is for maintainers and project documentation only.
- `tmp/` is scratch space and must never be treated as durable state.

## Execution Contract

1. `01` prepares local source inputs and manifests.
2. `02a` through `02h` extract source-specific content into L1.
3. `03` normalizes L1 into L2 and promotes stable intermediates into the output tree.
4. `04` optionally enriches staged L2 files with AI summary metadata.
5. `05` assembles skeletons and monolithic references.
6. `06a` through `06d` generate indexes, agent guidance, IDE schemas, and telemetry.
7. `07` generates the HTML landing page after the map outputs exist.
8. `08` validates the entire output tree.

## Local-First Verification Model

- The required first-stage verification path is local and sequential.
- Deterministic fixture tests are the core protection against accidental regressions.
- Local smoke tests should isolate `WORKDIR` and `OUTDIR` so the repository is not corrupted during development.
- GitHub Actions remains a second-stage verification target after local proof, and it is now also the normal publication path for generated outputs.

## Remote Promotion Contract

- The `process` job builds generated artifacts into `staging/` (`OUTDIR`) and uploads that tree as `final-staging`.
- The `deploy` job promotes `final-staging` into `openwrt-condensed-docs/` with `rsync -a --delete`.
- Generated-output commits use the `docs: v12 auto-update YYYY-MM-DD` format and are written by the GitHub Actions bot only when the staged tree changed.
- GitHub Pages publishes a `public/` copy of staging that excludes `L1-raw` and `L2-semantic`, so those intermediate layers remain committed in-repo without being exposed on the public site.

## Active Documents

- `README.md`: short external overview.
- `DEVELOPMENT.md`: maintainer quick start and local workflow reference.
- `docs/ARCHITECTURE.md`: durable architecture and naming contract.
- `docs/specs/v12/`: active v12 specifications, current status, execution map, active bug log, and stabilization plan.

## Archive Policy

Documents under `docs/archive/v12/` remain useful as historical design context, but they do not control implementation. If an archived document conflicts with an active spec or with verified code behavior, the active spec wins.