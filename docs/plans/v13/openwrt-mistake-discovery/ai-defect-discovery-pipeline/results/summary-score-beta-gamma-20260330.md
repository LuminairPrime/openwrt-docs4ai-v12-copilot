# Cross-Batch Summary: Beta Batch Results

**Date:** 2026-03-30
**Note:** Gamma batch is excluded from this document. Gamma results were lost and are not being reconstituted.

This document summarizes findings from the Beta batch evaluation only, compiled for cross-batch reference at the results root.

## Beta Batch at a Glance

- **Scenarios:** 02 (ucode ubus), 04 (LuCI JS form), 08 (UCI modify), 11 (Makefile), 12 (C daemon), 17 (ucode definition)
- **Models Tested:** 10 unique models (11 score files including one full-run extraction)
- **Highest Score:** Claude Opus 4.6 Thinking — 5/6 (83%)
- **Lowest Score:** Spark — 2/6 (33%)

## Key Beta Findings

| Finding | Details |
| :--- | :--- |
| **`ubus_add_uloop()` invisible in training** | 60% of models omitted this call in C daemon. Universal pattern failure. |
| **LuCI JS barrier persists** | 20% pass rate on S04, consistent with alpha S05 (6%). The `L.ui` pattern is undertrained. |
| **UCI cursor widely known** | 100% pass on S08 — `cursor.set()/save()/commit()` is fully represented in training data. |
| **Makefile mostly known** | 90% pass on S11. Only `DEPENDS:=+libubus` caused issues in one case. |
| **ucode description improving** | 80% pass on S17 — basic ucode awareness is growing across models. |

## New Falsenesses from Beta

1. **Missing `ubus_add_uloop()`** — entering `uloop_run()` without prior `ubus_add_uloop()` creates a daemon that never processes ubus calls.
2. **Wrong C init order** — `ubus_connect()` must come after `uloop_init()`, not before.

## See Also

- Full per-model breakdown: `results/beta/beta-batch-scoring-summary-20260330.md`
- Consolidated alpha findings: `results/alpha/alpha-batch-scoring-summary-consolidated.md`
