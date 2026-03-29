---
title: Network Device Model Migrations
module: cookbook
origin_type: authored
token_count: 1367
source_file: L1-raw/cookbook/network-device-model-migrations.md
last_pipeline_run: '2026-03-29T23:50:02.157846+00:00'
source_locator: static/cookbook-source/network-device-model-migrations.md
description: Correct pattern for modern OpenWrt network model migrations, including
  bridge ifname-to-ports conversion, device-section migration, and current DSA-era
  helper usage in board defaults.
era_status: current
when_to_use: Use when migrating legacy network config, reviewing board defaults, or
  writing current-era OpenWrt network setup that must survive bridge and DSA model
  changes.
related_modules:
- openwrt-core
- uci
- wiki
verification_basis: Verified against current openwrt source checkout under tmp/authoring-repos
  on 2026-03-28 plus archive-backed shortlist for bridge and DSA migration lessons
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---

> **Source:** `static/cookbook-source/network-device-model-migrations.md`
> **Kind:** authored | **Method:** hand-authored
> **Normalized:** 2026-03-29

# Network Device Model Migrations

> **When to use:** Use this guide when you are moving older OpenWrt network config into the current bridge and device model, or when writing new board defaults that should match the post-swconfig, post-`ifname` era.
> **Key components:** UCI network config, bridge device sections, `uci-defaults` helper layer, board defaults
> **Era:** Current (23.x and later). New code should assume device sections and bridge `ports`, not legacy `ifname`-driven bridge layout.

## Overview

The durable migration rule is:

1. migrate old config explicitly
2. preserve user intent while changing schema
3. write new defaults in the current device model, not the deprecated one

That is why current OpenWrt carries both one-shot migration scripts and newer helper APIs.

## Pattern 1: Convert bridge `ifname` into `ports`

Current source evidence:

- https://github.com/openwrt/openwrt/blob/82d9859/package/base-files/files/etc/uci-defaults/11_network-migrate-bridges
  Read: 2026-03-28

Current live migration logic:

```sh
migrate_ports() {
	local config="$1"
	local type ports ifname

	config_get type "$config" type
	[ "$type" != "bridge" ] && return

	config_get ports "$config" ports
	[ -n "$ports" ] && return

	config_get ifname "$config" ifname
	[ -z "$ifname" ] && return

	for port in $ifname; do
		uci add_list network.$config.ports="$port"
	done
	uci delete network.$config.ifname
}
```

What this gets right:

1. it only mutates configs that are actually in the old shape
2. it preserves the user’s port list instead of overwriting it with a guess
3. it deletes the legacy key once the new key is populated

## Pattern 2: Move interface-owned bridge shape into a device section

The same migration script also handles the deeper schema shift from `type bridge` on an interface section to a dedicated `device` section with bridge ports.

That is the real current-era lesson: a modern bridge is a device object consumed by an interface, not just an interface with a legacy `ifname` string.

## Pattern 3: Current board defaults use DSA-era helper APIs

Current source evidence:

- https://github.com/openwrt/openwrt/blob/82d9859/package/base-files/files/lib/functions/uci-defaults.sh
  Read: 2026-03-28
- https://github.com/openwrt/openwrt/blob/82d9859/target/linux/realtek/base-files/etc/board.d/02_network
  Read: 2026-03-28
- https://github.com/openwrt/openwrt/blob/82d9859/target/linux/x86/base-files/etc/board.d/02_network
  Read: 2026-03-28

The helper layer already encodes the current model. In `uci-defaults.sh`, `ucidef_set_interface()` maps a space-separated `device` value into bridge `ports`, and target board files use helpers such as:

```sh
ucidef_set_bridge_device switch
ucidef_set_interface_lan "$lan_list"
```

and:

```sh
ucidef_set_interfaces_lan_wan "eth1 eth2" "eth0"
```

That is the live-repo proof of the current boundary: new defaults should be written in helper-driven, device-aware form, not by reintroducing old `switch_vlan` and `ifname` assumptions.

## Pattern 4: Treat swconfig-to-DSA as a user-intent migration problem

The archive evidence around DSA transition work points to the same broader rule: preserve the meaning of the user’s existing topology while moving it into the current model.

In practice this means:

1. migrate existing config explicitly rather than silently dropping it
2. prefer board-default helper APIs that already reflect the current model
3. avoid writing new examples that teach the deprecated layout just because old devices once used it

## Keep / Avoid

Keep:

1. detect old schema explicitly before mutating it
2. preserve existing port membership and bridge intent during migration
3. write new board defaults through current helper APIs
4. separate bridge device objects from interface attachment in new examples
5. treat migration as user-intent preservation, not a clean-slate rewrite

Avoid:

1. writing new cookbook examples that teach `ifname` as the preferred bridge model
2. silently dropping ports during migration
3. assuming the legacy switch model is still the authoritative shape
4. mixing migration logic into unrelated runtime service code
5. teaching target-specific switch quirks as if they were the modern default abstraction

## Related Pages

- [First-Boot uci-defaults Pattern](./firstboot-uci-defaults-pattern.md) - one-shot migration boundary and sequencing
- [Package Config Bootstrap Pattern](./package-config-bootstrap-pattern.md) - package-owned migration and bootstrap layout
- [Architecture Overview](./architecture-overview.md) - high-level component map

## Verification Notes

- Current source examples verified from live temporary clones on 2026-03-28:
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/base-files/files/etc/uci-defaults/11_network-migrate-bridges`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/base-files/files/lib/functions/uci-defaults.sh`
  - `https://github.com/openwrt/openwrt/blob/82d9859/target/linux/realtek/base-files/etc/board.d/02_network`
  - `https://github.com/openwrt/openwrt/blob/82d9859/target/linux/x86/base-files/etc/board.d/02_network`
- Archive evidence reviewed 2026-03-28:
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-May.txt` (`bridge: rename "ifname" attribute to "ports"`)
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-October.txt` (`bcm53xx: switch to the upstream DSA-based b53 driver`)
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2025-January.txt` (`ath79: Push MV88E6060 DSA switch into package`)
