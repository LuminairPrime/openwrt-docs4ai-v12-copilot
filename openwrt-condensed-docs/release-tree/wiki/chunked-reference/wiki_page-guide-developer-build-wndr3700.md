---
title: Building OpenWrt for Netgear WNDR3700
module: wiki
origin_type: wiki_page
token_count: 1172
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-build-wndr3700.md
last_pipeline_run: '2026-03-20T01:28:00.439321+00:00'
language: text
ai_summary: This document provides a comprehensive guide on building OpenWrt for the Netgear WNDR3700, detailing the steps required to create a functional firmware image from scratch. It includes prerequisites for setting up the OpenWrt Buildroot, instructions for pulling the latest code, and configuration steps necessary for a successful build. Additionally, it covers how to unbrick the device without a serial cable and offers optional guidance for creating one. The instructions are based on the trunk revision 19064 and emphasize the importance of specific configuration settings for network access.
ai_when_to_use: Use this guide when you need to build a custom OpenWrt image for the Netgear WNDR3700, especially if you are facing issues with the default firmware or need specific features not available in the standard release.
ai_related_topics:
- OpenWrt Buildroot – Installation
- OpenWrt Buildroot – Usage
- Target System
- Target Profile
- Target Images
- Image Configuration
- Network - CRDA
- Kernel Modules
---
# Building OpenWrt for Netgear WNDR3700

**WNDR3700 Developers' Overview**

This page contains, thus far, one user's complete notes on how to build a working OpenWrt WNDR3700 image from scratch, including working wireless on 2.4 GHz and 5 GHz bands. This page assumes that you are comfortable with building software and using kernel-style makefile systems, but otherwise, the page describes how to build the system from the ground up (including getting your base OS ready to build OpenWrt in the first place).

This page also describes the method used to unbrick a WNDR3700 (which does NOT require a serial cable), as well as optional instructions for manufacturing a serial cable (should you wish to use it for running ramdisk images).

These instructions are working fine as of the relatively-recent trunk revision 19064.

## Prerequisites

- [OpenWrt Buildroot – Installation](/docs/guide-developer/toolchain/install-buildsystem)
- [OpenWrt Buildroot – Usage](/docs/guide-developer/toolchain/start)

Until WNDR3700 support is integrated into a release, you'll need to execute the following commands to pull down the latest bleeding-edge code:

``` bash
cd ~
mkdir openwrt
cd openwrt
git clone git://git.openwrt.org/openwrt.git trunk
```

If you also want to check out the extra packages that can be installed on your system (including the helpful `ntpclient` and the *WebUI LuCI*), you can also run this:

``` bash
cd ~/openwrt/trunk
./scripts/feeds update packages luci
./scripts/feeds install -a -p luci
./scripts/feeds install <package_name>
```

## Configuration

Run the OpenWrt's BuildRoot menu configuration system to get started:

``` bash
cd ~/openwrt/trunk
make menuconfig
```

Make the following selections beyond the defaults. You might be able to get away with building things as kernel modules instead of built-in, but the author has not tried.

1.  Target System: Atheros AR71xx/AR7240/AR913x
2.  Target Profile: NETGEAR WNDR3700
3.  Target Images: if you want to build a ramdisk image, select "ramdisk" and ensure that LZMA compression is listed. Otherwise, leave the defaults alone (should be jffs2, squashfs and tgz). You seemingly need to rebuild everything except the toolchain if you want to switch from the ramdisk to a firmware image or vice versa.
4.  Image Configuration: Use this section to set up the defaults for the LAN ports on your router. If you don't have a serial cable connected to the router, you'll need to do this so that you can access the router once your newly-flashed code boots up. I recommend entering values for DNS server (on your ISP's network), LAN network mask (for the addresses to be doled out via DHCP), and LAN IP address (private IP address on your router's side).
    - eg. LAN DNS = (whatever your ISP tells you to use), LAN network mask=255.255.255.0, LAN IP address=192.168.0.1
    - [NOTE](../../wiki/chunked-reference/wiki_page-techref-luci2.md): **pfk3** didn't do this step and by default OpenWrt was built with 192.168.1.1 & 255.255.255.0 for it's LAN IP/subnet.
    - [NOTE](../../wiki/chunked-reference/wiki_page-techref-luci2.md): You still have to "\*" this option in order for the router to be on the network. You don't have to change the settings though
    - [NOTE](../../wiki/chunked-reference/wiki_page-techref-luci2.md): It is not possible to set this feature in the latest [attitude adjustment](https://dev.openwrt.org/changeset/31258/) release. See this [mailing list post](http://www.mail-archive.com/openwrt-devel@lists.openwrt.org/msg15992.html) for more information.
5.  Network -\> CRDA = YES (compile as built-in package with "\*", not as a module with "M")
6.  Kernel Modules -\> LED Modules -\> kmod-leds-wndr3700-usb = YES (compile as built-in driver as "\*", not as a module with "M")
7.  Kernel Modules -\> Wireless Drivers -\> kmod-ath -\> Configuration -\> Force Atheros drivers to respect the user's regdomain settings = YES

If you want to slap a USB memory stick in the back of your router to allow you to install many more packages read the pages [USB Basic Support](/docs/guide-user/storage/usb-installing) and [USB Storage](/docs/guide-user/storage/usb-drives).

A sample .config file is linked to below. If you use this, at the very least, you will need to edit the DNS server address listed in the "image configuration" step (see \#4 above).

Type

    make

and it should merrily build away for at least a good half hour (or more). When you're done, you should have the resulting binaries stored in `~/openwrt/trunk/bin/ar71xx`. As of trunk revision 25119, separate binaries will be created for the WNDR3700v1 and WNDR3700v2.

## Installation

Please see [WNDR3700 - Installation](toh/netgear/wndr3700#installation) or [OpenWrt - Installation](/docs/guide-user/installation/generic.flashing)
