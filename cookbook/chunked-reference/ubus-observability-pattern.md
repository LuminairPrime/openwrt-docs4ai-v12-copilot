---
title: ubus Observability Pattern
module: cookbook
origin_type: authored
token_count: 1321
source_file: L1-raw/cookbook/ubus-observability-pattern.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_locator: static/cookbook-source/ubus-observability-pattern.md
description: Correct pattern for publishing runtime state once through ubus and letting
  LuCI, CLI tooling, and other services consume that shared state instead of re-deriving
  it in multiple places.
era_status: current
when_to_use: Use when multiple consumers need the same live OpenWrt runtime state
  such as interface status, service state, or computed device information.
related_modules:
- ubus
- netifd
- procd
- luci
- rpcd
verification_basis: Verified against current netifd, procd, ubus, and luci source
  checkouts under tmp/authoring-repos on 2026-03-28; archive-backed shortlist for
  ubus-first state surfaces
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---

> **Source:** `static/cookbook-source/ubus-observability-pattern.md`
> **Kind:** authored | **Method:** hand-authored
> **Normalized:** 2026-04-01

# ubus Observability Pattern

> **When to use:** Use this pattern when more than one component needs the same runtime state. Publish it once through ubus and consume it everywhere else.
> **Key components:** ubus, netifd, procd, LuCI RPC
> **Era:** Current (23.x and later). Recomputing runtime state separately in init scripts, LuCI views, and shell helpers is usually the wrong boundary.

## Overview

The durable OpenWrt observability rule is:

1. the component that owns a runtime fact should publish it
2. consumers should query that state through ubus
3. presentation layers should render the published state, not rediscover it

This is the difference between a stable control plane and a pile of duplicated shell logic.

## Wrong Boundary

### WRONG

```sh
ip link show br-lan
cat /var/run/myservice.state
ps | grep myservice
```

Why this fails:

1. every consumer now needs its own parsing logic
2. different callers drift into different definitions of the same state
3. browser-facing code cannot safely reuse that path without extra backend glue

### CORRECT

Publish the state once through ubus and let every consumer query the same object contract.

## Pattern 1: The owner daemon should expose status methods

Current source evidence:

- https://github.com/openwrt/netifd/blob/69a5afc/ubus.c
  Read: 2026-03-28

Current live behavior from `netifd/ubus.c`:

```c
static struct ubus_object main_object = {
	.name = "network",
	.type = &main_object_type,
	.methods = main_object_methods,
	.n_methods = ARRAY_SIZE(main_object_methods),
};
```

and later:

```c
blob_buf_init(&b, 0);
device_dump_status(&b, dev);
ubus_send_reply(ctx, req, b.head);
```

What this gets right:

1. the owner daemon publishes named methods on a stable object
2. status is returned as structured data
3. callers do not need to understand netifd internals to consume the result

## Pattern 2: Service managers should publish service state, not just process ids

Current source evidence:

- https://github.com/openwrt/procd/blob/cd7a4e5/service/service.c
  Read: 2026-03-28

`procd/service/service.c` shows the same pattern at the service layer. It keeps a service model, updates instances through its own control path, and emits service-data update events with `trigger_event("service.data.update", ...)`.

What this gets right:

1. service state belongs to the service manager that owns lifecycle
2. updates are emitted as structured events, not implied through log scraping
3. other components can observe the manager instead of reverse-engineering process state

## Pattern 3: LuCI should consume ubus through a stable RPC layer

Current source evidence:

- https://github.com/openwrt/luci/blob/405d4af/modules/luci-base/htdocs/luci-static/resources/rpc.js
  Read: 2026-03-28

`rpc.js` already expects browser code to consume structured ubus replies. It supports:

1. `object` and `method` declarations through `rpc.declare()`
2. `expect` defaults for missing optional fields
3. `filter` functions for presentation-specific reshaping

That means the right browser pattern is not "shell out from LuCI." It is "call the ubus owner through the existing RPC layer."

## Pattern 4: The bus registry is part of the contract

Current source evidence:

- https://github.com/openwrt/ubus/blob/3cc98db/ubusd_obj.c
  Read: 2026-03-28

`ubusd_obj.c` shows the registry layer itself: object types, object creation, path registration, and subscription handling all live in the bus daemon. That is why object naming and method shape matter. Once other components consume an object, that object becomes a contract.

## Keep / Avoid

Keep:

1. publish runtime state in the daemon that owns it
2. return structured ubus data, not formatted text blobs
3. let LuCI and other consumers use the same ubus contract
4. use `expect` defaults for optional fields on the frontend
5. treat object names and method signatures as part of the public interface

Avoid:

1. recomputing runtime state in each consumer
2. parsing logs or shell command output when the owner can publish structured data
3. binding browser features to unstable local file paths
4. exposing presentation-shaped strings instead of machine-readable objects
5. changing ubus object shape casually once consumers depend on it

## Related Pages

- [ucode rpcd Service Pattern](./ucode-rpcd-service-pattern.md) - use this when you need a small privileged backend API
- [Inter-Component Communication Map](./inter-component-communication-map.md) - use this to decide whether the right boundary is ubus, UCI, rpcd, or LuCI
- [procd Service Lifecycle](./procd-service-lifecycle.md) - use this when the real concern is supervised service state and lifecycle

## Verification Notes

- Current source examples verified from live temporary clones on 2026-03-28:
  - `https://github.com/openwrt/netifd/blob/69a5afc/ubus.c`
  - `https://github.com/openwrt/procd/blob/cd7a4e5/service/service.c`
  - `https://github.com/openwrt/ubus/blob/3cc98db/ubusd_obj.c`
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-base/htdocs/luci-static/resources/rpc.js`
- Archive evidence reviewed 2026-03-28:
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-January.txt` (`add ubus support to ltq-[v|a]dsl-app`)
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-December.txt` (`netifd: add devtype to ubus call`)
