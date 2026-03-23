# luci (Skeleton Semantic Map)

> **Contains:** Headers and function signatures for luci.
> **Generated:** 2026-03-23T22:14:37.218591+00:00

---

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

# LuCI API: firewall
## initFirewallState() ⇒ `Promise`
## parseEnum(s, values) ⇒ `string`
## parsePolicy(s, [defaultValue]) ⇒ `string`
## lookupZone(name) ⇒ `Zone`
## getColorForName(forName) ⇒ `string`

# LuCI API: form
## isEqual(x, y) ⇒ `boolean`
## isContained(x, y) ⇒ `boolean`

# LuCI API: fs
## handleRpcReply(expect, rc) ⇒ `number`
## handleCgiIoReply(res) ⇒ `string`

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

# LuCI API: static
## isCIDR(value) ⇒ `boolean`
## calculateBroadcast(s, use_cfgvalue) ⇒ `string`
## validateBroadcast(section_id, value) ⇒ `boolean`

# LuCI API: prng
## mul(a, b) ⇒ `Array.<number>`
## add(a, n) ⇒ `Array.<number>`
## shr(a, n) ⇒ `Array.<number>`
## seed(n) ⇒ `void`
## int() ⇒ `number`
## get([lower], [upper]) ⇒ `number`



## derive\_color(string) ⇒ `string`

# LuCI API: widgets
## getUsers() ⇒ `Array.<string>`
## getGroups() ⇒ `Array.<string>`
## getDevices(network) ⇒ `Array.<string>`

# LuCI API: uci
## isEmpty(object, ignore) ⇒ `boolean`

# LuCI API: ui
## scrubMenu(node) ⇒ `Node`
