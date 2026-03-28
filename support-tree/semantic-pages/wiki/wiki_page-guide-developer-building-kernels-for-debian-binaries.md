---
title: Building OpenWrt Kernel for Debian System
module: wiki
origin_type: wiki_page
token_count: 540
source_file: L1-raw/wiki/wiki_page-guide-developer-building-kernels-for-debian-binaries.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_url: https://openwrt.org/docs/guide-developer/building_kernels_for_debian_binaries
language: text
ai_summary: This document provides guidance on building OpenWrt kernels for use with the Debian operating system, highlighting key compatibility issues and configuration settings. It discusses the implications of using soft-FPU instructions in OpenWrt versus hard FPU instructions in Debian, and how to enable FPU emulation in the kernel. Additionally, it covers the requirements for udev and SELinux support, as well as the potential discrepancies in kernel configuration options. Finally, it suggests enabling IKConfig to save the kernel configuration within the kernel itself for easier reference.
ai_when_to_use: Use this guide when you need to compile an OpenWrt kernel that is compatible with Debian, especially when addressing issues related to FPU instructions, udev, and SELinux support.
ai_related_topics:
- CONFIG_MIPS_FPU_EMULATOR
- CONFIG_DEVTMPFS
- CONFIG_KERNEL_DEVTMPFS
- CONFIG_IKCONFIG
- CONFIG_IKCONFIG_PROC
---
# Building OpenWrt Kernel for Debian System

For now this page serves to keep some notes about using OpenWrt kernels with Debian distribution.

## Floating Point Unit (MIPS)

If you boot OpenWrt kernel and expects it to start init but you see a kernel panic:

`Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000004`

OpenWrt userland packages are compiled with soft-FPU instructions by default. (The floating point math is emulated by the compiler during compile time.)

Debian binaries (jessie) are compiled with hard FPU instructions. As most embedded devices do not have FPUs, it's usually necessary for the kernel to emulate them in order for these instructions to be executed correctly. Since OpenWrt makes use of soft-FPU, the FPU emulation is turned off in the kernel by default. Inability to execute FP instructions is a possible reason for the crash.

To compile the kernel with FPU emulation, in kernel configuration check that you set CONFIG_MIPS_FPU_EMULATOR=y. See [use-buildsystem#Kernel configuration (optional)](/docs/guide-developer/toolchain/use-buildsystem#Kernel configuration (optional)).

## udev

Debian uses udev to populate /dev. For udev to work, devtmpfs pseudo filesystem must be enabled. Check that CONFIG_DEVTMPFS=y in kernel_menuconfig and CONFIG_KERNEL_DEVTMPFS=y in menuconfig.

## SELinux

Debian bins (e.g. init) are compiled with SELinux support. Init will try to initialise SELinux when starting. Since SELinux is not enabled in OpenWrt kernel, init might display a failure:

`Mount failed for selinuxfs on /sys/fs/selinux: No such file or directory`

This message is safe to ignore. Basically selinux initialisation attempts to mount the selinux filesystem but fails. Init ignores this failure and carries on booting as long as you do not provide enforcing=1 in kernel cmdline.

## IKConfig

The OpenWrt system messes with the kernel .config so you might not end up with the same options you set when you run kernel_menuconfig. If you want to know the final kernel options, look in your build_dir (e.g. build_dir/target-mips_34kc_glibc-2.19/linux-ar71xx_mikrotik/linux-3.18.23/.config). Alternatively if you can afford a bigger kernel, set CONFIG_IKCONFIG=y and CONFIG_IKCONFIG_PROC=y in kernel_menuconfig so that the kernel .config is saved in the kernel itself.
