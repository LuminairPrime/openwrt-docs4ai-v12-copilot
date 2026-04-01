# openwrt-core Navigation Map

> **Contains:** Headers and function signatures for openwrt-core.
> **Generated:** 2026-04-01T11:39:51.401225+00:00

---

> **Summary:** The OpenWrt Buildroot boot packages module provides essential firmware components required for the boot process of various ARM-based devices. It includes several trusted firmware implementations for different hardware platforms, such as bcm63xx, mediatek, microchipsw, mvebu, rockchip, stm32, and sunxi. Each package is maintained by specific individuals and is sourced from respective repositories. The module facilitates the integration of these boot packages into the OpenWrt build system, ensuring compatibility and functionality across supported devices.
> **Use Case:** Use this module when building OpenWrt firmware for ARM devices that require specific boot firmware. It is particularly useful for developers targeting various hardware platforms needing trusted firmware.
# OpenWrt Buildroot: boot packages
## apex
## arm-trusted-firmware-bcm63xx
## arm-trusted-firmware-mediatek
## arm-trusted-firmware-microchipsw
## arm-trusted-firmware-mvebu
## arm-trusted-firmware-rockchip
## arm-trusted-firmware-stm32
## arm-trusted-firmware-sunxi
## arm-trusted-firmware-tools
## at91bootstrap
## fconfig
## grub2
## imx-bootlets
## kexec-tools
## kobs-ng
## mt7623n-preloader
## opensbi
## optee-os-stm32
## rkbin
## tfa-layerscape
## uboot-airoha
## uboot-armsr
## uboot-at91
## uboot-ath79
## uboot-bcm4908
## uboot-bcm53xx
## uboot-bmips
## uboot-d1
## uboot-fritz4040
## uboot-imx
## uboot-kirkwood
## uboot-lantiq
# README
# How to refresh patches
## uboot-layerscape
## uboot-mediatek
## uboot-microchipsw
## uboot-mvebu
## uboot-mxs
## uboot-omap
## uboot-qoriq
## uboot-rockchip
## uboot-sifiveu
## uboot-stm32
## uboot-sunxi
## uboot-tegra
## uboot-tools
## uboot-zynq

# OpenWrt Buildroot: firmware packages
## ath10k-ct-firmware
## ath11k-firmware
## broadcom-sprom
## cypress-firmware
## cypress-nvram
## intel-microcode
## ipq-wifi
## ixp4xx-microcode
## linux-firmware
## murata-firmware
## murata-nvram
## omnia-mcu-firmware
## prism54-firmware
## wireless-regdb

> **Summary:** The OpenWrt Buildroot kernel packages module provides a collection of kernel-related packages essential for various hardware functionalities. It includes drivers and firmware for specific devices, such as ath10k-ct for Qualcomm Atheros chipsets and bcm27xx-gpu-fw for Raspberry Pi GPU support. Other packages like button-hotplug and gpio-button-hotplug facilitate button handling and GPIO support, respectively. Each package is maintained by specific contributors and is available through designated source URLs.
> **Use Case:** Use this module when building custom OpenWrt firmware that requires specific kernel drivers or firmware for hardware support. It is particularly useful for developers targeting embedded devices with unique hardware requirements.
# OpenWrt Buildroot: kernel packages
## ath10k-ct
## bcm27xx-gpu-fw
## bcm63xx-cfe
## bpf-headers
## button-hotplug
## cryptodev-linux
## econet-eth
## gpio-button-hotplug
## gpio-nct5104d
## leds-gca230718
## leds-ws2812b
## linux
## mac80211
## mt76
## mt7621-qtn-rgmii
## mwlwifi
## nat46
## qca-nss-dp
## qca-ssdk
## r8101
## r8125
## r8126
## r8127
## r8168
## rtc-rv5c386a
## rtl8812au-ct
## trelay
## ubnt-ledbar
## ubootenv-nvram

# OpenWrt Buildroot: libs packages
## argp-standalone
## elfutils
## gettext-full
## gmp
## gnulib-l10n
## jansson
## libbpf
## libbsd
## libcap
## libevent2
## libiconv-full
## libjson-c
## libmd
## libmnl
## libnetfilter-conntrack
## libnfnetlink
## libnftnl
## libnl
## libnl-tiny
## libpcap
## libselinux
## libsemanage
## libsepol
## libtool
## libtraceevent
## libtracefs
## libubox
## libunistring
## libunwind
## libusb
## libxml2
## mbedtls
## mpfr
## musl-fts
## ncurses
## nettle
## openssl
## pcre2
## popt
## readline
## sysfsutils
## toolchain
## uclient
## udebug
## ustream-ssl
## wolfssl
## zlib

