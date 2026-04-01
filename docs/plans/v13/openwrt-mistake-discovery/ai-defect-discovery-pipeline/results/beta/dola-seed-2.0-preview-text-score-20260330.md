# Dola Seed 2.0 Preview Text - Beta Batch Evaluation

**Date:** 2026-03-30
**Batch Evaluated:** 01b-batch-slice-beta.md
**Scenarios:** 02, 04, 08, 11, 12, 17
**Overall Score:** 3 / 6 (50%)

## Evaluation Methodology
Strict adherence to `03-golden-answers-key.md` falsification rules.

## Conversational Synthesis & Findings
Dola Seed 2.0 Preview performed at the mid-tier level on Beta. Its ucode network interface script was correct. The UCI modification was executed properly. However, Scenario 04 (LuCI JS dynamic form) fell into the legacy trap — it wrote a Lua-based CBI form using `m = Map(...)` syntax. Scenario 11 was accurate and complete. For Scenario 12, the model used `uloop_init()` and `uloop_run()` but omitted `ubus_add_uloop()` — necessary to integrate the ubus file descriptor into the event loop. Scenario 17 was an adequate description of ucode.

### New Truths Discovered
- None new.

### New Falsenesses Discovered
- None new.

## Scenario Breakdown
- **Scenario 02:** 1 (Pass) - Correct native ucode `import * as ubus from 'ubus'` with `ubus.conn()`.
- **Scenario 04:** 0 (Fail) - Used deprecated Lua CBI `m = Map(...)`. Taxonomy: `ERR_LEGACY_API`.
- **Scenario 08:** 1 (Pass) - Correct `cursor.set()`, `cursor.save()`, `cursor.commit()` sequence.
- **Scenario 11:** 1 (Pass) - Correct Makefile with `include $(TOPDIR)/rules.mk`, `DEPENDS:=+libubus`.
- **Scenario 12:** 0 (Fail) - Used `uloop_init()` and `uloop_run()` but omitted `ubus_add_uloop()`. Taxonomy: `ERR_MISSING_BOILERPLATE`.
- **Scenario 17:** 1 (Pass) - Correct description of ucode replacing Lua as lightweight scripting layer.
