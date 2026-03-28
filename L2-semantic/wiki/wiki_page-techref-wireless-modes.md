---
title: Wireless Modes
module: wiki
origin_type: wiki_page
token_count: 349
source_file: L1-raw/wiki/wiki_page-techref-wireless-modes.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_url: https://openwrt.org/docs/techref/wireless.modes
language: text
ai_summary: The Wireless Modes module in OpenWrt outlines various wireless operation modes supported by the system, including Access Point (AP), Ad-Hoc (IBSS), and Mesh Point (802.11s). Each mode serves specific networking purposes, such as AP for creating a wireless network, P2P for peer-to-peer connections, and Monitor for packet analysis. The module also references dynamic VLAN tagging and other advanced configurations. For detailed setup, users are directed to the relevant documentation and commands like 'iw list' to explore supported interface modes.
ai_when_to_use: This module is useful when configuring wireless interfaces in OpenWrt to meet specific networking requirements, such as setting up a home network or creating a mesh network.
ai_related_topics:
- AP
- AP/vlan
- IBSS
- MESH POINT (802.11s)
- MONITOR
- OCB
- P2P Client
- P2P-GO
- Station (Client)
- WDS
---
# Wireless Modes

FIXME This needs to indicate the UCI values for `option mode` to have any value

# Wireless Modes

For setting up the wireless modes see [Documentation](/docs/start)

    iw list

has a section with `Supported interface modes`

## AP

AP ... Access Point Also called "master" mode.

## AP/vlan

Dynamic VLAN tagging support in hostapd. see Kernel: [hostapd](https://wireless.wiki.kernel.org/en/users/documentation/hostapd#dynamic_vlan_tagging) see [ML](http://comments.gmane.org/gmane.linux.kernel.wireless.general/58064)

## IBSS (Ad-Hoc)

## MESH POINT (802.11s)

see [80211s](/docs/guide-user/network/wifi/mesh/80211s)

## MONITOR

radiotap headers package survey and injection

## OCB

Outside Context of a BSS

## P2P Client

P2P (Peer-to-peer) client

## P2P-GO

P2P (Peer-to-peer) Group Owner

## Station (Client)

Alternative name: managed mode Mode when connected to an AP.

## WDS

4address/4-address mode see: [IEEE 4-address](http://www.ieee802.org/1/files/public/802_architecture_group/802-11/4-address-format.doc)

## Links

     * Mode list taken from [[http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/nl80211.h|include/uapi/linux/nl80211.h]]
     * linux-wireless mailing list
