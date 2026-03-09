---
title: 'Device Support: MAC address setup'
module: wiki
origin_type: wiki_page
token_count: 2057
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-mac-address.md
last_pipeline_run: '2026-03-09T18:30:57.384548+00:00'
language: text
---
# Device Support: MAC address setup

## Retrieve addresses from stock firmware

The first step is to find out which addresses are present in stock configuration. The procedure depends on your level of access to the device's firmware.

The result would be a list like the following:

    LAN ..:..:..:..:..:0a
    WAN ..:..:..:..:..:0b
    2.4 GHz ..:..:..:..:..:0c
    5 GHz ..:..:..:..:..:0a

## Find out about flash locations

If you already have OpenWrt running on the device, you can try to find out about MAC locations on flash (note that not all devices store addresses there).

List partitions:

    $ cat /proc/mtd
    dev:    size   erasesize  name
    mtd0: 00020000 00010000 "u-boot"
    mtd1: 00189ce4 00010000 "kernel"
    mtd2: 0064631c 00010000 "rootfs"
    mtd3: 003b0000 00010000 "rootfs_data"
    mtd4: 00010000 00010000 "art"
    mtd5: 007d0000 00010000 "firmware"

You would normally expect WiFi MAC addresses in the art partition. To check for that, use hexdump on the corresponding mtd4:

    $ hexdump -C /dev/mtd4

This will dump the whole partition to your console. Now you can look for addresses there: Take one byte of the vendor part of the address (first three bytes) and do text search ...

The same should be done for other partitions. Usual suspects are:

- factory
- mac
- config
- art
- u-boot

If you are successful, you will have a list of addresses and locations, e.g.

    factory 0xe000 *:0A
    factory 0xe006 *:0B
    art 0x4 *:0A

You can check your data by using OpenWrt's get_mac_binary command (based on mtdX):

    . /lib/functions/system.sh
    get_mac_binary /dev/mtd4 0x4

or by using mtd_get_mac_binary (based on partition label):

    . /lib/functions/system.sh
    mtd_get_mac_binary art 0x4

## Merge your data

Now, combine data from stock firmware and your research to have a complete list:

    LAN *:0a factory 0xe000
    WAN *:0b factory 0xe006
    5 GHz *:0a art 0x4
    2.4 Ghz *:0c calculated from art 0x4 + 2

You could also include this list in your commit message to preserve the information.

As in the example, it is possible that the same address is present in different locations. In this case, use the location that "belongs" to the interface, i.e. art for WiFi, others for ethernet.

## Set MAC addresses

TBD: mtd_mac_address, 02_network, ...

### MAC address pulled by driver

In several cases, the MAC address is already provided at the correct location for the driver to use it automatically.

*(This list is incomplete. Please extend it.)*

Known cases:

- ath79: **mtd-cal-data**: The MAC address will be read from start +2
- ramips: **mediatek,mtd-eeprom/ralink,mtd-eeprom**: The MAC address will be read from start +4
- **ath9k**: offset + 2 (mostly)
- **ath10k**: offset + 6

So, if you have MAC location matching those, you do not have to specify the MAC address in DTS or base-files for the particular interface.

Correct:

    &wmac {
        status = "okay";

        mtd-cal-data = <&art 0x1000>;
    };

Suboptimal (not precisely wrong):

    &wmac {
        status = "okay";

        mtd-cal-data = <&art 0x1000>;
        mtd-mac-address = <&art 0x1002>;
    };

This can also be exploited for setting the label MAC address (see below) via 02_network.

## Label MAC address

refs: <https://github.com/openwrt/openwrt/pull/2159> <https://github.com/openwrt/openwrt/pull/2253>

Many devices bear a label with one or several MAC addresses on it. Those may be used to identify the device in the network and thus represent a valuable additional information about the device.

When adding device support, you should also check which of the interface addresses corresponds to address on the label. If we assume the label MAC address ends with `0a`, we could assign either LAN or 5 GHz to it. The choice for an ambiguous address is arbitrary, so let's choose 5 GHz.

