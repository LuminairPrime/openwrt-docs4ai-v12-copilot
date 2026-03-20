---
title: Boot/Init Requirements
module: wiki
origin_type: wiki_page
token_count: 1562
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-requirements-boot-process.md
last_pipeline_run: '2026-03-20T01:28:00.439321+00:00'
language: text
ai_summary: The Boot/Init Requirements document outlines the necessary functions and goals for initscripts in the new OpenWrt init system. It describes the boot process, which includes the kernel bootstrap, preinit, and init stages, emphasizing the importance of preinit in preparing the system for the init stage. Key goals include minimizing preinit functionality, ensuring failsafe access, and supporting configurable root filesystem mounts. The document also highlights the need for compatibility with /opt deployments and the proper handling of file descriptors during the transition to the target root filesystem.
ai_when_to_use: This document is useful for developers working on the OpenWrt boot process, particularly those involved in creating or modifying initscripts for system initialization. It provides guidance on managing race conditions and maintaining system functionality during boot.
ai_related_topics:
- procd
---
# Boot/Init Requirements

|                                                                   |                                                                                                                           |
|-------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| ![48px-dialog-warning.svg.png](/meta/48px-dialog-warning.svg.png) | This is not a reference document, it's an old design document that, at least in part, led to [procd](/docs/techref/procd) |

# Boot/Init Requirements

This article attempts to state what the initscripts must and should do for the new init system being developed for OpenWrt. The goal is to deal with the race conditions that currently can occur, without losing current functionality.

## Boot/Preinit

The Boot process currently consists of the kernel bootstrap (not discussed here), preinit, and init. Preinit takes care of things that init can't function without, while init is responsible for starting up the rest of the system.

On a Debian desktop system there is an analogue to preinit, which uses initramfs to bring up the system enough to the point init can operate. Unfortunately initramfs is not an option on openwrt because it wastes too much space. The binaries and scripts in an initramfs cannot be retained for use in the booted system, unless they are copied to RAM (tmpfs) (if anyone know otherwise and can point out how, please contact the devs), which is why preinit exists.

Preinit looks to linux like the final boot stage to init on the rootfs. Preinit then mounts the root file system, does `pivot_root` to the rootfs, and then use the real init to replace itself. Basically it transforms intself into the 'real' init and rootfs.

### Goals

- Reduce preinit as much as possible so that init does most of the work
- Maintain failsafe ability, so that if mounting, etc, rootfs fails, or init makes system inaccessible, that there is a way to get into the device and fix it.
- Not start hotplug at all in preinit ... for that matter no processes except the real init should cross the preinit/init boundary.
- Be configurable...it should be possible to configure rootfs mount, init start and anything else that can happen after the jffs2 is mounted (and therefore a writable config is available)
- LED and network message functionality should be available to switchinit (which runs a script to shutdown process and make some other process than the current init PID 1, e.g. for doing a safer sysupgrade, and firstboot ('factory reset'))
- Support /opt type deployments as well as extroot (that is, extra packages on /opt rather than by replacing the jffs2 rootfs)
- No open file descriptors/references on the old rootfs when init is executed on the target rootfs (this is why we don't just mount/pivot in init).

#### Notes

- JFFS2 Formatting must be done on a fully booted system, because on some routers (like the Fon with NOR flash), formatting takes a significant amount of time during which the router would be unavailable for use). That means preinit can't be where the formatting happens.
- Ideally the firstboot script will take the router back to state exactly like after flashing without configuration saved), including the needs for formatting jffs2
- Restoring the configuration needs to be done after the rootfs is mounted, but before most configuration is used (most configuration is used in init or init-launched hotplug).
- Saving the configuration should save the jffs2 (for squashfs)/or boot rootfs config not the config on external root. This is because the external root will still be available on the external storage after flashing, but the internal (jff2 or other boot rootfs) won't.

### Must-do's

1.  Allow failsafe
2.  If initramfs, do initramfs, skip rest of this list
3.  For Squashfs: Mount jffs2 (if already formatted)
4.  For External Block: Mount swap (so fsck has enough memory)[^1] if present
5.  For External Block: Mount rootfs (checking first if fsck available) or tmpfs (if no rootfs yet)
6.  For External Block: Mount marked fses before init (e.g. for deployments where /opt contains packages/script that need to run early in init)
7.  Start init or kexec

### 0) Before failsafe

- Enable script output to serial before failsafe
- emit UDP messages with progress of boot, or at the very least failsafe prompt
- Network or Serial access
  - network kernel modules
- LEDs indicator for hit button
  - kernel modules for gpio and gpio-leds
- Button (on any button during failsafe window, enter failsafe)
  - kernel module for gpio, gpio-buttons or keys-polled, and button-hotplug
- Setting LEDs requires sysfs (/sys)
- OpenWrt LEDs depend on specific hardware as defined by /proc/cpuinfo, so /proc is needed
- Obviously /dev is needed

### 1) Allow Failsafe

- LED indicator for failsafe mode

#### Configuration at Compile-time not Run-time

- failsafe-related items \*must not\* rely on changing config, only on what is available in the flashed image.

### 2) Mount swap and 3) Mount rootfs

- check if jffs2 formatted
- if formatted, mount it in a temporary location
- combine boot rootfs and jffs2 (if present) kernel modules and swap/rootfs config
- mount should have /proc
- requires /dev

#### 2) Mount swap

- load modules needed for swap (if swap configured) (from rootfs or jffs2)
- run any swap-related scripts from either boot rootfs or jffs2
- using swap-utils from either boot rootfs or jffs2 (if present) do swapon for configured swap
- needs swap-utils and blkid (for UUID based config) on bootfs or jffs2

#### 3) Mount rootfs

- load modules needed for rootfs (from rootfs or jffs2)
- run any rootfs-related scripts (e.g. for mmc) (e.g. mount usbfs)
- check filesystem for errors if fsck present on boot rootfs or jffs2 (depends on blkid)
- mount target rootfs (depends on blkid on boot rootfs or jffs2)
- pivot_root
- move any fs mounted on old root to new root

### 4) Mount marked fses other rootfs

- load modules needed by fses (if not previously loaded)
- run any associated scripts (.e.g for mmc/usbfs) (if not previously run)
- check filesystem for errors if fsck present on rootfs (depends on blkid)
- mount fs (depends on blkid)

### 5) Start Init or Kexec

- For Init: Configurable PATH and environment variables
- Either do init or kexec a kernel on the rootfs or other previously mounted storage

## Init

### Goals

- Split /etc/init.d into independent chunks

### Wants

- Support betwork rootfs, perhaps by using switchinit with network kept up

[^1]: Roughly 1 MB of RAM for every 1 GB of disk to successfully fsck the disk. [Source](http://www.openbsd.org/faq/faq14.html#LargeDrive).
