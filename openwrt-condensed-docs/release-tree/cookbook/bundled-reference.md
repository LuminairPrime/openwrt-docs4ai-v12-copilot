---
module: cookbook
total_token_count: 18852
section_count: 7
is_monolithic: true
generated: '2026-03-27T07:16:53.127109+00:00'
---

# cookbook Bundled Reference

> **Contains:** 7 documents concatenated
> **Tokens:** ~18852 (cl100k_base)

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

ucode is NOT Node.js. It does not have `require()`, `Buffer`, `process`, or browser globals. See [Common AI Mistakes](./chunked-reference/common-ai-mistakes.md) for the full list of ucode/Node.js confusion patterns.

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

- [OpenWrt Era Guide](./chunked-reference/openwrt-era-guide.md)
- [Common AI Mistakes](./chunked-reference/common-ai-mistakes.md)

## Verification Notes

- Component relationships verified against: ucode, procd, uci, and luci corpus files in `openwrt-condensed-docs/L2-semantic/`
- ACL boundary description: verified against rpcd documentation in luci corpus; `/usr/share/rpcd/acl.d/` path confirmed
- Build-time vs runtime table: build tooling presence verified against openwrt-core corpus; runtime component presence verified against procd and uci corpus
- ucode import pattern (`import { cursor } from 'uci'`): verified against ucode corpus module docs
- Reviewed by: placeholder
- Last reviewed: 2026-03-23
- Known limitation: ubus layer is referenced but not detailed here; inter-component IPC via ubus is out of scope for this overview

---

# Common AI Mistakes in OpenWrt Development

> **When to use:** Use when reviewing AI-generated OpenWrt init scripts, Makefile fragments, UCI calls, LuCI views, or ucode plugins -- to identify and correct era-mismatched or structurally incorrect patterns before deployment.
> **Key components:** procd, UCI, ucode, package Makefiles, LuCI, network config
> **Era:** Current (23.x+). Patterns labeled [WRONG](../cookbook/chunked-reference/uci-read-write-from-ucode.md) are common in AI output trained on generic Linux resources or older OpenWrt examples.

## Overview

Large language models trained on the broad web learn a mix of generic Linux, legacy OpenWrt, and current OpenWrt patterns without reliable era discrimination. The result is code that looks plausible but uses deprecated init-system hooks, incorrect UCI call sites, generic Linux package managers that do not exist on OpenWrt, or network configuration APIs that have been superseded by DSA.

This page catalogs seven recurring mistake categories with concrete [WRONG](../cookbook/chunked-reference/uci-read-write-from-ucode.md)/[CORRECT](../cookbook/chunked-reference/uci-read-write-from-ucode.md) pairs. Each mistake is grounded in actual reference material from the OpenWrt corpus rather than speculation.

## Mistake 1: Era Confusion -- Lua CBI Instead of JavaScript LuCI View

AI tools frequently generate Lua CBI model files when asked to create a LuCI settings page. Lua CBI was the pre-2019 pattern; modern LuCI uses JavaScript views with `LuCI.form`.

### WRONG

```lua
-- luci/model/cbi/myservice.lua  <- this file layout doesn't exist in modern LuCI
local m = Map("myservice", translate("My Service"))
local s = m:section(TypedSection, "config", translate("Config"))
local o = s:option(Value, "port", translate("Port"))
o.datatype = "port"
return m
```

### CORRECT

```javascript
// luci/controller/myservice.js  (view file path in modern LuCI)
'use strict';
'require view';
'require form';

return view.extend({
    render: function() {
        let m = new form.Map('myservice', _('My Service'));
        let s = m.section(form.TypedSection, 'config');
        s.option(form.Value, 'port', _('Port')).datatype = 'port';
        return m.render();
    }
});
```

**Why it fails:** Modern LuCI does not execute Lua at runtime. The `luci/model/cbi/` file path convention belongs to the Lua era. See [OpenWrt Era Guide](./chunked-reference/openwrt-era-guide.md) for full context.

---

## Mistake 2: Language Confusion -- Node.js/Browser APIs in Ucode

AI tools confuse ucode with Node.js or browser JavaScript and generate code using `require()` (Node.js CommonJS), `Buffer`, `process.env`, `fetch()`, or `window`. Ucode is a distinct language with its own stdlib.

### WRONG

```javascript
// ucode is NOT Node.js
const fs = require('fs');                  // Node.js -- does not exist
const data = fs.readFileSync('/tmp/x');    // Node.js -- does not exist
process.exit(1);                           // Node.js -- does not exist
```

### CORRECT

```javascript
// ucode stdlib
'use strict';
import { open } from 'fs';

let f = open('/tmp/x', 'r');
if (!f) die('Cannot open file');
let data = f.read('all');
f.close();
```

**Why it fails:** Ucode uses `import` with named module specifiers (`'fs'`, `'uci'`, `'uloop'`), not `require()`. There is no `process`, `Buffer`, or browser global in ucode. See `../../ucode/chunked-reference/` for available modules.

---

## Mistake 3: Network Stack Confusion -- swconfig Instead of DSA

AI tools generate `swconfig` commands or UCI `switch` sections for modern target devices. Most current OpenWrt targets use DSA (Distributed Switch Architecture) and configure bridges through standard `ip`/`bridge` commands or UCI `network` sections with `device` objects.

### WRONG

```sh
# swconfig is absent on DSA-based targets
swconfig dev switch0 vlan 1 set ports "0 1 2 3 5t"
swconfig dev switch0 set apply
```

```uci
# Legacy UCI switch section -- absent on DSA targets
config switch
    option name switch0
    option reset 1
config switch_vlan
    option device switch0
    option vlan 1
    option ports "0 1 2 3 5t"
```

### CORRECT

```uci
# DSA-based network config using bridge devices (current pattern)
config device
    option name br-lan
    option type bridge
    list ports eth0
    list ports eth1

config interface lan
    option device br-lan
    option proto static
    option ipaddr 192.168.1.1
    option netmask 255.255.255.0
```

**Why it fails:** DSA targets expose each physical port as a named netdev (e.g., `lan1`, `lan2`); the `switch0` device and `swconfig` utility are absent. Generating swconfig config for a DSA target produces a no-op or an error. Check device-specific docs before assuming switch architecture.

---

## Mistake 4: Filesystem Assumptions -- Writing Directly to /etc/

AI tools generate code that writes to `/etc/myapp.conf` or creates new files under `/etc/`. On squashfs+overlay OpenWrt systems, `/etc/` is a union mount. Direct writes persist only in the overlay layer and can be lost on firmware upgrade without explicit backup handling.

### WRONG

```sh
# Writing arbitrary config to /etc/ -- bypasses UCI, lost on sysupgrade
cat > /etc/myapp.conf << EOF
port=8080
debug=1
EOF
```

```javascript
// ucode -- writing to /etc/ directly
import { open } from 'fs';
let f = open('/etc/myapp.conf', 'w');
f.write('port=8080\n');
f.close();
```

### CORRECT

```sh
# Use UCI for persistent config -- survives sysupgrade if listed in /etc/sysupgrade.conf
uci set myapp.config.port=8080
uci commit myapp
```

```uci
# /etc/config/myapp -- managed by UCI, backed up by sysupgrade
config config 'config'
    option port '8080'
    option debug '0'
```

**Why it fails:** UCI-managed config files under `/etc/config/` are automatically included in sysupgrade backups. Arbitrary `/etc/` files are not unless explicitly listed. Use UCI for all persistent application config.

---

## Mistake 5: Package Manager Confusion -- apt/yum/pip Instead of opkg

AI tools generating installation or dependency instructions use apt-get, yum, or pip, none of which exist on OpenWrt. OpenWrt uses `opkg`.

### WRONG

```sh
apt-get install curl         # not available
yum install wget             # not available
pip install requests         # not available
npm install -g typescript    # not available
```

### CORRECT

```sh
opkg update
opkg install curl
opkg install wget
```

**Why it fails:** OpenWrt uses a purpose-built package manager (`opkg`) with its own feed infrastructure. Standard Linux package managers and language-specific package managers are absent. Python packages must be installed as OpenWrt-built `.ipk` packages, not via pip.

---

## Mistake 6: Init System Confusion -- systemctl/service Instead of procd

AI tools generate `systemctl enable`, `systemctl start`, or `service restart` commands. OpenWrt uses procd, not systemd.

### WRONG

```sh
systemctl enable myservice    # systemd -- not available
systemctl start myservice     # systemd -- not available
service myservice restart     # SysVinit -- not available
```

### WRONG init script

```sh
#!/bin/sh /etc/rc.common
START=95
start() {
    /usr/sbin/myservice &
}
stop() {
    killall myservice
}
```

### CORRECT

```sh
# Enable at boot
/etc/init.d/myservice enable
# Start immediately
/etc/init.d/myservice start
# Reload
/etc/init.d/myservice reload
```

### CORRECT init script

```sh
#!/bin/sh /etc/rc.common
USE_PROCD=1
START=95
start_service() {
    procd_open_instance
    procd_set_param command /usr/sbin/myservice
    procd_set_param respawn
    procd_close_instance
}
```

**Why it fails:** OpenWrt uses procd as its init system and service supervisor. systemd is not present. See [OpenWrt Era Guide](./chunked-reference/openwrt-era-guide.md) for procd patterns.

---

## Mistake 7: Build System Confusion -- Standard cmake/make Instead of OpenWrt Buildroot

AI tools generate standalone `cmake`/`make` build configurations or standard `./configure && make install` workflows. OpenWrt packages must be built inside the OpenWrt buildroot using its Makefile DSL.

### WRONG

```makefile
# Standard cmake package -- does not work inside OpenWrt buildroot
cmake_minimum_required(VERSION 3.10)
project(myservice)
add_executable(myservice main.c)
install(TARGETS myservice DESTINATION /usr/sbin)
```

```sh
# Standard install -- wrong outside of buildroot context
./configure --prefix=/usr
make
make install
```

### CORRECT

```makefile
include $(TOPDIR)/rules.mk

PKG_NAME:=myservice
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_SOURCE_URL:=https://github.com/example/myservice/archive/refs/tags/v$(PKG_VERSION).tar.gz
PKG_HASH:=<sha256sum>

include $(INCLUDE_DIR)/package.mk

define Package/myservice
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=My Service
endef

define Build/Configure
endef

define Build/Compile
$(TARGET_MAKE_FLAGS) $(MAKE) -C $(PKG_BUILD_DIR)
endef

define Package/myservice/install
$(INSTALL_DIR) $(1)/usr/sbin
$(INSTALL_BIN) $(PKG_BUILD_DIR)/myservice $(1)/usr/sbin/
endef

$(eval $(call BuildPackage,myservice))
```

**Why it fails:** The OpenWrt buildroot cross-compiles packages for the target architecture. It provides `$(TARGET_CC)`, `$(STAGING_DIR)`, and other variables that standard cmake/make workflows do not use. Packages must use `$(INCLUDE_DIR)/package.mk` and the `BuildPackage` macro.

---

## Related Topics

- [OpenWrt Era Guide](./chunked-reference/openwrt-era-guide.md)
- [OpenWrt Architecture Overview](./chunked-reference/architecture-overview.md)

## Verification Notes

- Mistake 1 (era confusion): LuCI form.js and cbi.js both present in `openwrt-condensed-docs/L2-semantic/luci/`; Lua CBI is the compatibility path, form.js is current
- Mistake 2 (language confusion): ucode fs module documented in `openwrt-condensed-docs/L2-semantic/ucode/` corpus; Node.js-style `require()` absent
- Mistake 3 (network stack): swconfig/DSA distinction noted in wiki and openwrt-core corpus files
- Mistake 4 (filesystem): UCI config file pattern verified against uci corpus; squashfs overlay behavior documented in wiki corpus
- Mistake 5 (package manager): opkg documented in wiki corpus; apt/yum/pip absence verified by absence in corpus
- Mistake 6 (init system): procd `USE_PROCD=1` pattern verified against procd corpus; systemd absence confirmed
- Mistake 7 (build system): OpenWrt Makefile DSL pattern verified against openwrt-core corpus files
- Reviewed by: placeholder
- Last reviewed: 2026-03-23
- Known limitation: DSA vs swconfig guidance is target-dependent; always check the specific device wiki page before assuming DSA

---

# LuCI Form with UCI

> **When to use:** Use when building a LuCI settings page that reads and writes configuration stored in `/etc/config/`. The correct pattern uses a JavaScript view with `form.Map` — LuCI handles the UCI binding automatically for simple forms. For more complex backend logic, pair the form with an rpcd ucode plugin.
> **Key components:** LuCI JavaScript view, form.Map, rpcd, ucode, UCI, ACL
> **Era:** Current (23.x+). Lua CBI model files (`.lua` under `luci/model/cbi/`) are the wrong approach for any new code. See [Common AI Mistakes](./chunked-reference/common-ai-mistakes.md) §Mistake 1 for the CBI anti-pattern.

## Overview

A LuCI settings page has two layers:

1. **The view** — a JavaScript file that defines the form structure. `form.Map` binds the form to a UCI config file. LuCI's RPC system handles the read/write to UCI automatically when the form uses direct UCI binding.
2. **The backend** (optional for simple forms) — an rpcd ucode plugin that exposes named RPC methods for operations the form cannot express as pure UCI reads/writes (computed state, cross-config operations, service control).

For a form that simply reads and writes a single config file, only the JavaScript view is required. LuCI's `form.Map` handles UCI read (`uci.load`) and UCI write (`uci.set` + `uci.commit`) automatically when the form is saved. The ACL file for the config file must grant read and write access to the LuCI session.

For a form that also calls service actions (start/stop/reload) or reads computed state (interface status, running processes), add an rpcd plugin alongside the view.

This guide covers both cases.

## Part 1: Simple Form — JavaScript View Only

### Complete Working Example (view)

```javascript
// htdocs/luci-static/resources/view/myapp/settings.js
'use strict';
'require view';
'require form';

// view.extend creates a new view object with a render() method.
// LuCI calls render() when the page loads.
return view.extend({
    render: function() {
        let m, s, o;

        // form.Map binds the form to the UCI config file 'myapp'
        // which maps to /etc/config/myapp on disk.
        // Arguments: config_name, title, description
        m = new form.Map('myapp', _('My Application'), _('Configure My Application.'));

        // form.TypedSection creates a form section bound to UCI sections of
        // type 'main'. anonymous = true means the section has no UCI title shown.
        s = m.section(form.TypedSection, 'main', _('General Settings'));
        s.anonymous = true;
        // addremove = false means users cannot add or remove sections from this form.
        s.addremove = false;

        // A simple text input bound to the UCI option 'host' in section 'main'.
        // Arguments: option_type, uci_option_name, label, description
        o = s.option(form.Value, 'host', _('Host'), _('Server hostname or IP address'));
        o.placeholder = '203.0.113.1';
        // datatype validates input before save; see LuCI form.Value docs for all types
        o.datatype = 'host';

        // A numeric input for a port option.
        o = s.option(form.Value, 'port', _('Port'), _('Server port'));
        o.datatype = 'port';
        o.placeholder = '8080';

        // form.Flag is a checkbox. The 'enabled' option is written as '0' or '1'.
        o = s.option(form.Flag, 'enabled', _('Enable'), _('Enable the service'));
        o.default = o.disabled;  // default off
        o.rmempty = false;       // always write this option even if at default value

        // form.ListValue is a select dropdown.
        o = s.option(form.ListValue, 'loglevel', _('Log Level'));
        o.value('error', _('Error'));
        o.value('warn', _('Warning'));
        o.value('info', _('Info'));
        o.value('debug', _('Debug'));
        o.default = 'warn';

        // m.render() returns a Promise<Node> -- LuCI awaits this internally.
        // Always return m.render() as the last statement.
        return m.render();
    }
});
```

