---
title: 'ucode module: debug'
module: ucode
origin_type: c_source
token_count: 3903
source_file: L1-raw/ucode/c_source-api-module-debug.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_commit: unknown
source_url: https://github.com/nicowillis/ucode/blob/unknown/lib/debug.c
source_locator: lib/debug.c
language: c
ai_summary: Provides runtime introspection and tracing utilities for ucode scripts. Implements traceback() to capture the current call stack, getinfo() to inspect function and closure metadata, and memdump() for object inspection at runtime. Used primarily for structured error reporting and development-time debugging in production handlers.
ai_when_to_use: Use to produce meaningful stack traces in error handlers, inspect closures during development, or emit diagnostic context information in ucode services running under procd where stderr is not easily accessible.
ai_related_topics:
- debug.traceback
- debug.getinfo
- debug.memdump
---

> **Source:** [https://github.com/nicowillis/ucode/blob/unknown/lib/debug.c](https://github.com/nicowillis/ucode/blob/unknown/lib/debug.c)
> **Kind:** c_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

# ucode module: debug

> **Live docs:** https://ucode.mein.io/module-debug.html

---

## Debugger Module

This module provides runtime debug functionality for ucode scripts.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { memdump, traceback } from 'debug';

  let stacktrace = traceback(1);

  memdump("/tmp/dump.txt");
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as debug from 'debug';

  let stacktrace = debug.traceback(1);

  debug.memdump("/tmp/dump.txt");
  ```

Additionally, the debug module namespace may also be imported by invoking the
`ucode` interpreter with the `-ldebug` switch.

Upon loading, the `debug` module will register a `SIGUSR2` signal handler
which, upon receipt of the signal, will write a memory dump of the currently
running program to `/tmp/ucode.$timestamp.$pid.memdump`. This default
behavior can be inhibited by setting the `UCODE_DEBUG_MEMDUMP_ENABLED`
environment variable to `0` when starting the process. The memory dump signal
and output directory can be overridden with the `UCODE_DEBUG_MEMDUMP_SIGNAL`
and `UCODE_DEBUG_MEMDUMP_PATH` environment variables respectively.

### debug.memdump(file) ⇒ `boolean`
Write a memory dump report to the given file.

This function generates a human readable memory dump of ucode values
currently managed by the running VM which is useful to track down logical
memory leaks in scripts.

The file parameter can be either a string value containing a file path, in
which case this function tries to create and write the report file at the
given location, or an already open file handle this function should write to.

Returns `true` if the report has been written.

Returns `null` if the file could not be opened or if the handle was invalid.

**Kind**: instance method of [`debug`](#module_debug)  

| Param | Type | Description |
| --- | --- | --- |
| file | `string` \| `module:fs.file` \| `module:fs.proc` | The file path or open file handle to write report to. |

### debug.traceback([level]) ⇒ [`Array.<StackTraceEntry>`](#module_debug.StackTraceEntry)
Capture call stack trace.

This function captures the current call stack and returns it. The optional
level parameter controls how many calls up the trace should start. It
defaults to `1`, that is the function calling this `traceback()` function.

Returns an array of stack trace entries describing the function invocations
up to the point where `traceback()` is called.

**Kind**: instance method of [`debug`](#module_debug)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [level] | `number` | `1` | The number of callframes up the call trace should start, `0` is this function itself, `1` the function calling it and so on. |

### debug.sourcepos() ⇒ [`SourcePosition`](#module_debug.SourcePosition)
Obtain information about the current source position.

The `sourcepos()` function determines the source code position of the
current instruction invoking this function.

Returns a dictionary containing the filename, line number and line byte
offset of the call site.

Returns `null` if this function was invoked from C code.

**Kind**: instance method of [`debug`](#module_debug)  

### debug.getinfo(value) ⇒ [`ValueInformation`](#module_debug.ValueInformation)
Obtain information about the given value.

The `getinfo()` function allows querying internal information about the
given ucode value, such as the current reference count, the mark bit state
etc.

Returns a dictionary with value type specific details.

Returns `null` if a `null` value was provided.

**Kind**: instance method of [`debug`](#module_debug)  

| Param | Type | Description |
| --- | --- | --- |
| value | `\*` | The value to query information for. |

### debug.getlocal([level], variable) ⇒ [`LocalInfo`](#module_debug.LocalInfo)
Obtain local variable.

The `getlocal()` function retrieves information about the specified local
variable at the given call stack depth.

The call stack depth specifies the amount of levels up local variables should
be queried. A value of `0` refers to this `getlocal()` function call itself,
`1` to the function calling `getlocal()` and so on.

The variable to query might be either specified by name or by its index with
index numbers following the source code declaration order.

Returns a dictionary holding information about the given variable.

Returns `null` if the stack depth exceeds the size of the current call stack.

Returns `null` if the invocation at the given stack depth is a C call.

Returns `null` if the given variable name is not found or the given variable
index is invalid.

**Kind**: instance method of [`debug`](#module_debug)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [level] | `number` | `1` | The amount of call stack levels up local variables should be queried. |
| variable | `string` \| `number` |  | The variable index or variable name to obtain information for. |

### debug.setlocal([level], variable, [value]) ⇒ [`LocalInfo`](#module_debug.LocalInfo)
Set local variable.

The `setlocal()` function manipulates the value of the specified local
variable at the given call stack depth.

The call stack depth specifies the amount of levels up local variables should
be updated. A value of `0` refers to this `setlocal()` function call itself,
`1` to the function calling `setlocal()` and so on.

The variable to update might be either specified by name or by its index with
index numbers following the source code declaration order.

Returns a dictionary holding information about the updated variable.

Returns `null` if the stack depth exceeds the size of the current call stack.

Returns `null` if the invocation at the given stack depth is a C call.

Returns `null` if the given variable name is not found or the given variable
index is invalid.

**Kind**: instance method of [`debug`](#module_debug)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [level] | `number` | `1` | The amount of call stack levels up local variables should be updated. |
| variable | `string` \| `number` |  | The variable index or variable name to update. |
| [value] | `\*` | `` | The value to set the local variable to. |

### debug.getupval(target, variable) ⇒ [`UpvalInfo`](#module_debug.UpvalInfo)
Obtain captured variable (upvalue).

The `getupval()` function retrieves information about the specified captured
variable associated with the given function value or the invoked function at
the given call stack depth.

The call stack depth specifies the amount of levels up the function should be
selected to query associated captured variables for. A value of `0` refers to
this `getupval()` function call itself, `1` to the function calling
`getupval()` and so on.

The variable to query might be either specified by name or by its index with
index numbers following the source code declaration order.

Returns a dictionary holding information about the given variable.

Returns `null` if the given function value is not a closure.

Returns `null` if the stack depth exceeds the size of the current call stack.

Returns `null` if the invocation at the given stack depth is not a closure.

Returns `null` if the given variable name is not found or the given variable
index is invalid.

**Kind**: instance method of [`debug`](#module_debug)  

| Param | Type | Description |
| --- | --- | --- |
| target | `function` \| `number` | Either a function value referring to a closure to query upvalues for or a stack depth number selecting a closure that many levels up. |
| variable | `string` \| `number` | The variable index or variable name to obtain information for. |

### debug.setupval(target, variable, value) ⇒ [`UpvalInfo`](#module_debug.UpvalInfo)
Set upvalue.

The `setupval()` function manipulates the value of the specified captured
variable associated with the given function value or the invoked function at
the given call stack depth.

The call stack depth specifies the amount of levels up the function should be
selected to update associated captured variables for. A value of `0` refers
to this `setupval()` function call itself, `1` to the function calling
`setupval()` and so on.

The variable to update might be either specified by name or by its index with
index numbers following the source code declaration order.

Returns a dictionary holding information about the updated variable.

Returns `null` if the given function value is not a closure.

Returns `null` if the stack depth exceeds the size of the current call stack.

Returns `null` if the invocation at the given stack depth is not a closure.

Returns `null` if the given variable name is not found or the given variable
index is invalid.

**Kind**: instance method of [`debug`](#module_debug)  

| Param | Type | Description |
| --- | --- | --- |
| target | `function` \| `number` | Either a function value referring to a closure to update upvalues for or a stack depth number selecting a closure that many levels up. |
| variable | `string` \| `number` | The variable index or variable name to update. |
| value | `\*` | The value to set the variable to. |

### debug.StackTraceEntry : `Object`
**Kind**: static typedef of [`debug`](#module_debug)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| callee | `function` | The function that was called. |
| this | `\*` | The `this` context the function was called with. |
| mcall | `boolean` | Indicates whether the function was invoked as a method. |
| [strict] | `boolean` | Indicates whether the VM was running in strict mode when the function was called (only applicable to non-C, pure ucode calls). |
| [filename] | `string` | The name of the source file that called the function (only applicable to non-C, pure ucode calls). |
| [line] | `number` | The source line of the function call (only applicable to non-C, pure ucode calls). |
| [byte] | `number` | The source line offset of the function call (only applicable to non-C, pure ucode calls). |
| [context] | `string` | The surrounding source code context formatted as human-readable string, useful for generating debug messages (only applicable to non-C, pure ucode calls). |

### debug.SourcePosition : `Object`
**Kind**: static typedef of [`debug`](#module_debug)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| filename | `string` | The name of the source file that called this function. |
| line | `number` | The source line of the function call. |
| byte | `number` | The source line offset of the function call. |

### debug.UpvalRef : `Object`
**Kind**: static typedef of [`debug`](#module_debug)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| name | `string` | The name of the captured variable. |
| closed | `boolean` | Indicates whether the captured variable (upvalue) is closed or not. A closed upvalue means that the function value outlived the declaration scope of the captured variable. |
| value | `\*` | The current value of the captured variable. |
| [slot] | `number` | The stack slot of the captured variable. Only applicable to open (non-closed) captured variables. |

### debug.ValueInformation : `Object`
**Kind**: static typedef of [`debug`](#module_debug)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| type | `string` | The name of the value type, one of `integer`, `boolean`, `string`, `double`, `array`, `object`, `regexp`, `cfunction`, `closure`, `upvalue` or `resource`. |
| value | `\*` | The value itself. |
| tagged | `boolean` | Indicates whether the given value is internally stored as tagged pointer without an additional heap allocation. |
| [mark] | `boolean` | Indicates whether the value has it's mark bit set, which is used for loop detection during recursive object traversal on garbage collection cycles or complex value stringification. Only applicable to non-tagged values. |
| [refcount] | `number` | The current reference count of the value. Note that the `getinfo()` function places a reference to the value into the `value` field of the resulting information dictionary, so the ref count will always be at least 2 - one reference for the function call argument and one for the value property in the result dictionary. Only applicable to non-tagged values. |
| [unsigned] | `boolean` | Whether the number value is internally stored as unsigned integer. Only applicable to non-tagged integer values. |
| [address] | `number` | The address of the underlying C heap memory. Only applicable to non-tagged `string`, `array`, `object`, `cfunction` or `resource` values. |
| [length] | `number` | The length of the underlying string memory. Only applicable to non-tagged `string` values. |
| [count] | `number` | The amount of elements in the underlying memory structure. Only applicable to `array` and `object` values. |
| [constant] | `boolean` | Indicates whether the value is constant (immutable). Only applicable to `array` and `object` values. |
| [prototype] | `\*` | The associated prototype value, if any. Only applicable to `array`, `object` and `prototype` values. |
| [source] | `string` | The original regex source pattern. Only applicable to `regexp` values. |
| [icase] | `boolean` | Whether the compiled regex has the `i` (ignore case) flag set. Only applicable to `regexp` values. |
| [global] | `boolean` | Whether the compiled regex has the `g` (global) flag set. Only applicable to `regexp` values. |
| [newline] | `boolean` | Whether the compiled regex has the `s` (single line) flag set. Only applicable to `regexp` values. |
| [nsub] | `number` | The amount of capture groups within the regular expression. Only applicable to `regexp` values. |
| [name] | `string` | The name of the non-anonymous function. Only applicable to `cfunction` and `closure` values. Set to `null` for anonymous function values. |
| [arrow] | `boolean` | Indicates whether the ucode function value is an arrow function. Only applicable to `closure` values. |
| [module] | `boolean` | Indicates whether the ucode function value is a module entry point. Only applicable to `closure` values. |
| [strict] | `boolean` | Indicates whether the function body will be executed in strict mode. Only applicable to `closure` values. |
| [vararg] | `boolean` | Indicates whether the ucode function takes a variable number of arguments. Only applicable to `closure` values. |
| [nargs] | `number` | The number of arguments expected by the ucode function, excluding a potential final variable argument ellipsis. Only applicable to `closure` values. |
| [argnames] | `Array.<string>` | The names of the function arguments in their declaration order. Only applicable to `closure` values. |
| [nupvals] | `number` | The number of upvalues associated with the ucode function. Only applicable to `closure` values. |
| [upvals] | [`Array.<UpvalRef>`](#module_debug.UpvalRef) | An array of upvalue information objects. Only applicable to `closure` values. |
| [filename] | `string` | The path of the source file the function was declared in. Only applicable to `closure` values. |
| [line] | `number` | The source line number the function was declared at. Only applicable to `closure` values. |
| [byte] | `number` | The source line offset the function was declared at. Only applicable to `closure` values. |
| [type] | `string` | The resource type name. Only applicable to `resource` values. |

### debug.LocalInfo : `Object`
**Kind**: static typedef of [`debug`](#module_debug)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| index | `number` | The index of the local variable. |
| name | `string` | The name of the local variable. |
| value | `\*` | The current value of the local variable. |
| linefrom | `number` | The source line number of the local variable declaration. |
| bytefrom | `number` | The source line offset of the local variable declaration. |
| lineto | `number` | The source line number where the local variable goes out of scope. |
| byteto | `number` | The source line offset where the local vatiable goes out of scope. |

### debug.UpvalInfo : `Object`
**Kind**: static typedef of [`debug`](#module_debug)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| index | `number` | The index of the captured variable (upvalue). |
| name | `string` | The name of the captured variable. |
| closed | `boolean` | Indicates whether the captured variable is closed or not. A closed upvalue means that the function outlived the declaration scope of the captured variable. |
| value | `\*` | The current value of the captured variable. |
