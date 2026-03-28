---
title: Overview
module: wiki
origin_type: wiki_page
token_count: 1468
source_file: L1-raw/wiki/wiki_page-guide-developer-overview.md
last_pipeline_run: '2026-03-28T11:59:43.422282+00:00'
source_url: https://openwrt.org/docs/guide-developer/overview
language: text
ai_summary: The OpenWrt API module provides an overview of how the OpenWrt GNU/Linux distribution is structured, focusing on package management and compilation. OpenWrt is designed for embedded devices, utilizing a package manager called opkg to handle software packages, which are compressed archives containing programs, libraries, and configuration files. The build process involves compiling packages separately and assembling them into a firmware image that can be installed on devices. Additionally, the module explains the role of Makefiles in specifying source downloads and integrity checks for packages.
ai_when_to_use: This module is useful for developers looking to understand the OpenWrt build system and how to create or modify packages for embedded devices.
ai_related_topics:
- package
- package manager
- Makefile
- patches
- toolchain
---
# Overview

If you are familiar with GNU/Linux systems, you should find your way around pretty easily; if you are not, you will need to learn some basic concepts and terminology first.

You might have read that OpenWrt is a **GNU/Linux distribution** (or "distro") aimed at embedded devices.
A GNU/Linux **distribution** is a project that creates and maintains *packages*, used with a Linux kernel to create a GNU/Linux operating system tailored to users' needs.
A **package** is a compressed archive containing a program, a [library](https://en.wikipedia.org/wiki/Library_(computing)) or some scripts, its accompanying configuration files and also information used to integrate it in the operating system. These packages are handled by a **package manager** (opkg in OpenWrt); a program that downloads/opens/installs/uninstalls the packages.
So, an OpenWrt firmware is made by assembling packages around a Linux kernel.

Each package is compiled separately, and when all are done the needed packages are "installed" in a temporary directory that will then be the compressed-read-only [SquashFS](https://en.wikipedia.org/wiki/SquashFS) partition in the device firmware.

While the kernel is handled as a package, it is added to firmware images in the special way each device's bootloader expects. So you can replace the stock firmware without touching the bootloader (which is dangerous and not always possible).

The last step in the build process is actually creating the firmware file, the file to install or upgrade OpenWrt.
This file is usually a memory image ready to be written as is on the internal flash storage of the device. You may notice that many developers simply call it "image" on IRC or in the mailing list.

## How Packages are Compiled

If you look at a package's **Makefile**[^1], you will notice it states the official download link for the sources to be compiled, a SHA256 hash to check the integrity of such download, a version number of the upstream project as package base and a release number to indicate OpenWrt changes. On some packages the version number states git commit, timestamp or another expression to identify the source code version to pull down and build. They generally favor archives with sources from official releases, but some upstream projects don't always have that.

In **patches** directory of each package you will find any patches that will be applied to the source after downloading and before compiling it: (e.g. [pathches dir of busybox](https://github.com/openwrt/openwrt/tree/master/package/utils/busybox/patches)). There are also other directories for configuration files or uci integration.

The kernel's Makefile is a bit more complex, but you can see that it still uses the same structure for pulling down the same kernel version depending on device every time. e.g. [Linux Makefile](https://github.com/openwrt/openwrt/blob/master/package/kernel/linux/Makefile)

All packages are compiled by OpenWrt's own toolchain, which is also handled like packages (see /toolchain and /tools in the source), so you will always have the same compilers/tools as everyone else as they are downloaded from the same sources at the same version.

When you run `make` the OpenWrt build system will use your system's existing building infrastructure to compile the OpenWrt's toolchain first, and then use that to compile the packages. This also has the major benefit of not requiring the user to set up a cross-compiling toolchain that is rather annoying and relatively complex.

## Package Feeds

Not all packages you can install in OpenWrt are from OpenWrt project proper, in fact most packages are not.

The packages from OpenWrt's main repository are maintained directly by core developers, and they are the important, even essential components of OpenWrt firmware or parts of the build system. "**package feeds**" are source repositories that contain additional packages maintained by the community, and each package has its own maintainer.

This is OpenWrt's main repo on github: <https://github.com/openwrt/openwrt>

These are official package feeds:

- <https://github.com/openwrt/luci>
- <https://github.com/openwrt/telephony>
- <https://github.com/openwrt-routing/packages>
- <https://github.com/openwrt/packages>

Being "official feeds", the packages therein will be compiled and offered by the official download server, but they are not technically OpenWrt proper, they are community-maintained. The "package feed" system is designed to allow easy addition of your own custom feeds to your own custom firmware images, but of course you will have to compile them and host them on your own servers.

If you look at the built packages [here](https://downloads.openwrt.org/releases/21.02.1/packages/x86_64/) on the download server (this is the same server opkg uses to download packages in a live OpenWrt system), they are divided by feed name, packages in "base" come from the main repository, and also from main repository are packages that are found in target-specific directories, for example [here](https://downloads.openwrt.org/releases/24.10.1/packages/x86_64/packages/) what you see are mostly drivers like kmod-\*.

## Package Versions

As stated above, package Makefiles have a PKG_VERSION tag that shows the upstream version which is the major version of the package, and a PKG_RELEASE tag that is used to show changes on the OpenWrt side, that is the minor version. If you see a package that lists version as 123-1, its major version is 123 and minor version is 1.

Some packages have timestamp or git commit as major version, for example 2016-09-21-42ad5367-1 where the last "1" is the minor version.

You can see all versions used in the first page of the [table of packages](/packages/table/start).

Or by browsing a Package.manifest in the package download directory <https://downloads.openwrt.org/releases/24.10.1/packages/mips_24kc/base/Packages.manifest>

## Repeatable Builds

The aforementioned system allows repeatable builds. The major version of source archives are written in the packages' Makefiles in the git repositories of main and community package feeds; you can see full history of changes to that file with *git*.

There is a cache server that stores source archives because it's more convenient than having the build bots spamming the upstream download servers, and it is also a fallback should the upstream server disappear. It should keep the packages' sources for a long while, as they are used by build bots for as long as the releases that depend on them are supported.

This server index may be browsed here: <https://sources.openwrt.org/>

[^1]: the file defines settings for building the package, [e.g. busybox's](https://github.com/openwrt/openwrt/blob/master/package/utils/busybox/Makefile)
