---
module: openwrt-core
total_token_count: 23147
section_count: 7
is_monolithic: true
generated: '2026-03-20T01:28:16.926497+00:00'
---

# openwrt-core Bundled Reference

> **Contains:** 7 documents concatenated
> **Tokens:** ~23147 (cl100k_base)

---

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
| Maintainer | Rafał Miłecki <rafal@milecki.pl> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default PLAT:=bcm DEFAULT:=y  |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-bcm63xx
---

## arm-trusted-firmware-mediatek

| Field | Value |
|---|---|
| Maintainer | Daniel Golle <daniel@makrotopia.org> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=med |
| Source URL | https://github.com/mtk-openwrt/arm-trusted-firmware.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-mediatek
---

## arm-trusted-firmware-microchipsw

| Field | Value |
|---|---|
| Maintainer | Robert Marko <robert.marko@sartura.hr> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=m |
| Source URL | https://github.com/microchip-ung/arm-trusted-firmware.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-microchipsw
---

## arm-trusted-firmware-mvebu

| Field | Value |
|---|---|
| Version | 2.9 |
| Maintainer | Vladimir Vid <vladimir.vid@sartura.hr> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=m |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-mvebu
---

## arm-trusted-firmware-rockchip

| Field | Value |
|---|---|
| Version | 2.14.0 |
| Maintainer | Sarah Maedel <openwrt@tbspace.de> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default NAME:=Rockchip $(1)  |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-rockchip
---

## arm-trusted-firmware-stm32

| Field | Value |
|---|---|
| Version | 2.14 |
| Maintainer | Thomas Richard <thomas.richard@bootlin.com> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARG |


> Source: https://github.com/openwrt/openwrt/tree/master/package/boot/arm-trusted-firmware-stm32
---

## arm-trusted-firmware-sunxi

| Field | Value |
|---|---|
| Version | 2.14 |
| License | BSD-3-Clause |
| Maintainer | Hauke Mehrtens <hauke@hauke-m.de> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default BUILD_TARGET:=sunxi  |


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

The kobs-ng application writes a bootstream to [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash with the proper FCB/DBBT headers and replicated streams.

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
| Maintainer | Zoltan HERPAI <wigyori@uid0.hu> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/opensbi SECTION:=boot CATEGORY:=Boot Loaders DEPENDS:=@(TARGET_sifiveu||TARGET_d1) URL:=https://github.com/riscv/opensb |
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
| Maintainer | Tianling Shen <cnsztl@immortalwrt.org> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/trusted-firmware-a.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Trusted-Firmware-A/Default NAME:=Rockchip  |
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
| Maintainer | Robert Marko <robert.marko@sartura.hr> include $(INCLUDE_DIR)/u-boot.mk include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define U-Boot/Default BUILD_TARGET:=microchipsw HIDDEN:=1 UBO |
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

---

# OpenWrt Buildroot: firmware packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/firmware
---

## ath10k-ct-firmware

Alternative ath10k firmware for QCA9887 from Candela Technologies. Enables [IBSS](../wiki/chunked-reference/wiki_page-techref-wireless-modes.md) and other features. See: http://www.candelatech.com/ath10k-10.1.php This firmware conflicts with the standard 9887 firmware, so select only one.

| Field | Value |
|---|---|
| Version | 2023.04.04 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/ath10k-ct-firmware
---

## ath11k-firmware

| Field | Value |
|---|---|
| Maintainer | Robert Marko <robimarko@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) |
| Source URL | https://git.codelinaro.org/clo/ath-firmware/ath11k-firmware.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/ath11k-firmware
---

## broadcom-sprom

| Field | Value |
|---|---|
| Maintainer | Álvaro Fernández Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/broadcom-sprom-default SECTION:=firmware CATEGORY:=Firmware endef define Build/Compile true endef # BCM4306  |
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
| Maintainer | Álvaro Fernández Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/cypress-nvram-default SECTION:=firmware CATEGORY:=Firmware endef define Build/Compile true endef # Cypress 4 |


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
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/wireless-regdb PKGARCH:=all SECTION:=firmware CATEGORY:=Firmware URL:=https://git.kernel.org/pub/scm/linux/kernel/git/wens |
| Source URL | @KERNEL/software/network/wireless-regdb/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/firmware/wireless-regdb
---

