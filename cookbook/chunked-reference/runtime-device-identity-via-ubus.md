---
title: Runtime Device Identity via ubus
module: cookbook
origin_type: authored
token_count: 1320
source_file: L1-raw/cookbook/runtime-device-identity-via-ubus.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_locator: static/cookbook-source/runtime-device-identity-via-ubus.md
description: Canonical pattern for identifying a running OpenWrt device from live
  system state using `ubus call system board` instead of reconstructing build tuples
  or scraping implementation-specific files.
era_status: current
when_to_use: Use when a script, LuCI component, upgrader, or external tool needs to
  determine the current device model, board identifier, target, release, or rootfs
  type from a running OpenWrt system.
related_modules:
- procd
- ubus
- luci
- openwrt-core
verification_basis: Verified against current procd checkout at cd7a4e5; procd/system.c
  implementation of `system.board`; archive thread Uniquely identifying a platform
  programmatically; current OpenWrt examples that report `ubus call system board`
  in diagnostics
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---

> **Source:** `static/cookbook-source/runtime-device-identity-via-ubus.md`
> **Kind:** authored | **Method:** hand-authored
> **Normalized:** 2026-04-01

# Runtime Device Identity via ubus

> **When to use:** Use this pattern whenever you need to know what device and release you are actually running on, rather than what build inputs you think created the image.
> **Key components:** `ubus`, `procd`, `system.board`, `jsonfilter`
> **Era:** Current (23.x and later). `ubus call system board` is the canonical runtime identity surface.

## Overview

One of the easiest OpenWrt mistakes is to reconstruct runtime identity from build-time variables such as target, subtarget, and profile naming conventions.

That approach is brittle because it assumes:

1. you still have the right build metadata available on the running device
2. every tool should rebuild the same mapping logic independently
3. the image naming convention is the runtime contract

The archive correction gives the better answer directly:

1. ask the running system for its runtime identity
2. use `ubus call system board`
3. treat that ubus reply as the canonical interface for device selection and upgrade tooling

## The Archive Correction

Archive evidence:

- `Uniquely identifying a platform programmatically`
  Source: https://lists.openwrt.org/pipermail/openwrt-devel/2021-May.txt
  Read: 2026-03-28

Problem summary:

1. a developer tried to infer the candidate firmware image from `CONFIG_TARGET_BOARD`, `CONFIG_TARGET_SUBTARGET`, and `CONFIG_TARGET_PROFILE`
2. that path still left gaps, especially around the effective board/profile identity on the running box

Correction:

```text
ubus call system board. That's what is used also by `auc` and `luci-app-attendedsysupgrade`,
it contains all information you need to know in order to decide which
target/subtarget ImageBuilder to use and which profile (=board) to
select.
```

That is the durable cookbook lesson. Do not teach each tool to rediscover the platform from fragments when the running system already publishes the answer.

## Current Source Anchor

Current `procd` still implements this surface in `system.board`.

Source evidence:

- https://github.com/openwrt/procd/blob/cd7a4e5/system.c
  Read: 2026-03-28

Key fields are built from live system sources:

1. `kernel` and `hostname` from `uname()`
2. `model` from `/tmp/sysinfo/model` or device-tree fallback
3. `board_name` from `/tmp/sysinfo/board_name` or compatible-string fallback
4. `rootfs_type` from the detected rootfs
5. `release.*` from `/usr/lib/os-release`, including `target`

That matters because it means the ubus surface is already normalizing multiple low-level sources into one stable reply shape.

## What The Reply Gives You

A typical reply looks like this:

```json
{
  "kernel": "6.6.57",
  "hostname": "OpenWrt",
  "system": "RTL8380",
  "model": "HPE 1920-8G-PoE+ 180W (JG922A)",
  "board_name": "hpe,1920-8g-poe-180w",
  "rootfs_type": "initramfs",
  "release": {
    "distribution": "OpenWrt",
    "version": "SNAPSHOT",
    "revision": "r27647+185-b5ffbe7c75",
    "target": "realtek/rtl838x",
    "description": "OpenWrt SNAPSHOT r27647+185-b5ffbe7c75"
  }
}
```

In practice the most useful fields are:

1. `board_name` for device-profile identity
2. `model` for human-readable display
3. `release.target` for target and subtarget selection
4. `release.version` and `release.revision` for upgrade and support decisions
5. `rootfs_type` when boot mode matters

## Preferred Usage Patterns

### Shell

```sh
ubus call system board
ubus call system board | jsonfilter -e '@.board_name' -e '@.release.target'
```

### LuCI Or Backend RPC Consumers

If a LuCI or rpcd-facing flow needs device identity, consume this ubus object once and pass the structured result upward. Do not rebuild the same answer by scraping multiple files in parallel.

### Upgrade Tooling

If you are selecting ImageBuilder targets, ASU inputs, or candidate sysupgrade images, use:

1. `release.target` for target and subtarget
2. `board_name` for the effective board or profile selector

That is exactly the archive guidance and exactly why this surface is so useful.

## Wrong Approaches

1. Do not reconstruct identity from `CONFIG_*` tuples unless you are operating inside the build system itself.
2. Do not scrape `/etc/board.json` first unless you have a very specific reason to bypass the canonical ubus layer.
3. Do not parse firmware filenames as if they were the runtime source of truth.
4. Do not make browser-side code guess the board by inspecting unrelated LuCI pages or package state.

## Decision Rule

Use this rule:

1. if the question is "what is this running device?", ask `system.board`
2. if the question is "what did my build system intend to produce?", inspect build metadata instead

Those are different questions. Confusing them is what produces fragile provisioning and upgrade logic.

## Related Pages

- [Inter-Component Communication Map](./inter-component-communication-map.md)
- [ubus Observability Pattern](./ubus-observability-pattern.md)
- [LuCI uhttpd HTTPS and Auth Pattern](./luci-uhttpd-https-auth.md)

## Verification Notes

- Current `system.board` implementation verified from `https://github.com/openwrt/procd/blob/cd7a4e5/system.c`
  Read: 2026-03-28
- Archive guidance verified from `https://lists.openwrt.org/pipermail/openwrt-devel/2021-May.txt`
  Read: 2026-03-28
- Example runtime outputs verified from processed archive diagnostics under `OpenWrt_Archives_Processed_Small`
  Read: 2026-03-28
