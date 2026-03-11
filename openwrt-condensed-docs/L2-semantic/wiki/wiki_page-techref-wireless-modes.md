---
title: Wireless Modes
module: wiki
origin_type: wiki_page
token_count: 349
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-wireless-modes.md
last_pipeline_run: '2026-03-11T12:37:15.044626+00:00'
language: text
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
