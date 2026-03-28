---
title: Package Config Bootstrap Pattern
module: cookbook
origin_type: authored
token_count: 1022
source_file: L1-raw/cookbook/package-config-bootstrap-pattern.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_locator: content/cookbook-source/package-config-bootstrap-pattern.md
description: 'Correct pattern for package-owned OpenWrt configuration: ship predictable
  /etc/config files, use /etc/uci-defaults only for one-shot detection or migration,
  and keep service application in init or procd logic.'
era_status: current
when_to_use: Use when creating a new package that owns config under /etc/config, needs
  to bootstrap defaults, or must migrate older config on upgrade.
related_modules:
- openwrt-core
- uci
- procd
- rpcd
verification_basis: Verified against current openwrt source checkout under tmp/authoring-repos
  on 2026-03-28; package Makefiles and installed defaults reviewed directly
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---
# Package Config Bootstrap Pattern

> **When to use:** Use this pattern when a package owns persistent config and needs to install a baseline config file, perform one-shot detection, or migrate older config keys.
> **Key components:** package Makefile, `/etc/config`, `/etc/uci-defaults`, init or procd scripts
> **Era:** Current (23.x and later). The package should own config explicitly instead of smuggling state through arbitrary runtime files.

## Overview

The package bootstrap rule is:

1. ship a predictable config file when a static baseline is enough
2. use `/etc/uci-defaults` only for one-shot detection or migration
3. let init or procd logic apply the resulting config at runtime

That keeps package installation, config ownership, migration, and service startup in separate layers.

## Pattern 1: Install the package-owned config file explicitly

Current source evidence:

  Read: 2026-03-28

`package/system/rpcd/Makefile` shows the basic ownership pattern:

```make
$(INSTALL_DIR) $(1)/etc/config
$(INSTALL_CONF) ./files/rpcd.config $(1)/etc/config/rpcd
$(INSTALL_DIR) $(1)/etc/uci-defaults
$(INSTALL_BIN) ./files/50-migrate-rpcd-ubus-sock.sh $(1)/etc/uci-defaults
```

What this gets right:

1. the package installs its canonical config file directly
2. migration logic is separated into a one-shot defaults script
3. the package layout shows ownership clearly to both humans and tooling

## Pattern 2: Static detection defaults belong in one-shot bootstrap scripts

Current source evidence:

  Read: 2026-03-28

Current live script:

```sh
[ ! -f /etc/config/fstab ] && ( block detect > /etc/config/fstab )
exit 0
```

This is the right shape for discovery-based bootstrap:

1. only create the config if it does not already exist
2. generate the file once
3. stop after bootstrap instead of mixing in service orchestration

## Pattern 3: Upgrades should migrate keys deliberately and commit only when needed

Current source evidence:

  Read: 2026-03-28
  Read: 2026-03-28

Two current patterns appear in live source:

1. **simple key migration**

```sh
[ "$(uci get rpcd.@rpcd[0].socket)" = "/var/run/ubus.sock" ] || exit 0

uci set rpcd.@rpcd[0].socket='/var/run/ubus/ubus.sock'
uci commit rpcd
```

2. **multi-step migration with changed-state tracking**

`odhcpd.defaults` keeps a `commit=0/1` flag, performs multiple guarded mutations, and commits only if something actually changed.

That is the correct migration boundary: explicit key changes, explicit commit, no hidden service restart.

## Pattern 4: Runtime application belongs to init or procd, not package install layout

Current source evidence:

  Read: 2026-03-28

The package bootstrap layer creates the intended config. The runtime layer reads it and turns it into daemon behavior. Keep those concerns separate.

## Keep / Avoid

Keep:

1. install the package-owned `/etc/config/<name>` file explicitly in the package
2. use `/etc/uci-defaults` for one-shot detection or migration only
3. keep migrations idempotent and guarded
4. commit config explicitly when a migration changes state
5. leave runtime application to init or procd logic

Avoid:

1. hiding canonical config in random package-private files
2. using package install scripts as ad-hoc runtime control paths
3. rewriting config on every boot when a one-shot bootstrap is enough
4. bundling migration and daemon startup in the same defaults script
5. assuming package-owned config can be reconstructed safely later if you never install it clearly

## Related Pages


## Verification Notes

  - `https://github.com/openwrt/openwrt/blob/82d9859/package/system/rpcd/Makefile`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/system/rpcd/files/50-migrate-rpcd-ubus-sock.sh`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/system/fstools/Makefile`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/system/fstools/files/fstab.default`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/network/services/odhcpd/files/odhcpd.defaults`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/network/services/uhttpd/files/uhttpd.init`