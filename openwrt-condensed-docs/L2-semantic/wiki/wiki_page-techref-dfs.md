---
title: DFS
module: wiki
origin_type: wiki_page
token_count: 611
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-dfs.md
last_pipeline_run: '2026-03-12T13:29:57.345766+00:00'
language: text
ai_summary: The DFS (Dynamic Frequency Selection) module in OpenWrt manages the use of 5GHz WLAN channels that may overlap with weather radar frequencies, ensuring compliance with regulations such as those outlined in 802.11h. It is utilized during Automatic Channel Selection (ACS) in hostapd to identify and select available channels. Different hardware drivers provide varying levels of DFS support, including ath9k, ath10k, and mt76, with some limitations based on regulatory schemes like DFS-FCC and DFS-ETSI. Users should be aware of potential interoperability issues due to changing hardware and regulatory compliance, as well as the availability of proprietary drivers that may offer additional DFS functionality.
ai_when_to_use: Use the DFS module when configuring 5GHz WLAN channels in OpenWrt to ensure compliance with local regulations and optimize channel selection. It is particularly relevant for environments where radar interference is a concern.
ai_related_topics:
- Dynamic_frequency_selection
- 802.11h
- ACS
---
# DFS

[Dynamic_frequency_selection](https://en.wikipedia.org/wiki/Dynamic_frequency_selection) plays a role in 5GHz frequencies that are shared with weather radar. It is related to [802.11h](https://en.wikipedia.org/wiki/IEEE_802.11h).

DFS support is used during ACS/"survey" in hostapd to find and select free WLAN channels.

Many countries regulate operation of the 5GHz spectrum - see [List_of_WLAN_channels](https://en.wikipedia.org/wiki/List_of_WLAN_channels).

:!: Due to fast development, changing hardware, regulatory changes and compliance issues there can be interoperability issues.

:!: OpenWrt uses open source drivers with varying quality and upstream support. Sometimes they can be abandoned by the manufactorer, or no longer support some 5GHz operation due to regulatory changes.

:!: OEM proprietary drivers can sometimes offer DFS when OpenWrt does not.

:!: There are different DFS schemes: DFS-FCC (USA), DFS-ETSI (Europe), DFS-JP (Japan).

:!: Try to use the non DFS channels if you have old hardware/clients.

## DFS support

- ath9k: DFS-ETSI, DFS-FCC (source: [linux-wireless](http://marc.info/?l=linux-wireless&m=144524581929146)), probably DFS-JP (git commits)
- ath10k: DFS-FCC (source: [linux-wireless](http://marc.info/?l=linux-wireless&m=144524581929146)), probably DFS-ETSI
- ath11k: DFS-FCC (source: [linux-wireless](https://marc.info/?l=linux-wireless&m=170227574420539)), probably DFS-ETSI
- mt76: DFS-ETSI, DFS-FCC, DFS-JP. As of 2021-02-22, DFS is unsupported on the MT7613 radio however, despite the hardware supporting it.
- mwlwifi (source:[linux-wireless](http://marc.info/?l=linux-wireless&m=146707822404863&w=2)), but support is problematic on some hardware and won't be fixed ([GitHub issue \#75](https://github.com/kaloz/mwlwifi/issues/75))
- mwifiex (source: git log: "DFS support in AP mode",[kernel.org](http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cf075eac9ca94ec54b5ae0c0ec798839f962be55))

## DFS status unknown

- ath9k_htc
- wlcore, wl18xx (allow using dfs channels,add radar_debug_mode debugfs file for DFS testing)
- brcmfmac
- brcmsmac
- b43

## No DFS support

- mwl8k
