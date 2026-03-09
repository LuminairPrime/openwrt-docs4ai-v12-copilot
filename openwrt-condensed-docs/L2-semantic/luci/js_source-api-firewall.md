---
title: 'LuCI API: firewall'
module: luci
origin_type: js_source
token_count: 262
version: unknown
source_file: L1-raw/luci/js_source-api-firewall.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/firewall.js
language: javascript
---
# LuCI API: firewall

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.firewall.html

---



## initFirewallState() ⇒ `Promise`
Load the firewall configuration.

**Kind**: global function  

## parseEnum(s, values) ⇒ `string`
Parse an enum value.

**Kind**: global function  

| Param | Type |
| --- | --- |
| s | `string` | 
| values | `Array.<string>` | 

## parsePolicy(s, [defaultValue]) ⇒ `string`
Parse a policy value, or defaultValue if not found.

**Kind**: global function  

| Param | Type | Default |
| --- | --- | --- |
| s | `string` |  | 
| [defaultValue] | `Array.<string>` | `['DROP', 'REJECT', 'ACCEPT']` | 

## lookupZone(name) ⇒ `Zone`
Look up a firewall zone.

**Kind**: global function  

| Param | Type |
| --- | --- |
| name | `string` | 

## getColorForName(forName) ⇒ `string`
Generate a colour for a name.

**Kind**: global function  

| Param | Type |
| --- | --- |
| forName | `string` |