---
title: swconfig
module: wiki
origin_type: wiki_page
token_count: 3222
source_file: L1-raw/wiki/wiki_page-techref-swconfig.md
last_pipeline_run: '2026-03-27T07:16:36.403470+00:00'
source_url: https://openwrt.org/docs/techref/swconfig
language: text
ai_summary: The `swconfig` program is used for configuring Ethernet network switches in OpenWrt. It supports various hardware switches through specific drivers and allows users to view and manage switch configurations. Although `swconfig` is considered legacy, it remains functional for supported devices, enabling commands like `swconfig list` and `swconfig dev switch0 show` to display current settings. Users should transition to the DSA framework for new switch drivers to utilize standard tools like `ip` for configuration.
ai_when_to_use: Use `swconfig` when managing legacy Ethernet switches in OpenWrt that are compatible with its drivers. It is particularly useful for troubleshooting or configuring network settings on older hardware.
ai_related_topics:
- swconfig
- adm6996
- ar8216
- b53
- ip17xx
- psb6970
- rtl8306
- rtl8366s
- rtl8366rb
- rtl8367
- rtl8367b
---

> **Source:** [https://openwrt.org/docs/techref/swconfig](https://openwrt.org/docs/techref/swconfig)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-27

# swconfig

The program `swconfig` allows you to configure *configurable* [Ethernet network switches](/docs/techref/hardware/switch).

It is considered legacy and new switch drivers should use the DSA (distributed switch architecture) kernel framework which makes it possible to use standard userspace tools such as `ip` to configure the switches.

Make sure you can [safemode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) or TTL before changing network/switch settings

## Supported hardware

`swconfig` supports the following hardware switches using the mentioned `swconfig` driver;

| Driver                                                                                                    | Ethernet switches models                                                             | Hardware wiring   |
|-----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|-------------------|
| [adm6996](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/adm6996.c)     | Infineon/ADMTek 6996M/L/FC                                                           | MDIO / [GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md)       |
| [ar8216](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/ar8216.c)       | Qualcomm/Atheros AR8216/8236/8316/8327/8337                                          | MDIO              |
| [b53](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/b53)               | Broadcom BCM5325/5365/5395/5398/53115/53125/53128/53010/53011/53012/53018/53019/63xx | MDIO / SPI / MMIO |
| [ip17xx](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/ip17xx.c)       | IC+ IP178C IP175A/C/D                                                                | MDIO              |
| [psb6970](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/psb6970.c)     | Lantiq PSB6970                                                                       | MDIO              |
| [rtl8306](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8306.c)     | Realtek RTL8306S/SD/SDM                                                              | MDIO              |
| [rtl8366s](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8366s.c)   | Realtek RTL8366S                                                                     | MDIO [GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md)/SMI     |
| [rtl8366rb](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8366rb.c) | Realtek RTL8366RB                                                                    | MDIO [GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md)/SMI     |
| [rtl8367](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8367.c)     | Realtek RTL8367                                                                      | MDIO              |
| [rtl8367b](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8367b.c)   | Realtek RTL8367B                                                                     | MDIO              |

## Usage examples

## Show

- `swconfig list`
- `swconfig dev switch0 show`
- Show current configuration`swconfig dev rtl8366rb show
  `and you will obtain:`VLAN 1:
          info: VLAN 1: Ports: '12345t', members=003e, untag=001e, fid=0
          fid: 0
          ports: 1 2 3 4 5t
  VLAN 2:
          info: VLAN 2: Ports: '05t', members=0021, untag=0001, fid=0
          fid: 0
          ports: 0 5t
  `
- Show available features`swconfig dev rt305x help
  switch0: rt305x(rt305x-esw), ports: 7 (cpu @ 6), vlans: 4096
       --switch
          Attribute 1 (int): enable_vlan (VLAN mode (1:enabled))
          Attribute 2 (int): alternate_vlan_disable (Use en_vlan instead of doubletag to disable VLAN mode)
          Attribute 3 (none): apply (Activate changes in the hardware)
          Attribute 4 (none): reset (Reset the switch)
       --vlan
          Attribute 1 (ports): ports (VLAN port mapping)
       --port
          Attribute 1 (int): disable (Port state (1:disabled))
          Attribute 2 (int): doubletag (Double tagging for incoming vlan packets (1:enabled))
          Attribute 3 (int): untag (Untag (1:strip outgoing vlan tag))
          Attribute 4 (int): led (LED mode (0:link, 1:100m, 2:duplex, 3:activity, 4:collision, 5:linkact, 6:duplcoll, 7:10mact, 8:1)
          Attribute 5 (int): lan (HW port group (0:wan, 1:lan))
          Attribute 6 (int): recv_bad (Receive bad packet counter)
          Attribute 7 (int): recv_good (Receive good packet counter)
          Attribute 8 (int): pvid (Primary VLAN ID)
          Attribute 9 (string): link (Get port link information)
  `or`swconfig dev rtl8366rb help
  switch1: rtl8366rb(RTL8366RB), ports: 6 (cpu @ 5), vlans: 4096
       --switch
          Attribute 1 (int): enable_learning (Enable learning, enable aging)
          Attribute 2 (int): enable_vlan (Enable VLAN mode)
          Attribute 3 (int): enable_vlan4k (Enable VLAN 4K mode)
          Attribute 4 (none): reset_mibs (Reset all MIB counters)
          Attribute 5 (int): blinkrate (Get/Set LED blinking rate (0 = 43ms, 1 = 84ms, 2 = 120ms, 3 = 170ms, 4 = 340ms, 5 = 670ms))
          Attribute 6 (int): enable_qos (Enable QOS)
          Attribute 7 (none): apply (Activate changes in the hardware)
          Attribute 8 (none): reset (Reset the switch)
       --vlan
          Attribute 1 (string): info (Get vlan information)
          Attribute 2 (int): fid (Get/Set vlan FID)
          Attribute 3 (ports): ports (VLAN port mapping)
       --port
          Attribute 1 (none): reset_mib (Reset single port MIB counters)
          Attribute 2 (string): mib (Get MIB counters for port)
          Attribute 3 (int): led (Get/Set port group (0 - 3) led mode (0 - 15))
          Attribute 4 (int): disable (Get/Set port state (enabled or disabled))
          Attribute 5 (int): rate_in (Get/Set port ingress (incoming) bandwidth limit in kbps)
          Attribute 6 (int): rate_out (Get/Set port egress (outgoing) bandwidth limit in kbps)
          Attribute 7 (int): pvid (Primary VLAN ID)
          Attribute 8 (string): link (Get port link information)
  `

### Example switch port on/off per port (ex: on/off port 4)

    disable: ssh > swconfig dev switch0 port 4 set disable 1
    enable:  ssh > swconfig dev switch0 port 4 set disable 0

## Change

Note: Make sure to apply any changes made previously with the "**set**" command.

- LEDs:`swconfig dev rtl8366s port 0 set led 2
  swconfig dev rtl8366rb set apply`
- Disable VLANs:`swconfig dev switch0 set enable_vlan 0
  swconfig dev switch0 set apply`

### Design and rationale

Generic Netlink Switch configuration API

## Introduction

The following documentation covers the Linux Ethernet switch configuration API which is based on the Generic Netlink infrastructure.

## Scope and rationale

Most Ethernet switches found in small routers are managed switches which allow the following operations:

- configure a port to belong to a particular set of VLANs either as tagged or untagged
- configure a particular port to advertise specific link/speed/duplex settings
- collect statistics about the number of packets/bytes transferred/received
- any other vendor specific feature: rate limiting, single/double tagging...

Such switches can be connected to the controlling CPU using different hardware busses, but most commonly:

- SPI/I2C/[GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) bitbanging
- MDIO
- Memory mapped into the CPU register address space

As of today the usual way to configure such a switch was either to write a specific driver or to write an user-space application which would have to know about the hardware differences and figure out a way to access the switch registers (spidev, SIOCIGGMIIREG, mmap...) from user-space.

This has multiple issues:

- proliferation of ad-hoc solutions to configure a switch both open source and proprietary
- absence of common software reference for switches commonly found on the market (Broadcom, Lantiq/Infineon/ADMTek, Marvell, Qualcomm/Atheros...) which implies a duplication effort for each implementer
- inability to leverage existing hardware representation mechanisms such as Device Tree (spidev, i2c-dev.. do not belong in Device Tree and rely on Linux-specific "forwarder" drivers) to describe a switch device

The goal of the switch configuration API is to provide a common basis to build re-usable and extensible switch drivers with the following ideas in mind:

- having a central point of configuration on top of which a reference user-space implementation can be provided but also allow for other user-space implementations to exist
- ensure the Linux kernel is in control of the actual hardware access
- be extensible enough to support per-switch features without making the generic implementation too heavy weighted and without making user-space changes each and every time a new feature is added

Based on these design goals the Generic Netlink kernel/user-space communication mechanism was chosen because it allows for all design goals to be met.

## Distributed Switch Architecture vs. swconfig

The Marvell Distributed Switch Architecture (DSA) drivers is an existing solution which is a heavy switch driver infrastructure, is [Marvell](/docs/techref/hardware/soc/soc.marvell)-centric, only supports MDIO connected switches, mangles an Ethernet driver transmit/receive paths and does not offer a central control path for the user.

swconfig is vendor agnostic, does not mangle the transmit/receive path of an Ethernet driver and is focused on the control path of the switch rather that the data path. It is based on Generic Netlink to allow for each switch driver to easily extend the swconfig API without causing major core parts rework each and every time someone has a specific feature to implement and offers a central configuration point with a well-defined API.

\* More info e.g. at [LWN.net 2017-04-19: The rise of Linux-based networking hardware](https://lwn.net/Articles/720313/):

"The Linux kernel manipulates switches with three different operation structures: `switchdev_ops`, `ethtool_ops` and `netdev_ops`. Certain switches, however, also need distributed switch architecture (DSA).

DSA's development was parallel to swconfig, written by the OpenWrt project. The main difference between swconfig and DSA is that DSA-supported switches show one network interface per port, whereas swconfig-configured switches show up as a single port, which limits the amount of information that can be extracted from the switch. For example, you cannot have per-port traffic statistics with swconfig. That limitation is what led to the creation of the switchdev framework, when swconfig was proposed (then refused) for inclusion in mainline. Another goal of switchdev was to support bridge hardware offloading and network interface card (NIC) virtualization…"

## Switch configuration API

The main data structure of the switch configuration API is a "struct switch_dev" which contains the following members:

- a set of common operations to all switches (struct switch_dev_ops)
- a network device pointer it is physically attached to
- a number of physical switch ports (including CPU port)
- a set of configured vlans
- a CPU specific port index

A particular switch device is registered/unregistered using the following pair of functions:

register_switch(struct switch_dev \*sw_dev, struct net_device \*dev); unregister_switch(struct switch_dev);

A given switch driver can be backed by any kind of underlying bus driver (i2c client, [GPIO](../../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) driver, MMIO driver, directly into the Ethernet MAC driver...).

The set of common operations to all switches is represented by the "struct switch_dev_ops" function pointers, these common operations are defined as such:

- get the port list of a VLAN identifier
- set the port list of a VLAN identifier
- get the primary VLAN identifier of a port
- set the primary VLAN identifier of a port
- apply the changed configuration to the switch
- reset the switch
- get a port link status
- get a port statistics counters

The switch_dev_ops structure also contains an extensible way of representing and querying switch specific features, 3 different types of attributes are available:

- global attributes: attributes global to a switch (name, identifier, number of ports)
- port attributes: per-port specific attributes (MIB counters, enabling port mirroring...)
- vlan attributes: per-VLAN specific attributes (VLAN id, specific VLAN information)

Each of these 3 categories must be represented using an array of "struct switch_attr" attributes. This structure must be filed with:

- an unique name for the operation
- a description for the operation
- a setter operation
- a getter operation
- a data type (string, integer, port)
- eventual min/max limits to validate user input data

The "struct switch_attr" directly maps to a Generic Netlink type of command and will be automatically discovered by the "swconfig" user-space utility without requiring user-space changes.

## References

- <https://web.archive.org/web/20081205103732/http://inst.eecs.berkeley.edu/~pathorn/ip175c/> (links to archive.org; content of original site is gone)
- <https://web.archive.org/web/20110831151445/http://inst.eecs.berkeley.edu/~pathorn/ip175c/phylib-swconfig/> (links to archive.org; content of original site is gone)
- <http://www.debwrt.net/2010/11/07/switch-configuration-command-line-tool-swconfig-ported-2/>
- <http://www.icplus.com.tw/pp-IP175C.html>
- [OpenWrt Forum](https://forum.openwrt.org/viewtopic.php?pid=152508)
- [switch_port](https://forum.openwrt.org/viewtopic.php?id=28716)
- [Is VLAN trunking on WR1034ND with VLAN id higher than 15 possible](https://forum.openwrt.org/viewtopic.php?id=27485)
