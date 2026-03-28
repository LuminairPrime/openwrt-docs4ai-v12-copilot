---
title: OpenWrt Era Guide
module: cookbook
origin_type: authored
token_count: 2653
source_file: L1-raw/cookbook/openwrt-era-guide.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_locator: content/cookbook-source/openwrt-era-guide.md
description: Reference for identifying which OpenWrt era (legacy, transitional, or
  current) a given pattern belongs to, so AI tools produce era-appropriate recommendations.
era_status: current
when_to_use: Use when you need to verify whether a pattern, API, or package script
  is current-era OpenWrt (23.x+) or belongs to a legacy/transitional era.
related_modules:
- procd
- uci
- ucode
- luci
- wiki
- openwrt-core
verification_basis: Corpus review of procd, uci, ucode, and luci modules; cbi.js and
  form.js API presence in luci corpus; procd corpus init-script patterns
reviewed_by: placeholder
last_reviewed: '2026-03-23'
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

- [OpenWrt Architecture Overview](./architecture-overview.md)
- [Common AI Mistakes](./common-ai-mistakes.md)

## Verification Notes

- Init script patterns: verified against `openwrt-condensed-docs/L2-semantic/procd/` corpus files; `USE_PROCD=1` and `procd_open_instance` present in corpus
- LuCI JS API: `form.Map`, `view.extend` verified against `openwrt-condensed-docs/L2-semantic/luci/js_source-api-form.md` and `js_source-api-luci.md`; `cbi.js` present in corpus as `js_source-api-cbi.md` (CBI compatibility layer confirming legacy pattern still in tree)
- ucode UCI cursor: verified against `openwrt-condensed-docs/L2-semantic/ucode/` corpus; `import { cursor } from 'uci'` pattern present in ucode API docs
- `PKG_HASH` vs `PKG_MD5SUM`: verified against openwrt-core and wiki corpus files
- Reviewed by: placeholder
- Last reviewed: 2026-03-23
- Known limitation: exact version dates for era transitions are approximate; precise commit-level evidence from upstream git history is pending external research
