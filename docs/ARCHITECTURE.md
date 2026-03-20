# openwrt-docs4ai Architecture

## Purpose

This repository is a documentation production pipeline, not an application runtime. Its job is to collect OpenWrt documentation from multiple upstream sources, normalize it into stable intermediate layers, and publish compact outputs that are useful to humans, IDE tooling, and LLM workflows.

The primary engineering goal for the current stage is maintainable correctness on Windows with verified remote publication behavior. Local validation remains the first gate, and GitHub Actions is now a confirmed verification and deployment layer rather than an unproven future target.

The repository also has a dual-role documentation boundary: maintainer guidance lives in the source tree under `docs/`, while the generated AI-facing navigation surface lives under `openwrt-condensed-docs/`. The generated-corpus routing contract is authoritative for `llms.txt`, `llms-full.txt`, module `llms.txt`, and `AGENTS.md`; a source-repo root `llms.txt` remains explicitly deferred. The live public contract is the V5a release-tree layout, which separates the publishable output (`release-tree/`) from internal pipeline artifacts and uses generic public filenames (`map.md`, `bundled-reference.md`, `chunked-reference/`) instead of module-prefixed names.

## Repository Zones

| Path | Role | Notes |
| --- | --- | --- |
| `.github/scripts/` | Numbered pipeline scripts | `00` is workflow orchestration. Whole numbers denote stage boundaries, and letter suffixes denote sibling scripts within a stage family. A bare stage id cannot coexist with same-family lettered siblings. |
| `.github/workflows/` | GitHub Actions workflows | Remote execution only. Current stabilization work does not assume GitHub behavior is already verified. |
| `lib/` | Shared Python support code | Shared config, file writing, extraction helpers, and other reusable logic. |
| `tools/` | Non-numbered maintainer support tools | Local-only operator CLIs and helpers that are not part of the numbered hosted pipeline surface. |
| `tests/` | Local deterministic tests and smoke runners | Local verification is required before remote workflow testing. |
| `docs/specs/v12/` | Active v12 technical specifications | These are the current engineering references. |
| `docs/archive/v12/` | Archived planning and review material | Historical context only. Not authoritative for implementation. |
| `openwrt-condensed-docs/` | Published output root | Stable output tree for generated artifacts and local inspection. |
| `tmp/` | Ephemeral working area | Never authoritative. Safe to delete between runs. |
| `templates/` | Static content templates | Only keep templates that are actually consumed by the live pipeline. |
| `openwrt-condensed-docs/release-tree/` | Publishable output root inside staged source-repo output | External publish targets receive this subtree as the direct-root `release-tree/` layout. |
| `openwrt-condensed-docs/support-tree/` | Internal CI support artifacts | Not public; may be uploaded as CI artifact. |
| `release-inputs/` | Source-controlled overlay directories | `release-include/` (common), `pages-include/` (Pages-specific), `release-repo-include/` (reserved). |

## Layer Model

| Layer | Meaning | Primary Location | Persistence |
| --- | --- | --- | --- |
| `L0` | Untouched upstream source inputs | `tmp/repo-*` | Ephemeral |
| `L1` | Raw normalized markdown plus sidecar metadata | `tmp/L1-raw/` during build, optionally copied to `openwrt-condensed-docs/L1-raw/` for inspection | Generated |
| `L2` | Semantic markdown with YAML frontmatter and cross-links | `tmp/L2-semantic/` during build, optionally copied to `openwrt-condensed-docs/L2-semantic/` for inspection | Generated |
| `L3` | Navigational and operational outputs | `openwrt-condensed-docs/` and module subdirectories | Published |
| `L4` | Complete-reference index files plus optional sharded parts | `openwrt-condensed-docs/{module}/` | Published |
| `L5` | Telemetry and drift outputs | `openwrt-condensed-docs/` | Published |
| `L3/L4` | Public publish contract with renamed files (`map.md`, `bundled-reference.md`, `chunked-reference/`). | `openwrt-condensed-docs/release-tree/{module}/` during staging, `release-tree/{module}/` when published externally | Published |

## Naming Conventions

### Script numbering

