# Minimax m2.7 - Beta Batch Evaluation

**Date:** 2026-03-30
**Batch Evaluated:** 01b-batch-slice-beta.md
**Scenarios:** 02, 04, 08, 11, 12, 17
**Overall Score:** 3 / 6 (50%)

## Evaluation Methodology
Strict adherence to `03-golden-answers-key.md` falsification rules.

## Conversational Synthesis & Findings
Minimax m2.7 achieved 3/6 on Beta, consistent with its Alpha performance. It correctly handled the ucode network interfaces scenario (S02), UCI modification (S08), and C Makefile (S11). Scenario 04 (LuCI JS form) used raw HTML `<form>` elements and a custom `fetch()` call to a non-existent REST endpoint rather than the `rpc.declare` / `widgets.NetworkSelect` architecture — a clear double Falseness. The C daemon (S12) correctly entered `uloop_run()` but jumped there without `ubus_add_uloop()`, leaving the ubus connection unregistered with the event loop. Scenario 17 was accurate.

### New Truths Discovered
- None new.

### New Falsenesses Discovered
- None new.

## Scenario Breakdown
- **Scenario 02:** 1 (Pass) - Correct `import * as ubus from 'ubus'`, `ubus.conn()`, JSON output.
- **Scenario 04:** 0 (Fail) - Raw `<form>` HTML with `fetch()` to custom REST endpoint. Taxonomy: `ERR_LEGACY_API`.
- **Scenario 08:** 1 (Pass) - Correct `cursor.set()`, `cursor.save()`, `cursor.commit()`.
- **Scenario 11:** 1 (Pass) - Correct `include $(TOPDIR)/rules.mk`, `DEPENDS:=+libubus`.
- **Scenario 12:** 0 (Fail) - Missing `ubus_add_uloop()` before `uloop_run()`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
- **Scenario 17:** 1 (Pass) - Accurate description of ucode as modern lightweight scripting layer.
