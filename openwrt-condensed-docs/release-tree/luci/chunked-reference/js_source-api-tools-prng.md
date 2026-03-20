---
title: 'LuCI API: prng'
module: luci
origin_type: js_source
token_count: 982
version: 18e0538
source_file: L1-raw/luci/js_source-api-tools-prng.md
last_pipeline_run: '2026-03-20T01:28:00.439321+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/tools/prng.js
language: javascript
ai_summary: Provides a lightweight pseudo-random number generator utility for the LuCI frontend. Implements prng.generate(n) to produce n-byte hex strings and prng.uuid() for v4-compatible UUID generation; uses the Web Crypto API when available and falls back to Math.random(), making it suitable for generating unique DOM IDs and one-time tokens in LuCI views.
ai_when_to_use: Reference when a LuCI view or widget needs to generate a unique identifier for a DOM element, create a nonce for a form submission, or produce a random token without depending on server-side generation.
ai_related_topics:
- LuCI.tools.prng.generate
- LuCI.tools.prng.uuid
- Web Crypto API
- LuCI.ui
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
