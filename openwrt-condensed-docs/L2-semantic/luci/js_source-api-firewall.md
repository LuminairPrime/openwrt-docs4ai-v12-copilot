---
title: 'LuCI API: firewall'
module: luci
origin_type: js_source
token_count: 262
version: 8fa4744
source_file: L1-raw/luci/js_source-api-firewall.md
last_pipeline_run: '2026-03-12T18:07:24.356646+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/firewall.js
language: javascript
ai_summary: Implements the LuCI firewall abstraction over the nftables/iptables UCI config. Provides Firewall, Zone, Rule, Redirect, and Forwarding classes; Firewall.getZones() returns zone objects with getNetworks(), getSrcRules(), getDestRules(); Rule and Redirect mirror UCI firewall sections and expose getOptions(), setOption(), and remove() for in-memory editing before save.
ai_when_to_use: Reference when building a LuCI view that reads or modifies firewall zones, inter-zone forwarding rules, DNAT redirects, or custom iptables rules; use Firewall.getZoneByNetwork() to look up the zone for a given network interface name.
ai_related_topics:
- LuCI.firewall.Firewall
- LuCI.firewall.Zone
- LuCI.firewall.Rule
- LuCI.firewall.Redirect
- LuCI.firewall.getZones
- LuCI.uci
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