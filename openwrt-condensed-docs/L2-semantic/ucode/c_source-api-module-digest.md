---
title: 'ucode module: digest'
module: ucode
origin_type: c_source
token_count: 2040
version: unknown
source_file: L1-raw/ucode/c_source-api-module-digest.md
last_pipeline_run: '2026-03-09T17:28:41.757217+00:00'
upstream_path: lib/digest.c
language: c
---
# ucode module: digest

> **Live docs:** https://ucode.mein.io/module-digest.html

---

<a name="module_digest"></a>

## digest
# Digest Functions

The `digest` module bundles various digest functions.

* [digest](#module_digest)
    * [.md5(str)](#module_digest+md5) ⇒ `string`
    * [.sha1(str)](#module_digest+sha1) ⇒ `string`
    * [.sha256(str)](#module_digest+sha256) ⇒ `string`
    * [.md2(str)](#module_digest+md2) ⇒ `string`
    * [.md4(str)](#module_digest+md4) ⇒ `string`
    * [.sha384(str)](#module_digest+sha384) ⇒ `string`
    * [.sha512(str)](#module_digest+sha512) ⇒ `string`
    * [.md5_file(path)](#module_digest+md5_file) ⇒ `string`
    * [.sha1_file(path)](#module_digest+sha1_file) ⇒ `string`
    * [.sha256_file(path)](#module_digest+sha256_file) ⇒ `string`
    * [.md2_file(path)](#module_digest+md2_file) ⇒ `string`
    * [.md4_file(path)](#module_digest+md4_file) ⇒ `string`
    * [.sha384_file(path)](#module_digest+sha384_file) ⇒ `string`
    * [.sha512_file(path)](#module_digest+sha512_file) ⇒ `string`

<a name="module_digest+md5"></a>

### digest.md5(str) ⇒ `string`
Calculates the MD5 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```js
md5("This is a test");  // Returns "ce114e4501d2f4e2dcea3e17b546f339"
md5(123);               // Returns null
```
<a name="module_digest+sha1"></a>

### digest.sha1(str) ⇒ `string`
Calculates the SHA1 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```js
sha1("This is a test");  // Returns "a54d88e06612d820bc3be72877c74f257b561b19"
sha1(123);               // Returns null
```
<a name="module_digest+sha256"></a>

### digest.sha256(str) ⇒ `string`
Calculates the SHA256 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```js
sha256("This is a test");  // Returns "c7be1ed902fb8dd4d48997c6452f5d7e509fbcdbe2808b16bcf4edce4c07d14e"
sha256(123);               // Returns null
```
<a name="module_digest+md2"></a>

### digest.md2(str) ⇒ `string`
Calculates the MD2 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```js
md2("This is a test");  // Returns "dc378580fd0722e56b82666a6994c718"
md2(123);               // Returns null
```
<a name="module_digest+md4"></a>

### digest.md4(str) ⇒ `string`
Calculates the MD4 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```js
md4("This is a test");  // Returns "3b487cf6856af7e330bc4b1b7d977ef8"
md4(123);               // Returns null
```
<a name="module_digest+sha384"></a>

### digest.sha384(str) ⇒ `string`
Calculates the SHA384 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```js
sha384("This is a test");  // Returns "a27c7667e58200d4c0688ea136968404a0da366b1a9fc19bb38a0c7a609a1eef2bcc82837f4f4d92031a66051494b38c"
sha384(123);               // Returns null
```
<a name="module_digest+sha512"></a>

### digest.sha512(str) ⇒ `string`
Calculates the SHA512 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```js
sha512("This is a test");  // Returns "a028d4f74b602ba45eb0a93c9a4677240dcf281a1a9322f183bd32f0bed82ec72de9c3957b2f4c9a1ccf7ed14f85d73498df38017e703d47ebb9f0b3bf116f69"
sha512(123);               // Returns null
```
<a name="module_digest+md5_file"></a>

### digest.md5\_file(path) ⇒ `string`
Calculates the MD5 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

<a name="module_digest+sha1_file"></a>

### digest.sha1\_file(path) ⇒ `string`
Calculates the SHA1 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

<a name="module_digest+sha256_file"></a>

### digest.sha256\_file(path) ⇒ `string`
Calculates the SHA256 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

<a name="module_digest+md2_file"></a>

### digest.md2\_file(path) ⇒ `string`
Calculates the MD2 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

<a name="module_digest+md4_file"></a>

### digest.md4\_file(path) ⇒ `string`
Calculates the MD4 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

<a name="module_digest+sha384_file"></a>

### digest.sha384\_file(path) ⇒ `string`
Calculates the SHA384 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

<a name="module_digest+sha512_file"></a>

### digest.sha512\_file(path) ⇒ `string`
Calculates the SHA512 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |