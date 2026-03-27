---
title: 'LuCI API: static'
module: luci
origin_type: js_source
token_count: 217
source_file: L1-raw/luci/js_source-api-protocol-static.md
last_pipeline_run: '2026-03-27T07:16:36.403470+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/protocol/static.js
source_locator: modules/luci-base/htdocs/luci-static/resources/protocol/static.js
language: javascript
ai_summary: Implements the LuCI protocol handler for static IP interfaces. Extends the base network Protocol class with getIPAddr(), getNetmask(), getGateway(), and getDNS() accessors that read directly from the UCI interface section; used by the LuCI Network model when rendering or editing a static-type interface in the Interfaces page.
ai_when_to_use: Reference when extending LuCI network views that need to read or display static IP configuration, or when implementing a custom protocol handler that should follow the same pattern of extending LuCI.network.Protocol with typed getter methods.
ai_related_topics:
- LuCI.network.Protocol
- LuCI.network.getIPAddr
- LuCI.network.getNetmask
- LuCI.network.getGateway
- LuCI.uci
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