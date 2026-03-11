---
title: Internal Layout D-Link DIR-825
module: wiki
origin_type: wiki_page
token_count: 732
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-internal-layout.md
last_pipeline_run: '2026-03-11T14:46:50.602050+00:00'
language: text
---
# Internal Layout D-Link DIR-825

This article describes the internal layout and configuration of the [D-Link DIR-825](/toh/d-link/dir-825). This particular hardware has two physical network interfaces, `eth0` and `eth1`, whereas most emebedded devices have only one: `eth0`. It also has two two wireless network interfaces using the IEEE 802.11 protocol, represented by `wlan0` and `wlan1`.

![dir-825_hardware_diagram2.gif](/media/dlink/dir-825/dir-825_hardware_diagram2.gif)

| iface | Port                                                     |
|-------|----------------------------------------------------------|
| eth0  | internal interface connected to Gigabit Switch (default) |
| eth1  | internal interface connected to WAN port (default)       |
| wlan0 | radio0                                                   |
| wlan1 | radio1                                                   |
| usb   | Bluetooth/3G/etc.                                        |

Additional information on the rtl8366s switch. Switch 1: rtl8366s(RTL8366S), ports: 6 (cpu @ 5), vlans: 16 (4096 starting with 10.03.1-rc4)

| switch port id | Label on the back |
|:---------------|:------------------|
| port:0         | LAN4              |
| port:1         | LAN3              |
| port:2         | LAN2              |
| port:3         | LAN1              |
| port:4         | WAN               |
| port:5         | internal          |

The default config provided looks something like below:

    config interface loopback
            option ifname   lo
            option proto    static
            option ipaddr   127.0.0.1
            option netmask  255.0.0.0

    config interface lan
            option ifname   eth0
            option type     bridge
            option proto    static
            option ipaddr   192.168.1.1
            option netmask  255.255.255.0

    config interface wan
            option ifname   eth1
            option proto    dhcp

    config switch rtl8366s
            option enable   1
            option reset    1
            option enable_vlan 1

    config switch_vlan
            option device   rtl8366s
            option vlan     0
            option ports    "0 1 2 3 5"

Going through the configuration, step by step, provides the following information.

- First there's the loopback interface `lo`.
- Second, in this configuration, `eth0` is part of the bridged interface `lan`.
- Third, `eth1` is configured as the `wan` interface.
- Fourth, is the switch configuration.
- The 'config switch rtl8366s' options enable the switch, reset it and enable VLAN capability.
- The 'config switch_vlan' options enable VLAN0 and assigns it to the 4 external LAN ports and internal `eth0` interface.

**Note:** The `eth1` network interface is assigned to VLAN1 by default, which in turn is assigned to switch port 4 by default. Further, `eth1` is also configured to be part of the virtual interface `wan`. Configuring `wan` with a static ip address will provide another avenue to access the router using SSH. Finally, either of the wireless interfaces can be configured to enable wifi access as well.
