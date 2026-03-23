---
title: ubox
module: wiki
origin_type: wiki_page
token_count: 242
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-ubox.md
last_pipeline_run: '2026-03-23T22:14:22.429226+00:00'
language: text
---
# ubox

- [Project's git](http://git.openwrt.org/?p=project/ubox.git;a=summary)

Package `ubox` was added in [r36427](https://dev.openwrt.org/changeset/36427) and package `block-mount` was dropped in [r36988](https://dev.openwrt.org/changeset/36988). [r37199](https://dev.openwrt.org/changeset/37199) finally adds a UCI-default script for fstab generation.

Cf.

- <https://forum.openwrt.org/viewtopic.php?pid=205552#p205552>
- <https://lists.openwrt.org/pipermail/openwrt-devel/2013-June/020538.html>

for some insight.

call

    block detect

to get a sample UCI configuration file. If target is / then it will be used as extroot. block info is also valid to get the uuid.

## OpenWrt – operating system architecture

![architecture&noheader&nofooter](/page>docs/techref/architecture&noheader&nofooter)