> **Summary:** The OpenWrt Buildroot system packages module provides a collection of essential packages for system management and functionality within the OpenWrt environment. Key packages include 'opkg', a lightweight package management system that handles installation and removal of packages, and 'ca-certificates', which ensures secure connections by providing trusted CA certificates. Other notable packages are 'fstools' for filesystem management, 'fwtool' for firmware upgrades, and 'mtd' for managing flash memory devices. Each package is maintained by specific developers and is available from designated source URLs.
> **Use Case:** This module is particularly useful when building custom OpenWrt firmware images that require specific system functionalities or package management capabilities.
# OpenWrt Buildroot: system packages
## apk
## ca-certificates
## fstools
## fwtool
## iucode-tool
## mtd
## openwrt-keyring
## opkg
## procd
## refpolicy
## rpcd
## selinux-policy
## ubox
## ubus
## ucert
## uci
## urandom-seed
## urngd
## usign
## zram-swap

> **Summary:** The OpenWrt Buildroot utils packages module provides a collection of utility tools and libraries for embedded Linux systems. Key components include Android Debug Bridge (adb) for device communication, audit libraries for security auditing, and various utilities for specific hardware like BCM27xx and BCM4908. Additionally, it includes essential tools like busybox for command-line operations and bzip2 for data compression. Each package is maintained by specific contributors and has its own versioning and licensing details.
> **Use Case:** Use this module when you need to integrate utility packages into your OpenWrt build for enhanced functionality or specific hardware support.
# OpenWrt Buildroot: utils packages
## adb
## audit
## bcm27xx-utils
## bcm4908img
## bsdiff
## busybox
## bzip2
## checkpolicy
## cli
## ct-bugcheck
## debugcc
## dns320l-mcu
## dtc
## e2fsprogs
## f2fs-tools
## fbtest
## firmware-utils
## fitblk
## fritz-tools
# README
## Building
## Usage
## LICENSE
## jboot-tools
# README
## Building
## Usage
## LICENSE
## jsonfilter
## lua
## lua5.3
## mdadm
## mtd-utils
## nilfs-utils
## nvram
## omnia-eeprom
## omnia-mcutool
## osafeloader
## policycoreutils
## provision
## px5g-mbedtls
## px5g-wolfssl
## ravpower-mcu
## secilc
## spidev_test
## ucode
## ucode-mod-bpf
## ucode-mod-pkgen
## ucode-mod-uline
## uencrypt
## ugps
## usbgadget
## usbmode
## util-linux
## yafut
## zyxel-bootconfig
## zyxel-bootconfig-ipq807x

> **Summary:** The OpenWrt Buildroot includes a collection of Makefile fragments that are essential for the build system. These fragments, such as autotools.mk, debug.mk, and download.mk, provide various functionalities including package configuration, dependency management, and download handling. Each fragment is designed to streamline the build process for OpenWrt packages, ensuring that developers can efficiently compile and manage their software. The documentation for each file is available in the OpenWrt GitHub repository.
> **Use Case:** Use these include files when developing or modifying packages for OpenWrt to leverage the predefined build system functionalities.
# OpenWrt Buildroot: Build System Include Files
## autotools.mk
# Documentation
## debug.mk
# Documentation
## depends.mk
# Documentation
## download.mk
# Documentation
## feeds.mk
# Documentation
## hardening.mk
# Documentation
## host-build.mk
# Documentation
## image.mk
# Documentation
## kernel-build.mk
# Documentation
## kernel-defaults.mk
# Documentation
## kernel.mk
# Documentation
## meson.mk
# Documentation
## netfilter.mk
# Documentation
## nls.mk
# Documentation
## openssl-module.mk
# Documentation
## package-bin.mk
# Documentation
## package-defaults.mk
# Documentation
## package-dumpinfo.mk
# Documentation
## package-pack.mk
# Documentation
## package-seccomp.mk
# Documentation
## package.mk
# Documentation
## prereq-build.mk
# Documentation
## prereq.mk
# Documentation
## quilt.mk
# Documentation
## subdir.mk
# Documentation
## target.mk
# Documentation
## toolchain-build.mk
# Documentation
## toplevel.mk
# Documentation
## unpack.mk
# Documentation
## verbose.mk
# Documentation
## version.mk
# Documentation
