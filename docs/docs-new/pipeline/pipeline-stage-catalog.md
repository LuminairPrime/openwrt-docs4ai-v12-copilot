# Pipeline Stage Catalog

**Version:** V13  
**Status:** Active  
**Source of truth for stage ordering:** [execution-map.md](../../specs/v12/execution-map.md)

---

## Overview

All numbered scripts live in `.github/scripts/`. Each script writes deterministic output to a specific layer directory. Letter suffixes within a stage family (e.g. `05a`, `05b`) are siblings with no ordering dependency between them.

---

## Stage Table

| Script | Stage | Family | I/O |
|--------|-------|--------|-----|
| `01-clone-repos.py` | 01 | Clone | **In:** `data/repo-manifest.json` **Out:** `tmp/repo-{module}/` |
| `02a-scrape-wiki.py` | 02a | L1 extractor (repo-independent) | **In:** OpenWrt wiki HTTP **Out:** `L1-raw/wiki/` |
| `02b-extract-ucode.py` | 02b | L1 extractor (clone-gated) | **In:** `tmp/repo-ucode/` **Out:** `L1-raw/ucode/` |
| `02c-extract-luci.py` | 02c | L1 extractor (clone-gated) | **In:** `tmp/repo-luci/` **Out:** `L1-raw/luci/` |
| `02d-extract-luci-examples.py` | 02d | L1 extractor (clone-gated) | **In:** `tmp/repo-luci/` **Out:** `L1-raw/luci-examples/` |
| `02e-extract-openwrt-core.py` | 02e | L1 extractor (clone-gated) | **In:** `tmp/repo-openwrt/` **Out:** `L1-raw/openwrt-core/` |
| `02f-extract-procd.py` | 02f | L1 extractor (clone-gated) | **In:** `tmp/repo-openwrt/` **Out:** `L1-raw/procd/` |
| `02g-extract-openwrt-hotplug.py` | 02g | L1 extractor (clone-gated) | **In:** `tmp/repo-openwrt/` **Out:** `L1-raw/openwrt-hotplug/` |
| `02h-extract-uci.py` | 02h | L1 extractor (clone-gated) | **In:** `tmp/repo-openwrt/` **Out:** `L1-raw/uci/` |
| `02i-ingest-cookbook.py` | 02i | L1 extractor (repo-independent) | **In:** `content/cookbook-source/` **Out:** `L1-raw/cookbook/` |
| `03-normalize-semantic.py` | 03 | L2 normalizer | **In:** `L1-raw/` **Out:** `L2-semantic/` |
| `04-generate-ai-summaries.py` | 04 | L2 enrichment (optional) | **In:** `L2-semantic/` (also reads/writes `data/base/` AI store) **Out:** `L2-semantic/` (writes routing annotations back) |
| `05a-assemble-references.py` | 05a | Assembler | **In:** `L2-semantic/` **Out:** `release-tree/{module}/bundled-reference.md`, `map.md`, `chunked-reference/` |
| `05b-generate-agents-and-readme.py` | 05b | Publication companion generator | **In:** `L2-semantic/`, `release-inputs/` **Out:** `release-tree/AGENTS.md`, `release-tree/README.md` |
| `05c-generate-ucode-ide-schemas.py` | 05c | IDE surface generator | **In:** `cross-link-registry.json` **Out:** `release-tree/ucode/types/ucode.d.ts` |
| `05d-generate-api-drift-changelog.py` | 05d | Telemetry | **In:** `cross-link-registry.json`, `data/base/signature-inventory.json` **Out:** `support-tree/telemetry/changelog.json` |
| `06-generate-llm-routing-indexes.py` | 06 | Router | **In:** `L2-semantic/` **Out:** `release-tree/llms.txt`, `release-tree/llms-full.txt`, `release-tree/{module}/llms.txt` |
| `07-generate-web-index.py` | 07 | Finalizer | **In:** `release-tree/`, `release-inputs/` **Out:** `release-tree/index.html` (plus support tree materialization) |
| `08-validate-output.py` | 08 | Validator / gatekeeper | **In:** `release-tree/, L2-semantic/` **Out:** `exit(1)` on hard failure; V6 stale-field warnings are soft |

---

## Execution Order

```
[01 clone-repos] ─┬─ (parallel) ─────────── [02a scrape-wiki]
                  │                           [02i ingest-cookbook]
                  │
                  └─ (after 01) ─────────── [02b extract-ucode]
                                             [02c extract-luci]
                                             [02d extract-luci-examples]
                                             [02e extract-openwrt-core]
                                             [02f extract-procd]
                                             [02g extract-openwrt-hotplug]
                                             [02h extract-uci]
                                                   │
                                                   ▼
                                            [03 normalize-semantic]
                                                   │
                                                   ▼
                                            [04 ai-summaries] (optional)
                                                   │
                                                   ▼
                            ┌──────────────────────┤
                        [05a]  [05b]  [05c]  [05d]  (parallel)
                            └──────────────────────┤
                                                   ▼
                                            [06 routing-indexes]
                                                   │
                                                   ▼
                                            [07 web-index]
                                                   │
                                                   ▼
                                            [08 validate-output]
```

---

## New in V13: `02i-ingest-cookbook.py`

Script: `.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py`

**Purpose:** Ingest hand-authored cookbook content from `content/cookbook-source/` into `L1-raw/cookbook/`, following the same `.meta.json` sidecar convention used by all other 02* extractors.

**Origin type:** `"authored"`  
**Input directory:** `content/cookbook-source/` (each `.md` file is one cookbook entry)  
**Output directory:** `L1-raw/cookbook/`

**Sidecar fields written:**
- `extractor`: `"02i-ingest-cookbook"`
- `origin_type`: `"authored"`
- `module`: `"cookbook"`
- `slug`: filename stem
- `source_url`: null (content is hand-authored; no upstream URL)
- `language`: `"en"`
- `fetch_status`: `"ok"`
- `extraction_timestamp`: ISO 8601 UTC
- `content_hash`: SHA-256 of file content

**Rerun safety:** Rerunning stage 02i is always safe; it clears and re-populates `L1-raw/cookbook/`.

---

## Stage Dependencies Matrix

| Stage | Requires | Blocks |
|-------|----------|--------|
| 01 | Nothing | 02b, 02c, 02d, 02e, 02f, 02g, 02h |
| 02a | Nothing (HTTP) | 03 |
| 02i | Nothing (local) | 03 |
| 02b–02h | 01 | 03 |
| 03 | All 02* complete | 04, 05a, 05b, 06 |
| 04 | 03 | 05a, 05b, 06 |
| 05a, 05b, 05c, 05d | 03 (+ 04 if AI) | 06, 07 |
| 06 | 05a, 05b, 05c, 05d | 07 |
| 07 | 06 | 08 |
| 08 | 07 | — |

---

## Independent Rerun Paths

If a single stage must be re-executed without running the full pipeline:

| Use case | Rerun |
|----------|-------|
| Wiki content changed | `02a` → `03` → `05a` → `06` → `07` → `08` |
| Cookbook content changed | `02i` → `03` → `05a` → `06` → `07` → `08` |
| Git source changed | `01` → `02b–02h` → `03` → `05a` → `06` → `07` → `08` |
| Routing text changes only | `06` → `07` → `08` |
| Web index only | `07` → `08` |
| Full validation gate | `08` only |
