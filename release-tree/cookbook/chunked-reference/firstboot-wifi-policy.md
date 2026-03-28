---
title: First-Boot Wi-Fi Policy
module: cookbook
origin_type: authored
token_count: 1767
source_file: L1-raw/cookbook/firstboot-wifi-policy.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_locator: content/cookbook-source/firstboot-wifi-policy.md
description: Focused guide to enabling or pre-seeding Wi-Fi on first boot in OpenWrt
  without turning asynchronous radio discovery into ad-hoc boot orchestration.
era_status: current
when_to_use: Use when an image, board integration, or package wants Wi-Fi enabled
  or pre-seeded on first boot and you need to decide whether the change belongs in
  board defaults, a uci-defaults script, or a custom build option.
related_modules:
- openwrt-core
- uci
- procd
- luci
verification_basis: Verified against current openwrt/openwrt checkout at 56bf67d47406bd7c64cdfc6a8610032afe7094cf;
  package/base-files/files/etc/init.d/boot; package/base-files/files/lib/functions/uci-defaults.sh;
  package/boot/uboot-tools/uboot-envtools/files/fw_defaults; package/network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/10-wifi-detect;
  OpenWrt-devel thread Enabling Wi-Fi on First boot
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---

> **Source:** `content/cookbook-source/firstboot-wifi-policy.md`
> **Kind:** authored | **Method:** hand-authored
> **Normalized:** 2026-03-28

# First-Boot Wi-Fi Policy

> **When to use:** Use this guide when you want first-boot Wi-Fi behavior to be predictable across image builds, board integrations, and reset-to-default workflows.
> **Key components:** `/etc/uci-defaults`, `/etc/init.d/boot`, `config_generate`, `ucidef_set_wireless`, `/etc/config/wireless`
> **Era:** Current (23.x and later). The core problem is policy placement, not radio timing.

## Overview

The recurring mistake is to treat first-boot Wi-Fi as an asynchronous probe race that needs sleeps, polling loops, or manual service starts.

The durable OpenWrt pattern is narrower:

1. decide the desired Wi-Fi policy in configuration space
2. write that policy at the right boot boundary
3. let the normal boot path and wireless stack apply it

If you remember only one rule, use this one:

1. first-boot Wi-Fi enablement is a config problem first
2. it is only a runtime orchestration problem if you ignored the config boundary

## The Current Boot Boundary

Current `/etc/init.d/boot` still shows the important sequence:

1. optional early defaults such as `30_uboot-envtools` are sourced before `config_generate`
2. `config_generate` materializes missing config files
3. `/sbin/wifi config` generates wireless config when needed
4. `uci_apply_defaults` runs normal `uci-defaults` scripts
5. `/sbin/reload_config` applies the settled configuration

That sequence explains why two different first-boot Wi-Fi patterns both exist:

1. if you must shape generated defaults before `/etc/config/wireless` exists, write board or image defaults before `config_generate`
2. if you only need to mutate the final wireless config before services settle, use a normal `uci-defaults` script and let `reload_config` apply the result

## Wrong Mental Model

The archive discussion starts with the common fear: Wi-Fi probes asynchronously on some devices, so enabling Wi-Fi in `uci-defaults` sounds unsafe.

The correction is simpler than that. You do not need a `uci-defaults` script to wait for radios. You only need it to express the desired config state before the later config-apply path runs.

Archive evidence:

- `Enabling Wi-Fi on First boot`
  Source: https://lists.openwrt.org/pipermail/openwrt-devel/2021-July.txt
  Read: 2026-03-28
- Correction summary: the first-boot change is just enabling Wi-Fi in UCI; it does not require special runtime handling in the defaults script itself

## Pattern 1: Pre-Seed Wireless Defaults Before config_generate

If you want image-owned or board-owned wireless defaults, use the `uci-defaults` helper layer before `config_generate` runs.

Current source example:

- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/boot/uboot-tools/uboot-envtools/files/fw_defaults
  Read: 2026-03-28

