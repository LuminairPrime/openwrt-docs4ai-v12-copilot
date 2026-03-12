---
title: TRX vs. TRX2 vs. BIN
module: wiki
origin_type: wiki_page
token_count: 1469
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-headers.md
last_pipeline_run: '2026-03-12T09:09:53.122488+00:00'
language: text
ai_summary: The TRX, TRX2, and BIN firmware formats are used in various OpenWrt devices, each having distinct header structures despite containing similar content. TRX v1 and v2 both start with a magic number and include fields for header length, CRC value, flags, version, and multiple partition offsets, with TRX v2 adding an additional partition offset. The BIN header format is less defined, but it also begins with a magic number and includes reserved fields. Understanding these formats is crucial for firmware development and modification in OpenWrt.
ai_when_to_use: Use this information when developing or modifying firmware for OpenWrt devices that utilize TRX or BIN formats.
ai_related_topics:
- TRX
- TRX2
- BIN
---
# TRX vs. TRX2 vs. BIN

[Broadcom Firmware Format](http://skaya.enix.org/wiki/FirmwareFormat)

# The various headers

Some devices have firmware files with different file name endings. While the overall content of the files are identical, there are some slight differences at their beginnings:

## TRX v1

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +---------------------------------------------------------------+
     |                     magic number ('HDR0')                     |
     +---------------------------------------------------------------+
     |                  length (header size + data)                  |
     +---------------+---------------+-------------------------------+
     |                       32-bit CRC value                        |
     +---------------+---------------+-------------------------------+
     |           TRX flags           |          TRX version          |
     +-------------------------------+-------------------------------+
     |                      Partition offset[0]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[1]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[2]                      |
     +---------------------------------------------------------------+

- offset\[0\] = lzma-loader
- offset\[1\] = Linux-Kernel
- offset\[2\] = rootfs

## TRX v2

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +---------------------------------------------------------------+
     |                     magic number ('HDR0')                     |
     +---------------------------------------------------------------+
     |                  length (header size + data)                  |
     +---------------+---------------+-------------------------------+
     |                       32-bit CRC value                        |
     +---------------+---------------+-------------------------------+
     |           TRX flags           |          TRX version          |
     +-------------------------------+-------------------------------+
     |                      Partition offset[0]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[1]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[2]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[3]                      |
     +---------------------------------------------------------------+

- offset\[0\] = lzma-loader
- offset\[1\] = Linux-Kernel
- offset\[2\] = rootfs
- offset\[3\] = bin-Header

Source: [openwrt/tools/firmware-utils/src/trx.c](http://git.openwrt.org/?p=14.07/openwrt.git;a=blob;f=tools/firmware-utils/src/trx.c;h=aa1f5be4b65b66ac9a1a48d7304d9bef131080e1;hb=HEAD#l69)

## BIN-Header

FIXME (which bin header?)

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +---------------------------------------------------------------+
     |                            magic                              |
     +---------------------------------------------------------------+
     |                            res1                               |
     +---------------------------------------------------------------+
     |                fwdate                         |   fwvern...   |
     +---------------------------------------------------------------+
     |    ...fwvern                  |              ID...            |
     +---------------------------------------------------------------+
     |         ...ID                 |  hw_ver       |    s/n        |
     +---------------------------------------------------------------+
     |           flags               |           stable              |
     +---------------------------------------------------------------+
     |           try1                |           try2                |
     +---------------------------------------------------------------+
     |           try3                |           res3                |
     +---------------------------------------------------------------+

- magic: firmware magic depends on board etc. s.th. like '3G2V' or 'W54U'
- res1: reserved for extra magic??
- char fwdate\[3\]: fwdate\[0\]: Year, fwdate\[1\]: Month, fwdate\[2\]: Day
- fwvern: version informations a.b.c.
- ID: fix "U2ND"
- hw_ver: depends on board
- s/n: depends on board
- flags:
- stable: Marks the firmware stable, this is 0xFF in the image and will be written to 0x73 by the running system once it completed booting.
- try1-3: 0xFF in firmware image. CFE will set try1 to 0x74 on first boot and continue with try2 and try3 unless "stable" was written by the running image. After writing try3 and the stable flag was not written yet, the CFE assumes that the image is broken and starts a [TFTP](../wiki/wiki_page-guide-developer-adding-new-device.md) server
- res3: unused?

## TP-LINK BIN Header

      0   1   2   3   4   5   6   7   8   9   a   b   c   d   e   f
    +---------------------------------------------------------------+
    |    version    |          vendor_name...                       |
    +---------------------------------------------------------------+
    |                       ...vendor_name          | fw_version... |
    +---------------------------------------------------------------+
    |                       ...fw_version...                        |
    +---------------------------------------------------------------+
    |                       ...fw_version                           |
    +---------------------------------------------------------------+
    |     hw_id     |    hw_rev     |     unk1      |    md5sum1... |
    +---------------------------------------------------------------+
    |                         ...md5sum1            |     unk2      |
    +---------------------------------------------------------------+
    |                            md5sum2                            |
    +---------------------------------------------------------------+
    |     unk3      |   kernel_la   |   kernel_ep   |   fw_length   |
    +---------------------------------------------------------------+
    |  kernel_ofs   |   kernel_len  |   rootfs_ofs  |  rootfs_len   |
    +---------------------------------------------------------------+
    |   boot_ofs    |   boot_len    |ver_hi |ver_mid| ver_lo| pad...|
    +---------------------------------------------------------------+
    |                           ...pad...                           |
    +---------------------------------------------------------------+

source: [openwrt/tools/firmware-utils/src/mktplinkfw.c](http://git.openwrt.org/?p=openwrt.git;a=blob;f=tools/firmware-utils/src/mktplinkfw.c;h=a6aab598a1ffa677e64307ee4234479d45de9140;hb=HEAD#l78)
