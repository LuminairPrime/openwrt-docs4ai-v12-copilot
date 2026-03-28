---
title: Common AI Mistakes in OpenWrt Development
module: cookbook
origin_type: authored
token_count: 2833
source_file: L1-raw/cookbook/common-ai-mistakes.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_locator: content/cookbook-source/common-ai-mistakes.md
description: Documents seven recurring categories of era-mismatched or API-incorrect
  patterns that AI tools produce when generating OpenWrt code, with WRONG/CORRECT
  pairs for each.
era_status: current
when_to_use: Use when reviewing AI-generated OpenWrt code or prompting an AI tool,
  to check output against known failure categories.
related_modules:
- procd
- uci
- ucode
- luci
- wiki
- openwrt-core
verification_basis: Patterns sourced from procd, uci, ucode, and luci corpus review;
  swconfig/DSA distinction from wiki corpus; package path conventions from openwrt-core
  corpus
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---
# Common AI Mistakes in OpenWrt Development

> **When to use:** Use when reviewing AI-generated OpenWrt init scripts, Makefile fragments, UCI calls, LuCI views, or ucode plugins -- to identify and correct era-mismatched or structurally incorrect patterns before deployment.
> **Key components:** procd, UCI, ucode, package Makefiles, LuCI, network config
> **Era:** Current (23.x+). Patterns labeled `WRONG` are common in AI output trained on generic Linux resources or older OpenWrt examples.

## Overview

Large language models trained on the broad web learn a mix of generic Linux, legacy OpenWrt, and current OpenWrt patterns without reliable era discrimination. The result is code that looks plausible but uses deprecated init-system hooks, incorrect UCI call sites, generic Linux package managers that do not exist on OpenWrt, or network configuration APIs that have been superseded by DSA.

This page catalogs seven recurring mistake categories with concrete `WRONG`/`CORRECT` pairs. Each mistake is grounded in actual reference material from the OpenWrt corpus rather than speculation.

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
// htdocs/luci-static/resources/view/myservice/settings.js
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

**Why it fails:** Modern LuCI does not execute Lua at runtime. The `luci/model/cbi/` file path convention belongs to the Lua era. See [OpenWrt Era Guide](./openwrt-era-guide.md) for full context.

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

**Why it fails:** OpenWrt uses procd as its init system and service supervisor. systemd is not present. See [OpenWrt Era Guide](./openwrt-era-guide.md) for procd patterns.

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

- [OpenWrt Era Guide](./openwrt-era-guide.md)
- [OpenWrt Architecture Overview](./architecture-overview.md)

## Deep-Dive Follow-Up Pages

- [First-Boot uci-defaults Pattern](./firstboot-uci-defaults-pattern.md)
- [First-Boot Wi-Fi Policy](./firstboot-wifi-policy.md)
- [Hotplug Handler Pattern](./hotplug-handler-pattern.md)
- [ucode rpcd Service Pattern](./ucode-rpcd-service-pattern.md)
- [ubus Observability Pattern](./ubus-observability-pattern.md)
- [Inter-Component Communication Map](./inter-component-communication-map.md)
- [Runtime Device Identity via ubus](./runtime-device-identity-via-ubus.md)
- [LuCI uhttpd HTTPS and Auth Pattern](./luci-uhttpd-https-auth.md)
- [Package Config Bootstrap Pattern](./package-config-bootstrap-pattern.md)
- [Network Device Model Migrations](./network-device-model-migrations.md)

## Verification Notes

- Mistake 1 (era confusion): LuCI form.js and cbi.js both present in `openwrt-condensed-docs/L2-semantic/luci/`; Lua CBI is the compatibility path, form.js is current
- Mistake 2 (language confusion): ucode fs module documented in `openwrt-condensed-docs/L2-semantic/ucode/` corpus; Node.js-style `require()` absent
- Mistake 3 (network stack): swconfig/DSA distinction noted in wiki and openwrt-core corpus files
- Mistake 4 (filesystem): UCI config file pattern verified against uci corpus; squashfs overlay behavior documented in wiki corpus
- Mistake 5 (package manager): opkg documented in wiki corpus; apt/yum/pip absence verified by absence in corpus
- Mistake 6 (init system): procd `USE_PROCD=1` pattern verified against procd corpus; systemd absence confirmed
- Mistake 7 (build system): OpenWrt Makefile DSL pattern verified against openwrt-core corpus files
- Reviewed by: placeholder
- Last reviewed: 2026-03-28
- Known limitation: DSA vs swconfig guidance is target-dependent; always check the specific device wiki page before assuming DSA
