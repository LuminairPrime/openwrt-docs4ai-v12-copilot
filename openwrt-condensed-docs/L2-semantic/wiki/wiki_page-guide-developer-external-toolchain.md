---
title: External Toolchain
module: wiki
origin_type: wiki_page
token_count: 409
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-external-toolchain.md
last_pipeline_run: '2026-03-09T18:30:57.384548+00:00'
language: text
---
# External Toolchain

## Use OpenWrt as External Toolchain

Using an external toolchain reduce build time when starting with a cleaned-up source tree. Useful when using an automated build system like Hudson/Tinderbox.  

### Step 1: Build Toolchain

Just do the same as everytime you (re)compile OpenWrt. Checkout openwrt repo, set your options in .config and build the whole thing. Only difference you have to select `Package the OpenWrt-based Toolchain` in the main view of `make menuconfig`

Alternatively you can download precompiled toolchain from openwrt download page by searching for the correct toolchain for your target. For example if you need precompiled toolchain for openwrt 22.03.0 for target ipq806x/generic [this is the link to use](https://downloads.openwrt.org/releases/22.03.0/targets/ipq806x/generic/openwrt-toolchain-22.03.0-ipq806x-generic_gcc-11.2.0_musl_eabi.Linux-x86_64.tar.xz).

### Step 2: Build Firmware

1.  Checkout OpenWrt into directory **openwrt**
2.  Follow normal instruction for openwrt prereq
3.  Use the utility script to setup your buildroot `   ./scripts/ext-toolchain.sh \
                --toolchain TOOLCHAIN_FILE_LOCATION \
                --config TARGET_NAME (example ipq806x/generic)
      `
4.  Use your buildroot like a normal one. Edit your config with `make menuconfig` and run `make` to compile your image

If you want to update a .config to use an external toolchain you can use the `--overwrite-config`. For example:

       ./scripts/ext-toolchain.sh \
                --toolchain TOOLCHAIN_FILE_LOCATION \
                --overwrite-config
                --config TARGET_NAME (example ipq806x/generic)