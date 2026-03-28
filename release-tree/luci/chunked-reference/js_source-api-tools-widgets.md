---
title: 'LuCI API: widgets'
module: luci
origin_type: js_source
token_count: 126
source_file: L1-raw/luci/js_source-api-tools-widgets.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/tools/widgets.js
source_locator: modules/luci-base/htdocs/luci-static/resources/tools/widgets.js
language: javascript
ai_summary: Provides reusable LuCI view-level widget helpers shared across multiple LuCI packages. Implements bandwidth graph components, interface status badges, SSID/signal display helpers, and shared CSS-class-to-color mappings; widgets are instantiated in render() methods and updated live via polling or event callbacks rather than full page reloads.
ai_when_to_use: Reference when building a LuCI view that needs a pre-built interface status indicator, an animated traffic graph, or a generic signal-strength display; use these helpers to match the visual conventions of the default OpenWrt LuCI theme.
ai_related_topics:
- LuCI.tools.widgets
- LuCI.ui
- LuCI.network
- renderBadge
- updateIfaceStatus
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/tools/widgets.js](https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/tools/widgets.js)
> **Kind:** js_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

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
