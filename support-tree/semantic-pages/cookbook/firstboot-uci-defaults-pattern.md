---
title: First-Boot uci-defaults Pattern
module: cookbook
origin_type: authored
token_count: 2815
source_file: L1-raw/cookbook/firstboot-uci-defaults-pattern.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_locator: content/cookbook-source/firstboot-uci-defaults-pattern.md
description: Correct pattern for first-boot and migration-time configuration changes
  in OpenWrt using /etc/uci-defaults, including sequencing, idempotency, helper usage,
  and the boundary between config mutation and service orchestration.
era_status: current
when_to_use: Use when a package, board integration, or image customization needs to
  set default config, migrate old config keys, or enable policy at first boot without
  starting services manually.
related_modules:
- openwrt-core
- uci
- procd
- luci
verification_basis: Verified against current openwrt/openwrt checkout at 56bf67d47406bd7c64cdfc6a8610032afe7094cf;
  package/boot/uboot-tools/uboot-envtools/files/fw_defaults; package/network/services/odhcpd/files/odhcpd.defaults;
  package/utils/mtd-utils/files/ubihealthd.defaults; package/network/services/uhttpd/files/ubus.default;
  OpenWrt wiki uci-defaults developer page; OpenWrt-devel threads on uhttpd reload
  from uci-defaults and enabling Wi-Fi on first boot
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---
# First-Boot uci-defaults Pattern

> **When to use:** Use this pattern when you need to write default config, migrate old config keys, or apply first-boot policy in OpenWrt before normal services start.
> **Key components:** `/etc/uci-defaults`, UCI, `board_config_update`, `board_config_flush`
> **Era:** Current (23.x and later). `/etc/uci-defaults` is still the right boundary for first-boot mutation and upgrade-time config migration. It is not the right place to start or reload daemons.

## Overview

`/etc/uci-defaults` scripts run early, before the normal service graph settles. That timing is exactly why they are useful for configuration mutation and exactly why they are dangerous for service orchestration.

The durable rule is simple:

1. Use `uci-defaults` to change configuration state.
2. Let the rest of boot, or later procd triggers, apply that state.
3. Do not call init scripts from `uci-defaults` unless you are deliberately accepting early-boot side effects.

Exit status is part of the contract too:

1. `exit 0` means the script succeeded and may be deleted.
2. non-zero exit means the script should remain and be retried on the next boot.
3. if a failed mutation must not be lost, handle that path explicitly instead of always ending with `exit 0`.

In the normal boot path, `/etc/init.d/boot` treats a successful `uci-defaults` run as complete and removes the script so it does not execute again.

This matters for three recurring OpenWrt mistake families:

1. calling `/etc/init.d/...` from `uci-defaults` to make a config change take effect immediately
2. writing migrations that always commit, even when nothing changed
3. treating first-boot Wi-Fi enablement as a hardware-probe timing problem instead of a config mutation problem

## Wrong Boundary

An OpenWrt-devel review on the historical `uhttpd` `ubus.default` change states the rule directly: calling init scripts from a `uci-defaults` script starts services too early and breaks the intended sequencing.

The useful lesson is not specific to `uhttpd`. It applies to any service managed by procd: write config in `uci-defaults`, then let the normal boot path or later reload triggers apply it.

The historical `uhttpd` `ubus.default` file is still useful as boundary evidence because it changes config without calling init scripts, but it is not as clean a copyable template as the explicit-commit examples below.

Archive evidence:

- `uhttpd: Reload config after uhttpd-mod-ubus was added` review thread
  Source: https://lists.openwrt.org/pipermail/openwrt-devel/2022-January.txt
  Read: 2026-03-28
- Reviewer quote: `Calling init.d scripts from uci-defaults script may result ... in starting uhttpd too early. We need all uci-defaults script to do their updates before we call any init.d.`

## Pattern 1: Config-Only Mutation Then Exit

The simplest valid `uci-defaults` script checks whether mutation is needed, writes only config, and exits cleanly.

Current source example:

Source evidence:

- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/system/rpcd/files/50-migrate-rpcd-ubus-sock.sh
	Read: 2026-03-28

```sh
#!/bin/sh

[ "$(uci get rpcd.@rpcd[0].socket)" = "/var/run/ubus.sock" ] || exit 0

uci set rpcd.@rpcd[0].socket='/var/run/ubus/ubus.sock'
uci commit rpcd

exit 0
```

What this gets right:

1. It mutates only UCI state.
2. It commits the change explicitly instead of relying on later side effects.
3. It does not try to restart `rpcd` inside the defaults script.
4. It is guarded so existing correct values are left alone.

## Pattern 2: Commit Only If You Changed Something

Migration scripts should track whether they actually changed state. This avoids unnecessary writes and makes the script easier to reason about during upgrades.

Current source example:

Source evidence:

- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/services/odhcpd/files/odhcpd.defaults
  Read: 2026-03-28

```sh
if [ -n "$(uci -q get dhcp.odhcpd)" ]; then
	local commit hostsfile piodir piofolder

	commit=0

	piodir=$(uci -q get dhcp.odhcpd.piodir)
	if [ -z "$piodir" ]; then
		piodir=/tmp/odhcpd-piodir
		uci set dhcp.odhcpd.piodir=$piodir
		commit=1
	fi

	piofolder=$(uci -q get dhcp.odhcpd.piofolder)
	if [ -n "$piofolder" ]; then
		pio_folder_migrate $piofolder $piodir
		uci delete dhcp.odhcpd.piofolder
		commit=1
	fi

	[ "$commit" -eq 1 ] && uci commit dhcp

	exit 0
fi
```

