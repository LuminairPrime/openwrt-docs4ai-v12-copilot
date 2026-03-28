---
title: OpenWrt Architecture Overview
module: cookbook
origin_type: authored
token_count: 2981
source_file: L1-raw/cookbook/architecture-overview.md
last_pipeline_run: '2026-03-27T20:02:39.961617+00:00'
source_locator: content/cookbook-source/architecture-overview.md
description: Structural overview of OpenWrt component relationships, data flow, ACL/permission
  boundaries, and build-time vs runtime distinctions for AI tools and developers building
  on the platform.
era_status: current
when_to_use: Use before writing any cross-component OpenWrt code that involves service
  management, configuration storage, web UI, or scripting to ensure the components
  are wired correctly.
related_modules:
- procd
- uci
- ucode
- luci
- openwrt-core
verification_basis: Corpus review of procd, ucode, luci, and uci modules; upstream
  repo structure; rpcd ACL documentation in luci corpus
reviewed_by: placeholder
last_reviewed: '2026-03-23'
---
# OpenWrt Architecture Overview

> **When to use:** Use before writing any cross-component OpenWrt code that involves service management, configuration storage, web UI, or scripting to ensure the components are wired correctly.
> **Key components:** procd, UCI, ucode, rpcd, uhttpd, LuCI
> **Era:** Current (23.x+). Component relationships described here reflect the procd-based init era and JavaScript LuCI era. Legacy sysvinit and Lua LuCI wiring are not covered.

## Overview

OpenWrt is a Linux distribution purpose-built for embedded networking hardware. Its component stack is not the same as a general-purpose Linux distribution, and generic Linux patterns do not map cleanly onto it. The key difference is that nearly all runtime configuration, service lifecycle, and web-UI state passes through a small set of purpose-designed subsystems rather than being scattered across distro conventions.

Understanding the component relationships is the most important prerequisite for writing correct OpenWrt code. Wiring a component incorrectly -- for example, calling UCI from within an rpcd handler without checking ACL -- produces code that compiles and runs but violates the permission model in ways that are not immediately visible.

This page gives a structural overview of the primary components and their boundaries. Each section links to the detailed module reference for API depth.

## Component Map (Runtime)

```
Browser
  |
  | HTTP/HTTPS
  v
uhttpd (web server, port 80/443)
  |
  | Lua/CGI dispatcher routes LuCI JS app to browser
  | JSON-RPC requests proxied to rpcd
  v
rpcd (RPC daemon, listens on /var/run/ubus.ch or HTTP socket)
  |
  | ACL enforcement  (/usr/share/rpcd/acl.d/*.json)
  | Plugin dispatch
  v
ucode plugins (/usr/share/rpcd/exec.d/*.uc)
  |         |
  |         | sys.exec(), fs.popen()
  |         v
  |      Daemons managed by procd
  |         |
  v         v
UCI config files (/etc/config/)
  ^         |
  |         | uci commit -> file write
  |         v
procd (reads UCI config via triggers)
  |
  | service lifecycle, watch, respawn
  v
Running processes (/usr/sbin/mydaemon, etc.)
```

## Component Map (Simplified)

```
+----------------------------------------------------------+
|  LuCI (JavaScript, runs in browser)                      |
|  view.extend() -> form.Map -> L.rpc.call()               |
+---------------------------+------------------------------+
                            | JSON-RPC (authenticated)
+---------------------------v------------------------------+
|  uhttpd + rpcd                                           |
|  ACL check -> ucode plugin dispatch                      |
+--------+------------------+------------------------------+
         |                  |
   +-----v-------+    +-----v-------+
   |  UCI        |    |  procd      |
   |  /etc/config|    |  init, svc  |
   +-----+-------+    +-------------+
         |
   +-----v------------------+
   |  Config files (text)   |
   |  /etc/config/mypkg     |
   +------------------------+
```

## Component Descriptions

### procd

procd is the init system and service supervisor. It replaces legacy sysvinit for service lifecycle management. Services register with procd via `/etc/init.d/` scripts using the `USE_PROCD=1` convention and the `procd_open_instance`/`procd_close_instance` API.

procd also manages hotplug events via `/etc/hotplug.d/` scripts and the `hotplug-call` interface.

Key capabilities:
- Service instance lifecycle (start, stop, respawn on crash)
- Config-change triggers (`procd_add_reload_trigger`)
- Watchdog monitoring

