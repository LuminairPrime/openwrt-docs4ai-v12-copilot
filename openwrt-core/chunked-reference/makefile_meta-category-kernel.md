---
title: 'OpenWrt Buildroot: kernel packages'
module: openwrt-core
origin_type: makefile_meta
token_count: 2744
source_file: L1-raw/openwrt-core/makefile_meta-category-kernel.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/openwrt/blob/unknown/package/kernel
source_locator: package/kernel
language: makefile
ai_summary: The OpenWrt Buildroot kernel packages module provides a collection of kernel-related packages essential for various hardware functionalities. It includes drivers and firmware for specific devices, such as ath10k-ct for Qualcomm Atheros chipsets and bcm27xx-gpu-fw for Raspberry Pi GPU support. Other packages like button-hotplug and gpio-button-hotplug facilitate button handling and GPIO support, respectively. Each package is maintained by specific contributors and is available through designated source URLs.
ai_when_to_use: Use this module when building custom OpenWrt firmware that requires specific kernel drivers or firmware for hardware support. It is particularly useful for developers targeting embedded devices with unique hardware requirements.
ai_related_topics:
- ath10k-ct
- bcm27xx-gpu-fw
- bcm63xx-cfe
- bpf-headers
- button-hotplug
- cryptodev-linux
- econet-eth
- gpio-button-hotplug
- gpio-nct5104d
- leds-gca230718
- leds-ws2812b
---

> **Source:** [https://github.com/openwrt/openwrt/blob/unknown/package/kernel](https://github.com/openwrt/openwrt/blob/unknown/package/kernel)
> **Kind:** makefile_meta | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-04-01

# OpenWrt Buildroot: kernel packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/kernel
---

## ath10k-ct

| Field | Value |
|---|---|
| License | GPLv2 |
| Maintainer | Ben Greear <greearb@candelatech.com> |
| Source URL | https://github.com/greearb/ath10k-ct.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/ath10k-ct
---

## bcm27xx-gpu-fw

GPU and kernel boot firmware for bcm27xx.

| Field | Value |
|---|---|
| Version | 2025.04.30 |
| Source URL | https://github.com/raspberrypi/firmware/releases/download/$(PKG_VERSION_REAL) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/bcm27xx-gpu-fw
---

## bcm63xx-cfe

CFE RAM binaries for bcm63xx.

| Field | Value |
|---|---|
| Source URL | https://github.com/openwrt/bcm63xx-cfe.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/bcm63xx-cfe
---

## bpf-headers

| Field | Value |
|---|---|
| Source URL | @KERNEL/linux/kernel/v$(word 1,$(subst ., ,$(PKG_PATCHVER))).x |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/bpf-headers
---

## button-hotplug

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/button-hotplug SUBMENU:=Other modules TITLE:=Button Hotplug driver DEPENDS:=+kmod-input-core FILES:=$(PKG_BUILD_DIR)/button-hotplug.ko AU |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/button-hotplug
---

## cryptodev-linux

| Field | Value |
|---|---|
| Version | 1.14 |
| License | GPL-2.0 |
| Maintainer | Ansuel Smith <ansuelsmth@gmail.com> |
| Source URL | https://codeload.github.com/$(PKG_NAME)/$(PKG_NAME)/tar.gz/$(PKG_NAME)-$(PKG_VERSION)? |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/cryptodev-linux
---

## econet-eth

| Field | Value |
|---|---|
| Source URL | https://github.com/cjdelisle/econet_eth.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/econet-eth
---

## gpio-button-hotplug

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/gpio-button-hotplug SUBMENU:=[GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) support TITLE:=Simple [GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) Button Hotplug driver FILES:=$(PKG_BUILD_DIR)/gpio-button-hotplug.ko AUTOLOA |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/gpio-button-hotplug
---

## gpio-nct5104d

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/gpio-nct5104d SUBMENU:=[GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) support TITLE:= [GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) nct5104d support DEPENDS:= @GPIO_SUPPORT @TARGET_x86 FILES:=$(PKG_BUILD_DIR)/gpio-nct510 |
| Maintainer | Florian Eckert <Eckert.Florian@googlemail.com> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/gpio-nct5104d
---

## leds-gca230718

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/leds-gca230718 SUBMENU:=LED modules TITLE:=GCA230718 LED support (e.g. for D-Link M30) FILES:= $(PKG_BUILD_DIR)/leds-gca230718.ko AUTOLOA |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/leds-gca230718
---

## leds-ws2812b

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/leds-ws2812b SUBMENU:=LED modules TITLE:=Worldsemi WS2812B (NeoPixel) LED support FILES:= $(PKG_BUILD_DIR)/leds-ws2812b.ko AUTOLOAD:=$(ca |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/leds-ws2812b
---

## linux

| Field | Value |
|---|---|
| License | GPL-2.0-only |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/linux
---

## mac80211

| Field | Value |
|---|---|
| Version | 6.18.7 |
| License | GPL-2.0-only |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://github.com/openwrt/backports/releases/download/backports-v$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/mac80211
---

## mt76

| Field | Value |
|---|---|
| License | BSD-3-Clause-Clear |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://github.com/openwrt/mt76 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/mt76
---

## mt7621-qtn-rgmii

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Bjørn Mork <bjorn@mork.no> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/mt7621-qtn-rgmii SECTION:=kernel SUBMENU:=Other modules TITLE:=Enable RGMII connected Quantenna module on MT7621 DEPEN |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/mt7621-qtn-rgmii
---

## mwlwifi

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Imre Kaloz <kaloz@openwrt.org> |
| Source URL | https://github.com/kaloz/mwlwifi |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/mwlwifi
---

## nat46

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/nat46 DEPENDS:=@IPV6 +kmod-nf-conntrack TITLE:=Stateless NAT46 translation kernel module SECTION:=kernel SUBMENU:=Network Support FILES:= |
| Maintainer | Hans Dedecker <dedeckeh@gmail.com> |
| Source URL | https://github.com/ayourtch/nat46.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/nat46
---

## qca-nss-dp

| Field | Value |
|---|---|
| Source URL | https://github.com/openwrt/qca-nss-dp.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/qca-nss-dp
---

## qca-ssdk

| Field | Value |
|---|---|
| Source URL | https://github.com/openwrt/qca-ssdk.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/qca-ssdk
---

## r8101

| Field | Value |
|---|---|
| Version | 1.039.00 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8101 SUBMENU:=Network Devices TITLE:=Realtek RTL8101 PCI Fast Ethern |
| Source URL | https://github.com/openwrt/rtl8101/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8101
---

## r8125

| Field | Value |
|---|---|
| Version | 9.016.01 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8125 SUBMENU:=Network Devices TITLE:=Realtek RTL8125 PCI 2.5 Gigabit |
| Source URL | https://github.com/openwrt/rtl8125/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8125
---

## r8126

| Field | Value |
|---|---|
| Version | 10.016.00 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8126 SUBMENU:=Network Devices TITLE:=Realtek RTL8126 PCI 5 Gigabit E |
| Source URL | https://github.com/openwrt/rtl8126/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8126
---

## r8127

| Field | Value |
|---|---|
| Version | 11.015.00 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8127 SUBMENU:=Network Devices TITLE:=Realtek RTL8127 PCI 10 Gigabit  |
| Source URL | https://github.com/openwrt/rtl8127/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8127
---

## r8168

| Field | Value |
|---|---|
| Version | 8.055.00 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8168 SUBMENU:=Network Devices TITLE:=Realtek RTL8168 PCI Gigabit Eth |
| Source URL | https://github.com/openwrt/rtl8168/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8168
---

## rtc-rv5c386a


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/rtc-rv5c386a
---

## rtl8812au-ct

| Field | Value |
|---|---|
| License | GPLv2 |
| Maintainer | Ben Greear <greearb@candelatech.com> |
| Source URL | https://github.com/greearb/rtl8812AU_8821AU_linux.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/rtl8812au-ct
---

## trelay


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/trelay
---

## ubnt-ledbar

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/leds-ubnt-ledbar SUBMENU:=LED modules TITLE:=Ubiquiti UniFi 6 LR LED support FILES:= $(PKG_BUILD_DIR)/leds-ubnt-ledbar.ko AUTOLOAD:=$(cal |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/ubnt-ledbar
---

## ubootenv-nvram

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/ubootenv-nvram SUBMENU:=Other modules TITLE:=NVRAM environment for uboot-envtools FILES:=$(PKG_BUILD_DIR)/ubootenv-nvram.ko AUTOLOAD:=$(c |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/ubootenv-nvram
---
