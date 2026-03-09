---
title: Xenomai - real-time framework inside OpenWrt
module: wiki
origin_type: wiki_page
token_count: 503
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-xenomai.md
last_pipeline_run: '2026-03-09T18:12:55.650305+00:00'
language: text
---
# Xenomai - real-time framework inside OpenWrt

![cleanup&noheader&nofooter&noeditbtn](/page>meta/infobox/cleanup&noheader&nofooter&noeditbtn) ![wip&noheader&nofooter&noeditbtn](/page>meta/infobox/wip&noheader&nofooter&noeditbtn)

# Xenomai - real-time framework inside OpenWrt

This techref describe a work in progress finalize to support Xenomai (<http://www.xenomai.org/>) real-time framework inside OpenWrt.

:!: This article describe a WIP activity. Don't rely on it. :!:

Thanks to Adeos, Xenomai will receive the interrupts first and decide to handle them or not. If not, they will then be transfered to the regular Linux kernel. Also, Xenomai provides a framework to develop applications which can be easily moved between the Real Time Xenomai environment and the regular Linux system. Moreover, Xeno provides a set of APIs (called "skins") that emulate traditional RTOSes such as VxWorks and pSOS and implement other APIs such as POSIX. Thus, porting third party real time applications to Xenomai is a fairly simple process.[^1]

An example of usage is available on xenomai.org website.

## Pre-condition

Xenomai framework run only on some architecture and generally isn't needed for your purpose; the 2.5.3 version can be used for arm\|x86\|powerpc and only for a specific linux kernel version. Here follows a table that can help you to choise the couple xenomai versione/kernel version per arch.

|                 |         |               |
|:----------------|:--------|--------------:|
| Xenomai version | Arch    | linux version |
| 2.5.3           | arm     |        2.6.33 |
| 2.5.3           | powerpc |        2.6.34 |
| 2.5.3           | x86     |    2.6.34-rc5 |

## Status

Xenomai is intended to be used only for specific purpose and OpenWrt community generally don't support it directly.  

[^1]: from <http://www.armadeus.com/wiki/index.php?title=Xenomai>