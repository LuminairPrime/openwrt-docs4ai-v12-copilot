---
title: Abstract
module: wiki
origin_type: wiki_page
token_count: 12192
source_file: L1-raw/wiki/wiki_page-techref-preinit-mount.md
last_pipeline_run: '2026-03-27T20:02:39.961617+00:00'
source_url: https://openwrt.org/docs/techref/preinit_mount
language: text
ai_summary: The OpenWrt preinit and root mount system is responsible for the initial boot sequence and firstboot scripts that prepare the system for multiuser operation. It details the boot process from the moment the bootloader loads the kernel, through the execution of the `/etc/preinit` script, to the initialization of the root filesystem. The document outlines how various scripts are executed during this phase, including those for failsafe and external root filesystem configurations. Additionally, it provides an overview of available preinit scripts and their configurations.
ai_when_to_use: This module is useful when configuring the boot sequence of OpenWrt devices, especially for custom setups involving external storage or enhanced failsafe mechanisms.
ai_related_topics:
- preinit
- firstboot
- failsafe
- rootfs
- init
---
# Abstract

======= Preinit and Root Mount and Firstboot Scripts =======

FIXME Information may be outdated and obsolete information as of April, 2018; Overview, Preinit and Overview, Failsafe updated from April 2018 based on reading `master` code.

See [Rootfs on External Storage](/docs/guide-user/additional-software/extroot_configuration) for information on external rootfs mounting.

# Abstract

This document presents the preinit / firstboot boot sequence. The boot system is extensible via (new) packages such as rootfs on usb, or enhanced failsafe.

We describe the portion of the OpenWrt boot sequence that occurs before the 'init' program is executed (when booting in multiuser mode), as well as the script that is responsible for creating and initializing the root filesystem on the first boot after flashing the device with OpenWrt.

# Context: Boot Sequence

The basic OpenWrt boot sequence is:

