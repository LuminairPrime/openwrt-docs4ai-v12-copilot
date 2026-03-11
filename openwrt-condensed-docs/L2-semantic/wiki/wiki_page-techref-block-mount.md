---
title: Mounting Block Devices
module: wiki
origin_type: wiki_page
token_count: 2063
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-block-mount.md
last_pipeline_run: '2026-03-11T14:46:50.602050+00:00'
language: text
---
# Mounting Block Devices

This pages discuses the advanced details and underlying operation. For general usage, see [fstab](/docs/guide-user/storage/fstab).

## Overview

The mounting of block devices is handled by the `block-mount` source package, which contains the `block-mount` and `block-hotplug` packages. `block-mount` contains the code that does the actual mounting, and the mounting via `/etc/init.d/fstab` (i.e. on boot rather than when device is hotplugged), and `block-hotplug` takes care of mounting devices when the device is recognized by the system (.e.g. when modules are loaded and the partition detected).

## block-mount (binary package)

~~The `block-mount` binary package (i.e. the one you actually install, rather than the source package containing `block-mount` and `block-hotplug`), contains three library scripts (in addition to `/etc/init.d/fstab` and the sample config file `/etc/config/fstab`). These three scripts are: `block.sh`, `mount.sh`, and `fsck.sh`. ~~

|                                                                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|-------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ![48px-outdated.svg.png](/meta/icons/tango/48px-outdated.svg.png) | As of [r26314](https://dev.openwrt.org/changeset/26314/trunk) `block-extroot` and `block-hotplug` have been merged with `block-mount`. That means that once you install `block-mount` the scripts for [extroot](/docs/guide-user/additional-software/extroot_configuration) mounting and hotplug mounting are installed. With [r36988](https://dev.openwrt.org/changeset/36988) the original package `block-mount` was removed. Technically, the new package `ubox` replaced its functionality. For [Fstab configuration](/docs/guide-user/storage/fstab), the new block-mount package now contains the executable `block` which facilitates this. You can run `block <info|mount|umount|detect>`. See [Fstab configuration](/docs/guide-user/storage/fstab). |

With the new block mount mechanism you can run `block info` to get the same output that blkid delivered (however it only returns info for filesystems it supports). You can do "block mount" to mount all devices (same as what `/etc/init.d/fstab restart` used to do. If you run "`block detect`" you will get a sample uci file for the currently attached block devices. That way you can do "`block detect | uci import fstab`" to store it

:!: block info cannot detect btrfs (added [r43868](https://dev.openwrt.org/changeset/43868/trunk)), xfs , jfs, ntfs, exfat, and some other FS. Use manual scripting to mount them.

:!: For ntfs mount [read here](https://forum.openwrt.org/t/block-mount-ntfs-not-a-tty/64350)

    root@OpenWrt:~# blkid
    /dev/sda1: TYPE="ext2"
    /dev/sda2: UUID="890c87d4-e276-4fb0-a34a-296db408d792" TYPE="ext4"
    /dev/sdb1: LABEL="OPENWRT-BTRFS" UUID="2412e056-a1d8-4710-bf0e-d54b8ff0662f" UUID_SUB="edd04b0f-ccf6-4978-9d76-1fa17921fe58" TYPE="btrfs"
    root@OpenWrt:~# block info
    /dev/sda1: VERSION="1.0" TYPE="ext2"
    /dev/sda2: UUID="890c87d4-e276-4fb0-a34a-296db408d792" VERSION="1.0" TYPE="ext4"

### The new block-mount in Barrier Breaker

#### Usage: block \<info\|mount\|umount\|detect\>

- **info** -\> get the same output that blkid delivered (including mtdblock)

      /dev/mtdblock2: UUID="0906f1b4-51688c99-666b11b5-71d70575" VERSION="4.0" TYPE="squashfs"
      /dev/mtdblock3: TYPE="jffs2"
      /dev/sda1: UUID="e81a771e-249f-4f9e-ab30-b2fb73789744" LABEL="overlay" NAME="EXT_JOURNAL" VERSION="1.0" TYPE="ext4"
      /dev/sda2: UUID="090b67fa-afbb-4771-8efd-7a515c742c18" LABEL="swap" VERSION="2" TYPE="swap"
      /dev/sda5: UUID="91f1-f7ed" LABEL="TRANSPORT" VERSION="FAT32" TYPE="vfat"
      /dev/sda6: UUID="b01791a5-647a-4ab0-9adf-5b626ee5407c" LABEL="daten" NAME="EXT_JOURNAL" VERSION="1.0" TYPE="ext4"
      /dev/sda7: UUID="9f822714-fb75-40c3-9382-f1df42343229" LABEL="rest" NAME="EXT_JOURNAL" VERSION="1.0" TYPE="ext4"

- **mount** -\> mount all devices listed in fstab
- **umount** -\> unmount all devices listed in fstab
- **detect** -\> get a sample uci file for the currently attached block devices

    config 'global'
        option  anon_swap   '0'
        option  anon_mount  '0'
        option  auto_swap   '1'
        option  auto_mount  '1'
        option  delay_root  '5'
        option  check_fs    '0'

    config 'mount'
        option  target  '/mnt/sda1'
        option  uuid    'e81a771e-249f-4f9e-ab30-b2fb73789744'
        option  enabled '0'

    config 'swap'
        option  uuid    '090b67fa-afbb-4771-8efd-7a515c742c18'
        option  enabled '0'

    config 'mount'
        option  target  '/mnt/sda5'
        option  uuid    '91f1-f7ed'
        option  enabled '0'

    config 'mount'
        option  target  '/mnt/sda6'
        option  uuid    'b01791a5-647a-4ab0-9adf-5b626ee5407c'
        option  enabled '0'

    config 'mount'
        option  target  '/mnt/sda7'
        option  uuid    '9f822714-fb75-40c3-9382-f1df42343229'
        option  enabled '0'
        option  options 'lazytime,noatime,background_gc=off,gc_merge'

you can do "`block detect | uci import fstab`" to store it as a sample config file (already with UUID ;-) )

### working/not working in Barrier Breaker as of 2015/01/30

|       | info          | detect        | on boot       | on plug       | mount/umount[^1] | needs         | and                                                              |
|-------|---------------|---------------|---------------|---------------|------------------|---------------|------------------------------------------------------------------|
| ext4  | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔    | kmod-fs-ext4  | libext2fs, :?: kmod-fs-autofs4                                   |
| swap  | @lightgreen:✔ | @lightgreen:✔ | ?             | ?             | ?                | ???           | swap-utils                                                       |
| vfat  | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔    | kmod-fs-vfat  | kmod-nls-base, kmod-nls-cp437, kmod-nls-iso8859-1, kmod-nls-utf8 |
| btrfs | @red:✘[^2]    | @red:✘        | @red:✘        | @red:✘        | @red:✘           | kmod-fs-btrfs | btrfs-progs                                                      |

## block-hotplug (binary package)

Block hotplug consists of three scripts, `10-swap`, `20-fsck`, and `40-mount`. When a block devices is added these scripts are executed in the order listed. So, first the device is checked for being a `swap` section, or to attempt to mount as swap, if it is not a defined section for swap or mount (this is known as `anon_swap` or anonymous swap). Then `20-fsck` checks if the device is listed as `enabled_fsck` and if so, attempts to check/repair the filesystem, and, finally, we check if the device should be mounted, either named, or anonymously (i.e. not listed in any section).

[^1]: with the mount command instead of block mount/block umount

[^2]: use btrfs-show to get the UUID
