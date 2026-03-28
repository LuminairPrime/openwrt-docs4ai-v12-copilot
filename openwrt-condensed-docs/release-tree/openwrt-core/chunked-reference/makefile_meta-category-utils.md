---
title: 'OpenWrt Buildroot: utils packages'
module: openwrt-core
origin_type: makefile_meta
token_count: 5864
source_file: L1-raw/openwrt-core/makefile_meta-category-utils.md
last_pipeline_run: '2026-03-27T20:02:39.961617+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/openwrt/blob/unknown/package/utils
source_locator: package/utils
language: makefile
ai_summary: The OpenWrt Buildroot utils packages module provides a collection of utility tools and libraries for embedded Linux systems. Key components include Android Debug Bridge (adb) for device communication, audit libraries for security auditing, and various utilities for specific hardware like BCM27xx and BCM4908. Additionally, it includes essential tools like busybox for command-line operations and bzip2 for data compression. Each package is maintained by specific contributors and has its own versioning and licensing details.
ai_when_to_use: Use this module when you need to integrate utility packages into your OpenWrt build for enhanced functionality or specific hardware support.
ai_related_topics:
- adb
- audit
- bcm27xx-utils
- bcm4908img
- bsdiff
- busybox
- bzip2
- checkpolicy
- cli
---

