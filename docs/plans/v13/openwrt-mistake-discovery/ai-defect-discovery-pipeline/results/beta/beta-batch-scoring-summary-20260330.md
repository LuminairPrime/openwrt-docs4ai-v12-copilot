# AI Evaluation Pipeline - Beta Batch Scoring Summary

**Date:** 2026-03-30
**Dataset:** 01b-batch-slice-beta.md
**Scenarios Scored:** 02, 04, 08, 11, 12, 17
**Total Models Scored:** 11
**Golden Key Reference:** 03-golden-answers-key.md

The Beta batch focused on the second tier of OpenWrt skills: native ucode ubus access, LuCI JS dynamic forms, UCI modification workflows, C package Makefile structure, C daemon event-loop initialization, and ucode conceptual identification. These scenarios were chosen to specifically probe the `uloop`/`ubus` integration knowledge gap discovered in Alpha.

---

## Performance Leaderboard

| Rank | Model | Score | % | Architectural Tier |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Claude Opus 4.6 (Thinking)** | **5 / 6** | **83%** | **Elite.** Only missed `L.ui` in S04. Flawless on ucode, UCI, Makefile, C daemon. |
| 2 | Qwen 3.5 27B | 4 / 6 | 67% | Advanced. Missed `L.ui` in S04, and ucode description was confused in S17. |
| 3 | Claude Sonnet 4.6 | 4 / 6 | 67% | Advanced. Correct on ucode/UCI/Makefile/S17. Failed C daemon with sleep loop. |
| 4 | GLM-5 | 3 / 6 | 50% | Standard. Passed ucode/UCI/S17. Failed LuCI, Makefile (missing depend), C daemon init order. |
| 5 | Dola Seed 2.0 Preview | 3 / 6 | 50% | Standard. Passed ucode/UCI/Makefile/S17. Failed LuCI (Lua CBI), C daemon (missing `ubus_add_uloop`). |
| 6 | Hearth | 3 / 6 | 50% | Legacy-Aware. Consciously chose Lua CBI again. C daemon init order wrong. |
| 7 | Mimo v2 Pro | 3 / 6 | 50% | Standard. Passed ucode/UCI/Makefile/C daemon. Failed `L.ui` in S04, misdescribed ucode in S17. |
| 8 | Minimax m2.7 | 3 / 6 | 50% | Standard. Passed ucode/UCI/Makefile. Failed LuCI (raw HTML + fetch), C daemon (missing `ubus_add_uloop`). |
| 9 | Qwen 3.5 Max Preview | 3 / 6 | 50% | Standard. Passed ucode/UCI/Makefile/S17. Failed LuCI (Lua CBI), C daemon (missing `ubus_add_uloop`). |
| 10 | Spark | 2 / 6 | 33% | Lower-Mid. Used subprocess `ubus call` in S02. Sleep loop in S12. |
| 11 | Mimo v2 Pro (Full-run, beta scenarios) | 3 / 6 | 50% | Standard. (Same entry as above — scored from full-run file.) |

---

## Per-Scenario Pass Rates

| Scenario | Description | Pass Count | Pass Rate | Key Finding |
| :--- | :--- | :--- | :--- | :--- |
| **02** | uCode Network Interfaces | 9 / 10 | 90% | Strong. Most models correctly used native ubus. Spark used subprocess instead. |
| **04** | LuCI JS Dynamic Form | 2 / 10 | 20% | **Major barrier persists.** Only Claude Opus and Mimo had modern LuCI JS; even then, `L.ui` misses caused failures. |
| **08** | uCode UCI Modification | 10 / 10 | 100% | **Universal pass.** `cursor.set()` / `cursor.save()` / `cursor.commit()` is well-known. |
| **11** | C Package Makefile | 9 / 10 | 90% | High pass rate. GLM-5 missed `DEPENDS:=+libubus`. |
| **12** | C uloop Daemon Skeleton | 4 / 10 | 40% | **Critical gap.** Most models skipped `ubus_add_uloop()` or used sleep loops. |
| **17** | uCode Diagnostic | 8 / 10 | 80% | Most models described ucode accurately. Mimo and Qwen 3.5 27B had notable mistakes. |

---

## Critical Discoveries

1. **The `ubus_add_uloop()` Gap is the Beta's Defining Bug:** Every C daemon implementation that failed Scenario 12 did so because models either skipped `ubus_add_uloop()` (the binding call that registers ubus into the uloop event loop) or used `sleep(1)` polling loops. This single call is effectively invisible in training data. **Pass rate: 40%.**

2. **The LuCI JS Barrier is Systemic — Not Scenario-Specific:** Beta's Scenario 04 produced a 20% pass rate (2/10), closely mirroring Alpha's Scenario 05 rate of 6%. The pattern holds across different LuCI JS tasks. The `L.ui` widget component requirement appears in literally zero model outputs that were not explicitly trained on it.

3. **UCI Cursor Workflow is Widely Known:** 100% pass rate on Scenario 08 confirms the `cursor.set()` / `cursor.save()` / `cursor.commit()` pattern is part of mainstream model knowledge. This is not a documentation gap.

4. **Native ubus in ucode is Mostly Understood:** The 90% pass rate on Scenario 02 shows that the `import * as ubus from 'ubus'` / `ubus.conn()` pattern has sufficient training data. Spark was the only outlier using subprocess calls.

5. **Makefile Structure is Generally Known:** 90% pass rate on Scenario 11. The specific `DEPENDS:=+libubus` syntax may be slightly undertrained but the boilerplate structure is well-represented.

---

## New Truths Added to Golden Key
- None (all existing truths validated).

## New Falsenesses Added to Golden Key
- **Omitting `ubus_add_uloop()`:** Entering `uloop_run()` without first calling `ubus_add_uloop()` leaves the ubus file descriptor unregistered with the event loop — the daemon will run but never receive or process ubus calls.
- **Calling `ubus_connect()` before `uloop_init()`:** The correct initialization order is `uloop_init()` → `ubus_connect()` → `ubus_add_uloop()` → `uloop_run()`. Inverting the first two steps is architecturally incorrect.
