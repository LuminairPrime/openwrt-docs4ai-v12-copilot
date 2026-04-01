---
title: 'LuCI API: fs'
module: luci
origin_type: js_source
token_count: 140
source_file: L1-raw/luci/js_source-api-fs.md
last_pipeline_run: '2026-04-01T13:49:08.540826+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/fs.js
source_locator: modules/luci-base/htdocs/luci-static/resources/fs.js
language: javascript
ai_summary: Provides the LuCI client-side filesystem API that proxies calls to the rpcd file plugin over HTTP. Implements stat(), list(), read(), write(), exec(), remove(), and lines(); all functions return Promises and pass arguments as JSON to the /ubus endpoint, so the calling LuCI view does not need to manage XHR directly.
ai_when_to_use: Reference when a LuCI view needs to read a config file that is not in UCI format, execute a shell command and capture stdout/stderr, list directory contents, or write a blob to the filesystem from the browser without a separate CGI endpoint.
ai_related_topics:
- LuCI.fs.read
- LuCI.fs.write
- LuCI.fs.exec
- LuCI.fs.stat
- LuCI.fs.list
- rpcd file plugin
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/fs.js](https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/fs.js)
> **Kind:** js_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-04-01

# LuCI API: fs

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.fs.html

---



## handleRpcReply(expect, rc) ⇒ `number`
Handle an RPC reply.

**Kind**: global function  
**Throws**:

- `Error` 

| Param | Type |
| --- | --- |
| expect | `object` | 
| rc | `number` | 

## handleCgiIoReply(res) ⇒ `string`
Handle a CGI-IO reply.

**Kind**: global function  
**Throws**:

- `Error` 

| Param | Type |
| --- | --- |
| res | `object` |
