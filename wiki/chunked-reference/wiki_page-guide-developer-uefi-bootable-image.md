---
title: OpenWrt on UEFI based x86 systems
module: wiki
origin_type: wiki_page
token_count: 842
source_file: L1-raw/wiki/wiki_page-guide-developer-uefi-bootable-image.md
last_pipeline_run: '2026-03-29T23:50:02.157846+00:00'
source_url: https://openwrt.org/docs/guide-developer/uefi-bootable-image
language: text
ai_summary: The OpenWrt module for UEFI based x86 systems provides guidance on generating UEFI bootable images for x86-64 architecture. It outlines the necessary steps to build these images using the OpenWrt build system, including configuring the menu options and running the build command. Additionally, it covers the process for creating UEFI secure boot images, detailing the required tools and commands to sign EFI binaries. The module also references a development repository for secure boot capabilities and provides instructions for importing signing certificates.
ai_when_to_use: Use this module when you need to create UEFI bootable images for x86-64 systems in OpenWrt, especially when targeting modern hardware that requires UEFI support.
ai_related_topics:
- make menuconfig
- Build GRUB EFI images (Linux x86 or x86_64 host only)
- Sign EFI executable binaries
- efitools
- efibootmgr
- efivar
- sbsigntool
---

> **Source:** [https://openwrt.org/docs/guide-developer/uefi-bootable-image](https://openwrt.org/docs/guide-developer/uefi-bootable-image)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-29

# OpenWrt on UEFI based x86 systems

## Introduction

UEFI boot has been required for years now, boards that only support UEFI are common, and Intel has stated back in 2017 that "legacy" BIOS will no longer be supported after 2020.[^1][^2]

To accommodate this, the OpenWrt build system generates UEFI bootable images.

## Status

As of OpenWrt `a6b7c3e672764858fd294998406ae791f5964b4a`, EFI-compatible images are available on the x86-64 [snapshots](https://downloads.openwrt.org/snapshots/targets/x86/64/) downloads page.

## Building UEFI bootable OpenWrt image

To build an EFI-compatible OpenWrt image:

      * Run ''make menuconfig''.

      * Go to **Target Images** and make sure that the option **Build GRUB EFI images (Linux x86 or x86_64 host only)** is checked.

Select additional packages as necessary and finally save changes and exit menuconfig.

Run `make` as usual to build the image.

The resulting image(s) will be available in `./bin/targets/x86/64/` (depending on the image format(s) you chose), which can be written to disk after decompression.

Note that these are **disk images**, not partition images, which must be written to a block device directly e.g. `/dev/sdb`.

## UEFI Secure Boot

To generate signed image for use with secure boot, there is a [development repository](https://github.com/alive4ever/openwrt) with corresponding [packages feed](https://github.com/alive4ever/packages) under `feature-uefi-secure-boot` branch.

The repository contains changes based on Jow-staging branch to generate secure boot capable image

The related packages feed repository contains stuffs needed to sign efi binaries, i.e. gnu-efi and sbsigntool and stuffs to manipulate efi variables, i.e. efivar, efibootmgr, and efitools.

``` bash
# Add the development git repository
$ git remote add devrepo https://github.com/alive4ever/openwrt
$ git fetch devrepo
$ git checkout feature-uefi-secure-boot

# Configure the corresponding package repository
$ echo 'src-git packages https://github.com/alive4ever/packages;feature-uefi-secure-boot' > ./feeds.conf
$ ./scripts/feeds clean
$ ./scripts/feeds update packages
$ ./scripts/feeds update -i
$ ./scripts/feeds install -a

# Now, configure the build system
# Select x86 as Target, x86_64 as Subtarget
# make sure to select 'Sign EFI executable binaries' under 'Target Images'
# UEFI related tools are available under Utilities section,
# which consist of efitools, efibootmgr, efivar, and sbsigntool
$ make menuconfig

# The certificate and key need to be generated
# to perform uefi binary signing
$ OLD_UMASK=$(umask)
$ umask 077
$ openssl req -new -x509 -sha256 \
  -days 90 -out ./db.crt \
  -subj '/CN=secure boot signing certificate' \
  -newkey rsa:2048 -nodes \
  -keyout ./db.key
$ umask $OLD_UMASK

# run make to generate UEFI secure bootable OpenWrt image
$ make

```

Remember to import `db.crt` (which may needs to be converted into DER or other format) into `db` UEFI variable to securely boot the resulting image.

[^1]: <https://www.anandtech.com/show/12068/intel-to-remove-bios-support-from-uefi-by-2020>

[^2]: <http://www.uefi.org/sites/default/files/resources/Brian_Richardson_Intel_Final.pdf>