### ACL file for the simple form

```json
{
  "luci-app-myapp": {
    "description": "myapp LuCI application",
    "read": {
      "uci": ["myapp"]
    },
    "write": {
      "uci": ["myapp"]
    }
  }
}
```

Place this file at:
```
root/usr/share/rpcd/acl.d/luci-app-myapp.json
```

The file name must match the rpcd session permission name used by the LuCI login session (by convention, `luci-app-<pkgname>`). Without this ACL file, LuCI will silently fail to save the form — the `uci.set` calls will be rejected by rpcd's permission check with no visible error in the UI.

### Package install snippet

```makefile
define Package/luci-app-myapp/install
    $(INSTALL_DIR) $(1)/usr/lib/lua/luci/view/myapp
    $(INSTALL_DATA) ./htdocs/luci-static/resources/view/myapp/settings.js \
        $(1)/htdocs/luci-static/resources/view/myapp/settings.js
    $(INSTALL_DIR) $(1)/usr/share/luci/menu.d
    $(INSTALL_DATA) ./root/usr/share/luci/menu.d/luci-app-myapp.json \
        $(1)/usr/share/luci/menu.d/luci-app-myapp.json
    $(INSTALL_DIR) $(1)/usr/share/rpcd/acl.d
    $(INSTALL_DATA) ./root/usr/share/rpcd/acl.d/luci-app-myapp.json \
        $(1)/usr/share/rpcd/acl.d/luci-app-myapp.json
endef
```

## Part 2: Form with rpcd Backend

When the form needs to trigger service actions or read computed state, add an rpcd ucode plugin. The view calls the plugin methods using `rpc.declare()`.

### rpcd ucode plugin

```ucode
// root/usr/share/rpcd/ucode/myapp.uc
'use strict';
import { cursor } from 'uci';

const uci = cursor();

const methods = {
    // get_status: returns runtime state that cannot come from UCI alone.
    // LuCI calls this method via rpc.declare() when the view loads.
    get_status: {
        call: function() {
            const enabled = uci.get('myapp', 'main', 'enabled') ?? '0';
            // In a real implementation, check if the process is running
            // via procd, pidfile, or similar mechanism.
            const running = (enabled === '1');
            uci.unload('myapp');
            return { enabled, running };
        }
    },

    // apply_config: receive changes from the form and commit them.
    // This wraps the UCI write + service reload in one atomic call.
    apply_config: {
        args: { host: '', port: '0', enabled: '0' },
        call: function(req) {
            uci.set('myapp', 'main', 'host', req.args.host);
            uci.set('myapp', 'main', 'port', req.args.port);
            uci.set('myapp', 'main', 'enabled', req.args.enabled);
            const ok = uci.commit('myapp');
            uci.unload('myapp');
            return { result: ok ? 'ok' : 'error' };
        }
    }
};

// The key 'luci.myapp' is the RPC namespace used in rpc.declare() calls.
return { 'luci.myapp': methods };
```

### JavaScript view with RPC calls

```javascript
// htdocs/luci-static/resources/view/myapp/settings.js
'use strict';
'require view';
'require form';
'require rpc';

// Declare the RPC method. The object sent to rpc.declare() maps to the
// rpcd method defined in the ucode plugin.
const callGetStatus = rpc.declare({
    object: 'luci.myapp',  // must match the key in return { 'luci.myapp': methods }
    method: 'get_status',
    expect: { '': {} }    // expect an object; fallback to {} on null response
});

return view.extend({
    // load() is called before render(). Return a Promise (or array of Promises)
    // whose resolved values are passed as arguments to render().
    load: function() {
        return callGetStatus();
    },

    render: function(status) {
        // status is the resolved value from callGetStatus()
        let m, s, o;

        m = new form.Map('myapp', _('My Application'));

        s = m.section(form.TypedSection, 'main', _('General Settings'));
        s.anonymous = true;
        s.addremove = false;

        o = s.option(form.Value, 'host', _('Host'));
        o.datatype = 'host';

        o = s.option(form.Value, 'port', _('Port'));
        o.datatype = 'port';

        o = s.option(form.Flag, 'enabled', _('Enable'));
        o.rmempty = false;

        // Add a read-only field showing computed runtime state from RPC.
        // This cannot come from UCI (UCI only stores config, not runtime state).
        o = s.option(form.DummyValue, '_running', _('Running'));
        o.cfgvalue = function() {
            return status.running ? _('Yes') : _('No');
        };

        return m.render();
    }
});
```

### Extended ACL for the rpcd plugin

```json
{
  "luci-app-myapp": {
    "description": "myapp LuCI application",
    "read": {
      "uci": ["myapp"]
    },
    "write": {
      "uci": ["myapp"]
    },
    "exec": {
      "ucode": ["/usr/share/rpcd/ucode/myapp.uc"]
    }
  }
}
```

## Anti-Patterns

### WRONG: Lua CBI model file

```lua
-- luci/model/cbi/myapp.lua (WRONG -- this file path does not exist in modern LuCI)
local m = Map("myapp", translate("My Application"))
local s = m:section(TypedSection, "main")
return m
```

**Why it fails:** Modern LuCI does not execute Lua at runtime. The `luci/model/cbi/` path convention does not exist in the JavaScript LuCI era. See [Common AI Mistakes](./chunked-reference/common-ai-mistakes.md) for the full explanation.

### WRONG: Missing ACL file

Creating a form.Map and a ucode plugin but forgetting the ACL file causes silent save failures. The UI form appears to work — the Save button is clickable, LuCI shows no error — but the configuration is never written to disk because rpcd's permission check fails and LuCI does not surface the denial to the user.

**Why it fails:** rpcd enforces the ACL before allowing any `uci` operation from a LuCI session. No ACL entry = no write permission = silent no-op.

### CORRECT: Always ship the ACL file with the package

The ACL file must be:
1. Named `luci-app-<pkgname>.json`
2. Placed at `root/usr/share/rpcd/acl.d/` in the source tree
3. Installed via `Package/install` to `/usr/share/rpcd/acl.d/`
4. Granted both `read` and `write` access to every UCI config file the form touches

### WRONG: Calling rpc.declare without load()

```javascript
// Calling an RPC method directly in render() instead of load():
return view.extend({
    render: function() {
        callGetStatus().then(function(status) {
            // This runs AFTER render() returns -- the DOM is already built
            // and you cannot update it from here without manually touching elements.
        });
    }
});
```

**Why it fails:** `rpc.declare()` returns an async function. The result is not available synchronously. LuCI's view lifecycle provides `load()` specifically to fetch async data before `render()` is called. Put all RPC/network calls in `load()`, return the Promises, and receive the resolved values as parameters in `render()`.

## Quick Reference: form option types

| Type | UCI storage | Use for |
|------|------------|---------|
| `form.Value` | string | Text input, hostnames, paths |
| `form.Flag` | '0' / '1' | Checkboxes, boolean options |
| `form.ListValue` | string | Select dropdown with fixed choices |
| `form.DynamicList` | list (array) | Multi-value UCI lists |
| `form.TextValue` | string | Multi-line text area |
| `form.DummyValue` | n/a | Read-only display, computed values |
| `form.TypedSection` | section | Groups options by UCI section type |
| `form.GridSection` | section | Table view for multiple sections |

## Related Topics

- [UCI Read/Write from ucode](./chunked-reference/uci-read-write-from-ucode.md) — the cursor API used in the rpcd backend
- [Architecture Overview](./chunked-reference/architecture-overview.md) — full ACL format and placement, rpcd permission model
- [Common AI Mistakes](./chunked-reference/common-ai-mistakes.md) — Lua CBI vs JavaScript form anti-pattern
- [luci-app-example form.js](../luci-examples/chunked-reference/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md) — real-world reference implementation from LuCI upstream

## Verification Notes

