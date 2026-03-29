# Minimax M2.7 - Alpha Batch Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** 01a-batch-slice-alpha.md
**Raw Output File:** minimax-m2.7.txt
**Overall Score:** 0 / 6 (0%)

## Conversational Synthesis & Findings
This is the most generically Linux answer in the Alpha set. It invents infrastructure around OpenWrt instead of using OpenWrt's native boundaries, and its C answer also hallucinates non-existent ubus APIs.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - Uses classic manual init script and PID-file management instead of `procd`, and omits `uci_load_validate`. Taxonomy: `ERR_LINUX_HALLUCINATION`.
* **Scenario 05:** 0 (Fail) - Uses raw HTML plus `XMLHttpRequest` to a guessed `/ubus` endpoint. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 07:** 0 (Fail) - Uses raw JSON strings plus fabricated APIs such as `ubus_request_set_result()` or `ubus_add_workhandler()`. Taxonomy: `ERR_NON_C_COMPLIANT`.
* **Scenario 10:** 0 (Fail) - Uses boot or init flow with sentinel lockfiles instead of the `uci-defaults` state machine. Taxonomy: `ERR_STATE_MACHINE_VIOLATION`.
* **Scenario 13:** 0 (Fail) - Uses shell `jsonfilter` rather than native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 16:** 0 (Fail) - Uses shell background jobs and `stdbuf` tricks instead of native ucode async multiplexing. Taxonomy: `ERR_SHELL_HACK`.
