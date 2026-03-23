---
title: 'OpenWrt Buildroot: Build System Include Files'
module: openwrt-core
origin_type: makefile_meta
token_count: 2083
version: 41d6584
source_file: L1-raw/openwrt-core/makefile_meta-include-mk.md
last_pipeline_run: '2026-03-23T22:14:22.429226+00:00'
upstream_path: include/
language: makefile
---
# OpenWrt Buildroot: Build System Include Files

> **Source:** https://github.com/openwrt/openwrt/tree/master/include

Core build system Makefile fragments.

---

## autotools.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/autotools.mk
---

## debug.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/debug.mk
---

## depends.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/depends.mk
---

## download.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2012 OpenWrt.org
Copyright (C) 2016 LEDE project
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/download.mk
---

## feeds.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2014 OpenWrt.org
Copyright (C) 2016 LEDE Project
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/feeds.mk
---

## hardening.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2015-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/hardening.mk
---

## host-build.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/host-build.mk
---

## image.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/image.mk
---

## kernel-build.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/kernel-build.mk
---

## kernel-defaults.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/kernel-defaults.mk
---

## kernel.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/kernel.mk
---

## meson.mk

# Documentation
```text
To build your package using meson:
include $(INCLUDE_DIR)/meson.mk
MESON_ARGS+=-Dfoo -Dbar=baz
To pass additional environment variables to meson:
MESON_VARS+=FOO=bar
Default configure/compile/install targets are provided, but can be
overwritten if required:
define Build/Configure
$(call Build/Configure/Meson)
...
endef
same for Build/Compile and Build/Install
Host packages are built in the same fashion, just use these vars instead:
MESON_HOST_ARGS+=-Dfoo -Dbar=baz
MESON_HOST_VARS+=FOO=bar
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/meson.mk
---

## netfilter.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/netfilter.mk
---

## nls.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2011-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/nls.mk
---

## openssl-module.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2022-2023 Enéas Ulir de Queiroz
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/openssl-module.mk
---

## package-bin.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/package-bin.mk
---

## package-defaults.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/package-defaults.mk
---

## package-dumpinfo.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/package-dumpinfo.mk
---

## package-pack.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2022 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/package-pack.mk
---

## package-seccomp.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2015-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/package-seccomp.mk
---

## package.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/package.mk
---

## prereq-build.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/prereq-build.mk
---

## prereq.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/prereq.mk
---

## quilt.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/quilt.mk
---

## subdir.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/subdir.mk
---

## target.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2008 OpenWrt.org
Copyright (C) 2016 LEDE Project
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/target.mk
---

## toolchain-build.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2009-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/toolchain-build.mk
---

## toplevel.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2007-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/toplevel.mk
---

## unpack.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/unpack.mk
---

## verbose.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2006-2020 OpenWrt.org
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/verbose.mk
---

## version.mk

# Documentation
```text
SPDX-License-Identifier: GPL-2.0-only
Copyright (C) 2012-2015 OpenWrt.org
Copyright (C) 2016 LEDE Project
```


> Source: https://github.com/openwrt/openwrt/blob/master/include/version.mk
---
