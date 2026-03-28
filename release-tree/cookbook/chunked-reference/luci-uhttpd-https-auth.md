---
title: LuCI uhttpd HTTPS and Auth Pattern
module: cookbook
origin_type: authored
token_count: 1547
source_file: L1-raw/cookbook/luci-uhttpd-https-auth.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_locator: content/cookbook-source/luci-uhttpd-https-auth.md
description: Explains the current OpenWrt login and transport path across LuCI, uhttpd,
  rpcd sessions, cookies, bearer auth, and HTTPS configuration, including the main
  edge cases that break deployments.
era_status: current
when_to_use: Use when building or debugging LuCI login flows, rpc endpoints, HTTPS
  deployment, session cookies, or ubus-backed browser requests behind uhttpd.
related_modules:
- luci
- uhttpd
- rpcd
- ubus
verification_basis: Verified against current luci, uhttpd, and openwrt source checkouts
  under tmp/authoring-repos on 2026-03-28; archive-backed shortlist for LuCI and uhttpd
  HTTPS/auth edge cases
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---

> **Source:** `content/cookbook-source/luci-uhttpd-https-auth.md`
> **Kind:** authored | **Method:** hand-authored
> **Normalized:** 2026-03-28

# LuCI uhttpd HTTPS and Auth Pattern

> **When to use:** Use this guide when a LuCI page, RPC endpoint, or custom integration depends on login state, session propagation, HTTPS listeners, or ubus-backed browser requests.
> **Key components:** LuCI dispatcher, uhttpd, rpcd session, `sysauth` cookie, ubus
> **Era:** Current (23.x and later). Modern OpenWrt auth is a pipeline, not a single cookie check.

## Overview

The current path is:

1. LuCI authenticates through the `session login` ubus method
2. LuCI stores the returned session id in the `sysauth` cookie for browser flows
3. the dispatcher decides which auth methods are accepted for a route
4. uhttpd terminates [HTTP](../../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) or HTTPS and forwards ubus-backed requests with the session context

That means login bugs often come from boundary mismatches, not just wrong passwords.

## Pattern 1: LuCI login is a session-creation flow

Current source evidence:

- https://github.com/openwrt/luci/blob/405d4af/modules/luci-mod-rpc/luasrc/controller/rpc.lua
  Read: 2026-03-28

Current live behavior from `rpc.lua`:

```lua
local login = util.ubus("session", "login", {
	username = user,
	password = pass,
	timeout  = tonumber(config.sauth.sessiontime)
})
```

and then:

```lua
http.header("Set-Cookie", 'sysauth=%s; path=%s' %{
	challenge.sid,
	http.getenv("SCRIPT_NAME")
})
```

What this gets right:

1. the browser session is rooted in rpcd session state, not a LuCI-only token store
2. the cookie carries the session id, not an unrelated app-specific identifier
3. login is a backend flow tied to `session login`, not a purely frontend event

## Pattern 2: Dispatcher rules distinguish auth methods by route

Current source evidence:

- https://github.com/openwrt/luci/blob/405d4af/modules/luci-lua-runtime/luasrc/dispatcher.lua
  Read: 2026-03-28

Current live behavior from `dispatcher.lua`:

```lua
entry.auth = {
	login = true,
	methods = { "cookie:sysauth_https", "cookie:sysauth_http" }
}
```

and for RPC:

```lua
entry.auth = {
	login = false,
	methods = { "query:auth", "cookie:sysauth_https", "cookie:sysauth_http", "cookie:sysauth" }
}
```

What this means in practice:

1. not every route accepts the same auth transport
2. HTTPS and [HTTP](../../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) cookie paths are differentiated explicitly
3. older or custom endpoints that assume one universal cookie path are easy to get wrong

## Pattern 3: HTTPS is a real deployment surface, not only a theme option

Current source evidence:

- https://github.com/openwrt/openwrt/blob/82d9859/package/network/services/uhttpd/files/uhttpd.config
  Read: 2026-03-28
- https://github.com/openwrt/openwrt/blob/82d9859/package/network/services/uhttpd/files/uhttpd.init
  Read: 2026-03-28

Current live config shows:

```uci
list listen_https 0.0.0.0:443
list listen_https [::]:443
option redirect_https 0
option cert /etc/uhttpd.crt
option key /etc/uhttpd.key
```

and `uhttpd.init` wires that into the daemon with certificate generation, `-s` listeners, and optional `-q` redirect behavior.

The durable lesson is:

1. HTTPS availability depends on the actual `uhttpd` instance config and key material
2. redirect behavior is explicit and per-instance
3. LuCI login behavior sits on top of that transport choice, it does not replace it

## Pattern 4: ubus-backed HTTP calls still enforce session semantics

Current source evidence:

- https://github.com/openwrt/uhttpd/blob/506e249/ubus.c
  Read: 2026-03-28

Current live behavior from `uhttpd/ubus.c`:

```c
if (tb[HDR_AUTHORIZATION]) {
	const char *tmp = blobmsg_get_string(tb[HDR_AUTHORIZATION]);

	if (!strncasecmp(tmp, "Bearer ", 7))
		return tmp + 7;
}
```

and later, requests are checked against ubus session permissions unless `no_ubusauth` is explicitly enabled.

What this gets right:

1. bearer-style auth can be accepted for ubus [HTTP](../../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) flows
2. transport-layer auth is still mapped back to ubus session checks
3. disabling ubus auth is available only as a dangerous debug escape hatch, not a normal deployment pattern

## Keep / Avoid

Keep:

1. treat login as a `session login` plus cookie or bearer propagation flow
2. verify route-level accepted auth methods before debugging the wrong layer
3. keep HTTPS listener, certificate, and redirect behavior explicit in `uhttpd` config
4. assume ubus-backed browser calls still need valid session and ACL context
5. use HTTPS by intent, not by theme assumption

Avoid:

1. assuming the same cookie or query-token path works for every route
2. debugging LuCI login without checking `uhttpd` listener and certificate state
3. turning on `no_ubusauth` outside local debug work
4. assuming browser auth state can bypass rpcd session policy
5. treating [HTTP](../../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) versus HTTPS differences as purely cosmetic

## Related Pages

- [Inter-Component Communication Map](./inter-component-communication-map.md) - full boundary view across LuCI, uhttpd, rpcd, and ubus
- [ucode rpcd Service Pattern](./ucode-rpcd-service-pattern.md) - backend method design behind LuCI
- [LuCI Form with UCI](./luci-form-with-uci.md) - direct config-editing flows that still rely on the same session boundary

## Verification Notes

- Current source examples verified from live temporary clones on 2026-03-28:
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-mod-rpc/luasrc/controller/rpc.lua`
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-lua-runtime/luasrc/dispatcher.lua`
  - `https://github.com/openwrt/uhttpd/blob/506e249/ubus.c`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/network/services/uhttpd/files/uhttpd.config`
  - `https://github.com/openwrt/openwrt/blob/82d9859/package/network/services/uhttpd/files/uhttpd.init`
- Archive evidence reviewed 2026-03-28:
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-May.txt` (`Activate https server support in 21.02 by default`)
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-September.txt` (follow-on auth and HTTPS behavior discussion)