> **Source:** [https://github.com/openwrt/openwrt/blob/unknown/package/utils](https://github.com/openwrt/openwrt/blob/unknown/package/utils)
> **Kind:** makefile_meta | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-27

# OpenWrt Buildroot: utils packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/utils
---

## adb

Android Debug Bridge (adb) is a versatile command line tool that lets you communicate with an emulator instance or connected Android-powered device.

| Field | Value |
|---|---|
| Version | 5.0.2~$(call version_abbrev,$(PKG_SOURCE_VERSION)) |
| Maintainer | Henryk Heisig <hyniu@o2.pl> |
| Source URL | https://android.googlesource.com/platform/system/core |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/adb
---

## audit

$(call Package/audit/Default/description) This package contains the audit shared library.

| Field | Value |
|---|---|
| Version | 3.1.5 |
| License | GPL-2.0-or-later LGPL-2.1-or-later |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/linux-audit/$(PKG_NAME).git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/audit
---

## bcm27xx-utils

BCM27xx scripts and simple applications. Replaces bcm27xx-userland scripts and applications.

| Field | Value |
|---|---|
| Version | 2025.03.14 |
| License | BSD-3-Clause |
| Source URL | https://github.com/raspberrypi/utils.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/bcm27xx-utils
---

## bcm4908img

CFE bootloader for BCM4908 uses custom image format. It consists of: 1. Optional cferom image 2. bootfs JFFS2 partition (cferam, kernel, DTB and optional helper files) 3. padding 4. rootfs simply appended to the bootfs + padding 5. tail with checksum and basic device info This util allows creating, modifying and extracting from BCM4908 images.


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/bcm4908img
---

## bsdiff

| Field | Value |
|---|---|
| Version | 4.3 |
| License | BSD-2-Clause |
| Maintainer | Hauke Mehrtens <hauke@hauke-m.de> |
| Source URL | https://www.daemonology.net/bsdiff/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/bsdiff
---

## busybox

The Swiss Army Knife of embedded Linux. It slices, it dices, it makes Julian Fries.

| Field | Value |
|---|---|
| Version | 1.37.0 |
| License | GPL-2.0 |
| Source URL | https://www.busybox.net/downloads https://sources.buildroot.net/$(PKG_NAME) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/busybox
---

## bzip2

bzip2 is a freely available, patent free, high-quality data compressor. This packages provides libbz2 library.

| Field | Value |
|---|---|
| Version | 1.0.8 |
| License | bzip2-1.0.8 |
| Maintainer | Steven Barth <cyrus@openwrt.org> |
| Source URL | https://sourceware.org/pub/bzip2 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/bzip2
---

## checkpolicy

checkpolicy is the SELinux policy compiler. It uses libsepol to generate the binary policy. checkpolicy uses the static libsepol since it deals with low level details of the policy that have not been encapsulated/abstracted by a proper shared library interface.

| Field | Value |
|---|---|
| Version | 3.9 |
| License | GPL-2.0-or-later |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/checkpolicy
---

## cli

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/cli SECTION:=utils CATEGORY:=Utilities TITLE:=OpenWrt CLI DEPENDS:=+ucode +ucode-mod-uline +ucode-mod-ubus +ucode-mod-uloo |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/cli
---

## ct-bugcheck

Scripts to check for bugs (like firmware crashes) and package them for reporting. Currently this script only checks for ath10k firmware crashes. Once installed, you can enable this tool by creating a file called /etc/config/bugcheck with the following contents: DO_BUGCHECK=1 export DO_BUGCHECK


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ct-bugcheck
---

## debugcc

| Field | Value |
|---|---|
| License | BSD-3-Clause |
| Maintainer | Christian Marangi <ansuelsmth@gmail.com> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[meson.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/debugcc SECTION:=utils CATEGORY:=Utilities TITLE:=QCOM debugcc utility DEPENDS |
| Source URL | https://github.com/linux-msm/debugcc.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/debugcc
---

## dns320l-mcu

| Field | Value |
|---|---|
| License | GPL-3.0+ |
| Maintainer | Zoltan HERPAI <wigyori@uid0.hu> |
| Source URL | https://github.com/wigyori/dns320l-daemon.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/dns320l-mcu
---

## dtc

Device Tree Compiler for Flat Device Trees Device Tree Compiler, dtc, takes as input a device-tree in a given format and outputs a device-tree in another format for booting kernels on embedded systems.

| Field | Value |
|---|---|
| Version | 1.7.2 |
| License | GPL-2.0-only |
| Maintainer | Yousong Zhou <yszhou4tech@gmail.com> |
| Source URL | @KERNEL/software/utils/dtc |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/dtc
---

## e2fsprogs

This package contains essential ext2 filesystem utilities which consists of e2fsck, mke2fs and most of the other core ext2 filesystem utilities.

| Field | Value |
|---|---|
| Version | 1.47.3 |
| License | GPL-2.0 |
| Source URL | @KERNEL/linux/kernel/people/tytso/e2fsprogs/v$(PKG_VERSION)/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/e2fsprogs
---

## f2fs-tools

| Field | Value |
|---|---|
| Version | 1.16.0 |
| License | GPL-2.0-only |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://git.kernel.org/pub/scm/linux/kernel/git/jaegeuk/f2fs-tools.git/snapshot/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/f2fs-tools
---

## fbtest


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/fbtest
---

## firmware-utils


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/firmware-utils
---

## fitblk

Release [uImage](../../wiki/chunked-reference/wiki_page-techref-image-format.md).FIT block devices using ioctl.

| Field | Value |
|---|---|
| License | GPL-2.0-only |
| Maintainer | Daniel Golle <daniel@makrotopia.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/fitblk
---

## fritz-tools

Utility to partially read the TFFS filesystems.

**README:**

# README
```markdown
Userspace utilties for accessing TFFS (a name-value storage usually found in AVM Fritz!Box based devices)

## Building

```
mkdir build
cd build
cmake /path/to/fritz_tffs_tools
make
```

## Usage

All command line parameters are documented:
```
fritz_tffs_read -h
```

Show all entries from a TFFS partition dump  (in the format: name=value):
```
fritz_tffs_read -i /path/to/tffs.dump -a
```

Read a TFFS partition and show all entries (in the format: name=value):
```
fritz_tffs_read -i /dev/mtdX -a
```

Output only the value of a specific key (this will only show the value):
```
fritz_tffs_read -i /dev/mtdX -n my_ipaddress
```

## LICENSE

See `LICENSE`:

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
```


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/fritz-tools
---

## jboot-tools

This package contains: jboot_config_read.c: partially read the config partition of JBOOT based D-Link devices.

**README:**

# README
```markdown
Userspace utilties for jboot based devices config partition read

## Building

```
mkdir build
cd build
cmake /path/to/jboot-tools
make
```

## Usage

All command line parameters are documented:
```
jboot_config_read -h
```

Show all stored MACs:
```
jboot_config_read -m -i PATH_TO_CONFIG_PARTITIO
```

Extract wifi eeprom data:
```
jboot_config_read  -i PATH_TO_CONFIG_PARTITION -e OUTPUT_PATH
```


## LICENSE

See `LICENSE`:

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
```


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/jboot-tools
---

## jsonfilter

| Field | Value |
|---|---|
| License | ISC include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/jsonfilter SECTION:=base CATEGORY:=Base system DEPENDS:=+libubox +libjson-c TITLE:=OpenWrt JSON filter utility URL: |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/jsonfilter
---

## lua

$(call Package/lua/Default/description) This package contains the Lua shared libraries, needed by other programs.

| Field | Value |
|---|---|
| Version | 5.1.5 |
| License | MIT |
| Source URL | https://www.lua.org/ftp/ https://www.tecgraf.puc-rio.br/lua/ftp/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/lua
---

## lua5.3

$(call Package/lua5.3/Default/description) This package contains the Lua shared libraries, needed by other programs.

| Field | Value |
|---|---|
| Version | 5.3.5 |
| License | MIT |
| Source URL | https://www.lua.org/ftp/ https://www.tecgraf.puc-rio.br/lua/ftp/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/lua5.3
---

## mdadm

A tool for managing Linux Software RAID arrays. RAID 0, 1 and 10 support included. If you need RAID 4,5 or 6 functionality please install kmod-md-raid456 .

| Field | Value |
|---|---|
| Version | 4.3 |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | @KERNEL/linux/utils/raid/mdadm |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/mdadm
---

## mtd-utils

Utilities for manipulating memory technology devices.

| Field | Value |
|---|---|
| Version | 2.3.0 |
| License | GPLv2 |
| Maintainer | John Crispin <john@phrozen.org> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/mtd-utils/Default SECTION:=utils CATEGORY:=Utilities URL:=http://www.linux-mtd.infradead.org/ DEPENDS:=@NAND_SUPPORT en |
| Source URL | https://infraroot.at/pub/mtd/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/mtd-utils
---

## nilfs-utils

| Field | Value |
|---|---|
| Version | 2.2.12 |
| License | GPL-2.0 |
| Maintainer | Pavlo Samko <bulldozerbsg@gmail.com> |
| Source URL | https://nilfs.sourceforge.io/download/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/nilfs-utils
---

## nvram

This package contains an utility to manipulate NVRAM on Broadcom based devices. It works on bcm47xx (Linux 2.6) without using the kernel api.


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/nvram
---

## omnia-eeprom

This package contains the omnia-eeprom utility, which allows you to display and update EEPROM fields on the Turris Omnia router. The EEPROM is normally not meant to be updated by users, but there are some exceptions where it might be useful. One such example is to change the DDR3 speed from the default 1600K mode to 1333H mode, in order to solve random crashes that occur on some boards with newer versions of the U-Boot bootloader (because of bugs in newer versions of the DDR training algorithm).

| Field | Value |
|---|---|
| Version | 0.1 |
| License | GPL-2.0-or-later |
| Maintainer | Marek Behun <kabel@kernel.org> |
| Source URL | https://gitlab.nic.cz/turris/omnia-eeprom/-/archive/v$(PKG_VERSION)/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/omnia-eeprom
---

## omnia-mcutool

The omnia-mcutool utility is mainly used to upgrade the firmware on the microcontroller on the Turris Omnia router. It can also show state of MCU settings and configure MCU options (GPIOs, LEDs, power).

| Field | Value |
|---|---|
| License | GPL-2.0-or-later include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/omnia-mcutool SECTION:=utils CATEGORY:=Utilities URL:=https://gitlab.nic.cz/turris/$(PKG_NAME) TITLE:=CZ.NIC Turris Omnia MCU utility  |
| Maintainer | Marek Mojik <marek.mojik@nic.cz> |
| Source URL | https://gitlab.nic.cz/turris/$(PKG_NAME) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/omnia-mcutool
---

## osafeloader

This package contains an utility that allows handling SafeLoader images.


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/osafeloader
---

## policycoreutils

Policycoreutils is a collection of policy utilities (originally the "core" set of utilities needed to use SELinux, although it has grown a bit over time). This package provides the $(2) utility. endef

| Field | Value |
|---|---|
| Version | 3.9 |
| License | GPL-2.0-or-later |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/policycoreutils
---

## provision

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/provision SECTION:=utils CATEGORY:=Utilities TITLE:=Utility for managing device provisioning data DEPENDS:=+ucode +ucode-m |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/provision
---

## px5g-mbedtls

Px5g is a tiny standalone X.509 certificate generator. It suitable to create key files and certificates in DER and PEM format for use with stunnel, uhttpd and others.

| Field | Value |
|---|---|
| License | LGPL-2.1 |
| Maintainer | Jo-Philipp Wich <jo@mein.io> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/px5g-mbedtls SECTION:=utils CATEGORY:=Utilities SUBMENU:=Encryption TITLE:=X.509 certificate generator (using mbedtls) DEP |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/px5g-mbedtls
---

## px5g-wolfssl

Px5g is a tiny X.509 certificate generator. It suitable to create key files and certificates in DER and PEM format for use with stunnel, uhttpd and others.

| Field | Value |
|---|---|
| License | GPL-2.0-or-later |
| Maintainer | Paul Spooren <mail@aparcar.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/px5g-wolfssl
---

## ravpower-mcu

| Field | Value |
|---|---|
| License | GPL-2.0-or-later include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/ravpower-mcu SECTION:=utils CATEGORY:=Utilities TITLE:=Utility to control the RAVPower RP-WD009 PMIC URL:=https://github.com/blocktrro |
| Maintainer | David Bauer <mail@david-bauer.net> |
| Source URL | https://github.com/blocktrron/ravpower-mcu.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ravpower-mcu
---

## secilc

The SELinux CIL Compiler is a compiler that converts the CIL language as described on the CIL design wiki into a kernel binary policy file. Please see the CIL Design Wiki at: http://github.com/SELinuxProject/cil/wiki/ for more information about the goals and features on the CIL language.

| Field | Value |
|---|---|
| Version | 3.9 |
| License | BSD-2-Clause |
| Maintainer | Dominick Grift <dominick.grift@defensec.nl> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/secilc
---

## spidev_test

SPI testing utility.

| Field | Value |
|---|---|
| License | GPL-2.0-only include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/spidev-test SECTION:=utils CATEGORY:=Utilities DEPENDS:=+kmod-spi-dev TITLE:=SPI testing utility VERSION:=$(LINUX_VERSION)-r$(PKG_RELEASE) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/spidev_test
---

## ucode

ucode is a tiny script interpreter featuring an ECMAScript oriented script language and Jinja-inspired templating.

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | https://github.com/jow-/ucode.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ucode
---

## ucode-mod-bpf

The bpf plugin provides functionality for loading and interacting with eBPF modules. It allows loading full modules and pinned maps/programs and supports interacting with maps and attaching programs as tc classifiers.

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[nls.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/ucode-mod-bpf SECTION:=utils CATEGORY:=Utilities TITLE:=ucode eBPF module DEPENDS:=+libucode |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ucode-mod-bpf
---

## ucode-mod-pkgen

The pkgen module provides functionality for generating cryptographic keys and (self-)signed certificates. It supports exporting PEM/DER format files, as well as PKCS#12 bundle for client cert/key pairs with CA.

| Field | Value |
|---|---|
| License | GPL-2.0-or-later |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ucode-mod-pkgen
---

## ucode-mod-uline

This module provides similar functionality as libreadline for ucode, without depending on other libraries like ncurses.

| Field | Value |
|---|---|
| License | GPL-2.0-or-later |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ucode-mod-uline
---

## uencrypt

| Field | Value |
|---|---|
| License | GPL-2.0-or-later |
| Maintainer | Eneas U de Queiroz <cotequeiroz@gmail.com> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/uencrypt
---

## ugps

| Field | Value |
|---|---|
| License | GPL-2.0+ include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/ugps SECTION:=utils CATEGORY:=Utilities TITLE:=OpenWrt GPS Daemon DEPENDS:=+libubox +libubus endef |
| Maintainer | John Crispin <john@phrozen.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ugps
---

## usbgadget

This package contains the USB gadget preset for $(3). endef define Package/$(PKG_NAME)-$(1)/install $(INSTALL_DIR) $$(1)/usr/share/usbgadget $(INSTALL_CONF) ./files/presets/$(1) $$(1)/usr/share/usbgadget endef $$(eval $$(call BuildPackage,$(PKG_NAME)-$(1)))

| Field | Value |
|---|---|
| License | BSD-2-Clause |
| Maintainer | Chuanhong Guo <gch981213@gmail.com> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/$(PKG_NAME) SECTION:=utils CATEGORY:=Utilities DEPENDS:=@USB_GADGET_SUPPORT +kmod-usb-gadget +kmod-fs-configfs +kmo |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/usbgadget
---

## usbmode

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/usbmode
---

## util-linux

The libblkid library is used to identify block devices (disks) as to their content (e.g. filesystem type, partitions) as well as extracting additional information such as filesystem labels/volume names, partitions, unique identifiers/serial numbers...

| Field | Value |
|---|---|
| Version | 2.41.3 |
| Source URL | @KERNEL/linux/utils/$(PKG_NAME)/v2.41 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/util-linux
---

## yafut

A program for copying files from/to Yaffs file systems from userspace.

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Source URL | https://github.com/kempniu/yafut.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/yafut
---

## zyxel-bootconfig

This package contains an utility that allows handling Zyxel Bootconfig settings.


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/zyxel-bootconfig
---

## zyxel-bootconfig-ipq807x

This package contains an utility for handling Zyxel bootconfig settings on ipq807x devices.


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/zyxel-bootconfig-ipq807x
---