```sh
. /lib/functions/uci-defaults.sh

fw_loadenv
board_config_update

[ -f /var/run/uboot-env/owrt_ssid -a -f /var/run/uboot-env/owrt_wifi_key ] &&
	ucidef_set_wireless all "$(cat /var/run/uboot-env/owrt_ssid)" sae-mixed "$(cat /var/run/uboot-env/owrt_wifi_key)"
[ -f /var/run/uboot-env/owrt_country ] && ucidef_set_country "$(cat /var/run/uboot-env/owrt_country)"

board_config_flush
exit 0
```

What this gets right:

1. it treats SSID, key, and country as defaults, not as post-boot runtime actions
2. it uses `ucidef_set_wireless` and related helpers instead of editing generated config by hand
3. it feeds the board-config path early enough that later config generation can consume the intended defaults cleanly

## Pattern 2: Mutate /etc/config/wireless Before reload_config Applies It

If `/etc/config/wireless` already exists, or if you are comfortable mutating the generated file after `wifi config` but before `reload_config`, a normal `uci-defaults` script is enough.

The key point from the archive thread is not the exact shell snippet. It is the boundary:

1. write the desired enabled state in UCI
2. do not start or restart wireless manually from the defaults script
3. let the normal boot path apply the final config

A minimal pattern looks like this:

```sh
#!/bin/sh

changed=0

for section in $(uci show wireless | sed -n "s/^wireless\.\([^.=][^.=]*\)=.*/\1/p" | sort -u); do
	case "$(uci -q get wireless.$section)" in
		wifi-device|wifi-iface)
			if [ "$(uci -q get wireless.$section.disabled)" = "1" ]; then
				uci delete wireless.$section.disabled
				changed=1
			fi
			;;
	esac
done

[ "$changed" -eq 1 ] && uci commit wireless
exit 0
```

This is intentionally boring. That is the point.

## Pattern 3: Keep Hardware Discovery Separate From Policy

Current wireless hotplug still shows the right ownership boundary for late device-add events:

- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/10-wifi-detect
  Read: 2026-03-28

```sh
#!/bin/sh

[ "${ACTION}" = "add" ] && {
	/sbin/wifi config
	ubus call network.wireless retry
}
```

This file exists to react to radio add events. It is not the place to encode your product policy about whether Wi-Fi should be enabled by default.

Use it as evidence for separation of concerns:

1. device discovery is owned by the wireless boot and hotplug path
2. product policy is owned by defaults and config mutation

## What To Avoid

1. Do not sleep in `uci-defaults` waiting for PHYs to appear.
2. Do not call `wifi up`, `/etc/init.d/network restart`, or `reload_config` from the defaults script just to force early visibility.
3. Do not bake device-specific SSID or key logic into a generic hotplug script.
4. Do not confuse default OpenWrt security policy with technical impossibility. Keeping Wi-Fi disabled by default is a policy choice, not evidence that first-boot enablement requires special async tricks.

## Decision Guide

Use this split:

1. Need custom generated defaults from board or image metadata: use `ucidef_set_wireless` before `config_generate`.
2. Need to remove `disabled` flags or commit a simple post-generation mutation: use a normal `uci-defaults` script.
3. Need a different first-boot security posture for your own image: make it a build or image policy toggle, not a runtime workaround.

## Related Pages

- [First-Boot uci-defaults Pattern](./firstboot-uci-defaults-pattern.md)
- [Network Device Model Migrations](./network-device-model-migrations.md)
- [Inter-Component Communication Map](./inter-component-communication-map.md)

## Verification Notes

- Current boot path verified from `package/base-files/files/etc/init.d/boot`
  Read: 2026-03-28
- Current helper API verified from `package/base-files/files/lib/functions/uci-defaults.sh`
  Read: 2026-03-28
- Current image-default pattern verified from `package/boot/uboot-tools/uboot-envtools/files/fw_defaults`
  Read: 2026-03-28
- Current wireless hotplug detection pattern verified from `package/network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/10-wifi-detect`
  Read: 2026-03-28
- Archive evidence verified from `https://lists.openwrt.org/pipermail/openwrt-devel/2021-July.txt`
  Read: 2026-03-28
