# AGENTS.md — luci module

## Scope
Modern JavaScript LuCI framework for building OpenWrt web interfaces.

## Era Warning
Do NOT generate Lua CBI templates. The current LuCI framework uses JavaScript ES modules.
Legacy patterns like `require("luci.model.cbi")` are pre-2019 and will not work on modern OpenWrt.

## Start Here
- `map.md` → structural overview of all API surfaces
- `chunked-reference/js_source-api-form.md` → primary form framework (use this, not CBI)
- `chunked-reference/js_source-api-uci.md` → UCI config bindings

## Avoid
- `js_source-api-cbi.md` is a legacy compatibility layer. Reference it only for maintaining existing Lua views.
