---
title: 'OpenWrt Buildroot: boot packages'
module: openwrt-core
origin_type: makefile_meta
token_count: 3710
source_file: L1-raw/openwrt-core/makefile_meta-category-boot.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/openwrt/blob/unknown/package/boot
source_locator: package/boot
language: makefile
ai_summary: The OpenWrt Buildroot boot packages module provides essential firmware components required for the boot process of various ARM-based devices. It includes several trusted firmware implementations for different hardware platforms, such as bcm63xx, mediatek, microchipsw, mvebu, rockchip, stm32, and sunxi. Each package is maintained by specific individuals and is sourced from respective repositories. The module facilitates the integration of these boot packages into the OpenWrt build system, ensuring compatibility and functionality across supported devices.
ai_when_to_use: Use this module when building OpenWrt firmware for ARM devices that require specific boot firmware. It is particularly useful for developers targeting various hardware platforms needing trusted firmware.
ai_related_topics:
- apex
- arm-trusted-firmware-bcm63xx
- arm-trusted-firmware-mediatek
- arm-trusted-firmware-microchipsw
- arm-trusted-firmware-mvebu
- arm-trusted-firmware-rockchip
- arm-trusted-firmware-stm32
- arm-trusted-firmware-sunxi
---

> **Source:** [https://github.com/openwrt/openwrt/blob/unknown/package/boot](https://github.com/openwrt/openwrt/blob/unknown/package/boot)
> **Kind:** makefile_meta | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

# OpenWrt Buildroot: boot packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/boot
---

## apex

| Field | Value |
|---|---|
| Version | 1.6.10-openwrt |
| License | GPL-2.0 |
| Source URL | https://github.com/linusw/apex.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/apex
---

## arm-trusted-firmware-bcm63xx

| Field | Value |
|---|---|
| Version | 2.2 |
| Maintainer | Rafał Miłecki <rafal@milecki.pl> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default PLAT:=bcm DEFAULT:=y  |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-bcm63xx
---

## arm-trusted-firmware-mediatek

| Field | Value |
|---|---|
| Maintainer | Daniel Golle <daniel@makrotopia.org> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=med |
| Source URL | https://github.com/mtk-openwrt/arm-trusted-firmware.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-mediatek
---

## arm-trusted-firmware-microchipsw

| Field | Value |
|---|---|
| Maintainer | Robert Marko <robert.marko@sartura.hr> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=m |
| Source URL | https://github.com/microchip-ung/arm-trusted-firmware.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-microchipsw
---

## arm-trusted-firmware-mvebu

| Field | Value |
|---|---|
| Version | 2.9 |
| Maintainer | Vladimir Vid <vladimir.vid@sartura.hr> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=m |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-mvebu
---

## arm-trusted-firmware-rockchip

| Field | Value |
|---|---|
| Version | 2.14.0 |
| Maintainer | Sarah Maedel <openwrt@tbspace.de> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default NAME:=Rockchip $(1)  |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-rockchip
---

## arm-trusted-firmware-stm32

| Field | Value |
|---|---|
| Version | 2.14 |
| Maintainer | Thomas Richard <thomas.richard@bootlin.com> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARG |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-stm32
---

## arm-trusted-firmware-sunxi

| Field | Value |
|---|---|
| Version | 2.14 |
| License | BSD-3-Clause |
| Maintainer | Hauke Mehrtens <hauke@hauke-m.de> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=sunxi  |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-sunxi
---

## arm-trusted-firmware-tools

| Field | Value |
|---|---|
| Version | 2.12 |
| Maintainer | Daniel Golle <daniel@makrotopia.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-tools
---

## at91bootstrap

| Field | Value |
|---|---|
| Version | v4.0.10 |
| Source URL | https://github.com/linux4sam/at91bootstrap.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/at91bootstrap
---

## fconfig

displays and (if writable) also edits the RedBoot configuration.

| Field | Value |
|---|---|
| Version | 20080329 |
| Source URL | @OPENWRT |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/fconfig
---

## grub2

Edit grub2 environment files.

| Field | Value |
|---|---|
| Version | 2.12 |
| License | GPL-3.0-or-later |
| Source URL | @GNU/grub |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/grub2
---

## imx-bootlets

i.MX23/i.MX28 bootlets (for oLinuxino)

| Field | Value |
|---|---|
| Version | 10.12.01 |
| Source URL | http://trabant.uid0.hu/openwrt/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/imx-bootlets
---

## kexec-tools

kexec is a set of system calls that allows you to load another kernel from the currently executing Linux kernel. The kexec utility allows to load and boot another kernel.

| Field | Value |
|---|---|
| Version | 2.0.32 |
| License | GPL-2.0-only |
| Source URL | @KERNEL/linux/utils/kernel/kexec |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/kexec-tools
---

## kobs-ng

The kobs-ng application writes a bootstream to [NAND](../../wiki/chunked-reference/wiki_page-techref-flash.md) flash with the proper FCB/DBBT headers and replicated streams.

| Field | Value |
|---|---|
| Version | 5.4 |
| License | GPLv2 |
| Source URL | http://www.freescale.com/lgfiles/NMG/MAD/YOCTO/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/kobs-ng
---

## mt7623n-preloader

Preloader image for mt7623n based boards like Banana Pi R2.

| Field | Value |
|---|---|
| Version | 2020-03-11 |
| Maintainer | David Woodhouse <dwmw2@infradead.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/mt7623n-preloader
---

## opensbi

| Field | Value |
|---|---|
| License | BSD-2-Clause |
| Maintainer | Zoltan HERPAI <wigyori@uid0.hu> include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/opensbi SECTION:=boot CATEGORY:=Boot Loaders DEPENDS:=@(TARGET_sifiveu||TARGET_d1) URL:=https://github.com/riscv/opensb |
| Source URL | https://github.com/riscv/opensbi |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/opensbi
---

## optee-os-stm32

| Field | Value |
|---|---|
| Version | 4.9.0 |
| Maintainer | Thomas Richard <thomas.richard@bootlin.com> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/optee-os-stm32
---

## rkbin

| Field | Value |
|---|---|
| Maintainer | Tianling Shen <cnsztl@immortalwrt.org> include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default NAME:=Rockchip  |
| Source URL | https://github.com/rockchip-linux/rkbin.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/rkbin
---

## tfa-layerscape

| Field | Value |
|---|---|
| Version | 6.12.20.2.0.0 |
| Source URL | https://github.com/nxp-qoriq/atf |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/tfa-layerscape
---

## uboot-airoha

| Field | Value |
|---|---|
| Version | 2026.01 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-airoha
---

## uboot-armsr

| Field | Value |
|---|---|
| Version | 2025.04 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-armsr
---

## uboot-at91

| Field | Value |
|---|---|
| Version | linux4sam-2022.04 |
| Source URL | https://github.com/linux4sam/u-boot-at91.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-at91
---

## uboot-ath79

| Field | Value |
|---|---|
| Version | 2025.10 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-ath79
---

## uboot-bcm4908

| Field | Value |
|---|---|
| Source URL | https://git.openwrt.org/project/bcm63xx/u-boot.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-bcm4908
---

## uboot-bcm53xx

| Field | Value |
|---|---|
| Version | 2025.10 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-bcm53xx
---

## uboot-bmips

| Field | Value |
|---|---|
| Version | 2024.04 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-bmips
---

## uboot-d1

| Field | Value |
|---|---|
| Version | 2024.01 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-d1
---

## uboot-fritz4040

| Field | Value |
|---|---|
| Source URL | https://github.com/chunkeey/FritzBox-4040-UBOOT |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-fritz4040
---

## uboot-imx

| Field | Value |
|---|---|
| Version | 2022.01 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-imx
---

## uboot-kirkwood

| Field | Value |
|---|---|
| Version | 2020.04 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-kirkwood
---

## uboot-lantiq

| Field | Value |
|---|---|
| Version | 2013.10 |

**README:**

# README
```markdown
# How to refresh patches

$ git clone git@github.com:danielschwierzeck/u-boot-lantiq.git
$ mkdir -p $OPENWRT_ROOT/packages/boot/uboot-lantiq/patches
$ cd u-boot-lantiq.git
$ git format-patch -p -k --no-renames --no-binary -o $OPENWRT_ROOT/package/boot/uboot-lantiq/patches v2013.10..u-boot-lantiq-v2013.10-openwrtN
```


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-lantiq
---

## uboot-layerscape

| Field | Value |
|---|---|
| Version | 6.12.20.2.0.0 |
| Source URL | https://github.com/nxp-qoriq/u-boot |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-layerscape
---

## uboot-mediatek

| Field | Value |
|---|---|
| Version | 2026.01 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-mediatek
---

## uboot-microchipsw

| Field | Value |
|---|---|
| Maintainer | Robert Marko <robert.marko@sartura.hr> include $(INCLUDE_DIR)/u-boot.mk include $(INCLUDE_DIR)/[package.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[kernel.mk](../../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define U-Boot/Default BUILD_TARGET:=microchipsw HIDDEN:=1 UBO |
| Source URL | https://github.com/microchip-ung/u-boot.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-microchipsw
---

## uboot-mvebu

| Field | Value |
|---|---|
| Version | 2026.01 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-mvebu
---

## uboot-mxs

| Field | Value |
|---|---|
| Version | 2020.04 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-mxs
---

## uboot-omap

| Field | Value |
|---|---|
| Version | 2021.07 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-omap
---

## uboot-qoriq

| Field | Value |
|---|---|
| Version | 2025.01 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-qoriq
---

## uboot-rockchip

| Field | Value |
|---|---|
| Version | 2026.01 |
| Maintainer | Sarah Maedel <openwrt@tbspace.de> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-rockchip
---

## uboot-sifiveu

| Field | Value |
|---|---|
| Version | 2023.10 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-sifiveu
---

## uboot-stm32

| Field | Value |
|---|---|
| Version | 2026.01 |
| Maintainer | Thomas Richard <thomas.richard@bootlin.com> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-stm32
---

## uboot-sunxi

| Field | Value |
|---|---|
| Version | 2025.10 |
| Maintainer | Zoltan HERPAI <wigyori@uid0.hu> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-sunxi
---

## uboot-tegra

| Field | Value |
|---|---|
| Version | 2025.04 |
| Maintainer | Tomasz Maciej Nowak <tmn505@gmail.com> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-tegra
---

## uboot-tools

dumpimage lists and extracts data from U-Boot images. If -l is specified, dumpimage lists the components in image.Otherwise, dumpimage extracts the component at position to outfile.

| Field | Value |
|---|---|
| Version | 2026.01 |
| License | GPL-2.0 GPL-2.0+ |
| Source URL | https://ftp.denx.de/pub/u-boot https://mirror.cyberbits.eu/u-boot ftp://ftp.denx.de/pub/u-boot |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-tools
---

## uboot-zynq

| Field | Value |
|---|---|
| Version | 2019.07 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/uboot-zynq
---
