---
title: MTD
module: wiki
origin_type: wiki_page
token_count: 1589
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-mtd.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
language: text
---
# MTD

|                                                                                                                                                                     |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FIXME This page is a Work In Progress. The goal is to make it similar to [opkg](/docs/guide-user/additional-software/opkg) and then link to it as often as possible |

# MTD

`mtd` is a utility we use to write to an MTD (Memory Technology Device). Please read the [\#Notes](#Notes) to learn more.

## Invocation

    Usage: mtd [<options> ...] <command> [<arguments> ...] <device>[:<device>...]

### Writing to MTD

|                       |                                                      |
|:----------------------|:-----------------------------------------------------|
| `unlock <dev>`        | unlock the device                                    |
| `refresh <dev>`       | refresh mtd partition                                |
| `erase <dev>`         | erase all data on device                             |
| `write <imagefile>|-` | write \<imagefile\> (use - for stdin) to device      |
| `jffs2write <file>`   | append \<file\> to the jffs2 partition on the device |
| `fixtrx <dev>`        | fix the checksum in a trx header on first boot       |

### Options

|                                                 |                                                                                                                                                                        |
|:------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-q`                                            | quiet mode (once: no \[w\] on writing, twice: no status messages)                                                                                                      |
| `-n`                                            | write without first erasing the blocks                                                                                                                                 |
| `-r`                                            | reboot after successful command                                                                                                                                        |
| `-f`                                            | force write without trx checks                                                                                                                                         |
| `-e <device>`                                   | erase \<device\> before executing the command                                                                                                                          |
| `-d <name>`                                     | directory for jffs2write, defaults to "tmp"                                                                                                                            |
| `-j <name>`                                     | integrate \<file\> into jffs2 data when writing an image                                                                                                               |
| `-o offset`                                     | offset of the image header in the partition(for fixtrx)                                                                                                                |
| `-F <part>[:<size>[:<entrypoint>]][,<part>...]` | alter the fis partition table to create new partitions replacing the partitions provided as argument to the write command (only valid together with the write command) |

## Examples

Download `linux.bin` from Internet (it's not safe to do so, here is for demonstration purpose only), then write `linux.bin` to a MTD partition labeled as `linux` (could be `mtd4`) and reboot afterwards:

    cd /tmp
    wget http://www.example.org/linux.bin
    mtd -r write /tmp/linux.bin linux

## Example (flash u-boot from OpenWrt)

Tested on Marvell EspressoBinBoard based on MVEBU, (see [forum topic](https://forum.openwrt.org/t/is-it-possible-to-flash-u-boot-from-openwrt/90284)) Download `flash-image.bin` for your specific hardware from [SnapShots](https://downloads.openwrt.org/snapshots/targets/mvebu/cortexa53/)

You can checks your mtd partitions from proc :

    root@EBIN:~# cat /proc/mtd 
    dev:    size   erasesize  name
    mtd0: 003f0000 00010000 "firmware"
    mtd1: 00010000 00010000 "u-boot-env"

(it's not safe to do so, here is for demonstration purpose only),

then write `flash-image.bin` to a MTD partition labeled as `spi0.0` (could be `mtd0` or `firmware`) and reboot afterwards :

    cd /tmp
    wget https://downloads.openwrt.org/snapshots/targets/mvebu/cortexa53/trusted-firmware-a-espressobin-v7-1gb/flash-image.bin
    mtd -r write /tmp/flash-image.bin /dev/mtd0

## mtd vs dd

The differences between `dd` (disc dump) and `mtd` are ... [TODO](/docs/techref/flash#nand-specific_tools_for_reading_and_writing_to_raw_nand)

## mtd on vendor-firmware

`mtd` can even be used with vendor-firmware, as long as the kernel had mtd-support and not using something "home-brewed". When the vendor is not shipping the binary it can probably transferred via `scp`, `netcat`, `tftp`, `ftp`, `http`onto the board. The original binary from the OpenWrt-package might not run on the vendor-os, but linking it static should do the trick. With OpenWrt-21.02 I was using a small hack to to let the buildroot create a static binary:

    sed -i -e "s/^LDFLAGS += /LDFLAGS += -static /" package/system/mtd/src/Makefile
    make package/mtd/compile

This patches the mtd source to include the "-static" option when building the binary. This way the binary gets all dependent library-code embedded to make it run itself, as long as the correct CPU-target is used. The new binary can be extracted from the resulting package or just copied from `build_dir/target-<ARCH>/linux-<TARGET>-<SUBTARGET>/mtd`.

## Notes

- [Flash memory - things to consider](/docs/techref/flash)
- [MTD (Memory Technology Device)](https://en.wikipedia.org/wiki/Memory Technology Device)
- [documentation on MTDs](http://www.linux-mtd.infradead.org/doc/general.html).
- [The differences between flash devices and block drives in a table](http://www.linux-mtd.infradead.org/faq/general.html#L_mtd_vs_hdd)
- To make it more clear, here is a small [comparison of MTD devices and block devices](http://lxr.free-electrons.com/source/Documentation/filesystems/ubifs.txt):
  - MTD devices represent flash devices and they consist of eraseblocks of rather large size, typically about 128KiB. Block devices consist of small blocks, typically 512 bytes. MTD devices support 3 main operations - read from some offset within an eraseblock, write to some offset within an eraseblock, and erase a whole eraseblock. Block devices support 2 main operations - read a whole block and write a whole block.
  - The whole eraseblock has to be erased before it becomes possible to re-write its contents. Blocks may be just re-written.
  - Eraseblocks become worn out after some number of erase cycles - typically 100K-1G for SLC [NAND](../wiki/wiki_page-techref-flash.md) and NOR flashes, and 1K-10K for MLC [NAND](../wiki/wiki_page-techref-flash.md) flashes. Blocks do not have the wear-out property.
  - Eraseblocks may become bad (only on [NAND](../wiki/wiki_page-techref-flash.md) flashes) and software should deal with this. Blocks on hard drives typically do not become bad, because hardware has mechanisms to substitute bad blocks, at least in modern LBA disks.
- Sometimes flash memory uses FTL: [Raw Flash vs. FTL (Flash Translation Layer)](http://www.linux-mtd.infradead.org/doc/ubifs.html#L_raw_vs_ftl)
- Although most flashes on the commodity hardware have FTL, there are systems which have **bare flashes and do not use FTL**! Those are mostly various handheld devices and **embedded systems**.
