---
title: OpenWrt Buildroot – Technical Reference
module: wiki
origin_type: wiki_page
token_count: 1012
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-buildroot.md
last_pipeline_run: '2026-03-20T01:28:00.439321+00:00'
language: text
ai_summary: Explains the OpenWrt build system (buildroot), covering the directory layout (package/, target/, toolchain/, staging_dir/), the package Makefile structure (PKG_NAME, PKG_BUILD_DIR, Package/install, Build/Compile targets), the feeds system for third-party packages, the menuconfig workflow for selecting packages and target configs, and DL_DIR/TOPDIR conventions for reproducible builds.
ai_when_to_use: Reference when creating a new OpenWrt package Makefile, adding a new package to a feed, configuring a cross-compilation toolchain for a specific target board, or troubleshooting why a package fails to compile in the buildroot environment.
ai_related_topics:
- PKG_BUILD_DIR
- Package/install
- Build/Compile
- feeds.conf
- scripts/feeds update
- make menuconfig
- TOPDIR
---
# OpenWrt Buildroot – Technical Reference

See also: [Using the toolchain](/docs/guide-developer/start#using_the_toolchain)

## Kernel related options

The available Kernel version are listed in include/kernel-[version.mk](../openwrt-core/makefile_meta-include-mk.md):

Example:

    # Use the default kernel version if the Makefile doesn't override it

    LINUX_RELEASE?=1

    LINUX_VERSION-3.18 = .20
    LINUX_VERSION-4.0 = .9
    LINUX_VERSION-4.1 = .5

    LINUX_KERNEL_MD5SUM-3.18.20 = 952c9159acdf4efbc96e08a27109d994
    LINUX_KERNEL_MD5SUM-4.0.9 = 40fc5f6e2d718e539b45e6601c71985b
    LINUX_KERNEL_MD5SUM-4.1.5 = f23e1d4ce8f63e46db81d56e36281885

    ifdef KERNEL_PATCHVER
      LINUX_VERSION:=$(KERNEL_PATCHVER)$(strip $(LINUX_VERSION-$(KERNEL_PATCHVER)))
    endif

    split_version=$(subst ., ,$(1))
    merge_version=$(subst $(space),.,$(1))
    KERNEL_BASE=$(firstword $(subst -, ,$(LINUX_VERSION)))
    KERNEL=$(call merge_version,$(wordlist 1,2,$(call split_version,$(KERNEL_BASE))))
    KERNEL_PATCHVER ?= $(KERNEL)

    # disable the md5sum check for unknown kernel versions
    LINUX_KERNEL_MD5SUM:=$(LINUX_KERNEL_MD5SUM-$(strip $(LINUX_VERSION)))
    LINUX_KERNEL_MD5SUM?=x

Kernel code is added with contents of generic/files and selectively \<arch\>/files/ subdirs.

It is patched with generic/patches-\<Kernel version\> and \<arch\>/patches-\<Kernel version\>

### CONFIG_EXTERNAL_KERNEL_TREE

OpenWrt will create a symlink to a Kernel repository in the file system.

The target can be a local git kernel repository.

:!: You should patch your tree to contain OpenWrt changes - builds might fail to compile or fail at boot.

:!: Musl libc need patches to kernel headers that fix redifinitions errors with user space headers. uclibc and glibc don't need these changes.

Example:

    095-api-fix-compatibility-of-linux-in.h-with-netinet-in..patch
    270-uapi-kernel.h-glibc-specific-inclusion-of-sysinfo.h.patch
    271-uapi-libc-compat.h-do-not-rely-on-__GLIBC__.patch
    272-uapi-if_ether.h-prevent-redefinition-of-struct-ethhd.patch

see <http://wiki.musl-libc.org/wiki/Building_Busybox>

### OpenWrt Buildroot – Build sequence

      tools – automake, autoconf, sed, cmake
      toolchain/binutils – as, ld, …
      toolchain/gcc – gcc, g++, cpp, …
      target/linux – kernel modules
      package – core and feed packages
      target/linux – kernel image
      target/linux/image – firmware image file generation

### Make sequence

Top command `make world` calls the following sequence of the commands:
`make target/compile`
`make package/cleanup`
`make package/compile`
`make package/install`
`make package/preconfig`
`make target/install`
`make package/index`

You may run each command independently. For example, if the process of compilation of packages stops on error, you may fix the problem and next continue without cleanup:
`make package/compile`
`make package/install`
`make package/preconfig`
`make target/install`
`make package/index`

see [packages](/docs/guide-developer/packages)

### Warnings, errors and tracing

The parameter `V=x` specifies level of messages in the process of the build.

        V=99 and V=1 are now deprecated in favor of a new verbosity class system,
        though the old flags are still supported.
        You can set the V variable on the command line (or OPENWRT_VERBOSE in the
        environment) to one or more of the following characters:

        - s: stdout+stderr (equal to the old V=99)
        - c: commands (for build systems that suppress commands by default, e.g. kbuild, cmake)
        - w: warnings/errors only (equal to the old V=1)

source: <https://dev.openwrt.org/changeset/31484>

old options:

- `1` - print a messages containing the working directory before and after other processing.
- `99` - trace of the build, ordinary messages yellow, error messages red, debug - black;

Examples:

    make V=sc

    make V=sw
