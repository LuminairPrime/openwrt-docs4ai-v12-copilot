---
title: Device Tree Usage in OpenWrt (DTS)
module: wiki
origin_type: wiki_page
token_count: 1049
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-defining-firmware-partitions.md
last_pipeline_run: '2026-03-11T12:37:15.044626+00:00'
language: text
---
# Device Tree Usage in OpenWrt (DTS)

Current development (2019) uses kernel based on Device Tree (DT) files (.dts, .dtsi, .dtb) rather than the older "mach" files.

This page tries to pull together some of the knowledge about DT usage and conventions used by the OpenWrt project.

## References

- <https://elinux.org/Device_Tree_Reference>
- <https://elinux.org/Device_Tree_Mysteries>
- <https://elinux.org/Device_Tree_Source_Undocumented>
- <https://developer.toradex.com/device-tree-customization>
- <https://events.static.linuxfound.org/sites/events/files/slides/petazzoni-device-tree-dummies.pdf>
- Linux binding defintions, in source or online at <https://www.kernel.org/doc/Documentation/devicetree/bindings/>
- OpenWrt wiki on Defining software partitions in all DTS targets
- <https://devicetree-specification.readthedocs.io/en/latest/source-language.html>
- <https://github.com/devicetree-org/devicetree-specification/blob/master/source/source-language.rst>

## General

Use c-style `#include` instead of DT-specific `/include/`

If possible, license the content as `// SPDX-License-Identifier: GPL-2.0-or-later OR MIT`

Use tab indentation -- see also <https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Documentation/process/coding-style.rst>

While upstream, architecture-specific .dtsi files *may* remain stable (such as `qcom-ipq4019.dtsi`), board-specific files (such as `qcom-ipq4019-ap.dk07.1.dtsi`) may change, causing breakage to specific devices, perhaps just one, that may go unnoticed. At least if, for example, the generic IPQ4019 .dtsi changes, there is a chance that it would be seen quickly by or more of the boards that use that SoC.

## Defining software partitions in all DTS targets

Partition nodes should be named `partition@<start address>`

Boot loader binaries, firmware, and configuration partitions (such as "ART") should be marked as read-only. This helps reduce the risk of users following outdated or questionable advice in using low-level writes. Users advanced enough to need to write these partitions should be sophisticated enough to be able to compile their own kernel to do so.

The MTD labels of "firmware" and "ubi" have special meaning to the OpenWrt kernel.

See below on supplying the proper "compatible" label so that the OpenWrt kernel can properly "split" the partition and `CONFIG_MTD_SPLIT_FIRMWARE` is not needed. (note that `CONFIG_MTD_SPLIT_UIMAGE_FW` is still required!)

 this article was an email sent to the OpenWrt-devel mailing list by OpenWrt dev Rafał Miłecki
**Subject:** \[OpenWrt-Devel\] Specifying "firmware" partition format on all DTS targets
**Date:** Sat, 24 Nov 2018 11:32:25 +0100

Parsing "firmware" partition (to create kernel + rootfs) was implemented using OpenWrt downstream code enabled by CONFIG_MTD_SPLIT_FIRMWARE.
With recent upstream mtd changes we can do it in a more clean way for DTS targets. It just requires adding a proper "compatible" string to the "firmware" partition node.

I'd like all DTS supported devices to use that "compatible" and disable CONFIG_MTD_SPLIT_FIRMWARE eventually.

*Wiki note: This objective may be a challenge for dual-firmware units as the partition to be split will be different depending on which was selected by the boot loader.*

1\) Default uimage
If you see:
2 uimage-fw partitions found on MTD device firmware
please use "denx,uimage"; e.g.
`partition@70000 {
        label = "firmware";
        reg = <0x070000 0x790000>;
        compatible = "denx,uimage";
};`

2\) Netgear's uimage
If you see:
2 netgear-fw partitions found on MTD device firmware
please use "netgear,uimage"; e.g.
`partition@70000 {
        label = "firmware";
        reg = <0x070000 0xf80000>;
        compatible = "netgear,uimage";
};`

3\) TP-LINK's firmware
If you see:
2 tplink-fw partitions found on MTD device firmware
please use "tplink,firmware"; e.g.
`firmware@20000 {
        label = "firmware";
        reg = <0x020000 0xfd0000>;
        compatible = "tplink,firmware";
};`

Please kindly:
1) Use that for all newly added devices
2) Port already supported devices you can test
--
Rafał
