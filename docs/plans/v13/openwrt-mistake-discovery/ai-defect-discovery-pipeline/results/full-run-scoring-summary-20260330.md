# Full Run Scoring Summary

**Date:** 2026-03-30
**Scope:** All evaluated scenarios across Alpha + Beta batches
**Note:** Gamma batch results are excluded (lost, not being reconstituted).

This document aggregates scoring results from full-run model files (models that answered all 17 scenarios at once) alongside the Alpha and Beta batch slices.

---

## Full-Run Files Evaluated

| Model | File | Score | % | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Mimo v2 Pro | mimo-v2-pro-20260328-0901am.md | 11 / 17 | 65% | Strongest full-run. Broad competence. Narrow misses on `uci_load_validate`, `L.ui`, `uci-defaults` service boundary, ucode async I/O events. |
| Arcee AI Trinity Large | arcee-ai-trinity-large-preview-free-... | See score file | — | See `arcee-ai-trinity-large-preview-free-...-score-20260328-0554pm.md` |
| Minimax m2.5 | minimax-m2.5-20260328-0856am.md | 4 / 17 | 24% | Scored during Alpha session. Strong on core procd, failed LuCI, ucode, async. |
| Nvidia Nemotron | nemotron-3-super-120b-a12b... | See score file | — | Very low full-run score; SysV patterns throughout. |
| StepFlash | stepflash-20260328-0856am.md | See score file | — | See dedicated score file. |

---

## Cross-Batch Aggregate Statistics

### Alpha Batch (6 scenarios × 16 models = 96 scorable instances)
- **Scenarios:** 01, 05, 07, 10, 13, 16
- **Top score:** GPT 5.2 High — 4/6 (67%)
- **Batch average:** ~2.2 / 6 (37%)
- **Universal zeros:** S13 (0/16), S16 (0/16)
- **Near-universal pass:** S01 (15/16)

### Beta Batch (6 scenarios × 10 models = 60 scorable instances)
- **Scenarios:** 02, 04, 08, 11, 12, 17
- **Top score:** Claude Opus 4.6 Thinking — 5/6 (83%)
- **Batch average:** ~3.2 / 6 (53%)
- **Universal pass:** S08 (10/10)
- **Lowest pass rate:** S04 (2/10 = 20%)

---

## Cross-Batch Hardest Scenarios

| Rank | Scenario | Description | Batch | Pass Rate | Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **S13** | Native JSON Parsing | Alpha | **0%** | No model knew `ucode` `fs.readfile()` + `json()`. All used shell wrappers. |
| 2 | **S16** | Async Parallel Ping | Alpha | **0%** | No model knew `uloop` async + `uloop.ULOOP_READ`. All used shell `&`. |
| 3 | **S05** | LuCI JS Live Status | Alpha | **6%** | Only GPT 5.2 used `rpc.declare`. Legacy Lua swept the field. |
| 4 | **S04** | LuCI JS Dynamic Form | Beta | **20%** | `L.ui` + `widgets.NetworkSelect` widely absent. Most used Lua CBI or raw HTML. |
| 5 | **S12** | C Daemon Skeleton | Beta | **40%** | `ubus_add_uloop()` universally unknown or skipped. |

---

## Cross-Batch Model Performance (Alpha + Beta combined, where model appeared in both)

| Model | Alpha | Beta | Combined | Tier |
| :--- | :--- | :--- | :--- | :--- |
| Claude Opus 4.6 (Thinking) | 3/6 | 5/6 | 8/12 (67%) | **Elite** |
| Claude Sonnet 4.6 | 3/6 | 4/6 | 7/12 (58%) | Advanced |
| GPT 5.2 High | 4/6 | N/A | — | Elite (Alpha only) |
| Minimax m2.7 | 2/6 | 3/6 | 5/12 (42%) | Standard |
| Mimo v2 Pro | 1/6 | 3/6 | 4/12 (33%) | Fragmented |
| Qwen 3.5 Max Preview | 2/6 | 3/6 | 5/12 (42%) | Standard |
| Dola Seed 2.0 | 2/6 | 3/6 | 5/12 (42%) | Standard |
| GLM-5 | 3/6 | 3/6 | 6/12 (50%) | Standard |
| Hearth | 3/6 | 3/6 | 6/12 (50%) | Legacy-Aware |
| Nvidia Nemotron | 0/6 | N/A | — | Failed |

---

## Documentation Priority Actions

Based on the 0% and near-0% scenario pass rates, the following documentation is confirmed P0-priority for the openwrt-docs4ai project:

| Priority | Topic | Evidence |
| :--- | :--- | :--- |
| **P0** | `uci_load_validate` complete cookbook page | 0% pass if omitted in S01; missing `ubus_add_uloop` variant |
| **P0** | Modern LuCI JS forms with `L.ui` / `widgets.NetworkSelect` | S04 and S05: combined <10% pass rate |
| **P1** | C ubus/libubox daemon skeleton w/ correct init order | S12: 40% pass; `ubus_add_uloop()` gap |
| **P1** | ucode async patterns: `uloop.handle()` + `ULOOP_READ` | S16: 0% pass; event flags universally absent |
