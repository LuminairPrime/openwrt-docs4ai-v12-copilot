---
title: RPC daemon
module: wiki
origin_type: wiki_page
token_count: 274
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-rpcd.md
last_pipeline_run: '2026-03-11T12:37:15.044626+00:00'
language: text
---
# RPC daemon

In OpenWrt we commonly use [ubus](/docs/techref/ubus) for all kinds of communication. It can provide info from various software as well as request various actions. Nevertheless, not every part of OpenWrt has a daemon that can register itself using `ubus`. For an example `uci` and `opkg` are command-line tools without any background process running all the time.

It would be not efficient to write a daemon for every software like this and run them independently. This is why `rpcd` was developed. It’s a tiny daemon with support for plugins using trivial API. It loads library `.so` files and calls init function of each of them.

The code is published under [ISC license](https://en.wikipedia.org/wiki/ISC_license) and can be found via git at <https://git.openwrt.org/project/rpcd.git>.

### Default plugins

There are few small plugins distributed with the `rpcd` sources. Two of them (`session` and `uci`) are built-in, others are optional and have to be build as separated `.so` libraries. Apart from that there are other projects providing their own plugins.

See details here: [rpcd: OpenWrt ubus RPC daemon for backend server](/docs/techref/rpcd)
