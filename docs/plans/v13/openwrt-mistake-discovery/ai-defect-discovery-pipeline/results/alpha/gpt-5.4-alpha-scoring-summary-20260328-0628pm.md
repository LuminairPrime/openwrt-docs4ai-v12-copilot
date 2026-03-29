# GPT-5.4 Alpha Scoring Summary

**Date:** 2026-03-28
**Scope:** Fresh Alpha-only rescoring after removing copied `0554pm` Alpha artifacts
**Folder:** `results/alpha`
**Model:** GPT-5.4

## What This Session Did
This pass left all historical Alpha score runs untouched, removed the copied `0554pm` Alpha artifacts created earlier in the conversation, and then rescored the Alpha raw files from scratch using the current `03-golden-answers-key.md` and repo documentation. The updated top-level golden key and the earlier top-level GPT-5.4 summary were preserved.

## Files Scored
* `claude-opus-4-6-thinking.txt` - 1/6
* `claude-sonnet-4-6.txt` - 1/6
* `deepseek32.txt` - 1/6
* `dola-seed-2.0-pro-text.txt` - 1/6
* `geminiflashthinking.txt` - 2/6
* `geminipro.txt` - 2/6
* `glm-5.txt` - 1/6
* `gpt-5.2-high.txt` - 1/6
* `grok-4.20-multi-agent-beta-0309.txt` - 1/6
* `hearth.txt` - 2/6
* `kimi-k2.5.txt` - 1/6
* `mimo-v2-pro.txt` - 0/6
* `minimax-m2.7.txt` - 0/6
* `nvidia-nemotron-3-nano-30b-a3b-bf16.txt` - 0/6
* `qwen3.5-max-preview.txt` - 1/6
* `qwen3.5-max-preview - Copy.txt` - 0/0
* `significantotter.txt` - 0/6
* `minimax-m2.5-20260328-0856am.md` - 4/17

## Aggregate Result
Across 113 scorable scenario instances, this Alpha-only pass recorded 19 passes and 94 failures. The strongest Alpha-slice results in this session were `geminiflashthinking.txt`, `geminipro.txt`, and `hearth.txt` at 2/6. The broad full-run file `minimax-m2.5-20260328-0856am.md` reached 4/17.

## Dominant Failure Patterns
* Scenario 01: every Alpha-slice file failed on missing or wrong validation boilerplate, usually the absence of `uci_load_validate`.
* Scenario 05: every Alpha-slice file failed on LuCI modernization, usually by using legacy Lua or otherwise missing required `rpc.declare`, `L.resolveDefault`, and `E()` patterns.
* Scenario 13: every Alpha-slice file failed by preferring shell JSON parsers such as `jsonfilter`, `jshn`, `jq`, or `awk` instead of native ucode `fs.readfile()` plus `json()`.
* Scenario 16: every Alpha-slice file failed by using shell background jobs, FIFOs, `while read` loops, or similar shell orchestration instead of native ucode async with `uloop`.
* Scenario 07 was the most survivable Alpha scenario; 11 of 16 Alpha-slice files correctly used `blob_buf`, `blobmsg_add_string()`, and `ubus_send_reply()`.

## Notes On Special Cases
* `qwen3.5-max-preview - Copy.txt` contained no scorable scenario content and was recorded as `0/0` rather than as a technical fail.
* `significantotter.txt` was notable not just for outdated patterns but for fabricated or noncanonical API surface in both LuCI and ubus C answers.
* `minimax-m2.5-20260328-0856am.md` is not an Alpha-slice response. It is a full 17-scenario run stored under the Alpha folder and was scored as such.

## Golden Key Impact
No additional golden-key edits were required during this Alpha-only rescoring pass. The earlier session updates to `03-golden-answers-key.md` remain in place.