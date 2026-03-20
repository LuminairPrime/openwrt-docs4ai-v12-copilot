---
title: ubox
module: wiki
origin_type: wiki_page
token_count: 242
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-ubox.md
last_pipeline_run: '2026-03-20T04:40:03.869041+00:00'
language: text
ai_summary: The `ubox` package is a component of the OpenWrt operating system that facilitates the management of UCI configurations and block devices. Introduced in revision r36427, it includes features for generating fstab configurations and detecting block devices. Users can utilize the `block detect` command to create a sample UCI configuration file, which is particularly useful for setting up extroot if the target is set to '/'. Additionally, the `block info` command can be employed to retrieve the UUID of block devices.
ai_when_to_use: Use the `ubox` package when configuring block devices and UCI settings in OpenWrt, especially for generating fstab entries. It is particularly relevant during the initial setup of storage devices.
ai_related_topics:
- block detect
- block info
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