- `00` denotes orchestration or workflow entry points.
- Whole numbers denote dependency boundaries and high-level stage order.
- A letter suffix such as `05a` or `05d` denotes sibling scripts inside the same stage family.
- A bare stage id such as `04` cannot coexist with `04a`, `04b`, or other same-family siblings.
- Non-pipeline helpers must live outside the numbered stage surface, typically under `tools/`.
- Stage-family siblings may run sequentially locally and may be parallelized in deployment when their direct dependencies are satisfied.
- Local smoke tests may still run all scripts sequentially for simplicity and debuggability.

### Directory names

- Use `L1-raw` and `L2-semantic` without leading dots.
- Avoid hidden directory naming for active pipeline outputs because the current project targets Windows development and public GitHub use.
- Use lowercase, hyphenated filenames for human-authored specs in `docs/specs/v12/`.

### Output philosophy

- `openwrt-condensed-docs/` is the stable output root for generated documentation.
- `docs/` is for maintainers and project documentation only.
- `tmp/` is scratch space and must never be treated as durable state.
- `openwrt-condensed-docs/` remains the internal staging root, but public surfaces expose only the `release-tree/` layout.

## Execution Contract

1. `01` prepares local source inputs and manifests.
2. `02a` is an independent wiki extractor and can run in parallel with `01` in hosted workflow execution.
3. `02b` through `02h` extract source-specific content into L1 and remain gated on `01` because they consume cloned repositories.
4. `03` normalizes L1 into L2 and promotes stable intermediates into the output tree.
5. `04` optionally enriches staged L2 files with AI summary metadata and performs its own AI-store preflight.
6. `05a` assembles internal references and release-tree bundled outputs, sharding oversized modules into smaller part files while preserving the stable bundled-reference filename.
7. `05b`, `05c`, and `05d` generate companion publication artifacts from the stabilized post-`03` snapshot.
8. `06` generates routing indexes after `05a` has produced the publishable reference assets.
9. `07` generates the internal and release-tree HTML landing pages, applies release overlays, and materializes `support-tree/`.
10. `08` validates the entire staged output tree, including the mandatory release-tree contract.

Current Option B hardening adds per-extractor status manifests, disables matrix fail-fast for repo-backed extractors, and emits extract plus pipeline summary artifacts for faster triage.

## Local-First Verification Model

- The required first-stage verification path is local and sequential.
- Deterministic fixture tests are the core protection against accidental regressions.
- Local smoke tests should isolate `WORKDIR` and `OUTDIR` so the repository is not corrupted during development.
- GitHub Actions remains a second-stage verification target after local proof, and it is now also the normal publication path for generated outputs.

## Remote Promotion Contract

- The `process` job builds generated artifacts into `staging/` (`OUTDIR`) and uploads that tree as `final-staging`.
- The `deploy` job promotes `final-staging` into `openwrt-condensed-docs/` with `rsync -a --delete`.
- Generated-output commits use the `docs: v12 auto-update YYYY-MM-DD` format and are written by the GitHub Actions bot only when the staged tree changed.
- The `deploy` job then mirrors `openwrt-condensed-docs/` into the source-repo `gh-pages` branch as an internal evidence surface and writes `.nojekyll` there so GitHub Pages serves the packaged tree, including `L1-raw` and `L2-semantic`, without Jekyll rewriting.

Deployment additionally publishes the validated `release-tree/` to external targets: `openwrt-docs4ai.github.io` (GitHub Pages) and the `corpus` release repository. The existing source-repo deploy behavior remains intact (locked decision D13).

## Active Documents

- `README.md`: short external overview.
- `DEVELOPMENT.md`: maintainer quick start and local workflow reference.
- `docs/ARCHITECTURE.md`: durable architecture and naming contract.
- `docs/specs/v12/`: active v12 specifications, current status, execution map, active bug log, and stabilization plan.
- `docs/specs/v12/release-tree-contract.md`: V5a public output contract.
- `docs/specs/v12/feature-flag-contract.md`: retired rollout history for the removed feature flag.

## Archive Policy

Documents under `docs/archive/v12/` remain useful as historical design context, but they do not control implementation. If an archived document conflicts with an active spec or with verified code behavior, the active spec wins.
