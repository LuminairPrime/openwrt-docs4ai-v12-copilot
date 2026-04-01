# AI Evaluation Pipeline - Alpha Batch Scoring Summary (Consolidated)

**Date:** 2026-03-28 – 2026-03-30
**Dataset:** 01a-batch-slice-alpha.md
**Scenarios Scored:** 01, 05, 07, 10, 13, 16
**Total Models Scored:** 16
**Evaluators:** Gemini Flash, Claude Opus 4.6 (Thinking), GPT-5.4
**Golden Key Reference:** 03-golden-answers-key.md

This consolidated summary reconciles results across all evaluator passes on the Alpha batch. Where evaluators disagreed, the highest-fidelity run (Claude Opus 4.6 Thinking at `0807am`) is treated as authoritative.

---

## Authoritative Performance Leaderboard (0807am Opus pass)

| Rank | Model | Score | % | Architectural Tier |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **GPT 5.2 High** | **4 / 6** | **67%** | **Elite.** Only model to correctly use modern LuCI JS `rpc.declare`. |
| 2 | Claude Opus 4.6 (Thinking) | 3 / 6 | 50% | Advanced. Flawless procd/C/uci-defaults. Failed LuCI JS and uCode. |
| 3 | Claude Sonnet 4.6 | 3 / 6 | 50% | Advanced. Most verbose, excellent C. Failed LuCI JS and uCode. |
| 4 | Gemini Flash Thinking | 3 / 6 | 50% | Standard. Solid basics. No uCode or LuCI JS awareness. |
| 5 | Gemini Pro | 3 / 6 | 50% | Standard. Mirrors Gemini Flash. |
| 6 | GLM-5 | 3 / 6 | 50% | Standard. Added unnecessary `rm -f`, saved by `exit 0`. |
| 7 | Hearth | 3 / 6 | 50% | Legacy-Aware. Consciously chose legacy Lua despite knowing JS exists. |
| 8 | Kimi k2.5 | 3 / 6 | 50% | Standard. Wrote CGI for S05 but correct procd/C/uci-defaults. |
| 9 | DeepSeek V3 32B | 2 / 6 | 33% | Lower-Mid. Created banned sentinel file in Scenario 10. |
| 10 | Dola Seed 2.0 Pro | 2 / 6 | 33% | Lower-Mid. Missing `exit 0` in Scenario 10. |
| 11 | Grok 4.20 | 2 / 6 | 33% | Lower-Mid. Missing `exit 0` in Scenario 10. |
| 12 | Minimax m2.7 | 2 / 6 | 33% | Lower-Mid. Missing `exit 0`, manual `rm -f` in Scenario 10. |
| 13 | Qwen 3.5 Max | 2 / 6 | 33% | Lower-Mid. Missing `exit 0` in Scenario 10. |
| 14 | Significant Otter | 1 / 6 | 17% | Fragmented. Fabricated C API signatures. Fabricated ubus methods. Missing `exit 0`. |
| 15 | Mimo v2 Pro | 1 / 6 | 17% | Fragmented. Used `json-c` double-wrap pattern. Sentinel file. |
| 16 | Nvidia Nemotron | 0 / 6 | 0% | **Failed.** SysVinit, PID files, fabricated APIs, no `uci-defaults` awareness. |

---

## Evaluator Cross-Reference Notes

### Gemini Flash Pass (0730am) — 15 models scored
The earlier Gemini Flash pass had slightly different rankings because it applied looser `uci-defaults` boundary rules before the `exit 0` contract was formally documented. Notable deltas from the authoritative Opus pass:
- Significant Otter ranked higher (3/6) because the LuCI JS scenario was marked as pass; later investigation found the `L.resolveDefault` call was absent.
- DeepSeek was marked 3/6; sentinel file Falseness was added to golden key after this pass.

### GPT-5.4 Rescore Pass (0628pm) — Alpha-only rescore
Performed after discovery that Alpha artifacts had been incorrectly copied across to other directories. This pass re-established scores with stricter enforcement of `uci_load_validate` in Scenario 01, dropping nearly all models that had previously passed that scenario via config_load alone. Aggregate: 19 passes / 94 failures across 113 scorable instances.

### Claude Opus 4.6 Thinking Pass (0807am) — **Authoritative**
The most rigorous pass. Applied all golden key updates from both earlier sessions. Full detailed per-scenario breakdowns exist in the individual `*-score-20260328-0807am.md` files.

---

## Per-Scenario Pass Rates (Authoritative)

| Scenario | Description | Pass Rate | Key Finding |
| :--- | :--- | :--- | :--- |
| **01** | Procd Daemon & Config | 15 / 16 (94%) | Near-universal. Only Nvidia Nemotron used SysVinit `start()`/`stop()`. |
| **05** | LuCI JS Live Status | 1 / 16 (6%) | **Near-total barrier.** Only GPT 5.2 used `rpc.declare`. |
| **07** | C ubus RPC Handler | 13 / 16 (81%) | 3 failures: Nemotron fabricated APIs, Mimo double-wrapped, Otter wrong signatures. |
| **10** | UCI Defaults First-Boot | 8 / 16 (50%) | Half missed `exit 0`. 2 used sentinel files. 1 used `/etc/rc.local`. |
| **13** | Native JSON Parsing | 0 / 16 (0%) | **Universal failure.** All models used `jsonfilter`, `jshn`, `jq`, or `awk`. |
| **16** | Async Parallel Ping | 0 / 16 (0%) | **Universal failure.** All models used shell `&` background jobs or FIFOs. |

---

## Critical Discoveries

1. **The uCode Knowledge Gap (CONFIRMED):** 0/16 models identified `ucode` as the correct standard for native JSON parsing (S13) or async parallel processing (S16). The largest single training data gap in the entire test matrix.

2. **The Modern LuCI JS Barrier:** 1/16 models (GPT 5.2) correctly used `rpc.declare`. 14/16 fell into the deprecated Lua `.htm` template trap. 1 wrote a standalone CGI script.

3. **The `exit 0` Trap:** 8/16 models correctly included `exit 0` in `uci-defaults`. The other 50% demonstrated: missing `exit 0` (5), sentinel files (2), or `/etc/rc.local` with `/tmp` lockfiles (1).

4. **Core IPC Proficiency:** 13/16 (81%) models correctly used `blobmsg_add_string` and `ubus_send_reply` for C-based RPC.

5. **procd Universality:** 15/16 (94%) models correctly identified `USE_PROCD=1`. Only Nvidia Nemotron used SysVinit-style `start()`/`stop()`.

---

## New Truths Added to Golden Key
- `jshn.sh` with `json_init`, `json_load`, `json_get_var` is valid at the shell tier (below `ucode`, above `jsonfilter`).
- `L.ready()` + modern LuCI JS runtime (`rpc.declare`, `E()`, `view.extend`) is the correct client-side entry point.

## New Falsenesses Added to Golden Key
- **FIFO-based parallel processing** — variant of banned Shell Hacks pattern.
- **Standalone CGI scripts** (`/www/cgi-bin/`) bypassing LuCI architecture.
- **`blobmsg_add_json_from_string()` double-wrap** — building JSON with `json-c` then injecting.
- **Fabricated ubus API functions** — `ubus_request_set_result()`, `ubus_add_workhandler()`.
- **PID file management** — SysVinit-era pattern replaced by procd.
- **`/tmp` lockfile for first-boot** — cleared every reboot; runs every boot.
- **Non-existent ubus methods** — `network.get_wireless_clients` is fabricated.
- **Self-deleting `uci-defaults` scripts** — manual `rm -f` shows misunderstanding of contract.
