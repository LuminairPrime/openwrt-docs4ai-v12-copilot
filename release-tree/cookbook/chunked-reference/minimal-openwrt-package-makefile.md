---
title: Minimal OpenWrt Package Makefile
module: cookbook
origin_type: authored
token_count: 2639
source_file: L1-raw/cookbook/minimal-openwrt-package-makefile.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_locator: content/cookbook-source/minimal-openwrt-package-makefile.md
description: Annotated minimal Makefile for packaging a C program in OpenWrt, covering
  the required variables, Build/Compile, Package/install, and the correct PKG_HASH
  vs PKG_MD5SUM distinction.
era_status: current
when_to_use: Use when porting a C application, daemon, or utility to OpenWrt as a
  proper package. Do not use standalone cmake, make, or ./configure -- these tools
  run on the host, not in the cross-compilation environment.
related_modules:
- wiki
- openwrt-core
verification_basis: Corpus review of wiki/wiki_page-guide-developer-packages.md; PKG_HASH
  vs PKG_MD5SUM distinction sourced from wiki corpus; INSTALL_BIN/INSTALL_CONF macros
  from wiki packages guide
reviewed_by: placeholder
last_reviewed: '2026-03-23'
---

> **Source:** `content/cookbook-source/minimal-openwrt-package-makefile.md`
> **Kind:** authored | **Method:** hand-authored
> **Normalized:** 2026-03-28

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

For cmake-based upstreams, use the cmake [package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include instead:

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

- [procd Service Lifecycle](./procd-service-lifecycle.md) — how to write the init script installed by Package/install
- [Architecture Overview](./architecture-overview.md) — where packages fit in the build and runtime stack
- [OpenWrt Era Guide](./openwrt-era-guide.md) — PKG_HASH vs PKG_MD5SUM era distinction
- [Wiki: Creating packages](../../wiki/chunked-reference/wiki_page-guide-developer-packages.md) — full reference for all Makefile variables

## Verification Notes

- Makefile variable names (`PKG_NAME`, `PKG_HASH`, `PKG_RELEASE`, etc.) verified against `wiki/wiki_page-guide-developer-packages.md` in corpus
- `PKG_MD5SUM` deprecated status confirmed from same wiki page
- `INSTALL_BIN`, `INSTALL_CONF`, `INSTALL_DATA`, `INSTALL_DIR` macro names verified from wiki packages guide
- `$(TARGET_CONFIGURE_OPTS)` usage verified from wiki corpus build examples
- `$(eval $(call BuildPackage,...))` as mandatory last line confirmed from wiki packages guide
