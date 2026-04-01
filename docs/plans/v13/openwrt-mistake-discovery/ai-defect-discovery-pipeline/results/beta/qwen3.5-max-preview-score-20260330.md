# Qwen 3.5 Max Preview - Beta Batch Evaluation

**Date:** 2026-03-30
**Batch Evaluated:** 01b-batch-slice-beta.md
**Scenarios:** 02, 04, 08, 11, 12, 17
**Overall Score:** 3 / 6 (50%)

## Evaluation Methodology
Strict adherence to `03-golden-answers-key.md` falsification rules.

## Conversational Synthesis & Findings
Qwen 3.5 Max Preview (the larger preview model) scored 3/6 on the Beta batch — interestingly lower than the 27B variant on this particular slice. The ucode network script was correct. The UCI modification was clean. The Makefile was complete. Scenario 04 used deprecated Lua CBI `m = Map(...)`. The C daemon skeleton called `uloop_run()` without `ubus_add_uloop()`, leaving the ubus connection unregistered. Scenario 17 was adequate.

### New Truths Discovered
- None new.

### New Falsenesses Discovered
- None new.

## Scenario Breakdown
- **Scenario 02:** 1 (Pass) - Correct `import * as ubus from 'ubus'`, `ubus.conn()`.
- **Scenario 04:** 0 (Fail) - Used deprecated Lua CBI `m = Map(...)`. Taxonomy: `ERR_LEGACY_API`.
- **Scenario 08:** 1 (Pass) - Correct `cursor.set()`, `cursor.save()`, `cursor.commit()`.
- **Scenario 11:** 1 (Pass) - Correct Makefile. `DEPENDS:=+libubus` present.
- **Scenario 12:** 0 (Fail) - Missing `ubus_add_uloop()`; entered `uloop_run()` without ubus event loop integration. Taxonomy: `ERR_MISSING_BOILERPLATE`.
- **Scenario 17:** 1 (Pass) - Accurately identified ucode as lightweight JavaScript-like replacement for Lua.
