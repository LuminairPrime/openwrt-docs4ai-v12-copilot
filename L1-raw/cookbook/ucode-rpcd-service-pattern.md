# ucode rpcd Service Pattern

> **When to use:** Use this pattern when the browser or another frontend needs a controlled backend method for computed state, cross-config operations, or privileged actions. If the problem is only "edit one UCI file", a plain LuCI `form.Map` is usually enough.
> **Key components:** rpcd, ucode, ubus, ACLs, LuCI `rpc.declare()`
> **Era:** Current (23.x and later). New OpenWrt backend glue should prefer small ubus or rpcd methods over ad-hoc shell CGI helpers.

## Overview

The durable boundary is:

1. LuCI or another frontend declares a remote method contract.
2. rpcd owns the privilege boundary and ACL check.
3. the backend implementation returns a small structured object, not formatted text.
4. missing optional state should degrade into a predictable reply, not a crash.

This matters because archive review repeatedly surfaced the same failure shape: code assumed a ubus object, backend field, or ACL surface would always exist, then a missing component caused the whole feature path to fail.

## Wrong Boundary

### WRONG

```sh
#!/bin/sh

# Called directly from a web action.
uci get myservice.main.enabled
/etc/init.d/myservice restart
```

Why this fails:

1. it has no named API contract
2. it mixes state reads with service control
3. it bypasses rpcd ACLs and makes graceful fallback hard

### CORRECT

Use an rpcd ucode plugin that returns a structured object, then let the frontend decide how to render or react to that data.

## Pattern 1: Export a small method table from ucode

Current source example:

Source evidence:

- https://github.com/openwrt/luci/blob/405d4af/applications/luci-app-example/root/usr/share/rpcd/ucode/example.uc
  Read: 2026-03-28

```ucode
#!/usr/bin/env ucode

'use strict';

import { cursor } from 'uci';

const uci = cursor();

const methods = {
	get_sample1: {
		call: function() {
			const num_cats = uci.get('example', 'animals', 'num_cats');
			const num_dogs = uci.get('example', 'animals', 'num_dogs');
			const num_parakeets = uci.get('example', 'animals', 'num_parakeets');
			const result = {
				num_cats,
				num_dogs,
				num_parakeets,
				is_this_real: false,
				not_found: null,
			};

			uci.unload();
			return result;
		}
	}
};

return { 'luci.example': methods };
```

What this gets right:

1. the exported object name is explicit
2. methods return structured data, not shell-formatted text
3. `null` and missing values are represented deliberately instead of being hidden

## Pattern 2: Let rpcd own the type bridge

The modern ucode plugin path works because rpcd already converts between ubus blob messages and ucode values.

Current source evidence:

- https://github.com/openwrt/rpcd/blob/5b07867/ucode.c
  Read: 2026-03-28

Relevant live behavior in `rpcd/ucode.c`:

1. `rpc_ucode_blob_to_ucv()` converts incoming blob fields into ucode values
2. `rpc_ucode_ucv_to_blob()` converts returned ucode values back into ubus replies
3. scripts and registered ubus objects are tracked centrally by the plugin runtime

The practical lesson is that plugin code should stay close to business logic and data shape. Do not re-implement your own text protocol on top of rpcd.

## Pattern 3: Put permissions at the rpcd boundary

Current source evidence:

- https://github.com/openwrt/rpcd/blob/5b07867/file.c
  Read: 2026-03-28
- https://github.com/openwrt/rpcd/blob/5b07867/session.c
  Read: 2026-03-28

`rpcd/file.c` shows the correct pattern for privileged methods:

```c
static bool
rpc_file_access(const struct blob_attr *sid,
                const char *path, const char *perm)
{
	if (!sid)
		return true;

	return ops->session_access(blobmsg_data(sid), "file", path, perm);
}
```

What this gets right:

1. permission is checked at the method boundary, not after side effects
2. the check is tied to the ubus session id, not ambient process state
3. the permission model is object-oriented (`file`, path, permission), which maps cleanly to ACLs

That is the model new ucode-backed methods should preserve. If a frontend must call it, the ACL contract should be explicit and minimal.

## Pattern 4: Frontends should expect defaults, not perfection

Current source evidence:

- https://github.com/openwrt/luci/blob/405d4af/modules/luci-base/htdocs/luci-static/resources/rpc.js
  Read: 2026-03-28

`rpc.js` already supports defensive frontend consumption through `expect` and `filter`. That means a backend method can expose a narrow structured contract and the frontend can still degrade safely when a field is missing.

What this means in practice:

1. backend methods should return stable keys
2. frontend code should use `expect` defaults for optional data
3. do not treat a missing optional backend as proof that the entire page must fail

## Keep / Avoid

Keep:

1. export a small named method table from the ucode plugin
2. return plain objects, arrays, booleans, numbers, and `null`
3. check permissions at the rpcd boundary through session-aware ACLs
4. treat optional runtime state as optional in both backend and frontend code
5. keep service control and config mutation explicit instead of implicit side effects

Avoid:

1. shelling out from the browser path through ad-hoc CGI glue
2. returning formatted strings when the caller really needs structured data
3. assuming a ubus object or plugin backend always exists
4. baking authorization into the frontend instead of rpcd ACLs
5. mixing unrelated methods into one oversized plugin namespace

## Related Pages

- [LuCI Form with UCI](./luci-form-with-uci.md) - use this when the page only needs standard UCI form binding
- [ubus Observability Pattern](./ubus-observability-pattern.md) - use this when the right answer is to publish runtime state once and consume it everywhere
- [Inter-Component Communication Map](./inter-component-communication-map.md) - use this to choose between UCI, ubus, rpcd, and LuCI boundaries

## Verification Notes

- Current source examples verified from live temporary clones on 2026-03-28:
  - `https://github.com/openwrt/luci/blob/405d4af/applications/luci-app-example/root/usr/share/rpcd/ucode/example.uc`
  - `https://github.com/openwrt/luci/blob/405d4af/modules/luci-base/htdocs/luci-static/resources/rpc.js`
  - `https://github.com/openwrt/rpcd/blob/5b07867/ucode.c`
  - `https://github.com/openwrt/rpcd/blob/5b07867/file.c`
  - `https://github.com/openwrt/rpcd/blob/5b07867/session.c`
- Archive evidence reviewed 2026-03-28:
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-June.txt` (dnsmasq ubus collision and init failure discussion)
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2025-December.txt` (`ufpd: import unetmsg.client conditionally`)