- `form.Map`, `form.TypedSection`, `form.Value`, `form.Flag`, `form.ListValue`, `form.DynamicList`, `view.extend`, `m.render()` verified from `luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md`
- `rpc.declare({ object, method, expect })` pattern verified from `luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-rpc-js.md`
- rpcd ucode plugin return format `return { 'luci.name': methods }` verified from `luci-examples/example.uc`
- ACL JSON format (`read.uci`, `write.uci`) verified from `luci-examples/example_app-luci-app-example-root-usr-share-rpcd...` and architecture-overview.md
- `load()` + `render(data)` lifecycle is standard LuCI view pattern; confirmed from luci-examples

---

# Minimal OpenWrt Package Makefile

> **When to use:** Use when adding a new compiled package (C application, daemon, or utility) to the OpenWrt build system. The OpenWrt build system uses a custom Makefile DSL that wraps cross-compilation, staging, and image inclusion. Generic `cmake ..`, `./configure && make`, or `pip install` instructions from upstream software do not work in this environment.
> **Key components:** OpenWrt build system, package Makefile, cross-compiler
> **Era:** Current (23.x+). `PKG_MD5SUM` is deprecated — use `PKG_HASH` with SHA-256.

## Overview

OpenWrt packages each piece of software in a Makefile that lives under `package/<category>/<name>/Makefile`. The Makefile uses a set of macros from `$(INCLUDE_DIR)/package.mk` that abstract the cross-compilation environment: source download, patching, configure, compile, staging, and image installation. The build system is not GNU Make as normally used — it has its own variable conventions, macro expansion order, and implicit targets.

AI tools frequently produce incorrect OpenWrt Makefiles because they blend generic GNU Make syntax, CMake patterns, or Debian `debian/rules` conventions into the output. All three are wrong in this context. The correct pattern is declarative: define the required variables and the `Package/install` target, then let the build system handle the rest.

This guide shows the minimal correct Makefile for a C application downloaded from a source tarball. A `cmake`-based variant is included as an anti-pattern comparison.

## Complete Working Example

```makefile
# package/utils/myapp/Makefile
# Minimal correct OpenWrt package Makefile for a C application.

include $(TOPDIR)/rules.mk

# ── Package metadata ────────────────────────────────────────────────────────

PKG_NAME:=myapp
PKG_VERSION:=1.2.3
PKG_RELEASE:=1

# Source tarball: the build system downloads this from PKG_SOURCE_URL.
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://example.com/releases/

# SHA-256 checksum of the downloaded tarball.
# Use PKG_HASH, not PKG_MD5SUM (deprecated since 18.x).
PKG_HASH:=abc123def456...  # replace with actual sha256sum of the tarball

# Where the source extracts to under $(BUILD_DIR).
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

# Upstream project homepage (for package metadata, not for downloading).
PKG_URL:=https://example.com/myapp

# SPDX license identifier (required for upstream acceptance).
PKG_LICENSE:=GPL-2.0-or-later
PKG_LICENSE_FILES:=LICENSE

include $(INCLUDE_DIR)/package.mk

# ── Package definition ───────────────────────────────────────────────────────

# Package/<name> defines the package metadata shown in menuconfig and ipkg.
define Package/myapp
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=My application
  URL:=$(PKG_URL)
  # Runtime dependencies: other packages that must be installed for myapp to run.
  # Use the package name (e.g., libuci), not the directory name (e.g., uci).
  DEPENDS:=+libc +libuci
endef

define Package/myapp/description
  My application does something useful on OpenWrt.
  Replace this description with one sentence about what the package does.
endef

# ── Build ────────────────────────────────────────────────────────────────────

# If the upstream uses a standard autoconf/automake chain:
#   Build/Configure is provided automatically by package.mk.
#   Build/Compile is provided automatically by package.mk.
# Override only if you need to pass non-standard flags.

define Build/Configure
  $(call Build/Configure/Default, \
    --disable-nls \
    --without-libcap \
  )
endef

# Build/Compile calls make in the build dir with the cross-compiler toolchain.
# The CROSS_COMPILE, CC, CXX, AR, RANLIB, CFLAGS etc. variables are
# injected by the build system -- do not set them manually.
define Build/Compile
  $(MAKE) -C $(PKG_BUILD_DIR) \
    $(TARGET_CONFIGURE_OPTS) \
    CFLAGS="$(TARGET_CFLAGS)" \
    all
endef

# ── Install ──────────────────────────────────────────────────────────────────

# Package/install copies files into the image staging root ($(1)).
# $(1) is the package staging dir -- files placed here end up in the image.
# Use INSTALL_DIR, INSTALL_BIN, INSTALL_CONF macros -- not raw cp/mkdir commands.
define Package/myapp/install
    # Create the target directory in the staging root
    $(INSTALL_DIR) $(1)/usr/bin

    # Install the compiled binary with executable permissions (755)
    $(INSTALL_BIN) $(PKG_BUILD_DIR)/myapp $(1)/usr/bin/myapp

    # Install a default config file with non-executable permissions (644)
    $(INSTALL_DIR) $(1)/etc/config
    $(INSTALL_CONF) ./files/myapp.conf $(1)/etc/config/myapp

    # Install the init script (executable, goes to /etc/init.d/)
    $(INSTALL_DIR) $(1)/etc/init.d
    $(INSTALL_BIN) ./files/myapp.init $(1)/etc/init.d/myapp
endef

# ── Evaluation ───────────────────────────────────────────────────────────────

# This line must be the last line of the Makefile.
# It registers the package with the build system.
$(eval $(call BuildPackage,myapp))
```

Supporting files referenced in the Makefile above:

```
package/utils/myapp/
├── Makefile               # this file
├── files/
│   ├── myapp.conf         # default UCI config, installed to /etc/config/myapp
│   └── myapp.init         # procd init script, installed to /etc/init.d/myapp
└── patches/               # optional: patches applied to the source tree before Build/Configure
    └── 001-fix-cast.patch
```

## Step-by-Step Explanation

### Required variables

| Variable | Purpose |
|----------|---------|
| `PKG_NAME` | Package name in menuconfig and ipkg. Avoid underscores. |
| `PKG_VERSION` | Upstream version. Reset `PKG_RELEASE` to 1 when this changes. |
| `PKG_RELEASE` | Package Makefile version. Increment on Makefile-only changes. |
| `PKG_SOURCE` | Filename of the source tarball. |
| `PKG_SOURCE_URL` | Download URL directory. The build system appends `PKG_SOURCE`. |
| `PKG_HASH` | SHA-256 of the tarball. Required for integrity checking. |
| `PKG_LICENSE` | SPDX identifier — required for upstream submissions. |

### `include $(TOPDIR)/rules.mk` and `include $(INCLUDE_DIR)/package.mk`

These two includes are mandatory and must appear in this order. `rules.mk` sets up the toolchain variables. `package.mk` provides the default `Build/Configure`, `Build/Compile`, and `Build/Install` implementations plus the `BuildPackage` macro.

### `Package/<name>` define block

This block sets the metadata visible in `make menuconfig`. `SECTION` and `CATEGORY` control where the package appears in the menu. `DEPENDS` lists runtime package dependencies using `+<package>` syntax. Build-time dependencies use `PKG_BUILD_DEPENDS` at the top level.

### `$(TARGET_CONFIGURE_OPTS)` and `$(TARGET_CFLAGS)`

These variables are injected by the build system and contain the cross-compiler prefix, compiler flags for the target architecture, sysroot paths, etc. **Do not hardcode these values** — the build system sets them correctly for the selected target.

### `$(1)` in `Package/install`

`$(1)` refers to the package staging directory, which is a path under `$(BUILD_DIR)/packages/`. Files placed here are collected by the image builder. Paths within `$(1)` map directly to the target filesystem: `$(1)/usr/bin/myapp` becomes `/usr/bin/myapp` in the image.

### `INSTALL_BIN`, `INSTALL_CONF`, `INSTALL_DIR`

