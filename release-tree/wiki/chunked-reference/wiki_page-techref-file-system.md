---
title: OpenWrt File System Hierarchy / Memory Usage
module: wiki
origin_type: wiki_page
token_count: 1566
source_file: L1-raw/wiki/wiki_page-techref-file-system.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_url: https://openwrt.org/docs/techref/file_system
language: text
ai_summary: The OpenWrt File System Hierarchy and Memory Usage module provides a detailed overview of how flash storage is partitioned and utilized in OpenWrt devices, specifically using the TP-Link WR1043ND as an example. It outlines the different memory layers, including hardware specifications, kernel space, and user space allocations. Key components such as u-boot, firmware, kernel, and root filesystem are identified along with their respective sizes. Additionally, it highlights the usage of overlay filesystems and the distribution of main memory.
ai_when_to_use: This module is useful when configuring or troubleshooting memory usage and filesystem layout on OpenWrt devices. It is particularly relevant for developers working on embedded systems that require efficient memory management.
ai_related_topics:
- Flash Storage Partitioning
- main memory
- Kernel space
- User space
- overlayfs
---

> **Source:** [https://openwrt.org/docs/techref/file_system](https://openwrt.org/docs/techref/file_system)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-28

# OpenWrt File System Hierarchy / Memory Usage

| OpenWrt File System Hierarchy |                                                                     |                                       |                                                                       |                                                   |                                |                                |                                                   |                                                   |                    |
|:-----------------------------:|---------------------------------------------------------------------|---------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------|--------------------------------|--------------------------------|---------------------------------------------------|---------------------------------------------------|--------------------|
|                               | Flash Storage Partitioning (TP-Link WR1043ND)                       |                                       |                                                                       |                                                   |                                | Main Memory Usage              |                                                   |                                                   |                    |
|           Hardware            | m25p80 [spi](https://en.wikipedia.org/wiki/spi)0.0: m25p64 8192 KiB |                                       |                                                                       |                                                   |                                | main memory 32 768 KiB         |                                                   |                                                   |                    |
|            Layer1             | @#de401d:mtd0 ***u-boot*** 128 KiB                                  | @#25540b:mtd5 ***firmware*** 8000 KiB |                                                                       |                                                   | @#1dbade:mtd4 ***art*** 64 KiB | @#ff00ff:Kernel space 3828 KiB | @#00ffff:User space 28 940 KiB                    |                                                   |                    |
|            Layer2             | @#de401d:                                                           | @#a11dde:mtd1 ***kernel*** 1280 KiB   | @#378712:mtd2 ***rootfs*** 6720 KiB                                   |                                                   | @#1dbade:                      | @#ff00ff:                      | @#00ffff:up to 50%                                | @#00ffff:512 KiB                                  | @#00ffff:remaining |
|          mountpoint           | @#de401d:                                                           | @#a11dde:                             | @#378712:/                                                            |                                                   | @#1dbade:                      | @#ff00ff:                      | @#00ffff:                                         | @#00ffff:                                         | @#00ffff:          |
|          filesystem           | @#de401d:                                                           | @#a11dde:                             | @#378712:[filesystems#overlayfs](/docs/techref/filesystems#overlayfs) |                                                   | @#1dbade:                      | @#ff00ff:                      | @#00ffff:                                         | @#00ffff:                                         | @#00ffff:          |
|            Layer3             | @#de401d:                                                           | @#a11dde:                             | @#dea11d:1536 KiB                                                     | @#5ade1d:mtd3 ***rootfs_data*** 5184 KiB          | @#1dbade:                      | @#ff00ff:                      | @#00ffff:                                         | @#00ffff:                                         | @#00ffff:          |
|          mountpoint           | @#de401d:none                                                       | @#a11dde:none                         | @#dea11d:/rom                                                         | @#5ade1d:/overlay                                 | @#1dbade:none                  | @#ff00ff:                      | @#00ffff:/tmp                                     | @#00ffff:/dev                                     | @#00ffff:          |
|          filesystem           | @#de401d:none                                                       | @#a11dde:none                         | @#dea11d:[SquashFS](/docs/techref/filesystems#squashfs)               | @#5ade1d:[JFFS2](/docs/techref/filesystems#JFFS2) | @#1dbade:none                  | @#ff00ff:                      | @#00ffff:[tmpfs](/docs/techref/filesystems#tmpfs) | @#00ffff:[tmpfs](/docs/techref/filesystems#tmpfs) | @#00ffff:          |

### Mount Points

- `/` this is your entire root filesystem, it comprises `/rom` and `/overlay`. Please ignore `/rom` and `/overlay` and use exclusively `/` for your daily routines!
- `/rom` contains all the basic files, like `busybox`, `dropbear` or `iptables`. It also includes default configuration files used when booting into [OpenWrt Failsafe mode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset). It does not contain the Linux kernel. All files in this directory are located on the SqashFS partition, and thus cannot be altered or deleted. But, because we use overlay_fs filesystem, so called *overlay-whiteout*-symlinks can be created on the JFFS2 partition.
- `/overlay` is the writable part of the file system that gets merged with `/rom` to create a uniform `/`-tree. It contains anything that was written to the router after [installation](/docs/guide-user/installation/generic.flashing), e.g. changed configuration files, additional packages installed with `opkg`, etc. It is formated with JFFS2.
  Rather than deleting the files, insert a whiteout, a special high-priority entry that marks the file as deleted. File system code that sees a whiteout entry for file F behaves as if F does not exist.
  `#!/bin/sh
  # shows all overlay-whiteout symlinks in the directory /overlay

  find /overlay -type l | while read FILE
    do
      [ -z "$FILE" ] && break
      if ls -la "$FILE" 2>&- | grep -q '(overlay-whiteout)'; then
      echo "$FILE"
      fi
    done
  `
- `/tmp` is a tmpfs-partition `#!/bin/sh
  # shows current size of the tmpfs-partition mounted to /tmp
  calc_tmpfs_size() {pi_size=$(awk '/MemTotal:/ {l=10485760;mt=($2*1024);print((s=mt/2)<l)&&(mt>l)?mt-l:s}' /proc/meminfo)}}
  echo $pi_size
  `
- `/dev` [Driver Core: devtmpfs - kernel-maintained tmpfs-based /dev](http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2b2af54a5bb6f7e80ccf78f20084b93c398c3a8b)

## History

- early OpenWrt-versions: the rootfs was readonly and only NVRAM-variables could be edited
- symlink approach
- [mini_fo](../../wiki/chunked-reference/wiki_page-techref-filesystems.md) [r3667 add mini_fo patches to mount_root and firstboot](https://dev.openwrt.org/changeset/3667) and [r3669 mini_fo works](https://dev.openwrt.org/changeset/3669) and [r3928 enabled mini_fo by default](https://dev.openwrt.org/changeset/3928)
- overlayfs [r26209 kernel: replace mini_fo with overlayfs for 2.6.37](https://dev.openwrt.org/changeset/26209) and [r26213 kernel: replace mini_fo with overlayfs for 2.6.38](https://dev.openwrt.org/changeset/26213)
