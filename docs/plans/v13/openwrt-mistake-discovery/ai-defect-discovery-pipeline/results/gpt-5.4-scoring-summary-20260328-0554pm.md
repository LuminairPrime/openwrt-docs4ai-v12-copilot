# GPT-5.4 Scoring Summary - 2026-03-28 Session

**Model:** GPT-5.4
**Session Date:** 2026-03-28
**Timestamp Suffix:** 20260328-0554pm
**Golden Key Reference:** 03-golden-answers-key.md
**Raw Result Files Scored:** 22
**New Score Files Written:** 22

## What This Session Did
This session re-ran the manual falsification pass across every raw AI output file in the `results/` tree, one file at a time. Existing Alpha judgments that were already validated against the same golden key were re-issued under a fresh timestamp, and the previously unscored raw files were scored from scratch against the current truth schema plus authoritative OpenWrt docs contained in this repository.

## Newly Scored From Scratch
*   arcee-ai-trinity-large-preview-free-2026-03-28-0855am.md -> 6 / 17
*   nemotron-3-super-120b-a12b-2026087-0855am.md -> 4 / 11
*   stepflash-20260328-0856am.md -> 5 / 17
*   alpha/minimax-m2.5-20260328-0856am.md -> 4 / 17
*   beta/mimo-v2-pro-20260328-0901am.md -> 11 / 17
*   alpha/qwen3.5-max-preview - Copy.txt -> 2 / 6

## Reissued Existing Validated Alpha Scores
16 Alpha raw files already had prior deterministic score artifacts. Those judgments were re-issued under the new timestamp so every raw file in the tree now has a session-consistent score artifact.

## Golden Key Updates Made
*   Scenario 02: banned raw `ip`/`/sys/class/net`/`jq` shell parsing in place of native ucode `ubus`.
*   Scenario 09: added the requirement to filter accepted `$ACTION` values early and exit for unrelated events.
*   Scenario 10: added the config-mutation-only truth for `/etc/uci-defaults/` and banned calling `/etc/init.d/...` from inside `uci-defaults`.
*   Scenario 11: banned deprecated `PKG_MD5SUM` in current-era package Makefiles.
*   Scenario 14: banned `/usr/share/luci/menus.d/` and other noncanonical menu JSON contracts.
*   Scenario 16: added explicit async ucode wiring truths around `uloop.handle(..., uloop.ULOOP_READ)` and banned invented `fs.read(fd, len)`-style process reads.

## Session Results Highlights
*   Best newly scored full run: `beta/mimo-v2-pro-20260328-0901am.md` at 11 / 17.
*   Most common failure families remained unchanged: legacy LuCI Lua/UI patterns, shell parsing in place of native ucode/ubus, missing `uci_load_validate`, and broken first-boot semantics.
*   The new docs-backed scoring refinements mostly affected boundary correctness rather than broad architectural direction, especially around `uci-defaults`, current-era package metadata, and precise async ucode APIs.

## Output Files Generated This Session
22 score artifacts with the suffix `20260328-0554pm` were written to the same result directories as their corresponding raw files.