---
title: 'OpenWrt Buildroot: firmware packages'
module: openwrt-core
origin_type: makefile_meta
token_count: 1435
version: a1f5273
source_file: L1-raw/openwrt-core/makefile_meta-category-firmware.md
last_pipeline_run: '2026-03-20T04:40:03.869041+00:00'
upstream_path: package/firmware
language: makefile
---
# OpenWrt Buildroot: firmware packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/firmware
---

## ath10k-ct-firmware

Alternative ath10k firmware for QCA9887 from Candela Technologies. Enables [IBSS](../wiki/wiki_page-techref-wireless-modes.md) and other features. See: http://www.candelatech.com/ath10k-10.1.php This firmware conflicts with the standard 9887 firmware, so select only one.

| Field | Value |
|---|---|
| Version | 2023.04.04 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/ath10k-ct-firmware
---

## ath11k-firmware

| Field | Value |
|---|---|
| Maintainer | Robert Marko <robimarko@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/makefile_meta-include-mk.md) |
| Source URL | https://git.codelinaro.org/clo/ath-firmware/ath11k-firmware.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/ath11k-firmware
---

## broadcom-sprom

| Field | Value |
|---|---|
| Maintainer | Álvaro Fernández Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/makefile_meta-include-mk.md) define Package/broadcom-sprom-default SECTION:=firmware CATEGORY:=Firmware endef define Build/Compile true endef # BCM4306  |
| Source URL | https://github.com/openwrt/broadcom-sprom.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/broadcom-sprom
---

## cypress-firmware

| Field | Value |
|---|---|
| Maintainer | Álvaro Fernández Rojas <noltari@gmail.com> |
| Source URL | https://github.com/Infineon/ifx-linux-firmware/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/cypress-firmware
---

## cypress-nvram

| Field | Value |
|---|---|
| Maintainer | Álvaro Fernández Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/makefile_meta-include-mk.md) define Package/cypress-nvram-default SECTION:=firmware CATEGORY:=Firmware endef define Build/Compile true endef # Cypress 4 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/cypress-nvram
---

## intel-microcode

| Field | Value |
|---|---|
| Version | 20260227 |
| Source URL | @DEBIAN/pool/non-free-firmware/i/intel-microcode/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/intel-microcode
---

## ipq-wifi

The $(2) requires board-specific, reference ("cal") data that is not yet present in the upstream wireless firmware distribution. This package supplies board-2.bin file(s) that, in the interim, overwrite those supplied by the ath10k-firmware-* packages. This is package is only necessary for the $(2). Do not install it for any other device! endef define Package/ipq-wifi-$(1)/install-overlay $$$$(foreach IPQ_WIFI_BOARD_FILE,$$$$(wildcard $(PKG_BUILD_DIR)/board-$(1).*), $$$$(call ipq-wifi-install-one,$$$$(IPQ_WIFI_BOARD_FILE),$$(1))) endef PREV_BOARD+=ipq-wifi-$(1)


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/ipq-wifi
---

## ixp4xx-microcode

This package contains the microcode needed to use the network engines in IXP4xx CPUs for ethernet on all three NPEs.

| Field | Value |
|---|---|
| Version | 2.4 |
| Source URL | http://downloads.openwrt.org/sources |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/ixp4xx-microcode
---

## linux-firmware

| Field | Value |
|---|---|
| Version | 20260309 |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | @KERNEL/linux/kernel/firmware |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/linux-firmware
---

## murata-firmware

| Field | Value |
|---|---|
| Maintainer | Thomas Richard <thomas.richard@bootlin.com> |
| Source URL | https://github.com/murata-wireless/cyw-fmac-fw.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/murata-firmware
---

## murata-nvram

| Field | Value |
|---|---|
| Maintainer | Thomas Richard <thomas.richard@bootlin.com> |
| Source URL | https://github.com/murata-wireless/cyw-fmac-nvram.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/murata-nvram
---

## omnia-mcu-firmware

Firmware binaries for the microcontroller on the Turris Omnia router. These are used by the omnia-mcutool utility when upgrading MCU firmware.

| Field | Value |
|---|---|
| Version | 4.1 |
| License | GPL-3.0-or-later |
| Maintainer | Marek Mojik <marek.mojik@nic.cz> |
| Source URL | https://gitlab.nic.cz/turris/hw/$(PKG_DISTNAME)/-/releases/v$(PKG_VERSION)/downloads/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/omnia-mcu-firmware
---

## prism54-firmware


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/prism54-firmware
---

## wireless-regdb

| Field | Value |
|---|---|
| Version | 2026.02.04 |
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/makefile_meta-include-mk.md) define Package/wireless-regdb PKGARCH:=all SECTION:=firmware CATEGORY:=Firmware URL:=https://git.kernel.org/pub/scm/linux/kernel/git/wens |
| Source URL | @KERNEL/software/network/wireless-regdb/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/wireless-regdb
---
