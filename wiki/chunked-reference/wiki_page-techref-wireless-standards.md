---
title: Wireless Standards
module: wiki
origin_type: wiki_page
token_count: 845
source_file: L1-raw/wiki/wiki_page-techref-wireless-standards.md
last_pipeline_run: '2026-03-29T23:50:02.157846+00:00'
source_url: https://openwrt.org/docs/techref/wireless.standards
language: text
ai_summary: The Wireless Standards module in OpenWrt provides an overview of various wireless communication standards relevant to the operating system. It covers standards such as 802.11a, 802.11b, 802.11g, 802.11n, 802.11ac, 802.11ad, and 802.11ax, detailing their frequency bands and characteristics. Additionally, it discusses features in drivers that can be queried using the `iw phy <phy interface> info` command, highlighting the importance of compatibility for optimal data transfer rates. The module also introduces concepts like MIMO, HT, VHT, HE, MCS, RSDB, and WOW, which are essential for understanding wireless performance and capabilities.
ai_when_to_use: This module is useful when configuring or troubleshooting wireless settings in OpenWrt, especially when selecting hardware or optimizing performance based on supported standards and features.
ai_related_topics:
- MIMO
- HT
- VHT
- HE
- MCS
- RSDB
- WOW
---

> **Source:** [https://openwrt.org/docs/techref/wireless.standards](https://openwrt.org/docs/techref/wireless.standards)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-29

# Wireless Standards

This article lists common standards and basic features that are relevant to OpenWrt.

## 802.11a

Old standard that operates in 5GHz [frequency band](https://en.wikipedia.org/wiki/Frequency_band)

[IEEE_802.11a-1999](https://en.wikipedia.org/wiki/IEEE_802.11a-1999)

## 802.11b

[IEEE_802.11b-1999](https://en.wikipedia.org/wiki/IEEE_802.11b-1999) Operates in 2.4GHz Band Old standard.

## 802.11g

[](https://en.wikipedia.org/wiki/IEEE_802.11g-2003) Operates in 2.4GHz Band Old standard.

## 802.11n

[IEEE_802.11n-2009](https://en.wikipedia.org/wiki/IEEE_802.11n-2009)

## 802.11ac

[IEEE_802.11ac](https://en.wikipedia.org/wiki/IEEE_802.11ac) Also called "Wifi 5"

## 802.11ad

[IEEE_802.11ad](https://en.wikipedia.org/wiki/IEEE_802.11ad) Not very common in OpenWrt.

## 802.11ax

[IEEE_802.11ax](https://en.wikipedia.org/wiki/IEEE_802.11ax)

Also called "Wifi 6"

### Features in Drivers

Each hardware has certain features that can be queried in OpenWrt by using `iw phy <phy interface> info `

Mismatching features result in compatibility problems and possibly reduced data transfer rates.

example:

    RX LDPC
    HT20/HT40
    SM Power Save disabled
    RX HT20 SGI
    RX HT40 SGI
    TX STBC
    RX STBC 1-stream
    Max AMSDU length: 3839 bytes
    DSSS/CCK HT40

#### MIMO multiple-input and multiple-output

Technology that uses multiple antennas to increase data transfer rates. see also MCS tables

[STBC](https://en.wikipedia.org/wiki/Space%E2%80%93time_block_code) is part of MIMO.

[MU-MIMO](https://en.wikipedia.org/wiki/Multi-user_MIMO)

#### HT, VHT, HE

Required for higher throughput - 802.11n, 802.11ac, 802.11ax standards. HT ... 802.11n , VHT ... 802.11ac, HE ... 802.11ax

HT20 : 20 MHz wide channels HT40: 40 MHz VHT80 : 80 MHz VHT160: 160MHz

see also MCS table

#### MCS Modulation and Coding Scheme

often visualized as a table. The MCS Index is a value that the hardware supports and uses when communicating.

:!: Low data rates mean the higher indexes are not used. Reasons might be configuration or interference.

#### RSDB DBDC

Acronym for Radio Simultan Dual Band, Dual Band Dual Concurrent

Use two frequency bands at the same time by one endpoint.

Supported by: mt76 and potentially brcmfmac ([BCM4359](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/drivers/net/wireless/broadcom?id=d4aef159394d5940bd7158ab789969dab82f7c76) )

Normally radios operate in Single Band Single Concurrent (SBSC) (OpenWrt: 802.11an, 802.11bgn) or are capable of Dual Band Single Concurrent (DBSC): having 2 frequency bands selectable (OpenWrt: 802.11abgn capable).

#### WOW Wake On Wlan

[Wake-on-LAN](https://en.wikipedia.org/wiki/Wake-on-LAN)

## Links

[some MCS Tables](https://www.semfionetworks.com/blog/mcs-table-updated-with-80211ax-data-rates)
