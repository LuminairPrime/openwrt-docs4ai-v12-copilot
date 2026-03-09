---
title: 'LuCI API: widgets'
module: luci
origin_type: js_source
token_count: 126
version: unknown
source_file: L1-raw/luci/js_source-api-tools-widgets.md
last_pipeline_run: '2026-03-09T18:30:57.384548+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/tools/widgets.js
language: javascript
---
# LuCI API: widgets

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.widgets.html

---



## getUsers() ⇒ `Array.<string>`
Get users found in `/etc/passwd`.

**Kind**: global function  

## getGroups() ⇒ `Array.<string>`
Get users found in `/etc/group`.

**Kind**: global function  

## getDevices(network) ⇒ `Array.<string>`
Get bridge devices or Layer 3 devices of a network object.

**Kind**: global function  

| Param | Type |
| --- | --- |
| network | `object` |