---
module: luci
total_token_count: 19723
section_count: 10
is_monolithic: true
generated: '2026-03-20T04:40:19.476369+00:00'
---

# luci Complete Reference

> **Contains:** 10 documents concatenated
> **Tokens:** ~19723 (cl100k_base)

---

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

---

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

---

# LuCI API: luci

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.html

---



## LuCI
**Kind**: global class  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| env | `object` | The environment settings to use for the LuCI runtime. |

* [LuCI](#LuCI)
    * [new LuCI(window, document, undefined)](#new_LuCI_new)
    * _instance_
        * [.env](#LuCI+env)
        * [.naturalCompare](#LuCI+naturalCompare) ⇒ `number`
        * ~~[.dom](#LuCI+dom)~~
        * ~~[.view](#LuCI+view)~~
        * ~~[.Poll](#LuCI+Poll)~~
        * ~~[.Request](#LuCI+Request)~~
        * ~~[.Class](#LuCI+Class)~~
        * [.raise([type], [fmt], [...args])](#LuCI+raise)
        * [.error([type], [fmt], [...args])](#LuCI+error)
        * [.bind(fn, self, [...args])](#LuCI+bind) ⇒ `function`
        * [.require(name, [from])](#LuCI+require) ⇒ [`Promise.<baseclass>`](#LuCI.baseclass)
        * [.hasSystemFeature(feature, [subfeature])](#LuCI+hasSystemFeature) ⇒ `boolean` \| `null`
        * [.fspath([...parts])](#LuCI+fspath) ⇒ `string`
        * [.path([prefix], [...parts])](#LuCI+path) ⇒ `string`
        * [.url([...parts])](#LuCI+url) ⇒ `string`
        * [.resource([...parts])](#LuCI+resource) ⇒ `string`
        * [.media([...parts])](#LuCI+media) ⇒ `string`
        * [.location()](#LuCI+location) ⇒ `string`
        * [.isObject([val])](#LuCI+isObject) ⇒ `boolean`
        * [.isArguments([val])](#LuCI+isArguments) ⇒ `boolean`
        * [.sortedKeys(obj, [key], [sortmode])](#LuCI+sortedKeys) ⇒ `Array.<string>`
        * [.sortedArray(val)](#LuCI+sortedArray) ⇒ `Array.<\*>`
        * [.toArray(val)](#LuCI+toArray) ⇒ `Array.<\*>`
        * [.resolveDefault(value, defvalue)](#LuCI+resolveDefault) ⇒ `Promise.<\*>`
        * ~~[.get(url, [args], cb)](#LuCI+get) ⇒ `Promise.<null>`~~
        * ~~[.post(url, [args], cb)](#LuCI+post) ⇒ `Promise.<null>`~~
        * ~~[.poll(interval, url, [args], cb, [post])](#LuCI+poll) ⇒ `function`~~
        * [.hasViewPermission()](#LuCI+hasViewPermission) ⇒ `boolean` \| `null`
        * ~~[.stop(entry)](#LuCI+stop) ⇒ `boolean`~~
        * ~~[.halt()](#LuCI+halt) ⇒ `boolean`~~
        * ~~[.run()](#LuCI+run) ⇒ `boolean`~~
    * _static_
        * [.baseclass](#LuCI.baseclass)
            * _instance_
                * [.varargs(args, offset, [...extra_args])](#LuCI.baseclass+varargs) ⇒ `Array.<\*>`
                * [.super(key, [callArgs])](#LuCI.baseclass+super) ⇒ `\*` \| `null`
                * [.toString()](#LuCI.baseclass+toString) ⇒ `string`
            * _static_
                * [.extend(properties)](#LuCI.baseclass.extend) ⇒ [`baseclass`](#LuCI.baseclass)
                * [.singleton(properties, ...new_args)](#LuCI.baseclass.singleton) ⇒ [`baseclass`](#LuCI.baseclass)
                * [.instantiate(args)](#LuCI.baseclass.instantiate) ⇒ [`baseclass`](#LuCI.baseclass)
                * [.isSubclass(classValue)](#LuCI.baseclass.isSubclass) ⇒ `boolean`
        * [.headers](#LuCI.headers)
            * [.has(name)](#LuCI.headers+has) ⇒ `boolean`
            * [.get(name)](#LuCI.headers+get) ⇒ `string` \| `null`
        * [.response](#LuCI.response)
            * [.ok](#LuCI.response+ok) : `boolean`
            * [.status](#LuCI.response+status) : `number`
            * [.statusText](#LuCI.response+statusText) : `string`
            * [.headers](#LuCI.response+headers) : [`headers`](#LuCI.headers)
            * [.duration](#LuCI.response+duration) : `number`
            * [.url](#LuCI.response+url) : `string`
            * [.clone([content])](#LuCI.response+clone) ⇒ [`response`](#LuCI.response)
            * [.json()](#LuCI.response+json) ⇒ `\*`
            * [.text()](#LuCI.response+text) ⇒ `string`
            * [.blob()](#LuCI.response+blob) ⇒ `Blob`
        * [.request](#LuCI.request)
            * _instance_
                * [.expandURL(url)](#LuCI.request+expandURL) ⇒ `string`
                * [.request(target, [options])](#LuCI.request+request) ⇒ [`Promise.<response>`](#LuCI.response)
                * [.handleReadyStateChange(resolveFn, rejectFn, [ev])](#LuCI.request+handleReadyStateChange) ⇒ `void`
                * [.get(url, [options])](#LuCI.request+get) ⇒ [`Promise.<response>`](#LuCI.response)
                * [.post(url, [data], [options])](#LuCI.request+post) ⇒ [`Promise.<response>`](#LuCI.response)
                * [.addInterceptor(interceptorFn)](#LuCI.request+addInterceptor) ⇒ [`interceptorFn`](#LuCI.request.interceptorFn)
                * [.removeInterceptor(interceptorFn)](#LuCI.request+removeInterceptor) ⇒ `boolean`
            * _static_
                * [.poll](#LuCI.request.poll)
                    * _instance_
                        * [.add(interval, url, [options], [callback])](#LuCI.request.poll+add) ⇒ `function`
                        * [.remove(entry)](#LuCI.request.poll+remove) ⇒ `boolean`
                        * [.start()](#LuCI.request.poll+start) ⇒ `boolean`
                        * [.stop()](#LuCI.request.poll+stop) ⇒ `boolean`
                        * [.active()](#LuCI.request.poll+active) ⇒ `boolean`
                    * _inner_
                        * [~callbackFn](#LuCI.request.poll..callbackFn) : `function`
                * [.RequestOptions](#LuCI.request.RequestOptions) : `Object`
                * [.interceptorFn](#LuCI.request.interceptorFn) : `function`
        * [.poll](#LuCI.poll)
            * [.add(fn, interval)](#LuCI.poll+add) ⇒ `boolean`
            * [.remove(fn)](#LuCI.poll+remove) ⇒ `boolean`
            * [.start()](#LuCI.poll+start) ⇒ `boolean`
            * [.stop()](#LuCI.poll+stop) ⇒ `boolean`
            * [.active()](#LuCI.poll+active) ⇒ `boolean`
        * [.dom](#LuCI.dom)
            * _instance_
                * [.elem(e)](#LuCI.dom+elem) ⇒ `boolean`
                * [.parse(s)](#LuCI.dom+parse) ⇒ `Node`
                * [.matches(node, [selector])](#LuCI.dom+matches) ⇒ `boolean`
                * [.parent(node, [selector])](#LuCI.dom+parent) ⇒ `Node` \| `null`
                * [.append(node, [children])](#LuCI.dom+append) ⇒ `Node` \| `null`
                * [.content(node, [children])](#LuCI.dom+content) ⇒ `Node` \| `null`
                * [.attr(node, key, [val])](#LuCI.dom+attr) ⇒ `null`
                * [.create(html, [attr], [data])](#LuCI.dom+create) ⇒ `Node`
                * [.data(node, [key], [val])](#LuCI.dom+data) ⇒ `\*`
                * [.bindClassInstance(node, inst)](#LuCI.dom+bindClassInstance) ⇒ `Class`
                * [.findClassInstance(node)](#LuCI.dom+findClassInstance) ⇒ `Class` \| `null`
                * [.callClassMethod(node, method, ...args)](#LuCI.dom+callClassMethod) ⇒ `\*` \| `null`
                * [.isEmpty(node, [ignoreFn])](#LuCI.dom+isEmpty) ⇒ `boolean`
            * _inner_
                * [~ignoreCallbackFn](#LuCI.dom..ignoreCallbackFn) ⇒ `boolean`
        * [.session](#LuCI.session)
            * [.getID()](#LuCI.session+getID) ⇒ `string`
            * [.getToken()](#LuCI.session+getToken) ⇒ `string` \| `null`
            * [.getLocalData([key])](#LuCI.session+getLocalData) ⇒ `\*`
            * [.setLocalData(key, value)](#LuCI.session+setLocalData) ⇒ `boolean`
        * [.view](#LuCI.view)
            * *[.load()](#LuCI.view+load) ⇒ `\*` \| `Promise.<\*>`*
            * *[.render(load_results)](#LuCI.view+render) ⇒ `Node` \| `Promise.<Node>`*
            * [.handleSave(ev)](#LuCI.view+handleSave) ⇒ `\*` \| `Promise.<\*>`
            * [.handleSaveApply(ev, mode)](#LuCI.view+handleSaveApply) ⇒ `\*` \| `Promise.<\*>`
            * [.handleReset(ev)](#LuCI.view+handleReset) ⇒ `\*` \| `Promise.<\*>`
            * [.addFooter()](#LuCI.view+addFooter) ⇒ `DocumentFragment`
        * ~~[.xhr](#LuCI.xhr)~~
            * ~~[.get(url, [data], [callback], [timeout])](#LuCI.xhr+get) ⇒ `Promise.<null>`~~
            * ~~[.post(url, [data], [callback], [timeout])](#LuCI.xhr+post) ⇒ `Promise.<null>`~~
            * ~~[.cancel()](#LuCI.xhr+cancel)~~
            * ~~[.busy()](#LuCI.xhr+busy) ⇒ `boolean`~~
            * ~~[.abort()](#LuCI.xhr+abort)~~
            * ~~[.send_form()](#LuCI.xhr+send_form)~~
        * [.requestCallbackFn](#LuCI.requestCallbackFn) : `function`

### new LuCI(window, document, undefined)
This is the LuCI base class. It is automatically instantiated and
accessible using the global `L` variable.

| Param | Type | Description |
| --- | --- | --- |
| window | `Window` | The browser global `window` object. |
| document | `Document` | The DOM `document` root for the current page. |
| undefined | `undefined` | Local `undefined` slot (prevents shadowing and ensures `undefined` is the real undefined value). |

### luCI.env
The `env` object holds environment settings used by LuCI, such
as request timeouts, base URLs, etc.

**Kind**: instance property of [`LuCI`](#LuCI)  

### luCI.naturalCompare ⇒ `number`
Compares two values numerically and returns -1, 0, or 1 depending
on whether the first value is smaller, equal to, or larger than the
second one respectively.

This function is meant to be used as a comparator function for
Array.sort().

**Kind**: instance property of [`LuCI`](#LuCI)  
**Returns**: `number` - Returns -1 if the first value is smaller than the second one.
Returns 0 if both values are equal.
Returns 1 if the first value is larger than the second one.  

| Param | Type | Description |
| --- | --- | --- |
| a | `\*` | The first value |
| b | `\*` | The second value. |

### ~~luCI.dom~~
***Deprecated***

Legacy `L.dom` class alias. New view code should use `'require dom';`
to request the `LuCI.dom` class.

**Kind**: instance property of [`LuCI`](#LuCI)  

### ~~luCI.view~~
***Deprecated***

Legacy `L.view` class alias. New view code should use `'require view';`
to request the `LuCI.view` class.

**Kind**: instance property of [`LuCI`](#LuCI)  

### ~~luCI.Poll~~
***Deprecated***

Legacy `L.Poll` class alias. New view code should use `'require poll';`
to request the `LuCI.poll` class.

**Kind**: instance property of [`LuCI`](#LuCI)  

### ~~luCI.Request~~
***Deprecated***

Legacy `L.Request` class alias. New view code should use `'require request';`
to request the `LuCI.request` class.

**Kind**: instance property of [`LuCI`](#LuCI)  

### ~~luCI.Class~~
***Deprecated***

Legacy `L.Class` class alias. New view code should use `'require baseclass';`
to request the `LuCI.baseclass` class.

**Kind**: instance property of [`LuCI`](#LuCI)  

### luCI.raise([type], [fmt], [...args])
Captures the current stack trace and throws an error of the
specified type as a new exception. Also logs the exception as
an error to the debug console if it is available.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Throws**:

- `Error` Throws the created error object with the captured stack trace
appended to the message and the type set to the given type
argument or copied from the given error instance.

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [type] | `Error` \| `string` | `Error` | Either a string specifying the type of the error to throw or an existing `Error` instance to copy. |
| [fmt] | `string` | `"Unspecified error"` | A format string which is used to form the error message, together with all subsequent optional arguments. |
| [...args] | `\*` |  | Zero or more variable arguments to the supplied format string. |

### luCI.error([type], [fmt], [...args])
A wrapper around [raise()](#LuCI+raise) which also renders
the error either as modal overlay when `ui.js` is already loaded
or directly into the view body.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Throws**:

- `Error` Throws the created error object with the captured stack trace
appended to the message and the type set to the given type
argument or copied from the given error instance.

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [type] | `Error` \| `string` | `Error` | Either a string specifying the type of the error to throw or an existing `Error` instance to copy. |
| [fmt] | `string` | `"Unspecified error"` | A format string which is used to form the error message, together with all subsequent optional arguments. |
| [...args] | `\*` |  | Zero or more variable arguments to the supplied format string. |

### luCI.bind(fn, self, [...args]) ⇒ `function`
Return a bound function using the given `self` as `this` context
and any further arguments as parameters to the bound function.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `function` - Returns the bound function.  

| Param | Type | Description |
| --- | --- | --- |
| fn | `function` | The function to bind. |
| self | `\*` | The value to bind as `this` context to the specified function. |
| [...args] | `\*` | Zero or more variable arguments which are bound to the function as parameters. |

### luCI.require(name, [from]) ⇒ [`Promise.<baseclass>`](#LuCI.baseclass)
Load an additional LuCI JavaScript class and its dependencies,
instantiate it and return the resulting class instance. Each
class is only loaded once. Subsequent attempts to load the same
class will return the already instantiated class.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: [`Promise.<baseclass>`](#LuCI.baseclass) - Returns the instantiated class.  
**Throws**:

- `DependencyError` Throws a `DependencyError` when the class to load includes
circular dependencies.
- `NetworkError` Throws `NetworkError` when the underlying [request](#LuCI.request)
call failed.
- `SyntaxError` Throws `SyntaxError` when the loaded class file code cannot
be interpreted by `eval`.
- `TypeError` Throws `TypeError` when the class file could be loaded and
interpreted, but when invoking its code did not yield a valid
class instance.

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| name | `string` |  | The name of the class to load in dotted notation. Dots will be replaced by spaces and joined with the runtime-determined base URL of LuCI.js to form an absolute URL to load the class file from. |
| [from] | `Array.<string>` | `[]` | Optional dependency chain used during dependency resolution. This array contains the sequence of class names already being resolved (the caller stack). It is used to detect circular dependencies — if `name` appears in `from` a `DependencyError` is thrown. |

### luCI.hasSystemFeature(feature, [subfeature]) ⇒ `boolean` \| `null`
Test whether a particular system feature is available, such as
hostapd SAE support or an installed firewall. The features are
queried once at the beginning of the LuCI session and cached in
`SessionStorage` throughout the lifetime of the associated tab or
browser window.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `boolean` \| `null` - Return `true` if the queried feature (and sub-feature) is available
or `false` if the requested feature isn't present or known.
Return `null` when a sub-feature was queried for a feature which
has no sub-features.  

| Param | Type | Description |
| --- | --- | --- |
| feature | `string` | The feature to test. For a detailed list of known feature flags, see `/modules/luci-base/root/usr/share/rpcd/ucode/luci`. |
| [subfeature] | `string` | Some feature classes like `hostapd` provide sub-feature flags, such as `sae` or `11w` support. The `subfeature` argument can be used to query these. |

### luCI.fspath([...parts]) ⇒ `string`
Construct an absolute filesystem path relative to the server
document root.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `string` - Return the joined path.  

| Param | Type | Description |
| --- | --- | --- |
| [...parts] | `string` | An array of parts to join into a path. |

### luCI.path([prefix], [...parts]) ⇒ `string`
Construct a relative URL path from the given prefix and parts.
The resulting URL is guaranteed to contain only the characters
`a-z`, `A-Z`, `0-9`, `_`, `.`, `%`, `,`, `;`, and `-` as well
as `/` for the path separator. Suffixing '?x=y&foo=bar' URI
parameters also limited to the aforementioned characters is
permissible.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `string` - Return the joined URL path.  

| Param | Type | Description |
| --- | --- | --- |
| [prefix] | `string` | The prefix to join the given parts with. If the `prefix` is omitted, it defaults to an empty string. |
| [...parts] | `string` | An array of parts to join into a URL path. Parts may contain slashes and any of the other characters mentioned above. |

### luCI.url([...parts]) ⇒ `string`
Construct a URL with a path relative to the script path of the server
side LuCI application (usually `/cgi-bin/luci`).

The resulting URL is guaranteed to contain only the characters
`a-z`, `A-Z`, `0-9`, `_`, `.`, `%`, `,`, `;`, and `-` as well
as `/` for the path separator. Suffixing '?x=y&foo=bar' URI
parameters also limited to the aforementioned characters is
permissible.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `string` - Returns the resulting URL path.  

| Param | Type | Description |
| --- | --- | --- |
| [...parts] | `string` | An array of parts to join into a URL path. Parts may contain slashes and any of the other characters mentioned above. |

### luCI.resource([...parts]) ⇒ `string`
Construct a URL path relative to the global static resource path
of the LuCI ui (usually `/luci-static/resources`).

The resulting URL is guaranteed to contain only the characters
`a-z`, `A-Z`, `0-9`, `_`, `.`, `%`, `,`, `;`, and `-` as well
as `/` for the path separator. Suffixing '?x=y&foo=bar' URI
parameters also limited to the aforementioned characters is
permissible.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `string` - Returns the resulting URL path.  

| Param | Type | Description |
| --- | --- | --- |
| [...parts] | `string` | An array of parts to join into a URL path. Parts may contain slashes and any of the other characters mentioned above. |

### luCI.media([...parts]) ⇒ `string`
Construct a URL path relative to the media resource path of the
LuCI ui (usually `/luci-static/$theme_name`).

The resulting URL is guaranteed to contain only the characters
`a-z`, `A-Z`, `0-9`, `_`, `.`, `%`, `,`, `;`, and `-` as well
as `/` for the path separator. Suffixing '?x=y&foo=bar' URI
parameters also limited to the aforementioned characters is
permissible.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `string` - Returns the resulting URL path.  

| Param | Type | Description |
| --- | --- | --- |
| [...parts] | `string` | An array of parts to join into a URL path. Parts may contain slashes and any of the other characters mentioned above. |

### luCI.location() ⇒ `string`
Return the complete URL path to the current view.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `string` - Returns the URL path to the current view.  

### luCI.isObject([val]) ⇒ `boolean`
Tests whether the passed argument is a JavaScript object.
This function is meant to be an object counterpart to the
standard `Array.isArray()` function.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `boolean` - Returns `true` if the given value is of a type object and
not `null`, else returns `false`.  

| Param | Type | Description |
| --- | --- | --- |
| [val] | `\*` | The value to test |

### luCI.isArguments([val]) ⇒ `boolean`
Tests whether the passed argument is a function arguments object.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `boolean` - Returns `true` if the given value is a function arguments object,
else returns `false`.  

| Param | Type | Description |
| --- | --- | --- |
| [val] | `\*` | The value to test |

### luCI.sortedKeys(obj, [key], [sortmode]) ⇒ `Array.<string>`
Return an array of sorted object keys, optionally sorted by
a different key or a different sorting mode.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `Array.<string>` - Returns an array containing the sorted keys of the given object.  

| Param | Type | Description |
| --- | --- | --- |
| obj | `object` | The object to extract the keys from. If the given value is not an object, the function will return an empty array. |
| [key] | `string` \| `null` | Specifies the key to order by. This is mainly useful for nested objects of objects or objects of arrays when sorting shall not be performed by the primary object keys but by some other key pointing to a value within the nested values. |
| [sortmode] | `"addr"` \| `"num"` | Can be either `addr` or `num` to override the natural lexicographic sorting with a sorting suitable for IP/MAC style addresses or numeric values respectively. |

### luCI.sortedArray(val) ⇒ `Array.<\*>`
Converts the given value to an array using toArray() if needed,
performs a numerical sort using naturalCompare() and returns the
result. If the input already is an array, no copy is being made
and the sorting is performed in-place.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `Array.<\*>` - Returns the resulting, numerically sorted array.  
**See**

- toArray
- naturalCompare

| Param | Type | Description |
| --- | --- | --- |
| val | `\*` | The input value to sort (and convert to an array if needed). |

### luCI.toArray(val) ⇒ `Array.<\*>`
Converts the given value to an array. If the given value is of
type array, it is returned as-is, values of a type object are
returned as one-element array containing the object, empty
strings and `null` values are returned as an empty array, all other
values are converted using `String()`, trimmed, split on white
space and returned as an array.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `Array.<\*>` - Returns the resulting array.  

| Param | Type | Description |
| --- | --- | --- |
| val | `\*` | The value to convert into an array. |

### luCI.resolveDefault(value, defvalue) ⇒ `Promise.<\*>`
Returns a promise resolving with either the given value or with
the given default in case the input value is a rejecting promise.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `Promise.<\*>` - Returns a new promise resolving either to the given input value or
to the given default value on error.  

| Param | Type | Description |
| --- | --- | --- |
| value | `\*` | The value to resolve the promise with. |
| defvalue | `\*` | The default value to resolve the promise with in case the given input value is a rejecting promise. |

### ~~luCI.get(url, [args], cb) ⇒ `Promise.<null>`~~
***Deprecated***

Issues a GET request to the given url and invokes the specified
callback function. The function is a wrapper around
[Request.request()](#LuCI.request+request).

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `Promise.<null>` - Returns a promise resolving to `null` when concluded.  

| Param | Type | Description |
| --- | --- | --- |
| url | `string` | The URL to request. |
| [args] | `Object.<string, string>` | Additional query string arguments to append to the URL. |
| cb | [`requestCallbackFn`](#LuCI.requestCallbackFn) | The callback function to invoke when the request finishes. |

### ~~luCI.post(url, [args], cb) ⇒ `Promise.<null>`~~
***Deprecated***

Issues a POST request to the given url and invokes the specified
callback function. The function is a wrapper around
[Request.request()](#LuCI.request+request). The request is
sent using `application/x-www-form-urlencoded` encoding and will
contain a field `token` with the current value of `LuCI.env.token`
by default.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `Promise.<null>` - Returns a promise resolving to `null` when concluded.  

| Param | Type | Description |
| --- | --- | --- |
| url | `string` | The URL to request. |
| [args] | `Object.<string, string>` | Additional post arguments to append to the request body. |
| cb | [`requestCallbackFn`](#LuCI.requestCallbackFn) | The callback function to invoke when the request finishes. |

### ~~luCI.poll(interval, url, [args], cb, [post]) ⇒ `function`~~
***Deprecated***

Register a polling [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) request that invokes the specified
callback function. The function is a wrapper around
[Request.poll.add()](#LuCI.request.poll+add).

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `function` - Returns the internally created function that has been passed to
[Request.poll.add()](#LuCI.request.poll+add). This value can
be passed to [Poll.remove()](LuCI.poll.remove) to remove the
polling request.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| interval | `number` |  | The poll interval to use. If set to a value less than or equal to `0`, it will default to the global poll interval configured in `LuCI.env.pollinterval`. |
| url | `string` |  | The URL to request. |
| [args] | `Object.<string, string>` |  | Specifies additional arguments for the request. For GET requests, the arguments are appended to the URL as query string, for POST requests, they'll be added to the request body. |
| cb | [`requestCallbackFn`](#LuCI.requestCallbackFn) |  | The callback function to invoke whenever a request finishes. |
| [post] | `boolean` | `false` | When set to `false` or not specified, poll requests will be made using the GET method. When set to `true`, POST requests will be issued. In the case of POST requests, the request body will contain an argument `token` with the current value of `LuCI.env.token` by default, regardless of the parameters specified with `args`. |

### luCI.hasViewPermission() ⇒ `boolean` \| `null`
Check whether a view has sufficient permissions.

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `boolean` \| `null` - Returns `null` if the current session has no permission at all to
load resources required by the view. Returns `false` if readonly
permissions are granted or `true` if at least one required ACL
group is granted with write permissions.  

### ~~luCI.stop(entry) ⇒ `boolean`~~
***Deprecated***

Deprecated wrapper around [Poll.remove()](LuCI.poll.remove).

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `boolean` - Returns `true` when the function has been removed or `false` if
it could not be found.  

| Param | Type | Description |
| --- | --- | --- |
| entry | `function` | The polling function to remove. |

### ~~luCI.halt() ⇒ `boolean`~~
***Deprecated***

Deprecated wrapper around [Poll.stop()](LuCI.poll.stop).

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `boolean` - Returns `true` when the polling loop has been stopped or `false`
when it didn't run to begin with.  

### ~~luCI.run() ⇒ `boolean`~~
***Deprecated***

Deprecated wrapper around [Poll.start()](LuCI.poll.start).

**Kind**: instance method of [`LuCI`](#LuCI)  
**Returns**: `boolean` - Returns `true` when the polling loop has been started or `false`
when it was already running.  

### LuCI.baseclass
`LuCI.baseclass` is the abstract base class all LuCI classes inherit from.

It provides a simple means to create subclasses of given classes and
implements prototypal inheritance.

**Kind**: static class of [`LuCI`](#LuCI)  

* [.baseclass](#LuCI.baseclass)
    * _instance_
        * [.varargs(args, offset, [...extra_args])](#LuCI.baseclass+varargs) ⇒ `Array.<\*>`
        * [.super(key, [callArgs])](#LuCI.baseclass+super) ⇒ `\*` \| `null`
        * [.toString()](#LuCI.baseclass+toString) ⇒ `string`
    * _static_
        * [.extend(properties)](#LuCI.baseclass.extend) ⇒ [`baseclass`](#LuCI.baseclass)
        * [.singleton(properties, ...new_args)](#LuCI.baseclass.singleton) ⇒ [`baseclass`](#LuCI.baseclass)
        * [.instantiate(args)](#LuCI.baseclass.instantiate) ⇒ [`baseclass`](#LuCI.baseclass)
        * [.isSubclass(classValue)](#LuCI.baseclass.isSubclass) ⇒ `boolean`

#### baseclass.varargs(args, offset, [...extra_args]) ⇒ `Array.<\*>`
Extract all values from the given argument array beginning from
`offset` and prepend any further given optional parameters to
the beginning of the resulting array copy.

**Kind**: instance method of [`baseclass`](#LuCI.baseclass)  
**Returns**: `Array.<\*>` - Returns a new array consisting of the optional extra arguments
and the values extracted from the `args` array beginning with
`offset`.  

| Param | Type | Description |
| --- | --- | --- |
| args | `Array.<\*>` | The array to extract the values from. |
| offset | `number` | The offset from which to extract the values. An offset of `0` would copy all values till the end. |
| [...extra_args] | `\*` | Extra arguments to add to prepend to the resulting array. |

#### baseclass.super(key, [callArgs]) ⇒ `\*` \| `null`
Walks up the parent class chain and looks for a class member
called `key` in any of the parent classes this class inherits
from. Returns the member value of the superclass or calls the
member as a function and returns its return value when the
optional `callArgs` array is given.

This function has two signatures and is sensitive to the
amount of arguments passed to it:
 - `super('key')` -
	Returns the value of `key` when found within one of the
	parent classes.
 - `super('key', ['arg1', 'arg2'])` -
	Calls the `key()` method with parameters `arg1` and `arg2`
	when found within one of the parent classes.

**Kind**: instance method of [`baseclass`](#LuCI.baseclass)  
**Returns**: `\*` \| `null` - Returns the value of the found member or the return value of
the call to the found method. Returns `null` when no member
was found in the parent class chain or when the call to the
superclass method returned `null`.  
**Throws**:

- `ReferenceError` Throws a `ReferenceError` when `callArgs` are specified and
the found member named by `key` is not a function value.

| Param | Type | Description |
| --- | --- | --- |
| key | `string` | The name of the superclass member to retrieve. |
| [callArgs] | `\*` \| `Array.<\*>` | Arguments to pass when invoking the superclass method. May be  either an argument array or variadic arguments. |

#### baseclass.toString() ⇒ `string`
Returns a string representation of this class.

**Kind**: instance method of [`baseclass`](#LuCI.baseclass)  
**Returns**: `string` - Returns a string representation of this class containing the
constructor functions `displayName` and describing the class
members and their respective types.  

#### baseclass.extend(properties) ⇒ [`baseclass`](#LuCI.baseclass)
Extends this base class with the properties described in
`properties` and returns a new subclassed Class instance

**Kind**: static method of [`baseclass`](#LuCI.baseclass)  
**Returns**: [`baseclass`](#LuCI.baseclass) - Returns a new LuCI.baseclass subclassed from this class, extended
by the given properties and with its prototype set to this base
class to enable inheritance. The resulting value represents a
class constructor and can be instantiated with `new`.  
**this**: `{LuCI.baseclass}`  

| Param | Type | Description |
| --- | --- | --- |
| properties | `Object.<string, \*>` | An object describing the properties to add to the new subclass. |

#### baseclass.singleton(properties, ...new_args) ⇒ [`baseclass`](#LuCI.baseclass)
Extends this base class with the properties described in
`properties`, instantiates the resulting subclass using
the given arguments passed to this function
and returns the resulting subclassed Class instance.

This function serves as a convenience shortcut for
[Class.extend()](#LuCI.baseclass.extend) and subsequent
`new`.

**Kind**: static method of [`baseclass`](#LuCI.baseclass)  
**Returns**: [`baseclass`](#LuCI.baseclass) - Returns a new LuCI.baseclass instance extended by the given
properties with its prototype set to this base class to
enable inheritance.  

| Param | Type | Description |
| --- | --- | --- |
| properties | `Object.<string, \*>` | An object describing the properties to add to the new subclass. |
| ...new_args | `\*` | Arguments forwarded to the constructor of the generated subclass. |

#### baseclass.instantiate(args) ⇒ [`baseclass`](#LuCI.baseclass)
Calls the class constructor using `new` with the given argument
array being passed as variadic parameters to the constructor.

**Kind**: static method of [`baseclass`](#LuCI.baseclass)  
**Returns**: [`baseclass`](#LuCI.baseclass) - Returns a new LuCI.baseclass instance extended by the given
properties with its prototype set to this base class to
enable inheritance.  

| Param | Type | Description |
| --- | --- | --- |
| args | `Array.<\*>` | An array of arbitrary values which will be passed as arguments to the constructor function. |

#### baseclass.isSubclass(classValue) ⇒ `boolean`
Checks whether the given class value is a subclass of this class.

**Kind**: static method of [`baseclass`](#LuCI.baseclass)  
**Returns**: `boolean` - Returns `true` when the given `classValue` is a subclass of this
class or `false` if the given value is not a valid class or not
a subclass of this class.  

| Param | Type | Description |
| --- | --- | --- |
| classValue | [`baseclass`](#LuCI.baseclass) | The class object to test. |

### LuCI.headers
The `Headers` class is an internal utility class exposed in [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md)
response objects using the `response.headers` property.

**Kind**: static class of [`LuCI`](#LuCI)  

* [.headers](#LuCI.headers)
    * [.has(name)](#LuCI.headers+has) ⇒ `boolean`
    * [.get(name)](#LuCI.headers+get) ⇒ `string` \| `null`

#### headers.has(name) ⇒ `boolean`
Checks whether the given header name is present.
Note: Header-Names are case-insensitive.

**Kind**: instance method of [`headers`](#LuCI.headers)  
**Returns**: `boolean` - Returns `true` if the header name is present, `false` otherwise  

| Param | Type | Description |
| --- | --- | --- |
| name | `string` | The header name to check |

#### headers.get(name) ⇒ `string` \| `null`
Returns the value of the given header name.
Note: Header-Names are case-insensitive.

**Kind**: instance method of [`headers`](#LuCI.headers)  
**Returns**: `string` \| `null` - The value of the given header name or `null` if the header isn't present.  

| Param | Type | Description |
| --- | --- | --- |
| name | `string` | The header name to read |

### LuCI.response
The `Response` class is an internal utility class representing [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) responses.

**Kind**: static class of [`LuCI`](#LuCI)  

* [.response](#LuCI.response)
    * [.ok](#LuCI.response+ok) : `boolean`
    * [.status](#LuCI.response+status) : `number`
    * [.statusText](#LuCI.response+statusText) : `string`
    * [.headers](#LuCI.response+headers) : [`headers`](#LuCI.headers)
    * [.duration](#LuCI.response+duration) : `number`
    * [.url](#LuCI.response+url) : `string`
    * [.clone([content])](#LuCI.response+clone) ⇒ [`response`](#LuCI.response)
    * [.json()](#LuCI.response+json) ⇒ `\*`
    * [.text()](#LuCI.response+text) ⇒ `string`
    * [.blob()](#LuCI.response+blob) ⇒ `Blob`

#### response.ok : `boolean`
Describes whether the response is successful (status codes `200..299`) or not

**Kind**: instance property of [`response`](#LuCI.response)  

#### response.status : `number`
The numeric [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) status code of the response

**Kind**: instance property of [`response`](#LuCI.response)  

#### response.statusText : `string`
The [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) status description message of the response

**Kind**: instance property of [`response`](#LuCI.response)  

#### response.headers : [`headers`](#LuCI.headers)
The [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) headers of the response

**Kind**: instance property of [`response`](#LuCI.response)  

#### response.duration : `number`
The total duration of the [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) request in milliseconds

**Kind**: instance property of [`response`](#LuCI.response)  

#### response.url : `string`
The final URL of the request, i.e. after following redirects.

**Kind**: instance property of [`response`](#LuCI.response)  

#### response.clone([content]) ⇒ [`response`](#LuCI.response)
Clones the given response object, optionally overriding the content
of the cloned instance.

**Kind**: instance method of [`response`](#LuCI.response)  
**Returns**: [`response`](#LuCI.response) - The cloned `Response` instance.  

| Param | Type | Description |
| --- | --- | --- |
| [content] | `\*` | Override the content of the cloned response. Object values will be treated as JSON response data, all other types will be converted using `String()` and treated as response text. |

#### response.json() ⇒ `\*`
Access the response content as JSON data.

**Kind**: instance method of [`response`](#LuCI.response)  
**Returns**: `\*` - The parsed JSON data.  
**Throws**:

- `SyntaxError` Throws `SyntaxError` if the content isn't valid JSON.

#### response.text() ⇒ `string`
Access the response content as string.

**Kind**: instance method of [`response`](#LuCI.response)  
**Returns**: `string` - The response content.  

#### response.blob() ⇒ `Blob`
Access the response content as blob.

**Kind**: instance method of [`response`](#LuCI.response)  
**Returns**: `Blob` - The response content as blob.  

### LuCI.request
The `Request` class allows initiating [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) requests and provides utilities
for dealing with responses.

**Kind**: static class of [`LuCI`](#LuCI)  

* [.request](#LuCI.request)
    * _instance_
        * [.expandURL(url)](#LuCI.request+expandURL) ⇒ `string`
        * [.request(target, [options])](#LuCI.request+request) ⇒ [`Promise.<response>`](#LuCI.response)
        * [.handleReadyStateChange(resolveFn, rejectFn, [ev])](#LuCI.request+handleReadyStateChange) ⇒ `void`
        * [.get(url, [options])](#LuCI.request+get) ⇒ [`Promise.<response>`](#LuCI.response)
        * [.post(url, [data], [options])](#LuCI.request+post) ⇒ [`Promise.<response>`](#LuCI.response)
        * [.addInterceptor(interceptorFn)](#LuCI.request+addInterceptor) ⇒ [`interceptorFn`](#LuCI.request.interceptorFn)
        * [.removeInterceptor(interceptorFn)](#LuCI.request+removeInterceptor) ⇒ `boolean`
    * _static_
        * [.poll](#LuCI.request.poll)
            * _instance_
                * [.add(interval, url, [options], [callback])](#LuCI.request.poll+add) ⇒ `function`
                * [.remove(entry)](#LuCI.request.poll+remove) ⇒ `boolean`
                * [.start()](#LuCI.request.poll+start) ⇒ `boolean`
                * [.stop()](#LuCI.request.poll+stop) ⇒ `boolean`
                * [.active()](#LuCI.request.poll+active) ⇒ `boolean`
            * _inner_
                * [~callbackFn](#LuCI.request.poll..callbackFn) : `function`
        * [.RequestOptions](#LuCI.request.RequestOptions) : `Object`
        * [.interceptorFn](#LuCI.request.interceptorFn) : `function`

#### request.expandURL(url) ⇒ `string`
Turn the given relative URL into an absolute URL if necessary.

**Kind**: instance method of [`request`](#LuCI.request)  
**Returns**: `string` - The absolute URL derived from the given one, or the original URL
if it already was absolute.  

| Param | Type | Description |
| --- | --- | --- |
| url | `string` | The URL to convert. |

#### request.request(target, [options]) ⇒ [`Promise.<response>`](#LuCI.response)
Initiate an [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) request to the given target.

**Kind**: instance method of [`request`](#LuCI.request)  
**Returns**: [`Promise.<response>`](#LuCI.response) - The resulting [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response.  

| Param | Type | Description |
| --- | --- | --- |
| target | `string` | The URL to request. |
| [options] | [`RequestOptions`](#LuCI.request.RequestOptions) | Additional options to configure the request. |

#### request.handleReadyStateChange(resolveFn, rejectFn, [ev]) ⇒ `void`
Handle XHR readyState changes for an in-flight request and resolve or
reject the originating promise.

**Kind**: instance method of [`request`](#LuCI.request)  
**Returns**: `void` - No return value; the function resolves or rejects the supplied callbacks.  

| Param | Type | Description |
| --- | --- | --- |
| resolveFn | `function` | Callback invoked on success with the constructed [response](#LuCI.response). |
| rejectFn | `function` | Callback invoked on failure or abort with an `Error` instance. |
| [ev] | `Event` | The XHR `readystatechange` event (optional). |

#### request.get(url, [options]) ⇒ [`Promise.<response>`](#LuCI.response)
Initiate an [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) GET request to the given target.

**Kind**: instance method of [`request`](#LuCI.request)  
**Returns**: [`Promise.<response>`](#LuCI.response) - The resulting [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response.  

| Param | Type | Description |
| --- | --- | --- |
| url | `string` | The URL to request. |
| [options] | [`RequestOptions`](#LuCI.request.RequestOptions) | Additional options to configure the request. |

#### request.post(url, [data], [options]) ⇒ [`Promise.<response>`](#LuCI.response)
Initiate an [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) POST request to the given target.

**Kind**: instance method of [`request`](#LuCI.request)  
**Returns**: [`Promise.<response>`](#LuCI.response) - The resulting [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response.  

| Param | Type | Description |
| --- | --- | --- |
| url | `string` | The URL to request. |
| [data] | `\*` | The request data to send, see [RequestOptions](#LuCI.request.RequestOptions) for details. |
| [options] | [`RequestOptions`](#LuCI.request.RequestOptions) | Additional options to configure the request. |

#### request.addInterceptor(interceptorFn) ⇒ [`interceptorFn`](#LuCI.request.interceptorFn)
Register an [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response interceptor function. Interceptor
functions are useful to perform default actions on incoming [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md)
responses, such as checking for expired authentication or for
implementing request retries before returning a failure.

**Kind**: instance method of [`request`](#LuCI.request)  
**Returns**: [`interceptorFn`](#LuCI.request.interceptorFn) - The registered function.  

| Param | Type | Description |
| --- | --- | --- |
| interceptorFn | [`interceptorFn`](#LuCI.request.interceptorFn) | The interceptor function to register. |

#### request.removeInterceptor(interceptorFn) ⇒ `boolean`
Remove an [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response interceptor function. The passed function
value must be the very same value that was used to register the
function.

**Kind**: instance method of [`request`](#LuCI.request)  
**Returns**: `boolean` - Returns `true` if any function has been removed, else `false`.  

| Param | Type | Description |
| --- | --- | --- |
| interceptorFn | [`interceptorFn`](#LuCI.request.interceptorFn) | The interceptor function to remove. |

#### request.poll
The `Request.poll` class provides some convenience wrappers around
[poll](#LuCI.poll) mainly to simplify registering repeating [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md)
request calls as polling functions.

**Kind**: static class of [`request`](#LuCI.request)  

* [.poll](#LuCI.request.poll)
    * _instance_
        * [.add(interval, url, [options], [callback])](#LuCI.request.poll+add) ⇒ `function`
        * [.remove(entry)](#LuCI.request.poll+remove) ⇒ `boolean`
        * [.start()](#LuCI.request.poll+start) ⇒ `boolean`
        * [.stop()](#LuCI.request.poll+stop) ⇒ `boolean`
        * [.active()](#LuCI.request.poll+active) ⇒ `boolean`
    * _inner_
        * [~callbackFn](#LuCI.request.poll..callbackFn) : `function`

##### poll.add(interval, url, [options], [callback]) ⇒ `function`
Register a repeating [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) request with an optional callback
to invoke whenever a response for the request is received.

**Kind**: instance method of [`poll`](#LuCI.request.poll)  
**Returns**: `function` - Returns the internally created poll function.  
**Throws**:

- `TypeError` Throws `TypeError` when an invalid interval was passed.

| Param | Type | Description |
| --- | --- | --- |
| interval | `number` | The poll interval in seconds. |
| url | `string` | The URL to request on each poll. |
| [options] | [`RequestOptions`](#LuCI.request.RequestOptions) | Additional options to configure the request. |
| [callback] | `LuCI.request.poll.callbackFn` | [Callback](#LuCI.request.poll..callbackFn) function to invoke for each [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) reply. |

##### poll.remove(entry) ⇒ `boolean`
Remove a polling request that has been previously added using `add()`.
This function is essentially a wrapper around
[LuCI.poll.remove()](LuCI.poll.remove).

**Kind**: instance method of [`poll`](#LuCI.request.poll)  
**Returns**: `boolean` - Returns `true` if any function has been removed, else `false`.  

| Param | Type | Description |
| --- | --- | --- |
| entry | `function` | The poll function returned by [add()](#LuCI.request.poll+add). |

##### poll.start() ⇒ `boolean`
Alias for [LuCI.poll.start()](LuCI.poll.start).

**Kind**: instance method of [`poll`](#LuCI.request.poll)  

##### poll.stop() ⇒ `boolean`
Alias for [LuCI.poll.stop()](LuCI.poll.stop).

**Kind**: instance method of [`poll`](#LuCI.request.poll)  

##### poll.active() ⇒ `boolean`
Alias for [LuCI.poll.active()](LuCI.poll.active).

**Kind**: instance method of [`poll`](#LuCI.request.poll)  

##### poll~callbackFn : `function`
The callback function is invoked whenever an [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) reply to a
polled request is received or when the polled request timed
out.

**Kind**: inner typedef of [`poll`](#LuCI.request.poll)  

| Param | Type | Description |
| --- | --- | --- |
| res | [`response`](#LuCI.response) | The [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response object. |
| data | `\*` | The response JSON if the response could be parsed as such, else `null`. |
| duration | `number` | The total duration of the request in milliseconds. |

#### request.RequestOptions : `Object`
**Kind**: static typedef of [`request`](#LuCI.request)  
**Properties**

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| [method] | `string` | `"GET"` | The [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) method to use, e.g. `GET` or `POST`. |
| [query] | `Object.<string, (Object\|string)>` |  | Query string data to append to the URL. Non-string values of the given object will be converted to JSON. |
| [cache] | `boolean` | `false` | Specifies whether the [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response may be retrieved from cache. |
| [username] | `string` |  | Provides a username for [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) basic authentication. |
| [password] | `string` |  | Provides a password for [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) basic authentication. |
| [timeout] | `number` |  | Specifies the request timeout in milliseconds. |
| [credentials] | `boolean` | `false` | Whether to include credentials such as cookies in the request. |
| [responseType] | `string` | `"text"` | Overrides the request response type. Valid values or `text` to interpret the response as UTF-8 string or `blob` to handle the response as binary `Blob` data. |
| [content] | `\*` |  | Specifies the [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) message body to send along with the request. If the value is a function, it is invoked and the return value used as content, if it is a FormData instance, it is used as-is, if it is an object, it will be converted to JSON, in all other cases it is converted to a string. |
| [header] | `Object.<string, string>` |  | Specifies [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) headers to set for the request. |
| [progress] | `function` |  | An optional request callback function which receives ProgressEvent instances as sole argument during the [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) request transfer. |
| [responseProgress] | `function` |  | An optional request callback function which receives ProgressEvent instances as sole argument during the [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response transfer. |

#### request.interceptorFn : `function`
Interceptor functions are invoked whenever an [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) reply is received, in the order
these functions have been registered.

**Kind**: static typedef of [`request`](#LuCI.request)  

| Param | Type | Description |
| --- | --- | --- |
| res | [`response`](#LuCI.response) | The [HTTP](../L2-semantic/wiki/wiki_page-guide-developer-adding-new-device.md) response object |

### LuCI.poll
The `Poll` class allows registering and unregistering poll actions,
as well as starting, stopping, and querying the state of the polling
loop.

**Kind**: static class of [`LuCI`](#LuCI)  

* [.poll](#LuCI.poll)
    * [.add(fn, interval)](#LuCI.poll+add) ⇒ `boolean`
    * [.remove(fn)](#LuCI.poll+remove) ⇒ `boolean`
    * [.start()](#LuCI.poll+start) ⇒ `boolean`
    * [.stop()](#LuCI.poll+stop) ⇒ `boolean`
    * [.active()](#LuCI.poll+active) ⇒ `boolean`

#### poll.add(fn, interval) ⇒ `boolean`
Add a new operation to the polling loop. If the polling loop is not
already started at this point, it will be implicitly started.

**Kind**: instance method of [`poll`](#LuCI.poll)  
**Returns**: `boolean` - Returns `true` if the function has been added or `false` if it
already is registered.  
**Throws**:

- `TypeError` Throws `TypeError` when an invalid interval was passed.

| Param | Type | Description |
| --- | --- | --- |
| fn | `function` | The function to invoke on each poll interval. |
| interval | `number` | The poll interval in seconds. |

#### poll.remove(fn) ⇒ `boolean`
Remove an operation from the polling loop. If no further operations
are registered, the polling loop is implicitly stopped.

**Kind**: instance method of [`poll`](#LuCI.poll)  
**Returns**: `boolean` - Returns `true` if the function has been removed or `false` if it
wasn't found.  
**Throws**:

- `TypeError` Throws `TypeError` when the given argument isn't a function.

| Param | Type | Description |
| --- | --- | --- |
| fn | `function` | The function to remove. |

#### poll.start() ⇒ `boolean`
(Re)start the polling loop. Dispatches a custom `poll-start` event
to the `document` object upon successful start.

**Kind**: instance method of [`poll`](#LuCI.poll)  
**Returns**: `boolean` - Returns `true` if polling has been started (or if no functions
where registered) or `false` when the polling loop already runs.  

#### poll.stop() ⇒ `boolean`
Stop the polling loop. Dispatches a custom `poll-stop` event
to the `document` object upon successful stop.

**Kind**: instance method of [`poll`](#LuCI.poll)  
**Returns**: `boolean` - Returns `true` if polling has been stopped or `false` if it didn't
run to begin with.  

#### poll.active() ⇒ `boolean`
Test whether the polling loop is running.

**Kind**: instance method of [`poll`](#LuCI.poll)  
**Returns**: `boolean` - - Returns `true` if polling is active, else `false`.  

### LuCI.dom
The `dom` class provides a convenience method for creating and
manipulating DOM elements.

To import the class in views, use `'require dom'`, to import it in
external JavaScript, use `L.require("dom").then(...)`.

**Kind**: static class of [`LuCI`](#LuCI)  

* [.dom](#LuCI.dom)
    * _instance_
        * [.elem(e)](#LuCI.dom+elem) ⇒ `boolean`
        * [.parse(s)](#LuCI.dom+parse) ⇒ `Node`
        * [.matches(node, [selector])](#LuCI.dom+matches) ⇒ `boolean`
        * [.parent(node, [selector])](#LuCI.dom+parent) ⇒ `Node` \| `null`
        * [.append(node, [children])](#LuCI.dom+append) ⇒ `Node` \| `null`
        * [.content(node, [children])](#LuCI.dom+content) ⇒ `Node` \| `null`
        * [.attr(node, key, [val])](#LuCI.dom+attr) ⇒ `null`
        * [.create(html, [attr], [data])](#LuCI.dom+create) ⇒ `Node`
        * [.data(node, [key], [val])](#LuCI.dom+data) ⇒ `\*`
        * [.bindClassInstance(node, inst)](#LuCI.dom+bindClassInstance) ⇒ `Class`
        * [.findClassInstance(node)](#LuCI.dom+findClassInstance) ⇒ `Class` \| `null`
        * [.callClassMethod(node, method, ...args)](#LuCI.dom+callClassMethod) ⇒ `\*` \| `null`
        * [.isEmpty(node, [ignoreFn])](#LuCI.dom+isEmpty) ⇒ `boolean`
    * _inner_
        * [~ignoreCallbackFn](#LuCI.dom..ignoreCallbackFn) ⇒ `boolean`

#### dom.elem(e) ⇒ `boolean`
Tests whether the given argument is a valid DOM `Node`.

**Kind**: instance method of [`dom`](#LuCI.dom)  
**Returns**: `boolean` - Returns `true` if the value is a DOM `Node`, else `false`.  

| Param | Type | Description |
| --- | --- | --- |
| e | `\*` | The value to test. |

#### dom.parse(s) ⇒ `Node`
Parses a given string as HTML and returns the first child node.

**Kind**: instance method of [`dom`](#LuCI.dom)  
**Returns**: `Node` - Returns the first DOM `Node` extracted from the HTML fragment or
`null` on parsing failures or if no element could be found.  

| Param | Type | Description |
| --- | --- | --- |
| s | `string` | A string containing an HTML fragment to parse. Note that only the first result of the resulting structure is returned, so an input value of `<div>foo</div> <div>bar</div>` will only return the first `div` element node. |

#### dom.matches(node, [selector]) ⇒ `boolean`
Tests whether a given `Node` matches the given query selector.

This function is a convenience wrapper around the standard
`Node.matches("selector")` function with the added benefit that
the `node` argument may be a non-`Node` value, in which case
this function simply returns `false`.

**Kind**: instance method of [`dom`](#LuCI.dom)  
**Returns**: `boolean` - Returns `true` if the given node matches the specified selector
or `false` when the node argument is no valid DOM `Node` or the
selector didn't match.  

| Param | Type | Description |
| --- | --- | --- |
| node | `\*` | The `Node` argument to test the selector against. |
| [selector] | `string` | The query selector expression to test against the given node. |

#### dom.parent(node, [selector]) ⇒ `Node` \| `null`
Returns the closest parent node that matches the given query
selector expression.

This function is a convenience wrapper around the standard
`Node.closest("selector")` function with the added benefit that
the `node` argument may be a non-`Node` value, in which case
this function simply returns `null`.

**Kind**: instance method of [`dom`](#LuCI.dom)  
**Returns**: `Node` \| `null` - Returns the closest parent node matching the selector or
`null` when the node argument is no valid DOM `Node` or the
selector didn't match any parent.  

| Param | Type | Description |
| --- | --- | --- |
| node | `\*` | The `Node` argument to find the closest parent for. |
| [selector] | `string` | The query selector expression to test against each parent. |

#### dom.append(node, [children]) ⇒ `Node` \| `null`
Appends the given children data to the given node.

**Kind**: instance method of [`dom`](#LuCI.dom)  
**Returns**: `Node` \| `null` - Returns the last children `Node` appended to the node or `null`
if either the `node` argument was no valid DOM `node` or if the
`children` was `null` or didn't result in further DOM nodes.  

| Param | Type | Description |
| --- | --- | --- |
| node | `\*` | The `Node` argument to append the children to. |
| [children] | `\*` | The children to append to the given node. When `children` is an array, then each item of the array will be either appended as a child element or text node, depending on whether the item is a DOM `Node` instance or some other non-`null` value. Non-`Node`, non-`null` values will be converted to strings first before being passed as argument to `createTextNode()`. When `children` is a function, it will be invoked with the passed `node` argument as the sole parameter and the `append` function will be invoked again, with the given `node` argument as first and the return value of the `children` function as  the second parameter. When `children` is a DOM `Node` instance, it will be appended to the given `node`. When `children` is any other non-`null` value, it will be converted to a string and appended to the `innerHTML` property of the given `node`. |

#### dom.content(node, [children]) ⇒ `Node` \| `null`
Replaces the content of the given node with the given children.

This function first removes any children of the given DOM
`Node` and then adds the given children following the
rules outlined below.

**Kind**: instance method of [`dom`](#LuCI.dom)  
**Returns**: `Node` \| `null` - Returns the last children `Node` appended to the node or `null`
if either the `node` argument was no valid DOM `node` or if the
`children` was `null` or didn't result in further DOM nodes.  

| Param | Type | Description |
| --- | --- | --- |
| node | `\*` | The `Node` argument to replace the children of. |
| [children] | `\*` | The children to replace into the given node. When `children` is an array, then each item of the array will be either appended as a child element or text node, depending on whether the item is a DOM `Node` instance or some other non-`null` value. Non-`Node`, non-`null` values will be converted to strings first before being passed as argument to `createTextNode()`. When `children` is a function, it will be invoked with the passed `node` argument as the sole parameter and the `append` function will be invoked again, with the given `node` argument as first and the return value of the `children` function as the second parameter. When `children` is a DOM `Node` instance, it will be appended to the given `node`. When `children` is any other non-`null` value, it will be converted to a string and appended to the `innerHTML` property of the given `node`. |

---

# LuCI API: static

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.static.html

---



## isCIDR(value) ⇒ `boolean`
Determine whether a provided value is a CIDR format IP string.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| value | `string` | the IP string to test. |

## calculateBroadcast(s, use_cfgvalue) ⇒ `string`
Calculate the broadcast IP for a given IP.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| s | `Node` | the ui element to test. |
| use_cfgvalue | `boolean` | whether to use the config or form value. |

## validateBroadcast(section_id, value) ⇒ `boolean`
Validate a broadcast IP for a section value.

**Kind**: global function  

| Param | Type |
| --- | --- |
| section_id | `string` | 
| value | `string` |

---

# LuCI API: prng

> **Live docs:** https://openwrt.github.io/luci/jsapi/LuCI.prng.html

---



## mul(a, b) ⇒ `Array.<number>`
Multiply two 64-bit values represented as arrays of four 16-bit words.

Arrays use little-endian word order (least-significant 16-bit word first).
The result is truncated to the lower 64 bits and returned as a 4-element
array of 16-bit words.

**Kind**: global function  
**Returns**: `Array.<number>` - Product as 4 × 16-bit words (little-endian)  

| Param | Type | Description |
| --- | --- | --- |
| a | `Array.<number>` | Multiplicand (4 × 16-bit words, little-endian) |
| b | `Array.<number>` | Multiplier  (4 × 16-bit words, little-endian) |

## add(a, n) ⇒ `Array.<number>`
Add a small integer to a 64-bit value represented as four 16-bit words.

Treats `a` as a little-endian 64-bit value (4 × 16-bit words). Adds the
integer `n` to the least-significant word and propagates carry across
subsequent 16-bit words. The result is truncated to 64 bits and returned
as a 4-element array of 16-bit words (little-endian).

**Kind**: global function  
**Returns**: `Array.<number>` - Sum as 4 × 16-bit words (little-endian)  

| Param | Type | Description |
| --- | --- | --- |
| a | `Array.<number>` | Addend as 4 × 16-bit words (little-endian) |
| n | `number` | Value to add (integer carry) |

## shr(a, n) ⇒ `Array.<number>`
Shift a 64-bit value (4 × 16-bit words, little-endian) right by `n` bits.

The input array is treated as little-endian 16-bit words. Bits shifted out
on the right are discarded; the returned array contains the lower 64-bit
result after the logical right shift.

**Kind**: global function  
**Returns**: `Array.<number>` - Shifted value as 4 × 16-bit words (little-endian)  

| Param | Type | Description |
| --- | --- | --- |
| a | `Array.<number>` | Source value as 4 × 16-bit words (little-endian) |
| n | `number` | Number of bits to shift right (non-negative integer) |

## seed(n) ⇒ `void`
Seed the PRNG state.

The seed is treated as a 32-bit integer; the lower 16 bits are stored
in `s[0]`, the upper 16 bits in `s[1]`. `s[2]` and `s[3]` are zeroed.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| n | `number` | Seed value (32-bit integer) |

## int() ⇒ `number`
Produce the next PRNG 32-bit integer.

Advances the internal state and returns a 32-bit pseudo-random integer
derived from the current state.

**Kind**: global function  
**Returns**: `number` - 32-bit pseudo-random integer (JS number)  

## get([lower], [upper]) ⇒ `number`
Return a pseudo-random value.

Overloads:
- get() -> number in [0, 1]
- get(upper) -> integer in [1, upper]
- get(lower, upper) -> integer in [lower, upper]

**Kind**: global function  
**Returns**: `number` - Random value (float in [0,1] or integer in requested range)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [lower] | `number` | `0` | Lower bound (when two args supplied) |
| [upper] | `number` | `0` | Upper bound (when one or two args supplied) |

## derive\_color(string) ⇒ `string`
Derive a deterministic hex color from an input string.

The color is produced by seeding the PRNG from a string-derived
hash and producing RGB components. Returns a `#rrggbb` hex string.

**Kind**: global function  
**Returns**: `string` - Hex color string in `#rrggbb` format  

| Param | Type | Description |
| --- | --- | --- |
| string | `string` | Input string used to derive the color |

---

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

---

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
