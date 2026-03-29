# Dola Seed 2.0 Pro Text - Alpha Batch Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** 01a-batch-slice-alpha.md
**Raw Output File:** dola-seed-2.0-pro-text.txt
**Overall Score:** 1 / 6 (17%)

## Conversational Synthesis & Findings
Directionally competent on classic OpenWrt service and C patterns, but it still collapses into older shell and Lua-era habits on the modern surfaces the batch is testing.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - Missing mandatory `uci_load_validate`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 05:** 0 (Fail) - Uses Lua or templated LuCI instead of modern JavaScript view code with `rpc.declare` and `L.resolveDefault`. Taxonomy: `ERR_ERA_CONFUSION`.
* **Scenario 07:** 1 (Pass) - Correct `blob_buf`, `blobmsg_add_string()`, and `ubus_send_reply()` handler pattern.
* **Scenario 10:** 0 (Fail) - Omits `exit 0` and calls `/etc/init.d/system reload` from `uci-defaults`. Taxonomy: `ERR_BOUNDARY_VIOLATION`.
* **Scenario 13:** 0 (Fail) - Uses `jsonfilter` shell parsing instead of native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_NON_NATIVE_JSON`.
* **Scenario 16:** 0 (Fail) - Uses shell background jobs and streaming text utilities instead of ucode or `uloop`. Taxonomy: `ERR_SHELL_HACK`.
