---
title: 'ucode module: zlib'
module: ucode
origin_type: c_source
token_count: 1913
version: unknown
source_file: L1-raw/ucode/c_source-api-module-zlib.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
upstream_path: lib/zlib.c
language: c
---
# ucode module: zlib

> **Live docs:** https://ucode.mein.io/module-zlib.html

---

## Zlib bindings

The `zlib` module provides single-call and stream-oriented functions for interacting with zlib data.

### zlib.deflate(str_or_resource, [gzip], [level]) ⇒ `string`
Compresses data in Zlib or gzip format.

If the input argument is a plain string, it is directly compressed.

If an array, object or resource value is given, this function will attempt to
invoke a `read()` method on it to read chunks of input text to incrementally
compress. Reading will stop if the object's `read()` method returns
either `null` or an empty string.

Throws an exception on errors.

Returns the compressed data.

**Kind**: instance method of [`zlib`](#module_zlib)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| str_or_resource | `string` |  | The string or resource object to be compressed. |
| [gzip] | `boolean` | `false` | Add a gzip header if true (creates a gzip-compliant output, otherwise defaults to Zlib) |
| [level] | `number` | `Z_DEFAULT_COMPRESSION` | The compression level (0-9). |

**Example**  
```ucode
// deflate content using default compression
const deflated = deflate(content);

// deflate content using fastest compression
const deflated = deflate(content, Z_BEST_SPEED);
```

### zlib.inflate(str_or_resource) ⇒ `string`
Decompresses data in Zlib or gzip format.

If the input argument is a plain string, it is directly decompressed.

If an array, object or resource value is given, this function will attempt to
invoke a `read()` method on it to read chunks of input text to incrementally
decompress. Reading will stop if the object's `read()` method returns
either `null` or an empty string.

Throws an exception on errors.

Returns the decompressed data.

**Kind**: instance method of [`zlib`](#module_zlib)  

| Param | Type | Description |
| --- | --- | --- |
| str_or_resource | `string` | The string or resource object to be parsed as JSON. |

### zlib.deflater([gzip], [level]) ⇒ [`deflate`](#module_zlib.deflate)
Initializes a deflate stream.

Returns a stream handle on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`zlib`](#module_zlib)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [gzip] | `boolean` | `false` | Add a gzip header if true (creates a gzip-compliant output, otherwise defaults to Zlib) |
| [level] | `number` | `Z_DEFAULT_COMPRESSION` | The compression level (0-9). |

**Example**  
```ucode
// initialize a Zlib deflate stream using default compression
const zstrmd = deflater();

// initialize a gzip deflate stream using fastest compression
const zstrmd = deflater(true, Z_BEST_SPEED);
```

### zlib.inflater() ⇒ [`inflate`](#module_zlib.inflate)
Initializes an inflate stream. Can process either Zlib or gzip data.

Returns a stream handle on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`zlib`](#module_zlib)  
**Example**  
```ucode
// initialize an inflate stream
const zstrmi = inflater();
```

### zlib.deflate
**Kind**: static class of [`zlib`](#module_zlib)  
**See**: [module:zlib#deflater()](module:zlib#deflater())  

* [.deflate](#module_zlib.deflate)
    * [.write(src, [flush])](#module_zlib.deflate+write) ⇒ `boolean`
    * [.read()](#module_zlib.deflate+read) ⇒ `string`
    * [.error()](#module_zlib.deflate+error) ⇒ `string`

#### deflate.write(src, [flush]) ⇒ `boolean`
Writes a chunk of data to the deflate stream.

Input data must be a string, it is internally compressed by the zlib `deflate()` routine,
the end result is buffered according to the requested `flush` mode until read via
[module:zlib.zstrmd#read](module:zlib.zstrmd#read).
Valid `flush`values are `Z_NO_FLUSH` (the default),
`Z_SYNC_FLUSH, Z_PARTIAL_FLUSH, Z_FULL_FLUSH, Z_FINISH`.
If `flush` is `Z_FINISH` then no more data can be written to the stream.
Refer to the [Zlib manual](https://zlib.net/manual.html) for details
on each flush mode.

Returns `true` on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`deflate`](#module_zlib.deflate)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| src | `string` |  | The string of data to deflate. |
| [flush] | `number` | `Z_NO_FLUSH` | The zlib flush mode. |

#### deflate.read() ⇒ `string`
Reads a chunk of compressed data from the deflate stream.

Returns the current content of the deflate buffer, fed through
[write](#module_zlib.deflate+write).

Returns compressed chunk on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`deflate`](#module_zlib.deflate)  

#### deflate.error() ⇒ `string`
Queries error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`deflate`](#module_zlib.deflate)  

### zlib.inflate
**Kind**: static class of [`zlib`](#module_zlib)  
**See**: [module:zlib#inflater()](module:zlib#inflater())  

* [.inflate](#module_zlib.inflate)
    * [.write(src, [flush])](#module_zlib.inflate+write) ⇒ `boolean`
    * [.read()](#module_zlib.inflate+read) ⇒ `string`
    * [.error()](#module_zlib.inflate+error) ⇒ `string`

#### inflate.write(src, [flush]) ⇒ `boolean`
Writes a chunk of data to the inflate stream.

Input data must be a string, it is internally decompressed by the zlib `inflate()` routine,
the end result is buffered according to the requested `flush` mode until read via
[read](#module_zlib.inflate+read).
Valid `flush` values are `Z_NO_FLUSH` (the default), `Z_SYNC_FLUSH, Z_FINISH`.
If `flush` is `Z_FINISH` then no more data can be written to the stream.
Refer to the [Zlib manual](https://zlib.net/manual.html) for details
on each flush mode.

Returns `true` on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`inflate`](#module_zlib.inflate)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| src | `string` |  | The string of data to inflate. |
| [flush] | `number` | `Z_NO_FLUSH` | The zlib flush mode. |

#### inflate.read() ⇒ `string`
Reads a chunk of decompressed data from the inflate stream.

Returns the current content of the inflate buffer, fed through
[write](#module_zlib.inflate+write).

Returns decompressed chunk on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`inflate`](#module_zlib.inflate)  

#### inflate.error() ⇒ `string`
Queries error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`inflate`](#module_zlib.inflate)  

### zlib~Compression levels
Constants representing predefined compression levels.

**Kind**: inner typedef of [`zlib`](#module_zlib)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| Z_NO_COMPRESSION. | `number` |  |
| Z_BEST_SPEED. | `number` |  |
| Z_BEST_COMPRESSION. | `number` |  |
| Z_DEFAULT_COMPRESSION | `number` | default compromise between speed and compression (currently equivalent to level 6). |

### zlib~flush options
Constants representing flush options.

**Kind**: inner typedef of [`zlib`](#module_zlib)  
**Properties**

| Name | Type |
| --- | --- |
| Z_NO_FLUSH. | `number` | 
| Z_PARTIAL_FLUSH. | `number` | 
| Z_SYNC_FLUSH. | `number` | 
| Z_FULL_FLUSH. | `number` | 
| Z_FINISH. | `number` |