---

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
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/button-hotplug SUBMENU:=Other modules TITLE:=Button Hotplug driver DEPENDS:=+kmod-input-core FILES:=$(PKG_BUILD_DIR)/button-hotplug.ko AU |


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
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/gpio-button-hotplug SUBMENU:=[GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) support TITLE:=Simple [GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) Button Hotplug driver FILES:=$(PKG_BUILD_DIR)/gpio-button-hotplug.ko AUTOLOA |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/gpio-button-hotplug
---

## gpio-nct5104d

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/gpio-nct5104d SUBMENU:=[GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) support TITLE:= [GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) nct5104d support DEPENDS:= @GPIO_SUPPORT @TARGET_x86 FILES:=$(PKG_BUILD_DIR)/gpio-nct510 |
| Maintainer | Florian Eckert <Eckert.Florian@googlemail.com> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/gpio-nct5104d
---

## leds-gca230718

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/leds-gca230718 SUBMENU:=LED modules TITLE:=GCA230718 LED support (e.g. for D-Link M30) FILES:= $(PKG_BUILD_DIR)/leds-gca230718.ko AUTOLOA |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/leds-gca230718
---

## leds-ws2812b

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/leds-ws2812b SUBMENU:=LED modules TITLE:=Worldsemi WS2812B (NeoPixel) LED support FILES:= $(PKG_BUILD_DIR)/leds-ws2812b.ko AUTOLOAD:=$(ca |


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
| Maintainer | Bjørn Mork <bjorn@mork.no> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/mt7621-qtn-rgmii SECTION:=kernel SUBMENU:=Other modules TITLE:=Enable RGMII connected Quantenna module on MT7621 DEPEN |


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
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/nat46 DEPENDS:=@IPV6 +kmod-nf-conntrack TITLE:=Stateless NAT46 translation kernel module SECTION:=kernel SUBMENU:=Network Support FILES:= |
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
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8101 SUBMENU:=Network Devices TITLE:=Realtek RTL8101 PCI Fast Ethern |
| Source URL | https://github.com/openwrt/rtl8101/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8101
---

## r8125

| Field | Value |
|---|---|
| Version | 9.016.01 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8125 SUBMENU:=Network Devices TITLE:=Realtek RTL8125 PCI 2.5 Gigabit |
| Source URL | https://github.com/openwrt/rtl8125/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8125
---

## r8126

| Field | Value |
|---|---|
| Version | 10.016.00 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8126 SUBMENU:=Network Devices TITLE:=Realtek RTL8126 PCI 5 Gigabit E |
| Source URL | https://github.com/openwrt/rtl8126/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8126
---

## r8127

| Field | Value |
|---|---|
| Version | 11.015.00 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8127 SUBMENU:=Network Devices TITLE:=Realtek RTL8127 PCI 10 Gigabit  |
| Source URL | https://github.com/openwrt/rtl8127/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/r8127
---

## r8168

| Field | Value |
|---|---|
| Version | 8.055.00 |
| License | GPLv2 |
| Maintainer | Alvaro Fernandez Rojas <noltari@gmail.com> include $(INCLUDE_DIR)/[kernel.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/r8168 SUBMENU:=Network Devices TITLE:=Realtek RTL8168 PCI Gigabit Eth |
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
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/leds-ubnt-ledbar SUBMENU:=LED modules TITLE:=Ubiquiti UniFi 6 LR LED support FILES:= $(PKG_BUILD_DIR)/leds-ubnt-ledbar.ko AUTOLOAD:=$(cal |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/ubnt-ledbar
---

## ubootenv-nvram

| Field | Value |
|---|---|
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define KernelPackage/ubootenv-nvram SUBMENU:=Other modules TITLE:=NVRAM environment for uboot-envtools FILES:=$(PKG_BUILD_DIR)/ubootenv-nvram.ko AUTOLOAD:=$(c |


> Source: https://github.com/openwrt/openwrt/tree/master/package/kernel/ubootenv-nvram
---

---

# OpenWrt Buildroot: libs packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/libs
---

## argp-standalone

GNU libc hierarchial argument parsing library broken out from glibc.

| Field | Value |
|---|---|
| Version | 1.3 |
| License | LGPL-2.1 |
| Maintainer | Ted Hess <thess@kitschensync.net> |
| Source URL | https://www.lysator.liu.se/~nisse/misc/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/argp-standalone
---

## elfutils

| Field | Value |
|---|---|
| Version | 0.192 |
| License | GPL-2.0-or-later LGPL-3.0-or-later |
| Maintainer | Luiz Angelo Daros de Luca <luizluca@gmail.com> |
| Source URL | https://sourceware.org/$(PKG_NAME)/ftp/$(PKG_VERSION) https://mirrors.kernel.org/sourceware/$(PKG_NAME)/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/elfutils
---

## gettext-full

| Field | Value |
|---|---|
| Version | 0.24.1 |
| License | LGPL-2.1-or-later |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | @GNU/gettext |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/gettext-full
---

## gmp

GMP is a free library for arbitrary precision arithmetic, operating on signed integers, rational numbers, and floating point numbers.

| Field | Value |
|---|---|
| Version | 6.3.0 |
| License | GPL-2.0-or-later |
| Source URL | @GNU/gmp/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/gmp
---

## gnulib-l10n

Localizations (translations) of messages for GNU gnulib code.

| Field | Value |
|---|---|
| Version | 20241231 |
| Source URL | @GNU/gnulib |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/gnulib-l10n
---

## jansson

Jansson is a C library for encoding, decoding and manipulating JSON data

| Field | Value |
|---|---|
| Version | 2.15.0 |
| License | MIT |
| Source URL | https://codeload.github.com/akheron/$(PKG_NAME)/tar.gz/v$(PKG_VERSION)? |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/jansson
---

## libbpf

libbpf is a library for loading eBPF programs and reading and manipulating eBPF objects from user-space.

| Field | Value |
|---|---|
| Version | 1.6.2 |
| Maintainer | Tony Ambardar <itugrok@yahoo.com> |
| Source URL | https://github.com/libbpf/libbpf |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libbpf
---

## libbsd

This library provides useful functions commonly found on BSD systems, and lacking on others like GNU systems, thus making it easier to port projects with strong BSD origins, without needing to embed the same code over and over again on each project.

| Field | Value |
|---|---|
| Version | 0.12.2 |
| License | BSD-4-Clause |
| Source URL | https://libbsd.freedesktop.org/releases |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libbsd
---

## libcap

$(call Package/libcap/description/Default) . This package contains the libcap utilities.

| Field | Value |
|---|---|
| Version | 2.69 |
| License | GPL-2.0-only |
| Maintainer | Paul Wassi <p.wassi@gmx.at> |
| Source URL | @KERNEL/linux/libs/security/linux-privs/libcap2 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libcap
---

## libevent2

$(call Package/libevent2/Default/description) This package contains the libevent shared library historically containing both the core & extra libraries.

| Field | Value |
|---|---|
| Version | 2.1.12 |
| License | BSD-3-Clause |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | https://github.com/libevent/libevent/releases/download/release-$(PKG_VERSION)-stable |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libevent2
---

## libiconv-full

| Field | Value |
|---|---|
| Version | 1.18 |
| License | LGPL-2.1-or-later |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | @GNU/libiconv |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libiconv-full
---

## libjson-c

This package contains a library for javascript object notation backends.

| Field | Value |
|---|---|
| Version | 0.18 |
| License | MIT |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://s3.amazonaws.com/json-c_releases/releases/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libjson-c
---

## libmd

This library provides message digest functions found on BSD systems either on their libc or libmd libraries and lacking on others like GNU systems, thus making it easier to port projects with strong BSD origins, without needing to embed the same code over and over again on each project.

| Field | Value |
|---|---|
| Version | 1.1.0 |
| License | BSD-3-Clause |
| Source URL | https://archive.hadrons.org/software/libmd/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libmd
---

## libmnl

libmnl is a minimalistic user-space library oriented to Netlink developers. There are a lot of common tasks in parsing, validating, constructing of both the Netlink header and TLVs that are repetitive and easy to get wrong. This library aims to provide simple helpers that allows you to re-use code and to avoid re-inventing the wheel. The main features of this library are: . * Small: the shared library requires around 30KB for an x86-based computer. . * Simple: this library avoids complexity and elaborated abstractions that tend to hide Netlink details. . * Easy to use: the library simplifies the work for Netlink-wise developers. It provides functions to make socket handling, message building, validating, parsing and sequence tracking, easier. . * Easy to re-use: you can use the library to build your own abstraction layer on top of this library. . * Decoupling: the interdependency of the main bricks that compose the library is reduced, i.e. the library provides many helpers, but the pro

| Field | Value |
|---|---|
| Version | 1.0.5 |
| License | LGPL-2.1+ |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | http://www.netfilter.org/projects/libmnl/files ftp://ftp.netfilter.org/pub/libmnl |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libmnl
---

## libnetfilter-conntrack

libnetfilter_conntrack is a userspace library providing a programming interface (API) to the in-kernel connection tracking state table. The library libnetfilter_conntrack has been previously known as libnfnetlink_conntrack and libctnetlink. This library is currently used by conntrack-tools among many other applications.

| Field | Value |
|---|---|
| Version | 1.1.0 |
| License | GPL-2.0-or-later |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | https://www.netfilter.org/projects/libnetfilter_conntrack/files |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnetfilter-conntrack
---

## libnfnetlink

libnfnetlink is is the low-level library for netfilter related kernel/userspace communication. It provides a generic messaging infrastructure for in-kernel netfilter subsystems (such as nfnetlink_log, nfnetlink_queue, nfnetlink_conntrack) and their respective users and/or management tools in userspace.

| Field | Value |
|---|---|
| Version | 1.0.2 |
| License | GPL-2.0+ |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | http://www.netfilter.org/projects/libnfnetlink/files/ ftp://ftp.netfilter.org/pub/libnfnetlink/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnfnetlink
---

## libnftnl

libnftnl is a userspace library providing a low-level netlink programming interface (API) to the in-kernel nf_tables subsystem.

| Field | Value |
|---|---|
| Version | 1.3.1 |
| License | GPL-2.0-or-later |
| Maintainer | Steven Barth <steven@midlink.org> |
| Source URL | https://netfilter.org/projects/$(PKG_NAME)/files |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnftnl
---

## libnl

Common code for all netlink libraries

| Field | Value |
|---|---|
| Version | 3.12.0 |
| License | LGPL-2.1 |
| Source URL | https://github.com/thom311/libnl/releases/download/libnl$(subst .,_,$(PKG_VERSION)) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnl
---

## libnl-tiny

This package contains a stripped down version of libnl

| Field | Value |
|---|---|
| License | LGPL-2.1 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/libnl-tiny SECTION:=libs CATEGORY:=Libraries TITLE:=netlink socket library ABI_VERSION:=1  |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnl-tiny
---

## libpcap

This package contains a system-independent library for user-level network packet capture.

| Field | Value |
|---|---|
| Version | 1.10.6 |
| License | BSD-3-Clause |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://www.tcpdump.org/release/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libpcap
---

## libselinux

libselinux is the runtime SELinux library that provides interfaces (e.g. library functions for the SELinux kernel APIs like getcon(), other support functions like getseuserbyname()) to SELinux-aware applications. libselinux may use the shared libsepol to manipulate the binary policy if necessary (e.g. to downgrade the policy format to an older version supported by the kernel) when loading policy.

| Field | Value |
|---|---|
| Version | 3.9 |
| License | libselinux-1.0 |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libselinux
---

## libsemanage

libsemanage is the policy management library. It uses libsepol for binary policy manipulation and libselinux for interacting with the SELinux system. It also exec's helper programs for loading policy and for checking whether the file_contexts configuration is valid (load_policy and setfiles from policycoreutils) presently, although this may change at least for the bootstrapping case (for rpm).

| Field | Value |
|---|---|
| Version | 3.9 |
| License | LGPL-2.1 |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libsemanage
---

## libsepol

Libsepol is the binary policy manipulation library. It doesn't depend upon or use any of the other SELinux components.

| Field | Value |
|---|---|
| Version | 3.9 |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libsepol
---

## libtool

| Field | Value |
|---|---|
| Version | 2.5.4 |
| License | GPL-2.0+ |
| Source URL | @GNU/libtool |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libtool
---

## libtraceevent

The libtraceevent library provides APIs to access kernel tracepoint events, located in the tracefs file system under the events directory.

| Field | Value |
|---|---|
| Version | 1.9.0 |
| Maintainer | Nick Hainke <vincent@systemli.org> |
| Source URL | https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/snapshot/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libtraceevent
---

## libtracefs

The libtracefs library provides APIs to access kernel trace file system.

| Field | Value |
|---|---|
| Version | 1.8.3 |
| Maintainer | Nick Hainke <vincent@systemli.org> |
| Source URL | https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/snapshot/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libtracefs
---

## libubox

Library for parsing and generating JSON from shell scripts

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libubox
---

## libunistring

This library provides functions for manipulating Unicode strings and for manipulating C strings according to the Unicode standard.

| Field | Value |
|---|---|
| Version | 1.4.2 |
| License | GPL-3.0 |
| Source URL | @GNU/$(PKG_NAME) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libunistring
---

## libunwind

Libunwind defines a portable and efficient C programming interface (API) to determine the call-chain of a program.

| Field | Value |
|---|---|
| Version | 1.8.3 |
| License | X11 |
| Maintainer | Yousong Zhou <yszhou4tech@gmail.com> |
| Source URL | https://github.com/libunwind/libunwind/releases/download/v$(PKG_VERSION)/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libunwind
---

## libusb

libusb is a C library that gives applications easy access to USB devices on many different operating systems.

| Field | Value |
|---|---|
| Version | 1.0.29 |
| License | LGPL-2.1-or-later |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://github.com/libusb/libusb/releases/download/v$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libusb
---

## libxml2

A library for manipulating XML and HTML resources.

| Field | Value |
|---|---|
| Version | 2.15.1 |
| License | MIT |
| Source URL | @GNOME/libxml2/$(basename $(PKG_VERSION)) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libxml2
---

## mbedtls

$(call Package/mbedtls/Default/description) This package contains the mbedtls library.

| Field | Value |
|---|---|
| Version | 3.6.5 |
| License | GPL-2.0-or-later |
| Source URL | https://github.com/Mbed-TLS/$(PKG_NAME)/releases/download/$(PKG_NAME)-$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/mbedtls
---

## mpfr

MPFR is a portable library written in C for arbitrary precision arithmetic on floating-point numbers. It is based on the GNU MP library. It aims to provide a class of floating-point numbers with precise semantics.

| Field | Value |
|---|---|
| Version | 4.2.2 |
| License | LGPL-3.0-or-later |
| Maintainer | Jeffery To <jeffery.to@gmail.com> |
| Source URL | @GNU/mpfr http://www.mpfr.org/mpfr-$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/mpfr
---

## musl-fts

The musl-fts package implements the fts(3) functions fts_open, fts_read, fts_children, fts_set and fts_close, which are missing in musl libc.

| Field | Value |
|---|---|
| Version | 1.2.7 |
| License | LGPL-2.1 |
| Maintainer | Lucian Cristian <lucian.cristian@gmail.com> |
| Source URL | https://github.com/pullmoll/musl-fts.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/musl-fts
---

## ncurses

| Field | Value |
|---|---|
| Version | 6.4 |
| License | MIT |
| Source URL | @GNU/$(PKG_NAME) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/ncurses
---

## nettle

| Field | Value |
|---|---|
| Version | 3.10.2 |
| License | GPL-2.0-or-later |
| Source URL | @GNU/nettle |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/nettle
---

## openssl

$(call Package/openssl/Default/description) This package contains the OpenSSL shared libraries, needed by other programs.

| Field | Value |
|---|---|
| Version | 3.5.5 |
| License | Apache-2.0 |
| Maintainer | Eneas U de Queiroz <cotequeiroz@gmail.com> |
| Source URL | https://www.openssl.org/source/ https://www.openssl.org/source/old/$(PKG_BASE)/ https://github.com/openssl/openssl/relea |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/openssl
---

## pcre2

| Field | Value |
|---|---|
| Version | 10.47 |
| License | BSD-3-Clause |
| Maintainer | Shane Peelar <lookatyouhacker@gmail.com> |
| Source URL | https://github.com/PCRE2Project/pcre2/releases/download/$(PKG_NAME)-$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/pcre2
---

## popt

| Field | Value |
|---|---|
| Version | 1.19 |
| License | MIT |
| Source URL | http://ftp.rpm.org/popt/releases/popt-1.x/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/popt
---

## readline

The Readline library provides a set of functions for use by applications that allow users to edit command lines as they are typed in. Both Emacs and vi editing modes are available. The Readline library includes additional functions to maintain a list of previously-entered command lines, to recall and perhaps reedit those lines, and perform csh-like history expansion on previous commands.

| Field | Value |
|---|---|
| Version | 8.3 |
| License | GPL-3.0-or-later |
| Source URL | @GNU/readline |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/readline
---

## sysfsutils

The library's purpose is to provide a consistant and stable interface for querying system device information exposed through sysfs.

| Field | Value |
|---|---|
| Version | 2.1.0 |
| License | LGPL-2.1 |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | @SF/linux-diag |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/sysfsutils
---

## toolchain

| Field | Value |
|---|---|
| License | GPL-3.0-with-GCC-exception |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/toolchain
---

## uclient

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/uclient
---

## udebug

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/libudebug SECTION:=libs CATEGORY:=Libraries TITLE:=udebug client library DEPENDS:=+libubox |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/udebug
---

## ustream-ssl

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/libustream/default SECTION:=libs CATEGORY:=Libraries TITLE:=ustream SSL Library DEPENDS:=+ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/ustream-ssl
---

## wolfssl

wolfSSL (formerly CyaSSL) is an SSL library optimized for small footprint, both on disk and for memory use.

| Field | Value |
|---|---|
| Version | 5.8.4 |
| License | GPL-3.0-or-later |
| Maintainer | Eneas U de Queiroz <cotequeiroz@gmail.com> |
| Source URL | https://github.com/wolfSSL/wolfssl/archive/v$(PKG_REAL_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/wolfssl
---

## zlib

zlib is a lossless data-compression library. This package includes the shared library.

| Field | Value |
|---|---|
| Version | 1.3.2 |
| License | Zlib |
| Source URL | https://github.com/madler/zlib/releases/download/v$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/zlib
---

---

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
| Maintainer | John Crispin <john@phrozen.org> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


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
| License | GPL-2.0 include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/openwrt-keyring SECTION:=base CATEGORY:=Base system PROVIDES:=lede-keyring TITLE:=OpenWrt Developer Keyring URL:=https://openwrt.org/docs/guide |
| Maintainer | John Crispin <john@phrozen.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/openwrt-keyring
---

## opkg

Lightweight package management system opkg is the opkg Package Management System, for handling installation and removal of packages on a system. It can recursively follow dependencies and download all packages necessary to install a particular package. opkg knows how to install both .ipk and .deb packages.

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Jo-Philipp Wich <jo@mein.io> # Extend depends from [version.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) |


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
| Maintainer | John Crispin <john@phrozen.org> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/ubox SECTION:=base CATEGORY:=Base system DEPENDS:=+libubox +ubusd +ubus +libubus +libuc |


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
| Maintainer | Daniel Golle <daniel@makrotopia.org> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/host-build.mk include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/ucert
---

## uci

| Field | Value |
|---|---|
| License | LGPL-2.1 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk # set to 1 to enable debugging |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/uci
---

## urandom-seed

| Field | Value |
|---|---|
| License | GPL-2.0-only include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/urandom-seed SECTION:=base CATEGORY:=Base system DEPENDS:=+getrandom TITLE:=/etc/urandom.seed handling for OpenWrt URL:=https://openwrt.or |


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
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/host-build.mk include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/usign
---

## zram-swap

A script to activate swaping on a compressed zram partition. This could be used to increase the available memory, by using compressed memory.


> Source: https://github.com/openwrt/openwrt/tree/master/package/system/zram-swap
---

---

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
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/cli SECTION:=utils CATEGORY:=Utilities TITLE:=OpenWrt CLI DEPENDS:=+ucode +ucode-mod-uline +ucode-mod-ubus +ucode-mod-uloo |


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
| Maintainer | Christian Marangi <ansuelsmth@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[meson.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/debugcc SECTION:=utils CATEGORY:=Utilities TITLE:=QCOM debugcc utility DEPENDS |
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

Release [uImage](../wiki/chunked-reference/wiki_page-techref-image-format.md).FIT block devices using ioctl.

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
| License | ISC include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/jsonfilter SECTION:=base CATEGORY:=Base system DEPENDS:=+libubox +libjson-c TITLE:=OpenWrt JSON filter utility URL: |
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
| Maintainer | John Crispin <john@phrozen.org> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/mtd-utils/Default SECTION:=utils CATEGORY:=Utilities URL:=http://www.linux-mtd.infradead.org/ DEPENDS:=@NAND_SUPPORT en |
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
| License | GPL-2.0-or-later include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/omnia-mcutool SECTION:=utils CATEGORY:=Utilities URL:=https://gitlab.nic.cz/turris/$(PKG_NAME) TITLE:=CZ.NIC Turris Omnia MCU utility  |
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
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/provision SECTION:=utils CATEGORY:=Utilities TITLE:=Utility for managing device provisioning data DEPENDS:=+ucode +ucode-m |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/provision
---

## px5g-mbedtls

Px5g is a tiny standalone X.509 certificate generator. It suitable to create key files and certificates in DER and PEM format for use with stunnel, uhttpd and others.

| Field | Value |
|---|---|
| License | LGPL-2.1 |
| Maintainer | Jo-Philipp Wich <jo@mein.io> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/px5g-mbedtls SECTION:=utils CATEGORY:=Utilities SUBMENU:=Encryption TITLE:=X.509 certificate generator (using mbedtls) DEP |


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
| License | GPL-2.0-or-later include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/ravpower-mcu SECTION:=utils CATEGORY:=Utilities TITLE:=Utility to control the RAVPower RP-WD009 PMIC URL:=https://github.com/blocktrro |
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
| License | GPL-2.0-only include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/spidev-test SECTION:=utils CATEGORY:=Utilities DEPENDS:=+kmod-spi-dev TITLE:=SPI testing utility VERSION:=$(LINUX_VERSION)-r$(PKG_RELEASE) |


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
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/[nls.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/ucode-mod-bpf SECTION:=utils CATEGORY:=Utilities TITLE:=ucode eBPF module DEPENDS:=+libucode |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ucode-mod-bpf
---

## ucode-mod-pkgen

The pkgen module provides functionality for generating cryptographic keys and (self-)signed certificates. It supports exporting PEM/DER format files, as well as PKCS#12 bundle for client cert/key pairs with CA.

| Field | Value |
|---|---|
| License | GPL-2.0-or-later |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ucode-mod-pkgen
---

## ucode-mod-uline

This module provides similar functionality as libreadline for ucode, without depending on other libraries like ncurses.

| Field | Value |
|---|---|
| License | GPL-2.0-or-later |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ucode-mod-uline
---

## uencrypt

| Field | Value |
|---|---|
| License | GPL-2.0-or-later |
| Maintainer | Eneas U de Queiroz <cotequeiroz@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/uencrypt
---

## ugps

| Field | Value |
|---|---|
| License | GPL-2.0+ include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/ugps SECTION:=utils CATEGORY:=Utilities TITLE:=OpenWrt GPS Daemon DEPENDS:=+libubox +libubus endef |
| Maintainer | John Crispin <john@phrozen.org> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/utils/ugps
---

## usbgadget

This package contains the USB gadget preset for $(3). endef define Package/$(PKG_NAME)-$(1)/install $(INSTALL_DIR) $$(1)/usr/share/usbgadget $(INSTALL_CONF) ./files/presets/$(1) $$(1)/usr/share/usbgadget endef $$(eval $$(call BuildPackage,$(PKG_NAME)-$(1)))

| Field | Value |
|---|---|
| License | BSD-2-Clause |
| Maintainer | Chuanhong Guo <gch981213@gmail.com> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) define Package/$(PKG_NAME) SECTION:=utils CATEGORY:=Utilities DEPENDS:=@USB_GADGET_SUPPORT +kmod-usb-gadget +kmod-fs-configfs +kmo |


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
