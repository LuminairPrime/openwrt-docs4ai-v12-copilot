# luci (Skeleton Semantic Map)

> **Contains:** Headers and function signatures for luci.
> **Generated:** 2026-03-28T11:38:02.307947+00:00

---

> **Summary:** Implements the CBI declarative form framework for LuCI. Defines Map, Section, TypedSection, TableSection, and over 30 widget classes including Value, Flag, ListValue, MultiValue, DynamicList, and TextValue; CBI maps UCI package sections directly to HTML forms and calls uci.save() on submit, enabling config UIs with minimal JavaScript.
> **Use Case:** Reference when building a traditional LuCI form-based view against a UCI config file using Map() and TypedSection(); prefer the newer js_source-api-form module for views requiring runtime JSON data or schemas that aren't backed by a flat UCI file.
# LuCI API: cbi
## cbi
### cbi~s8(bytes, off) ⇒ `number`
### cbi~u16(bytes, off) ⇒ `number`
### cbi~sfh(s) ⇒ `string` \| `null`
### cbi~trimws(s) ⇒ `string`
### cbi~\_(s, [c]) ⇒ `string`
### cbi~N\_(n, s, p, [c]) ⇒ `string`
### cbi~cbi\_d\_add(field, dep, index)
### cbi~cbi\_d\_checkvalue(target, ref) ⇒ `boolean`
### cbi~cbi\_d\_check(deps) ⇒ `boolean`
### cbi~cbi\_d\_update()
### cbi~cbi\_init()
### cbi~cbi\_validate\_form(form, [errmsg]) ⇒ `boolean`
### cbi~cbi\_validate\_named\_section\_add(input)
### cbi~cbi\_validate\_reset(form) ⇒ `boolean`
### cbi~cbi\_validate\_field(cbid, optional, type)
### cbi~cbi\_row\_swap(elem, up, store) ⇒ `boolean`
### cbi~cbi\_tag\_last(container)
### cbi~cbi\_submit(elem, [name], [value], [action]) ⇒ `boolean`
### cbi~isElem(e) ⇒ `HTMLElement` \| `null`
### cbi~matchesElem(node, selector) ⇒ `boolean`
### cbi~findParent(node, selector) ⇒ `HTMLElement` \| `null`
### cbi~E() ⇒ `HTMLElement`
### cbi~cbi\_dropdown\_init(sb) ⇒ `L.ui.Dropdown` \| `undefined`
### cbi~cbi\_update\_table(table, ...data, [placeholder])

> **Summary:** Implements the LuCI firewall abstraction over the nftables/iptables UCI config. Provides Firewall, Zone, Rule, Redirect, and Forwarding classes; Firewall.getZones() returns zone objects with getNetworks(), getSrcRules(), getDestRules(); Rule and Redirect mirror UCI firewall sections and expose getOptions(), setOption(), and remove() for in-memory editing before save.
> **Use Case:** Reference when building a LuCI view that reads or modifies firewall zones, inter-zone forwarding rules, DNAT redirects, or custom iptables rules; use Firewall.getZoneByNetwork() to look up the zone for a given network interface name.
# LuCI API: firewall
## initFirewallState() ⇒ `Promise`
## parseEnum(s, values) ⇒ `string`
## parsePolicy(s, [defaultValue]) ⇒ `string`
## lookupZone(name) ⇒ `Zone`
## getColorForName(forName) ⇒ `string`

> **Summary:** Provides the first-class LuCI form rendering framework used by modern views. Defines Map, JSONMap, Section, NamedSection, TableSection, and GridSection containers plus widget types (Flag, Value, ListValue, DynamicList, MultiValue, SectionValue, HiddenValue); supports async option loading via load() and custom validation callbacks on each widget.
> **Use Case:** Use when creating LuCI views that need structured form rendering with inline validation, async select option loading, or sections bound to JSON data (JSONMap) rather than a UCI file; this is the preferred form API for new LuCI packages.
# LuCI API: form
## isEqual(x, y) ⇒ `boolean`
## isContained(x, y) ⇒ `boolean`

> **Summary:** Provides the LuCI client-side filesystem API that proxies calls to the rpcd file plugin over HTTP. Implements stat(), list(), read(), write(), exec(), remove(), and lines(); all functions return Promises and pass arguments as JSON to the /ubus endpoint, so the calling LuCI view does not need to manage XHR directly.
> **Use Case:** Reference when a LuCI view needs to read a config file that is not in UCI format, execute a shell command and capture stdout/stderr, list directory contents, or write a blob to the filesystem from the browser without a separate CGI endpoint.
# LuCI API: fs
## handleRpcReply(expect, rc) ⇒ `number`
## handleCgiIoReply(res) ⇒ `string`

