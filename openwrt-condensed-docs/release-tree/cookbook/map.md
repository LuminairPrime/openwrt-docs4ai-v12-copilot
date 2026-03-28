# cookbook Navigation Map

> **Contains:** Headers and function signatures for cookbook.
> **Generated:** 2026-03-27T20:02:56.666251+00:00

---

> **Summary:** Structural overview of OpenWrt component relationships, data flow, ACL/permission boundaries, and build-time vs runtime distinctions for AI tools and developers building on the platform.
# OpenWrt Architecture Overview
## Overview
## Component Map (Runtime)
## Component Map (Simplified)
## Component Descriptions
### procd


### UCI (Unified Configuration Interface)
### rpcd
### ucode
### uhttpd
### LuCI
## Build-Time vs Runtime Components
## ACL and Permission Boundaries

## Data Flow Example: LuCI Form Save
## Complete Working Example
## Step-by-Step Explanation



## Anti-Patterns
### WRONG: Calling uci CLI via shell from inside ucode
### CORRECT: Use the native ucode uci module
### WRONG: Missing uci.commit()
### CORRECT
### WRONG: rpcd plugin without an ACL file
### CORRECT
## Related Topics
## Verification Notes


> **Summary:** Documents seven recurring categories of era-mismatched or API-incorrect patterns that AI tools produce when generating OpenWrt code, with WRONG/CORRECT pairs for each.
# Common AI Mistakes in OpenWrt Development
## Overview
## Mistake 1: Era Confusion -- Lua CBI Instead of JavaScript LuCI View
### WRONG
### CORRECT
## Mistake 2: Language Confusion -- Node.js/Browser APIs in Ucode
### WRONG
### CORRECT
## Mistake 3: Network Stack Confusion -- swconfig Instead of DSA
### WRONG
# swconfig is absent on DSA-based targets
# Legacy UCI switch section -- absent on DSA targets
### CORRECT
# DSA-based network config using bridge devices (current pattern)
## Mistake 4: Filesystem Assumptions -- Writing Directly to /etc/
### WRONG
# Writing arbitrary config to /etc/ -- bypasses UCI, lost on sysupgrade
### CORRECT
# Use UCI for persistent config -- survives sysupgrade if listed in /etc/sysupgrade.conf
# /etc/config/myapp -- managed by UCI, backed up by sysupgrade
## Mistake 5: Package Manager Confusion -- apt/yum/pip Instead of opkg
### WRONG
### CORRECT
## Mistake 6: Init System Confusion -- systemctl/service Instead of procd
### WRONG
### WRONG init script
#!/bin/sh /etc/rc.common
### CORRECT
# Enable at boot
# Start immediately
# Reload
### CORRECT init script
#!/bin/sh /etc/rc.common
## Mistake 7: Build System Confusion -- Standard cmake/make Instead of OpenWrt Buildroot
### WRONG
# Standard cmake package -- does not work inside OpenWrt buildroot
# Standard install -- wrong outside of buildroot context
### CORRECT
## Related Topics
## Verification Notes







> **Summary:** End-to-end guide to creating a LuCI settings page that reads and writes UCI configuration, covering the JavaScript view, form.Map binding, rpcd plugin, ACL file, and the complete request flow from browser to disk.
# LuCI Form with UCI
## Overview
## Part 1: Simple Form — JavaScript View Only
### Complete Working Example (view)
### ACL file for the simple form
### Package install snippet
## Part 2: Form with rpcd Backend
### rpcd ucode plugin
### JavaScript view with RPC calls
### Extended ACL for the rpcd plugin
## Anti-Patterns
### WRONG: Lua CBI model file
### WRONG: Missing ACL file
### CORRECT: Always ship the ACL file with the package
### WRONG: Calling rpc.declare without load()
## Quick Reference: form option types
## Related Topics
## Verification Notes


> **Summary:** Annotated minimal Makefile for packaging a C program in OpenWrt, covering the required variables, Build/Compile, Package/install, and the correct PKG_HASH vs PKG_MD5SUM distinction.
# Minimal OpenWrt Package Makefile
## Overview
## Complete Working Example
# package/utils/myapp/Makefile
# Minimal correct OpenWrt package Makefile for a C application.
# ── Package metadata ────────────────────────────────────────────────────────
# Source tarball: the build system downloads this from PKG_SOURCE_URL.
# SHA-256 checksum of the downloaded tarball.
# Use PKG_HASH, not PKG_MD5SUM (deprecated since 18.x).
# Where the source extracts to under $(BUILD_DIR).
# Upstream project homepage (for package metadata, not for downloading).
# SPDX license identifier (required for upstream acceptance).
# ── Package definition ───────────────────────────────────────────────────────
# Package/<name> defines the package metadata shown in menuconfig and ipkg.
# ── Build ────────────────────────────────────────────────────────────────────
# If the upstream uses a standard autoconf/automake chain:
#   Build/Configure is provided automatically by package.mk.
#   Build/Compile is provided automatically by package.mk.
# Override only if you need to pass non-standard flags.
# Build/Compile calls make in the build dir with the cross-compiler toolchain.
# The CROSS_COMPILE, CC, CXX, AR, RANLIB, CFLAGS etc. variables are
# injected by the build system -- do not set them manually.
# ── Install ──────────────────────────────────────────────────────────────────
# Package/install copies files into the image staging root ($(1)).
# $(1) is the package staging dir -- files placed here end up in the image.
# Use INSTALL_DIR, INSTALL_BIN, INSTALL_CONF macros -- not raw cp/mkdir commands.
# ── Evaluation ───────────────────────────────────────────────────────────────
# This line must be the last line of the Makefile.
# It registers the package with the build system.
## Step-by-Step Explanation
### Required variables
### `include $(TOPDIR)/rules.mk` and `include $(INCLUDE_DIR)/package.mk`
### `Package/<name>` define block
### `$(TARGET_CONFIGURE_OPTS)` and `$(TARGET_CFLAGS)`
### `$(1)` in `Package/install`
### `INSTALL_BIN`, `INSTALL_CONF`, `INSTALL_DIR`



