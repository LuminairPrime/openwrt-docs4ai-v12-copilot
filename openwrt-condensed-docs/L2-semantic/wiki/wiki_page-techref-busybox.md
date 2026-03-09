---
title: BusyBox
module: wiki
origin_type: wiki_page
token_count: 676
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-busybox.md
last_pipeline_run: '2026-03-09T19:21:03.362055+00:00'
language: text
---
# BusyBox

[BusyBox](https://en.wikipedia.org/wiki/BusyBox) is used for several system utilities in OpenWrt like `ash` shell, `cp`, `ls`, `echo`, `ping` and many others. It provides tiny replacements with fewer options for most of the utilities from [GNU Core Utilities](https://en.wikipedia.org/wiki/GNU Core Utilities), [GNU Inetutils](https://www.gnu.org/software/inetutils/) and other essential tools like `gzip`.

All this utilities are compiled as "applets" into a single binary file `/bin/busybox`.

## Identify OpenWrt version through udhcp

When an OpenWrt system tries to obtain an IP using DHCP on its WAN interface, it adds a Vendor-Class option that contains the Busybox version:

`Vendor-Class Option 60, length 12: "udhcp 1.28.3"`

This can be used to estimate which OpenWrt version is running on a router if you don't have access to the router itself.

| OpenWrt version | Busybox version |
|:----------------|:----------------|
| 7.06            | 1.4.2           |
| 7.07            | 1.4.2           |
| 7.09            | 1.4.2           |
| 8.09            | 1.11.2          |
| 8.09.1          | 1.11.2          |
| 8.09.2          | 1.11.2          |
| 10.03           | 1.15.3          |
| 10.03.1         | 1.15.3          |
| 12.09           | 1.19.4          |
| 17.01.0         | 1.25.1          |
| 17.01.1         | 1.25.1          |
| 17.01.2         | 1.25.1          |
| 17.01.3         | 1.25.1          |
| 17.01.4         | 1.25.1          |
| 17.01.5         | 1.25.1          |
| 17.01.6         | 1.25.1          |
| 17.01.7         | 1.25.1          |
| 18.06.0         | 1.28.3          |
| 18.06.1         | 1.28.3          |
| 18.06.2         | 1.28.4          |
| 18.06.3         | 1.28.4          |
| 18.06.4         | 1.28.4          |
| 18.06.5         | 1.28.4          |
| 19.07.0         | 1.30.1          |
| 22.03.0         | 1.35.0          |
| 23.05.0         | 1.36.1          |
| 24.10.0         | 1.36.1          |