# Minimax M2.5 20260328 0856am - Full Run Evaluation

**Date:** 2026-03-28
**Batch Evaluated:** Full 17-scenario run stored in alpha folder
**Raw Output File:** minimax-m2.5-20260328-0856am.md
**Overall Score:** 4 / 17 (24%)

## Conversational Synthesis & Findings
This file is broad but shallow. It covers all 17 scenarios, yet most failures come from reaching for generic Linux or OpenWrt-adjacent patterns instead of the repo's exact architectural contracts. Its strongest areas are plain ubus C reply handling, hotplug filtering, and `uloop` initialization.

## Scenario Breakdown
* **Scenario 01:** 0 (Fail) - SysV-style `start()` or `stop()` service without `USE_PROCD=1`. Taxonomy: `ERR_LINUX_HALLUCINATION`.
* **Scenario 02:** 0 (Fail) - Shell wrapper using `/sys/class/net`, `ip`, or `grep` instead of native ucode plus `ubus`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 03:** 1 (Pass) - Includes `libubus.h` and uses `ubus_add_object()`.
* **Scenario 04:** 0 (Fail) - Uses manual raw HTML form in legacy Lua LuCI. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 05:** 0 (Fail) - Uses legacy Lua or manual table rendering and misses `rpc.declare`, `L.resolveDefault`, and `E()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 06:** 0 (Fail) - Uses custom shell validation instead of `uci_load_validate`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 07:** 1 (Pass) - Proper `blob_buf`, `blobmsg_add_string()`, and `ubus_send_reply()` pattern.
* **Scenario 08:** 0 (Fail) - Uses UCI cursor but omits required `commit()`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
* **Scenario 09:** 1 (Pass) - Correct hotplug `$ACTION` and `$INTERFACE` gating.
* **Scenario 10:** 0 (Fail) - Uses `/etc/rc.d/` or `rc.local` marker-file fallback instead of proper `uci-defaults` flow. Taxonomy: `ERR_BOUNDARY_VIOLATION`.
* **Scenario 11:** 0 (Fail) - Uses deprecated `PKG_MD5SUM`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 12:** 1 (Pass) - Uses `uloop_init()`, `ubus_connect()`, `ubus_add_uloop()`, and `uloop_run()`.
* **Scenario 13:** 0 (Fail) - Uses `jsonfilter` and shell fallbacks instead of native ucode `fs.readfile()` plus `json()`. Taxonomy: `ERR_LEGACY_API`.
* **Scenario 14:** 0 (Fail) - Uses wrong or noncanonical LuCI menu JSON schema. Taxonomy: `ERR_NON_CANONICAL_FRONTEND`.
* **Scenario 15:** 0 (Fail) - Parses attributes manually with `blob_for_each_attr()` instead of `blobmsg_parse()` plus policy. Taxonomy: `ERR_NON_C_COMPLIANT`.
* **Scenario 16:** 0 (Fail) - Uses shell background jobs and FIFO or named-pipe alternatives instead of `uloop`. Taxonomy: `ERR_SHELL_HACK`.
* **Scenario 17:** 0 (Fail) - Misclassifies `ucode` conceptually. Taxonomy: `ERR_CONCEPTUAL_MISS`.