### `$(eval $(call BuildPackage,myapp))`
## Anti-Patterns
### WRONG: Using cmake/make directly
# DO NOT DO THIS
### CORRECT: Let package.mk handle cross-compilation
# Build/Configure and Build/Compile are now handled automatically.
### WRONG: PKG_MD5SUM instead of PKG_HASH
### CORRECT: PKG_HASH with SHA-256
# Generate the hash:
### WRONG: Raw mkdir/cp in Package/install
## Related Topics
## Verification Notes




> **Summary:** Reference for identifying which OpenWrt era (legacy, transitional, or current) a given pattern belongs to, so AI tools produce era-appropriate recommendations.
# OpenWrt Era Guide
## Version Target Statement
## Overview
## Era Reference Table
## Era Markers and Regex Detectors
### Legacy markers (do not use in new code)
# init script without procd


### Transitional markers (use only for compatibility maintenance)


### Current markers (prefer these in all new code)
## Complete Working Examples
### Example 1: Current-era procd init script
#!/bin/sh /etc/rc.common
# Current procd-managed service -- correct era (23.x+)
### Example 2: Current-era LuCI JavaScript view
### Example 3: Current-era ucode UCI script
## Step-by-Step Explanation








## Anti-Patterns
### WRONG: Legacy sysvinit init script
#!/bin/sh /etc/rc.common
### CORRECT: Current procd init script
#!/bin/sh /etc/rc.common
### WRONG: Lua CBI view (deprecated pattern very common in AI output)
### CORRECT: Current JavaScript LuCI view
### WRONG: PKG_MD5SUM in package Makefile
### CORRECT: PKG_HASH with SHA-256
## When Legacy Code Is Acceptable
## Related Topics
## Verification Notes

> **Summary:** Complete guide to writing a procd-managed init script for an OpenWrt service, covering the full lifecycle from start to reload to stop with supervised respawn.
# procd Service Lifecycle
## Overview
## Complete Working Example
#!/bin/sh /etc/rc.common
# /etc/init.d/myapp
# USE_PROCD=1 tells rc.common to delegate lifecycle to procd functions
# instead of sysvinit start/stop/restart shims.
# START and STOP define the boot sequence priority (lower = earlier)
# start_service() is called by procd when the service should launch.
# procd_open_service / procd_close_service bracket the declaration.
# service_triggers() declares which UCI config changes trigger a reload.
# When 'uci commit myapp' is run, procd will call reload_service.
# reload_service() is called instead of stop/start when a trigger fires.
# Default behavior (omitting this function) is to call stop_service
# then start_service. Override only if you need a graceful in-process
# reload (e.g., sending SIGHUP to reload config without process restart).
## Step-by-Step Explanation
### `USE_PROCD=1`
### `START` and `STOP`
### `procd_open_service` / `procd_close_service`
### `procd_open_instance` / `procd_close_instance`
### `procd_set_param command`
### `procd_set_param respawn`
### `service_triggers` and `procd_add_reload_trigger`
## Anti-Patterns
### WRONG: sysvinit-style start/stop without USE_PROCD
#!/bin/sh /etc/rc.common
### CORRECT: USE_PROCD with procd_set_param
### WRONG: Hardcoding config values in the command
### CORRECT: Load from UCI in start_service
## Running user and resource limits
# Run the service as a non-root user (user must exist on the system)
# Optional: set resource limits (ulimit-style)
## Related Topics
## Verification Notes



> **Summary:** Concrete guide to reading and writing UCI configuration from a ucode script or rpcd plugin, covering cursor lifecycle, get/set/commit, section iteration, and error handling.
# UCI Read/Write from ucode
## Overview
## Complete Working Example
#!/usr/bin/env ucode
## Step-by-Step Explanation
### Importing cursor
### `uci.get(config, section, option)`
### `uci.get_first(config, type, option)`
### `uci.foreach(config, type, callback)`
### `uci.set(config, section, option, value)`
### `uci.commit(config)`
### `uci.unload(config)`
## Anti-Patterns
### WRONG: Reading /etc/config/ with open()
### CORRECT: Read with cursor
### WRONG: Writing config with shell UCI calls from ucode
### CORRECT: Use cursor set + commit
### WRONG: Forgetting commit()
## Using uci in an rpcd plugin
## Related Topics
## Verification Notes
