---
title: "mountd \u2013 Technical Reference"
module: wiki
origin_type: wiki_page
token_count: 323
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-mountd.md
last_pipeline_run: '2026-03-11T14:46:50.602050+00:00'
language: text
---
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