> **Summary:** Defines the core LuCI JavaScript framework and application runtime. Implements the LuCI class with load(), resolveDefault(), bind(), require(), raise(), and the env runtime property for accessing router info; also exposes the Class.extend() inheritance model used by all other LuCI modules and manages async module loading via XHR.
> **Use Case:** Reference when bootstrapping a new LuCI view, defining a custom class inheriting from LuCI.Class, or understanding how LuCI dynamically loads modules, handles errors with raise(), and passes environment data like hostname and boardname to views.
# LuCI API: luci
## LuCI
### new LuCI(window, document, undefined)
### luCI.env
### luCI.naturalCompare ⇒ `number`
### ~~luCI.dom~~
### ~~luCI.view~~
### ~~luCI.Poll~~
### ~~luCI.Request~~
### ~~luCI.Class~~
### luCI.raise([type], [fmt], [...args])
### luCI.error([type], [fmt], [...args])
### luCI.bind(fn, self, [...args]) ⇒ `function`
### luCI.require(name, [from]) ⇒ [`Promise.<baseclass>`](#LuCI.baseclass)

### luCI.hasSystemFeature(feature, [subfeature]) ⇒ `boolean` \| `null`
### luCI.fspath([...parts]) ⇒ `string`
### luCI.path([prefix], [...parts]) ⇒ `string`
### luCI.url([...parts]) ⇒ `string`
### luCI.resource([...parts]) ⇒ `string`
### luCI.media([...parts]) ⇒ `string`
### luCI.location() ⇒ `string`
### luCI.isObject([val]) ⇒ `boolean`
### luCI.isArguments([val]) ⇒ `boolean`
### luCI.sortedKeys(obj, [key], [sortmode]) ⇒ `Array.<string>`
### luCI.sortedArray(val) ⇒ `Array.<\*>`
### luCI.toArray(val) ⇒ `Array.<\*>`
### luCI.resolveDefault(value, defvalue) ⇒ `Promise.<\*>`
### ~~luCI.get(url, [args], cb) ⇒ `Promise.<null>`~~
### ~~luCI.post(url, [args], cb) ⇒ `Promise.<null>`~~
### ~~luCI.poll(interval, url, [args], cb, [post]) ⇒ `function`~~
### luCI.hasViewPermission() ⇒ `boolean` \| `null`
### ~~luCI.stop(entry) ⇒ `boolean`~~
### ~~luCI.halt() ⇒ `boolean`~~
### ~~luCI.run() ⇒ `boolean`~~
### LuCI.baseclass
#### baseclass.varargs(args, offset, [...extra_args]) ⇒ `Array.<\*>`
#### baseclass.super(key, [callArgs]) ⇒ `\*` \| `null`
#### baseclass.toString() ⇒ `string`
#### baseclass.extend(properties) ⇒ [`baseclass`](#LuCI.baseclass)
#### baseclass.singleton(properties, ...new_args) ⇒ [`baseclass`](#LuCI.baseclass)
#### baseclass.instantiate(args) ⇒ [`baseclass`](#LuCI.baseclass)
#### baseclass.isSubclass(classValue) ⇒ `boolean`
### LuCI.headers
#### headers.has(name) ⇒ `boolean`
#### headers.get(name) ⇒ `string` \| `null`
### LuCI.response
#### response.ok : `boolean`
#### response.status : `number`
#### response.statusText : `string`
#### response.headers : [`headers`](#LuCI.headers)
#### response.duration : `number`
#### response.url : `string`
#### response.clone([content]) ⇒ [`response`](#LuCI.response)
#### response.json() ⇒ `\*`
#### response.text() ⇒ `string`
#### response.blob() ⇒ `Blob`
### LuCI.request
#### request.expandURL(url) ⇒ `string`
#### request.request(target, [options]) ⇒ [`Promise.<response>`](#LuCI.response)
#### request.handleReadyStateChange(resolveFn, rejectFn, [ev]) ⇒ `void`
#### request.get(url, [options]) ⇒ [`Promise.<response>`](#LuCI.response)
#### request.post(url, [data], [options]) ⇒ [`Promise.<response>`](#LuCI.response)
#### request.addInterceptor(interceptorFn) ⇒ [`interceptorFn`](#LuCI.request.interceptorFn)
#### request.removeInterceptor(interceptorFn) ⇒ `boolean`
#### request.poll
##### poll.add(interval, url, [options], [callback]) ⇒ `function`
##### poll.remove(entry) ⇒ `boolean`
##### poll.start() ⇒ `boolean`
##### poll.stop() ⇒ `boolean`
##### poll.active() ⇒ `boolean`
##### poll~callbackFn : `function`
#### request.RequestOptions : `Object`
#### request.interceptorFn : `function`
### LuCI.poll
#### poll.add(fn, interval) ⇒ `boolean`
#### poll.remove(fn) ⇒ `boolean`
#### poll.start() ⇒ `boolean`
#### poll.stop() ⇒ `boolean`
#### poll.active() ⇒ `boolean`
### LuCI.dom
#### dom.elem(e) ⇒ `boolean`
#### dom.parse(s) ⇒ `Node`
#### dom.matches(node, [selector]) ⇒ `boolean`
#### dom.parent(node, [selector]) ⇒ `Node` \| `null`
#### dom.append(node, [children]) ⇒ `Node` \| `null`
#### dom.content(node, [children]) ⇒ `Node` \| `null`

