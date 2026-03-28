---
title: LuCI Form with UCI
module: cookbook
origin_type: authored
token_count: 3159
source_file: L1-raw/cookbook/luci-form-with-uci.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_locator: content/cookbook-source/luci-form-with-uci.md
description: End-to-end guide to creating a LuCI settings page that reads and writes
  UCI configuration, covering the JavaScript view, form.Map binding, rpcd plugin,
  ACL file, and the complete request flow from browser to disk.
era_status: current
when_to_use: Use when writing a new LuCI settings page that lets users edit configuration
  stored in /etc/config/. This pattern requires a JavaScript view (form.Map), an rpcd
  ucode backend (for non-UCI-direct writes), and an ACL file. A Lua CBI model file
  is the wrong approach.
related_modules:
- luci
- luci-examples
- ucode
- uci
verification_basis: Corpus review of luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md;
  example_app-luci-app-example-root-usr-share-rpcd-ucode-example-uc.md; luci/js_source-api-form.md;
  architecture-overview.md ACL section
reviewed_by: placeholder
last_reviewed: '2026-03-23'
---

> **Source:** `content/cookbook-source/luci-form-with-uci.md`
> **Kind:** authored | **Method:** hand-authored
> **Normalized:** 2026-03-28

# LuCI Form with UCI

> **When to use:** Use when building a LuCI settings page that reads and writes configuration stored in `/etc/config/`. The correct pattern uses a JavaScript view with `form.Map` — LuCI handles the UCI binding automatically for simple forms. For more complex backend logic, pair the form with an rpcd ucode plugin.
> **Key components:** LuCI JavaScript view, form.Map, rpcd, ucode, UCI, ACL
> **Era:** Current (23.x+). Lua CBI model files (`.lua` under `luci/model/cbi/`) are the wrong approach for any new code. See [Common AI Mistakes](./common-ai-mistakes.md) §Mistake 1 for the CBI anti-pattern.

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

**Why it fails:** Modern LuCI does not execute Lua at runtime. The `luci/model/cbi/` path convention does not exist in the JavaScript LuCI era. See [Common AI Mistakes](./common-ai-mistakes.md) for the full explanation.

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

- [UCI Read/Write from ucode](./uci-read-write-from-ucode.md) — the cursor API used in the rpcd backend
- [Architecture Overview](./architecture-overview.md) — full ACL format and placement, rpcd permission model
- [Common AI Mistakes](./common-ai-mistakes.md) — Lua CBI vs JavaScript form anti-pattern
- [luci-app-example form.js](../../luci-examples/chunked-reference/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md) — real-world reference implementation from LuCI upstream

## Verification Notes

- `form.Map`, `form.TypedSection`, `form.Value`, `form.Flag`, `form.ListValue`, `form.DynamicList`, `view.extend`, `m.render()` verified from `luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md`
- `rpc.declare({ object, method, expect })` pattern verified from `luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-rpc-js.md`
- rpcd ucode plugin return format `return { 'luci.name': methods }` verified from `luci-examples/example.uc`
- ACL JSON format (`read.uci`, `write.uci`) verified from `luci-examples/example_app-luci-app-example-root-usr-share-rpcd...` and architecture-overview.md
- `load()` + `render(data)` lifecycle is standard LuCI view pattern; confirmed from luci-examples
