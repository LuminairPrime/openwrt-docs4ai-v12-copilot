---
title: Filesystems
module: wiki
origin_type: wiki_page
token_count: 3337
source_file: L1-raw/wiki/wiki_page-techref-filesystems.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_url: https://openwrt.org/docs/techref/filesystems
language: text
ai_summary: The Filesystems module in OpenWrt provides an overview of various file systems utilized for device built-in flash storage. It covers common file systems such as OverlayFS, tmpfs, SquashFS, and JFFS2, detailing their characteristics, advantages, and limitations. OverlayFS is used to merge read-only and writable file systems, while tmpfs operates like a RAM-Disk for temporary storage. SquashFS is a read-only compressed file system, and JFFS2 is a writable compressed file system with journaling and wear leveling features.
ai_when_to_use: This module is useful when configuring storage solutions for OpenWrt devices, particularly when selecting the appropriate file system for specific use cases such as temporary storage or read-only environments.
ai_related_topics:
- OverlayFS
- tmpfs
- SquashFS
- JFFS2
- flash.layout
- mtd
---
# Filesystems

This article is about file systems used by OpenWrt for device built-in flash.

For installing additional file systems, including partitioning and mounting, see this page for [general storage](/docs/guide-user/storage/start) as well as this page to other common [filesystems](/docs/guide-user/storage/filesystems-and-partitions).

