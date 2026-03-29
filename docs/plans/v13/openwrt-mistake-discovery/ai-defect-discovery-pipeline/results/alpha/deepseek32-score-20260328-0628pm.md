# DeepSeek 32B - Alpha Batch Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** 01a-batch-slice-alpha.md
**Raw Output File:** deepseek32.txt
**Overall Score:** 1 / 6 (17%)

## Conversational Synthesis & Findings
This answer gets the ubus C reply shape right but drifts into generic Linux problem-solving elsewhere. The first-boot answer is the clearest miss because it reimplements state tracking instead of using the OpenWrt framework boundary.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - Missing mandatory `uci_load_validate`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 05:** 0 (Fail) - Uses Lua template or server-side LuCI instead of modern LuCI JS. Taxonomy: `ERR_ERA_CONFUSION`.
* **Scenario 07:** 1 (Pass) - Includes `struct blob_buf`, `blobmsg_add_string()`, and `ubus_send_reply()`.
* **Scenario 10:** 0 (Fail) - Creates redundant marker-file state and restarts a service from `uci-defaults`. Taxonomy: `ERR_STATE_MACHINE_VIOLATION`.
* **Scenario 13:** 0 (Fail) - Prefers `jq` or `awk` parsing instead of native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_LEGACY_PARSER`.
* **Scenario 16:** 0 (Fail) - Uses shell background jobs rather than ucode plus `uloop`. Taxonomy: `ERR_SHELL_HACK`.
