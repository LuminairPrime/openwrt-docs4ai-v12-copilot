---
title: mountd – Technical Reference
module: wiki
origin_type: wiki_page
token_count: 323
source_file: L1-raw/wiki/wiki_page-techref-mountd.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_url: https://openwrt.org/docs/techref/mountd
language: text
ai_summary: The mountd module is an automount daemon for OpenWrt, configured through the `/etc/config/mountd` file. It has been part of OpenWrt since version r17853 and is licensed under GPLv2. Although mountd was designed for embedded devices, it has since been replaced by blockd in newer versions. The module requires dependencies such as +uci, +kmod-usb-storage, and +kmod-fs-autofs4 to function properly.
ai_when_to_use: Use mountd when you need an automount daemon specifically tailored for embedded devices in OpenWrt. However, consider using blockd for newer implementations.
ai_related_topics:
- mountd
- blockd
- uci
- kmod-usb-storage
- kmod-fs-autofs4
---

> **Source:** [https://openwrt.org/docs/techref/mountd](https://openwrt.org/docs/techref/mountd)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-28

# mountd – Technical Reference

OpenWrt automount daemon, is configured in `/etc/config/mountd`

- mountd is available in OpenWrt since [r17853 (trunk)](https://dev.openwrt.org/changeset/17853) and published under the GPLv2.
- [mountd has been replaced](https://git.openwrt.org/?p=openwrt/openwrt.git;a=commit;h=6a772cb953c4c36dfdf49365937b71017652562a) by [blockd](https://git.openwrt.org/?p=openwrt/openwrt.git;a=commit;h=7e4b869c451383f7fca654abd1cd726c862d6dd7)
- [git commits regarding mountd](git>mountd)

## What is mountd?

- `mountd` is another [daemon](https://en.wikipedia.org/wiki/Daemon (computing)) written in [C](https://en.wikipedia.org/wiki/C (programming language)) with the ability to ...:?:
- `mountd` replaces ...:?:... on full blown desktop distributions.

## Help with the development of mountd

1.  review of the code
2.  augment new functions

## Why do we want mountd?

There was no daemon for the above mentioned purposes suited for embedded devices available. Now there is one.

## Dependencies of mountd

- +uci +kmod-usb-storage +kmod-fs-autofs4
