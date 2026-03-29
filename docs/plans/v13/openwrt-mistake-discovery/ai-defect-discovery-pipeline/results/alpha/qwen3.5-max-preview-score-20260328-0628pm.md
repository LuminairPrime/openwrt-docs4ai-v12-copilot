# Qwen 3.5 Max Preview - Alpha Batch Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** 01a-batch-slice-alpha.md
**Raw Output File:** qwen3.5-max-preview.txt
**Overall Score:** 1 / 6 (17%)

## Conversational Synthesis & Findings
This file shows decent OpenWrt surface familiarity in the ubus C handler, but most answers fall back to older or generic patterns the current rubric explicitly rejects. The dominant failure mode is choosing plausible older OpenWrt patterns where the repo standard requires newer, stricter primitives.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - Missing mandatory `uci_load_validate`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 05:** 0 (Fail) - Uses legacy Lua or server-side LuCI view instead of modern JS with `rpc.declare`, `L.resolveDefault`, and `E()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 07:** 1 (Pass) - Uses `libubus`, `blob_buf`, `blobmsg_add_string()`, and `ubus_send_reply()`.
* **Scenario 10:** 0 (Fail) - Places script in `/etc/uci-defaults/` but omits explicit `exit 0`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 13:** 0 (Fail) - Uses shell `jsonfilter` instead of native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 16:** 0 (Fail) - Uses shell background jobs and `while read` pipelines instead of `uloop`-based async handling. Taxonomy: `ERR_SHELL_HACK`.
