# Beta Batch Answer Key — Sonnet 4.6

**Batch:** 01b-batch-slice-beta.md
**Evaluator:** Claude Sonnet 4.6
**Scenarios:** 02, 04, 08, 11, 12, 17

---

## Scenario 02 — uCode Network Interface Listing

**PASS criteria:** Must use `import * as ubus from 'ubus'` and `ubus.conn()` natively.

**Canonical Answer:**
```js
#!/usr/bin/ucode

import * as ubus from 'ubus';

const conn = ubus.connect();
if (!conn) {
    die('Failed to connect to ubus');
}

const ifaces = conn.call('network.interface', 'dump', {});
if (!ifaces || !ifaces.interface) {
    die('Failed to get interface list');
}

const result = {};
for (const iface of ifaces.interface) {
    const ipv4 = iface['ipv4-address'];
    result[iface.interface] = {
        device: iface.l3_device || iface.device,
        ip4addr: ipv4 && ipv4.length ? ipv4[0].address : null,
        up: iface.up,
    };
}

print(result);

conn.close();
```

**Pattern Notes:**
- `import * as ubus from 'ubus'` — this exact import form is required.
- `ubus.connect()` creates the connection. Do NOT call `ubus` as a subprocess.
- `conn.call(object, method, params)` is the native ubus RPC call from ucode.
- Using a shell `ubus call network.interface dump | jsonfilter` pattern is a Falseness.
- Using raw `ip addr`, `/sys/class/net/`, or `ifconfig` is a Falseness.

---

## Scenario 04 — LuCI JS Dynamic Firewall Form

**PASS criteria:** Must use `luci.view` architecture, `L.ui`, `form.Map`, and widgets like `form.ListValue` or `widgets.NetworkSelect`.

**Canonical Answer:**
```js
'use strict';
'require view';
'require form';
'require ui';
'require widgets';

return view.extend({
    render: function() {
        const m = new form.Map('firewall', _('Firewall Zone Settings'));
        const s = m.section(form.NamedSection, 'zone1', 'zone', _('Zone'));

        const o1 = s.option(form.ListValue, 'input', _('Input Policy'));
        o1.value('ACCEPT', _('Accept'));
        o1.value('REJECT', _('Reject'));
        o1.value('DROP', _('Drop'));

        // Dynamic interface selector using LuCI widget
        const o2 = s.option(widgets.NetworkSelect, 'network', _('Network Interface'));
        o2.multiple = false;

        L.ui.addNotification(null, E('p', _('Configure firewall zone settings below.')));

        return m.render();
    }
});
```

**Pattern Notes:**
- `view.extend` is the entry point for all LuCI JS views.
- `form.Map` binds to a UCI package. Do NOT use raw `<form>` HTML elements.
- `widgets.NetworkSelect` dynamically fetches available network interfaces from the system — no manual `fetch()` calls.
- `L.ui` is required when adding notifications or performing UI-level actions.
- Lua CBI (`m = Map(...)`) is a Falseness for all new development.

---

## Scenario 08 — uCode UCI Modification

**PASS criteria:** Must use `import * as uci from 'uci'`, `cursor.set()`, `cursor.save()`, and `cursor.commit()`.

**Canonical Answer:**
```js
#!/usr/bin/ucode

import * as uci from 'uci';

const cursor = uci.cursor();
cursor.set('network', 'lan', 'ipaddr', '10.10.10.1');
cursor.save('network');
cursor.commit('network');

print('Network LAN IP updated successfully.\n');
```

**Pattern Notes:**
- `import * as uci from 'uci'` — this exact import form is required.
- `cursor.set(package, section, option, value)` modifies the in-memory value.
- `cursor.save(package)` writes to the run-time staging files (but not flash).
- `cursor.commit(package)` flushes to flash storage permanently.
- Appending text directly to `/etc/config/network` via `fs.open()` is a Falseness.

---

## Scenario 11 — C Package Makefile

**PASS criteria:** Must include `$(TOPDIR)/rules.mk`, `$(INCLUDE_DIR)/package.mk`, and `DEPENDS:=+libubus`.

**Canonical Answer:**
```makefile
include $(TOPDIR)/rules.mk

PKG_NAME:=my_app
PKG_VERSION:=1.0.0
PKG_RELEASE:=1

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

define Package/my_app
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=My Custom Application
  DEPENDS:=+libubus
endef

define Package/my_app/description
  A custom application that communicates over the OpenWrt system bus.
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)"
endef

define Package/my_app/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/my_app $(1)/usr/bin/
endef

$(eval $(call BuildPackage,my_app))
```

**Pattern Notes:**
- `include $(TOPDIR)/rules.mk` must be first.
- `include $(INCLUDE_DIR)/package.mk` provides the build infrastructure.
- `DEPENDS:=+libubus` is the canonical runtime dependency declaration for ubus-linked programs.
- `PKG_MD5SUM` is deprecated — use `PKG_HASH` for source integrity.
- A standard `gcc` Makefile without OpenWrt cross-compile boilerplate is a Falseness.

---

## Scenario 12 — C uloop + ubus Daemon Skeleton

**PASS criteria:** Must call `uloop_init()`, `ubus_connect()`, `ubus_add_uloop()`, and `uloop_run()` in that order.

**Canonical Answer:**
```c
#include <libubus.h>
#include <libubox/uloop.h>

int main(void)
{
    struct ubus_context *ctx;

    /* 1. Initialize the event loop FIRST */
    uloop_init();

    /* 2. Connect to ubus */
    ctx = ubus_connect(NULL);
    if (!ctx) {
        fprintf(stderr, "Failed to connect to ubus\n");
        return 1;
    }

    /* 3. Register ubus connection with the event loop */
    ubus_add_uloop(ctx);

    /* 4. Block in the event loop — this is the correct replacement for sleep() loops */
    uloop_run();

    /* Cleanup (only reached on uloop_end() or signal) */
    ubus_free(ctx);
    uloop_done();

    return 0;
}
```

**Pattern Notes:**
- **Order is strict:** `uloop_init()` → `ubus_connect()` → `ubus_add_uloop()` → `uloop_run()`.
- `ubus_add_uloop(ctx)` binds the ubus socket into the event loop. Without it, the event loop runs but ubus calls are never received.
- `uloop_run()` is the blocking main loop. Using `while(1) { sleep(1); }` is a Falseness.
- `uloop_done()` / `ubus_free()` for cleanup after receiving a termination signal.

---

## Scenario 17 — uCode Conceptual Description

**PASS criteria:** Must identify ucode as a lightweight JavaScript-like language replacing Lua in modern OpenWrt.

**Canonical Answer:**
ucode is a lightweight scripting language developed specifically for OpenWrt. It was created to replace Lua as the primary scripting language for the LuCI web UI and other OpenWrt components, offering JavaScript-like syntax while being natively compiled to bytecode for efficient execution in memory-constrained embedded environments.

Key characteristics:
- **JavaScript-like syntax** — familiar to modern developers, unlike Lua's unusual conventions.
- **Native C integration** — modules like `ubus`, `uci`, `fs`, `uloop` provide direct access to OpenWrt subsystems without subprocess overhead.
- **Replaces Lua** — LuCI views are now written in ucode/JavaScript rather than Lua CBI.
- **Ideal for** — UCI config management, ubus interaction, hotplug handlers, LuCI view logic, async network tasks via `uloop`.

**Pattern Notes:**
- ucode is NOT a general-purpose language unrelated to OpenWrt.
- ucode is NOT a unicode encoding or text processing utility.
- Claiming Lua is the "modern flagship" or describing ucode as an "alternative" rather than a "replacement" is a Falseness.