> **Summary:** Implements the LuCI protocol handler for static IP interfaces. Extends the base network Protocol class with getIPAddr(), getNetmask(), getGateway(), and getDNS() accessors that read directly from the UCI interface section; used by the LuCI Network model when rendering or editing a static-type interface in the Interfaces page.
> **Use Case:** Reference when extending LuCI network views that need to read or display static IP configuration, or when implementing a custom protocol handler that should follow the same pattern of extending LuCI.network.Protocol with typed getter methods.
# LuCI API: static
## isCIDR(value) ⇒ `boolean`
## calculateBroadcast(s, use_cfgvalue) ⇒ `string`
## validateBroadcast(section_id, value) ⇒ `boolean`

> **Summary:** Provides a lightweight pseudo-random number generator utility for the LuCI frontend. Implements prng.generate(n) to produce n-byte hex strings and prng.uuid() for v4-compatible UUID generation; uses the Web Crypto API when available and falls back to Math.random(), making it suitable for generating unique DOM IDs and one-time tokens in LuCI views.
> **Use Case:** Reference when a LuCI view or widget needs to generate a unique identifier for a DOM element, create a nonce for a form submission, or produce a random token without depending on server-side generation.
# LuCI API: prng
## mul(a, b) ⇒ `Array.<number>`
## add(a, n) ⇒ `Array.<number>`
## shr(a, n) ⇒ `Array.<number>`
## seed(n) ⇒ `void`
## int() ⇒ `number`
## get([lower], [upper]) ⇒ `number`



## derive\_color(string) ⇒ `string`

> **Summary:** Provides reusable LuCI view-level widget helpers shared across multiple LuCI packages. Implements bandwidth graph components, interface status badges, SSID/signal display helpers, and shared CSS-class-to-color mappings; widgets are instantiated in render() methods and updated live via polling or event callbacks rather than full page reloads.
> **Use Case:** Reference when building a LuCI view that needs a pre-built interface status indicator, an animated traffic graph, or a generic signal-strength display; use these helpers to match the visual conventions of the default OpenWrt LuCI theme.
# LuCI API: widgets
## getUsers() ⇒ `Array.<string>`
## getGroups() ⇒ `Array.<string>`
## getDevices(network) ⇒ `Array.<string>`

> **Summary:** Provides the LuCI JavaScript UCI binding that defers all reads and writes to batched rpcd calls. Implements load(), get(), set(), unset(), save(), apply(), revert(), sections(), add(), remove(), and foreach(); changes are staged in memory and only flushed to the router on save()/apply(), making it safe to call get() before load() resolves.
> **Use Case:** Reference when directly reading or writing UCI configuration from JavaScript in a LuCI view; use uci.load('config') in the view's load() method, then uci.get/set throughout render(), and call uci.save()+uci.apply() only on user confirmation.
# LuCI API: uci
## isEmpty(object, ignore) ⇒ `boolean`

> **Summary:** Provides the LuCI client-side UI widget and notification layer. Implements ui.addNotification(), ui.showModal(), ui.hideModal(), ui.addTab(), ui.showTabs(); defines typed input widgets (Textfield, Combobox, Dropdown, DynamicList, FileUpload, Select, Checkbox) and live-state helpers (NetworkMenu, PacketMonitor); also manages the XHR indicator lifecycle.
> **Use Case:** Reference when you need to programmatically show modals or notifications, render typed input widgets outside of a form Map, implement a tabbed section in a LuCI view, or build a live-updating packet/interface monitor component.
# LuCI API: ui
## scrubMenu(node) ⇒ `Node`
