---
title: 'LuCI API: cbi'
module: luci
origin_type: js_source
token_count: 3075
source_file: L1-raw/luci/js_source-api-cbi.md
last_pipeline_run: '2026-03-27T20:02:39.961617+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/cbi.js
source_locator: modules/luci-base/htdocs/luci-static/resources/cbi.js
language: javascript
ai_summary: Implements the CBI declarative form framework for LuCI. Defines Map, Section, TypedSection, TableSection, and over 30 widget classes including Value, Flag, ListValue, MultiValue, DynamicList, and TextValue; CBI maps UCI package sections directly to HTML forms and calls uci.save() on submit, enabling config UIs with minimal JavaScript.
ai_when_to_use: Reference when building a traditional LuCI form-based view against a UCI config file using Map() and TypedSection(); prefer the newer js_source-api-form module for views requiring runtime JSON data or schemas that aren't backed by a flat UCI file.
ai_related_topics:
- LuCI.cbi.Map
- LuCI.cbi.TypedSection
- LuCI.cbi.Value
- LuCI.cbi.Flag
- LuCI.cbi.DynamicList
- LuCI.uci
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/cbi.js](https://github.com/openwrt/luci/blob/unknown/modules/luci-base/htdocs/luci-static/resources/cbi.js)
> **Kind:** js_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-27

# LuCI API: cbi

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.cbi.html

---



## cbi
CBI (Configuration Bindings Interface) helper utilities and DOM helpers.

Provides initialization for CBI UI elements, dependency handling,
validation wiring and miscellaneous helpers used by LuCI forms. Functions
defined here are registered as global `window.*` symbols.

* [cbi](#LuCI.module_cbi)
    * [~s8(bytes, off)](#LuCI.module_cbi..s8) ⇒ `number`
    * [~u16(bytes, off)](#LuCI.module_cbi..u16) ⇒ `number`
    * [~sfh(s)](#LuCI.module_cbi..sfh) ⇒ `string` \| `null`
    * [~trimws(s)](#LuCI.module_cbi..trimws) ⇒ `string`
    * [~_(s, [c])](#LuCI.module_cbi.._) ⇒ `string`
    * [~N_(n, s, p, [c])](#LuCI.module_cbi..N_) ⇒ `string`
    * [~cbi_d_add(field, dep, index)](#LuCI.module_cbi..cbi_d_add)
    * [~cbi_d_checkvalue(target, ref)](#LuCI.module_cbi..cbi_d_checkvalue) ⇒ `boolean`
    * [~cbi_d_check(deps)](#LuCI.module_cbi..cbi_d_check) ⇒ `boolean`
    * [~cbi_d_update()](#LuCI.module_cbi..cbi_d_update)
    * [~cbi_init()](#LuCI.module_cbi..cbi_init)
    * [~cbi_validate_form(form, [errmsg])](#LuCI.module_cbi..cbi_validate_form) ⇒ `boolean`
    * [~cbi_validate_named_section_add(input)](#LuCI.module_cbi..cbi_validate_named_section_add)
    * [~cbi_validate_reset(form)](#LuCI.module_cbi..cbi_validate_reset) ⇒ `boolean`
    * [~cbi_validate_field(cbid, optional, type)](#LuCI.module_cbi..cbi_validate_field)
    * [~cbi_row_swap(elem, up, store)](#LuCI.module_cbi..cbi_row_swap) ⇒ `boolean`
    * [~cbi_tag_last(container)](#LuCI.module_cbi..cbi_tag_last)
    * [~cbi_submit(elem, [name], [value], [action])](#LuCI.module_cbi..cbi_submit) ⇒ `boolean`
    * [~isElem(e)](#LuCI.module_cbi..isElem) ⇒ `HTMLElement` \| `null`
    * [~matchesElem(node, selector)](#LuCI.module_cbi..matchesElem) ⇒ `boolean`
    * [~findParent(node, selector)](#LuCI.module_cbi..findParent) ⇒ `HTMLElement` \| `null`
    * [~E()](#LuCI.module_cbi..E) ⇒ `HTMLElement`
    * [~cbi_dropdown_init(sb)](#LuCI.module_cbi..cbi_dropdown_init) ⇒ `L.ui.Dropdown` \| `undefined`
    * [~cbi_update_table(table, ...data, [placeholder])](#LuCI.module_cbi..cbi_update_table)

### cbi~s8(bytes, off) ⇒ `number`
Read signed 8-bit integer from a byte array at the given offset.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `number` - Signed 8-bit value (returned as unsigned number).  

| Param | Type | Description |
| --- | --- | --- |
| bytes | `Array.<number>` | Byte array. |
| off | `number` | Offset into the array. |

### cbi~u16(bytes, off) ⇒ `number`
Read unsigned 16-bit little-endian integer from a byte array at offset.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `number` - Unsigned 16-bit integer.  

| Param | Type | Description |
| --- | --- | --- |
| bytes | `Array.<number>` | Byte array. |
| off | `number` | Offset into the array. |

### cbi~sfh(s) ⇒ `string` \| `null`
Compute a stable 32-bit-ish string hash used for translation keys.
Encodes UTF-8 surrogate pairs and mixes bytes into a hex hash string.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `string` \| `null` - Hex hash string or null for empty input.  

| Param | Type | Description |
| --- | --- | --- |
| s | `string` \| `null` | Input string. |

### cbi~trimws(s) ⇒ `string`
Trim whitespace and normalise internal whitespace sequences to single spaces.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `string` - Trimmed and normalised string.  

| Param | Type | Description |
| --- | --- | --- |
| s | `\*` | Value to convert to string and trim. |

### cbi~\_(s, [c]) ⇒ `string`
Lookup a translated string for the given message and optional context.
Falls back to the source string when no translation found.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `string` - Translated string or original.  

| Param | Type | Description |
| --- | --- | --- |
| s | `string` | Source string. |
| [c] | `string` | Optional translation context. |

### cbi~N\_(n, s, p, [c]) ⇒ `string`
Plural-aware translation lookup.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `string` - Translated plural form or source string.  

| Param | Type | Description |
| --- | --- | --- |
| n | `number` | Quantity to evaluate plural form. |
| s | `string` | Singular string. |
| p | `string` | Plural string. |
| [c] | `string` | Optional context. |

### cbi~cbi\_d\_add(field, dep, index)
Register a dependency entry for a field.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| field | `HTMLElement` \| `string` | Field element or its id. |
| dep | `Object` | Dependency specification object. |
| index | `number` | Order index of the dependent node. |

### cbi~cbi\_d\_checkvalue(target, ref) ⇒ `boolean`
Check whether an input/select identified by target matches the given reference value.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `boolean` - True if the current value matches ref.  

| Param | Type | Description |
| --- | --- | --- |
| target | `string` | Element id or name to query. |
| ref | `string` | Reference value to compare with. |

### cbi~cbi\_d\_check(deps) ⇒ `boolean`
Evaluate a list of dependency descriptors and return whether any match.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `boolean` - True when dependencies indicate the element should be shown.  

| Param | Type | Description |
| --- | --- | --- |
| deps | `Array.<Object>` | Array of dependency objects to evaluate. |

### cbi~cbi\_d\_update()
Update DOM nodes based on registered dependencies, showing or hiding
nodes and restoring their order when dependency state changes.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

### cbi~cbi\_init()
Initialize CBI widgets and wire up dependency and validation handlers.
Walks the DOM looking for CBI-specific data attributes and replaces
placeholders with interactive widgets.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

### cbi~cbi\_validate\_form(form, [errmsg]) ⇒ `boolean`
Run all validators associated with a form and optionally show an error.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `boolean` - True when form is valid.  

| Param | Type | Description |
| --- | --- | --- |
| form | `HTMLFormElement` | Form element containing validators. |
| [errmsg] | `string` | Message to show when validation fails. |

### cbi~cbi\_validate\_named\_section\_add(input)
Enable/disable a named-section add button depending on input value.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| input | `HTMLInputElement` | Input that contains the new section name. |

### cbi~cbi\_validate\_reset(form) ⇒ `boolean`
Trigger a delayed form validation (used to allow UI state to settle).

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `boolean` - Always returns true.  

| Param | Type | Description |
| --- | --- | --- |
| form | `HTMLFormElement` | Form to validate after a short delay. |

### cbi~cbi\_validate\_field(cbid, optional, type)
Attach a validator to a field and wire validation events.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| cbid | `HTMLElement` \| `string` | Element or element id to validate. |
| optional | `boolean` | Whether an empty value is allowed. |
| type | `string` | Validator type expression (passed to L.validation). |

### cbi~cbi\_row\_swap(elem, up, store) ⇒ `boolean`
Move a table row up or down within a section and update the storage field.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `boolean` - Always returns false to cancel default action.  

| Param | Type | Description |
| --- | --- | --- |
| elem | `HTMLElement` | Element inside the row that triggers the swap. |
| up | `boolean` | If true, move the row up; otherwise move down. |
| store | `string` | ID of the hidden input used to store the order. |

### cbi~cbi\_tag\_last(container)
Mark the last visible value container child with class `cbi-value-last`.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| container | `HTMLElement` | Parent container element. |

### cbi~cbi\_submit(elem, [name], [value], [action]) ⇒ `boolean`
Submit a form, optionally adding a hidden input to pass a name/value pair.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `boolean` - True on successful submit, false when no form found.  

| Param | Type | Description |
| --- | --- | --- |
| elem | `HTMLElement` | Element inside the form or an element with a form. |
| [name] | `string` | Name of hidden input to include, if any. |
| [value] | `string` | Value for the hidden input (defaults to '1'). |
| [action] | `string` | Optional form action URL override. |

### cbi~isElem(e) ⇒ `HTMLElement` \| `null`
Return the element for input which may be an element or an id.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| e | `Element` \| `string` | Element or id. |

### cbi~matchesElem(node, selector) ⇒ `boolean`
Test whether node matches a CSS selector.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| node | `Node` | Node to test. |
| selector | `string` | CSS selector. |

### cbi~findParent(node, selector) ⇒ `HTMLElement` \| `null`
Find the parent matching selector from node upwards.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| node | `Node` | Starting node. |
| selector | `string` | CSS selector to match ancestor. |

### cbi~E() ⇒ `HTMLElement`
Create DOM elements using [L.dom.create](L.dom.create) helper (convenience wrapper).

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

### cbi~cbi\_dropdown\_init(sb) ⇒ `L.ui.Dropdown` \| `undefined`
Initialize a dropdown element into an [L.ui.Dropdown](L.ui.Dropdown) instance and bind it.
If already bound, this is a no-op.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  
**Returns**: `L.ui.Dropdown` \| `undefined` - Dropdown instance or undefined when already bound.  

| Param | Type | Description |
| --- | --- | --- |
| sb | `HTMLElement` | The select element to convert. |

### cbi~cbi\_update\_table(table, ...data, [placeholder])
Update or initialize a table UI widget with new data.

**Kind**: inner method of [`cbi`](#LuCI.module_cbi)  

| Param | Type | Description |
| --- | --- | --- |
| table | `HTMLElement` \| `string` | Table element or selector. |
| ...data | `Array.<Node>` | Data to update the table with. |
| [placeholder] | `string` | Placeholder text when empty. |
