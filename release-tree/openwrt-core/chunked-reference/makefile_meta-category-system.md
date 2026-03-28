---
title: 'OpenWrt Buildroot: system packages'
module: openwrt-core
origin_type: makefile_meta
token_count: 2031
source_file: L1-raw/openwrt-core/makefile_meta-category-system.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/openwrt/blob/unknown/package/system
source_locator: package/system
language: makefile
ai_summary: The OpenWrt Buildroot system packages module provides a collection of essential packages for system management and functionality within the OpenWrt environment. Key packages include 'opkg', a lightweight package management system that handles installation and removal of packages, and 'ca-certificates', which ensures secure connections by providing trusted CA certificates. Other notable packages are 'fstools' for filesystem management, 'fwtool' for firmware upgrades, and 'mtd' for managing flash memory devices. Each package is maintained by specific developers and is available from designated source URLs.
ai_when_to_use: This module is particularly useful when building custom OpenWrt firmware images that require specific system functionalities or package management capabilities.
ai_related_topics:
- apk
- ca-certificates
- fstools
- fwtool
- iucode-tool
- mtd
- openwrt-keyring
- opkg
- procd
- refpolicy
---

> **Source:** [https://github.com/openwrt/openwrt/blob/unknown/package/system](https://github.com/openwrt/openwrt/blob/unknown/package/system)
> **Kind:** makefile_meta | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

# OpenWrt Buildroot: system packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/system
---

## apk

| Field | Value |
|---|---|
| Version | 3.0.5 |
| License | GPL-2.0-only |
| Maintainer | Paul Spooren <mail@aparcar.org> |
| Source URL | https://gitlab.alpinelinux.org/alpine/apk-tools.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/apk
---

## ca-certificates

| Field | Value |
|---|---|
| Version | 20250419 |
| License | GPL-2.0-or-later MPL-2.0 |
| Maintainer | PKG_LICENSE:=GPL-2.0-or-later MPL-2.0 |
| Source URL | @DEBIAN/pool/main/c/ca-certificates |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/ca-certificates
---

## fstools

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | John Crispin <john@phrozen.org> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/fstools
---

## fwtool

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/fwtool
---

## iucode-tool

| Field | Value |
|---|---|
| Version | 2.3.1 |
| License | GPL-2.0 |
| Maintainer | Zoltan HERPAI <wigyori@uid0.hu> |
| Source URL | https://gitlab.com/iucode-tool/releases/raw/latest |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/iucode-tool
---

## mtd

This package contains an utility useful to upgrade from other firmware or older OpenWrt releases.

| Field | Value |
|---|---|
| License | GPL-2.0+ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/mtd
---

## openwrt-keyring

The keyring of with the developer using and gpg public keys.

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/openwrt-keyring SECTION:=base CATEGORY:=Base system PROVIDES:=lede-keyring TITLE:=OpenWrt Developer Keyring URL:=https://openwrt.org/docs/guide |
| Maintainer | John Crispin <john@phrozen.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/openwrt-keyring
---

## opkg

Lightweight package management system opkg is the opkg Package Management System, for handling installation and removal of packages on a system. It can recursively follow dependencies and download all packages necessary to install a particular package. opkg knows how to install both .ipk and .deb packages.

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Jo-Philipp Wich <jo@mein.io> # Extend depends from [version.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/opkg
---

## procd

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | John Crispin <john@phrozen.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/procd
---

## refpolicy

The SELinux Reference Policy project (refpolicy) is a complete SELinux policy that can be used as the system policy for a variety of systems and used as the basis for creating other policies. Reference Policy was originally based on the NSA example policy, but aims to accomplish many additional goals. The current refpolicy does not fully support OpenWRT and needs modifications to work with the default system file layout. These changes should be added as patches to the refpolicy that modify a single SELinux policy. The refpolicy works for the most part in permissive mode. Only the basic set of utilities are enabled in the example policy config and some of the pathing in the policies is not correct. Individual policies would need to be tweaked to get everything functioning properly.

| Field | Value |
|---|---|
| Version | 2.20250923 |
| License | GPL-2.0-or-later |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/refpolicy/releases/download/RELEASE_2_20250923 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/refpolicy
---

## rpcd

This package provides the UBUS RPC backend server to expose various functionality to frontend programs via JSON-RPC.

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/rpcd
---

## selinux-policy

Basic SELinux Security Policy designed specifically for OpenWrt and written in Common Intermediate Language.

| Field | Value |
|---|---|
| Version | 2.8.4 |
| License | Unlicense |
| Maintainer | Dominick Grift <dominick.grift@defensec.nl> |
| Source URL | https://git.defensec.nl/selinux-policy.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/selinux-policy
---

## ubox

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | John Crispin <john@phrozen.org> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/ubox SECTION:=base CATEGORY:=Base system DEPENDS:=+libubox +ubusd +ubus +libubus +libuc |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/ubox
---

## ubus

| Field | Value |
|---|---|
| License | LGPL-2.1 |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/ubus
---

## ucert

| Field | Value |
|---|---|
| License | GPL-3.0+ |
| Maintainer | Daniel Golle <daniel@makrotopia.org> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/host-build.mk include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/ucert
---

## uci

| Field | Value |
|---|---|
| License | LGPL-2.1 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk # set to 1 to enable debugging |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/uci
---

## urandom-seed

| Field | Value |
|---|---|
| License | GPL-2.0-only include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/urandom-seed SECTION:=base CATEGORY:=Base system DEPENDS:=+getrandom TITLE:=/etc/urandom.seed handling for OpenWrt URL:=https://openwrt.or |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/urandom-seed
---

## urngd

urngd is OpenWrt's micro non-physical true random number generator based on timing jitter. Using the Jitter RNG core, the rngd provides an entropy source that feeds into the Linux /dev/random device if its entropy runs low. It updates the /dev/random entropy estimator such that the newly provided entropy unblocks /dev/random. The seeding of /dev/random also ensures that /dev/urandom benefits from entropy. Especially during boot time, when the entropy of Linux is low, the Jitter RNGd provides a source of sufficient entropy.

| Field | Value |
|---|---|
| License | GPL-2.0 BSD-3-Clause |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/urngd
---

## usign

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/host-build.mk include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/usign
---

## zram-swap

A script to activate swaping on a compressed zram partition. This could be used to increase the available memory, by using compressed memory.


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/zram-swap
---
