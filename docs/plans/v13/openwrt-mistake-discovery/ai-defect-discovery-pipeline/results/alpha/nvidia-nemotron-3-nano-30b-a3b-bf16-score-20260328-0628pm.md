# Nvidia Nemotron 3 Nano 30B A3B BF16 - Alpha Batch Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** 01a-batch-slice-alpha.md
**Raw Output File:** nvidia-nemotron-3-nano-30b-a3b-bf16.txt
**Overall Score:** 0 / 6 (0%)

## Conversational Synthesis & Findings
The file understands some OpenWrt vocabulary, but not the current implementation contract. It repeatedly answers with near-miss patterns that sound embedded-friendly while still missing the mandatory OpenWrt-native primitives.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - Uses manual S-style init plus PID files instead of `procd`, and omits `uci_load_validate`. Taxonomy: `ERR_LINUX_HALLUCINATION`.
* **Scenario 05:** 0 (Fail) - Uses raw HTML and ad hoc `/ubus` HTTP access instead of LuCI JS runtime helpers. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 07:** 0 (Fail) - Uses raw JSON replies plus fabricated ubus request or registration APIs. Taxonomy: `ERR_NON_C_COMPLIANT`.
* **Scenario 10:** 0 (Fail) - Manually deletes itself instead of relying on the `exit 0` deletion contract. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 13:** 0 (Fail) - Uses shell `jshn` instead of native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 16:** 0 (Fail) - Uses shell background pipelines instead of native ucode `fs.popen` plus `uloop.handle`. Taxonomy: `ERR_SHELL_HACK`.
