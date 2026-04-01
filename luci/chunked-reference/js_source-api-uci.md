---
title: 'LuCI API: uci'
module: luci
origin_type: js_source
token_count: 95
source_file: L1-raw/luci/js_source-api-uci.md
last_pipeline_run: '2026-04-01T13:49:08.540826+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/uci.js
source_locator: modules/luci-base/htdocs/luci-static/resources/uci.js
language: javascript
ai_summary: Provides the LuCI JavaScript UCI binding that defers all reads and writes to batched rpcd calls. Implements load(), get(), set(), unset(), save(), apply(), revert(), sections(), add(), remove(), and foreach(); changes are staged in memory and only flushed to the router on save()/apply(), making it safe to call get() before load() resolves.
ai_when_to_use: Reference when directly reading or writing UCI configuration from JavaScript in a LuCI view; use uci.load('config') in the view's load() method, then uci.get/set throughout render(), and call uci.save()+uci.apply() only on user confirmation.
ai_related_topics:
- LuCI.uci.load
- LuCI.uci.get
- LuCI.uci.set
- LuCI.uci.save
- LuCI.uci.apply
- LuCI.uci.sections
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/uci.js](https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/uci.js)
> **Kind:** js_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-04-01

# LuCI API: uci

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.uci.html

---



## isEmpty(object, ignore) ⇒ `boolean`
Determine whether an object is empty.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| object | `object` | object to enumerate. |
| ignore | `string` | property to ignore. |
