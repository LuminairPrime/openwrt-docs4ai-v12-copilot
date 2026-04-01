# Spark - Beta Batch Evaluation

**Date:** 2026-03-30
**Batch Evaluated:** 01b-batch-slice-beta.md
**Scenarios:** 02, 04, 08, 11, 12, 17
**Overall Score:** 2 / 6 (33%)

## Evaluation Methodology
Strict adherence to `03-golden-answers-key.md` falsification rules.

## Conversational Synthesis & Findings
Spark scored 2/6 on Beta, placing it in the lower-mid tier. The ucode network script used `import * as ubus from 'ubus'` correctly but employed `ubus call` subprocess calls rather than the native `ubus.conn()` API — this counts as using a shell wrapper where native ucode access was available, a General Falseness. The LuCI form was Lua CBI. The UCI modification was correct. The Makefile was complete. The C daemon used a `while(1) { sleep(1); }` loop. Scenario 17 was accurate.

### New Truths Discovered
- None new.

### New Falsenesses Discovered
- None new.

## Scenario Breakdown
- **Scenario 02:** 0 (Fail) - Used `ubus call` subprocess instead of native `ubus.conn()`. Taxonomy: `ERR_LEGACY_API`.
- **Scenario 04:** 0 (Fail) - Lua CBI `m = Map(...)`. Taxonomy: `ERR_LEGACY_API`.
- **Scenario 08:** 1 (Pass) - Correct `cursor.set()`, `cursor.save()`, `cursor.commit()`.
- **Scenario 11:** 1 (Pass) - Correct Makefile with `DEPENDS:=+libubus`.
- **Scenario 12:** 0 (Fail) - `while(1) { sleep(1); }` polling loop instead of `uloop_run()`. Taxonomy: `ERR_LEGACY_API`.
- **Scenario 17:** 1 (Pass) - Accurate description of ucode as modern OpenWrt scripting language.
