---
title: The OpenWrt Flash Layout
module: wiki
origin_type: wiki_page
token_count: 9839
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-flash-layout.md
last_pipeline_run: '2026-03-23T22:14:22.429226+00:00'
language: text
---
# The OpenWrt Flash Layout

The embedded devices (routers and such) OpenWrt/LEDE (Linux Embedded Development Environment) has mainly targeted since its inception, use flash memory as the form of non-volatile memory for the persistent storage of the firmware and its configuration.

## Types of flash memory

### Non-mechanical wear

Moving parts are prone to [wear](https://en.wikipedia.org/wiki/wear) (german: [Verschleiß](https://de.wikipedia.org/wiki/Verschleiß)) and experience all sorts of "mechanical breakage/mechanical failure". But how can a non-moving part possibly break? Possibly by [electromigration](https://en.wikipedia.org/wiki/electromigration), by [whisker growth](https://en.wikipedia.org/wiki/Whisker (metallurgy)), etc.

Non-mechanical wear does not only occur when flash memory is erased!

> [![NOTE](../wiki/wiki_page-techref-luci2.md)]
> 1. Flash memory is more likely to experience failure than a [Hard_disk_drive](https://en.wikipedia.org/wiki/Hard_disk_drive) (the ones with the platters rotating at 5400–15000 [RPM](https://en.wikipedia.org/wiki/Revolutions per minute))
>
> 2. Some types of flash memory seem to experience more non-mechanical wear then other types
>
> 3. How do we deal with failure?

### Host-managed vs. self-managed

Based on how the flash memory chip is connected with the [SoC](/docs/techref/hardware/soc) (i.e. the "host") we at OpenWrt distinguish between ***"raw flash"*** or ***"host-managed"*** and ***"FTL (Flash Translation Layer) flash"*** or ***"self-managed"***: in case the flash memory chip is connected directly with the SoC we call it "raw flash" / "host-managed" and in case there is an additional controller chip between the flash memory chip and the SoC, we call it "FTL flash" / "self-managed". Primarily the controller chip does [wear-leveling](https://en.wikipedia.org/wiki/wear-leveling) and manages known bad blocks, but it may do other stuff as well. The flash memory cannot be accessed directly, but only through this controller. The controller has to be considered a [black box](https://en.wikipedia.org/wiki/black box).

> [![NOTE](../wiki/wiki_page-techref-luci2.md)]
> Embedded systems almost exclusively use "raw flash", while [solid-state drives (SSDs)](https://en.wikipedia.org/wiki/Solid-state drive) and USB memory sticks, almost exclusively use "FTL flash"!

### NOR flash vs NAND flash

Additionally we at OpenWrt distinguish between the two basic types of flash memory: [NOR flash](https://en.wikipedia.org/wiki/Flash_memory#NOR_flash) and [NAND flash](https://en.wikipedia.org/wiki/Flash_memory#NAND_flash).
"Raw NOR flash" in typical routers is generally small (4 MiB – 16 MiB) and **error-free**: all data blocks are guaranteed to work correctly. Because raw NOR flash is error-free, the installed file system(s) do not need to take bad blocks into account, and neither SquashFS nor JFFS2 do. The combination of OverlayFS with SquashFS and JFFS2 has been the default OpenWrt setup since the beginning, and it works flawlessly on "raw NOR flash". Older routers typically use NOR flash.

"Raw [NAND](../wiki/wiki_page-techref-flash.md) flash" in typical routers is generally much larger (32 MiB – 1 GiB) and **not error-free**: in general the flash contains bad blocks when new and may develop more at any time. Newer routers use [NAND](../wiki/wiki_page-techref-flash.md) flash because it is much cheaper for a given capacity and is also faster for bulk access (disk emulation), but at the cost of the increased complexity required to handle flash defects.

Bad blocks in [NAND](../wiki/wiki_page-techref-flash.md) flash and handled in various ways:

- The [NAND](../wiki/wiki_page-techref-flash.md) flash manufacturer guarantees that certain very small areas of the flash are defect-free. The use of such areas is up to the system designer. Some SoCs may store the first stage bootloader there (but since newer SoCs tend to support chain-of-trust booting, they typically store the first stage bootloader on-chip).
- Some partitions are used as large files that can only be read or written completely and in one go. This is the case of raw bootloaders and kernels in MTD partitions. For these partitions, bad blocks are simply skipped during both reads and writes. Because new defects almost exclusively develop during erase and writes, once written these partitions are mostly trusted to be readable forever. (But newer devices tend to duplicate these partitions to minimize failures.)
- Some partitions are used as large files that can only be written completely and in one go, but can be read in a random access fashion. This is the case of raw read-only file systems (such as squashfs) in MTD partitions. For these partitions, bad blocks are simply skipped during writes, and a kernel driver is used to read them. The driver reads the complete partition during setup skipping bad blocks, and builds a logical-block-to-flash-block table in RAM to be able to later access the partition random-access.
- Some large partitions are used as containers for other compartmentalized data. Note that the amount of bad blocks in a certain partition is a-priory unknown, and thus a raw partition size cannot be taken as the its usable size. For smaller partitions this effect is amplified: although there is a manufacturer-defined limit on the number of bad blocks in a flash, nothing precludes all bad blocks from residing in the same partition. Thus, for guaranteed operation, a system designer should allow *in each and every partition* the maximum number of bad blocks specified for the complete flash. (In practice though, this is almost never done.) Also note that the previous kinds of defect handling do not spread wear produced by erase/write cycles across the whole flash, and thus in general reduce the lifespan of the device. These problems are both solved by UBI. Ideally a single very large UBI partition is created that entirely manages flash defects and wear-leveling for contained volumes, and inside it different UBI volumes are created:
  - Some UBI volumes are used as large files that can only be read or written completely and in one go. This is the case of kernels in UBI partitions.
  - Some UBI volumes are used as large files that can only be written completely and in one go, but can be read in a random access fashion. This is the case of read-only file systems (such as squashfs) in UBI partitions. For these volumes, an ubiblock kernel device is used to read them: the device emulates a read-only block device and maintains a logical-block-to-flash-block table in RAM to be able to access the volume random-access.
  - Some UBI volumes are used as read-write filesystems. Only the [UBIFS](../wiki/wiki_page-techref-filesystems.md) filesystem is used for this. (It would be possible to emulate read-write block devices on top of UBI and use regular filesystems on top of that, but such setups would underperfom compared to [UBIFS](../wiki/wiki_page-techref-filesystems.md), and it seems that the necessary UBI block emulation driver has not yet been implemented, if ever.)

Note that because of these factors, the OpenWrt [Image Generator](/docs/guide-user/additional-software/imagebuilder) has been constrained to build images that are smaller than the size of the partitions to which they are supposed to be flashed by an arbitrary margin, to maximize the probability that such images can be flashed on all devices.

### MLC vs. SLC flash

The main difference between SLC and MLC is durability. [single-level cell (SLC)](https://en.wikipedia.org/wiki/Single-level cell) flash memory may have a lifetime of about 50,000 to 100,000 program/erase cycles, while [multi-level cell (MLC)](https://en.wikipedia.org/wiki/Multi-level cell) flash may have a lifetime of about 1,000 to 10,000 program/erase cycles.

To be noted that it is **NOT RIGHT** to estimate the life of a [NAND](../wiki/wiki_page-techref-flash.md) flash in embedded devices using the same method for SSD!

## Partitioning of NOR flash-based devices

On these systems, the storage is presented by the kernel as an MTD device, and it is divided into MTD partitions. The device is not partitioned in the traditional way, where you store information about partitions in a [GPT](https://en.wikipedia.org/wiki/GUID Partition Table) or [MBR](https://en.wikipedia.org/wiki/Master boot record). Instead, the partitioning information is directly known by the bootloader and the kernel, either through configuration, or more typically through baking it in at build time. For example, in the kernel it may simply be defined that *"MTD partition **`kernel`** starts at flash block `X` and consists of `Y` blocks"*. MTD partitions can be accessed by name or number.

The generic flash layout is:

```tsv
Layer0	raw flash
Layer1	bootloader; partition(s)	optional; SoC; specific; partition(s)	firmware partition	 	 	optional; SoC; specific; partition(s)
Layer2	:::	:::	OpenWrt firmware image	 	*(space available for storage)*	:::
Layer3	:::	:::	Linux kernel; (raw image)	**`rootfs`**; mounted: "`/rom`", [SquashFS](/docs/techref/filesystems#SquashFS); size depends on selected packages	**`rootfs_data`**; mounted: "`/overlay`", [JFFS2](/docs/techref/filesystems#JFFS2); all remaining free space	:::
Layer4	:::	:::	:::	mounted: "`/`", [OverlayFS](/docs/techref/filesystems#overlayfs); stacking `/overlay` on top of `/rom`	 	:::
```

Many NOR devices share this scheme, but the flash layout can differ between the devices. Please see the wiki pages for each SoC and devices for information about a particular layout. In case the flash layout differs for your device please update the wiki pages.

### Sysupgrade and `rootfs_data`

To better use the minimal storage on devices available when OpenWrt was originally being developed, the **`rootfs_data`** partition was placed immediately after the OpenWrt firmware image (which contains the kernel and rootfs), without any padding in-between. This means that during upgrades, the beginning of **`rootfs_data`** might need to be overwritten (either because the OpenWrt image grew, or because the [NAND](../wiki/wiki_page-techref-flash.md) flash developed new defects in the firmware area that need to be skipped during firmware flashing).

To handle this situation, sysupgrade works in an atypical fashion. During an upgrade OpenWrt reads selected content from **`rootfs_data`** that it wants surviving the upgrade into RAM, flashes the new firmware, formats the remaining flash space as the new **`rootfs_data`** partition, and writes back the selected content to it from RAM.

Because of this, a failed sysupgrade might not only brick the device, it might also cause the contents of **`rootfs_data`** to be irrevocably lost.

Note: Arbitrary files you may choose to store in **`rootfs_data`** are by default **not kept** across sysupgrades (but there is a way to request future sysupgrades to conserve selected files).

### Example NOR flash partitioning

[Qualcomm Atheros](/docs/techref/hardware/soc/soc.qualcomm)-based [TL-WR1043ND](/toh/tp-link/TL-WR1043ND). Somebody also provided a [LibreOffice Calc ODS](https://web.archive.org/web/20131021013058/http://ubuntuone.com/2aPBH9pwkxtYzy93S0cS1z).

SquashFS-Images are suitable for devices with *"raw NOR flash memory"*-chips and it is not recommended to install them onto devices with *"raw [NAND](../wiki/wiki_page-techref-flash.md) flash memory"*-chips. SquashFS-Images comprise both, a SquashFS partition and an JFFS2 partition. JFFS2-Images omit the SquashFS partition.

|     TP-Link WR1043ND Flash Layout     |                                                                                                                             |                              |                                                            |                                                      |                       |
|:-------------------------------------:|-----------------------------------------------------------------------------------------------------------------------------|------------------------------|------------------------------------------------------------|------------------------------------------------------|-----------------------|
|                Layer0                 | raw NOR flash memory chip (m25p80 [spi](https://en.wikipedia.org/wiki/Serial Peripheral Interface Bus)0.0: m25p64) 8192 KiB |                              |                                                            |                                                      |                       |
|                Layer1                 | mtd0 ***u-boot*** 128 KiB                                                                                                   | mtd5 ***firmware*** 8000 KiB |                                                            |                                                      | mtd4 ***art*** 64 KiB |
|                Layer2                 |                                                                                                                             | mtd1 ***kernel*** 1280 KiB   | mtd2 ***rootfs*** 6720 KiB                                 |                                                      |                       |
| mountpoint |                                                                                                                             |                              | `/`                             |                                                      |                       |
|              filesystem               |                                                                                                                             |                              | [OverlayFS](/docs/techref/filesystems#overlayfs)           |                                                      |                       |
|                Layer3                 |                                                                                                                             |                              |                                                            | mtd3 ***rootfs_data*** 5184 KiB                      |                       |
|              Size in KiB              | 128 KiB                                                                                                                     | 1280 KiB                     | 1536 KiB                                                   | 5184 KiB                                             | 64 KiB                |
|                 Name                  | ***u-boot***                                                                                                                | ***kernel***                 |                                                            | ***rootfs_data***                                    | ***art***             |
| mountpoint | *none*                                                                                                                      | *none*                       | `/rom`                          | `/overlay`                | *none*                |
|              filesystem               | *none*                                                                                                                      | *none*                       | [filesystems#SquashFS](/docs/techref/filesystems#SquashFS) | [filesystems#JFFS2](/docs/techref/filesystems#JFFS2) | *none*                |

#### Another Flash layout example

[TP-Link Archer C6 V2 (EU/RU/JP)](/toh/tp-link/archer_c6_v2#flash_layout)

### Explanations

The Linux kernel treats "raw flash memory" (no matter whether NOR or [NAND](../wiki/wiki_page-techref-flash.md)) chips as an [MTD (Memory Technology Device)](/docs/techref/mtd) and employs [filesystems](/docs/techref/filesystems) developed for this purpose on top of the MTD layer.

Since the partitions are nested we look at this whole thing in layers:

1.  Layer0: So we have the Flashchip, 8 MiB in size, which is soldered to the PCB and connected to the [soc](/docs/techref/hardware/soc) over [SPI (Serial Peripheral Interface Bus)](https://en.wikipedia.org/wiki/Serial Peripheral Interface Bus).
2.  Layer1: We "partition" the space into mtd0 for the bootloader, mtd5 for OpenWrt and, in this case, mtd4 for the ART (Atheros Radio Test) - it contains calibration data for the wifi (EEPROM). If it is missing or corrupt, `ath9k` (wireless driver) won't come up anymore. The bootloader (128 KiB) contains of the u-boot 64KiB block AND a data section which contains the MAC, WPS-PIN and type description. If no MAC is configured ath9k will not work correctly due to a faulty MAC.
3.  Layer2: we subdivide mtd5 (firmware) into mtd1 (kernel) and mtd2 (rootfs); In the generation process of the firmware (see [imagebuilder](/docs/guide-user/additional-software/imagebuilder)) the Kernel binary file is first packed with [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm), then the obtained file is packed with [gzip](https://en.wikipedia.org/wiki/gzip) and then this file will be written onto the raw flash (mtd1) without being part of any filesystem! During boot, u-boot copies this entire section into RAM and executes it. From there on, the Linux kernel bootstraps itself…
4.  Layer3: we subdivide rootfs even further into mtd3 for rootfs_data and the rest for an unnamed partition which will accommodate the SquashFS-partition.

#### Mount Points

- `/` this is your entire root filesystem, it comprises `/rom` and `/overlay`. Please ignore `/rom` and `/overlay` and use exclusively `/` for your daily routines!
- `/rom` contains all the basic files, like `busybox`, `dropbear` or `iptables`. It also includes default configuration files used when booting into [OpenWrt Failsafe mode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset). It does not contain the Linux kernel. All files in this directory are located on the SquashFS partition, and thus cannot be altered or deleted. But, because we use overlay_fs filesystem, *overlay-whiteout*-symlinks can be created on the JFFS2 partition.
- `/overlay` is the writable part of the file system that gets merged with `/rom` to create a uniform `/`-tree. It contains anything that was written to the router after [installation](/docs/guide-user/installation/generic.flashing), e.g. changed configuration files, additional packages installed with `opkg`, etc. It is formatted with JFFS2.

Whenever the system is asked to look for an existing file in `/`, it first looks in `/overlay`, and if not there, then in `/rom`. In this way `/overlay` overrides `/rom` and creates the effect of a writable `/` while much of the content is safely and efficiently stored in the read-only `/rom`.

When the system is asked to delete a file that is in `/rom`, it instead creates a corresponding entry in `/overlay`, a whiteout. A whiteout is a symlink to `(overlay-whiteout)` that mostly behaves like a file that doesn't exist. In newer versions, the whiteout is created as a character device with 0/0 device number instead.

``` bash
#!/bin/sh
# shows all overlay-whiteout symlinks
# 2018: overlay-whiteouts are a character device on CC 'find /overlay -type c' seems to work
#  https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt  put me on the right track

find /overlay -type c; find /overlay -type l -exec sh -c \
    'for x; do [ "$(readlink -n -- "$x")" = "(overlay-whiteout)" ] && printf %s\\n "$x"; done' -- {} +
```

#### Example 2: Hoo Too HT-TM02

[Ralink RT5350F](/docs/techref/hardware/soc/soc.ralink)-based [Hoo Too HT-TM02](/toh/hwdata/hootoo/hootoo_tripmatenano_v15).

```tsv
Layer0	raw flash, 8192 KiB
Layer1	**mtd0**; `u-boot`; 192 KiB	**mtd1**; `u-boot-env`; 64 KiB	**mtd2**; `factory`; 64 KiB	**mtd3**; `firmware`; 7872 KiB (= FlashSize-(192+64+64))
Layer2	:::	:::	:::	**mtd4**; `kernel`; about 1 MiB	**mtd5**; `rootfs`
Layer3	:::	:::	:::	:::	**`/dev/root`**; around 2 MiB	**mtd6**; `rootfs_data`; around 4.5 MiB
```

#### Example 3: D-Link DIR-300

For some devices, the OpenWrt partition `firmware` may not exist at all. The [DIR-300 flash layout](/toh/d-link/DIR-300#flash_layout) is such an example.

## Partitioning of NAND flash-based devices

On these systems, the storage is presented by the kernel as an MTD device, and it is divided into MTD partitions. The device is not partitioned in the traditional way, where you store information about partitions in a [GPT](https://en.wikipedia.org/wiki/GUID Partition Table) or [MBR](https://en.wikipedia.org/wiki/Master boot record). Instead, the partitioning information is directly known by the bootloader and the kernel, either through configuration, or more typically through baking it in at build time. For example, in the kernel it may simply be defined that *"MTD partition **`kernel`** starts at flash block `X` and consists of `Y` blocks"*. MTD partitions can be accessed by name or number.

Some [NAND](../wiki/wiki_page-techref-flash.md) devices contain bootloaders that do not understand UBI partitions and thus cannot boot kernels contained in UBI volumes. The generic flash layout for these devices is:

```tsv
Layer0	raw flash
Layer1	bootloader; partition(s)	optional; SoC; specific; partition(s)	Linux kernel; (raw image)	optional; SoC; specific; partition(s)	UBI partition	 	optional; SoC; specific; partition(s)
Layer2	:::	:::	:::	:::	**`rootfs`**; mounted: "`/rom`", [SquashFS](/docs/techref/filesystems#SquashFS); size depends on selected packages	**`rootfs_data`**; mounted: "`/overlay`", [UBIFS](/docs/techref/filesystems#UBIFS); all remaining free space	:::
Layer3	:::	:::	:::	:::	mounted: "`/`", [OverlayFS](/docs/techref/filesystems#overlayfs); stacking `/overlay` on top of `/rom`	 	:::
```

The generic flash layout for [NAND](../wiki/wiki_page-techref-flash.md) devices that can boot kernels contained in UBI volumes is:

```tsv
Layer0	raw flash
Layer1	bootloader; partition(s)	optional; SoC; specific; partition(s)	UBI partition	 	 	optional; SoC; specific; partition(s)
Layer2	:::	:::	**`kernel`**; Linux kernel; (raw image)	**`rootfs`**; mounted: "`/rom`", [SquashFS](/docs/techref/filesystems#SquashFS); size depends on selected packages	**`rootfs_data`**; mounted: "`/overlay`", [UBIFS](/docs/techref/filesystems#UBIFS); all remaining free space	:::
Layer3	:::	:::	:::	mounted: "`/`", [OverlayFS](/docs/techref/filesystems#overlayfs); stacking `/overlay` on top of `/rom`	 	:::
```

Many [NAND](../wiki/wiki_page-techref-flash.md) devices share this scheme, but the flash layout can differ between the devices. Please see the wiki pages for each SoC and devices for information about a particular layout. In case the flash layout differs for your device please update the wiki pages.

### Reserving UBI partition space for user-defined UBI volumes

For [historical reasons](/docs/techref/flash.layout#sysupgrade_and_rootfs_data) concerning NOR flash-based devices, sysupgrade works in an atypical fashion. During upgrades OpenWrt reads selected content from **`rootfs_data`** that it wants surviving the upgrade into RAM, creates an all-new **`rootfs_data`**, and writes back the selected content to it from RAM.

On [NAND](../wiki/wiki_page-techref-flash.md) devices using UBI, sysupgrade partially reads the **`rootfs_data`** volume to RAM, deletes **`kernel`** (for kernel-in-UBI devices), **`rootfs`** and **`rootfs_data`** volumes, recreates **`kernel`** (if kernel-in-UBI) and **`rootfs`** volumes sizing them to fit the new images, recreates the **`rootfs_data`** volume utilizing all remaining free space in the UBI partition, flashes the firmware, and writes back data from RAM to **`rootfs_data`**.

While this setup worked well for old space-limited NOR devices, it may not be optimal for today's large NANDs. Nowadays, devices with flash sizes of 1 GiB or more are not uncommon, and for these devices moving all flash data to RAM and back is inefficient, unduly dangerous, and may not even be possible.

Fortunately the default behavior of sysupgrade on [NAND](../wiki/wiki_page-techref-flash.md) devices using UBI can be modified: instead of recreating the **`rootfs_data`** volume utilizing all the free space in the UBI partition, sysupgrade can restrict the volume to a specific user-defined size. The requested **`rootfs_data`** size must be specified in bytes in the **`rootfs_data_max`** bootloader environment variable. (The variable is evaluated when read, so "128\*1024\*1024", "0x8000000", "134217728" are all valid and equivalent.)

The relevant bootloader variable can be read with this command:

    fw_printenv -n rootfs_data_max

Set with:

    fw_setenv rootfs_data_max <VALUE>

And cleared with:

    fw_setenv rootfs_data_max

Note that sysupgrade will fail if there is not enough space in the UBI partition to create **`rootfs_data`** of the specified size, and the contents of **`rootfs_data`** will then be lost. (The **`rootfs_data_max`** variable should have better been named **`rootfs_data_size`**.) The user must make sure that enough free space exists in UBI to accommodate growth of future OpenWrt images and/or custom OpenWrt images with more packages.

### Example: Creating a UBI volume for persistent storage across sysupgrades

In an Askey RT4230W REV6 router with 512 MiB flash, the **`rootfs_data`** volume is normally sized at around 370 MiB (the remaining flash space being used for bootloaders, SoC-specific partitions, kernel, rootfs, and recovery). You can check this using:

    root@router:~# ubinfo -d 0 -N rootfs_data
    Volume ID:   2 (on ubi0)
    Type:        dynamic
    Alignment:   1
    Size:        3086 LEBs (391847936 bytes, 373.6 MiB)
    State:       OK
    Name:        rootfs_data
    Character device major/minor: 246:3

Given that this volume is routinely wiped by sysupgrade, storing any remotely valuable files here would be ill-advised. For this router you might choose to limit **`rootfs_data`** to a generous 128 MiB, and create a new 192 MiB [UBIFS](../wiki/wiki_page-techref-filesystems.md) volume for persistent storage, while still reserving 50+ MiB as free space to accommodate future growth of OpenWrt images. Let's do just that and name the new volume **`extra`**.

First you need to limit **`rootfs_data`** to 128 MiB for all following sysupgrades:

    root@router:~# fw_setenv rootfs_data_max 0x8000000

Next do a sysupgarde (even if no upgrade is needed) to resize **`rootfs_data`**. After that, verify its new size:

    root@router:~# ubinfo -d 0 -N rootfs_data
    Volume ID:   2 (on ubi0)
    Type:        dynamic
    Alignment:   1
    Size:        1058 LEBs (134340608 bytes, 128.1 MiB)
    State:       OK
    Name:        rootfs_data
    Character device major/minor: 246:3

You just freed 240+ MiB in the UBI partition. Next, you could manually create, format, and mount a new [UBIFS](../wiki/wiki_page-techref-filesystems.md) volume. But OpenWrt has a tool to automate this, so let's use it.

Connect the router to the internet if necessary, and use Luci to install package `uvol` (**System \> Software**). You might also want to install your favorite text editor now (`nano-full` is a good option).

Now check the installation (sizes are in bytes):

    root@router:~# uvol list
    root@router:~# uvol total
    422576128
    root@router:~# uvol free
    253317120

Create and enable the `extra` volume using `uvol`:

    root@router:~# uvol create extra $(( 192*1024*1024 )) rw
    Volume ID 4, size 1586 LEBs (201383936 bytes, 192.0 MiB), LEB size 126976 bytes (124.0 KiB), dynamic, name "uvol-wp-extra", alignment 1
    root@router:~# uvol up extra
    root@router:~# uvol list
    extra rw 201383936
    root@router:~# mount | grep extra
    /dev/ubi0_4 on /tmp/run/uvol/extra type ubifs (rw,relatime,assert=read-only,ubi=0,vol=4)

You do not like the default mount path (`/tmp/run/uvol/extra`), so you change it to `/extra` using you text editor:

    root@router:~# nano /etc/config/fstab

Finally reboot and check that your new volume is mounted where you want it:

    root@router:~# mount | grep extra
    /dev/ubi0_4 on /extra type ubifs (rw,relatime,assert=read-only,ubi=0,vol=4)

## MTD (Memory Technology Device) and MTDSPLIT

The Linux kernel treats "raw/host-managed" flash memory (NOR and [NAND](../wiki/wiki_page-techref-flash.md) alike) as an MTD (Memory Technology Device). An MTD is different to a [block device](https://en.wikipedia.org/wiki/block device) or a [character device](https://en.wikipedia.org/wiki/character device).

On a common block device such as a hard drive, the storage space is split up into "blocks", which are also named "sectors", of a size of 512 Bytes or 4096 Bytes. Blocks do not get corrupted during common operation, but only exceptionally. In the very rare case this happens, the LBA hard disk controller takes care, that accesses to such a bad block are redirected to a replacement block. Block devices support 2 main operations - read a whole block and write a whole block. When a block device is partitioned, the information is stored in the [MBR](https://en.wikipedia.org/wiki/Master boot record) or the [GPT](https://en.wikipedia.org/wiki/GUID Partition Table).

Flash memory using MTD is different from this.

The storage space of a MTD is split up into "erase-blocks", of a size of e.g 64 KiB, 128 KiB or much more, which themselves are split up into "blocks", which are more correctly named "pages", of smaller sizes.

A single "page" can be written to, but it cannot be overwritten, but instead the entire "erase block" that page is part of, has to be erased before it becomes possible to re-write its "pages". Erase-blocks do become worn out after some number of erase cycles – typically 100K-1G for SLC [NAND](../wiki/wiki_page-techref-flash.md) and NOR flashes, and 1K-10K for MLC [NAND](../wiki/wiki_page-techref-flash.md) flashes. Erase-blocks may become bad (only [NAND](../wiki/wiki_page-techref-flash.md)). In case of "FTL flash", the controller should notice and avoid further access to bad erase-blocks. In case of "raw flash", the operating system should deal with such cases.

MTD devices support 3 main operations - read from some offset within an erase block, write to some offset within an erase-block, and erase a whole erase-block.

The utility program [mtd](/docs/techref/mtd) can be used to manage MTD devices.

### MTD partitions

The MTD device is often subdivided into logical chunks of memory called partitions. Each partition start at the beginning of an erase-block and end at the end of an erase-block.

The partitioning of MTD devices is not stored in some MBR/GPT, but it is done in the Linux Kernel using MTD-specific partition parsers determining the location and size of these partitions. (sometimes the partitioning is implemented independently in the [bootloader](/docs/techref/bootloader) as well!).

The kernel boot process involves discovering of partitions within the NOR flash and it can be done by various target-dependent means:

- some bootloaders store a partition table at a known location
- some pass the partition layout via kernel command line
- some pass the partition layout using Device Tree
- some targets require specifying the kernel command line at the compile time (thus overriding the one provided by the bootloader).

Some of these schemes but not all are implemented in the mainline Linux kernel. The standard kernel can usually detect the top level coarse partitioning scheme, but not the more fine-grained sub-partitions.

### MTDSPLIT

In order to deal with some of the custom flash partitioning schemes directly in the kernel, OpenWrt has developed `mtdsplit` which is a set of patches currently maintained separately from the mainline kernel, but used in OpenWrt to parse different flash layouts and split them into further "logical" partitions.

This is done recursively so that further split of a new "child" partition may be attempted. Whether an attempt is made to split a partition depends on the partition name.

- `rootfs` is hardcoded to be split.
- `CONFIG_MTD_SPLIT_FIRMWARE` can be used to control whether attempt is made on `firmware` partition. The most common splitting here is kernel, followed by padding, followed by SquashFS root filesystem, followed by padding, followed by free space.

During splitting, the kernel walks the erase blocks and detects magic bytes via parsers. Each partition type (usually determined from name) has its own list of parsers.

New partitions are usually some offset into the start of the original partition. The size and number of the "children" depends on what is detected. For example if SquashFS image is found then the `rootfs` partition is added. For SquashFS image the splitter also automatically adds `rootfs_data` to the list of the available mtd partitions, setting this partition's beginning to the first appropriate address after the SquashFS end and size to the remainder of the `rootfs` partition.

The resulting list of split off partitions is stored in RAM only, so no partition table of any kind gets actually modified. This also includes detection and creation of `ubi` partition and others, as well as for vendor-specific layouts.

For more details please refer to the code for the mtdsplit: <https://github.com/openwrt/openwrt/tree/master/target/linux/generic/files/drivers/mtd/mtdsplit>

For overlaying a special `mini_fo` filesystem is used, the `README` is available from the sources at <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.37/209-mini_fo.patch>

## UBI (Unsorted Block Images)

Unsorted Block Images (UBI) is an `erase block` management layer in the Linux kernel for raw [NAND](../wiki/wiki_page-techref-flash.md) flash memory chips. It is layer on top of the MTD layer. UBI is used by [UBIFS](/docs/techref/filesystems#UBIFS).

UBI serves two purposes, tracking "bad erase blocks" of a raw [NAND](../wiki/wiki_page-techref-flash.md) flash memory chip and also providing wear-leveling. To accomplish this, UBI maps *logical erase blocks* to *physical erase blocks* and presents the first ones to higher layers.

- \[<http://www.linux-mtd.infradead.org/doc/ubi.html> UBI Documentation\]

## Discovery (How to find out)

    cat /proc/mtd
    dev:    size   erasesize  name
    mtd0: 00020000 00010000 "u-boot"
    mtd1: 00140000 00010000 "kernel"
    mtd2: 00690000 00010000 "rootfs"
    mtd3: 00530000 00010000 "rootfs_data"
    mtd4: 00010000 00010000 "art"
    mtd5: 007d0000 00010000 "firmware"

The *erasesize* is the [block size](https://en.wikipedia.org/wiki/Block (data storage)) of the flash, in this case 64KiB. The *size* is little or big [endian](https://en.wikipedia.org/wiki/Endianess) hex value in Bytes. In case of little endian, you switch to hex-mode and enter 02 0000 into the calculator for example and convert to decimal (by switching back to decimal mode again). Then guess how they are nested into each other. Or execute `dmesg` after a fresh boot and look for something like:

    Creating 5 MTD partitions on "spi0.0":
    0x000000000000-0x000000020000 : "u-boot"
    0x000000020000-0x000000160000 : "kernel"
    0x000000160000-0x0000007f0000 : "rootfs"
    mtd: partition "rootfs" set to be root filesystem
    mtd: partition "rootfs_data" created automatically, ofs=2C0000, len=530000
    0x0000002c0000-0x0000007f0000 : "rootfs_data"
    0x0000007f0000-0x000000800000 : "art"
    0x000000020000-0x0000007f0000 : "firmware"

These are the start and end offsets of the partitions as hex values in Bytes. Now you don't have to guess which is nested in which. E.g. 02 0000 = 131.072 Bytes = 128KiB.

## Details

### generic

The flash chip can be represented as a large block of continuous space:

|                                               |
|:----------------------------------------------|
| start of flash ................. end of flash |

There is no ROM to boot from; at power up the CPU begins executing the code at the very start of the flash. Luckily this isn't the firmware or we'd be in real danger every time we reflashed. Boot is actually handled by a section of code we tend to refer to as the [bootloader](bootloader) (the BIOS of your PC *is* a bootloader).

|          |                                          |                    |                              |                  |               |
|----------|------------------------------------------|--------------------|------------------------------|------------------|---------------|
|          | Boot Loader Partition                    | Firmware Partition | `Special Configuration Data` |                  |               |
| Atheros  | [U-Boot](/docs/techref/bootloader/uboot) | firmware           | `ART`                        |                  |               |
| Broadcom | CFE                                      | firmware           | `NVRAM`                      |                  |               |
| Atheros  | RedBoot                                  | firmware           | `FIS recovery`               | `RedBoot config` | `boardconfig` |

The partition or partitions containing so called *Special Configuration Data* differ very much from each other. Example: The `ART`-partition you will meet in conjunction with Atheros-Wireless and U-Boot, contains only data regarding the wireless driver, while the `NVRAM`-partition of broadcom devices is used for much more than only that. There are special utilities to access and modify special configuration partitions. For Broadcom devices this is the `nvram` utility. To find out what is written in `NVRAM` you can run `nvram show`.

Note that clearing these special configuration data partitions like `ART, NVRAM` and `FIS` does not clear much of OpenWrt's configuration, unlike other router software which keep configuration data solely in e.g. `NVRAM`. Instead, as a consequence of using the overlay_fs filesystem configuration with JFFS2 flash partition, the whole file system is writable and allows the flexibility of extending your OpenWrt installation in any way you want. OpenWrt's main configuration is therefore just kept in the root file system, using [UCI](/docs/guide-user/base-system/uci) configuration files. For convenience, many other packages are made UCI compatible. If you want to reset your complete installation you should use OpenWrt's built-in functionality such as [sysupgrade](/docs/guide-user/installation/generic.sysupgrade) to restore settings, by clearing the JFFS2 partition. Or, if you cannot boot normally, you can wipe or change the JFFS2 partition using OpenWrt's [failsafe mode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) (look in your device's dedicated page for information how to boot into failsafe).

### broadcom with CFE

If you dig into the "firmware" section you'll find a trx. A trx is just an encapsulation, which looks something like this:

| trx-header |        |       |       |          |      |     |
|------------|--------|-------|-------|----------|------|-----|
| HDR0       | length | crc32 | flags | pointers | data |     |

"HDR0" is a magic value to indicate a trx header, rest is 4 byte unsigned values followed by the actual contents. In short, it's a block of data with a length and a checksum. So, our flash usage actually looks something like this:

|     |                         |       |
|:---:|:-----------------------:|:-----:|
| CFE | trx containing firmware | NVRAM |

Except that the firmware is generally pretty small and doesn't use the entire space between CFE and NVRAM:

|     |              |        |       |
|:---:|:------------:|:------:|:-----:|
| CFE | trx firmware | unused | NVRAM |

(***`NOTE`*:** The \<model\>.bin files are nothing more than the generic \*.trx file with an additional header appended to the start to identify the model. The model information gets verified by the vendor's upgrade utilities and only the remaining data -- the trx -- gets written to the flash. When upgrading from within OpenWrt remember to use the \*.trx file.)

So what exactly is the firmware?

The boot loader really has no concept of filesystems, it pretty much assumes that the start of the trx data section is executable code. So, at the very start of our firmware is the kernel. But just putting a kernel directly onto flash is quite boring and consumes a lot of space, so we compress the kernel with a heavy compression known as [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm). Now the start of firmware is code for an LZMA decompress:

|                 |                        |
|:---------------:|:----------------------:|
| lzma decompress | lzma compressed kernel |

Now, the boot loader boots into an LZMA program which decompresses the kernel into RAM and executes it. It adds one second to the bootup time, but it saves a large chunk of flash space. (And if that wasn't amusing enough, it turns out the boot loader does know gzip compression, so we gzip compressed the LZMA decompression program)

Immediately following the kernel is the filesystem. We use SquashFS for this because it's a highly compressed readonly filesystem -- remember that altering the contents of the trx in any way would invalidate the crc, so we put our writable data in a JFFS2 partition, which is outside the trx. This means that our firmware looks like this:

|     |                        |               |                       |
|:---:|:-----------------------|:-------------:|:---------------------:|
| trx | gzip'd lzma decompress | lzma'd kernel | (SquashFS filesystem) |

And the entire flash usage looks like this -

|     |     |           |               |          |                  |       |
|:---:|:---:|:---------:|:-------------:|:--------:|:----------------:|:-----:|
| CFE | trx | gz'd lzma | lzma'd kernel | SquashFS | JFFS2 filesystem | NVRAM |

That's about as tight as we can possibly pack things into flash.

------------------------------------------------------------------------

## Explanations

### What is an Image File?

An image file is byte by byte copy of data contained in a file system. If you installed a Debian or a Windows in the usual way onto one or two hard disk partitions and would afterwards copy the whole content byte by byte from the hard disk into one file:

``` bash
dd if=/dev/sda of=/media/sdb3/backup.dd
```

the obtained backup file `/media/sdb3/backup.dd`, could be used in the exact same manner like an OpenWrt-Image-File.

The difference is, that OpenWrt-Image-File are not created that way ;-) They are being generated with the [Image Generator](/docs/guide-user/additional-software/imagebuilder) (former called Image Builder). Other resources:

- [headers](/docs/techref/headers)
- back to [downloads](/downloads)
- About [Broadcom Firmware Format](http://skaya.enix.org/wiki/FirmwareFormat)
