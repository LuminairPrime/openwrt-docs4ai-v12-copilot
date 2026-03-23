---
title: Device support policies / best practices
module: wiki
origin_type: wiki_page
token_count: 2003
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-device-support-policies.md
last_pipeline_run: '2026-03-23T22:14:22.429226+00:00'
language: text
---
# Device support policies / best practices

Check this one beforehand: [Submitting patches](/submitting-patches)

This page provides additional guidelines for adding device support.

These guidelines are no rules, but may help you to improve the experience for both yourself and the reviewers when you submit a device support patch. Beyond that, they may just describe recommended and/or frequently applied practice throughout OpenWrt.

What's actually *required* will depend on who is reviewing your submission, though.

## Commit message

General guidelines for how to write a good commit message are found in [Submitting patches](/submitting-patches)

For device support commits, the commit message needs to contain at least the Specifications and Flashing instructions section.

Beyond that, it is recommended to add an overview of the MAC address assignment that you evaluated (see MAC address section below for further details).

Additional information is always helpful: While you shouldn't tell every detail of your struggle to support the device, it is generally a good idea to provide information that might help other developers in the future to understand why you did things as you did them.

## DTS files

### License

Please add a license via SPDX identifier to every file: <https://spdx.org/licenses/>

A very abundant license for DTS(I) files is:

    // SPDX-License-Identifier: GPL-2.0-or-later OR MIT

Please don't add a full-text license, but choose the appropriate identifier for it.

### dts-v1

The `/dts-v1/;` identifier must only be defined once and needs to be before any other content (except the license).

For several targets, it's already defined in the parent/SoC-based DTSI file, and does not need to be included a second time then.

### Model/device name

**Naming of the device should be consistent.** Many targets enforce that programmatically anyway, but if that's not the case please be consistent in your naming anyway.

If your model property contains a "v1", then your compatible should as well. Try to avoid abbreviations, these might cause confusion. The easiest way is to just create the compatible from the model by converting everything to lower case and replacing every space by a hyphen:

        model = "TP-Link TL-WR841N v14";
        compatible = "tplink,tl-wr841n-v14", "mediatek,mt7628an-soc";

An exception should be made for the vendor part of the compatible, where the kernel provides a list of strings to be used: <https://www.kernel.org/doc/Documentation/devicetree/bindings/vendor-prefixes.txt>

### General style

Indent style for DTS files is **tabs-only**.

To enhance readability, it is recommended to separate all blocks by empty lines. Despite, it may be helpful to structure properties into groups separated by empty lines.

For the status property, a frequent practice is to put it as a node's first line and add an empty line afterwards.

### LEDs

Typically, LEDs should have a label property following the `color:function` scheme.

The node name should be chosen in order to match the `function` from the label, i.e. if `green:wlan` is used, the node name should be `wlan` as well, and not `wifi`. If there is more than one LED with the same use, the color should be added to the node name, typically *after* the function in this case (`wlan_green`).

The *DT label* (not the label property) should be created from the node name by adding a `led_` prefix, because the DT label will be used in global context. Only add a DT label if you use it for something, otherwise just omit it.

Example:

    leds {
        compatible = "gpio-leds";

        lan {
            label = "green:lan";
            gpios = <&gpio 39 GPIO_ACTIVE_LOW>;
        };

        wan_green {
            label = "green:wan";
            gpios = <&gpio 40 GPIO_ACTIVE_LOW>;
        };

        wan_amber {
            label = "amber:wan";
            gpios = <&gpio 41 GPIO_ACTIVE_LOW>;
        };

        led_system: system {
            label = "green:system";
            gpios = <&gpio 42 GPIO_ACTIVE_LOW>;
        };
    };

## base-files

The cases in base-files are sorted in two levels: Within each block the devices are sorted alphabetically, and all of the blocks are sorted alphabetically based on the first device.

Where possible, add your device to an existing block instead of creating a new one.

### No wildcards

Occationally, you might be tempted to use wildcards in a case like the following:

    vendor_model-v1|\
    vendor_model-v2)
        ...

While this technically could be replaced by `vendor_model-*` to make your code shorter, this is generally not a good idea, because:

- You never know whether a different model will come up later that will be different, but fall within your wildcard
- Wildcard will prevent effective searching: If you e.g. want to grep for all settings applied to `vendor_model-v1`, grepping won't work because it won't match the wildcard definition. However, you cannot possibly guess the wildcard used in many cases.

## MAC addresses

In general, it is safest to define MAC addresses the same way as the vendor does it on it's device. Don't invent your own MAC address assignment scheme.

This may produce overlapping MAC addresses e.g. for LAN and one WiFi interface for several vendors, but that's still better than having overlapping MAC addresses with another device when using OpenWrt in a network afterwards (consecutive addresses in real world networks do happen).

Further reading on MAC address setup is found here: [Device support: MAC address setup](/docs/guide-developer/mac.address)

### Documentation

It will be helpful to other people if you document your MAC address assignment (flash locations and adresses or address increments) in the commit message. An easy and helpful way can be a simple table:

Example 1:

    MAC addresses as verified by OEM firmware:

    use   address   source
    LAN   *:f0      config 0x0 (label)
    WAN   *:f1      config 0x6
    2g    *:f0      art 0x1002
    5g    *:ef      art 0x5006

Example 2:

    MAC addresses as verified by OEM firmware:

    vendor   OpenWrt   address
    LAN      eth0      label
    WAN      eth1      label + 1
    2g       phy0      label + 2
    5g       phy1      label + 3

    The label MAC address was found in u-boot 0x1fc00.

### Data source

When defining MAC addresses in board.d and hotplug.d files, calculate them based on the flash locations and *not* relative to other interfaces. The numbering of interfaces may change, and then the address would be calculated incorrectly ...

For example

    wan_mac=$(macaddr_add $(mtd_get_mac_binary u-boot 0x1fc00) 1)

will always yield the same address while

    wan_mac=$(macaddr_add $(cat /sys/class/net/eth0/address) 1)

might be wrong if eth0/eth1 are swapped.

So, effectively, don't chain assignments, but read from the upmost data source where possible.

Try to always use hex locations (0x0 instead of 0) and lower-case characters for consistency.

## Backports

Generally, there is no hard rule or formal consensus about what is allowed to be backported from master into a stable.

However, the concept of a stable branch implies that backports will typically be *fixes, not features*. Adding support to a new device obviously is considered a feature in that context.

While feature backports still should be an exception, they typically are done for changes that are easy and well isolated. In contrast, requiring new drivers or patches to kernel subsystems etc. will drive your chances close to zero.

### Device support backports

Reviewing device support backports requires a detailed knowledge not only of the target setup in general, but also of all the changes applied to it until the last branch was made. Depending on the age of the stable branch and the number of changes to the target in the meantime, reviewing a backport will range from trivial to more work than reviewing the actual initial support.

In a project where reviewing time is scarce, doing backport reviews will obviously draw away time from other features that may be merged into master.

**Thus, device support *typically* is not backported.**

Exceptions have been made in the past for the following reasons. This is an observation, it will not constitute any claim:

1.  Device support is trivial, e.g. for a 100 % clone of a device already existing in stable.
2.  There are two similar devices that may be confused, and only one is present in stable branch. Backporting may prevent some users from destroying their devices.
3.  A device backport has been created by one of the committers: If the work has been done already, there is no reason to not share it with others. (Note that this is *not* the same as reviewing a patch provided by somebody else, as the committer will have to invest time for reviewing that one.)

Of course, despite everything said in this paragraph, every committer is free to choose whatever (s)he may find suitable. The lines above are just a description of what will probably happen.
