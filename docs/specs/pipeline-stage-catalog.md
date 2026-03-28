# Pipeline Stage Catalog

**Version:** V13  
**Status:** Active

This document is the source of truth for stage ordering and stage-family ownership.

## Overview

All numbered scripts live in `.github/scripts/`. Whole numbers define stage boundaries. Letter suffixes such as `05a` and `05e` are sibling scripts inside the same stage family.

The hosted workflow is named `openwrt-docs4ai-pipeline`.

## Stage Table

| Script | Stage | Family | I/O summary |
| --- | --- | --- | --- |
| `01-clone-repos.py` | 01 | Clone | clones upstream repos into `WORKDIR/repo-*` |
| `02a-scrape-wiki.py` | 02a | L1 extractor | wiki HTTP -> `L1-raw/wiki/` |
| `02b-scrape-ucode.py` | 02b | L1 extractor | cloned ucode repo -> `L1-raw/ucode/` |
| `02c-scrape-jsdoc.py` | 02c | L1 extractor | cloned LuCI repo -> `L1-raw/luci/` |
| `02d-scrape-core-packages.py` | 02d | L1 extractor | cloned OpenWrt repo -> `L1-raw/openwrt-core/` |
| `02e-scrape-example-packages.py` | 02e | L1 extractor | cloned LuCI repo -> `L1-raw/luci-examples/` |
| `02f-scrape-procd-api.py` | 02f | L1 extractor | cloned OpenWrt repo -> `L1-raw/procd/` |
| `02g-scrape-uci-schemas.py` | 02g | L1 extractor | cloned OpenWrt repo -> `L1-raw/uci/` |
| `02h-scrape-hotplug-events.py` | 02h | L1 extractor | cloned OpenWrt repo -> `L1-raw/openwrt-hotplug/` |
| `02i-ingest-cookbook.py` | 02i | L1 extractor | `content/cookbook-source/` -> `L1-raw/cookbook/` |
| `03-normalize-semantic.py` | 03 | L2 normalizer | `L1-raw/` -> `L2-semantic/` and cross-link state |
| `04-generate-ai-summaries.py` | 04 | L2 enrichment | optionally enriches L2 from the AI store |
| `05a-assemble-references.py` | 05a | Assembler | builds module reference surfaces in `release-tree/` |
| `05b-generate-agents-and-readme.py` | 05b | Publication companion generator | builds root `AGENTS.md` and generated `README.md` |
| `05c-generate-ucode-ide-schemas.py` | 05c | IDE surface generator | emits `release-tree/ucode/types/ucode.d.ts` |
| `05d-generate-api-drift-changelog.py` | 05d | Telemetry | emits telemetry under `support-tree/telemetry/` |
| `05e-generate-luci-dts.py` | 05e | IDE surface generator | emits `release-tree/luci/types/luci-env.d.ts` |
| `06-generate-llm-routing-indexes.py` | 06 | Router | builds root and module `llms.txt` surfaces |
| `07-generate-web-index.py` | 07 | Finalizer | applies overlays, emits `index.html`, materializes `support-tree/` |
| `08-validate-output.py` | 08 | Validator | validates the staged output tree |

## Execution Order

```text
[01 clone-repos] ─┬─ [02a scrape-wiki]
                  ├─ [02i ingest-cookbook]
                  └─ [02b-02h repo-backed extractors]
                              ↓
                       [03 normalize-semantic]
                              ↓
                    [04 ai-summaries] (optional)
                              ↓
               [05a] [05b] [05c] [05d] [05e]
                              ↓
                   [06 routing-indexes]
                              ↓
                        [07 finalizer]
                              ↓
                        [08 validator]
```

## Hosted Workflow Notes

- `push` runs on `main`.
- `schedule` runs monthly at `13:00 UTC` on the first day of the month.
- `workflow_dispatch` exposes `skip_wiki`, `skip_buildroot`, `skip_ai`, and `max_ai_files`.
- The hosted workflow does not expose a `start_stage` input. Partial reruns are a local maintenance practice, not a hosted workflow contract.

## Stage Dependency Matrix

| Stage | Requires | Typical downstream blockers |
| --- | --- | --- |
| `01` | nothing | `02b`-`02h`, `05e` |
| `02a` | nothing | `03` |
| `02i` | nothing | `03` |
| `02b`-`02h` | `01` | `03` |
| `03` | all required `02*` inputs | `04`, all `05*`, `06`, `08` |
| `04` | `03` | richer outputs for `05a` and `06` when AI is enabled |
| `05a` | `03` | `06`, `08` |
| `05b` | `03` | `06`, `07`, `08` |
| `05c` | `03` | `06`, `08` |
| `05d` | `03` | `08` |
| `05e` | `01` plus active output context | `06`, `08` |
| `06` | `05a`, `05b`, `05c`, `05e` | `07`, `08` |
| `07` | `06` | `08` |
| `08` | staged output tree | none |

## Local Rerun Paths

These are the minimal local rerun paths when you already have the prerequisite state on disk.

| Use case | Minimal rerun path |
| --- | --- |
| Wiki-only source change | `02a -> 03 -> 05a -> 05b -> 06 -> 07 -> 08` |
| Cookbook source change | `02i -> 03 -> 05a -> 05b -> 06 -> 07 -> 08` |
| Repo-backed extractor change | `01 -> affected 02* -> 03 -> 05a-05e -> 06 -> 07 -> 08` |
| Routing text or grouping change | `06 -> 07 -> 08` |
| Root README or AGENTS generator change | `05b -> 06 -> 07 -> 08` |
| Ucode type-generation change | `05c -> 06 -> 07 -> 08` |
| LuCI type-generation change | `05e -> 06 -> 07 -> 08` |
| Overlay-only local change | `07 -> 08` |
| Validation-only check | `08` |

For cookbook-only local authoring work, do not assume that rerunning `03 -> 05a -> 05b -> 06 -> 07` in a dirty workspace is isolated to the cookbook module. If unrelated generated module trees under `staging/`, `release-tree/`, or `support-tree/` drift or disappear, restore the non-cookbook generated paths from `HEAD`, keep the cookbook slice, then rerun `06 -> 07 -> 08`.

## Generate → Validate Cycle

Direct local script execution generates into `staging/` (the default `OUTDIR`, gitignored). Tests read from `staging/` to validate fresh pipeline output. The source repository does not track generated output.

```powershell
# Generate into staging (default OUTDIR=staging)
python .github/scripts/openwrt-docs4ai-03-normalize-semantic.py
python .github/scripts/openwrt-docs4ai-05a-assemble-references.py
python .github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py
python .github/scripts/openwrt-docs4ai-07-generate-web-index.py
python .github/scripts/openwrt-docs4ai-08-validate-output.py
```

Local smoke runners use isolated temp directories and never write to `staging/`.
