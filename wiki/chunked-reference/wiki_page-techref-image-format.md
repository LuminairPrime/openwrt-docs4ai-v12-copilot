---
title: Image formats
module: wiki
origin_type: wiki_page
token_count: 1610
source_file: L1-raw/wiki/wiki_page-techref-image-format.md
last_pipeline_run: '2026-04-01T13:49:08.540826+00:00'
source_url: https://openwrt.org/docs/techref/image.format
language: text
ai_summary: The Image formats module provides an overview of various firmware types and their respective file extensions used in OpenWrt. It categorizes these formats into standard and specific types, detailing their usage scenarios such as factory images for OEM flashing and sysupgrade images for upgrading existing OpenWrt installations. Additional formats like ext4, squashfs, and initramfs are explained, highlighting their characteristics and typical applications. The document also includes information on developer files and example firmware image names for different targets.
ai_when_to_use: This module is useful when determining the correct firmware image format to use for flashing or upgrading OpenWrt on various devices. It is particularly relevant for developers and users looking to understand the implications of different firmware types.
ai_related_topics:
- factory
- sysupgrade
- ext4
- squashfs
- initramfs
- sdcard.img.gz
- rootfs
- kernel
- u-boot
- ubinized.bin
- uImage
- zImage
- sdk
- Imagebuilder
- vmlinux
---