These macros set the correct permissions automatically:
- `INSTALL_DIR`: creates directory with mode 0755
- `INSTALL_BIN`: installs file with mode 0755 (executables, init scripts)
- `INSTALL_CONF`: installs file with mode 0600 (config files)
- `INSTALL_DATA`: installs file with mode 0644 (data files, read-only)

### `$(eval $(call BuildPackage,myapp))`

This mandatory last line registers the package with the build system. Without it, `make menuconfig` will not show the package and the build system will not know to build it.

## Anti-Patterns

### WRONG: Using cmake/make directly

```makefile
# DO NOT DO THIS
build:
    cmake -DCMAKE_BUILD_TYPE=Release .
    make -j4
    make install
```

**Why it fails:** `cmake` runs on the **host** machine. It uses the host compiler, not the cross-compiler for the target architecture (e.g., `mipsel-openwrt-linux-musl-gcc`). The resulting binary will not run on the router. Cross-compilation requires the `$(TARGET_CONFIGURE_OPTS)` injection that only the OpenWrt build system provides.

### CORRECT: Let package.mk handle cross-compilation

```makefile
define Build/Compile
  $(MAKE) -C $(PKG_BUILD_DIR) \
    $(TARGET_CONFIGURE_OPTS) \
    CFLAGS="$(TARGET_CFLAGS)"
endef
```

