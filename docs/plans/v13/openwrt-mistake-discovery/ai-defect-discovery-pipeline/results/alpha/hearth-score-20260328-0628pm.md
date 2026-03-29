# Hearth - Alpha Batch Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** 01a-batch-slice-alpha.md
**Raw Output File:** hearth.txt
**Overall Score:** 2 / 6 (33%)

## Conversational Synthesis & Findings
Hearth is one of the stronger Alpha entries on the C and first-boot basics, but it still falls back to older shell and Lua idioms where the key expects LuCI JS and native ucode or `uloop` patterns.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - Correct `procd` skeleton but omits mandatory `uci_load_validate`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 05:** 0 (Fail) - Uses legacy Lua LuCI template and manual HTML instead of LuCI JS view architecture with `rpc.declare`, `L.resolveDefault`, and `E('table')`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 07:** 1 (Pass) - Proper `blob_buf` reply path with `blobmsg_add_string()` and `ubus_send_reply()`.
* **Scenario 10:** 1 (Pass) - Correct `uci-defaults` placement, UCI mutation, commit, and explicit `exit 0`.
* **Scenario 13:** 0 (Fail) - Uses shell `jsonfilter` instead of native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 16:** 0 (Fail) - Uses shell background jobs and streaming text multiplexing instead of ucode plus `uloop`. Taxonomy: `ERR_SHELL_HACK`.
