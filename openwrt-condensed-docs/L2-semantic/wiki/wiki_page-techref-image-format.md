---
title: Image formats
module: wiki
origin_type: wiki_page
token_count: 2236
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-image-format.md
last_pipeline_run: '2026-03-09T17:28:41.757217+00:00'
language: text
---
# Image formats

\<WRAP center round info 50%\> You can help to improve this page by adding explanations for the different firmware types below.  
\</WRAP\>

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

\<color \#ed1c24\>??\</color\>

### ubi

\<color \#ed1c24\>??\</color\>

### tftp

\<color \#ed1c24\>Designed to be loaded from tftp server. Device in recovery mode?\</color\>

### u-boot

\<color \#ed1c24\>This is an image format designed for U-Boot loader. Same as initramfs-or-uImage?\</color\>

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

<table>
<thead>
<tr class="header">
<th>Target</th>
<th>Install</th>
<th>Upgrade</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>adm5120</td>
<td>squashfs.bin</td>
<td>squashfs.bin</td>
</tr>
<tr class="even">
<td>apm821xx</td>
<td>squashfs-factory.img<br />
initramfs-kernel.bin</td>
<td>squashfs-sysupgrade.tar<br />
ext4-rootfs.img.gz</td>
</tr>
<tr class="odd">
<td>ar7</td>
<td>squashfs.bin<br />
squashfs-code.bin</td>
<td>squashfs.bin</td>
</tr>
<tr class="even">
<td>ar71xx</td>
<td>factory.img<br />
factory.bin</td>
<td>sysupgrade.bin</td>
</tr>
<tr class="odd">
<td>at91</td>
<td></td>
<td></td>
</tr>
<tr class="even">
<td>atheros</td>
<td>squashfs-factory.bin</td>
<td>squashfs-sysupgrade.tar</td>
</tr>
<tr class="odd">
<td>brcm2708</td>
<td>ext4-sdcard.img.gz</td>
<td>-</td>
</tr>
<tr class="even">
<td>brcm47xx</td>
<td>squashfs.bin<br />
squashfs.chk<br />
squashfs.trx</td>
<td>squashfs.bin<br />
squashfs.chk<br />
squashfs.trx</td>
</tr>
<tr class="odd">
<td>bcm53xx</td>
<td>squashfs.bin<br />
squashfs.chk<br />
squashfs.trx</td>
<td><br />
squashfs.chk<br />
squashfs.trx</td>
</tr>
<tr class="even">
<td>brcm63xx</td>
<td>squashfs-cfe.bin<br />
squashfs-factory.chk</td>
<td>squashfs-sysupgrade.bin</td>
</tr>
<tr class="odd">
<td>cns3xxx</td>
<td>-</td>
<td>sysupgrade.bin</td>
</tr>
<tr class="even">
<td>imx6</td>
<td>?</td>
<td>?</td>
</tr>
<tr class="odd">
<td>ipq806x</td>
<td>factory.img</td>
<td>sysupgrade.tar</td>
</tr>
<tr class="even">
<td>ixp4xx</td>
<td>squashfs.bin<br />
squashfs.img<br />
zImage</td>
<td>squashfs-sysupgrade.bin</td>
</tr>
<tr class="odd">
<td>kirkwood</td>
<td>squashfs-factory.bin</td>
<td>squashfs-sysupgrade.bin</td>
</tr>
<tr class="even">
<td>lantiq</td>
<td>initramfs-kernel.bin<br />
squashfs-factory.bin</td>
<td>squashfs-sysupgrade.bin</td>
</tr>
<tr class="odd">
<td>layerscape</td>
<td>squashfs-firmware.bin</td>
<td>-</td>
</tr>
<tr class="even">
<td>mpc85xx</td>
<td>squashfs-factory.bin</td>
<td>squashfs-sysupgrade.bin</td>
</tr>
<tr class="odd">
<td>mvebu</td>
<td>sdcard.img.gz<br />
squashfs-factory.img</td>
<td><br />
squashfs-sysupgrade.bin</td>
</tr>
<tr class="even">
<td>mxs</td>
<td>?</td>
<td>?</td>
</tr>
<tr class="odd">
<td>orion</td>
<td>not supported</td>
<td>not supported</td>
</tr>
<tr class="even">
<td>oxnas</td>
<td>squashfs-ubinized.bin<br />
ubifs-ubinized.bin</td>
<td>squashfs-sysupgrade.tar<br />
ubifs-sysupgrade.tar</td>
</tr>
<tr class="odd">
<td>ramips</td>
<td>initramfs-kernel.bin<br />
squashfs-factory.bin<br />
squashfs-factory.dlf<br />
initramfs-uImage.bin</td>
<td>squashfs-sysupgrade.bin<br />
squashfs-sysupgrade.tar</td>
</tr>
<tr class="even">
<td>sunxi</td>
<td>ext4-sdcard.img.gz<br />
squashfs-sdcard.img.gz</td>
<td></td>
</tr>
<tr class="odd">
<td>x86</td>
<td>combined-ext4.img</td>
<td>combined-ext4.img.gz</td>
</tr>
</tbody>
</table>

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