There are two options to specify the label MAC address in OpenWrt:

### label-mac-device DTS file

We can refer to the device bearing the label MAC address in DTS. For that purpose, one needs to reference the node with an alias, e.g.

    aliases {
        label-mac-device = &wifi0;
    }

Obviously, this is only valid if the 5 GHz Wifi device tree node actually has been named wifi0.

*Attention: Not all interface can be referenced this way. To check whether there actually is a usable MAC address, check the device tree on your router:*

Run

    find /proc/device-tree/ -name "*mac-address"

on your device.

*Attention: This will only work if you have already set up MAC addresses correctly based on the information retrieved above.*

It will give you a list like the following:

    /proc/device-tree/ahb/eth@1a000000/mac-address
    /proc/device-tree/ahb/eth@1a000000/mtd-mac-address
    /proc/device-tree/ahb/eth@19000000/mac-address
    /proc/device-tree/ahb/eth@19000000/mtd-mac-address
    /proc/device-tree/ahb/apb/wmac@18100000/mac-address
    /proc/device-tree/ahb/apb/wmac@18100000/mtd-mac-address

For each of the returned paths (if there are any), retrieve the mac-address, e.g.

    . /lib/functions/system.sh
    get_mac_binary "/proc/device-tree/ahb/eth@1a000000/mac-address" 0

Valid choices are only `mac-address` or `local-mac-address`. There may be one, two or no paths giving the correct address.

If you find the label MAC address here, check your DTS for the corresponding parent node. The correct node for `/proc/device-tree/ahb/apb/wmac@18100000/mac-address` would be `/ahb/apb/wmac@18100000`. Use this node's alias or add a reasonable one yourself if missing.

*Attention: Note that label MAC addresses are assigned relatively randomly by vendors, so label-mac-device should be regularly put into DTS files or DTSIs with few users, so it is not inherited by accident.*

### Set label MAC address via 02_network

If device tree does not lead to the relevant MAC address, we can still set it in 02_network. In this case, you need to set label_mac in a similar way as it is already used for lan_mac and wan_mac, e.g.

    cudy,wr1000)
        wan_mac=$(mtd_get_mac_binary factory 0x2e)
        label_mac=$(mtd_get_mac_binary factory 0x4) # e.g. on ramips when caldata is read from factory 0x0

    belkin,f9k1109v1)
        wan_mac=$(mtd_get_mac_ascii uboot-env HW_WAN_MAC)
        lan_mac=$(mtd_get_mac_ascii uboot-env HW_LAN_MAC)
        label_mac=$wan_mac

This is evaluated below by the line

    [ -n "$label_mac" ] && ucidef_set_label_macaddr $label_mac

If possible, setting the address with the DTS approach is preferred.

### Using the label MAC address

When everything is set up correctly, the label MAC address can be accessed with:

    . /lib/functions.sh
    . /lib/functions/system.sh
    label_mac_addr=$(get_mac_label)

## Common MAC address locations

If there is an ART partition, WiFi MAC addresses are frequently/typically stored there.

ath79:

- All TP-LINK routers using old tp-link header (those using Device/tplink-Xm or Device/tplink-Xmlzma templates defined in target/linux/ath79/image/common-tplink.mk), store only one mac address in \<&uboot 0x1fc00\>, which is the label mac address.

ramips: For ramips, typical locations for ethernet addresses are as follows:

- mt7621: lan mac is at factory 0xe000 and wan mac at factory 0xe006. This is the default location for mt7621 boards in MTK's SDK.
- For mt7620/mt76x8 boards if there's a lan mac at 0x28 there may be a wan mac at 0x2e. (There's only one GMAC for these two chips so GMAC2_OFFSET defined above isn't used.)

//Attention: Those are *typical* addresses. Some vendors mix them, invert them, or even use completely different locations!//