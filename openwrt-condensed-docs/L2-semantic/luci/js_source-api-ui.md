---
title: 'LuCI API: ui'
module: luci
origin_type: js_source
token_count: 69
version: 8e3bc67
source_file: L1-raw/luci/js_source-api-ui.md
last_pipeline_run: '2026-03-11T14:46:50.602050+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/ui.js
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
# LuCI API: ui

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.ui.html

---



## scrubMenu(node) ⇒ `Node`
Erase the menu node

**Kind**: global function  

| Param | Type |
| --- | --- |
| node | `Node` |