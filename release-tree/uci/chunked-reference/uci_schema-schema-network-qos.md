---
title: 'UCI Default Schema: qos'
module: uci
origin_type: uci_schema
token_count: 420
source_file: L1-raw/uci/uci_schema-schema-network-qos.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/openwrt/blob/unknown/package/network/config/qos-scripts/files/etc/config/qos
source_locator: package/network/config/qos-scripts/files/etc/config/qos
language: uci
ai_summary: Defines the default UCI configuration schema for the OpenWrt qos-scripts traffic-shaping system. Specifies interface sections with classgroup, enabled, upload (kbit/s), and download (kbit/s) options, and classify sections mapping port ranges, protocols, and address patterns to priority classes (Priority, Express, Normal, Bulk) used by the HFS+ queue discipline.
ai_when_to_use: Reference when configuring per-interface bandwidth limits and traffic prioritization rules to ensure UCI key names, section types, and option values match what the qos-scripts daemon expects.
ai_related_topics:
- qos.interface
- qos.classify
- qos.classgroup
- qos.default
---

> **Source:** [https://github.com/openwrt/openwrt/blob/unknown/package/network/config/qos-scripts/files/etc/config/qos](https://github.com/openwrt/openwrt/blob/unknown/package/network/config/qos-scripts/files/etc/config/qos)
> **Kind:** uci_schema | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

# UCI Default Schema: qos

> **Source:** `package/network/config/qos-scripts/files/etc/config/qos`

# qos
```uci
# QoS configuration for OpenWrt

# INTERFACES:
config interface wan
	option classgroup  "Default"
	option enabled      0
	option upload       128
	option download     1024

# RULES:
config classify
	option target       "Priority"
	option ports        "22,53"
	option comment      "ssh, dns"
config classify
	option target       "Normal"
	option proto        "tcp"
	option ports        "20,21,25,80,110,443,993,995"
	option comment      "ftp, smtp, http(s), imap"
config classify
	option target       "Express"
	option ports        "5190"
	option comment      "AOL, iChat, ICQ"
config default
	option target       "Express"
	option proto        "udp"
	option pktsize      "-500"
config reclassify
	option target       "Priority"
	option proto        "icmp"
config default
	option target       "Bulk"
	option portrange    "1024-65535"


# Don't change the stuff below unless you
# really know what it means :)

config classgroup "Default"
	option classes      "Priority Express Normal Bulk"
	option default      "Normal"


config class "Priority"
	option packetsize  400
	option avgrate     10
	option priority    20
config class "Priority_down"
	option packetsize  1000
	option avgrate     10


config class "Express"
	option packetsize  1000
	option avgrate     50
	option priority    10

config class "Normal"
	option packetsize  1500
	option packetdelay 100
	option avgrate     10
	option priority    5
config class "Normal_down"
	option avgrate     20

config class "Bulk"
	option avgrate     1
	option packetdelay 200
```