See: `../../procd/chunked-reference/` for API detail.

### UCI (Unified Configuration Interface)

UCI is the central configuration system. All package configurations are stored as plain-text UCI files under `/etc/config/`. The `uci` command-line tool and the ucode `uci` module both provide read/write access.

UCI changes are two-phase: `uci set` stages a change, `uci commit` persists it to disk. Missing the commit step is the most common UCI mistake; staged changes do not survive a reboot.

See: `../../uci/chunked-reference/` for API detail.

### rpcd

rpcd is the privilege-separated RPC daemon. LuCI web views communicate with the system via rpcd over an authenticated JSON-RPC channel (proxied by uhttpd). rpcd enforces ACL rules defined in `/usr/share/rpcd/acl.d/*.json`. Ucode scripts registered as rpcd plugins run inside rpcd's privilege sandbox.

rpcd runs as root but enforces per-session ACL rules so that unprivileged LuCI sessions cannot call privileged methods.

### ucode

ucode is a lightweight scripting language purpose-built for OpenWrt. It is the preferred language for rpcd plugins and UCI manipulation from scripts. It runs `.uc` source files and has built-in modules for `uci`, `fs`, `uloop`, `math`, `struct`, and others.

ucode is NOT Node.js. It does not have `require()`, `Buffer`, `process`, or browser globals. See [Common AI Mistakes](./common-ai-mistakes.md) for the full list of ucode/Node.js confusion patterns.

See: `../../ucode/chunked-reference/` for API detail.

### uhttpd

uhttpd is the lightweight web server. It serves static LuCI assets, processes CGI/Lua requests (legacy), and proxies authenticated JSON-RPC calls to rpcd. It handles TLS termination and manages LuCI session tokens.

### LuCI

LuCI is the web management interface. In the current era it is a client-side JavaScript application served by uhttpd. Views inherit from `LuCI.view` and use `LuCI.form` to build declarative UCI-backed settings pages.

See: `../../luci/chunked-reference/` for JS API detail.

## Build-Time vs Runtime Components

Many AI errors stem from confusing build-time tooling with runtime components. The following table clarifies which components are present at build time only vs at runtime on the router.

| Component | Build-time only | Runtime (on router) |
|-----------|-----------------|---------------------|
| OpenWrt buildroot (`make`) | Yes | No |
| Cross-compiler (`$(TARGET_CC)`) | Yes | No |
| `cmake`, `autoconf`, `pkg-config` | Yes (during build) | No |
| `opkg` (package manager) | No | Yes |
| `uci` CLI | No | Yes |
| `procd` init | No | Yes |
| `rpcd` | No | Yes |
| `uhttpd` | No | Yes |
| LuCI JavaScript | No (served as static files) | Yes (runs in browser) |
| ucode interpreter | No | Yes |
| `/etc/config/` files | No | Yes (runtime config) |
| `/usr/share/rpcd/acl.d/` | No | Yes (ACL enforcement) |

**Key implication:** Build tools (`cmake`, `autoconf`) are not available on the router and must not be referenced in runtime scripts. Runtime tools (`uci`, `opkg`) are not available during the buildroot build and must not be called from `Makefile` build steps.

## ACL and Permission Boundaries

rpcd ACL files live at `/usr/share/rpcd/acl.d/<plugin>.json`. They must be installed by the package to declare which rpcd methods the LuCI session is allowed to call.

**ACL file format:**

```json
{
    "myservice": {
        "description": "My Service management",
        "read": {
            "ubus": {
                "myservice": ["get_config", "get_status"]
            }
        },
        "write": {
            "ubus": {
                "myservice": ["set_config"]
            }
        }
    }
}
```

**Common ACL mistakes:**
- Missing ACL file causes silent permission failure -- rpcd returns an empty result, not an error message
- Overly broad ACL (e.g., `"*"` wildcard) violates least-privilege
- ACL file not included in Package/install causes config to work in dev but fail on deployed image

## Data Flow Example: LuCI Form Save

Step-by-step trace of a user submitting a settings form:

1. User submits a LuCI form in the browser
2. JavaScript view's `handleSaveApply()` calls `L.rpc.call('myservice', 'set_config', {...})`
3. Browser sends POST to `http://router/ubus` (uhttpd endpoint)
4. uhttpd proxies the JSON-RPC request to rpcd
5. rpcd checks the session token and verifies ACL: does this session have write permission for `myservice.set_config`?
6. If permitted, rpcd dispatches to the registered ucode plugin at `/usr/share/rpcd/exec.d/myservice.uc`
7. Ucode plugin calls `uci.set(...)` + `uci.commit(...)`
8. UCI writes the change to `/etc/config/myservice`
9. Plugin optionally signals service reload: `/etc/init.d/myservice reload`
10. procd receives the reload signal and restarts or reconfigures the service instance

## Complete Working Example

A minimal rpcd ucode plugin that reads and writes a UCI value:

```javascript
// /usr/share/rpcd/exec.d/myplugin.uc
'use strict';
import { cursor } from 'uci';

return {
    get_config: {
        call: function() {
            let c = cursor();
            return {
                port: c.get('mypkg', 'config', 'port') ?? '8080'
            };
        }
    },
    set_config: {
        args: { port: 'port' },
        call: function(params) {
            if (!params.port) return { error: 'missing port' };
            let c = cursor();
            c.set('mypkg', 'config', 'port', String(params.port));
            c.commit('mypkg');
            return {};
        }
    }
};
```

ACL file for the above (`/usr/share/rpcd/acl.d/mypkg.json`):

```json
{
    "mypkg": {
        "description": "My Package management",
        "read": {
            "ubus": { "mypkg": ["get_config"] }
        },
        "write": {
            "ubus": { "mypkg": ["set_config"] }
        }
    }
}
```

## Step-by-Step Explanation

- `import { cursor } from 'uci'` -- loads the UCI module; not `require("luci.model.uci")`
- `c.get(pkg, section, option)` -- returns string value or null; never throws on missing option
- `val ?? 'default'` -- safe null coercion for JSON serialization
- `c.commit(pkg)` -- **required** -- stages-only without commit do not persist across reboots
- `params.port` -- rpcd passes the `args`-declared parameters; always validate before use
- Return value is JSON-serialized by rpcd and delivered back to the LuCI JavaScript view

## Anti-Patterns

### WRONG: Calling uci CLI via shell from inside ucode

```javascript
// Spawns a subprocess -- slow, fragile, returns string not typed value
let val = fs.popen("uci get mypkg.config.port").read("all").trim();
```

### CORRECT: Use the native ucode uci module

```javascript
import { cursor } from 'uci';
let c = cursor();
let val = c.get('mypkg', 'config', 'port') ?? '8080';
```

---

### WRONG: Missing uci.commit()

```javascript
// Change is staged but never written to disk
c.set('mypkg', 'config', 'port', '9090');
// forgot: c.commit('mypkg');
```

### CORRECT

```javascript
c.set('mypkg', 'config', 'port', '9090');
c.commit('mypkg');  // required -- persists the change
```

---

### WRONG: rpcd plugin without an ACL file

```javascript
// Plugin works in dev (running as root directly) but silently fails in production Lu CI
// because no /usr/share/rpcd/acl.d/mypkg.json exists
```

### CORRECT

Install an ACL file in `Package/mypkg/install`:

```makefile
define Package/mypkg/install
    $(INSTALL_DIR) $(1)/usr/share/rpcd/acl.d
    $(INSTALL_DATA) ./files/mypkg.json $(1)/usr/share/rpcd/acl.d/
    $(INSTALL_DIR) $(1)/usr/share/rpcd/exec.d
    $(INSTALL_DATA) ./files/mypkg.uc $(1)/usr/share/rpcd/exec.d/
endef
```

## Related Topics

- [OpenWrt Era Guide](./openwrt-era-guide.md)
- [Common AI Mistakes](./common-ai-mistakes.md)

## Verification Notes

- Component relationships verified against: ucode, procd, uci, and luci corpus files in `openwrt-condensed-docs/L2-semantic/`
- ACL boundary description: verified against rpcd documentation in luci corpus; `/usr/share/rpcd/acl.d/` path confirmed
- Build-time vs runtime table: build tooling presence verified against openwrt-core corpus; runtime component presence verified against procd and uci corpus
- ucode import pattern (`import { cursor } from 'uci'`): verified against ucode corpus module docs
- Reviewed by: placeholder
- Last reviewed: 2026-03-23
- Known limitation: ubus layer is referenced but not detailed here; inter-component IPC via ubus is out of scope for this overview