What this gets right:

1. It treats `uci-defaults` as a migration boundary, not as a runtime control path.
2. It uses explicit change tracking before `uci commit`.
3. It exits after the migration path completes instead of mixing migration with unrelated runtime work.

## Pattern 3: Use Helper APIs For Board-Or Image-Scoped Defaults

If your defaulting logic is board-scoped or image-scoped, use the helper layer from `/lib/functions/uci-defaults.sh` instead of open-coding raw file edits.

Current source example:

Source evidence:

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

1. It uses the `uci-defaults` helper API instead of editing `/etc/config` text directly.
2. It brackets board-scoped mutation with `board_config_update` and `board_config_flush`.
3. It shows that Wi-Fi first-boot policy is still just configuration mutation.

## Pattern 4: Create Missing Config Once, Then Populate It

For package-owned config bootstrapping, guard on file existence first, create the config once, and then write predictable defaults.

Current source example:

Source evidence:

- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/utils/mtd-utils/files/ubihealthd.defaults
  Read: 2026-03-28

```sh
#!/bin/sh

[ -e "/etc/config/ubihealthd" ] && exit 0
[ ! -e "/sys/class/ubi" ] && exit 0

touch "/etc/config/ubihealthd"

for ubidev in /sys/class/ubi/*/total_eraseblocks; do
	ubidev="${ubidev%/*}"
	ubidev="${ubidev##*/}"
	uci batch <<EOF
set ubihealthd.$ubidev=ubi-device
set ubihealthd.$ubidev.device="/dev/$ubidev"
set ubihealthd.$ubidev.enable=1
EOF
done

uci commit ubihealthd
```

The important nuance here is why `exit 0` is correct for both early guards. This script is defining package-owned defaults for systems that already expose UBI devices at boot. If `/etc/config/ubihealthd` already exists, or if the system does not expose `/sys/class/ubi`, there is nothing left for this script to do on later boots, so successful deletion is the intended outcome.

What this gets right:

1. It is idempotent: existing config short-circuits the script.
2. It checks whether the underlying subsystem exists before writing config.
3. It creates package-owned defaults without trying to start the daemon itself.
4. Its early `exit 0` guards are deliberate: they mean "nothing to do on this device state," not "retry later."

## First-Boot Wi-Fi Is A Policy Decision, Not A Probe Race

The recurring misconception is that Wi-Fi cannot be enabled safely in `uci-defaults` because radios probe asynchronously. The mailing-list discussion shows the opposite boundary: the `uci-defaults` job is only to write the desired config before normal services start.

That means:

1. enabling first-boot Wi-Fi is a config mutation problem
2. the service and driver stack apply that config later in the normal boot path
3. if you need board- or image-specific Wi-Fi defaults, `ucidef_set_wireless` is the right level of abstraction

Supporting evidence:

- `Enabling Wi-Fi on First boot` thread
  Source: https://lists.openwrt.org/pipermail/openwrt-devel/2021-July.txt
  Read: 2026-03-28
- OpenWrt developer wiki `uci-defaults` page
  Source: https://openwrt.org/docs/guide-developer/uci-defaults
  Read: 2026-03-28

## Rules To Keep

1. `uci-defaults` is for config mutation and migration.
2. Prefer guard checks so reruns and upgrades do not overwrite user intent unnecessarily.
3. Use helper functions when mutating board or image defaults.
4. Batch writes when setting several UCI keys together.
5. Commit only when you changed something.
6. Exit with status `0` only when the script completed successfully or intentionally determined there is nothing to do; use non-zero exit when you need a retry on the next boot.

## Rules To Avoid

1. Do not call `/etc/init.d/... start` or `reload` just to make a config change visible immediately.
2. Do not edit `/etc/config/*` as raw text when UCI or `ucidef_*` helpers already express the operation.
3. Do not assume `uci-defaults` is only for pristine installs; upgrade-time migrations matter too.
4. Do not write unconditional defaults that clobber already-migrated or user-owned settings.

## Related Pages

- [First-Boot Wi-Fi Policy](./firstboot-wifi-policy.md)
- [procd Service Lifecycle](./procd-service-lifecycle.md)
- [UCI Read/Write from ucode](./uci-read-write-from-ucode.md)
- [LuCI Form with UCI](./luci-form-with-uci.md)
- [OpenWrt Architecture Overview](./architecture-overview.md)

## Verification Notes

Source evidence:

- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/services/uhttpd/files/ubus.default
  Read: 2026-03-28
- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/services/odhcpd/files/odhcpd.defaults
  Read: 2026-03-28
- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/utils/mtd-utils/files/ubihealthd.defaults
  Read: 2026-03-28
- https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/boot/uboot-tools/uboot-envtools/files/fw_defaults
  Read: 2026-03-28
- https://openwrt.org/docs/guide-developer/uci-defaults
  Read: 2026-03-28
- https://lists.openwrt.org/pipermail/openwrt-devel/2022-January.txt
  Read: 2026-03-28
- https://lists.openwrt.org/pipermail/openwrt-devel/2021-July.txt
  Read: 2026-03-28