1.  boot loader loads kernel
2.  kernel loads whilst scanning the mtd partition *rootfs* for a valid superblock for mounting the SquashFS partition (which contains /etc). More info at [filesystems#technical.details](/docs/techref/filesystems#technical.details)
3.  ~~kernel calls `/etc/preinit` (the kernel considers this to be the `init` (or root) process~~ `/sbin/init` now the init process, which in turn launches `/sbin/procd -h /etc/hotplug-preinit.json` (a.k.a., "plugd") followed by `/bin/sh /etc/preinit`. Each is launched via `fork` and `execvp` and managed by the uloop library in libubox.
4.  `/etc/preinit` prepares system for multiuser mode
5.  `/etc/preinit` `exec`s `/sbin/init` which becomes the `init` (or root) process and launches multiuser
6.  `/sbin/init` launches processes according to /etc/inittab.
7.  Typically the first process launched is `/etc/init.d/rcS` which causes the scripts in `/etc/rc.d` which begin with 'S' to be launched (in glob sort order). The `/etc/rc.d` directory is populated with symlinks to the scripts in `/etc/init.d`. Each script in `/etc/init.d` accepts `enable` and `disable` arguments for creating and removing the symlinks.
8.  These script initialize the system and also initialize daemons that wait for input, so that when all the scripts have executed the normal system is active. On first boot this initializing includes the process of preparing the root filesystem for use.

------------------------------------------------------------------------

# Overview

The following preinit scripts are available in the OpenWrt master branches for base and packages feed (Status September 2024)

|          |                  |             |             |                                                                                    |                                            |                    |                       |
|:---------|:-----------------|:------------|:------------|:-----------------------------------------------------------------------------------|:-------------------------------------------|:-------------------|:----------------------|
| repo     | packages         | target      | subtarget   | file-repo                                                                          | file-target                                | hook               | info                  |
| packages | openssh          | all         | all         | net/openssh/files/sshd.failsafe                                                    | /lib/preinit/99_10_failsafe_sshd           | failsafe           |                       |
| packages | btrfs-progs      | all         | all         | utils/btrfs-progs/files/btrfs-scan.init                                            | /lib/preinit/85_btrfs_scan                 | preinit_main       | INITRAMFS check 'NO'  |
| packages | lvm2             | all         | all         | utils/lvm2/files/lvm2.preinit                                                      | /lib/preinit/80_lvm2                       | preinit_main       | INITRAMFS check 'NO'  |
| base     | dropbear         | all         | all         | package/network/services/dropbear/files/dropbear.failsafe                          | /lib/preinit/99_10_failsafe_dropbear       | failsafe           |                       |
| base     | zyxel-bootconfig | all         | all         | package/utils/zyxel-bootconfig/files/95_apply_bootconfig                           | /lib/preinit/95_apply_bootconfig           | preinit_main       | INITRAMFS check 'YES' |
| base     | linux            | imx         | cortexa53   | target/linux/imx/cortexa53/base-files/lib/preinit/79_move_config                   | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | imx         | cortexa7    | target/linux/imx/cortexa7/base-files/lib/preinit/79_move_config                    | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | imx         | cortexa9    | target/linux/imx/cortexa9/base-files/lib/preinit/79_move_config                    | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | rockchip    | armv8       | target/linux/rockchip/armv8/base-files/lib/preinit/79_move_config                  | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | omap        |             | target/linux/omap/base-files/lib/preinit/79_move_config                            | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | qoriq       |             | target/linux/qoriq/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | sifiveu     |             | target/linux/sifiveu/base-files/lib/preinit/79_move_config                         | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | tegra       |             | target/linux/tegra/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | sunxi       |             | target/linux/sunxi/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/02_default_set_state                          | /lib/preinit/02_default_set_state          | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/02_sysinfo                                    | /lib/preinit/02_sysinfo                    | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/10_indicate_failsafe                          | /lib/preinit/10_indicate_failsafe          | failsafe           |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/10_indicate_preinit                           | /lib/preinit/10_indicate_preinit           | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/30_failsafe_wait                              | /lib/preinit/30_failsafe_wait              | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/40_run_failsafe_hook                          | /lib/preinit/40_run_failsafe_hook          | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/50_indicate_regular_preinit                   | /lib/preinit/50_indicate_regular_preinit   | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/70_initramfs_test                             | /lib/preinit/70_initramfs_test             | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/80_mount_root                                 | /lib/preinit/80_mount_root                 | preinit_main       | INITRAMFS check 'YES' |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/99_10_failsafe_login                          | /lib/preinit/99_10_failsafe_login          | failsafe           |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/99_10_run_init                                | /lib/preinit/99_10_run_init                | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | bcm47xx     |             | target/linux/bcm47xx/base-files/lib/preinit/01_sysinfo                             | /lib/preinit/01_sysinfo                    | preinit_main       |                       |
| base     | linux            | lantiq      | xway_legacy | target/linux/lantiq/xway_legacy/base-files/lib/preinit/05_set_preinit_iface_lantiq | /lib/preinit/05_set_preinit_iface_lantiq   | preinit_main       |                       |
| base     | linux            | lantiq      | xway        | target/linux/lantiq/xway/base-files/lib/preinit/05_set_preinit_iface_lantiq        | /lib/preinit/05_set_preinit_iface_lantiq   | preinit_main       |                       |
| base     | linux            | lanitq      | ase         | target/linux/lantiq/ase/base-files/lib/preinit/05_set_preinit_iface_lantiq         | /lib/preinit/05_set_preinit_iface_lantiq   | preinit_main       |                       |
| base     | linux            | armsr       |             | target/linux/armsr/base-files/lib/preinit/01_sysinfo_acpi                          | /lib/preinit/01_sysinfo_acpi               | preinit_main       |                       |
| base     | linux            | armsr       |             | target/linux/armsr/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/02_load_x86_ucode                          | /lib/preinit/02_load_x86_ucode             | preinit_main       |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/15_essential_fs_x86                        | /lib/preinit/15_essential_fs_x86           | ?                  |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/20_check_iso                               | /lib/preinit/20_check_iso                  | preinit_mount_root |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/79_move_config                             | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | x86         |             | target/linux/x86/generic/base-files/lib/preinit/45_mount_xenfs                     | /lib/preinit/45_mount_xenfs                | preinit_mount_root |                       |
| base     | linux            | x86         | 64          | target/linux/x86/64/base-files/lib/preinit/45_mount_xenfs                          | /lib/preinit/45_mount_xenfs                | preinit_mount_root |                       |
| base     | linux            | bcm27xx     |             | target/linux/bcm27xx/base-files/lib/preinit/05_set_preinit_iface_brcm2708          | /lib/preinit/05_set_preinit_iface_brcm2708 | preinit_main       |                       |
| base     | linux            | bcm27xx     |             | target/linux/bcm27xx/base-files/lib/preinit/79_move_config                         | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | bcm27xx     |             | target/linux/bcm27xx/base-files/lib/preinit/81_set_root_part                       | /lib/preinit/81_set_root_part              | preinit_main       | INITRAMFS check 'YES' |
| base     | linux            | mediatek    |             | target/linux/mediatek/base-files/lib/preinit/05_set_preinit_iface                  | /lib/preinit/05_set_preinit_iface          | preinit_main       |                       |
| base     | linux            | mediatek    |             | target/linux/mediatek/base-files/lib/preinit/06_set_rps_sock_flow                  | /lib/preinit/06_set_rps_sock_flow          | preinit_main       |                       |
| base     | linux            | mediatek    |             | target/linux/mediatek/base-files/lib/preinit/07_trigger_fip_scrubbing              | /lib/preinit/07_trigger_fip_scrubbing      | preinit_main       |                       |
| base     | linux            | mediatek    | mt7623      | target/linux/mediatek/mt7623/base-files/lib/preinit/07_set_iface_mac               | /lib/preinit/07_set_iface_mac              | preinit_main       |                       |
| base     | linux            | mediatek    | mt7623      | target/linux/mediatek/mt7623/base-files/lib/preinit/79_move_config                 | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/04_set_netdev_label           | /lib/preinit/04_set_netdev_label           | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/05_extract_factory_data.sh    | /lib/preinit/05_extract_factory_data.sh    | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/09_mount_cfg_part             | /lib/preinit/09_mount_cfg_part             | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/10_fix_eth_mac.sh             | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/75_rootfs_prepare             | /lib/preinit/75_rootfs_prepare             | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | apm821xx    |             | target/linux/apm821xx/base-files/lib/preinit/05_set_preinit_iface_apm821xx         | /lib/preinit/05_set_preinit_iface_apm821xx | preinit_main       |                       |
| base     | linux            | apm821xx    |             | target/linux/apm821xx/base-files/lib/preinit/05_set_iface_mac_apm821xx             | /lib/preinit/05_set_iface_mac_apm821xx     | preinit_main       |                       |
| base     | linux            | apm821xx    |             | target/linux/apm821xx/base-files/lib/preinit/79_move_config                        | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | ixp4xx      |             | target/linux/ixp4xx/base-files/lib/preinit/05_set_ether_mac_ixp4xx                 | /lib/preinit/05_set_ether_mac_ixp4xx       | preinit_main       |                       |
| base     | linux            | kirkwood    |             | target/linux/kirkwood/base-files/lib/preinit/07_set_iface_mac                      | /lib/preinit/07_set_iface_mac              | preinit_main       |                       |
| base     | linux            | mvebu       |             | target/linux/mvebu/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | mvebu       | cortexa53   | target/linux/mvebu/cortexa53/base-files/lib/preinit/82_uDPU                        | /lib/preinit/82_uDPU                       | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | mvebu       | cortexa9    | target/linux/mvebu/cortexa9/base-files/lib/preinit/81_linksys_syscfg               | /lib/preinit/81_linksys_syscfg             | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | ipq806x     |             | target/linux/ipq806x/base-files/lib/preinit/04_reorder_eth                         | /lib/preinit/04_reorder_eth                | preinit_main       |                       |
| base     | linux            | ath79       | generic     | target/linux/ath79/generic/base-files/lib/preinit/02_sysinfo_fixup                 | /lib/preinit/02_sysinfo_fixup              | preinit_main       |                       |
| base     | linux            | ath79       | generic     | target/linux/ath79/generic/base-files/lib/preinit/10_fix_eth_mac.sh                | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | ath79       | nand        | target/linux/ath79/nand/base-files/lib/preinit/10_fix_eth_mac.sh                   | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | bcm4908     |             | target/linux/bcm4908/base-files/lib/preinit/75_rootfs_prepare                      | /lib/preinit/75_rootfs_prepare             | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | gemini      |             | target/linux/gemini/base-files/lib/preinit/05_set_ether_mac_gemini                 | /lib/preinit/05_set_ether_mac_gemini       | preinit_main       |                       |
| base     | linux            | loongarch64 |             | target/linux/loongarch64/base-files/lib/preinit/01_sysinfo_acpi                    | /lib/preinit/01_sysinfo_acpi               | preinit_main       |                       |
| base     | linux            | loongarch64 |             | target/linux/loongarch64/base-files/lib/preinit/79_move_config                     | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | mpc85xx     |             | target/linux/mpc85xx/base-files/lib/preinit/05_set_preinit_iface_mpc85xx           | /lib/preinit/05_set_preinit_iface_mpc85xx  | preinit_main       |                       |
| base     | linux            | mpc85xx     |             | target/linux/mpc85xx/base-files/lib/preinit/10_fix_eth_mac.sh                      | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | layerscape  |             | target/linux/layerscape/base-files/lib/preinit/02_sysinfo_fixup                    | /lib/preinit/02_sysinfo_fixup              | preinit_main       |                       |
| base     | linux            | layerscape  |             | target/linux/layerscape/base-files/lib/preinit/79_move_config                      | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | ramips      | mt7621      | target/linux/ramips/mt7621/base-files/lib/preinit/04_set_netdev_label              | /lib/preinit/04_set_netdev_label           | preinit_main       |                       |
| base     | linux            | ramips      | rt305x      | target/linux/ramips/rt305x/base-files/lib/preinit/04_handle_checksumming           | /lib/preinit/04_handle_checksumming        | preinit_main       |                       |
| base     | linux            | ramips      | rt3883      | target/linux/ramips/rt3883/base-files/lib/preinit/04_handle_checksumming           | /lib/preinit/04_handle_checksumming        | preinit_main       |                       |
| base     | linux            | ipq40xx     |             | target/linux/ipq40xx/base-files/lib/preinit/05_set_iface_mac_ipq40xx.sh            | /lib/preinit/05_set_iface_mac_ipq40xx.sh   | preinit_main       |                       |
| base     | linux            | octeon      |             | target/linux/octeon/base-files/lib/preinit/01_sysinfo                              | /lib/preinit/01_sysinfo                    | preinit_main       |                       |
| base     | linux            | octeon      |             | target/linux/octeon/base-files/lib/preinit/79_move_config                          | /lib/preinit/79_move_config                | preinit_mount_root |                       |

## Preinit

Preinit brings the system from raw kernel to ready for multiuser. To do so, as of April, 2018, `/etc/preinit` (ar71xx, Archer C7) performs the following tasks:

1.  Checks to see if `$PREINIT` is empty; if so `exec /sbin/init` and skip the rest
2.  Sources a set of files for common functions for boot/mount:
    - `/lib/functions.sh`
    - `/lib/functions/preinit.sh`
    -  `/lib/functions/system.sh`
3.  Prepares the "hooks" for the various stages of the preinit process
    - preinit_essential
    - preinit_main
    - failsafe
    - initramfs
    - preinit_mount_root
4.  Source the contents of `/lib/preinit/*` which generally add `sh` functions to the appropriate hooks
5.  Runs the `preinit_essential` hooks
6.  Runs the `preinit_main` hooks

On an ar71xx device (Archer C7) the default functions added to the various hooks include (with functions from device-specific files in *italics):*

- **preinit_main**
  1.  *do_ar71xx*
  2.  define_default_set_state
  3.  do_sysinfo_generic
  4.  *preinit_set_mac_address*
  5.  *set_preinit_iface*
  6.  preinit_ip
  7.  pi_indicate_preinit
  8.  failsafe_wait
  9.  run_failsafe_hook
      - **failsafe** (if "\$pi_preinit_no_failsafe" != "y" and "\$FAILSAFE" = "true")
        1.  indicate_failsafe
        2.  failsafe_netlogin
        3.  failsafe_shell
  10. indicate_regular_preinit
  11. do_mount_root (if "\$INITRAMFS" != "1")
  12. do_urandom_seed
  13. *check_patch_ath10k_firmware*
  14. run_init

Presently unused hooks, at least for the ar71xx Archer C7, appear to include

- preinit_essential
- initramfs
- preinit_mount_root

## Failsafe

The *root file system* is actually an overlay which can be consisted of a read-only SquashFS file system (mounted at `/rom`) and a writable JFFS2 partition (mounted under `/overlay`). In Failsafe mode only the squashfs FS will be mounted (changes made to jffs2 partitons will be ignored), plus the following steps:

1.  Notifies that failsafe mode is being entered (indicate_failsafe)
2.  Launches daemon to allow network logins (failsafe_netlogin)
3.  Allows login via serial console, if there is one (failsafe_shell)
    - If the serial console login process exits, failsafe doesn't exit, but restarts the process for additional logins.

## Mount Root Filesystem

all_jffs2 refers to a 'jffs2' target in menuconfig; e.g. firmware has no squashfs, but is purely a rw filesystem (jffs2), while, jffs2 in the following text refers to the jffs2 portion of a [squashfs/jffs2](/docs/techref/filesystems#overlayfs) system.

1.  Kernel has previously mounted squashfs partition by scanning the mtd partition `rootfs` for a valid superblock (see step 2 of [preinit_mount#contextboot.sequencel](/docs/techref/preinit_mount#contextboot.sequencel)) FIXME **Make sure it's correct**
2.  If there is no mtd device with label `rootfs_data`, then mounts `/dev/root` (e.g. squashfs or all_jffs2 with no squashfs) as root filesystem, and indicates that further steps should be skipped
3.  If mtd device `rootfs_data` has not already been formatted, mounts a tmpfs (ramdisk) as root filesystem, and indicates that further steps should be skipped.
4.  Mounts previously formatted jffs2 partition on `/overlay` and indicates successful mount.
5.  Makes successfully mounted `/overlay` (if it exists) the new root filesystem and moves previous root filesystem to `/rom`, and indicates to skip further steps.
6.  This is only reached on an error condition; attempts to mount a tmpfs (ramdisk) as root filesystem
7.  This is only reached if no other step succeeds; attempt to mount `/dev/root` (e.g. squashfs/all_jffs2) as root filesystem.

\*\* \* \*\* `/overlay` was previously named `/jffs2`.
\*\* \* \*\* [NOTE](../wiki/wiki_page-techref-luci2.md): If volatile files (e.g. a config) were preserved across firmware update via `sysupgrade`, step 3 is skipped. Instead, preinit_main hangs while the rootfs_data partition is formatted and the jffs2 overlay is mounted. Hypothetically, this is fatal on systems with weak cpu and exceptionally large rootfs_data partitions. For more information [consult this forum post](https://forum.openwrt.org/t/error-in-preinit-documentation-regarding-overlays/60188/4).

## First Boot

Updated to version 23.05. And, likely applies to a number of previous versions.

`/sbin/firstboot` is a script that simply calls `/sbin/jffs2reset $@` which clears the overlay if it's mounted:

- -y Answer yes to "Are you sure?"
- -r Reboot instead of returning control to the caller.
- -k Keep the file `/sysupgrade.tgz` while clearing the overlay.

`/lib/preinit/80_mount_root` will extract the contents of `/sysupgrade.tgz` into the overlay after the reboot. This mechanism may be used to write into `/etc/uci-defaults` as a way to create a custom configuration immediately after the reboot.

### Common

1.  Source `/lib/functions/boot.sh` for common functions (e.g. also used by preinit)
2.  Source files used by hooks
3.  Determine how called, and branch to appropriate commands.

### Sourced rather than executed

1.  Determine (and set variable for) MTD rootfs_data partition
2.  Determine (and set variable for) rom partition
3.  Determine (and set variable for) jffs2 partition

### Executed with no parameters

- Resets jffs2 to original settings, if possible.
- If jffs2 is not mounted, erases mtd and attempts format, mount, and pivot jffs2 as root.

If jffs2 is mounted, `firstboot` runs hook `jffs2reset`

1.  Determine (and set variable for) MTD rootfs_data partition
2.  Determine (and set variable for) rom partition
3.  Determine (and set variable for) jffs2 partition
4.  Determine (and set variable to indicate) whether the mini overlay filesystem type is supported.
5.  If overlay is supported, remove all files on jffs2 and remount it.
6.  If overlay not supported, create directories and symlinks, copying only certain critical files

- Note: since r35712 the firstboot script requires an inputted 'y' as confirmation. If using firstboot in a reset button script, you need to get that y inputted, e.g. by using the yes command: yes \| firstboot

### Executed with parameter 'switch2jffs'

1.  Determine (and set variable for) MTD rootfs_data partition
2.  Determine (and set variable for) rom partition
3.  Determine (and set variable for) jffs2 partition
4.  Determine if mini overlay is supported. If not run hook no_fo
5.  Otherwise, if mounted, skip the rest, otherwise mount under squashfs (`/rom/jffs`)
6.  Copy ramdisk to jffs2
7.  Move `/jffs` to `/` (root) and move `/` (root) to `/rom`
8.  Cleanup

### hook no_fo

1.  Switch to kernel fs, get rid of union overlay and bind from /tmp/root
2.  Mount jffs (and make it safe for union)
3.  If not mounted, mount; copy from squashfs, and pivot so that /jffs is now / (root)
4.  Copy files from ramdisk
5.  Get rid of unnecessary mounts (cleanup)

# Preinit Operation

Preinit consists of a number of scripts. The main script is `/etc/preinit` which reads in the scripts. The scripts define functions which they attach to hooks. These hooks are, when processed, launching the functions in the order they were added to the hooks.

Currently there are five hooks used by the preinit system:

- `preinit_essential`
- `preinit_main`
- `failsafe`
- `initramfs`
- `preinit_mount_root`

Each hook have a corresponding string variable containing the name of each function to be executed, separated by spaces. The hook variables have `_hook` appended to the hook name. Thus the name of the variable for the `preinit_essential` hook is `preinit_essential_hook`.

## Main Preinit Script

The main preinit script is actually quite empty. It:

1.  Initializes some variables (including the hook variables)
2.  Defines the function `pi_hook_add`, which is used to add functions to a hook
3.  Defines the function `pi_run_hook`, which executes the functions that were added to a hook
4.  Sources (reads) the shell scripts under folder `/lib/preinit/`, in glob sort order
5.  Processes the hook `preinit_essential`
6.  Initializes variables used by `preinit_main`
7.  Processes the hook `preinit_main`

That's it.

## Variables

There are a number of variables that control options of preinit. Defaults are defined in the main script `/etc/preinit` defined by the `base-files` package. However the variables are customizable via `make menuconfig`, in section "Preinit configuration options". The OpenWrt build process will then create the file `/lib/preinit/00_preinit.conf` which will be sourced by the main script.

The variables defined at present are:

| Variable                        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|:--------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `pi_ifname`                     | The device name of the network interface used to emit network messages during preinit (except failsafe)                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `pi_ip`                         | The IP address of the preinit network (see above)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `pi_broadcast`                  | The broadcast address of the preinit network (see above)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `pi_netmask`                    | The netmask for the preinit network (see above)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `fs_failsafe_wait_timeout`      | How long to pause while allowing the user to choose to enter failsafe mode. Default is two (2) seconds.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `pi_suppress_stderr`            | If this is "y", then output on standard error (stderr, file descriptor 2), is ignored during preinit. This is the default in previous versions of OpenWrt (which did not have this option)                                                                                                                                                                                                                                                                                                                                                      |
| `pi_init_suppress_stderr`       | If `pi_suppress_stderr` is not "y" (i.e. stderr is not suppressed for preinit), then this option controls whether init, and process run by init, except those associated with a terminal device (e.g. `tts/0`, `ttyS0`, `tty1`, `pts/0`, or other similar devices) will have stderr suppressed (not that network terminals such as those from SSH are associated with a pseudo-terminal device such as `pty0/pty1` and are thus unaffected). As with `pi_suppress_stderr`, the default, and behaviour from previous versions of OpenWrt is "y". |
| `pi_init_path`                  | The default search PATH for binaries for commands run by init. Default is `/bin:/sbin:/usr/bin:/usr/sbin`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `pi_init_cmd`                   | The command to run as `init`. Default is `/sbin/init`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `pi_preinit_no_failsafe_netmsg` | suppress netmsg to say that one can enter failsafe mode                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `pi_preinit_net_messages`       | If enabled, show more network messages than just the message that one can enter failsafe mode                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

There are also variables used in the operation of preinit. They are:

| Variable                  | Description                                                                                                        |
|:--------------------------|:-------------------------------------------------------------------------------------------------------------------|
| `preinit_essential_hook`  | Variable containing hook names to execute, in order, for hook `preinit_essential`                                  |
| `preinit_main_hook`       | Ditto, for `preinit_main`                                                                                          |
| `failsafe_hook`           | Ditto, for `failsafe`                                                                                              |
| `initramfs_hook`          | Ditto, for `initramfs`                                                                                             |
| `preinit_mount_root_hook` | Ditto, for `preinit_mount_root`                                                                                    |
| `pi_mount_skip_next`      | During hook `preinit_mount_root`, skips most steps; usually set by a preceeding step                               |
| `pi_jffs2_mount_success`  | During hook `preinit_mount_root`, used by steps following mount attempt to determine which action they should take |

## Hooks

The following sections describe the files and functions used by the various hooks.

**NB**: The files, even though divided by hook here are all in the single `/lib/preinit` directory, and are thus combined in the directory lists, and are processed in glob sort order, not by hook (when sourcing them, the hooks specify the order of the execution of functions, which is as listed below)

### Development

For the purposes of development, you will locate the files under `$ROOTDIR/package/base-files/files/lib/preinit`, for the existing files, and you can add new files anywhere that ultimately ends up in `/lib/preinit` on the router (while in preinit, e.g. not by user edits after read-write is mounted).

### preinit_essentials

:!: With the introduction of [procd](/docs/techref/procd), effective in Chaos Calmer release, the tasks of this hook are done in c code and at least on some images (verified on a BRCM63xx one) this hook is unused.

The preinit_essentials hook takes care of mounting essential kernel filesystems such as proc, and initializing the console.

Files containing the functions executed by this hook

| File               | Functions                                                         |
|:-------------------|:------------------------------------------------------------------|
| 10_essential_fs    | do_mount_procfs, do_mount_sysfs, do_mount_tmpfs                   |
| 20_device_fs_mount | do_mount_devfs, do_mount_hotplug, do_mount_udev, choose_device_fs |
| 30_device_daemons  | init_hotplug, init_udev, init_device_fs                           |
| 40_init_shm        | init_shm                                                          |
| 40_pts_mount       | do_mount_pts                                                      |
| 50_choose_console  | choose_console                                                    |
| 60_init_console    | init_console                                                      |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function         | Description                                                                                                                                                |
|:-----------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| do_mount_procfs  | mounts /proc                                                                                                                                               |
| do_mount_sysfs   | mounts /sys                                                                                                                                                |
| do_mount_tmpfs   | mounts /tmp                                                                                                                                                |
| choose_device_fs | determines type of device daemon and the appropriate filesystem to mount on /dev for that device daemon                                                    |
| init_device_fs   | launches daemons (if any) responsible for population /dev, and/or creating hotplug events when devices are added/removed (and for initial coldplug events) |
| init_shm         | makes sure /dev/shm exists                                                                                                                                 |
| init_pts         | makes sure /dev/pts exists                                                                                                                                 |
| do_mount_pts     | mounts devpts on /dev/pts (pseudo-terminals)                                                                                                               |
| choose_console   | determines devices for stdin, stdout, and stderr                                                                                                           |
| init_console     | activates stdin, stdout, and stderr of preinit (and subsequent init) (prior to this they are not present in the environment)                               |

Functions which are called by other functions, rather than directly as part of a hook

| Function         | Description                                                 |
|:-----------------|:------------------------------------------------------------|
| do_mount_devfs   | mount devfs on /dev                                         |
| do_mount_hotplug | mount tmpfs on /dev (for hotplug)                           |
| do_mount_udev    | mount tmpfs on /dev (for udev)                              |
| init_hotplug     | set hotplug handler (actually initiated after console init) |
| init_udev        | start udev                                                  |

### preinit_main

The *preinit_main* hook performs all the functions required of preinit, except those functions, like console, that are essential even for preinit tasks.

| File                        | Description                                                                                           |
|:----------------------------|:------------------------------------------------------------------------------------------------------|
| 10_indicate_preinit         | preinit_ip, preinit_ip_deconfig, preinit_net_echo, preinit_echo, pi_indicate_led, pi_indicate_preinit |
| 30_failsafe_wait            | fs_wait_for_key, failsafe_wait                                                                        |
| 40_run_failsafe_hook        | run_failsafe_hook                                                                                     |
| 50_indicate_regular_preinit | indicate_regular_preinit_boot                                                                         |
| 60_init_hotplug             | init_hotplug                                                                                          |
| 70_initramfs_test           | initramfs_test                                                                                        |
| 80_mount_root               | do_mount_root                                                                                         |
| 90_restore_config           | restore_config                                                                                        |
| 99_10_run_init              | run_init                                                                                              |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function                      | Description                                                                                                                                                                                                |
|:------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| init_hotplug                  | Initialize hotplug, if needed (that is for devfs). Hotplug or a device daemon is needed so that devices are available for use for preinit                                                                  |
| preinit_ip                    | Initialize network interface (if one has been defined for as available for preinit)                                                                                                                        |
| pi_indicate_preinit           | Send messages to console, network, and/or led, depending on which, if any, of these is present which say that we are in preinit mode                                                                       |
| failsafe_wait                 | Emits messages (to network and console) that indicate the user has the option to enter failsafe mode and wait for the configured period of time (default two seconds) for the user to select failsafe mode |
| run_failsafe_hook             | If user chooses to enter failsafe mode, run the \*failsafe\* hook (which at present doesn't return, which means no more functions from preinit_main get run on this boot)                                  |
| indicate_regular_preinit_boot | Emits messages to network, console, and/or LED depending on which (if any) is present, indicating that it's a regular boot not a failsafe boot                                                             |
| initramfs_test                | If initramfs is present run the \*initramfs\* hook and exit                                                                                                                                                |
| do_mount_root                 | Executes hook \*preinit_mount_root\*                                                                                                                                                                       |
| restore_config                | If a previous configuration was stored by sysupgrade, restore it to the rootfs                                                                                                                             |
| run_init                      | Exec the command defined by \`pi_init_cmd\` with the environment variables defined by \`pi_init_env\`, plus PATH \`pi_init_path\`                                                                          |

Functions which are called by other functions, rather than directly as part of a hook.

| Function            | Description                                                                 |
|:--------------------|:----------------------------------------------------------------------------|
| preinit_ip_deconfig | deconfigure interface used for preinit network messages etc                 |
| preinit_net_echo    | emit a message on the preinit network interface                             |
| preinit_echo        | emit a message on the (serial) console                                      |
| pi_indicate_led     | set LED status to indicate preinit mode                                     |
| fs_wait_for_key     | wait for reset button press, CTRL-C, or \<some_key\>\<ENTER\>, with timeout |

### failsafe

Do what needs to done to prepare failsafe mode and enter it.

| File                 | Description                              |
|:---------------------|:-----------------------------------------|
| 10_indicate_failsafe | indicate_failsafe_led, indicate_failsafe |
| 99_10_failsafe_login | failsafe_netlogin, failsafe_shell        |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function          | Description                                                                                                                                      |
|:------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
| indicate_failsafe | Emit message/status to network, console, and/or LED (depending on which, if any, are present) indicating that the device is now in failsafe mode |
| failsafe_netlogin | Launch telnet daemon to allow telnet login on the defined network interface (if any)                                                             |
| failsafe_shell    | Launch a shell for access via serial console (if present)                                                                                        |

Functions which are called by other functions, rather than directly as part of a hook

| Function              | Description                             |
|:----------------------|:----------------------------------------|
| indicate_failsafe_led | set LED status to indicate preinit mode |

### preinit_mount_root

Mount the root filesystem

| File             | Description                 |
|:-----------------|:----------------------------|
| 05_mount_skip    | check_skip                  |
| 10_check_for_mtd | mount_no_mtd, check_for_mtd |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function          | Description                                                                                                                          |
|:------------------|:-------------------------------------------------------------------------------------------------------------------------------------|
| check_for_mtd     | Check for a mtd partition named rootfs_data. If not present mount kernel fs as root (e.g. all_jjfs2 or squashfs only) and skip rest. |
| check_for_jffs2   | Check if jffs2 formatted yet. If not, mount ramoverlay and skip rest                                                                 |
| do_mount_jffs2    | find jffs2 partition and mount it, indicating result                                                                                 |
| rootfs_pivot      | if jffs2 mounted, make it root (/) and old root (squashfs) /rom , skipping rest on success                                           |
| do_mount_no_jffs2 | If nothing was mounted so far, mount ramdisk (ram overlay), skipping rest on success                                                 |
| do_mount_no_mtd   | If there was nothing mounted , mount /dev/root as root (/)                                                                           |

Functions which are called by other functions, rather than directly as part of a hook

| Function          | Description                                                                                                                                                                   |
|:------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mount_no_mtd      | if there is not mtd partition named rootfs_data, mount /dev/root as / (root). E.g. this can occur if the firmware filesystem is entirely a jffs2 partition, with no squashfs) |
| mount_no_jffs2    | mount ramdisk (ram overlay) if there is rootfs_data, but it has not been formatted yet)                                                                                       |
| find_mount_jffs2  | find and mount rootfs_data jffs2 partition on /jffs                                                                                                                           |
| jffs2_not_mounted | returns true (0) if jffs2 is not mounted                                                                                                                                      |

### initramfs

No files or functions at this time.

# Firstboot Operation

## Main Firstboot Script

1.  Source common functions
2.  Source functions for hooks
3.  if block:

      if invoked as executable
           if called with `switch2jffs` parameter (i.e. from rcS)
               run hook `switch2jffs`
           if called standalone (e.g. from commandline)
               if there is a jffs2 partition mounted
                    run hook `jffs2reset`
               else
                    erase rootfs_data mtd partition
                    format
                    and remount it
               end
           end
     if sourced (that is not executed)
          set some variables
     end

## Hooks

### switch2jffs

Make the filesystem that we want to be the rootfs, to be the rootfs

| File                  | Description                                                                                               |
|:----------------------|:----------------------------------------------------------------------------------------------------------|
| 10_determine_parts    | deterimine_mtd_part, determine_rom_part, determine_jffs2_part, set_mtd_part, set_rom_part, set_jffs2_part |
| 20_has_mini_fo        | check_for_mini_fo                                                                                         |
| 30_is_rootfs_mounted  | skip_if_rootfs_mounted                                                                                    |
| 40_copy_ramoverlay    | copy_ramoverlay                                                                                           |
| 50_pivot              | with_fo_pivot                                                                                             |
| 99_10_with_fo_cleanup | with_fo_cleanup                                                                                           |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function               | Description                                                                                                   |
|:-----------------------|:--------------------------------------------------------------------------------------------------------------|
| determine_mtd_part     | exit if no mtd partition at all                                                                               |
| determine_rom_part     | exit if not squashfs partition (firstboot not for all_jffs2)                                                  |
| determine_jffs2_part   | figure out the jffs2 partition (assuming we have an mtd part                                                  |
| check_for_mini_fo      | determine if we have [mini_fo](../wiki/wiki_page-techref-filesystems.md) overlay in kernel. If not run \*no_fo\* hook                                     |
| skip_if_rootfs_mounted | attempt mount jffs2 on /rom/jffs2. If partition already mounted exit                                          |
| copy_ramoverlay        | copy the data from the temporary rootfs (on the ramdisk overlay over the squashfs) to the new jffs2 partition |
| with_fo_pivot          | make current jffs2 partition the root partition and the current root /rom                                     |
| with_fo_cleanup        | clean up unneeded mount of ramdisk, if possible                                                               |

Functions which are called by other functions, rather than directly as part of a hook

| Function      | Description                               |
|:--------------|:------------------------------------------|
| set_mtd_part  | set variables for mtd partition           |
| set_rom_part  | set variable for squashfs (rom) partition |
| set_jffs_part | set variable for jffs2 partition          |

### no_fo

Make the filesystem that we want to be the rootfs, to be the rootfs, given that we have no mini\\fo overlay filesystem

| File                      | Description            |
|:--------------------------|:-----------------------|
| 10_no_fo_clear_overlay    | no_fo_clear_overlay    |
| 20_no_fo_mount_jffs       | no_fo_mount_jffs       |
| 30_no_fo_pivot            | no_fo_pivot            |
| 40_no_fo_copy_ram_overlay | no_fo_copy_ram_overlay |
| 99_10_no_fo_cleanup       | no_fo_cleanup          |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function               | Description                                                                     |
|:-----------------------|:--------------------------------------------------------------------------------|
| no_fo_clear_overlay    | stop ramdisk overlaying the squashfs                                            |
| no_fo_mount_jffs       | attempt to mount jffs (work around problem with union). If already mounted exit |
| no_fo_pivot            | make jffs root and old root /rom                                                |
| no_fo_copy_ram_overlay | copy data from ram overlay to jffs2 overlay of squashfs                         |
| no_fo_cleanup          | get rid of extra binds and mounts                                               |

### jffs2reset

Reset jffs2 to defaults

| File                | Description             |
|:--------------------|:------------------------|
| 10_rest_has_mini_fo | reset_check_for_mini_fo |
| 20_reset_clear_jffs | reset_clear_jffs        |
| 30_reset_copy_rom   | reset_copy_rom          |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function                | Description                                                                                             |
|:------------------------|:--------------------------------------------------------------------------------------------------------|
| reset_check_for_mini_fo | Determine if the kernel supports [mini_fo](../wiki/wiki_page-techref-filesystems.md) overlay                                                        |
| reset_clear_jffs        | if [mini_fo](../wiki/wiki_page-techref-filesystems.md) is supported, erase all data in overlay and remount (resets back to 'pure' squashfs versions |
| reset_copy_rom          | if [mini_fo](../wiki/wiki_page-techref-filesystems.md) is not supported, make symlinks and copy critical files from squashfs to jffs                |

# Customizing the system

**NB**: These files must be added to the \*squashfs\* (or if using a all_jffs2 system, to the jffs2). That means, for instance adding it to the image's rootfs. This can be done, for instace, by creating \`\${ROOTDIR}/files/filename\` (with appropriate substitutions of course).

## Overriding Example

![dangerous&noheader&nofooter&noeditbtn](/page>meta/infobox/dangerous&noheader&nofooter&noeditbtn)

Customizing the system is quite simple. We give an example of changing the message for preinit from '- preinit -' to '- setting the table for dinner -'

Create a file that replaces the function \`indicate_regular_preinit_boot\`. \`pi_indicate_preinit\` is defined in \`20_indicate_preinit\`, so we define our replace functions in \`25_dinner_not_router\`.

\`/lib/preinit/25_dinner_not_router\`

       pi_indicate_preinit() {
             echo "- setting the table for dinner -"
             preinit_net_echo "Dinner is just about ready!"
             pi_indicate_led
       }

This results in the following boot log:

      NET: Registered protocol family 17
      802.1Q VLAN Support v1.8 Ben Greear <greearb@candelatech.com>
      All bugs added by David S. Miller <davem@redhat.com>
      VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
      Freeing unused kernel memory: 132k freed
      Please be patient, while OpenWrt loads ...
      eth1: link forced UP - 100/full - flow control off/off
      - setting the table for dinner -
      Press CTRL-C or Press f<ENTER> to enter failsafe mode
      switching to jffs2
      [mini_fo](../wiki/wiki_page-techref-filesystems.md): using base directory: /
      [mini_fo](../wiki/wiki_page-techref-filesystems.md): using storage directory: /jffs
      - init -

The default boot log is

      NET: Registered protocol family 17
      802.1Q VLAN Support v1.8 Ben Greear <greearb@candelatech.com>
      All bugs added by David S. Miller <davem@redhat.com>
      VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
      Freeing unused kernel memory: 132k freed
      Please be patient, while OpenWrt loads ...
      eth1: link forced UP - 100/full - flow control off/off
      - preinit -
      Press CTRL-C or Press f<ENTER> to enter failsafe mode
      switching to jffs2
      [mini_fo](../wiki/wiki_page-techref-filesystems.md): using base directory: /
      [mini_fo](../wiki/wiki_page-techref-filesystems.md): using storage directory: /jffs
      - init -

## Adding Example

As another example we will add a message to failsafe, between the notice that we're in failsafe mode in the shell. You could use this, for example, to create a text menu system, or to launch a simple web server (with cgi scripts) to permit the user to do failsafe things.

We want to add the message, 'Remember, at this point there are no writable filesystems'

We create the file \`50_failsafe_remember_no_rw\`, in \`/lib/preinit\`

      remember_no_rw() {
          echo "Remember, at this point there are no writable filesystems"
      }

      boot_hook_add failsafe remember_no_rw

This creates the function \`remember_no_rw\` and adds it to the failsafe hook, in between \`10_indicate_failsafe\` and \`99_10_failsafe_login\` which define the other functions in the \`failsafe\` hook. This wasn't necessary for the previous example because the function was already in a hook.

The boot log for this, when entering failsafe, is:

      VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
      Freeing unused kernel memory: 132k freed
      Please be patient, while OpenWrt loads ...
      eth1: link forced UP - 100/full - flow control off/off
      - preinit -
      Press CTRL-C or Press f<ENTER> to enter failsafe mode
      f
      - failsafe -
      Remember, at this point there are no writable filesystems

      BusyBox v1.15.3 (2010-01-20 19:26:26 EST) built-in shell (ash)
      Enter 'help' for a list of built-in commands.

      ash: can't access tty; job control turned off

        _______                     ________        __
       |       |.-----.-----.-----.|  |  |  |.----.|  |_
       |   -   ||  _  |  -__|     ||  |  |  ||   _||   _|
       |_______||   __|_____|__|__||________||__|  |____|
                    |__| W I R E L E S S   F R E E D O M

       KAMIKAZE (bleeding edge, r19235) ------------------
        * 10 oz Vodka       Shake well with ice and strain
        * 10 oz Triple sec  mixture into 10 shot glasses.
        * 10 oz lime juice  Salute!
       ---------------------------------------------------

# Architecture-specific notes

Some architectures have additional files and functions (or overrides of the above functions) in order to accommodate specific needs of that hardware. In that case the files are located in the source tree under `$ROOTDIR/target/linux/<architecture[/subarch]/base-files/lib/preinit`. During build they are merged and appear under `/lib/preinit` along with the rest.
