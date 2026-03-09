---
title: 'LuCI API: static'
module: luci
origin_type: js_source
token_count: 217
version: unknown
source_file: L1-raw/luci/js_source-api-protocol-static.md
last_pipeline_run: '2026-03-09T18:12:55.650305+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/protocol/static.js
language: javascript
---
# LuCI API: static

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.static.html

---



## isCIDR(value) ⇒ `boolean`
Determine whether a provided value is a CIDR format IP string.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| value | `string` | the IP string to test. |

## calculateBroadcast(s, use_cfgvalue) ⇒ `string`
Calculate the broadcast IP for a given IP.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| s | `Node` | the ui element to test. |
| use_cfgvalue | `boolean` | whether to use the config or form value. |

## validateBroadcast(section_id, value) ⇒ `boolean`
Validate a broadcast IP for a section value.

**Kind**: global function  

| Param | Type |
| --- | --- |
| section_id | `string` | 
| value | `string` |