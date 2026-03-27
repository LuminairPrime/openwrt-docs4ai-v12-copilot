# Script Dependency Map

## Purpose

This document summarizes what each pipeline script reads, what it writes, and where it sits in the execution graph. Use [pipeline-stage-catalog.md](pipeline-stage-catalog.md) for the ordered stage catalog and rerun sequences. Use this file when you need the per-script read/write contract.

## Pipeline Overview

```text
01-clone-repos
  ├── 02b-02h repo-backed extractors
  ├── 02a scrape-wiki
  └── 02i ingest-cookbook
        ↓
03-normalize-semantic
        ↓
04-generate-ai-summaries (optional)
        ↓
  05a  05b  05c  05d  05e
        ↓
06-generate-llm-routing-indexes
        ↓
07-generate-web-index
        ↓
08-validate-output
```

## Per-Script Contract

| Script | Phase | Reads | Writes | Depends on | External tools | AI data |
| --- | --- | --- | --- | --- | --- | --- |
| `01-clone-repos.py` | L0 acquisition | upstream git repositories | `WORKDIR/repo-*`, `repo-manifest.json` | none | none | none |
| `02a-scrape-wiki.py` | L1 extraction | OpenWrt wiki HTTP | `WORKDIR/L1-raw/wiki/` | none | `pandoc` (apt/system) | none |
| `02b-scrape-ucode.py` | L1 extraction | `WORKDIR/repo-ucode/` | `WORKDIR/L1-raw/ucode/` | `01` | none | none |
| `02c-scrape-jsdoc.py` | L1 extraction | `WORKDIR/repo-luci/` | `WORKDIR/L1-raw/luci/` | `01` | `jsdoc-to-markdown` (npm global) | none |
| `02d-scrape-core-packages.py` | L1 extraction | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/openwrt-core/` | `01` | none | none |
| `02e-scrape-example-packages.py` | L1 extraction | `WORKDIR/repo-luci/` | `WORKDIR/L1-raw/luci-examples/` | `01` | none | none |
| `02f-scrape-procd-api.py` | L1 extraction | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/procd/` | `01` | none | none |
| `02g-scrape-uci-schemas.py` | L1 extraction | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/uci/` | `01` | none | none |
| `02h-scrape-hotplug-events.py` | L1 extraction | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/openwrt-hotplug/` | `01` | none | none |
| `02i-ingest-cookbook.py` | L1 extraction | `content/cookbook-source/` | `WORKDIR/L1-raw/cookbook/` | none | none | none |
| `03-normalize-semantic.py` | L2 normalization | all `WORKDIR/L1-raw/**` content | `OUTDIR/L1-raw/`, `OUTDIR/L2-semantic/`, `cross-link-registry.json` | all `02*` stages | none | none |
| `04-generate-ai-summaries.py` | L2 enrichment | `OUTDIR/L2-semantic/`, `data/base/`, `data/override/`, legacy cache | updated `OUTDIR/L2-semantic/`, optional writes to `data/base/` | `03` | none | reads and writes AI store |
| `05a-assemble-references.py` | release assembly | `OUTDIR/L2-semantic/` | module `map.md`, `bundled-reference.md`, `chunked-reference/` | `03`, optionally `04` | none | consumes AI-enriched L2 if present |
| `05b-generate-agents-and-readme.py` | companion generation | `OUTDIR/L2-semantic/`, `release-inputs/` | root `AGENTS.md`, root generated `README.md` | `03` | none | none |
| `05c-generate-ucode-ide-schemas.py` | IDE surface generation | `cross-link-registry.json` | `release-tree/ucode/types/ucode.d.ts` | `03` | none | none |
| `05d-generate-api-drift-changelog.py` | telemetry | `cross-link-registry.json`, baseline signature data | `support-tree/telemetry/` outputs | `03` | none | none |
| `05e-generate-luci-dts.py` | IDE surface generation | `WORKDIR/repo-luci/` | `release-tree/luci/types/luci-env.d.ts` | `01` and `03` output context | none | none |
| `06-generate-llm-routing-indexes.py` | routing | assembled release-tree surfaces and L2 metadata | root and module `llms.txt` files | `05a`, `05b`, `05c`, `05e` | none | consumes AI-enriched L2 if present |
| `07-generate-web-index.py` | finalization | `release-tree/`, `release-inputs/` | `release-tree/index.html`, applied overlays, `support-tree/` materialization | `06` | none | indirect only |
| `08-validate-output.py` | validation | staged output tree | validation status and warnings | `07` and the prior generated outputs | none | validates AI-related fields when present |

## AI Store Flow

The AI store affects the pipeline at one numbered stage and several downstream consumers.

1. `04` reads `data/base/` and `data/override/`, optionally generates missing summaries, and writes AI fields into L2 frontmatter.
2. `05a` can use the enriched L2 metadata when building reference surfaces.
3. `06` can use the enriched metadata when choosing routing summaries.
4. `08` validates the resulting output and warns on stale field names or bad payloads.

Local scratch-first review, promotion, and cleanup are intentionally handled outside the numbered pipeline in `tools/manage_ai_store.py`.

## Notes

- `02a` and `02i` are the only extraction stages that do not require cloned repos.
- `05d` is part of the same stage family as the other `05*` scripts, but it does not feed routing generation directly.
- `05e` is now part of the active pipeline surface and must be reflected in docs, workflow reasoning, and validation expectations.