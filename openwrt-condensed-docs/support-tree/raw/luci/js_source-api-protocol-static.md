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