For cmake-based upstreams, use the cmake [package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include instead:

```makefile
include $(INCLUDE_DIR)/cmake.mk
# Build/Configure and Build/Compile are now handled automatically.
```

### WRONG: PKG_MD5SUM instead of PKG_HASH

```makefile
PKG_MD5SUM:=d41d8cd98f00b204e9800998ecf8427e  # DO NOT USE
```

**Why it fails:** `PKG_MD5SUM` was deprecated in 18.x. MD5 is insufficient for integrity checking. The build system will emit a warning and may reject the package in CI. Use `PKG_HASH` with the SHA-256 checksum.

### CORRECT: PKG_HASH with SHA-256

```sh
# Generate the hash:
sha256sum myapp-1.2.3.tar.gz
```

```makefile
PKG_HASH:=a665a45920422f9d417e4867efdc4fb8a04a1f3755fc5fd10a4b5e76c36b3d9c
```

### WRONG: Raw mkdir/cp in Package/install

```makefile
define Package/myapp/install
    mkdir -p $(1)/usr/bin
    cp $(PKG_BUILD_DIR)/myapp $(1)/usr/bin/
endef
```

**Why it fails:** `mkdir -p` and `cp` do not set the correct permissions for the OpenWrt image format. Files installed with wrong permissions may fail sysupgrade signature checks or behave incorrectly on read-only overlays.

## Related Topics

- [procd Service Lifecycle](./chunked-reference/procd-service-lifecycle.md) — how to write the init script installed by Package/install
- [Architecture Overview](./chunked-reference/architecture-overview.md) — where packages fit in the build and runtime stack
- [OpenWrt Era Guide](./chunked-reference/openwrt-era-guide.md) — PKG_HASH vs PKG_MD5SUM era distinction
- [Wiki: Creating packages](../wiki/chunked-reference/wiki_page-guide-developer-packages.md) — full reference for all Makefile variables

## Verification Notes

- Makefile variable names (`PKG_NAME`, `PKG_HASH`, `PKG_RELEASE`, etc.) verified against `wiki/wiki_page-guide-developer-packages.md` in corpus
- `PKG_MD5SUM` deprecated status confirmed from same wiki page
- `INSTALL_BIN`, `INSTALL_CONF`, `INSTALL_DATA`, `INSTALL_DIR` macro names verified from wiki packages guide
- `$(TARGET_CONFIGURE_OPTS)` usage verified from wiki corpus build examples
- `$(eval $(call BuildPackage,...))` as mandatory last line confirmed from wiki packages guide

---

# OpenWrt Era Guide

> **When to use:** Use when you need to determine whether a given build pattern, init script, LuCI view, or package API belongs to a legacy, transitional, or current OpenWrt era.
> **Key components:** procd, UCI, LuCI, ucode, package Makefiles, init.d scripts
> **Era:** This page documents all eras; recommendations favor current (23.x/24.x) practice.

## Version Target Statement

**This guide targets current OpenWrt development in the 23.x/24.x family.**

If you are targeting a specific released version earlier than 21.02, some patterns described as "current" here may not be available. If you are modifying existing code written for an older release, check the era marker table first to understand what you are working with before updating patterns.

This guide must be reviewed and updated when the project changes its supported-current release family.

## Overview

OpenWrt has evolved through several eras with meaningfully different patterns for service management, package scripting, configuration access, and web UI development. AI tools trained on the broad web frequently conflate these eras: particularly the Lua-era LuCI patterns (pre-2019) with the current JavaScript-based LuCI, and the sysvinit-style init scripts with the current procd model.

This guide records the boundary events and pattern markers that distinguish legacy OpenWrt from the current era. It exists so that cookbook content can make explicit era claims and so AI consumers can calibrate their pattern selection before generating code.

The primary era boundaries are:

1. **procd adoption** -- displaced sysvinit-style init scripts; stable by ~18.06
2. **JavaScript LuCI rewrite** -- displaced Lua CBI and Lua MVC views; major rewrite landed in ~2019 and became dominant by 21.02
3. **ucode as preferred scripting language** -- displaced Lua for rpcd plugins and UCI manipulation; stabilized by 22.03

## Era Reference Table

| Area | Current (23.x+) | Deprecated (do NOT use) | Transitional era |
|------|-----------------|-------------------------|------------------|
| LuCI web views | JavaScript `view.extend({...})` with `LuCI.form.Map` | Lua CBI / SimpleForm / Map (Lua) | JS `cbi.js` compatibility shim (still in tree) |
| Scripting language | ucode with `import { cursor } from 'uci'` | Lua (`luci.model.uci`, `require "luci.*"`) | Lua scripts still work but not recommended |
| Init system | procd (`USE_PROCD=1`, `start_service()`, `service_triggers()`) | sysvinit-style `start()`/`stop()` in `/etc/init.d/` | Mixed scripts with both styles |
| Config access (script) | ucode `uci` module (`cursor()`, `get()`, `set()`, `commit()`) | `luci.model.uci` (Lua), or shell `uci` from within ucode | Shell `uci` CLI acceptable if not inside ucode |
| Package checksums | `PKG_HASH` (SHA-256 in Makefile) | `PKG_MD5SUM` | -- |
| JSON handling | Native ucode JSON / `jsonfilter` for shell | `luci.jsonc` (Lua) | -- |

## Era Markers and Regex Detectors

The following patterns can be detected programmatically to identify legacy code.

### Legacy markers (do not use in new code)

```
# init script without procd
grep -l "^start()" /etc/init.d/*
grep -rn "require \"luci\." .
grep -rn "luci.model.uci" .
grep -rn "LuCI.cbi.Map\|cbi.Map\b" .
grep -rn "PKG_MD5SUM" .
```

Signs:
- `/etc/init.d/` scripts with `start()` / `stop()` functions and no `USE_PROCD=1`
- Lua files importing `luci.*` namespaces (e.g., `require "luci.model.cbi"`)
- CBI forms using Lua `Map`, `SimpleForm`, `AbstractSection` from Lua
- `PKG_MD5SUM` in a package Makefile

### Transitional markers (use only for compatibility maintenance)

```
grep -rn "LuCI.cbi\b" .           # JS cbi.js compatibility shim
grep -rn "#!/usr/bin/lua" .
```

Signs:
- Use of `LuCI.cbi` JS module (exists in tree as compatibility layer; prefer `LuCI.form`)
- Mixed init scripts that include both `start()` and `start_service()` functions

### Current markers (prefer these in all new code)

```
grep -n "USE_PROCD=1" /etc/init.d/$pkg
grep -rn "view.extend\|LuCI.view" .
grep -rn "form.Map\|LuCI.form" .
grep -rn "import { cursor } from .uci." .
grep -n "PKG_HASH :=" Makefile
```

## Complete Working Examples

### Example 1: Current-era procd init script

```sh
#!/bin/sh /etc/rc.common
# Current procd-managed service -- correct era (23.x+)
USE_PROCD=1
START=95
STOP=05

start_service() {
    procd_open_instance
    procd_set_param command /usr/sbin/myservice --config /etc/config/myservice
    procd_set_param respawn               # auto-restart on crash
    procd_set_param file /etc/config/myservice  # restart on config change
    procd_close_instance
}

service_triggers() {
    procd_add_reload_trigger "myservice"  # reload when UCI config changes
}
```

### Example 2: Current-era LuCI JavaScript view

```javascript
'use strict';
'require view';
'require form';

return view.extend({
    render: function() {
        let m, s, o;

        m = new form.Map('myservice', _('My Service'), _('Configure my service'));

        s = m.section(form.TypedSection, 'config');
        s.anonymous = true;

        o = s.option(form.Value, 'listen_port', _('Listen Port'));
        o.datatype = 'port';
        o.placeholder = '8080';

        return m.render();
    }
});
```

### Example 3: Current-era ucode UCI script

```javascript
'use strict';
import { cursor } from 'uci';

let c = cursor();
let port = c.get('myservice', 'config', 'listen_port') ?? '8080';

c.set('myservice', 'config', 'listen_port', '9090');
c.commit('myservice');
```

## Step-by-Step Explanation

**Init script:**
- `USE_PROCD=1` -- required marker; enables procd helper functions in rc.common
- `start_service()` -- called by procd to define and register service instances
- `procd_set_param file` -- triggers service reload when the named file changes
- `service_triggers()` -- called by procd to register UCI config change triggers

**LuCI view:**
- `'require view'` -- imports the current-era base view class
- `'require form'` -- imports `LuCI.form`, the current declarative form framework
- `view.extend({render: ...})` -- defines a view with a `render()` lifecycle method
- `new form.Map('myservice', ...)` -- creates a form bound to the `myservice` UCI package
- `m.section(form.TypedSection, 'config')` -- maps to all sections of type `config`
- `s.option(form.Value, 'listen_port', ...)` -- maps to the `listen_port` UCI option

**ucode:**
- `import { cursor } from 'uci'` -- the current pattern; not `require "luci.model.uci"`
- `c.get(pkg, section, option)` -- returns the string value or null
- `c.commit(pkg)` -- persists changes; **required** -- omitting it leaves changes staged only

## Anti-Patterns

### WRONG: Legacy sysvinit init script

```sh
#!/bin/sh /etc/rc.common
START=95
start() {
    /usr/sbin/myservice &     # bare background process -- no procd supervision
}
stop() {
    killall myservice          # unreliable; ignores PID
}
```

**Why it fails:** procd will not know about the process; no respawn on crash; no config-change triggers.

### CORRECT: Current procd init script

```sh
#!/bin/sh /etc/rc.common
USE_PROCD=1
START=95
start_service() {
    procd_open_instance
    procd_set_param command /usr/sbin/myservice
    procd_set_param respawn
    procd_close_instance
}
```

---

### WRONG: Lua CBI view (deprecated pattern very common in AI output)

```lua
-- luci/model/cbi/myservice.lua  <- this file layout is Lua-era only
local m = Map("myservice", translate("My Service"))
local s = m:section(TypedSection, "config")
local o = s:option(Value, "listen_port", translate("Listen Port"))
return m
```

**Why it fails:** The Lua CBI model file layout and `Map(...)` Lua functions are from the pre-2019 era. Modern LuCI does not execute Lua at runtime.

### CORRECT: Current JavaScript LuCI view

```javascript
'use strict';
'require view';
'require form';
return view.extend({
    render: function() {
        let m = new form.Map('myservice', _('My Service'));
        let s = m.section(form.TypedSection, 'config');
        s.option(form.Value, 'listen_port', _('Listen Port'));
        return m.render();
    }
});
```

---

### WRONG: PKG_MD5SUM in package Makefile

```makefile
PKG_MD5SUM:=abc123                # MD5 is deprecated
```

### CORRECT: PKG_HASH with SHA-256

```makefile
PKG_HASH:=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## When Legacy Code Is Acceptable

Legacy patterns are acceptable in these specific situations:

1. **Modifying an existing Lua-era LuCI application** -- changing an existing Lua CBI module in-place is safer than partially migrating; document the legacy status clearly in comments
2. **Targeting a specific old release** -- if the target device is pinned to OpenWrt 17.01 or 18.06, procd may not support all current API parameters; check the release notes
3. **User explicitly requests legacy compatibility** -- if the user states they need to support both old and new devices, state the trade-off explicitly and provide both forms
4. **Vendor-patched OpenWrt forks** -- some router vendors ship frozen forks that do not track upstream; treat these as an older era until proven otherwise

In all cases, **mark legacy code with a comment explaining the era and why the legacy pattern is used there**.

## Related Topics

- [OpenWrt Architecture Overview](./chunked-reference/architecture-overview.md)
- [Common AI Mistakes](./chunked-reference/common-ai-mistakes.md)

## Verification Notes

- Init script patterns: verified against `openwrt-condensed-docs/L2-semantic/procd/` corpus files; `USE_PROCD=1` and `procd_open_instance` present in corpus
- LuCI JS API: `form.Map`, `view.extend` verified against `openwrt-condensed-docs/L2-semantic/luci/js_source-api-form.md` and `js_source-api-luci.md`; `cbi.js` present in corpus as `js_source-api-cbi.md` (CBI compatibility layer confirming legacy pattern still in tree)
- ucode UCI cursor: verified against `openwrt-condensed-docs/L2-semantic/ucode/` corpus; `import { cursor } from 'uci'` pattern present in ucode API docs
- `PKG_HASH` vs `PKG_MD5SUM`: verified against openwrt-core and wiki corpus files
- Reviewed by: placeholder
- Last reviewed: 2026-03-23
- Known limitation: exact version dates for era transitions are approximate; precise commit-level evidence from upstream git history is pending external research

---

# procd Service Lifecycle

> **When to use:** Use when writing a new `/etc/init.d/` service script on OpenWrt 23.x+. procd is the init system and process supervisor. It replaces sysvinit start/stop/restart patterns with a declarative instance model where the supervisor handles respawn, signals, and config-triggered reloads automatically.
> **Key components:** procd, UCI, bash
> **Era:** Current (23.x+). Sysvinit-style `start-stop-daemon` patterns do not integrate with procd supervision and are not covered here.

## Overview

procd is OpenWrt's init system and process supervisor. Unlike sysvinit, procd manages processes declaratively: you declare a service with its command, environment, and respawn policy, then procd supervises it. The supervisor restarts crashed processes, handles reload signals, and triggers config-aware restarts when UCI configuration changes.

Every `/etc/init.d/` script on a current OpenWrt system uses the procd API via sourcing `/lib/functions.sh` (which transitively loads the procd helper functions). The API is provided by `procd.sh` and exposes a small set of functions for declaring service instances.

The lifecycle is three phases: **start_service** (declare the supervised instance), **stop_service** (optional override; procd handles SIGTERM by default), and **reload_service** or **service_triggers** (UCI-aware reload without full restart).

## Complete Working Example

Below is a complete, annotated procd init script for a hypothetical service called `myapp` that reads config from `/etc/config/myapp` and runs as a dedicated user.

```bash
#!/bin/sh /etc/rc.common
# /etc/init.d/myapp
# USE_PROCD=1 tells rc.common to delegate lifecycle to procd functions
# instead of sysvinit start/stop/restart shims.

USE_PROCD=1

# START and STOP define the boot sequence priority (lower = earlier)
START=95
STOP=01

# start_service() is called by procd when the service should launch.
# procd_open_service / procd_close_service bracket the declaration.
start_service() {
    # Load config from UCI to pass as environment or arguments
    config_load 'myapp'

    local port
    config_get port main port '8080'   # default to 8080 if option not set

    # Open a service declaration for 'myapp'
    procd_open_service myapp

    # Declare one supervised process instance (name defaults to "instance1")
    procd_open_instance

    # Set the command to run. Each argument is a separate array element.
    procd_set_param command /usr/bin/myapp --port "$port"

    # Respawn policy: fail_threshold(s) restart_timeout(s) max_fail
    # If the process fails within 3600s more than 5 times, stop respawning.
    procd_set_param respawn 3600 5 5

    # Redirect stdout and stderr to syslog (facility: daemon)
    procd_set_param stdout 1
    procd_set_param stderr 1

    # Optional: file triggers -- if these files change, procd reload_config
    # will trigger a service reload (used for non-UCI config files)
    # procd_set_param file /etc/myapp/extra.conf

    procd_close_instance
    procd_close_service
}

# service_triggers() declares which UCI config changes trigger a reload.
# When 'uci commit myapp' is run, procd will call reload_service.
service_triggers() {
    procd_add_reload_trigger 'myapp'
}

# reload_service() is called instead of stop/start when a trigger fires.
# Default behavior (omitting this function) is to call stop_service
# then start_service. Override only if you need a graceful in-process
# reload (e.g., sending SIGHUP to reload config without process restart).
reload_service() {
    stop
    start
}
```

## Step-by-Step Explanation

### `USE_PROCD=1`

This flag tells `/etc/rc.common` (the shell shim that backs all init scripts) to use procd delegation mode. Without it, the script uses legacy sysvinit-style `start`/`stop`/`restart` functions. **Always set this flag.** Forgetting it is the single most common procd init script mistake.

### `START` and `STOP`

Boot sequence priorities. `START=95` means this service starts late in the boot sequence (after networking, after UCI defaults have been applied). `STOP=01` means it stops early during shutdown. Adjust these to match your service's dependency order.

### `procd_open_service` / `procd_close_service`

These bracket the full service declaration. The argument to `procd_open_service` is the service name used in `procd_running()` checks and in logread output.

### `procd_open_instance` / `procd_close_instance`

These bracket a single process instance. One service can have multiple instances (e.g., two daemons that together form one logical service). Each instance gets its own supervised process.

### `procd_set_param command`

Sets the command and arguments. Each argument is a **separate shell argument** — no string concatenation or quoting tricks. Incorrect quoting here causes the process to launch with wrong arguments without any shell error.

### `procd_set_param respawn`

The three values are:
- `fail_threshold`: time window in seconds during which failures are counted
- `restart_timeout`: time in seconds between restart attempts
- `max_fail`: maximum failures before supervision is abandoned

Setting `max_fail 0` means infinite restarts. Setting it to 5 means the process is abandoned after 5 failures in the time window.

### `service_triggers` and `procd_add_reload_trigger`

This is the UCI integration point. `procd_add_reload_trigger 'myapp'` means: whenever `uci commit myapp` is called (by any process), procd will call this service's `reload_service` function. Without this, config changes require manual `service myapp restart`.

## Anti-Patterns

### WRONG: sysvinit-style start/stop without USE_PROCD

```bash
#!/bin/sh /etc/rc.common
START=95
STOP=01

start() {
    start-stop-daemon -S -x /usr/bin/myapp -- --port 8080
}

stop() {
    start-stop-daemon -K -x /usr/bin/myapp
}
```

**Why it fails:** This script runs `myapp` as a child of the init script, not under procd supervision. If `myapp` crashes, it is not restarted. If `myapp` is already running when `start` is called, `start-stop-daemon` behavior depends on PID file presence. There is no UCI reload integration. The `/lib/functions.sh` config helpers (`config_load`, `config_get`) are available but the result is a script that runs outside the procd model entirely.

### CORRECT: USE_PROCD with procd_set_param

Use `USE_PROCD=1` and the procd API as shown in the working example above. The key behavioral differences:
- procd tracks the PID and supervises it directly
- crashes trigger automatic respawn per the declared policy
- `service myapp reload` triggers `reload_service` without a full restart
- `procd_running myapp` can check status from other scripts

### WRONG: Hardcoding config values in the command

```bash
procd_set_param command /usr/bin/myapp --port 8080 --host 192.168.1.1
```

**Why it fails:** Config changes require editing the init script. UCI integration is bypassed. The standard OpenWrt pattern is to load config via `config_load` in `start_service` and pass values as environment variables or arguments derived from UCI.

### CORRECT: Load from UCI in start_service

```bash
start_service() {
    config_load 'myapp'
    local port
    config_get port main port '8080'
    procd_open_service myapp
    procd_open_instance
    procd_set_param command /usr/bin/myapp --port "$port"
    # ...
    procd_close_instance
    procd_close_service
}

service_triggers() {
    procd_add_reload_trigger 'myapp'
}
```

## Running user and resource limits

```bash
# Run the service as a non-root user (user must exist on the system)
procd_set_param user nobody
procd_set_param group nogroup

# Optional: set resource limits (ulimit-style)
procd_set_param limits "nofile=1024"
```

Drop privileges by setting `user` and `group` parameters. These are applied before `execve`. The user must exist in `/etc/passwd` on the target image — if it does not exist at boot time, procd will refuse to start the service.

## Related Topics

- [procd API Reference](../procd/chunked-reference/header_api-procd-api.md) — full parameter list for `procd_set_param`
- [OpenWrt Era Guide](./chunked-reference/openwrt-era-guide.md) — init system era context (sysvinit vs procd)
- [UCI Read/Write from ucode](./chunked-reference/uci-read-write-from-ucode.md) — companion guide for config access from ucode plugins
- [Architecture Overview](./chunked-reference/architecture-overview.md) — where procd fits in the full component stack

## Verification Notes

- procd API (`procd_open_service`, `procd_open_instance`, `procd_set_param`, etc.) verified against `procd/header_api-procd-api.md` in corpus
- `procd_add_reload_trigger` function name verified from same source
- `USE_PROCD=1` pattern and `service_triggers` function verified from `wiki/wiki_page-guide-developer-procd-init-scripts.md` file listing
- respawn parameter order (fail_threshold, restart_timeout, max_fail) matches procd corpus documentation

---

# UCI Read/Write from ucode

> **When to use:** Use when writing a ucode script or rpcd plugin that needs to read or write OpenWrt configuration. UCI (`/etc/config/`) is the correct persistent config mechanism on OpenWrt. Reading files in `/etc/config/` directly with `open()` or writing them with string output is fragile, bypasses locking, and does not integrate with `procd_add_reload_trigger`.
> **Key components:** ucode, uci module, cursor API
> **Era:** Current (23.x+). The `cursor()` API wraps libuci and is the standard access mechanism in ucode scripts. Shell-based `uci get` calls from within ucode are never the right approach.

## Overview

OpenWrt's UCI (Unified Configuration Interface) stores all user-editable configuration in structured text files under `/etc/config/`. The ucode `uci` module exposes a `cursor()` API that reads, modifies, and commits these files with proper locking and change batching. Changes made to a cursor are staged in memory until `cursor.commit()` is called — before commit, other processes cannot see the pending changes.

The cursor pattern separates concerns cleanly: `get()` and `foreach()` for reading, `set()` and `delete()` for staging changes, and `commit()` to persist. Always call `commit()` after a write sequence. Always call `unload()` when done with a config file to release the in-memory cache.

This guide covers the four most common operations: reading a single option, iterating sections, writing an option, and adding a new section.

## Complete Working Example

```ucode
#!/usr/bin/env ucode
'use strict';

// Import cursor from the uci module. This is the standard import pattern.
import { cursor } from 'uci';

// ── Reading ──────────────────────────────────────────────────────────────────

// Create a new cursor instance. Each cursor has independent staging state.
const uci = cursor();

// get(config, section, option) -- returns the option value as a string,
// or null if the config/section/option does not exist.
const hostname = uci.get('system', '@system[0]', 'hostname');
print(`hostname: ${hostname}\n`);

// get_first(config, section_type, option) -- shorthand for the common case
// of a single anonymous section. Equivalent to get(config, '@type[0]', opt).
const tz = uci.get_first('system', 'system', 'timezone');
print(`timezone: ${tz}\n`);

// ── Iterating sections ───────────────────────────────────────────────────────

// foreach(config, section_type, callback) -- iterates every section of
// the named type in the config file. The callback receives a section object
// with all option values as properties plus '.name' (the section id).
uci.foreach('network', 'interface', function(section) {
    // section['.name'] is the UCI section id (e.g., 'loopback', 'lan', 'wan')
    const name = section['.name'];
    const proto = section['proto'] ?? 'unset';
    print(`interface ${name}: proto=${proto}\n`);
});

// ── Writing ──────────────────────────────────────────────────────────────────

// set(config, section, option, value) -- stages an option change.
// The change is NOT written to disk until commit() is called.
uci.set('myapp', 'main', 'port', '9090');
uci.set('myapp', 'main', 'enabled', '1');

// Commit the staged changes for the 'myapp' config file.
// Without commit(), the set() calls have no effect on disk.
const ok = uci.commit('myapp');
if (!ok) {
    warn(`uci.commit failed: ${uci.error()}\n`);
    // uci.error() returns a description of the last error, or null if no error.
}

// ── Adding a new section ─────────────────────────────────────────────────────

// add(config, section_type) -- creates a new anonymous section and returns
// the generated section id (e.g., 'cfg01234a').
const sid = uci.add('myapp', 'server');

// Set options on the new section using the returned id.
uci.set('myapp', sid, 'host', '203.0.113.1');
uci.set('myapp', sid, 'port', '443');

uci.commit('myapp');

// ── Cleanup ───────────────────────────────────────────────────────────────────

// unload() releases the cached state for a config file.
// Call it when you are done with a config to free memory.
// If you call get() again after unload(), it re-reads from disk.
uci.unload('system');
uci.unload('myapp');
```

## Step-by-Step Explanation

### Importing cursor

```ucode
import { cursor } from 'uci';
const uci = cursor();
```

`cursor` is a factory function, not a class. It returns a cursor object. Always use named import syntax (`import { cursor } from 'uci'`). The cursor has its own in-memory state — staged changes from one cursor are not visible to other cursor instances until `commit()` writes to disk.

### `uci.get(config, section, option)`

The three-argument form directly addresses a known named section and option. Returns the value as a string (or array of strings for UCI list options), or `null` if not found — never throws.

The `@type[0]` syntax addresses anonymous sections by type and index. `@system[0]` is the first section of type `system` in the `system` config file. This is the standard way to access single-section config files like `/etc/config/system`.

### `uci.get_first(config, type, option)`

Shorthand that is equivalent to `uci.get(config, '@type[0]', option)`. Use this for config files that always have exactly one section of the given type.

### `uci.foreach(config, type, callback)`

Iterates all sections of `type` in `config`. The callback receives a plain object with all option names as keys plus the special key `.name` (the section identifier). If `type` is `null`, iterates all sections regardless of type.

### `uci.set(config, section, option, value)`

Stages an in-memory change. The section must already exist — to create a new section, use `uci.add()` first. `value` can be a string (for options) or an array of strings (for UCI lists). Staged changes are private to this cursor until `commit()`.

### `uci.commit(config)`

Writes all staged changes for `config` to disk. Returns `true` on success, `false` on failure. On failure, `uci.error()` returns a description. **Always check the return value from commit**; write failures to `/etc/config/` can occur on read-only overlayfs under certain conditions.

### `uci.unload(config)`

Releases the in-memory cache for `config`. If you call `uci.get()` after `unload()`, the cursor re-reads from disk, picking up changes made by other processes since the last read. Always unload after a write sequence to keep memory usage bounded.

## Anti-Patterns

### WRONG: Reading /etc/config/ with open()

```ucode
// DO NOT DO THIS
import { open } from 'fs';
const f = open('/etc/config/myapp', 'r');
const content = f.read('all');
f.close();
// ...parse UCI text format manually
```

**Why it fails:** UCI files are not simple key=value text. The format has named sections, anonymous sections, type declarations, and list syntax that must be parsed correctly. Direct file reads bypass UCI's locking mechanism, meaning concurrent `uci commit` from another process can produce torn reads. Use `cursor().get()` instead.

### CORRECT: Read with cursor

```ucode
import { cursor } from 'uci';
const uci = cursor();
const value = uci.get('myapp', 'main', 'option');
uci.unload('myapp');
```

### WRONG: Writing config with shell UCI calls from ucode

```ucode
// DO NOT DO THIS
import { popen } from 'fs';
popen(`uci set myapp.main.port=${port}`, 'r');
popen('uci commit myapp', 'r');
```

**Why it fails:** Spawning a shell process for each UCI operation is expensive (fork + exec for every call). It also bypasses transaction semantics — if a set succeeds but the commit process fails to spawn, the config is partially written. The cursor API batches all changes in memory and writes atomically on commit.

### CORRECT: Use cursor set + commit

```ucode
import { cursor } from 'uci';
const uci = cursor();
uci.set('myapp', 'main', 'port', port);
uci.commit('myapp');
```

### WRONG: Forgetting commit()

```ucode
import { cursor } from 'uci';
const uci = cursor();
uci.set('myapp', 'main', 'enabled', '1');
// Missing: uci.commit('myapp');
// The change is lost when the cursor object is garbage collected.
```

**Why it fails:** `set()` is a staging operation. Without `commit()`, no bytes are written to disk. The configuration appears to succeed (no error is returned from `set()`) but the change does not survive process exit.

## Using uci in an rpcd plugin

In an rpcd ucode plugin, the cursor pattern is the same but code lives inside method call handlers:

```ucode
'use strict';
import { cursor } from 'uci';

const uci = cursor();

const methods = {
    get_config: {
        call: function() {
            const port = uci.get('myapp', 'main', 'port') ?? '8080';
            const enabled = uci.get('myapp', 'main', 'enabled') ?? '0';
            uci.unload('myapp');
            return { port, enabled };
        }
    },

    set_port: {
        args: { port: '0' },  // declares expected argument with type hint
        call: function(req) {
            uci.set('myapp', 'main', 'port', req.args.port);
            const ok = uci.commit('myapp');
            uci.unload('myapp');
            return { result: ok ? 'ok' : 'error', error: ok ? null : uci.error() };
        }
    }
};

return { 'luci.myapp': methods };
```

The ACL file for this plugin must grant `uci` write access to the `myapp` config:

```json
{
  "luci-app-myapp": {
    "description": "My application LuCI access",
    "read": { "uci": ["myapp"] },
    "write": { "uci": ["myapp"] }
  }
}
```

See [Architecture Overview](./chunked-reference/architecture-overview.md) §ACL for the ACL file placement and format.

## Related Topics

- [ucode UCI module reference](../ucode/chunked-reference/c_source-api-module-uci.md) — full cursor API with all method signatures
- [LuCI Form with UCI](./chunked-reference/luci-form-with-uci.md) — how the browser form save triggers a ucode plugin that calls this pattern
- [Architecture Overview](./chunked-reference/architecture-overview.md) — where the ucode/rpcd/UCI layer fits in the full stack
- [procd Service Lifecycle](./chunked-reference/procd-service-lifecycle.md) — `service_triggers` / `procd_add_reload_trigger` for UCI-driven service reload

## Verification Notes

- `cursor()` factory function import syntax verified from `ucode/c_source-api-module-uci.md`
- `get(config, section, option)`, `get_first()`, `foreach()`, `set()`, `commit()`, `unload()`, `add()`, `error()` all verified from ucode UCI module corpus
- `@type[0]` anonymous section syntax verified from ucode module docs
- `import { cursor } from 'uci'` as standard import pattern confirmed from luci-examples corpus (`example.uc`)
- rpcd plugin return format (`return { 'luci.myapp': methods }`) confirmed from `example_app-luci-app-example-root-usr-share-rpcd-ucode-example-uc.md`
