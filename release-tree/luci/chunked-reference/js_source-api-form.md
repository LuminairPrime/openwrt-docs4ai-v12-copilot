---
title: 'LuCI API: form'
module: luci
origin_type: js_source
token_count: 143
version: 18e0538
source_file: L1-raw/luci/js_source-api-form.md
last_pipeline_run: '2026-03-20T04:40:03.869041+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/form.js
language: javascript
ai_summary: Provides the first-class LuCI form rendering framework used by modern views. Defines Map, JSONMap, Section, NamedSection, TableSection, and GridSection containers plus widget types (Flag, Value, ListValue, DynamicList, MultiValue, SectionValue, HiddenValue); supports async option loading via load() and custom validation callbacks on each widget.
ai_when_to_use: Use when creating LuCI views that need structured form rendering with inline validation, async select option loading, or sections bound to JSON data (JSONMap) rather than a UCI file; this is the preferred form API for new LuCI packages.
ai_related_topics:
- LuCI.form.Map
- LuCI.form.JSONMap
- LuCI.form.GridSection
- LuCI.form.DynamicList
- LuCI.form.Value
- LuCI.cbi
---
# LuCI API: form

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.form.html

---



## isEqual(x, y) ⇒ `boolean`
Determines equality of two provided parameters. Can be arrays or objects.

**Kind**: global function  

| Param | Type |
| --- | --- |
| x | `\*` | 
| y | `\*` | 

## isContained(x, y) ⇒ `boolean`
Determines containment of two provided parameters. Can be arrays or objects.

**Kind**: global function  

| Param | Type |
| --- | --- |
| x | `\*` | 
| y | `\*` |
