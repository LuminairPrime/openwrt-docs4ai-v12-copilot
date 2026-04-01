---
title: 'LuCI API: ui'
module: luci
origin_type: js_source
token_count: 69
source_file: L1-raw/luci/js_source-api-ui.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/ui.js
source_locator: modules/luci-base/htdocs/luci-static/resources/ui.js
language: javascript
ai_summary: Provides the LuCI client-side UI widget and notification layer. Implements ui.addNotification(), ui.showModal(), ui.hideModal(), ui.addTab(), ui.showTabs(); defines typed input widgets (Textfield, Combobox, Dropdown, DynamicList, FileUpload, Select, Checkbox) and live-state helpers (NetworkMenu, PacketMonitor); also manages the XHR indicator lifecycle.
ai_when_to_use: Reference when you need to programmatically show modals or notifications, render typed input widgets outside of a form Map, implement a tabbed section in a LuCI view, or build a live-updating packet/interface monitor component.
ai_related_topics:
- LuCI.ui.showModal
- LuCI.ui.addNotification
- LuCI.ui.addTab
- LuCI.ui.Dropdown
- LuCI.ui.FileUpload
- LuCI.ui.NetworkMenu
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/ui.js](https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/ui.js)
> **Kind:** js_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-04-01

# LuCI API: ui

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.ui.html

---



## scrubMenu(node) ⇒ `Node`
Erase the menu node

**Kind**: global function  

| Param | Type |
| --- | --- |
| node | `Node` |
