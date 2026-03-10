---
title: lldpd
module: wiki
origin_type: wiki_page
token_count: 335
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-lldpd.md
last_pipeline_run: '2026-03-10T12:16:41.912319+00:00'
language: text
---
# lldpd

See also: [lldpd upstream documentation](https://github.com/lldpd/lldpd/blob/master/README.md)

The goal of LLDP is to provide an inter-vendor compatible mechanism to deliver Link-Layer notifications to adjacent network devices.

## Abstract

An implementation of IEEE 802.1ab

lldpd (Link Layer Discovery Protocol daemon) daemon providing an industry standard protocol designed to supplant proprietary Link-Layer protocols such as Extreme's EDP (Extreme Discovery Protocol) and CDP (Cisco Discovery Protocol).

## Configuration

LLDP frames are link-local frames, do not use any network interfaces other than the ones that achieve a link with its link partner, and the link partner being another networking device. Do not use bridge,VLAN, or DSA conduit interfaces.

Example `/etc/config/lldpd`, start lldpd on all interfaces:

``` bash
config lldpd config
       # lldp defaults to listening on all interfaces
       # Set class of device
       option lldp_class 4
       # if empty, the distribution description is sent
       option lldp_description "OpenWrt System"
```

## Usage

*daemon must be running for lldpcli to work*

View neighbors across each enabled interface.

``` bash
lldpcli show neighbors
```

Get statistics about which interfaces are sending/receiving LLDP frames:

``` bash
lldpcli show statistics
```

## Known Issues

\- lldpd unable to receive frames on mediatek due to bug: <https://github.com/openwrt/openwrt/issues/13788>