> **Source:** [https://openwrt.org/docs/techref/image.format](https://openwrt.org/docs/techref/image.format)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-04-01

# Image formats

 You can help to improve this page by adding explanations for the different firmware types below.

If you are confused by the many different firmware types and extensions in the [OpenWrt firmware downloads](/toh/views/toh_fwdownload) table, this pages tries to explain a bit about this topic.

## Standard formats

### factory (.img/.bin)

Use when flashing from OEM ( non-openwrt ) [^1]

If only a sysupgrade image is available for your router, either the router is already running some kind of OpenWrt fork (which understands the sysupgrade format natively) or web flash via the OEM UI is not possible... Please consult the Table of Hardware for your device for installation instructions from OEM firmware.

### sysupgrade ( or trx )

Previously known as *trx image*, *sysupgrade* is designed to be flashed from OpenWrt/LEDE itself [^2]. Commonly used when upgrading.

## Specific formats

### ext4

This firmware contains a regular ext4 Linux partition. Mostly used in x86 and x86_x64 systems.

### squashfs

This firmware contains a type of partition that is compressed and mounts read-only. All modifications (file edit, new files, deleted files) are committed to an overlay. .bin/.chk/.trx

- See also [TRX vs. TRX2 vs. BIN](/docs/techref/headers)

### initramfs

Can be loaded from an arbitrary location ( most often tftp ) and is self-contained in memory. This is like a Linux LiveCD. Often used to test firmware, as the first part of a multi-stage installation or as a recovery tool. [^3]

An initramfs and initrd are basically the same. It’s a filesystem in memory, which contains userland software. In an embedded environment it might contain the whole distro, on bigger systems it can contain tools&scripts to assemble&mount raid arrays and stuff like that before passing userland boot to them. Both can have a uHeader, to let uBoot know what it is.

The initramfs-kernel image is used for development or special situations as a one-time boot as a stepping stone toward installing the regular sysupgrade version. Since the initramfs version runs entirely from RAM, it does not store any settings in flash, so it is not suitable for operational use.

initramfs-uImage.bin: initramfs-kernel.bin:

### sdcard.img.gz

Used by few devices ( mvebu/RPi etc. ), most often a multi partition image which is uncompressed and written to external storage via PC.

### rootfs

Only the root filesystem.

### kernel

Linux core, generally without compression or appended headers.

### ubifs

??

### ubi

??

### tftp

Designed to be loaded from tftp server. Device in recovery mode?

### u-boot

This is an image format designed for U-Boot loader. Same as initramfs-or-uImage?

### ubinized.bin

### uImage

This is an image format designed for U-Boot loader, generally consisting of a kernel with a header for information. Often a zImage with a 64 byte uImage header, which contains the load address & entry point of the zImage, so that uBoot knows what to do with it. Further is contains a description of the actual contents (linux kernel, version, …)

### zImage

zImage is a compressed plain kernel with a ‘pyggyback’. Some extra code which can decompress the kernel before booting it.

## Subformats

### bin, img, elf, dtb, chk, dlf

These are raw binary data of the firmware file

### xz, gz, tar, lzma

These are compressed images

## Developer files

### sdk

SDK Toolchain for compiling single userspace packages [^4]

### Imagebuilder

To build custom images without compiling [^5]

### vmlinux

Linux kernel for build [^6]

# Example Firmware image names

## Firmware types

| Target | Install | Upgrade |
| --- | --- | --- |
| adm5120 | squashfs.bin | squashfs.bin |
| apm821xx | squashfs-factory.img; initramfs-kernel.bin | squashfs-sysupgrade.tar; ext4-rootfs.img.gz |
| ar7 | squashfs.bin; squashfs-code.bin | squashfs.bin |
| ar71xx | factory.img; factory.bin | sysupgrade.bin |
| at91 |   |   |
| atheros | squashfs-factory.bin | squashfs-sysupgrade.tar |
| brcm2708 | ext4-sdcard.img.gz | - |
| brcm47xx | squashfs.bin; squashfs.chk; squashfs.trx | squashfs.bin; squashfs.chk; squashfs.trx |
| bcm53xx | squashfs.bin; squashfs.chk; squashfs.trx | squashfs.chk; squashfs.trx |
| brcm63xx | squashfs-cfe.bin; squashfs-factory.chk | squashfs-sysupgrade.bin |
| cns3xxx | - | sysupgrade.bin |
| imx6 | ? | ? |
| ipq806x | factory.img | sysupgrade.tar |
| ixp4xx | squashfs.bin; squashfs.img; zImage | squashfs-sysupgrade.bin |
| kirkwood | squashfs-factory.bin | squashfs-sysupgrade.bin |
| lantiq | initramfs-kernel.bin; squashfs-factory.bin | squashfs-sysupgrade.bin |
| layerscape | squashfs-firmware.bin | - |
| mpc85xx | squashfs-factory.bin | squashfs-sysupgrade.bin |
| mvebu | sdcard.img.gz; squashfs-factory.img | squashfs-sysupgrade.bin |
| mxs | ? | ? |
| orion | not supported | not supported |
| oxnas | squashfs-ubinized.bin; ubifs-ubinized.bin | squashfs-sysupgrade.tar; ubifs-sysupgrade.tar |
| ramips | initramfs-kernel.bin; squashfs-factory.bin; squashfs-factory.dlf; initramfs-uImage.bin | squashfs-sysupgrade.bin; squashfs-sysupgrade.tar |
| sunxi | ext4-sdcard.img.gz; squashfs-sdcard.img.gz |   |
| x86 | combined-ext4.img | combined-ext4.img.gz |

# Image Formats General

This article describes and links to the various factory firmware image formats found.

For OpenWrt Flash Layout see: [flash.layout](/docs/techref/flash.layout).

[Binwalk](https://github.com/ReFirmLabs/binwalk) can help to analyze unknown formats.

## Known Formats

by extension:

- BIN
- CHK
- DLF
- IMG
- TRX

## Other Formats

- see [brcm63xx.imagetag](/docs/techref/brcm63xx.imagetag)
- see [headers](/docs/techref/headers)

[^1]: [before.installation](/docs/guide-user/installation/before.installation)

[^2]: [before.installation](/docs/guide-user/installation/before.installation)

[^3]: <https://forum.lede-project.org/t/toward-a-good-flashing-lede-instructions-page/52/5>

[^4]: <https://we.riseup.net/lackof/openwrt-on-x86-64>

[^5]: <https://we.riseup.net/lackof/openwrt-on-x86-64>

[^6]: <https://we.riseup.net/lackof/openwrt-on-x86-64>
