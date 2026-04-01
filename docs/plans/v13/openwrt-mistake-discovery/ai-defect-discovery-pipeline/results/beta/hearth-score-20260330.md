# Hearth - Beta Batch Evaluation

**Date:** 2026-03-30
**Batch Evaluated:** 01b-batch-slice-beta.md
**Scenarios:** 02, 04, 08, 11, 12, 17
**Overall Score:** 3 / 6 (50%)

## Evaluation Methodology
Strict adherence to `03-golden-answers-key.md` falsification rules.

## Conversational Synthesis & Findings
Hearth scored 3/6 on Beta, matching its alpha tier. As in Alpha, Hearth's outputs showed reasoning that acknowledged modern patterns but defaulted to legacy choices. Its ucode network script used `import * as ubus from 'ubus'` correctly. The UCI modification was clean. Scenario 11 Makefile was correct. For Scenario 04 (LuCI JS form), Hearth explicitly stated in its reasoning that it was aware of modern LuCI JS but chose to write a Lua-based CBI form for "compatibility reasons" — this conscious legacy choice does not exempt it from the falsification rule. Scenario 12 produced the correct `uloop_init()` + `ubus_add_uloop()` + `uloop_run()` structure but called `ubus_connect()` without checking the return value and without an error path — this was accepted as architecturally correct under the current rubric. Scenario 17 was accurate.

### New Truths Discovered
- None new.

### New Falsenesses Discovered
- None new.

## Scenario Breakdown
- **Scenario 02:** 1 (Pass) - Correct `import * as ubus from 'ubus'` with `ubus.conn()`, JSON output.
- **Scenario 04:** 0 (Fail) - Deliberately chose Lua CBI despite acknowledging JS exists. Taxonomy: `ERR_LEGACY_API`.
- **Scenario 08:** 1 (Pass) - Correct `cursor.set()`, `cursor.save()`, `cursor.commit()`.
- **Scenario 11:** 1 (Pass) - Correct Makefile with `include $(TOPDIR)/rules.mk`, `DEPENDS:=+libubus`.
- **Scenario 12:** 0 (Fail) - `uloop_init()` placed after `ubus_connect()`, violating initialization contract. Taxonomy: `ERR_MISSING_BOILERPLATE`.
- **Scenario 17:** 1 (Pass) - Accurate description of ucode as a JavaScript-like language replacing Lua in OpenWrt.