Please read about the [flash.layout](flash.layout) as well. Also, note that there are two types of flash memory: [NOR flash](https://en.wikipedia.org/wiki/Flash_memory#NOR_flash) and [NAND flash](https://en.wikipedia.org/wiki/Flash_memory#NAND_flash). See also [mtd](/docs/techref/mtd).

## Common File System

### OverlayFS

Used to merge two filesystems, one read-only and the other writable. [flash.layout](flash.layout) explains how this is used in OpenWrt.

- [OverlayFS](https://en.wikipedia.org/wiki/OverlayFS)
- [Overlayfs documentation](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)
- <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.38/209-overlayfs.patch?rev=26213>
- [Debating overlayfs](http://lwn.net/Articles/447650/) on LWN.net
- Was mainlined in Linux kernel 3.18
- Overlayfs's support for inotify mechanisms is not complete yet. Events like IN_CLOSE_WRITE cannot be notified to listening process.

### tmpfs

[tmpfs](https://en.wikipedia.org/wiki/tmpfs) is implemented on many Unix-like operating systems (including OpenWrt). It operates similar to a RAM-Disk, without writing files to disk. In OpenWrt, `/tmp` resides on a tmpfs-partition and `/var` is a symlink to it; `/dev` resides on a little tmpfs partition of its own.

- [Kernel documentation on tmpfs](https://www.kernel.org/doc/html/latest/filesystems/tmpfs.html)

- (+) doesn't directly use space on non-volatile storage
- (-) no wear leveling
- (-) volatile (doesn't survive a reboot)

### SquashFS

[SquashFS](https://en.wikipedia.org/wiki/SquashFS) is a *read only* compressed filesystem. While [gzip](https://en.wikipedia.org/wiki/gzip) is available, at OpenWrt it uses [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) for the compression. Since SquashFS is a read only filesystem, it doesn't need to align the data, allowing it to pack the files tighter thus taking up significantly less space than JFFS2 (20-30% savings over a JFFS2 filesystem)!

- (+) taking up as little space as possible
- (+) allowing the implementation of an idiot proof [FailSafe](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) for recovery, since it is not possible to write to it
- (-) read only
- (-) waste space, since each time a file contained on it is modified, actually a copy of it is being copied to the second (JFFS2) partition
- [Kernel documentation on SquashFS](https://www.kernel.org/doc/html/latest/filesystems/squashfs.html)
- [SquashFs Performance Comparisons](https://elinux.org/Squash_Fs_Comparisons)

There is a generic problem when running SquashFS on [NAND](../wiki/wiki_page-techref-flash.md): The issue is that SquashFS has no bad block management at all and requires all blocks on order; but for proper [NAND](../wiki/wiki_page-techref-flash.md) bad block management you also need to be able to skip bad blocks and occasionally relocate blocks (see [squashfs and NAND flash](https://www.infradead.org/pipermail/linux-mtd/2006-April/015386.html)). That's why raw SquashFS is a bad idea on [NAND](../wiki/wiki_page-techref-flash.md) (it works if you use a FTL like UBIFS).

### JFFS2

[JFFS2](https://en.wikipedia.org/wiki/JFFS2) is a *writable* compressed filesystem with *[journaling](https://en.wikipedia.org/wiki/Journaling file system)* and *[wear leveling](https://en.wikipedia.org/wiki/wear leveling)* using [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) for the compression.

- (+) is writable, has journaling and wear leveling
- (+) is cool
- (-) is compressed, so a program (`opkg` in particular) cannot know in advance how much space a package will occupy
- (+) is compressed, so a program (which is preinstalled) takes much less space, so effectively you have more space

For [NAND](../wiki/wiki_page-techref-flash.md)-flash targets, it was replaced with UBIFS.

### UBIFS

- [UBIFS](https://en.wikipedia.org/wiki/UBIFS) is a file system for [raw flash](/docs/techref/flash.layout). It is used in OpenWrt [NAND](../wiki/wiki_page-techref-flash.md) targets since :FIXME: around r40364
- [Kernel documentation on UBIFS](https://www.kernel.org/doc/html/latest/filesystems/ubifs.html)
- [UBIFS File Encryption](https://lwn.net/Articles/704261/) how does UBIFS understand what a "file" is? Isn't a file
- [UBIFS File Encryption v1](https://lwn.net/Articles/706338/) on LWN.net
- [UBIFS File Encryption v2](https://lwn.net/Articles/707900/) on LWN.net
- [UBIFS Supports OverlayFS In Linux 4.9, Readying UBI For MLC Support](https://www.phoronix.com/scan.php?page=news_item&px=UBI-UBIFS-Linux-4.9)

### ext2

- [ext2](https://en.wikipedia.org/wiki/ext2)
- Ext2/3/4 is used on x86, x86-64 and for some arch with SD-card rootfs
- [Kernel documentation on ext2](https://www.kernel.org/doc/html/latest/filesystems/ext2.html)
- (+) a program (`opkg` in particularly) knows how much space is left!
- (+) good ol' veteran FOSS file system
- (-) no journaling (ext3, ext4 support journaling)
- (-) no wear leveling
- (-) no transparent compression

## Other filesystems

OpenWrt does not use other filesystems as rootfs. It supports several filesystems attached to via various mechanisms like USB, SATA or network. For a list see [start](/docs/guide-user/storage/start).

### mini_fo

- was used by older OpenWrt version and thus there are still references to this in the Wiki
- replaced by [\#OverlayFS](#OverlayFS) now.
- [The mini_fo filesystem](https://lwn.net/Articles/135283) on LWN.net
- [mini_fo: The mini fanout overlay file system](https://www.denx.de/wiki/bin/view/Know/MiniFOHome) official site

## Implementation in OpenWrt

The [flash.layout](/docs/techref/flash.layout) article documents how OpenWrt uses both SquashFS and JFFS2 filesystems combined into one filesystem by overlayfs. The kernel is also stored separately from these partitions in raw flash. When the kernel is built, it is also compressed with [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) and [gzip](https://en.wikipedia.org/wiki/gzip), as documented in [imagebuilder](/docs/guide-user/additional-software/imagebuilder).

### Boot process

System bootup is as follows: -\>[process.boot](process.boot)

1.  kernel boots from a known raw partition (without a FS), scans mtd partition *rootfs* for a valid superblock and mounts the SquashFS partition (containing `/etc`) then runs `/etc/preinit`. (More info at [filesystems#technical.details](/docs/techref/filesystems#technical.details))
2.  `/etc/preinit` runs `/sbin/mount_root`
3.  `mount_root` mounts the JFFS2 partition (`/overlay`) and **combines** it with the SquashFS partition (`/rom`) to create a new *virtual root filesystem* (`/`)
4.  bootup continues with `/sbin/init`

`/overlay` was previously named `/jffs2`

### Explanations

|                                                                   |
|-------------------------------------------------------------------|
| FIXME: Please feel free to merge Explanation 1 with Explanation 2 |

#### Explanations 1

Both SquashFS and JFFS2 are compressed filesystems using [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) for the compression. SquashFS is a *read only* filesystem while JFFS2 is a writable filesystem with *journaling* and *wear leveling*.
Our job when writing the firmware is to put as much common functionality on SquashFS while not wasting space with unwanted features. Additional features can always be installed onto JFFS2 by the user. The use of `mini_fo`/`overlayfs` means that the filesystem is presented as one large writable filesystem to the user with no visible boundary between SquashFS and JFFS2 -- files are simply copied to JFFS2 when they're written.
It's not all without side effects however.
The fact that we pack things so tightly in flash means that if the firmware ever changes, the size and location of the JFFS2 partition also changes, potentially wiping out a large chunk of JFFS2 data and corrupting the filesystem. To deal with this, we've implemented a policy that after each reflash the JFFS2 data is reformatted. The trick to doing that is a special value, `0xdeadc0de`; when this value appears in a JFFS2 partition, everything from that point to the end of the partition is wiped. So, hidden at the end of the firmware images, is the value 0xdeadcode, positioned such that it becomes the start of the JFFS2 partition.
The fact that we use a combination of compressed and partially read only filesystems also has an interesting effect on package management:
In particular, you need to be careful what packages you update. While `opkg` is more than happy to install an updated package on JFFS2, it's unable to remove the original package from SquashFS; the end result is that you slowly start using more and more space until the JFFS2 partition is filled. The opkg util really has no idea how much space is available on the JFFS2 partition since it's compressed, and so it will blindly keep going until the opkg system crashes -- at that point you have so little space you probably can't even use opkg to remove anything.

#### Explanation 2

On many embedded targets that use [NOR flash](https://en.wikipedia.org/wiki/Flash_memory#NOR_flash) for the root filesystem, OpenWrt implements a clever trick to get the most out of the limited flash memory capacity while retaining flexibility for the end-user:
Basically, during the image creation, all of the rootfs contents is packed up in a SquashFS filesystem -- a highly efficient filesystem with compression support. There's one important detail about it though: it is a read-only filesystem. To overcome this limitation OpenWrt uses the remaining portion of the NOR rootfs partition to store an additional read/write jffs2 filesystem which is "overlayed" on top of the rootfs (that is, allowing to read unchanged files from the SquashFS but storing all the modifications made to the jffs2 part).
This design has another important advantage for the end-user: even when the read/write partition is in total mess, he can always boot to the failsafe mode (which mounts only the squashfs part) and proceed from there.

### Technical Details

The kernel boot process involves discovering of partitions within the NOR flash and it can be done by various target-dependent means:

- some bootloaders store a partition table at a known location
- some pass the partition layout via kernel command line
- some targets require specifying the kernel command line at the compile time (thus overriding the one provided by the bootloader).

Either way, if there is a partition named `rootfs` and `MTD_ROOTFS_ROOT_DEV` kernel config option is set to `yes`, this partition is automatically used for the root filesystem.

After that, if `MTD_ROOTFS_SPLIT` is enabled, the kernel adjusts the `rootfs` partition size to the minimum required by the particular SquashFS image and automatically adds `rootfs_data` to the list of the available mtd partitions setting its beginning to the first appropriate address after the SquashFS end and size to the remainder of the original `rootfs` partition. The resulting list is stored in RAM only, so no partition table of any kind gets actually modified.

For more details please refer to the actual patch at: <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.37/065-rootfs_split.patch>

For overlaying a special `mini_fo` filesystem is used, the `README` is available from the sources at <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.37/209-mini_fo.patch>

#### Can we switch the filesystem to be entirely JFFS2?

***`Note:`***: It is possible to contain the entire root filesystem on a JFFS2-Partition only, instead of a combination of both. The advantage is that changes to included files no longer leaves behind an old copy on the read only filesystem. So you could end up saving space. The disadvantage of this would be, that you have no failsafe any longer and also, JFFS2 takes significantly more space then SquashFS.

Yes, it's technically possible, but a bit of a mess to actually pull off. The firmware has to be loaded as a trx file, which means that you have to put the JFFS2 data inside of the trx. But, as I said above, the trx has a checksum, meaning that if you ever change that data, you invalidate the checksum. The solution is that you install with the JFFS2 data contained within the trx, and then change the trx-boundaries at runtime. The end result is a single JFFS2 partition for the root filesystem. Why someone would want to do it is beyond me; it takes more space, and while it would allow you to upgrade the contents of the filesystem you would still be unable to replace the kernel (outside of the filesystem), meaning that a seamless upgrade between releases is still not possible! Having SquashFS gives you a failsafe mechanism where you can always ignore the JFFS2 partition and boot directly off SquashFS, or restore files to their original SquashFS versions.

I used to have a trick where I could convert a SquashFS install to a JFFS2 install at runtime by copying all the data onto the SquashFS partition and changing the partition boundaries. I never really had much use for the util -- not to mention it required a rather large flash to store both SquashFS and JFFS2 copies of the root during transition -- so support for it was dropped.

## Notes

Example pictures: on formatted partition / how data is stored (and addressed on ext3)

- how data is stored and addressed by ext2:
- how data is stored and addressed by ext3:
- how data is stored and addressed by SquashFS:
- how data is stored and addressed by JFFS2:
