---
title: Inter-Component Communication Map
module: cookbook
origin_type: authored
token_count: 1645
source_file: L1-raw/cookbook/inter-component-communication-map.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_locator: content/cookbook-source/inter-component-communication-map.md
description: 'Practical guide to choosing the correct communication boundary in modern
  OpenWrt: UCI for persistent config, ubus for runtime state and method calls, rpcd
  for privileged backend APIs, and LuCI as the browser-facing consumer.'
era_status: current
when_to_use: Use when deciding where new logic belongs and how components should exchange
  data across browser, web server, backend services, and system daemons.
related_modules:
- luci
- uhttpd
- rpcd
- ubus
- uci
- procd
- netifd
- ucode
verification_basis: Verified against current luci, uhttpd, rpcd, netifd, procd, ubus,
  and ucode source checkouts under tmp/authoring-repos on 2026-03-28
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---
# Inter-Component Communication Map

> **When to use:** Use this guide when you are deciding where a new feature should live or how one OpenWrt component should talk to another.
> **Key components:** LuCI, uhttpd, rpcd, ubus, UCI, procd, netifd, ucode
> **Era:** Current (23.x and later). Most OpenWrt architecture mistakes are boundary mistakes, not syntax mistakes.

## Overview

The communication map is simple once you separate persistent configuration from live control-plane state:

1. **UCI** owns persistent configuration under `/etc/config/*`
2. **ubus** owns structured runtime calls and state exchange
3. **rpcd** exposes privileged backend methods and enforces ACLs for callers
4. **uhttpd** terminates [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) and forwards browser RPC traffic into the ubus world
5. **LuCI** renders the browser UI and consumes backend state through RPC, not through direct shell access

## The Current Request Path

For a browser-driven admin flow, the current path looks like this:

1. a LuCI view declares or issues an RPC call
2. uhttpd receives the request and handles the [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) session context
3. rpcd validates the session and ACL boundary
4. ubus routes the call to the owning daemon or plugin
5. the owner daemon returns structured data

Live source anchors:

- `luci/modules/luci-base/htdocs/luci-static/resources/rpc.js`
- `luci/modules/luci-mod-rpc/luasrc/controller/rpc.lua`
- `luci/modules/luci-lua-runtime/luasrc/dispatcher.lua`
- `uhttpd/ubus.c`
- `rpcd/session.c`

## Choose The Right Boundary

### If the data must persist across boots: use UCI

Examples:

1. package defaults under `/etc/config/*`
2. migration scripts under `/etc/uci-defaults`
3. LuCI forms that edit named config sections

If you are tempted to persist state in random files or in browser-only storage, step back and ask whether it belongs in UCI instead.

### If the data is live runtime state: use ubus

Examples:

1. netifd network status
2. procd service status
3. session and ACL state exposed through rpcd

If the answer changes while the system is running, it usually belongs on ubus, not in a config file.

### If the question is "what device am I actually running on?": use `ubus call system board`

This deserves its own rule because people keep trying to reconstruct runtime identity from build tuples or image filenames.

The archive correction is explicit: `ubus call system board` is what `auc` and `luci-app-attendedsysupgrade` use to decide which target, subtarget, and board selector apply to the running system.

Current `procd/system.c` still implements that contract by assembling `model`, `board_name`, `rootfs_type`, and `release.*` from live system sources.

Use that surface when you need:

1. a human-readable model name
2. the canonical board identifier
3. the active target or subtarget
4. release and revision metadata tied to the running system

### If a browser needs privileged backend logic: use rpcd

Examples:

1. a LuCI view that needs a computed reply instead of plain UCI binding
2. a backend method that reads runtime state and writes config together
3. a small privileged operation that must pass through ACL checks

rpcd is the privilege and ACL boundary. Do not replace it with ad-hoc shell CGI scripts.

### If the concern is HTTP session or request transport: use uhttpd and LuCI runtime

Current source examples show that LuCI auth and session handling are not generic web-app glue pasted on top of OpenWrt. They are part of a specific path:

1. `luci-mod-rpc/rpc.lua` uses `session login` and sets the `sysauth` cookie
2. `luci-lua-runtime/dispatcher.lua` differentiates between `cookie:sysauth_https`, `cookie:sysauth_http`, and query-token paths
3. `uhttpd/ubus.c` accepts bearer-style authorization and enforces ubus session checks

That means authentication, transport, and backend method boundaries must stay aligned.

## Common Placement Errors

### WRONG: Put runtime status in UCI

UCI is for intended configuration, not volatile status. If your code keeps rewriting a config option just to mirror runtime state, it is probably in the wrong layer.

### WRONG: Make LuCI rediscover backend state itself

LuCI should consume backend contracts, not rebuild them by running shell commands, parsing `/proc`, or reading private daemon files.

### WRONG: Treat rpcd as a generic shell executor

rpcd methods should have explicit object names, method names, and ACL-scoped behavior. A giant "run anything" path is a design failure.

## Practical Decision Rules

Ask these questions in order:

1. Does the value need to survive reboot? If yes, start with UCI.
2. Is this live state owned by a running daemon? If yes, publish or consume it through ubus.
3. Does a browser need a privileged backend action? If yes, expose a small rpcd method plus ACL.
4. Is the problem really about daemon lifecycle or boot sequencing? If yes, move toward procd, hotplug, or `uci-defaults` instead of inventing a new RPC path.

## Related Pages

- [LuCI Form with UCI](./luci-form-with-uci.md) - direct config editing through LuCI
- [ucode rpcd Service Pattern](./ucode-rpcd-service-pattern.md) - small privileged backend APIs
- [ubus Observability Pattern](./ubus-observability-pattern.md) - publish runtime state once and consume it everywhere
- [Runtime Device Identity via ubus](./runtime-device-identity-via-ubus.md) - canonical runtime board, model, and release lookup
- [First-Boot uci-defaults Pattern](./firstboot-uci-defaults-pattern.md) - first-boot and migration-time config mutation
- [First-Boot Wi-Fi Policy](./firstboot-wifi-policy.md) - where Wi-Fi enablement belongs in the first-boot sequence
- [Hotplug Handler Pattern](./hotplug-handler-pattern.md) - event-driven runtime dispatch without turning hotplug into a second service manager

## Verification Notes

- Current source examples verified from live temporary clones on 2026-03-28:
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-base/htdocs/luci-static/resources/rpc.js`
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-mod-rpc/luasrc/controller/rpc.lua`
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-lua-runtime/luasrc/dispatcher.lua`
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-base/ucode/dispatcher.uc`
  - `https://github.com/openwrt/uhttpd/blob/506e249/ubus.c`
  - `https://github.com/openwrt/rpcd/blob/5b07867/session.c`
  - `https://github.com/openwrt/rpcd/blob/5b07867/ucode.c`
  - `https://github.com/openwrt/netifd/blob/69a5afc/ubus.c`
  - `https://github.com/openwrt/procd/blob/cd7a4e5/service/service.c`
  - `https://github.com/jow-/ucode/blob/763d8c3/lib/ubus.c`