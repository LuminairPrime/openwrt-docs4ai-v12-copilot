---
title: '21.02: Major cosmetic changes'
module: wiki
origin_type: wiki_page
token_count: 2106
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-20-xx-major-changes.md
last_pipeline_run: '2026-03-12T22:39:22.932543+00:00'
language: text
ai_summary: The 21.02 release of OpenWrt introduces significant cosmetic changes, particularly in the naming conventions for devices and targets. This update aims to standardize device/image names using a vendor_model-variant scheme, enhancing consistency across various components such as Makefiles and DTS files. Key changes include the renaming of targets like ar71xx to ath79 and the systematic application of compatible names for board identification. Developers must adapt their scripts and configurations to reflect these new naming conventions to ensure compatibility with the updated system.
ai_when_to_use: This module is essential for developers maintaining or adapting OpenWrt builds, especially those transitioning from older versions like 19.07 to 21.02. It is particularly relevant when updating device configurations and scripts to align with the new naming standards.
ai_related_topics:
- DEVICE_TITLE
- SUPPORTED_DEVICES
- CONFIG_TARGET_DEVICE_*
- TARGET_*
---
# 21.02: Major cosmetic changes

This page intends to give an overview over major cosmetic changes since 19.07, focusing on those that will require adjustments/adaption downstream.

The idea is to give a broad overview like a Table of Contents, without too much details on the specific issues.

Note that this page is not even close to being complete.

## Device/target renames

Recently, most obvious through the transition from ar71xx to ath79, we tried to make device/image names more systematic by applying a vendor_model-variant scheme.

This has already been used in 19.07 in some cases (ath79, ipq40xx, ipq806x, mpc85xx, new ramips devices, ...).

After 19.07 had been released, the attempt was made to apply this more widely, and use the momentum to also achieve a more unified and systematic naming scheme for the different locations where the "device name" is used in its variations:

- device name in image/Makefile (will be used for image name)
- DEVICE_TITLE in image/Makefile
- DTS file name (soc_vendor_model or soc-vendor-model)
- DTS model name
- DTS compatible
- board_name (which should be derived from compatible instead of setting board names manually)
- SUPPORTED_DEVICES

The following subchapters will provide details on which changes have been applied to which targets so far.

### arc770

Manual board names (/tmp/sysinfo/board_name) have been replaced by compatible (vendor,model-variant)

So, all local scripts using the board name need to be updated.

<https://github.com/openwrt/openwrt/commit/0a5d74fa68bce598302236ca0f3eb2db2bc1592d>

### archs38

Manual board names (/tmp/sysinfo/board_name) have been replaced by compatible (vendor,model-variant)

So, all local scripts using the board name need to be updated.

<https://github.com/openwrt/openwrt/commit/3c190ef112979793cd0e2148c53c6208a642a463>

### ath79/ar71xx

In 21.02, ar71xx will finally be dropped. As already relevant in 19.07, ath79 introduces vendor_model-variant scheme for image names. It also drops the board_names used in ar71xx, so the compatible (from DTS) will be used as board name instead (being equivalent to vendor,model-variant, and unique for a specific device). While creating the new and shiny target, we again took the opportunity to use more systematic names on devices, using less abbreviations and staying closer to the device name. This will it result in several changed names compared to ar71xx additional to just adding the vendor to the name.

For downstream, (at least) the following will require adjustment:

- CONFIG_TARGET_DEVICE\_\* variables
- image names (e.g. if copied)
- board names (/tmp/sysinfo/board_name) if used for anything on device

Note that ath79 might also include several changes after 19.07.

### bcm27xx/brcm2708

The whole target has been renamed from "brcm2708" to "bcm27xx". This will affect all cases where target variables are used, i.e. CONFIG_TARGET\_\* or TARGET\_\* dependencies. Despite, image names will change. The same rename applies to packages brcm2708-userland and brcm2708-gpu-fw.

This can be easily addressed downstream by just grepping for "brcm2708".

### bcm47xx/brcm47xx

The whole target has been renamed from "brcm47xx" to "bcm47xx". This will affect all cases where target variables are used, i.e. CONFIG_TARGET\_\* or TARGET\_\* dependencies. Despite, image names will change.

This can be easily addressed downstream by just grepping for "brcm47xx".

### bcm63xx/brcm63xx

The whole target has been renamed from "brcm63xx" to "bcm63xx". This will affect all cases where target variables are used, i.e. CONFIG_TARGET\_\* or TARGET\_\* dependencies. Despite, image names will change.

This can be easily addressed downstream by just grepping for "brcm63xx".

Despite, this target has also been subject to an ath79-like unification of device names:

- device/image names and compatible have been adjusted to match device names (using vendor_model-variant scheme)
- DTS files have been renamed with soc-vendor-model scheme
- manual board names (/tmp/sysinfo/board_name) have been replaced by compatible (vendor,model-variant)

Patches:

- <https://github.com/openwrt/openwrt/commit/e4ba8c82947efd39b014496de32ee73e1bec9c71>
- <https://github.com/openwrt/openwrt/commit/0a3350d908ec466206f58b9e6b300c49e4fb3b13>
- <https://github.com/openwrt/openwrt/commit/d0e8e6db6b22b893da2f3a2cbe84adb753cb3303>

### imx6

Manual board names (/tmp/sysinfo/board_name) have been replaced by compatible (vendor,model-variant)

So, all local scripts using the board name need to be updated.

<https://github.com/openwrt/openwrt/commit/8126e572dd4f531c5f105b7197bc119b2b1ebb07>

### layerscape

Device nodes and thus image names have been changed to apply to vendor_model scheme.

This will affect CONFIG_TARGET_DEVICE\_\* variables and image names.

<https://github.com/openwrt/openwrt/commit/0f3c3a5fb2738b25c62eb0ff8ef7d0654c0b9300>

### mediatek

Device nodes and thus image names have been changed to apply to vendor_model scheme.

This will affect CONFIG_TARGET_DEVICE\_\* variables and image names.

<https://github.com/openwrt/openwrt/commit/49d66e0468c14d8a05bd6c33056708d2051437cb>

### mpc85xx

Device nodes and thus image names have been changed to apply to vendor_model scheme.

This will affect CONFIG_TARGET_DEVICE\_\* variables and image names.

<https://github.com/openwrt/openwrt/commit/118749271b311413307f0b6be91786d7ac368f8b>

### octeon

Device nodes and thus image names have been changed to apply to vendor_model scheme.

This will affect CONFIG_TARGET_DEVICE\_\* variables and image names.

<https://github.com/openwrt/openwrt/commit/1e3bfbafd37ccb32d0ed6618f4886e1dec6643d2>

### ramips

In ramips, the situation in 19.07 can be described as a mix of ar71xx and ath79. After 19.07, the target was updated and the same naming logic as for ath79 was applied. Thus, for this target effectively the same comments as for ath79/ar71xx apply.

### samsung

Device nodes and thus image names have been changed to apply to vendor_model scheme.

This will affect CONFIG_TARGET_DEVICE\_\* variables and image names.

<https://github.com/openwrt/openwrt/commit/6e70e4a071b233da83486414e65d15756ede63d2>

### sunxi

Device nodes and thus image names have been changed to apply to vendor_model scheme.

This will affect CONFIG_TARGET_DEVICE\_\* variables and image names.

<https://github.com/openwrt/openwrt/commit/a4cdb537b17ede9785ddbaef5ed9d69f3ab89052>

## DEVICE_TITLE split and tidy-up

To make device names more systematic, the DEVICE_TITLE make variable (primarily used for display in make menuconfig) was split into DEVICE_VENDOR, DEVICE_MODEL and DEVICE_VARIANT *for all targets.* DEVICE_TITLE is still available as (simplified)

    DEVICE_TITLE := $(DEVICE_VENDOR) $(DEVICE_MODEL) $(DEVICE_VARIANT)

During this update process, we took the opportunity to make names more systematic. Thus, several DEVICE_TITLEs will have changed effectively.

Despite, a new syntax to specify alternate device names has been introduced (ALT0 to ALT3):

    DEVICE_ALT0_VENDOR
    DEVICE_ALT0_MODEL
    DEVICE_ALT0_VARIANT

As for DEVICE_TITLE, those will not affect image names.

## Label MAC address

Many devices supported by OpenWrt bear one or many MAC addresses on them, which allow to identify those devices in large network. This fact has been exploited by downstream communities, which implemented those addresses locally. OpenWrt has now added a mechanism to store and retrieve those addresses:

Developer reference: <https://openwrt.org/docs/guide-developer/mac.address#label_mac_address>

Use:

    . /lib/functions/system.sh
    label_mac_addr=$(get_mac_label)

The label MAC address has to be provided in OpenWrt on a per-device basis. While a lot of devices has already been covered, there also is still a lot of devices to take care of.

## Support of Ed25519 SSH keys

With the commit [d0f295837a03f7f52000ae6d395827bdde7996a4](commit>d0f295837a03f7f52000ae6d395827bdde7996a4) it is now possible to use Ed25519 SSH keys on regular (aka not tiny) devices. These keys are much shorter than RSA keys while being equally secure. For embedded devices this should speed up the login process as the keys are much faster processed.
