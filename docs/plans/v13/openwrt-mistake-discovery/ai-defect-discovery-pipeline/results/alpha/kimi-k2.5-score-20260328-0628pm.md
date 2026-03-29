# Kimi K2.5 - Alpha Batch Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** 01a-batch-slice-alpha.md
**Raw Output File:** kimi-k2.5.txt
**Overall Score:** 1 / 6 (17%)

## Conversational Synthesis & Findings
Kimi gets only the first-boot boundary cleanly right. Everywhere else it collapses toward generic Linux and web patterns: CGI instead of LuCI JS, shell concurrency instead of `uloop`, and non-idiomatic C ubus reply construction.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - Uses `USE_PROCD=1` but still misses required `uci_load_validate`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 05:** 0 (Fail) - Bypasses LuCI with a CGI shell script under `/www/cgi-bin/`. Taxonomy: `ERR_LINUX_HALLUCINATION`.
* **Scenario 07:** 0 (Fail) - Builds JSON with `json-c` and feeds it through `blobmsg_add_json_from_string()`. Taxonomy: `ERR_NON_C_COMPLIANT`.
* **Scenario 10:** 1 (Pass) - Correct `uci-defaults` boundary, UCI commit, and `exit 0`.
* **Scenario 13:** 0 (Fail) - Uses shell JSON extraction instead of native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 16:** 0 (Fail) - Uses shell ampersand jobs and loops instead of native async ucode. Taxonomy: `ERR_SHELL_HACK`.
