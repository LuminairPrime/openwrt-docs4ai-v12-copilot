---
title: "libnl and libnl-tiny \u2013 Technical Reference"
module: wiki
origin_type: wiki_page
token_count: 545
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-libnl.md
last_pipeline_run: '2026-03-10T12:16:41.912319+00:00'
language: text
---
# libnl and libnl-tiny – Technical Reference

`libnl` is a library for applications dealing with netlink sockets, for instance to retrieve or change routing information, interface settings, and is used more generally when communicating with the kernel.

## libnl

The upstream version of `libnl` is maintained at <http://www.infradead.org/~tgr/libnl/>

Since `libnl` is somewhat heavyweight, it is not included by default on OpenWRT. If you need only basic netlink functionalities, you may want to use `libnl-tiny` instead. However, some applications require the full features of `libnl`.

Since [r47037](https://dev.openwrt.org/changeset/47037), the `libnl` package has been split into multiple components. The sizes below are approximate sizes after compression, based on the `ar71xx` target with musl:

| Name          | Size | Description                           |
|---------------|------|---------------------------------------|
| `libnl-core`  | 37K  | Common code for all netlink libraries |
| `libnl-genl`  | 8K   | Generic Netlink Library Functions     |
| `libnl-nf`    | 25K  | Netfilter Netlink Library Functions   |
| `libnl-route` | 91K  | Routing Netlink Library Functions     |

For compatibility, a meta-package name `libnl` depends on all the above packages.

## libnl-tiny

The `libnl-tiny` package is a stripped down version of libnl, included by default on OpenWRT.

The code is maintained directly in the OpenWRT code tree, see <http://git.openwrt.org/?p=openwrt.git;a=tree;f=package/libs/libnl-tiny>

| Name         | Size | Description                                                   |
|--------------|------|---------------------------------------------------------------|
| `libnl-tiny` | 14K  | Drop-in replacement for most of `libnl-core` and `libnl-genl` |

`libnl-tiny` replaces the most commonly used parts of `libnl-core` and `libnl-genl`. The API is a bit more limited, but compatible for most applications. The ABI is different, but that doesn't matter much.

Any package that can easily work with `libnl-tiny` instead of `libnl` should be changed to make use of it, since `libnl-tiny` is usually part of the default package set.

However, mixing `libnl`-based libraries with `libnl-tiny` does not work.
