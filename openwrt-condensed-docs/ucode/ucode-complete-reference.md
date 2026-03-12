---
module: "ucode"
total_token_count: 79937
section_count: 14
is_monolithic: true
generated: "2026-03-12T09:10:08.410847+00:00"
---

# ucode Complete Reference

> **Contains:** 14 documents concatenated
> **Tokens:** ~79937 (cl100k_base)

---

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

---

# ucode module: digest

> **Live docs:** https://ucode.mein.io/module-digest.html

---

## Digest Functions

The `digest` module bundles various digest functions.

### digest.md5(str) ⇒ `string`
Calculates the MD5 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```ucode
md5("This is a test");  // Returns "ce114e4501d2f4e2dcea3e17b546f339"
md5(123);               // Returns null
```

### digest.sha1(str) ⇒ `string`
Calculates the SHA1 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```ucode
sha1("This is a test");  // Returns "a54d88e06612d820bc3be72877c74f257b561b19"
sha1(123);               // Returns null
```

### digest.sha256(str) ⇒ `string`
Calculates the SHA256 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```ucode
sha256("This is a test");  // Returns "c7be1ed902fb8dd4d48997c6452f5d7e509fbcdbe2808b16bcf4edce4c07d14e"
sha256(123);               // Returns null
```

### digest.md2(str) ⇒ `string`
Calculates the MD2 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```ucode
md2("This is a test");  // Returns "dc378580fd0722e56b82666a6994c718"
md2(123);               // Returns null
```

### digest.md4(str) ⇒ `string`
Calculates the MD4 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```ucode
md4("This is a test");  // Returns "3b487cf6856af7e330bc4b1b7d977ef8"
md4(123);               // Returns null
```

### digest.sha384(str) ⇒ `string`
Calculates the SHA384 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```ucode
sha384("This is a test");  // Returns "a27c7667e58200d4c0688ea136968404a0da366b1a9fc19bb38a0c7a609a1eef2bcc82837f4f4d92031a66051494b38c"
sha384(123);               // Returns null
```

### digest.sha512(str) ⇒ `string`
Calculates the SHA512 hash of string and returns that hash.

Returns `null` if a non-string argument is given.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| str | `string` | The string to hash. |

**Example**  
```ucode
sha512("This is a test");  // Returns "a028d4f74b602ba45eb0a93c9a4677240dcf281a1a9322f183bd32f0bed82ec72de9c3957b2f4c9a1ccf7ed14f85d73498df38017e703d47ebb9f0b3bf116f69"
sha512(123);               // Returns null
```

### digest.md5\_file(path) ⇒ `string`
Calculates the MD5 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

### digest.sha1\_file(path) ⇒ `string`
Calculates the SHA1 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

### digest.sha256\_file(path) ⇒ `string`
Calculates the SHA256 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

### digest.md2\_file(path) ⇒ `string`
Calculates the MD2 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

### digest.md4\_file(path) ⇒ `string`
Calculates the MD4 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

### digest.sha384\_file(path) ⇒ `string`
Calculates the SHA384 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

### digest.sha512\_file(path) ⇒ `string`
Calculates the SHA512 hash of a given file and returns that hash.

Returns `null` if an error occurred.

**Kind**: instance method of [`digest`](#module_digest)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |

---

# ucode module: fs

> **Live docs:** https://ucode.mein.io/module-fs.html

---

## Filesystem Access

The `fs` module provides functions for interacting with the file system.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { readlink, popen } from 'fs';

  let dest = readlink('/sys/class/net/eth0');
  let proc = popen('ps ww');
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as fs from 'fs';

  let dest = fs.readlink('/sys/class/net/eth0');
  let proc = fs.popen('ps ww');
  ```

Additionally, the filesystem module namespace may also be imported by invoking
the `ucode` interpreter with the `-lfs` switch.

### fs.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`fs`](#module_fs)  
**Example**  
```ucode
// Trigger file system error
unlink('/path/does/not/exist');

// Print error (should yield "No such file or directory")
print(error(), "\n");
```

### fs.popen(command, [mode]) ⇒ [`proc`](#module_fs.proc)
Starts a process and returns a handle representing the executed process.

The handle will be connected to the process stdin or stdout, depending on the
value of the mode argument.

The mode argument may be either "r" to open the process for reading (connect
to its stdin) or "w" to open the process for writing (connect to its stdout).

The mode character "r" or "w" may be optionally followed by "e" to apply the
FD_CLOEXEC flag onto the open descriptor.

Returns a process handle referring to the executed process.

Returns `null` if an error occurred.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| command | `string` |  | The command to be executed. |
| [mode] | `string` | `"\"r\""` | The open mode of the process handle. |

**Example**  
```ucode
// Open a process
const process = popen('command', 'r');
```

### fs.open(path, [mode], [perm]) ⇒ [`file`](#module_fs.file)
Opens a file.

The mode argument specifies the way the file is opened, it may
start with one of the following values:

| Mode    | Description                                                                                                   |
|---------|---------------------------------------------------------------------------------------------------------------|
| "r"     | Opens a file for reading. The file must exist.                                                                 |
| "w"     | Opens a file for writing. If the file exists, it is truncated. If the file does not exist, it is created.     |
| "a"     | Opens a file for appending. Data is written at the end of the file. If the file does not exist, it is created. |
| "r+"    | Opens a file for both reading and writing. The file must exist.                                              |
| "w+"    | Opens a file for both reading and writing. If the file exists, it is truncated. If the file does not exist, it is created. |
| "a+"    | Opens a file for both reading and appending. Data can be read and written at the end of the file. If the file does not exist, it is created. |

Additionally, the following flag characters may be appended to
the mode value:

| Flag    | Description                                                                                                   |
|---------|---------------------------------------------------------------------------------------------------------------|
| "x"     | Opens a file for exclusive creation. If the file exists, the `open` call fails.                             |
| "e"     | Opens a file with the `O_CLOEXEC` flag set, ensuring that the file descriptor is closed on `exec` calls.      |

If the mode is one of `"w…"` or `"a…"`, the permission argument
controls the filesystem permissions bits used when creating
the file.

Returns a file handle object associated with the opened file.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| path | `string` |  | The path to the file. |
| [mode] | `string` | `"\"r\""` | The file opening mode. |
| [perm] | `number` | `0o666` | The file creation permissions (for modes `w…` and `a…`) |

**Example**  
```ucode
// Open a file in read-only mode
const fileHandle = open('file.txt', 'r');
```

### fs.fdopen(fd, [mode]) ⇒ `Object`
Associates a file descriptor number with a file handle object.

The mode argument controls how the file handle object is opened
and must match the open mode of the underlying descriptor.

It may be set to one of the following values:

| Mode    | Description                                                                                                  |
|---------|--------------------------------------------------------------------------------------------------------------|
| "r"     | Opens a file stream for reading. The file descriptor must be valid and opened in read mode.                  |
| "w"     | Opens a file stream for writing. The file descriptor must be valid and opened in write mode.                 |
| "a"     | Opens a file stream for appending. The file descriptor must be valid and opened in write mode.               |
| "r+"    | Opens a file stream for both reading and writing. The file descriptor must be valid and opened in read/write mode. |
| "w+"    | Opens a file stream for both reading and writing. The file descriptor must be valid and opened in read/write mode. |
| "a+"    | Opens a file stream for both reading and appending. The file descriptor must be valid and opened in read/write mode. |

Returns the file handle object associated with the file descriptor.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| fd | `number` |  | The file descriptor. |
| [mode] | `string` | `"\"r\""` | The open mode. |

**Example**  
```ucode
// Associate file descriptors of stdin and stdout with handles
const stdinHandle = fdopen(0, 'r');
const stdoutHandle = fdopen(1, 'w');
```

### fs.dup2(oldfd, newfd) ⇒ `boolean`
Duplicates a file descriptor.

This function duplicates the file descriptor `oldfd` to `newfd`. If `newfd`
was previously open, it is silently closed before being reused.

Returns `true` on success.
Returns `null` on error.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| oldfd | `number` | The file descriptor to duplicate. |
| newfd | `number` | The file descriptor number to duplicate to. |

**Example**  
```ucode
// Redirect stderr to a log file
const logfile = open('/tmp/error.log', 'w');
dup2(logfile.fileno(), 2);
logfile.close();
```

### fs.opendir(path) ⇒ [`dir`](#module_fs.dir)
Opens a directory and returns a directory handle associated with the open
directory descriptor.

Returns a director handle referring to the open directory.

Returns `null` if an error occurred.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the directory. |

**Example**  
```ucode
// Open a directory
const directory = opendir('path/to/directory');
```

### fs.readlink(path) ⇒ `string`
Reads the target path of a symbolic link.

Returns a string containing the target path.

Returns `null` if an error occurred.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the symbolic link. |

**Example**  
```ucode
// Read the value of a symbolic link
const targetPath = readlink('symbolicLink');
```

### fs.stat(path) ⇒ [`FileStatResult`](#module_fs.FileStatResult)
Retrieves information about a file or directory.

Returns an object containing information about the file or directory.

Returns `null` if an error occurred, e.g. due to insufficient permissions.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file or directory. |

**Example**  
```ucode
// Get information about a file
const fileInfo = stat('path/to/file');
```

### fs.lstat(path) ⇒ [`FileStatResult`](#module_fs.FileStatResult)
Retrieves information about a file or directory, without following symbolic
links.

Returns an object containing information about the file or directory.

Returns `null` if an error occurred, e.g. due to insufficient permissions.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file or directory. |

**Example**  
```ucode
// Get information about a directory
const dirInfo = lstat('path/to/directory');
```

### fs.mkdir(path) ⇒ `boolean`
Creates a new directory.

Returns `true` if the directory was successfully created.

Returns `null` if an error occurred, e.g. due to inexistent path.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the new directory. |

**Example**  
```ucode
// Create a directory
mkdir('path/to/new-directory');
```

### fs.rmdir(path) ⇒ `boolean`
Removes the specified directory.

Returns `true` if the directory was successfully removed.

Returns `null` if an error occurred, e.g. due to inexistent path.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the directory to be removed. |

**Example**  
```ucode
// Remove a directory
rmdir('path/to/directory');
```

### fs.symlink(target, path) ⇒ `boolean`
Creates a new symbolic link.

Returns `true` if the symlink was successfully created.

Returns `null` if an error occurred, e.g. due to inexistent path.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| target | `string` | The target of the symbolic link. |
| path | `string` | The path of the symbolic link. |

**Example**  
```ucode
// Create a symbolic link
symlink('target', 'path/to/symlink');
```

### fs.unlink(path) ⇒ `boolean`
Removes the specified file or symbolic link.

Returns `true` if the unlink operation was successful.

Returns `null` if an error occurred, e.g. due to inexistent path.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file or symbolic link. |

**Example**  
```ucode
// Remove a file
unlink('path/to/file');
```

### fs.getcwd() ⇒ `string`
Retrieves the current working directory.

Returns a string containing the current working directory path.

Returns `null` if an error occurred.

**Kind**: instance method of [`fs`](#module_fs)  
**Example**  
```ucode
// Get the current working directory
const cwd = getcwd();
```

### fs.chdir(path) ⇒ `boolean`
Changes the current working directory to the specified path.

Returns `true` if the permission change was successful.

Returns `null` if an error occurred, e.g. due to insufficient permissions or
invalid arguments.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the new working directory. |

**Example**  
```ucode
// Change the current working directory
chdir('new-directory');
```

### fs.chmod(path, mode) ⇒ `boolean`
Changes the permission mode bits of a file or directory.

Returns `true` if the permission change was successful.

Returns `null` if an error occurred, e.g. due to insufficient permissions or
invalid arguments.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file or directory. |
| mode | `number` | The new mode (permissions). |

**Example**  
```ucode
// Change the mode of a file
chmod('path/to/file', 0o644);
```

### fs.chown(path, [uid], [gid]) ⇒ `boolean`
Changes the owner and group of a file or directory.

The user and group may be specified either as uid or gid number respectively,
or as a string containing the user or group name, in which case it is
resolved to the proper uid/gid first.

If either the user or group parameter is omitted or given as `-1`,
it is not changed.

Returns `true` if the ownership change was successful.

Returns `null` if an error occurred or if a user/group name cannot be
resolved to a uid/gid value.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| path | `string` |  | The path to the file or directory. |
| [uid] | `number` \| `string` | `-1` | The new owner's user ID. When given as number, it is used as-is, when given as string, the user name is resolved to the corresponding uid first. |
| [gid] | `number` \| `string` | `-1` | The new group's ID. When given as number, it is used as-is, when given as string, the group name is resolved to the corresponding gid first. |

**Example**  
```ucode
// Change the owner of a file
chown('path/to/file', 1000);

// Change the group of a directory
chown('/htdocs/', null, 'www-data');
```

### fs.rename(oldPath, newPath) ⇒ `boolean`
Renames or moves a file or directory.

Returns `true` if the rename operation was successful.

Returns `null` if an error occurred.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| oldPath | `string` | The current path of the file or directory. |
| newPath | `string` | The new path of the file or directory. |

**Example**  
```ucode
// Rename a file
rename('old-name.txt', 'new-name.txt');
```

### fs.dirname(path) ⇒ `string`
Retrieves the directory name of a path.

Returns the directory name component of the specified path.

Returns `null` if the path argument is not a string.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to extract the directory name from. |

**Example**  
```ucode
// Get the directory name of a path
const directoryName = dirname('/path/to/file.txt');
```

### fs.basename(path) ⇒ `string`
Retrieves the base name of a path.

Returns the base name component of the specified path.

Returns `null` if the path argument is not a string.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to extract the base name from. |

**Example**  
```ucode
// Get the base name of a path
const baseName = basename('/path/to/file.txt');
```

### fs.lsdir(path) ⇒ `Array.<string>`
Lists the content of a directory.

Returns a sorted array of the names of files and directories in the specified
directory.

Returns `null` if an error occurred, e.g. if the specified directory cannot
be opened.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the directory. |

**Example**  
```ucode
// List the content of a directory
const fileList = lsdir('/path/to/directory');
```

### fs.mkstemp([template]) ⇒ [`file`](#module_fs.file)
Creates a unique, ephemeral temporary file.

Creates a new temporary file, opens it in read and write mode, unlinks it and
returns a file handle object referring to the yet open but deleted file.

Upon closing the handle, the associated file will automatically vanish from
the system.

The optional path template argument may be used to override the path and name
chosen for the temporary file. If the path template contains no path element,
`/tmp/` is prepended, if it does not end with `XXXXXX`, then  * `.XXXXXX` is
appended to it. The `XXXXXX` sequence is replaced with a random value
ensuring uniqueness of the temporary file name.

Returns a file handle object referring to the ephemeral file on success.

Returns `null` if an error occurred, e.g. on insufficient permissions or
inaccessible directory.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [template] | `string` | `"\"/tmp/XXXXXX\""` | The path template to use when forming the temporary file name. |

**Example**  
```ucode
// Create a unique temporary file in the current working directory
const tempFile = mkstemp('./data-XXXXXX');
```

### fs.mkdtemp([template]) ⇒ `string`
Creates a unique temporary directory based on the given template.

If the template argument is given and contains a relative path, the created
directory will be placed relative to the current working directory.

If the template argument is given and contains an absolute path, the created
directory will be placed relative to the given directory.

If the template argument is given but does not contain a directory separator,
the directory will be placed in `/tmp/`.

If no template argument is given, the default `/tmp/XXXXXX` is used.

The template argument must end with six consecutive X characters (`XXXXXX`),
which will be replaced with a random string to create the unique directory name.
If the template does not end with `XXXXXX`, it will be automatically appended.

Returns a string containing the path of the created directory on success.

Returns `null` if an error occurred, e.g. on insufficient permissions or
inaccessible directory.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [template] | `string` | `"\"/tmp/XXXXXX\""` | The path template to use when forming the temporary directory name. |

**Example**  
```ucode
// Create a unique temporary directory in the current working directory
const tempDir = mkdtemp('./data-XXXXXX');
```

### fs.access(path, [mode]) ⇒ `boolean`
Checks the accessibility of a file or directory.

The optional modes argument specifies the access modes which should be
checked. A file is only considered accessible if all access modes specified
in the modes argument are possible.

The following modes are recognized:

| Mode | Description                           |
|------|---------------------------------------|
| "r"  | Tests whether the file is readable.   |
| "w"  | Tests whether the file is writable.   |
| "x"  | Tests whether the file is executable. |
| "f"  | Tests whether the file exists.        |

Returns `true` if the given path is accessible or `false` when it is not.

Returns `null` if an error occurred, e.g. due to inaccessible intermediate
path components, invalid path arguments etc.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| path | `string` |  | The path to the file or directory. |
| [mode] | `number` | `"f"` | Optional access mode. |

**Example**  
```ucode
// Check file read and write accessibility
const isAccessible = access('path/to/file', 'rw');

// Check execute permissions
const mayExecute = access('/usr/bin/example', 'x');
```

### fs.readfile(path, [limit]) ⇒ `string`
Reads the content of a file, optionally limited to the given amount of bytes.

Returns a string containing the file contents.

Returns `null` if an error occurred, e.g. due to insufficient permissions.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |
| [limit] | `number` | Number of bytes to limit the result to. When omitted, the entire content is returned. |

**Example**  
```ucode
// Read first 100 bytes of content
const content = readfile('path/to/file', 100);

// Read entire file content
const content = readfile('path/to/file');
```

### fs.writefile(path, data, [limit]) ⇒ `number`
Writes the given data to a file, optionally truncated to the given amount
of bytes.

In case the given data is not a string, it is converted to a string before
being written into the file. String values are written as-is, integer and
double values are written in decimal notation, boolean values are written as
`true` or `false` while arrays and objects are converted to their JSON
representation before being written into the file. The `null` value is
represented by an empty string so `writefile(…, null)` would write an empty
file. Resource values are written in the form `<type address>`, e.g.
`<fs.file 0x7f60f0981760>`.

If resource, array or object values contain a `tostring()` function in their
prototypes, then this function is invoked to obtain an alternative string
representation of the value.

If a file already exists at the given path, it is truncated. If no file
exists, it is created with default permissions 0o666 masked by the currently
effective umask.

Returns the number of bytes written.

Returns `null` if an error occurred, e.g. due to insufficient permissions.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file. |
| data | `\*` | The data to be written. |
| [limit] | `number` | Truncates the amount of data to be written to the specified amount of bytes. When omitted, the entire content is written. |

**Example**  
```ucode
// Write string to a file
const bytesWritten = writefile('path/to/file', 'Hello, World!');

// Write object as JSON to a file and limit to 1024 bytes at most
const obj = { foo: "Hello world", bar: true, baz: 123 };
const bytesWritten = writefile('debug.txt', obj, 1024);
```

### fs.realpath(path) ⇒ `string`
Resolves the absolute path of a file or directory.

Returns a string containing the resolved path.

Returns `null` if an error occurred, e.g. due to insufficient permissions.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the file or directory. |

**Example**  
```ucode
// Resolve the absolute path of a file
const absolutePath = realpath('path/to/file', 'utf8');
```

### fs.pipe() ⇒ [`Array.<file>`](#module_fs.file)
Creates a pipe and returns file handle objects associated with the read- and
write end of the pipe respectively.

Returns a two element array containing both a file handle object open in read
mode referring to the read end of the pipe and a file handle object open in
write mode referring to the write end of the pipe.

Returns `null` if an error occurred.

**Kind**: instance method of [`fs`](#module_fs)  
**Example**  
```ucode
// Create a pipe
const pipeHandles = pipe();
pipeHandles[1].write("Hello world\n");
print(pipeHandles[0].read("line"));
```

### fs.proc
**Kind**: static class of [`fs`](#module_fs)  
**See**: [popen()](#module_fs+popen)  

* [.proc](#module_fs.proc)
    * [.close()](#module_fs.proc+close) ⇒ `number`
    * [.read(length)](#module_fs.proc+read) ⇒ `string`
    * [.write(data)](#module_fs.proc+write) ⇒ `number`
    * [.flush()](#module_fs.proc+flush) ⇒ `boolean`
    * [.fileno()](#module_fs.proc+fileno) ⇒ `number`
    * [.error()](#module_fs.proc+error) ⇒ `string`

#### proc.close() ⇒ `number`
Closes the program handle and awaits program termination.

Upon calling `close()` on the handle, the program's input or output stream
(depending on the open mode) is closed. Afterwards, the function awaits the
termination of the underlying program and returns its exit code.

- When the program was terminated by a signal, the return value will be the
  negative signal number, e.g. `-9` for SIGKILL.

- When the program terminated normally, the return value will be the positive
  exit code of the program.

Returns a negative signal number if the program was terminated by a signal.

Returns a positive exit code if the program terminated normally.

Returns `null` if an error occurred.

**Kind**: instance method of [`proc`](#module_fs.proc)  

#### proc.read(length) ⇒ `string`
Reads a chunk of data from the program handle.

The length argument may be either a positive number of bytes to read, in
which case the read call returns up to that many bytes, or a string to
specify a dynamic read size.

 - If length is a number, the method will read the specified number of bytes
   from the handle. Reading stops after the given amount of bytes or after
   encountering EOF, whatever comes first.

 - If length is the string "line", the method will read an entire line,
   terminated by "\n" (a newline), from the handle. Reading stops at the next
   newline or when encountering EOF. The returned data will contain the
   terminating newline character if one was read.

 - If length is the string "all", the method will read from the handle until
   encountering EOF and return the complete contents.

 - If length is a single character string, the method will read from the
   handle until encountering the specified character or upon encountering
   EOF. The returned data will contain the terminating character if one was
   read.

Returns a string containing the read data.

Returns an empty string on EOF.

Returns `null` if a read error occurred.

**Kind**: instance method of [`proc`](#module_fs.proc)  

| Param | Type | Description |
| --- | --- | --- |
| length | `number` \| `string` | The length of data to read. Can be a number, the string "line", the string "all", or a single character string. |

**Example**  
```ucode
const fp = popen("command", "r");

// Example 1: Read 10 bytes from the handle
const chunk = fp.read(10);

// Example 2: Read the handle line by line
for (let line = fp.read("line"); length(line); line = fp.read("line"))
  print(line);

// Example 3: Read the complete contents from the handle
const content = fp.read("all");

// Example 4: Read until encountering the character ':'
const field = fp.read(":");
```

#### proc.write(data) ⇒ `number`
Writes a chunk of data to the program handle.

In case the given data is not a string, it is converted to a string before
being written to the program's stdin. String values are written as-is,
integer and double values are written in decimal notation, boolean values are
written as `true` or `false` while arrays and objects are converted to their
JSON representation before being written. The `null` value is represented by
an empty string so `proc.write(null)` would be a no-op. Resource values are
written in the form `<type address>`, e.g. `<fs.file 0x7f60f0981760>`.

If resource, array or object values contain a `tostring()` function in their
prototypes, then this function is invoked to obtain an alternative string
representation of the value.

Returns the number of bytes written.

Returns `null` if a write error occurred.

**Kind**: instance method of [`proc`](#module_fs.proc)  

| Param | Type | Description |
| --- | --- | --- |
| data | `\*` | The data to be written. |

**Example**  
```ucode
const fp = popen("command", "w");

fp.write("Hello world!\n");
```

#### proc.flush() ⇒ `boolean`
Forces a write of all buffered data to the underlying handle.

Returns `true` if the data was successfully flushed.

Returns `null` on error.

**Kind**: instance method of [`proc`](#module_fs.proc)  

#### proc.fileno() ⇒ `number`
Obtains the number of the handle's underlying file descriptor.

Returns the descriptor number.

Returns `null` on error.

**Kind**: instance method of [`proc`](#module_fs.proc)  

#### proc.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`proc`](#module_fs.proc)  
**Example**  
```ucode
// Trigger file system error
unlink('/path/does/not/exist');

// Print error (should yield "No such file or directory")
print(error(), "\n");
```

### fs.file
**Kind**: static class of [`fs`](#module_fs)  
**See**

- [open()](#module_fs+open)
- [fdopen()](#module_fs+fdopen)
- [mkstemp()](#module_fs+mkstemp)
- [pipe()](#module_fs+pipe)

* [.file](#module_fs.file)
    * [.close()](#module_fs.file+close) ⇒ `boolean`
    * [.read(length)](#module_fs.file+read) ⇒ `string`
    * [.write(data)](#module_fs.file+write) ⇒ `number`
    * [.seek([offset], [position])](#module_fs.file+seek) ⇒ `boolean`
    * [.truncate([offset])](#module_fs.file+truncate) ⇒ `boolean`
    * [.lock([op])](#module_fs.file+lock) ⇒ `boolean`
    * [.tell()](#module_fs.file+tell) ⇒ `number`
    * [.isatty()](#module_fs.file+isatty) ⇒ `boolean`
    * [.flush()](#module_fs.file+flush) ⇒ `boolean`
    * [.fileno()](#module_fs.file+fileno) ⇒ `number`
    * [.ioctl(direction, type, num, [value])](#module_fs.file+ioctl) ⇒ `number` \| `string`
    * [.error()](#module_fs.file+error) ⇒ `string`

#### file.close() ⇒ `boolean`
Closes the file handle.

Upon calling `close()` on the handle, buffered data is flushed and the
underlying file descriptor is closed.

Returns `true` if the handle was properly closed.

Returns `null` if an error occurred.

**Kind**: instance method of [`file`](#module_fs.file)  

#### file.read(length) ⇒ `string`
Reads a chunk of data from the file handle.

The length argument may be either a positive number of bytes to read, in
which case the read call returns up to that many bytes, or a string to
specify a dynamic read size.

 - If length is a number, the method will read the specified number of bytes
   from the handle. Reading stops after the given amount of bytes or after
   encountering EOF, whatever comes first.

 - If length is the string "line", the method will read an entire line,
   terminated by "\n" (a newline), from the handle. Reading stops at the next
   newline or when encountering EOF. The returned data will contain the
   terminating newline character if one was read.

 - If length is the string "all", the method will read from the handle until
   encountering EOF and return the complete contents.

 - If length is a single character string, the method will read from the
   handle until encountering the specified character or upon encountering
   EOF. The returned data will contain the terminating character if one was
   read.

Returns a string containing the read data.

Returns an empty string on EOF.

Returns `null` if a read error occurred.

**Kind**: instance method of [`file`](#module_fs.file)  

| Param | Type | Description |
| --- | --- | --- |
| length | `number` \| `string` | The length of data to read. Can be a number, the string "line", the string "all", or a single character string. |

**Example**  
```ucode
const fp = open("file.txt", "r");

// Example 1: Read 10 bytes from the handle
const chunk = fp.read(10);

// Example 2: Read the handle line by line
for (let line = fp.read("line"); length(line); line = fp.read("line"))
  print(line);

// Example 3: Read the complete contents from the handle
const content = fp.read("all");

// Example 4: Read until encountering the character ':'
const field = fp.read(":");
```

#### file.write(data) ⇒ `number`
Writes a chunk of data to the file handle.

In case the given data is not a string, it is converted to a string before
being written into the file. String values are written as-is, integer and
double values are written in decimal notation, boolean values are written as
`true` or `false` while arrays and objects are converted to their JSON
representation before being written. The `null` value is represented by an
empty string so `file.write(null)` would be a no-op. Resource values are
written in the form `<type address>`, e.g. `<fs.file 0x7f60f0981760>`.

If resource, array or object values contain a `tostring()` function in their
prototypes, then this function is invoked to obtain an alternative string
representation of the value.

Returns the number of bytes written.

Returns `null` if a write error occurred.

**Kind**: instance method of [`file`](#module_fs.file)  

| Param | Type | Description |
| --- | --- | --- |
| data | `\*` | The data to be written. |

**Example**  
```ucode
const fp = open("file.txt", "w");

fp.write("Hello world!\n");
```

#### file.seek([offset], [position]) ⇒ `boolean`
Set file read position.

Set the read position of the open file handle to the given offset and
position.

Returns `true` if the read position was set.

Returns `null` if an error occurred.

**Kind**: instance method of [`file`](#module_fs.file)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [offset] | `number` | `0` | The offset in bytes. |
| [position] | `number` | `0` | The position of the offset. | Position | Description                                                                                  | |----------|----------------------------------------------------------------------------------------------| | `0`      | The given offset is relative to the start of the file. This is the default value if omitted. | | `1`      | The given offset is relative to the current read position.                                   | | `2`      | The given offset is relative to the end of the file.                                         | |

**Example**  
```ucode
const fp = open("file.txt", "r");

print(fp.read(100), "\n");  // read 100 bytes...
fp.seek(0, 0);              // ... and reset position to start of file
print(fp.read(100), "\n");  // ... read same 100 bytes again

fp.seek(10, 1);  // skip 10 bytes forward, relative to current offset ...
fp.tell();       // ... position is at 110 now

fp.seek(-10, 2);            // set position to ten bytes before EOF ...
print(fp.read(100), "\n");  // ... reads 10 bytes at most
```

#### file.truncate([offset]) ⇒ `boolean`
Truncate file to a given size

Returns `true` if the file was successfully truncated.

Returns `null` if an error occurred.

**Kind**: instance method of [`file`](#module_fs.file)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [offset] | `number` | `0` | The offset in bytes. |

#### file.lock([op]) ⇒ `boolean`
Locks or unlocks a file.

The mode argument specifies lock/unlock operation flags.

| Flag    | Description                  |
|---------|------------------------------|
| "s"     | shared lock                  |
| "x"     | exclusive lock               |
| "n"     | don't block when locking     |
| "u"     | unlock                       |

Returns `true` if the file was successfully locked/unlocked.

Returns `null` if an error occurred.

**Kind**: instance method of [`file`](#module_fs.file)  

| Param | Type | Description |
| --- | --- | --- |
| [op] | `string` | The lock operation flags |

#### file.tell() ⇒ `number`
Obtain current read position.

Obtains the current, absolute read position of the open file.

Returns an integer containing the current read offset in bytes.

Returns `null` if an error occurred.

**Kind**: instance method of [`file`](#module_fs.file)  

#### file.isatty() ⇒ `boolean`
Check for TTY.

Checks whether the open file handle refers to a TTY (terminal) device.

Returns `true` if the handle refers to a terminal.

Returns `false` if the handle refers to another kind of file.

Returns `null` on error.

**Kind**: instance method of [`file`](#module_fs.file)  

#### file.flush() ⇒ `boolean`
Forces a write of all buffered data to the underlying handle.

Returns `true` if the data was successfully flushed.

Returns `null` on error.

**Kind**: instance method of [`file`](#module_fs.file)  

#### file.fileno() ⇒ `number`
Obtains the number of the handle's underlying file descriptor.

Returns the descriptor number.

Returns `null` on error.

**Kind**: instance method of [`file`](#module_fs.file)  

#### file.ioctl(direction, type, num, [value]) ⇒ `number` \| `string`
Performs an ioctl operation on the file.

The direction parameter specifies who is reading and writing,
from the user's point of view. It can be one of the following values:

| Direction      | Description                                                                       |
|----------------|-----------------------------------------------------------------------------------|
| IOC_DIR_NONE   | neither userspace nor kernel is writing, ioctl is executed without passing data.  |
| IOC_DIR_WRITE  | userspace is writing and kernel is reading.                                       |
| IOC_DIR_READ   | kernel is writing and userspace is reading.                                       |
| IOC_DIR_RW     | userspace is writing and kernel is writing back into the data structure.          |

Returns the result of the ioctl operation; for `IOC_DIR_READ` and
`IOC_DIR_RW` this is a string containing the data, otherwise a number as
return code.

In case of an error, null is returned and error details are available via
[error()](#module_fs+error).

**Kind**: instance method of [`file`](#module_fs.file)  

| Param | Type | Description |
| --- | --- | --- |
| direction | `number` | The direction of the ioctl operation. Use constants IOC_DIR_*. |
| type | `number` | The ioctl type (see https://www.kernel.org/doc/html/latest/userspace-api/ioctl/ioctl-number.html) |
| num | `number` | The ioctl sequence number. |
| [value] | `number` \| `string` | The value to pass to the ioctl system call. For `IOC_DIR_NONE`, this argument is ignored. With `IOC_DIR_READ`, the value should be a positive integer specifying the number of bytes to expect from the kernel. For the other directions, `IOC_DIR_WRITE` and `IOC_DIR_RW`, that value parameter must be a string, serving as buffer for the data to send. |

#### file.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`file`](#module_fs.file)  
**Example**  
```ucode
// Trigger file system error
unlink('/path/does/not/exist');

// Print error (should yield "No such file or directory")
print(error(), "\n");
```

### fs.dir
**Kind**: static class of [`fs`](#module_fs)  
**See**: [opendir()](#module_fs+opendir)  

* [.dir](#module_fs.dir)
    * [.fileno()](#module_fs.dir+fileno) ⇒ `number`
    * [.read()](#module_fs.dir+read) ⇒ `string`
    * [.tell()](#module_fs.dir+tell) ⇒ `number`
    * [.seek(offset)](#module_fs.dir+seek) ⇒ `boolean`
    * [.close()](#module_fs.dir+close) ⇒ `boolean`
    * [.error()](#module_fs.dir+error) ⇒ `string`

#### dir.fileno() ⇒ `number`
Obtains the number of the handle's underlying file descriptor.

Returns the descriptor number.

Returns `null` on error.

**Kind**: instance method of [`dir`](#module_fs.dir)  

#### dir.read() ⇒ `string`
Read the next entry from the open directory.

Returns a string containing the entry name.

Returns `null` if there are no more entries to read.

Returns `null` if an error occurred.

**Kind**: instance method of [`dir`](#module_fs.dir)  

#### dir.tell() ⇒ `number`
Obtain current read position.

Returns the current read position in the open directory handle which can be
passed back to the `seek()` function to return to this position. This is
mainly useful to read an open directory handle (or specific items) multiple
times.

Returns an integer referring to the current position.

Returns `null` if an error occurred.

**Kind**: instance method of [`dir`](#module_fs.dir)  

#### dir.seek(offset) ⇒ `boolean`
Set read position.

Sets the read position within the open directory handle to the given offset
value. The offset value should be obtained by a previous call to `tell()` as
the specific integer values are implementation defined.

Returns `true` if the read position was set.

Returns `null` if an error occurred.

**Kind**: instance method of [`dir`](#module_fs.dir)  

| Param | Type | Description |
| --- | --- | --- |
| offset | `number` | Position value obtained by `tell()`. |

**Example**  
```ucode
const handle = opendir("/tmp");
const begin = handle.tell();

print(handle.read(), "\n");

handle.seek(begin);

print(handle.read(), "\n");  // prints the first entry again
```

#### dir.close() ⇒ `boolean`
Closes the directory handle.

Closes the underlying file descriptor referring to the opened directory.

Returns `true` if the handle was properly closed.

Returns `null` if an error occurred.

**Kind**: instance method of [`dir`](#module_fs.dir)  

#### dir.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`dir`](#module_fs.dir)  
**Example**  
```ucode
// Trigger file system error
unlink('/path/does/not/exist');

// Print error (should yield "No such file or directory")
print(error(), "\n");
```

### fs.FileStatResult : `Object`
**Kind**: static typedef of [`fs`](#module_fs)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| dev | `Object` | The device information. |
| dev.major | `number` | The major device number. |
| dev.minor | `number` | The minor device number. |
| perm | `Object` | The file permissions. |
| perm.setuid | `boolean` | Whether the setuid bit is set. |
| perm.setgid | `boolean` | Whether the setgid bit is set. |
| perm.sticky | `boolean` | Whether the sticky bit is set. |
| perm.user_read | `boolean` | Whether the file is readable by the owner. |
| perm.user_write | `boolean` | Whether the file is writable by the owner. |
| perm.user_exec | `boolean` | Whether the file is executable by the owner. |
| perm.group_read | `boolean` | Whether the file is readable by the group. |
| perm.group_write | `boolean` | Whether the file is writable by the group. |
| perm.group_exec | `boolean` | Whether the file is executable by the group. |
| perm.other_read | `boolean` | Whether the file is readable by others. |
| perm.other_write | `boolean` | Whether the file is writable by others. |
| perm.other_exec | `boolean` | Whether the file is executable by others. |
| inode | `number` | The inode number. |
| mode | `number` | The file mode. |
| nlink | `number` | The number of hard links. |
| uid | `number` | The user ID of the owner. |
| gid | `number` | The group ID of the owner. |
| size | `number` | The file size in bytes. |
| blksize | `number` | The block size for file system I/O. |
| blocks | `number` | The number of 512-byte blocks allocated for the file. |
| atime | `number` | The timestamp when the file was last accessed. |
| mtime | `number` | The timestamp when the file was last modified. |
| ctime | `number` | The timestamp when the file status was last changed. |
| type | `string` | The type of the file ("directory", "file", etc.). |

---

# ucode module: io

> **Live docs:** https://ucode.mein.io/module-io.html

---

## I/O Operations

The `io` module provides object-oriented access to UNIX file descriptors.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { open, O_RDWR } from 'io';

  let handle = open('/tmp/test.txt', O_RDWR);
  handle.write('Hello World\n');
  handle.close();
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as io from 'io';

  let handle = io.open('/tmp/test.txt', io.O_RDWR);
  handle.write('Hello World\n');
  handle.close();
  ```

Additionally, the io module namespace may also be imported by invoking
the `ucode` interpreter with the `-lio` switch.

### io.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`io`](#module_io)  
**Example**  
```ucode
// Trigger an error
io.open('/path/does/not/exist');

// Print error (should yield "No such file or directory")
print(io.error(), "\n");
```

### io.new(fd) ⇒ [`handle`](#module_io.handle)
Creates an io.handle from a file descriptor number.

Wraps the given file descriptor number in an io.handle object.

Returns an io.handle object.

Returns `null` if an error occurred.

**Kind**: instance method of [`io`](#module_io)  

| Param | Type | Description |
| --- | --- | --- |
| fd | `number` | The file descriptor number. |

**Example**  
```ucode
// Wrap stdin
const stdin = io.new(0);
const data = stdin.read(100);
```

### io.open(path, [flags], [mode]) ⇒ [`handle`](#module_io.handle)
Opens a file and returns an io.handle.

Opens the specified file with the given flags and mode, returning an
io.handle wrapping the resulting file descriptor.

Returns an io.handle object.

Returns `null` if an error occurred.

**Kind**: instance method of [`io`](#module_io)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| path | `string` |  | The path to the file. |
| [flags] | `number` | `O_RDONLY` | The open flags (O_RDONLY, O_WRONLY, O_RDWR, etc.). |
| [mode] | `number` | `0o666` | The file creation mode (used with O_CREAT). |

**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDWR | O_CREAT, 0o644);
handle.write('Hello World\n');
handle.close();
```

### io.pipe() ⇒ [`Array.<handle>`](#module_io.handle)
Creates a pipe.

Creates a unidirectional data channel (pipe) that can be used for
inter-process communication. Returns an array containing two io.handle
objects: the first is the read end of the pipe, the second is the write end.

Data written to the write end can be read from the read end.

Returns an array `[read_handle, write_handle]` on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`io`](#module_io)  
**Example**  
```ucode
const pipe_handles = io.pipe();
const reader = pipe_handles[0];
const writer = pipe_handles[1];
writer.write('Hello from pipe!');
const data = reader.read(100);
print(data, "\n");  // Prints: Hello from pipe!
```

### io.from(value) ⇒ [`handle`](#module_io.handle)
Creates an io.handle from various value types.

Creates an io.handle by extracting the file descriptor from the given value.
The value can be:
- An integer file descriptor number
- An [fs.file](../L2-semantic/ucode/c_source-api-module-fs.md), [fs.proc](../L2-semantic/ucode/c_source-api-module-fs.md), or socket resource
- Any object/array/resource with a fileno() method

Returns an io.handle object.

Returns `null` if an error occurred or the value cannot be converted.

**Kind**: instance method of [`io`](#module_io)  

| Param | Type | Description |
| --- | --- | --- |
| value | `\*` | The value to convert. |

**Example**  
```ucode
import { open as fsopen } from 'fs';
const fp = fsopen('/tmp/test.txt', 'r');
const handle = io.from(fp);
const data = handle.read(100);
```

### io.handle
**Kind**: static class of [`io`](#module_io)  
**See**

- [new()](#module_io+new)
- [open()](#module_io+open)
- [from()](#module_io+from)

* [.handle](#module_io.handle)
    * [.ptsname()](#module_io.handle+ptsname) ⇒ `string`
    * [.tcgetattr()](#module_io.handle+tcgetattr) ⇒ `object`
    * [.tcsetattr(attrs, [when])](#module_io.handle+tcsetattr) ⇒ `boolean`
    * [.grantpt()](#module_io.handle+grantpt) ⇒ `boolean`
    * [.unlockpt()](#module_io.handle+unlockpt) ⇒ `boolean`
    * [.read(length)](#module_io.handle+read) ⇒ `string`
    * [.write(data)](#module_io.handle+write) ⇒ `number`
    * [.seek([offset], [whence])](#module_io.handle+seek) ⇒ `boolean`
    * [.tell()](#module_io.handle+tell) ⇒ `number`
    * [.dup()](#module_io.handle+dup) ⇒ [`handle`](#module_io.handle)
    * [.dup2(newfd)](#module_io.handle+dup2) ⇒ `boolean`
    * [.fileno()](#module_io.handle+fileno) ⇒ `number`
    * [.fcntl(cmd, [arg])](#module_io.handle+fcntl) ⇒ `number` \| [`handle`](#module_io.handle)
    * [.ioctl(direction, type, num, [value])](#module_io.handle+ioctl) ⇒ `number` \| `string`
    * [.isatty()](#module_io.handle+isatty) ⇒ `boolean`
    * [.close()](#module_io.handle+close) ⇒ `boolean`
    * [.error()](#module_io.handle+error) ⇒ `string`

#### handle.ptsname() ⇒ `string`
Gets the name of the pseudo-terminal slave.

Returns the name of the pseudo-terminal slave device associated with
the master file descriptor.

Returns a string containing the slave device name.

Returns `null` if an error occurred or if the descriptor is not a
pseudo-terminal master.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const master = io.open('/dev/ptmx', O_RDWR);
const slave_name = master.ptsname();
print(slave_name, "\n");
```

#### handle.tcgetattr() ⇒ `object`
Gets terminal attributes.

Retrieves the terminal attributes for the file descriptor.

Returns an object containing terminal attributes (iflag, oflag, cflag, lflag,
ispeed, ospeed, and cc array).

Returns `null` if an error occurred or if the descriptor is not a terminal.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const handle = io.open('/dev/tty', O_RDWR);
const attrs = handle.tcgetattr();
if (attrs)
    print("Input flags: ", attrs.iflag, "\n");
```

#### handle.tcsetattr(attrs, [when]) ⇒ `boolean`
Sets terminal attributes.

Sets the terminal attributes for the file descriptor.

The attrs parameter should be an object with properties:
- iflag: input flags
- oflag: output flags
- cflag: control flags
- lflag: local flags
- ispeed: input speed
- ospeed: output speed
- cc: array of control characters (optional)

Returns `true` on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| attrs | `object` |  | The terminal attributes to set. |
| [when] | `number` | `0` | When to apply the changes (TCSANOW, TCSADRAIN, TCSAFLUSH). |

**Example**  
```ucode
const handle = io.open('/dev/tty', O_RDWR);
const attrs = handle.tcgetattr();
attrs.lflag &= ~0x0000008; // Disable ECHO
handle.tcsetattr(attrs, TCSANOW);
```

#### handle.grantpt() ⇒ `boolean`
Grants access to a pseudo-terminal slave device.

Allows the owner of the pseudo-terminal master device to grant the
appropriate permissions on the corresponding slave device so that it
may be opened.

This function is typically called before opening the slave device.

Returns `true` on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const master = io.open('/dev/ptmx', O_RDWR);
if (master.grantpt()) {
    print("Granted access to slave device\n");
}
```

#### handle.unlockpt() ⇒ `boolean`
Unlocks a pseudo-terminal slave device.

Unlocks the pseudo-terminal slave device associated with the master device
referred to by the file descriptor. This function is typically called after
grantpt() and before opening the slave device.

Returns `true` on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const master = io.open('/dev/ptmx', O_RDWR);
master.grantpt();
if (master.unlockpt()) {
    print("Unlocked slave device\n");
}
```

#### handle.read(length) ⇒ `string`
Reads data from the file descriptor.

Reads up to the specified number of bytes from the file descriptor.

Returns a string containing the read data.

Returns an empty string on EOF.

Returns `null` if a read error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  

| Param | Type | Description |
| --- | --- | --- |
| length | `number` | The maximum number of bytes to read. |

**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDONLY);
const data = handle.read(1024);
```

#### handle.write(data) ⇒ `number`
Writes data to the file descriptor.

Writes the given data to the file descriptor. Non-string values are
converted to strings before being written.

Returns the number of bytes written.

Returns `null` if a write error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  

| Param | Type | Description |
| --- | --- | --- |
| data | `\*` | The data to write. |

**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_WRONLY | O_CREAT);
handle.write('Hello World\n');
```

#### handle.seek([offset], [whence]) ⇒ `boolean`
Sets the file descriptor position.

Sets the file position of the descriptor to the given offset and whence.

Returns `true` if the position was successfully set.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [offset] | `number` | `0` | The offset in bytes. |
| [whence] | `number` | `0` | The position reference. | Whence | Description                                                        | |--------|--------------------------------------------------------------------| | `0`    | The offset is relative to the start of the file (SEEK_SET).       | | `1`    | The offset is relative to the current position (SEEK_CUR).        | | `2`    | The offset is relative to the end of the file (SEEK_END).         | |

**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDONLY);
handle.seek(100, 0);  // Seek to byte 100 from start
```

#### handle.tell() ⇒ `number`
Gets the current file descriptor position.

Returns the current file position as an integer.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDONLY);
const pos = handle.tell();
```

#### handle.dup() ⇒ [`handle`](#module_io.handle)
Duplicates the file descriptor.

Creates a duplicate of the file descriptor using dup(2).

Returns a new io.handle for the duplicated descriptor.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDONLY);
const dup_handle = handle.dup();
```

#### handle.dup2(newfd) ⇒ `boolean`
Duplicates the file descriptor to a specific descriptor number.

Creates a duplicate of the file descriptor to the specified descriptor
number using dup2(2). If newfd was previously open, it is silently closed.

Returns `true` on success.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  

| Param | Type | Description |
| --- | --- | --- |
| newfd | `number` | The target file descriptor number. |

**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_WRONLY);
handle.dup2(2);  // Redirect stderr to the file
```

#### handle.fileno() ⇒ `number`
Gets the file descriptor number.

Returns the underlying file descriptor number.

Returns `null` if the handle is closed.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDONLY);
print(handle.fileno(), "\n");
```

#### handle.fcntl(cmd, [arg]) ⇒ `number` \| [`handle`](#module_io.handle)
Performs fcntl() operations on the file descriptor.

Performs the specified fcntl() command on the file descriptor with an
optional argument.

Returns the result of the fcntl() call. For F_DUPFD and F_DUPFD_CLOEXEC,
returns a new io.handle wrapping the duplicated descriptor. For other
commands, returns a number (interpretation depends on cmd).

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  

| Param | Type | Description |
| --- | --- | --- |
| cmd | `number` | The fcntl command (e.g., F_GETFL, F_SETFL, F_GETFD, F_SETFD, F_DUPFD). |
| [arg] | `number` | Optional argument for the command. |

**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDONLY);
const flags = handle.fcntl(F_GETFL);
handle.fcntl(F_SETFL, flags | O_NONBLOCK);
const dup_handle = handle.fcntl(F_DUPFD, 10);  // Returns io.handle
```

#### handle.ioctl(direction, type, num, [value]) ⇒ `number` \| `string`
Performs an ioctl operation on the file descriptor.

The direction parameter specifies who is reading and writing,
from the user's point of view. It can be one of the following values:

| Direction      | Description                                                                       |
|----------------|-----------------------------------------------------------------------------------|
| IOC_DIR_NONE   | neither userspace nor kernel is writing, ioctl is executed without passing data.  |
| IOC_DIR_WRITE  | userspace is writing and kernel is reading.                                       |
| IOC_DIR_READ   | kernel is writing and userspace is reading.                                       |
| IOC_DIR_RW     | userspace is writing and kernel is writing back into the data structure.          |

Returns the result of the ioctl operation; for `IOC_DIR_READ` and
`IOC_DIR_RW` this is a string containing the data, otherwise a number as
return code.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  

| Param | Type | Description |
| --- | --- | --- |
| direction | `number` | The direction of the ioctl operation. Use constants IOC_DIR_*. |
| type | `number` | The ioctl type (see https://www.kernel.org/doc/html/latest/userspace-api/ioctl/ioctl-number.html) |
| num | `number` | The ioctl sequence number. |
| [value] | `number` \| `string` | The value to pass to the ioctl system call. For `IOC_DIR_NONE`, this argument is ignored. With `IOC_DIR_READ`, the value should be a positive integer specifying the number of bytes to expect from the kernel. For the other directions, `IOC_DIR_WRITE` and `IOC_DIR_RW`, that value parameter must be a string, serving as buffer for the data to send. |

**Example**  
```ucode
const handle = io.open('/dev/tty', O_RDWR);
const size = handle.ioctl(IOC_DIR_READ, 0x54, 0x13, 8);  // TIOCGWINSZ
```

#### handle.isatty() ⇒ `boolean`
Checks if the file descriptor refers to a terminal.

Returns `true` if the descriptor refers to a terminal device.

Returns `false` otherwise.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const handle = io.new(0);  // stdin
if (handle.isatty())
    print("Running in a terminal\n");
```

#### handle.close() ⇒ `boolean`
Closes the file descriptor.

Closes the underlying file descriptor. Further operations on this handle
will fail.

Returns `true` if the descriptor was successfully closed.

Returns `null` if an error occurred.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
const handle = io.open('/tmp/test.txt', O_RDONLY);
handle.close();
```

#### handle.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`handle`](#module_io.handle)  
**Example**  
```ucode
// Trigger an error
io.open('/path/does/not/exist');

// Print error (should yield "No such file or directory")
print(io.error(), "\n");
```

---

# ucode module: log

> **Live docs:** https://ucode.mein.io/module-log.html

---

## System logging functions

The `log` module provides bindings to the POSIX syslog functions `openlog()`,
`syslog()` and `closelog()` as well as - when available - the OpenWrt
specific ulog library functions.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { openlog, syslog, LOG_PID, LOG_USER, LOG_ERR } from 'log';

  openlog("my-log-ident", LOG_PID, LOG_USER);
  syslog(LOG_ERR, "An error occurred!");

  // OpenWrt specific ulog functions
  import { ulog_open, ulog, ULOG_SYSLOG, LOG_DAEMON, LOG_INFO } from 'log';

  ulog_open(ULOG_SYSLOG, LOG_DAEMON, "my-log-ident");
  ulog(LOG_INFO, "The current epoch is %d", time());
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as log from 'log';

  log.openlog("my-log-ident", log.LOG_PID, log.LOG_USER);
  log.syslog(log.LOG_ERR, "An error occurred!");

  // OpenWrt specific ulog functions
  log.ulog_open(log.ULOG_SYSLOG, log.LOG_DAEMON, "my-log-ident");
  log.ulog(log.LOG_INFO, "The current epoch is %d", time());
  ```

Additionally, the log module namespace may also be imported by invoking the
`ucode` interpreter with the `-llog` switch.

## Constants

The `log` module declares a number of numeric constants to specify logging
facility, priority and option values, as well as ulog specific channels.

### Syslog Options

| Constant Name | Description                                             |
|---------------|---------------------------------------------------------|
| `LOG_PID`     | Include PID with each message.                          |
| `LOG_CONS`    | Log to console if error occurs while sending to syslog. |
| `LOG_NDELAY`  | Open the connection to the logger immediately.          |
| `LOG_ODELAY`  | Delay open until the first message is logged.           |
| `LOG_NOWAIT`  | Do not wait for child processes created during logging. |

### Syslog Facilities

| Constant Name  | Description                                      |
|----------------|--------------------------------------------------|
| `LOG_AUTH`     | Authentication/authorization messages.           |
| `LOG_AUTHPRIV` | Private authentication messages.                 |
| `LOG_CRON`     | Clock daemon (cron and at commands).             |
| `LOG_DAEMON`   | System daemons without separate facility values. |
| `LOG_FTP`      | FTP server daemon.                               |
| `LOG_KERN`     | Kernel messages.                                 |
| `LOG_LPR`      | Line printer subsystem.                          |
| `LOG_MAIL`     | Mail system.                                     |
| `LOG_NEWS`     | Network news subsystem.                          |
| `LOG_SYSLOG`   | Messages generated internally by syslogd.        |
| `LOG_USER`     | Generic user-level messages.                     |
| `LOG_UUCP`     | UUCP subsystem.                                  |
| `LOG_LOCAL0`   | Local use 0 (custom facility).                   |
| `LOG_LOCAL1`   | Local use 1 (custom facility).                   |
| `LOG_LOCAL2`   | Local use 2 (custom facility).                   |
| `LOG_LOCAL3`   | Local use 3 (custom facility).                   |
| `LOG_LOCAL4`   | Local use 4 (custom facility).                   |
| `LOG_LOCAL5`   | Local use 5 (custom facility).                   |
| `LOG_LOCAL6`   | Local use 6 (custom facility).                   |
| `LOG_LOCAL7`   | Local use 7 (custom facility).                   |

### Syslog Priorities

| Constant Name | Description                         |
|---------------|-------------------------------------|
| `LOG_EMERG`   | System is unusable.                 |
| `LOG_ALERT`   | Action must be taken immediately.   |
| `LOG_CRIT`    | Critical conditions.                |
| `LOG_ERR`     | Error conditions.                   |
| `LOG_WARNING` | Warning conditions.                 |
| `LOG_NOTICE`  | Normal, but significant, condition. |
| `LOG_INFO`    | Informational message.              |
| `LOG_DEBUG`   | Debug-level message.                |

### Ulog channels

| Constant Name | Description                          |
|---------------|--------------------------------------|
| `ULOG_KMSG`   | Log messages to `/dev/kmsg` (dmesg). |
| `ULOG_STDIO`  | Log messages to stdout.              |
| `ULOG_SYSLOG` | Log messages to syslog.              |

### log.openlog([ident], [options], [facility]) ⇒ `boolean`
Open connection to system logger.

The `openlog()` function instructs the program to establish a connection to
the system log service and configures the default facility and identification
for use in subsequent log operations. It may be omitted, in which case the
first call to `syslog()` will implicitly call `openlog()` with a default
ident value representing the program name and a default `LOG_USER` facility.

The log option argument may be either a single string value containing an
option name, an array of option name strings or a numeric value representing
a bitmask of `LOG_*` option constants.

The facility argument may be either a single string value containing a
facility name or one of the numeric `LOG_*` facility constants in the module
namespace.

Returns `true` if the system `openlog()` function was invoked.

Returns `false` if an invalid argument, such as an unrecognized option or
facility name, was provided.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [ident] | `string` |  | A string identifying the program name. If omitted, the name of the calling process is used by default. |
| [options] | `number` \| [`LogOption`](#module_log.LogOption) \| [`Array.<LogOption>`](#module_log.LogOption) |  | Logging options to use. See [LogOption](#module_log.LogOption) for recognized option names. |
| [facility] | `number` \| [`LogFacility`](#module_log.LogFacility) | `"user"` | The facility to use for log messages generated by subsequent syslog calls. See [LogFacility](#module_log.LogFacility) for recognized facility names. |

**Example**  
```ucode
// Example usage of openlog function
openlog("myapp", LOG_PID | LOG_NDELAY, LOG_LOCAL0);

// Using option names instead of bitmask and LOG_USER facility
openlog("myapp", [ "pid", "ndelay" ], "user");
```

### log.syslog(priority, format, [...args]) ⇒ `boolean`
Log a message to the system logger.

This function logs a message to the system logger. The function behaves in a
sprintf-like manner, allowing the use of format strings and associated
arguments to construct log messages.

If the `openlog` function has not been called explicitly before, `syslog()`
implicitly calls `openlog()`, using a default ident and `LOG_USER` facility
value before logging the message.

If the `format` argument is not a string and not `null`, it will be
implicitly converted to a string and logged as-is, without further format
string processing.

Returns `true` if a message was passed to the system `syslog()` function.

Returns `false` if an invalid priority value or an empty message was given.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| priority | `number` \| [`LogPriority`](#module_log.LogPriority) | Log message priority. May be either a number value (potentially bitwise OR-ed with a log facility constant) which is passed as-is to the system `syslog()` function or a priority name string. See [LogPriority](#module_log.LogPriority) for recognized priority names. |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
// Example usage of syslog function with format string and arguments
const username = "user123";
const errorCode = 404;
syslog(LOG_ERR, "User %s encountered error: %d", username, errorCode);

// If openlog has not been called explicitly, it is implicitly called with defaults:
syslog(LOG_INFO, "This message will be logged with default settings.");

// Selectively override used facility by OR-ing numeric constant
const password =" secret";
syslog(LOG_DEBUG|LOG_AUTHPRIV, "The password %s has been wrong", secret);

// Using priority names for logging
syslog("emerg", "System shutdown imminent!");

// Implicit stringification
syslog("debug", { foo: 1, bar: true, baz: [1, 2, 3] });
```

### log.closelog()
Close connection to system logger.

The usage of this function is optional, and usually an explicit log
connection tear down is not required.

**Kind**: instance method of [`log`](#module_log)  

### log.ulog\_open([channel], [facility], [ident]) ⇒ `boolean`
Configure ulog logger.

This functions configures the ulog mechanism and is analogeous to using the
`openlog()` function in conjuncton with `syslog()`.

The `ulog_open()` function is OpenWrt specific and may not be present on
other systems. Use `openlog()` and `syslog()` instead for portability to
non-OpenWrt environments.

A program may use multiple channels to simultaneously output messages using
different means. The channel argument may either be a single string value
containing a channel name, an array of channel names or a numeric value
representing a bitmask of `ULOG_*` channel constants.

The facility argument may be either a single string value containing a
facility name or one of the numeric `LOG_*` facility constants in the module
namespace.

The default facility value varies, depending on the execution context of the
program. In OpenWrt's preinit boot phase, or when stdout is not connected to
an interactive terminal, the facility defaults to `"daemon"` (`LOG_DAEMON`),
otherwise to `"user"` (`LOG_USER`).

Likewise, the default channel is selected depending on the context. During
OpenWrt's preinit boot phase, the `"kmsg"` channel is used, for interactive
terminals the `"stdio"` one and for all other cases the `"syslog"` channel
is selected.

Returns `true` if ulog was configured.

Returns `false` if an invalid argument, such as an unrecognized channel or
facility name, was provided.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| [channel] | `number` \| [`UlogChannel`](#module_log.UlogChannel) \| [`Array.<UlogChannel>`](#module_log.UlogChannel) | Specifies the log channels to use. See [UlogChannel](#module_log.UlogChannel) for recognized channel names. |
| [facility] | `number` \| [`LogFacility`](#module_log.LogFacility) | The facility to use for log messages generated by subsequent `ulog()` calls. See [LogFacility](#module_log.LogFacility) for recognized facility names. |
| [ident] | `string` | A string identifying the program name. If omitted, the name of the calling process is used by default. |

**Example**  
```ucode
// Log to dmesg and stderr
ulog_open(["stdio", "kmsg"], "daemon", "my-program");

// Use numeric constants and use implicit default ident
ulog_open(ULOG_SYSLOG, LOG_LOCAL0);
```

### log.ulog(priority, format, [...args]) ⇒ `boolean`
Log a message via the ulog mechanism.

The `ulog()` function outputs the given log message to all configured ulog
channels unless the given priority level exceeds the globally configured ulog
priority threshold. See [ulog_threshold()](#module_log+ulog_threshold)
for details.

The `ulog()` function is OpenWrt specific and may not be present on other
systems. Use `syslog()` instead for portability to non-OpenWrt environments.

Like `syslog()`, the function behaves in a sprintf-like manner, allowing the
use of format strings and associated arguments to construct log messages.

If the `ulog_open()` function has not been called explicitly before, `ulog()`
implicitly configures certain defaults, see
[ulog_open()](#module_log+ulog_open) for a detailled description.

If the `format` argument is not a string and not `null`, it will be
implicitly converted to a string and logged as-is, without further format
string processing.

Returns `true` if a message was passed to the underlying `ulog()` function.

Returns `false` if an invalid priority value or an empty message was given.

**Kind**: instance method of [`log`](#module_log)  
**See**

- module:log#ulog_open
- module:log#ulog_threshold
- module:log#syslog

| Param | Type | Description |
| --- | --- | --- |
| priority | `number` \| [`LogPriority`](#module_log.LogPriority) | Log message priority. May be either a number value or a priority name string. See [LogPriority](#module_log.LogPriority) for recognized priority names. |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
// Example usage of ulog function with format string and arguments
const username = "user123";
const errorCode = 404;
ulog(LOG_ERR, "User %s encountered error: %d", username, errorCode);

// Using priority names for logging
ulog("err", "General error encountered");

// Implicit stringification
ulog("debug", { foo: 1, bar: true, baz: [1, 2, 3] });
```

### log.ulog\_close()
Close ulog logger.

Resets the ulog channels, the default facility and the log ident value to
defaults.

In case the `"syslog"` channel has been configured, the underlying
`closelog()` function will be invoked.

The usage of this function is optional, and usually an explicit ulog teardown
is not required.

The `ulog_close()` function is OpenWrt specific and may not be present on
other systems. Use `closelog()` in conjunction with `syslog()` instead for
portability to non-OpenWrt environments.

**Kind**: instance method of [`log`](#module_log)  
**See**: module:log#closelog  

### log.ulog\_threshold([priority]) ⇒ `boolean`
Set ulog priority threshold.

This function configures the application wide log message threshold for log
messages emitted with `ulog()`. Any message with a priority higher (= less
severe) than the threshold priority will be discarded. This is useful to
implement application wide verbosity settings without having to wrap `ulog()`
invocations into a helper function or guarding code.

When no explicit threshold has been set, `LOG_DEBUG` is used by default,
allowing log messages with all known priorities.

The `ulog_threshold()` function is OpenWrt specific and may not be present on
other systems. There is no syslog equivalent to this ulog specific threshold
mechanism.

The priority argument may be either a string value containing a priority name
or one of the numeric `LOG_*` priority constants in the module namespace.

Returns `true` if a threshold was set.

Returns `false` if an invalid priority value was given.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| [priority] | `number` \| [`LogPriority`](#module_log.LogPriority) | The priority threshold to configure. See [LogPriority](#module_log.LogPriority) for recognized priority names. |

**Example**  
```ucode
// Set threshold to "warning" or more severe
ulog_threshold(LOG_WARNING);

// This message will be supressed
ulog(LOG_DEBUG, "Testing thresholds");

// Using priority name
ulog_threshold("debug");
```

### log.INFO(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_INFO.

This function is convenience wrapper for `ulog(LOG_INFO, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
INFO("This is an info log message");
```

### log.NOTE(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_NOTICE.

This function is convenience wrapper for `ulog(LOG_NOTICE, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
NOTE("This is a notification log message");
```

### log.WARN(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_WARNING.

This function is convenience wrapper for `ulog(LOG_WARNING, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
WARN("This is a warning");
```

### log.ERR(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_ERR.

This function is convenience wrapper for `ulog(LOG_ERR, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
ERR("This is an error!");
```

### log.LogOption : `enum`
The following log option strings are recognized:

| Log Option | Description                                                |
|------------|------------------------------------------------------------|
| `"pid"`    | Include PID with each message.                             |
| `"cons"`   | Log to console if an error occurs while sending to syslog. |
| `"ndelay"` | Open the connection to the logger immediately.             |
| `"odelay"` | Delay open until the first message is logged.              |
| `"nowait"` | Do not wait for child processes created during logging.    |

**Kind**: static enum of [`log`](#module_log)  

### log.LogFacility : `enum`
The following log facility strings are recognized:

| Facility     | Description                                      |
|--------------|--------------------------------------------------|
| `"auth"`     | Authentication/authorization messages.           |
| `"authpriv"` | Private authentication messages.                 |
| `"cron"`     | Clock daemon (cron and at commands).             |
| `"daemon"`   | System daemons without separate facility values. |
| `"ftp"`      | FTP server daemon.                               |
| `"kern"`     | Kernel messages.                                 |
| `"lpr"`      | Line printer subsystem.                          |
| `"mail"`     | Mail system.                                     |
| `"news"`     | Network news subsystem.                          |
| `"syslog"`   | Messages generated internally by syslogd.        |
| `"user"`     | Generic user-level messages.                     |
| `"uucp"`     | UUCP subsystem.                                  |
| `"local0"`   | Local use 0 (custom facility).                   |
| `"local1"`   | Local use 1 (custom facility).                   |
| `"local2"`   | Local use 2 (custom facility).                   |
| `"local3"`   | Local use 3 (custom facility).                   |
| `"local4"`   | Local use 4 (custom facility).                   |
| `"local5"`   | Local use 5 (custom facility).                   |
| `"local6"`   | Local use 6 (custom facility).                   |
| `"local7"`   | Local use 7 (custom facility).                   |

**Kind**: static enum of [`log`](#module_log)  

### log.LogPriority : `enum`
The following log priority strings are recognized:

| Priority    | Description                         |
|-------------|-------------------------------------|
| `"emerg"`   | System is unusable.                 |
| `"alert"`   | Action must be taken immediately.   |
| `"crit"`    | Critical conditions.                |
| `"err"`     | Error conditions.                   |
| `"warning"` | Warning conditions.                 |
| `"notice"`  | Normal, but significant, condition. |
| `"info"`    | Informational message.              |
| `"debug"`   | Debug-level message.                |

**Kind**: static enum of [`log`](#module_log)  

### log.UlogChannel : `enum`
The following ulog channel strings are recognized:

| Channel    | Description                                       |
|------------|---------------------------------------------------|
| `"kmsg"`   | Log to `/dev/kmsg`, log messages appear in dmesg. |
| `"syslog"` | Use standard `syslog()` mechanism.                |
| `"stdio"`  | Use stderr for log output.                        |

**Kind**: static enum of [`log`](#module_log)

---

# ucode module: math

> **Live docs:** https://ucode.mein.io/module-math.html

---

## Mathematical Functions

The `math` module bundles various mathematical and trigonometrical functions.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { pow, rand } from 'math';

  let x = pow(2, 5);
  let y = rand();
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as math from 'math';

  let x = math.pow(2, 5);
  let y = math.rand();
  ```

Additionally, the math module namespace may also be imported by invoking the
`ucode` interpreter with the `-lmath` switch.

### math.abs(number) ⇒ `number`
Returns the absolute value of the given numeric value.

**Kind**: instance method of [`math`](#module_math)  
**Returns**: `number` - Returns the absolute value or `NaN` if the given argument could
not be converted to a number.  

| Param | Type | Description |
| --- | --- | --- |
| number | `\*` | The number to return the absolute value for. |

### math.atan2(y, x) ⇒ `number`
Calculates the principal value of the arc tangent of `y`/`x`,
using the signs of the two arguments to determine the quadrant
of the result.

On success, this function returns the principal value of the arc
tangent of `y`/`x` in radians; the return value is in the range [-pi, pi].

 - If `y` is +0 (-0) and `x` is less than 0, +pi (-pi) is returned.
 - If `y` is +0 (-0) and `x` is greater than 0, +0 (-0) is returned.
 - If `y` is less than 0 and `x` is +0 or -0, -pi/2 is returned.
 - If `y` is greater than 0 and `x` is +0 or -0, pi/2 is returned.
 - If either `x` or `y` is NaN, a NaN is returned.
 - If `y` is +0 (-0) and `x` is -0, +pi (-pi) is returned.
 - If `y` is +0 (-0) and `x` is +0, +0 (-0) is returned.
 - If `y` is a finite value greater (less) than 0, and `x` is negative
   infinity, +pi (-pi) is returned.
 - If `y` is a finite value greater (less) than 0, and `x` is positive
   infinity, +0 (-0) is returned.
 - If `y` is positive infinity (negative infinity), and `x` is finite,
   pi/2 (-pi/2) is returned.
 - If `y` is positive infinity (negative infinity) and `x` is negative
   infinity, +3*pi/4 (-3*pi/4) is returned.
 - If `y` is positive infinity (negative infinity) and `x` is positive
   infinity, +pi/4 (-pi/4) is returned.

When either `x` or `y` can't be converted to a numeric value, `NaN` is
returned.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| y | `\*` | The `y` value. |
| x | `\*` | The `x` value. |

### math.cos(x) ⇒ `number`
Calculates the cosine of `x`, where `x` is given in radians.

Returns the resulting consine value.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Radians value to calculate cosine for. |

### math.exp(x) ⇒ `number`
Calculates the value of `e` (the base of natural logarithms)
raised to the power of `x`.

On success, returns the exponential value of `x`.

 - If `x` is positive infinity, positive infinity is returned.
 - If `x` is negative infinity, `+0` is returned.
 - If the result underflows, a range error occurs, and zero is returned.
 - If the result overflows, a range error occurs, and `Infinity` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Power to raise `e` to. |

### math.log(x) ⇒ `number`
Calculates the natural logarithm of `x`.

On success, returns the natural logarithm of `x`.

 - If `x` is `1`, the result is `+0`.
 - If `x` is positive nfinity, positive infinity is returned.
 - If `x` is zero, then a pole error occurs, and the function
   returns negative infinity.
 - If `x` is negative (including negative infinity), then a domain
   error occurs, and `NaN` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Value to calulate natural logarithm of. |

### math.sin(x) ⇒ `number`
Calculates the sine of `x`, where `x` is given in radians.

Returns the resulting sine value.

 - When `x` is positive or negative infinity, a domain error occurs
   and `NaN` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Radians value to calculate sine for. |

### math.sqrt(x) ⇒ `number`
Calculates the nonnegative square root of `x`.

Returns the resulting square root value.

 - If `x` is `+0` (`-0`) then `+0` (`-0`) is returned.
 - If `x` is positive infinity, positive infinity is returned.
 - If `x` is less than `-0`, a domain error occurs, and `NaN` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Value to calculate square root for. |

### math.pow(x, y) ⇒ `number`
Calculates the value of `x` raised to the power of `y`.

On success, returns the value of `x` raised to the power of `y`.

 - If the result overflows, a range error occurs, and the function
   returns `Infinity`.
 - If result underflows, and is not representable, a range error
   occurs, and `0.0` with the appropriate sign is returned.
 - If `x` is `+0` or `-0`, and `y` is an odd integer less than `0`,
   a pole error occurs `Infinity` is returned, with the same sign
   as `x`.
 - If `x` is `+0` or `-0`, and `y` is less than `0` and not an odd
   integer, a pole error occurs and `Infinity` is returned.
 - If `x` is `+0` (`-0`), and `y` is an odd integer greater than `0`,
   the result is `+0` (`-0`).
 - If `x` is `0`, and `y` greater than `0` and not an odd integer,
   the result is `+0`.
 - If `x` is `-1`, and `y` is positive infinity or negative infinity,
   the result is `1.0`.
 - If `x` is `+1`, the result is `1.0` (even if `y` is `NaN`).
 - If `y` is `0`, the result is `1.0` (even if `x` is `NaN`).
 - If `x` is a finite value less than `0`, and `y` is a finite
   noninteger, a domain error occurs, and `NaN` is returned.
 - If the absolute value of `x` is less than `1`, and `y` is negative
   infinity, the result is positive infinity.
 - If the absolute value of `x` is greater than `1`, and `y` is
   negative infinity, the result is `+0`.
 - If the absolute value of `x` is less than `1`, and `y` is positive
   infinity, the result is `+0`.
 - If the absolute value of `x` is greater than `1`, and `y` is positive
   infinity, the result is positive infinity.
 - If `x` is negative infinity, and `y` is an odd integer less than `0`,
   the result is `-0`.
 - If `x` is negative infinity, and `y` less than `0` and not an odd
   integer, the result is `+0`.
 - If `x` is negative infinity, and `y` is an odd integer greater than
   `0`, the result is negative infinity.
 - If `x` is negative infinity, and `y` greater than `0` and not an odd
   integer, the result is positive infinity.
 - If `x` is positive infinity, and `y` less than `0`, the result is `+0`.
 - If `x` is positive infinity, and `y` greater than `0`, the result is
   positive infinity.

Returns `NaN` if either the `x` or `y` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | The base value. |
| y | `number` | The power value. |

### math.rand([a], [b]) ⇒ `number`
Depending on the arguments, it produces a pseudo-random positive integer, 
or a pseudo-random number in a supplied range.

Without arguments it returns the calculated pseuo-random value. The value 
is within the range `0` to `RAND_MAX` inclusive where `RAND_MAX` is a platform 
specific value guaranteed to be at least `32767`.

With 2 arguments `a, b` it returns a number in the range `a` to `b` inclusive.
With a single argument `a` it returns a number in the range `0` to `a` inclusive.

The [`srand()`](module:math~srand) function sets its argument as the
seed for a new sequence of pseudo-random integers to be returned by `rand()`.
These sequences are repeatable by calling [`srand()`](module:math~srand)
with the same seed value.

If no seed value is explicitly set by calling
[`srand()`](module:math~srand) prior to the first call to `rand()`,
the math module will automatically seed the PRNG once, using the current
time of day in milliseconds as seed value.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| [a] | `number` | End of the desired range. |
| [b] | `number` | The other end of the desired range. |

### math.srand(seed)
Seeds the pseudo-random number generator.

This functions seeds the PRNG with the given value and thus affects the
pseudo-random integer sequence produced by subsequent calls to
[`rand()`](module:math~rand).

Setting the same seed value will result in the same pseudo-random numbers
produced by [`rand()`](module:math~rand).

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| seed | `number` | The seed value. |

### math.isnan(x) ⇒ `boolean`
Tests whether `x` is a `NaN` double.

This functions checks whether the given argument is of type `double` with
a `NaN` (not a number) value.

Returns `true` if the value is `NaN`, otherwise false.

Note that a value can also be checked for `NaN` with the expression
`x !== x` which only evaluates to `true` if `x` is `NaN`.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | The value to test. |

---

# ucode module: nl80211

> **Live docs:** https://ucode.mein.io/module-nl80211.html

---

## Wireless Netlink

The `nl80211` module provides functions for interacting with the nl80211 netlink interface
for wireless networking configuration and management.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import * as nl80211 from 'nl80211';

  // Send a nl80211 request
  let response = nl80211.request(nl80211.const.NL80211_CMD_GET_WIPHY, 0, { wiphy: 0 });

  // Create a listener for wireless events
  let wifiListener = nl80211.listener((msg) => {
      print('Received wireless event:', msg, '\n');
  }, [nl80211.const.NL80211_CMD_NEW_INTERFACE, nl80211.const.NL80211_CMD_DEL_INTERFACE]);

  // Wait for a specific nl80211 event
  let event = nl80211.waitfor([nl80211.const.NL80211_CMD_NEW_SCAN_RESULTS], 5000);
  if (event)
      print('Received scan results:', event.msg, '\n');
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as nl80211 from 'nl80211';

  // Send a nl80211 request
  let response = nl80211.request(nl80211.const.NL80211_CMD_GET_WIPHY, 0, { wiphy: 0 });

  // Create a listener for wireless events
  let listener = nl80211.listener((msg) => {
      print('Received wireless event:', msg, '\n');
  }, [nl80211.const.NL80211_CMD_NEW_INTERFACE, nl80211.const.NL80211_CMD_DEL_INTERFACE]);
  ```

Additionally, the nl80211 module namespace may also be imported by invoking
the `ucode` interpreter with the `-lnl80211` switch.

### nl80211.listener
**Kind**: static class of [`nl80211`](#module_nl80211)  
**See**: [listener()](module:nl80211#listener)  

### nl80211~Netlink message flags
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NLM_F_ACK | `number` | Request for acknowledgment |
| NLM_F_ACK_TLVS | `number` | Request for acknowledgment with TLVs |
| NLM_F_APPEND | `number` | Append to existing list |
| NLM_F_ATOMIC | `number` | Atomic operation |
| NLM_F_CAPPED | `number` | Request capped |
| NLM_F_CREATE | `number` | Create if not exists |
| NLM_F_DUMP | `number` | Dump request |
| NLM_F_DUMP_FILTERED | `number` | Dump filtered request |
| NLM_F_DUMP_INTR | `number` | Dump interrupted |
| NLM_F_ECHO | `number` | Echo request |
| NLM_F_EXCL | `number` | Exclusive creation |
| NLM_F_MATCH | `number` | Match request |
| NLM_F_MULTI | `number` | Multi-part message |
| NLM_F_NONREC | `number` | Non-recursive operation |
| NLM_F_REPLACE | `number` | Replace existing |
| NLM_F_REQUEST | `number` | Request message |
| NLM_F_ROOT | `number` | Root operation |

### nl80211~nl80211 commands
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_CMD_GET_WIPHY | `number` | Get wireless PHY attributes |
| NL80211_CMD_SET_WIPHY | `number` | Set wireless PHY attributes |
| NL80211_CMD_NEW_WIPHY | `number` | Create new wireless PHY |
| NL80211_CMD_DEL_WIPHY | `number` | Delete wireless PHY |
| NL80211_CMD_GET_INTERFACE | `number` | Get interface information |
| NL80211_CMD_SET_INTERFACE | `number` | Set interface attributes |
| NL80211_CMD_NEW_INTERFACE | `number` | Create new interface |
| NL80211_CMD_DEL_INTERFACE | `number` | Delete interface |
| NL80211_CMD_GET_KEY | `number` | Get key |
| NL80211_CMD_SET_KEY | `number` | Set key |
| NL80211_CMD_NEW_KEY | `number` | Add new key |
| NL80211_CMD_DEL_KEY | `number` | Delete key |
| NL80211_CMD_GET_BEACON | `number` | Get beacon |
| NL80211_CMD_SET_BEACON | `number` | Set beacon |
| NL80211_CMD_NEW_BEACON | `number` | Set beacon (alias) |
| NL80211_CMD_STOP_AP | `number` | Stop AP operation |
| NL80211_CMD_DEL_BEACON | `number` | Delete beacon |
| NL80211_CMD_GET_STATION | `number` | Get station information |
| NL80211_CMD_SET_STATION | `number` | Set station attributes |
| NL80211_CMD_NEW_STATION | `number` | Add new station |
| NL80211_CMD_DEL_STATION | `number` | Delete station |
| NL80211_CMD_GET_MPATH | `number` | Get mesh path |
| NL80211_CMD_SET_MPATH | `number` | Set mesh path |
| NL80211_CMD_NEW_MPATH | `number` | Add new mesh path |
| NL80211_CMD_DEL_MPATH | `number` | Delete mesh path |
| NL80211_CMD_SET_BSS | `number` | Set BSS attributes |
| NL80211_CMD_SET_REG | `number` | Set regulatory domain |
| NL80211_CMD_REQ_SET_REG | `number` | Request regulatory domain change |
| NL80211_CMD_GET_MESH_CONFIG | `number` | Get mesh configuration |
| NL80211_CMD_SET_MESH_CONFIG | `number` | Set mesh configuration |
| NL80211_CMD_GET_REG | `number` | Get regulatory domain |
| NL80211_CMD_GET_SCAN | `number` | Get scan results |
| NL80211_CMD_TRIGGER_SCAN | `number` | Trigger scan |
| NL80211_CMD_NEW_SCAN_RESULTS | `number` | New scan results available |
| NL80211_CMD_SCAN_ABORTED | `number` | Scan aborted |
| NL80211_CMD_REG_CHANGE | `number` | Regulatory domain change |
| NL80211_CMD_AUTHENTICATE | `number` | Authenticate |
| NL80211_CMD_ASSOCIATE | `number` | Associate |
| NL80211_CMD_DEAUTHENTICATE | `number` | Deauthenticate |
| NL80211_CMD_DISASSOCIATE | `number` | Disassociate |
| NL80211_CMD_MICHAEL_MIC_FAILURE | `number` | Michael MIC failure |
| NL80211_CMD_REG_BEACON_HINT | `number` | Beacon regulatory hint |
| NL80211_CMD_JOIN_IBSS | `number` | Join [IBSS](../L2-semantic/wiki/wiki_page-techref-wireless-modes.md) |
| NL80211_CMD_LEAVE_IBSS | `number` | Leave [IBSS](../L2-semantic/wiki/wiki_page-techref-wireless-modes.md) |
| NL80211_CMD_TESTMODE | `number` | Test mode |
| NL80211_CMD_CONNECT | `number` | Connect |
| NL80211_CMD_ROAM | `number` | Roam |
| NL80211_CMD_DISCONNECT | `number` | Disconnect |
| NL80211_CMD_SET_WIPHY_NETNS | `number` | Set wireless PHY network namespace |
| NL80211_CMD_GET_SURVEY | `number` | Get survey data |
| NL80211_CMD_NEW_SURVEY_RESULTS | `number` | New survey results |
| NL80211_CMD_SET_PMKSA | `number` | Set PMKSA |
| NL80211_CMD_DEL_PMKSA | `number` | Delete PMKSA |
| NL80211_CMD_FLUSH_PMKSA | `number` | Flush PMKSA |
| NL80211_CMD_REMAIN_ON_CHANNEL | `number` | Remain on channel |
| NL80211_CMD_CANCEL_REMAIN_ON_CHANNEL | `number` | Cancel remain on channel |
| NL80211_CMD_SET_TX_BITRATE_MASK | `number` | Set TX bitrate mask |
| NL80211_CMD_REGISTER_FRAME | `number` | Register frame |
| NL80211_CMD_REGISTER_ACTION | `number` | Register action frame |
| NL80211_CMD_FRAME | `number` | Frame |
| NL80211_CMD_ACTION | `number` | Action frame |
| NL80211_CMD_FRAME_TX_STATUS | `number` | Frame TX status |
| NL80211_CMD_ACTION_TX_STATUS | `number` | Action TX status |
| NL80211_CMD_SET_POWER_SAVE | `number` | Set power save |
| NL80211_CMD_GET_POWER_SAVE | `number` | Get power save |
| NL80211_CMD_SET_CQM | `number` | Set CQM |
| NL80211_CMD_NOTIFY_CQM | `number` | Notify CQM |
| NL80211_CMD_SET_CHANNEL | `number` | Set channel |
| NL80211_CMD_SET_WDS_PEER | `number` | Set WDS peer |
| NL80211_CMD_FRAME_WAIT_CANCEL | `number` | Cancel frame wait |
| NL80211_CMD_JOIN_MESH | `number` | Join mesh |
| NL80211_CMD_LEAVE_MESH | `number` | Leave mesh |
| NL80211_CMD_UNPROT_DEAUTHENTICATE | `number` | Unprotected deauthenticate |
| NL80211_CMD_UNPROT_DISASSOCIATE | `number` | Unprotected disassociate |
| NL80211_CMD_NEW_PEER_CANDIDATE | `number` | New peer candidate |
| NL80211_CMD_GET_WOWLAN | `number` | Get WoWLAN |
| NL80211_CMD_SET_WOWLAN | `number` | Set WoWLAN |
| NL80211_CMD_START_SCHED_SCAN | `number` | Start scheduled scan |
| NL80211_CMD_STOP_SCHED_SCAN | `number` | Stop scheduled scan |
| NL80211_CMD_SCHED_SCAN_RESULTS | `number` | Scheduled scan results |
| NL80211_CMD_SCHED_SCAN_STOPPED | `number` | Scheduled scan stopped |
| NL80211_CMD_SET_REKEY_OFFLOAD | `number` | Set rekey offload |
| NL80211_CMD_PMKSA_CANDIDATE | `number` | PMKSA candidate |
| NL80211_CMD_TDLS_OPER | `number` | TDLS operation |
| NL80211_CMD_TDLS_MGMT | `number` | TDLS management |
| NL80211_CMD_UNEXPECTED_FRAME | `number` | Unexpected frame |
| NL80211_CMD_PROBE_CLIENT | `number` | Probe client |
| NL80211_CMD_REGISTER_BEACONS | `number` | Register beacons |
| NL80211_CMD_UNEXPECTED_4ADDR_FRAME | `number` | Unexpected 4-address frame |
| NL80211_CMD_SET_NOACK_MAP | `number` | Set no-ack map |
| NL80211_CMD_CH_SWITCH_NOTIFY | `number` | Channel switch notify |
| NL80211_CMD_START_P2P_DEVICE | `number` | Start P2P device |
| NL80211_CMD_STOP_P2P_DEVICE | `number` | Stop P2P device |
| NL80211_CMD_CONN_FAILED | `number` | Connection failed |
| NL80211_CMD_SET_MCAST_RATE | `number` | Set multicast rate |
| NL80211_CMD_SET_MAC_ACL | `number` | Set MAC ACL |
| NL80211_CMD_RADAR_DETECT | `number` | Radar detect |
| NL80211_CMD_GET_PROTOCOL_FEATURES | `number` | Get protocol features |
| NL80211_CMD_UPDATE_FT_IES | `number` | Update FT IEs |
| NL80211_CMD_FT_EVENT | `number` | FT event |
| NL80211_CMD_CRIT_PROTOCOL_START | `number` | Start critical protocol |
| NL80211_CMD_CRIT_PROTOCOL_STOP | `number` | Stop critical protocol |
| NL80211_CMD_GET_COALESCE | `number` | Get coalesce |
| NL80211_CMD_SET_COALESCE | `number` | Set coalesce |
| NL80211_CMD_CHANNEL_SWITCH | `number` | Channel switch |
| NL80211_CMD_VENDOR | `number` | Vendor command |
| NL80211_CMD_SET_QOS_MAP | `number` | Set QoS map |
| NL80211_CMD_ADD_TX_TS | `number` | Add TX TS |
| NL80211_CMD_DEL_TX_TS | `number` | Delete TX TS |
| NL80211_CMD_GET_MPP | `number` | Get MPP |
| NL80211_CMD_JOIN_OCB | `number` | Join OCB |
| NL80211_CMD_LEAVE_OCB | `number` | Leave OCB |
| NL80211_CMD_CH_SWITCH_STARTED_NOTIFY | `number` | Channel switch started notify |
| NL80211_CMD_TDLS_CHANNEL_SWITCH | `number` | TDLS channel switch |
| NL80211_CMD_TDLS_CANCEL_CHANNEL_SWITCH | `number` | Cancel TDLS channel switch |
| NL80211_CMD_ABORT_SCAN | `number` | Abort scan |

### nl80211~Scan flags
Constants for NL80211_ATTR_SCAN_FLAGS bitmask.

**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_SCAN_FLAG_LOW_PRIORITY | `number` | Low priority scan |
| NL80211_SCAN_FLAG_FLUSH | `number` | Flush scan results before returning |
| NL80211_SCAN_FLAG_AP | `number` | Force AP mode scan |
| NL80211_SCAN_FLAG_RANDOM_ADDR | `number` | Randomize source MAC address |
| NL80211_SCAN_FLAG_FILS_MAX_CHANNEL_TIME | `number` | FILS max channel time |
| NL80211_SCAN_FLAG_ACCEPT_BCAST_PROBE_RESP | `number` | Accept broadcast probe responses |
| NL80211_SCAN_FLAG_OCE_PROBE_REQ_HIGH_TX_RATE | `number` | OCE high TX rate probe requests |
| NL80211_SCAN_FLAG_OCE_PROBE_REQ_DEFERRAL_SUPPRESSION | `number` | OCE probe request deferral suppression |
| NL80211_SCAN_FLAG_LOW_SPAN | `number` | Low span scan |
| NL80211_SCAN_FLAG_LOW_POWER | `number` | Low power scan |
| NL80211_SCAN_FLAG_HIGH_ACCURACY | `number` | High accuracy scan |
| NL80211_SCAN_FLAG_RANDOM_SN | `number` | Randomize sequence number |
| NL80211_SCAN_FLAG_MIN_PREQ_CONTENT | `number` | Minimize probe request content |
| NL80211_SCAN_FLAG_FREQ_KHZ | `number` | Report scan results with frequency in KHz |
| NL80211_SCAN_FLAG_COLOCATED_6GHZ | `number` | Scan colocated 6GHz BSS |

### nl80211~BSS status constants
Constants for BSS status values.

**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_BSS_STATUS_AUTHENTICATED | `number` | Authenticated with BSS |
| NL80211_BSS_STATUS_ASSOCIATED | `number` | Associated with BSS |
| NL80211_BSS_STATUS_IBSS_JOINED | `number` | Joined [IBSS](../L2-semantic/wiki/wiki_page-techref-wireless-modes.md) |

### nl80211~BSS use-for and cannot-use-reasons constants
Constants for BSS use-for and cannot-use-reasons bitmasks.

**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_BSS_USE_FOR_NORMAL | `number` | Use BSS for normal connection |
| NL80211_BSS_USE_FOR_MLD_LINK | `number` | Use BSS as MLD link |
| NL80211_BSS_CANNOT_USE_NSTR_NONPRIMARY | `number` | NSTR nonprimary link not usable |
| NL80211_BSS_CANNOT_USE_6GHZ_PWR_MISMATCH | `number` | 6GHz power mode mismatch |

### nl80211~HWSIM commands
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| HWSIM_CMD_REGISTER | `number` | Register radio |
| HWSIM_CMD_FRAME | `number` | Send frame |
| HWSIM_CMD_TX_INFO_FRAME | `number` | Send TX info frame |
| HWSIM_CMD_NEW_RADIO | `number` | Create new radio |
| HWSIM_CMD_DEL_RADIO | `number` | Delete radio |
| HWSIM_CMD_GET_RADIO | `number` | Get radio information |
| HWSIM_CMD_ADD_MAC_ADDR | `number` | Add MAC address |
| HWSIM_CMD_DEL_MAC_ADDR | `number` | Delete MAC address |
| HWSIM_CMD_START_PMSR | `number` | Start peer measurement |
| HWSIM_CMD_ABORT_PMSR | `number` | Abort peer measurement |
| HWSIM_CMD_REPORT_PMSR | `number` | Report peer measurement |

### nl80211~Interface types
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_IFTYPE_ADHOC | `number` | [IBSS](../L2-semantic/wiki/wiki_page-techref-wireless-modes.md)/ad-hoc interface |
| NL80211_IFTYPE_STATION | `number` | Station interface |
| NL80211_IFTYPE_AP | `number` | Access point interface |
| NL80211_IFTYPE_AP_VLAN | `number` | AP VLAN interface |
| NL80211_IFTYPE_WDS | `number` | WDS interface |
| NL80211_IFTYPE_MONITOR | `number` | Monitor interface |
| NL80211_IFTYPE_MESH_POINT | `number` | Mesh point interface |
| NL80211_IFTYPE_P2P_CLIENT | `number` | P2P client interface |
| NL80211_IFTYPE_P2P_GO | `number` | P2P group owner interface |
| NL80211_IFTYPE_P2P_DEVICE | `number` | P2P device interface |
| NL80211_IFTYPE_OCB | `number` | Outside context of BSS (OCB) interface |

---

# ucode module: resolv

> **Live docs:** https://ucode.mein.io/module-resolv.html

---

## DNS Resolution Module

The `resolv` module provides DNS resolution functionality for ucode, allowing
you to perform DNS queries for various record types and handle responses.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { query } from 'resolv';

  let result = query('example.com', { type: ['A'] });
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as resolv from 'resolv';

  let result = resolv.query('example.com', { type: ['A'] });
  ```

Additionally, the resolv module namespace may also be imported by invoking
the `ucode` interpreter with the `-lresolv` switch.

## Record Types

The module supports the following DNS record types:

| Type    | Description                    |
|---------|--------------------------------|
| `A`     | IPv4 address record            |
| `AAAA`  | IPv6 address record            |
| `CNAME` | Canonical name record          |
| `MX`    | Mail exchange record           |
| `NS`    | Name server record             |
| `PTR`   | Pointer record (reverse DNS)   |
| `SOA`   | Start of authority record      |
| `SRV`   | Service record                 |
| `TXT`   | Text record                    |
| `ANY`   | Any available record type      |

## Response Codes

DNS queries can return the following response codes:

| Code        | Description                               |
|-------------|-------------------------------------------|
| `NOERROR`   | No error, query successful                |
| `FORMERR`   | Format error in query                     |
| `SERVFAIL`  | Server failure                            |
| `NXDOMAIN`  | Non-existent domain                       |
| `NOTIMP`    | Not implemented                           |
| `REFUSED`   | Query refused                             |
| `TIMEOUT`   | Query timed out                           |

## Response Format

DNS query results are returned as objects where:
- Keys are the queried domain names
- Values are objects containing arrays of records grouped by type
- Special `rcode` property indicates query status for failed queries

### Record Format by Type

**A and AAAA records:**
```json
{
  "example.com": {
    "A": ["192.0.2.1", "192.0.2.2"],
    "AAAA": ["2001:db8::1", "2001:db8::2"]
  }
}
```

**MX records:**
```json
{
  "example.com": {
    "MX": [
      [10, "mail1.example.com"],
      [20, "mail2.example.com"]
    ]
  }
}
```

**SRV records:**
```json
{
  "_http._tcp.example.com": {
    "SRV": [
      [10, 5, 80, "web1.example.com"],
      [10, 10, 80, "web2.example.com"]
    ]
  }
}
```

**SOA records:**
```json
{
  "example.com": {
    "SOA": [
      [
        "ns1.example.com",      // primary nameserver
        "admin.example.com",    // responsible mailbox
        2023010101,             // serial number
        3600,                   // refresh interval
        1800,                   // retry interval
        604800,                 // expire time
        86400                   // minimum TTL
      ]
    ]
  }
}
```

**TXT, NS, CNAME, PTR records:**
```json
{
  "example.com": {
    "TXT": ["v=spf1 include:_spf.example.com ~all"],
    "NS": ["ns1.example.com", "ns2.example.com"],
    "CNAME": ["alias.example.com"]
  }
}
```

**Error responses:**
```json
{
  "nonexistent.example.com": {
    "rcode": "NXDOMAIN"
  }
}
```

## Examples

Basic A record lookup:

```ucode
import { query } from 'resolv';

const result = query(['example.com']);
print(result, "\n");
// {
//   "example.com": {
//     "A": ["192.0.2.1"],
//     "AAAA": ["2001:db8::1"]
//   }
// }
```

Specific record type query:

```ucode
const mxRecords = query(['example.com'], { type: ['MX'] });
print(mxRecords, "\n");
// {
//   "example.com": {
//     "MX": [[10, "mail.example.com"]]
//   }
// }
```

Multiple domains and types:

```ucode
const results = query(
  ['example.com', 'google.com'],
  { 
    type: ['A', 'MX'],
    timeout: 10000,
    nameserver: ['8.8.8.8', '1.1.1.1']
  }
);
```

Reverse DNS lookup:

```ucode
const ptrResult = query(['192.0.2.1'], { type: ['PTR'] });
print(ptrResult, "\n");
// {
//   "1.2.0.192.in-addr.arpa": {
//     "PTR": ["example.com"]
//   }
// }
```

### resolv.query(names, [options]) ⇒ `object`
Perform DNS queries for specified domain names.

The `query()` function performs DNS lookups for one or more domain names
according to the specified options. It returns a structured object containing
all resolved DNS records grouped by domain name and record type.

If no record types are specified in the options, the function will perform
both A and AAAA record lookups for regular domain names, or PTR record
lookups for IP addresses (reverse DNS).

Returns an object containing DNS query results organized by domain name.

Raises a runtime exception if invalid arguments are provided or if DNS
resolution encounters critical errors.

**Kind**: instance method of [`resolv`](#module_resolv)  
**Returns**: `object` - Object containing DNS query results. Keys are domain names, values are
objects containing arrays of records grouped by type, or error information
for failed queries.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| names | `string` \| `Array.<string>` |  | Domain name(s) to query. Can be a single domain name string or an array of domain name strings. IP addresses can also be provided for reverse DNS lookups. |
| [options] | `object` |  | Query options object. |
| [options.type] | `Array.<string>` |  | Array of DNS record types to query for. Valid types are: 'A', 'AAAA', 'CNAME', 'MX', 'NS', 'PTR', 'SOA', 'SRV', 'TXT', 'ANY'. If not specified, defaults to 'A' and 'AAAA' for domain names, or 'PTR' for IP addresses. |
| [options.nameserver] | `Array.<string>` |  | Array of DNS nameserver addresses to query. Each address can optionally include a port number using '#' separator (e.g., '8.8.8.8#53'). IPv6 addresses can include interface scope using '%' separator. If not specified, nameservers are read from /etc/resolv.conf, falling back to '127.0.0.1'. |
| [options.timeout] | `number` | `5000` | Total timeout for all queries in milliseconds. |
| [options.retries] | `number` | `2` | Number of retry attempts for failed queries. |
| [options.edns_maxsize] | `number` | `4096` | Maximum UDP packet size for EDNS (Extension Mechanisms for DNS). Set to 0 to disable EDNS. |
| [options.txt_as_array] | `boolean` | `false` | Return TXT record strings as array elements instead of space-joining all record strings into one single string per record. |

**Example**  
```ucode
// Basic A and AAAA record lookup
const result = query('example.com');
print(result, "\n");
// {
//   "example.com": {
//     "A": ["192.0.2.1"],
//     "AAAA": ["2001:db8::1"]
//   }
// }
```
**Example**  
```ucode
// Specific record type queries
const mxResult = query('example.com', { type: ['MX'] });
print(mxResult, "\n");
// {
//   "example.com": {
//     "MX": [[10, "mail.example.com"]]
//   }
// }
```
**Example**  
```ucode
// Multiple domains and types with custom nameserver
const results = query(
  ['example.com', 'google.com'],
  {
    type: ['A', 'MX'],
    nameserver: ['8.8.8.8', '1.1.1.1'],
    timeout: 10000
  }
);
```
**Example**  
```ucode
// Reverse DNS lookup
const ptrResult = query(['192.0.2.1'], { type: ['PTR'] });
print(ptrResult, "\n");
// {
//   "1.2.0.192.in-addr.arpa": {
//     "PTR": ["example.com"]
//   }
// }
```
**Example**  
```ucode
// TXT record with multiple elements
const txtResult = query(['_spf.facebook.com'], { type: ['TXT'], txt_as_array: true });
printf(txtResult, "\n");
// {
//   "_spf.facebook.com": {
//     "TXT": [
//       [
//         "v=spf1 ip4:66.220.144.128/25 ip4:66.220.155.0/24 ip4:66.220.157.0/25 ip4:69.63.178.128/25 ip4:69.63.181.0/24 ip4:69.63.184.0/25",
//         " ip4:69.171.232.0/24 ip4:69.171.244.0/23 -all"
//       ]
//     ]
//   }
// }
```
**Example**  
```ucode
// Handling errors
const errorResult = query(['nonexistent.example.com']);
print(errorResult, "\n");
// {
//   "nonexistent.example.com": {
//     "rcode": "NXDOMAIN"
//   }
// }
```

### resolv.error() ⇒ `string` \| `null`
Get the last error message from DNS operations.

The `error()` function returns a descriptive error message for the last
failed DNS operation, or `null` if no error occurred. This function is
particularly useful for debugging DNS resolution issues.

After calling this function, the stored error state is cleared, so
subsequent calls will return `null` unless a new error occurs.

Returns a string describing the last error, or `null` if no error occurred.

**Kind**: instance method of [`resolv`](#module_resolv)  
**Returns**: `string` \| `null` - A descriptive error message for the last failed operation, or `null` if
no error occurred.  
**Example**  
```ucode
// Check for errors after a failed query
const result = query("example.org", { nameserver: "invalid..domain" });
const err = error();
if (err) {
  print("DNS query failed: ", err, "\n");
}
```

---

# ucode module: rtnl

> **Live docs:** https://ucode.mein.io/module-rtnl.html

---

## Routing Netlink

The `rtnl` module provides functions for interacting with the routing netlink interface.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { error, request, listener, RTM_GETROUTE, RTM_NEWROUTE, RTM_DELROUTE, AF_INET } from 'rtnl';

  // Send a netlink request
  let response = request(RTM_GETROUTE, 0, { family: AF_INET });

  // Create a listener for route changes
  let routeListener = listener((msg) => {
      print('Received route message:', msg, '\n');
  }, [RTM_NEWROUTE, RTM_DELROUTE]);
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as rtnl from 'rtnl';

  // Send a netlink request
  let response = rtnl.request(rtnl.RTM_GETROUTE, 0, { family: rtnl.AF_INET });

  // Create a listener for route changes
  let listener = rtnl.listener((msg) => {
      print('Received route message:', msg, '\n');
  }, [rtnl.RTM_NEWROUTE, rtnl.RTM_DELROUTE]);
  ```

Additionally, the rtnl module namespace may also be imported by invoking
the `ucode` interpreter with the `-lrtnl` switch.

### rtnl.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`rtnl`](#module_rtnl)  
**Example**  
```ucode
// Trigger rtnl error
request('invalid_command', {}, {});

// Print error (should yield error description)
print(error(), "\n");
```

### rtnl.request(cmd, flags, payload) ⇒ `\*`
Send a netlink request.

Sends a netlink request with the specified command, flags, and payload.

**Kind**: instance method of [`rtnl`](#module_rtnl)  
**Returns**: `\*` - - The response data or null on error  

| Param | Type | Description |
| --- | --- | --- |
| cmd | `string` | The netlink command to send |
| flags | `number` | The netlink flags for the request |
| payload | `\*` | The payload data for the request |

**Example**  
```ucode
// Send a route request
let response = request('RTM_GETROUTE', 0, { family: AF_INET });
```

### rtnl.listener(callback, [commands], [groups]) ⇒ [`listener`](#module_rtnl.listener)
Create a netlink listener.

Creates a new netlink listener that will receive messages matching the specified
commands and multicast groups.

**Kind**: instance method of [`rtnl`](#module_rtnl)  
**Returns**: [`listener`](#module_rtnl.listener) - - A listener object with methods to control the listener  

| Param | Type | Description |
| --- | --- | --- |
| callback | `function` | The callback function to invoke when a message is received |
| [commands] | `Array.<string>` | Array of netlink commands to listen for (optional) |
| [groups] | `Array.<number>` | Array of multicast groups to join (optional) |

**Example**  
```ucode
// Create a listener for route changes
let routeListener = listener((msg) => {
    print('Received route message:', msg, '\n');
}, [RTM_NEWROUTE, RTM_DELROUTE]);
```

### rtnl.listener
**Kind**: static class of [`rtnl`](#module_rtnl)  
**See**: [listener()](#module_rtnl+listener)  

* [.listener](#module_rtnl.listener)
    * [.set_commands(commands)](#module_rtnl.listener+set_commands) ⇒ `boolean`
    * [.close()](#module_rtnl.listener+close) ⇒ `boolean`

#### listener.set\_commands(commands) ⇒ `boolean`
Set the commands for a netlink listener.

Updates the set of netlink commands that the listener will receive.

**Kind**: instance method of [`listener`](#module_rtnl.listener)  
**Returns**: `boolean` - - true if successful, false on error  

| Param | Type | Description |
| --- | --- | --- |
| commands | `Array.<string>` | Array of netlink commands to listen for |

**Example**  
```ucode
// Update listener to only receive route messages
listener.set_commands([RTM_NEWROUTE, RTM_DELROUTE]);
```

#### listener.close() ⇒ `boolean`
Close a netlink listener.

Closes the netlink listener and stops receiving messages.

**Kind**: instance method of [`listener`](#module_rtnl.listener)  
**Returns**: `boolean` - - true if successful, false on error  
**Example**  
```ucode
// Close the listener
listener.close();
```

### rtnl~Netlink message flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NLM_F_ACK | `number` | Request for acknowledgment |
| NLM_F_ACK_TLVS | `number` | Request for acknowledgment with TLVs |
| NLM_F_APPEND | `number` | Append to existing list |
| NLM_F_ATOMIC | `number` | Atomic operation |
| NLM_F_CAPPED | `number` | Request capped |
| NLM_F_CREATE | `number` | Create if not exists |
| NLM_F_DUMP | `number` | Dump request |
| NLM_F_DUMP_FILTERED | `number` | Dump filtered request |
| NLM_F_DUMP_INTR | `number` | Dump interrupted |
| NLM_F_ECHO | `number` | Echo request |
| NLM_F_EXCL | `number` | Exclusive creation |
| NLM_F_MATCH | `number` | Match request |
| NLM_F_MULTI | `number` | Multi-part message |
| NLM_F_NONREC | `number` | Non-recursive operation |
| NLM_F_REPLACE | `number` | Replace existing |
| NLM_F_REQUEST | `number` | Request message |
| NLM_F_ROOT | `number` | Root operation |
| NLM_F_STRICT_CHK | `number` | Strict checking |

### rtnl~IPv6 address generation modes
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| IN6_ADDR_GEN_MODE_EUI64 | `number` | EUI-64 mode |
| IN6_ADDR_GEN_MODE_NONE | `number` | No mode |
| IN6_ADDR_GEN_MODE_STABLE_PRIVACY | `number` | Stable privacy mode |
| IN6_ADDR_GEN_MODE_RANDOM | `number` | Random mode |

### rtnl~MACVLAN modes
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| MACVLAN_MODE_PRIVATE | `number` | Private mode |
| MACVLAN_MODE_VEPA | `number` | VEPA mode |
| MACVLAN_MODE_BRIDGE | `number` | Bridge mode |
| MACVLAN_MODE_PASSTHRU | `number` | Pass-through mode |
| MACVLAN_MODE_SOURCE | `number` | Source mode |

### rtnl~MACVLAN MAC address commands
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| MACVLAN_MACADDR_ADD | `number` | Add MAC address |
| MACVLAN_MACADDR_DEL | `number` | Delete MAC address |
| MACVLAN_MACADDR_FLUSH | `number` | Flush MAC addresses |
| MACVLAN_MACADDR_SET | `number` | Set MAC address |

### rtnl~MACsec validation levels
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| MACSEC_VALIDATE_DISABLED | `number` | Disabled validation |
| MACSEC_VALIDATE_CHECK | `number` | Check validation |
| MACSEC_VALIDATE_STRICT | `number` | Strict validation |
| MACSEC_VALIDATE_MAX | `number` | Maximum validation |

### rtnl~MACsec offload modes
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| MACSEC_OFFLOAD_OFF | `number` | Offload off |
| MACSEC_OFFLOAD_PHY | `number` | Physical offload |
| MACSEC_OFFLOAD_MAC | `number` | MAC offload |
| MACSEC_OFFLOAD_MAX | `number` | Maximum offload |

### rtnl~IPVLAN modes
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| IPVLAN_MODE_L2 | `number` | Layer 2 mode |
| IPVLAN_MODE_L3 | `number` | Layer 3 mode |
| IPVLAN_MODE_L3S | `number` | Layer 3 symmetric mode |

### rtnl~VXLAN data frame flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| VXLAN_DF_UNSET | `number` | Data frame unset |
| VXLAN_DF_SET | `number` | Data frame set |
| VXLAN_DF_INHERIT | `number` | Data frame inherit |
| VXLAN_DF_MAX | `number` | Maximum data frame |

### rtnl~Geneve data frame flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| GENEVE_DF_UNSET | `number` | Data frame unset |
| GENEVE_DF_SET | `number` | Data frame set |
| GENEVE_DF_INHERIT | `number` | Data frame inherit |
| GENEVE_DF_MAX | `number` | Maximum data frame |

### rtnl~GTP roles
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| GTP_ROLE_GGSN | `number` | GGSN role |
| GTP_ROLE_SGSN | `number` | SGSN role |

### rtnl~Port request types
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| PORT_REQUEST_PREASSOCIATE | `number` | Pre-associate request |
| PORT_REQUEST_PREASSOCIATE_RR | `number` | Pre-associate round-robin request |
| PORT_REQUEST_ASSOCIATE | `number` | Associate request |
| PORT_REQUEST_DISASSOCIATE | `number` | Disassociate request |

### rtnl~Port VDP responses
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| PORT_VDP_RESPONSE_SUCCESS | `number` | Success response |
| PORT_VDP_RESPONSE_INVALID_FORMAT | `number` | Invalid format response |
| PORT_VDP_RESPONSE_INSUFFICIENT_RESOURCES | `number` | Insufficient resources response |
| PORT_VDP_RESPONSE_UNUSED_VTID | `number` | Unused VTID response |
| PORT_VDP_RESPONSE_VTID_VIOLATION | `number` | VTID violation response |
| PORT_VDP_RESPONSE_VTID_VERSION_VIOALTION | `number` | VTID version violation response |
| PORT_VDP_RESPONSE_OUT_OF_SYNC | `number` | Out of sync response |

### rtnl~Port profile responses
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| PORT_PROFILE_RESPONSE_SUCCESS | `number` | Success response |
| PORT_PROFILE_RESPONSE_INPROGRESS | `number` | In progress response |
| PORT_PROFILE_RESPONSE_INVALID | `number` | Invalid response |
| PORT_PROFILE_RESPONSE_BADSTATE | `number` | Bad state response |
| PORT_PROFILE_RESPONSE_INSUFFICIENT_RESOURCES | `number` | Insufficient resources response |
| PORT_PROFILE_RESPONSE_ERROR | `number` | Error response |

### rtnl~IPoIB modes
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| IPOIB_MODE_DATAGRAM | `number` | Datagram mode |
| IPOIB_MODE_CONNECTED | `number` | Connected mode |

### rtnl~HSR protocols
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| HSR_PROTOCOL_HSR | `number` | HSR protocol |
| HSR_PROTOCOL_PRP | `number` | PRP protocol |

### rtnl~Link extended statistics types
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| LINK_XSTATS_TYPE_UNSPEC | `number` | Unspecified type |
| LINK_XSTATS_TYPE_BRIDGE | `number` | Bridge type |
| LINK_XSTATS_TYPE_BOND | `number` | Bond type |

### rtnl~XDP attach types
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| XDP_ATTACHED_NONE | `number` | Not attached |
| XDP_ATTACHED_DRV | `number` | Driver attached |
| XDP_ATTACHED_SKB | `number` | SKB attached |
| XDP_ATTACHED_HW | `number` | Hardware attached |
| XDP_ATTACHED_MULTI | `number` | Multi attached |

### rtnl~FDB notification bits
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| FDB_NOTIFY_BIT | `number` | Notify bit |
| FDB_NOTIFY_INACTIVE_BIT | `number` | Inactive notify bit |

### rtnl~Route commands
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| RTM_BASE | `number` | Base command |
| RTM_NEWLINK | `number` | New link |
| RTM_DELLINK | `number` | Delete link |
| RTM_GETLINK | `number` | Get link |
| RTM_SETLINK | `number` | Set link |
| RTM_NEWADDR | `number` | New address |
| RTM_DELADDR | `number` | Delete address |
| RTM_GETADDR | `number` | Get address |
| RTM_NEWROUTE | `number` | New route |
| RTM_DELROUTE | `number` | Delete route |
| RTM_GETROUTE | `number` | Get route |
| RTM_NEWRULE | `number` | New rule |
| RTM_DELRULE | `number` | Delete rule |
| RTM_GETRULE | `number` | Get rule |
| RTM_NEWQDISC | `number` | New queue discipline |
| RTM_DELQDISC | `number` | Delete queue discipline |
| RTM_GETQDISC | `number` | Get queue discipline |
| RTM_NEWTCLASS | `number` | New traffic class |
| RTM_DELTCLASS | `number` | Delete traffic class |
| RTM_GETTCLASS | `number` | Get traffic class |
| RTM_NEWTFILTER | `number` | New traffic filter |
| RTM_DELTFILTER | `number` | Delete traffic filter |
| RTM_GETTFILTER | `number` | Get traffic filter |
| RTM_NEWACTION | `number` | New action |
| RTM_DELACTION | `number` | Delete action |
| RTM_GETACTION | `number` | Get action |
| RTM_NEWPREFIX | `number` | New prefix |
| RTM_GETMULTICAST | `number` | Get multicast |
| RTM_GETANYCAST | `number` | Get anycast |
| RTM_NEWNEIGHTBL | `number` | New neighbor table |
| RTM_GETNEIGHTBL | `number` | Get neighbor table |
| RTM_SETNEIGHTBL | `number` | Set neighbor table |
| RTM_NEWNDUSEROPT | `number` | New neighbor user option |
| RTM_NEWADDRLABEL | `number` | New address label |
| RTM_DELADDRLABEL | `number` | Delete address label |
| RTM_GETADDRLABEL | `number` | Get address label |
| RTM_GETDCB | `number` | Get DCB |
| RTM_SETDCB | `number` | Set DCB |
| RTM_NEWNETCONF | `number` | New network configuration |
| RTM_DELNETCONF | `number` | Delete network configuration |
| RTM_GETNETCONF | `number` | Get network configuration |
| RTM_NEWMDB | `number` | New multicast database |
| RTM_DELMDB | `number` | Delete multicast database |
| RTM_GETMDB | `number` | Get multicast database |
| RTM_NEWNSID | `number` | New network namespace ID |
| RTM_DELNSID | `number` | Delete network namespace ID |
| RTM_GETNSID | `number` | Get network namespace ID |
| RTM_NEWSTATS | `number` | New statistics |
| RTM_GETSTATS | `number` | Get statistics |
| RTM_NEWCACHEREPORT | `number` | New cache report |
| RTM_NEWCHAIN | `number` | New chain |
| RTM_DELCHAIN | `number` | Delete chain |
| RTM_GETCHAIN | `number` | Get chain |
| RTM_NEWNEXTHOP | `number` | New next hop |
| RTM_DELNEXTHOP | `number` | Delete next hop |
| RTM_GETNEXTHOP | `number` | Get next hop |
| RTM_NEWLINKPROP | `number` | New link property |
| RTM_DELLINKPROP | `number` | Delete link property |
| RTM_GETLINKPROP | `number` | Get link property |
| RTM_NEWVLAN | `number` | New VLAN |
| RTM_DELVLAN | `number` | Delete VLAN |
| RTM_GETVLAN | `number` | Get VLAN |

### rtnl~Route types
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| RTN_UNSPEC | `number` | Unspecified route |
| RTN_UNICAST | `number` | Unicast route |
| RTN_LOCAL | `number` | Local route |
| RTN_BROADCAST | `number` | Broadcast route |
| RTN_ANYCAST | `number` | Anycast route |
| RTN_MULTICAST | `number` | Multicast route |
| RTN_BLACKHOLE | `number` | Blackhole route |
| RTN_UNREACHABLE | `number` | Unreachable route |
| RTN_PROHIBIT | `number` | Prohibited route |
| RTN_THROW | `number` | Throw route |
| RTN_NAT | `number` | NAT route |
| RTN_XRESOLVE | `number` | External resolve route |

### rtnl~Route scopes
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| RT_SCOPE_UNIVERSE | `number` | Universe scope |
| RT_SCOPE_SITE | `number` | Site scope |
| RT_SCOPE_LINK | `number` | Link scope |
| RT_SCOPE_HOST | `number` | Host scope |
| RT_SCOPE_NOWHERE | `number` | Nowhere scope |

### rtnl~Route tables
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| RT_TABLE_UNSPEC | `number` | Unspecified table |
| RT_TABLE_COMPAT | `number` | Compatibility table |
| RT_TABLE_DEFAULT | `number` | Default table |
| RT_TABLE_MAIN | `number` | Main table |
| RT_TABLE_LOCAL | `number` | Local table |
| RT_TABLE_MAX | `number` | Maximum table |

### rtnl~Route metrics
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| RTAX_MTU | `number` | Maximum transmission unit |
| RTAX_HOPLIMIT | `number` | Hop limit |
| RTAX_ADVMSS | `number` | Advertised MSS |
| RTAX_REORDERING | `number` | Reordering |
| RTAX_RTT | `number` | Round trip time |
| RTAX_WINDOW | `number` | Window size |
| RTAX_CWND | `number` | Congestion window |
| RTAX_INITCWND | `number` | Initial congestion window |
| RTAX_INITRWND | `number` | Initial receive window |
| RTAX_FEATURES | `number` | Features |
| RTAX_QUICKACK | `number` | Quick acknowledgment |
| RTAX_CC_ALGO | `number` | Congestion control algorithm |
| RTAX_RTTVAR | `number` | RTT variance |
| RTAX_SSTHRESH | `number` | Slow start threshold |
| RTAX_FASTOPEN_NO_COOKIE | `number` | Fast open no cookie |

### rtnl~Prefix types
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| PREFIX_UNSPEC | `number` | Unspecified prefix |
| PREFIX_ADDRESS | `number` | Address prefix |
| PREFIX_CACHEINFO | `number` | Cache info prefix |

### rtnl~Neighbor discovery user option types
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NDUSEROPT_UNSPEC | `number` | Unspecified option |
| NDUSEROPT_SRCADDR | `number` | Source address option |

### rtnl~Multicast groups
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| RTNLGRP_NONE | `number` | No group |
| RTNLGRP_LINK | `number` | Link group |
| RTNLGRP_NOTIFY | `number` | Notify group |
| RTNLGRP_NEIGH | `number` | Neighbor group |
| RTNLGRP_TC | `number` | Traffic control group |
| RTNLGRP_IPV4_IFADDR | `number` | IPv4 interface address group |
| RTNLGRP_IPV4_MROUTE | `number` | IPv4 multicast route group |
| RTNLGRP_IPV4_ROUTE | `number` | IPv4 route group |
| RTNLGRP_IPV4_RULE | `number` | IPv4 rule group |
| RTNLGRP_IPV6_IFADDR | `number` | IPv6 interface address group |
| RTNLGRP_IPV6_MROUTE | `number` | IPv6 multicast route group |
| RTNLGRP_IPV6_ROUTE | `number` | IPv6 route group |
| RTNLGRP_IPV6_IFINFO | `number` | IPv6 interface info group |
| RTNLGRP_DECnet_IFADDR | `number` | DECnet interface address group |
| RTNLGRP_NOP2 | `number` | No operation 2 |
| RTNLGRP_DECnet_ROUTE | `number` | DECnet route group |
| RTNLGRP_DECnet_RULE | `number` | DECnet rule group |
| RTNLGRP_NOP4 | `number` | No operation 4 |
| RTNLGRP_IPV6_PREFIX | `number` | IPv6 prefix group |
| RTNLGRP_IPV6_RULE | `number` | IPv6 rule group |
| RTNLGRP_ND_USEROPT | `number` | Neighbor discovery user option group |
| RTNLGRP_PHONET_IFADDR | `number` | Phonet interface address group |
| RTNLGRP_PHONET_ROUTE | `number` | Phonet route group |
| RTNLGRP_DCB | `number` | Data Center Bridging group |
| RTNLGRP_IPV4_NETCONF | `number` | IPv4 network configuration group |
| RTNLGRP_IPV6_NETCONF | `number` | IPv6 network configuration group |
| RTNLGRP_MDB | `number` | Multicast database group |
| RTNLGRP_MPLS_ROUTE | `number` | MPLS route group |
| RTNLGRP_NSID | `number` | Network namespace ID group |
| RTNLGRP_MPLS_NETCONF | `number` | MPLS network configuration group |
| RTNLGRP_IPV4_MROUTE_R | `number` | IPv4 multicast route reverse group |
| RTNLGRP_IPV6_MROUTE_R | `number` | IPv6 multicast route reverse group |
| RTNLGRP_NEXTHOP | `number` | Next hop group |
| RTNLGRP_BRVLAN | `number` | Bridge VLAN group |

### rtnl~Route flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| RTM_F_CLONED | `number` | Cloned route |
| RTM_F_EQUALIZE | `number` | Equalize route |
| RTM_F_FIB_MATCH | `number` | FIB match |
| RTM_F_LOOKUP_TABLE | `number` | Lookup table |
| RTM_F_NOTIFY | `number` | Notify |
| RTM_F_PREFIX | `number` | Prefix |

### rtnl~Address families
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| AF_UNSPEC | `number` | Unspecified address family |
| AF_INET | `number` | IPv4 address family |
| AF_INET6 | `number` | IPv6 address family |
| AF_MPLS | `number` | MPLS address family |
| AF_BRIDGE | `number` | Bridge address family |

### rtnl~Generic Routing Encapsulation flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| GRE_CSUM | `number` | Checksum flag |
| GRE_ROUTING | `number` | Routing flag |
| GRE_KEY | `number` | Key flag |
| GRE_SEQ | `number` | Sequence flag |
| GRE_STRICT | `number` | Strict flag |
| GRE_REC | `number` | Record flag |
| GRE_ACK | `number` | Acknowledgment flag |

### rtnl~Tunnel encapsulation types
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| TUNNEL_ENCAP_NONE | `number` | No encapsulation |
| TUNNEL_ENCAP_FOU | `number` | Foo over UDP |
| TUNNEL_ENCAP_GUE | `number` | Generic UDP Encapsulation |
| TUNNEL_ENCAP_MPLS | `number` | MPLS encapsulation |

### rtnl~Tunnel encapsulation flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| TUNNEL_ENCAP_FLAG_CSUM | `number` | Checksum flag |
| TUNNEL_ENCAP_FLAG_CSUM6 | `number` | IPv6 checksum flag |
| TUNNEL_ENCAP_FLAG_REMCSUM | `number` | Remote checksum flag |

### rtnl~IPv6 tunnel flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| IP6_TNL_F_ALLOW_LOCAL_REMOTE | `number` | Allow local remote |
| IP6_TNL_F_IGN_ENCAP_LIMIT | `number` | Ignore encapsulation limit |
| IP6_TNL_F_MIP6_DEV | `number` | Mobile IPv6 device |
| IP6_TNL_F_RCV_DSCP_COPY | `number` | Receive DSCP copy |
| IP6_TNL_F_USE_ORIG_FLOWLABEL | `number` | Use original flow label |
| IP6_TNL_F_USE_ORIG_FWMARK | `number` | Use original firewall mark |
| IP6_TNL_F_USE_ORIG_TCLASS | `number` | Use original traffic class |

### rtnl~Interface flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NTF_EXT_LEARNED | `number` | Externally learned |
| NTF_MASTER | `number` | Master interface |
| NTF_OFFLOADED | `number` | Offloaded |
| NTF_PROXY | `number` | Proxy |
| NTF_ROUTER | `number` | Router |
| NTF_SELF | `number` | Self |
| NTF_STICKY | `number` | Sticky |
| NTF_USE | `number` | Use |

### rtnl~Neighbor states
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NUD_DELAY | `number` | Delay state |
| NUD_FAILED | `number` | Failed state |
| NUD_INCOMPLETE | `number` | Incomplete state |
| NUD_NOARP | `number` | No ARP |
| NUD_NONE | `number` | No state |
| NUD_PERMANENT | `number` | Permanent state |
| NUD_PROBE | `number` | Probe state |
| NUD_REACHABLE | `number` | Reachable state |
| NUD_STALE | `number` | Stale state |

### rtnl~Address flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| IFA_F_DADFAILED | `number` | DAD failed |
| IFA_F_DEPRECATED | `number` | Deprecated |
| IFA_F_HOMEADDRESS | `number` | Home address |
| IFA_F_MANAGETEMPADDR | `number` | Manage temporary address |
| IFA_F_MCAUTOJOIN | `number` | Multicast auto join |
| IFA_F_NODAD | `number` | No DAD |
| IFA_F_NOPREFIXROUTE | `number` | No prefix route |
| IFA_F_OPTIMISTIC | `number` | Optimistic |
| IFA_F_PERMANENT | `number` | Permanent |
| IFA_F_SECONDARY | `number` | Secondary |
| IFA_F_STABLE_PRIVACY | `number` | Stable privacy |
| IFA_F_TEMPORARY | `number` | Temporary |
| IFA_F_TENTATIVE | `number` | Tentative |

### rtnl~FIB rule flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| FIB_RULE_PERMANENT | `number` | Permanent rule |
| FIB_RULE_INVERT | `number` | Invert rule |
| FIB_RULE_UNRESOLVED | `number` | Unresolved rule |
| FIB_RULE_IIF_DETACHED | `number` | Interface detached |
| FIB_RULE_DEV_DETACHED | `number` | Device detached |
| FIB_RULE_OIF_DETACHED | `number` | Output interface detached |

### rtnl~FIB rule actions
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| FR_ACT_TO_TBL | `number` | To table action |
| FR_ACT_GOTO | `number` | Goto action |
| FR_ACT_NOP | `number` | No operation action |
| FR_ACT_BLACKHOLE | `number` | Blackhole action |
| FR_ACT_UNREACHABLE | `number` | Unreachable action |
| FR_ACT_PROHIBIT | `number` | Prohibit action |

### rtnl~Network configuration indices
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NETCONFA_IFINDEX_ALL | `number` | All interfaces |
| NETCONFA_IFINDEX_DEFAULT | `number` | Default interface |

### rtnl~Bridge flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| BRIDGE_FLAGS_MASTER | `number` | Master flag |
| BRIDGE_FLAGS_SELF | `number` | Self flag |

### rtnl~Bridge modes
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| BRIDGE_MODE_VEB | `number` | Virtual Ethernet Bridge mode |
| BRIDGE_MODE_VEPA | `number` | Virtual Ethernet Port Aggregator mode |
| BRIDGE_MODE_UNDEF | `number` | Undefined mode |
| BRIDGE_MODE_UNSPEC | `number` | Unspecified mode |
| BRIDGE_MODE_HAIRPIN | `number` | Hairpin mode |

### rtnl~Bridge VLAN information flags
**Kind**: inner typedef of [`rtnl`](#module_rtnl)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| BRIDGE_VLAN_INFO_MASTER | `number` | Master VLAN info |
| BRIDGE_VLAN_INFO_PVID | `number` | Primary VLAN ID |
| BRIDGE_VLAN_INFO_UNTAGGED | `number` | Untagged VLAN |
| BRIDGE_VLAN_INFO_RANGE_BEGIN | `number` | Range begin |
| BRIDGE_VLAN_INFO_RANGE_END | `number` | Range end |
| BRIDGE_VLAN_INFO_BRENTRY | `number` | Bridge entry |

---

# ucode module: socket

> **Live docs:** https://ucode.mein.io/module-socket.html

---

## Socket Module

The `socket` module provides functions for interacting with sockets.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```text
  import { AF_INET, SOCK_STREAM, create as socket } from 'socket';

  let sock = socket(AF_INET, SOCK_STREAM, 0);
  sock.connect('192.168.1.1', 80);
  sock.send(…);
  sock.recv(…);
  sock.close();
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```text
  import * as socket from 'socket';

  let sock = socket.create(socket.AF_INET, socket.SOCK_STREAM, 0);
  sock.connect('192.168.1.1', 80);
  sock.send(…);
  sock.recv(…);
  sock.close();
  ```

Additionally, the socket module namespace may also be imported by invoking
the `ucode` interpreter with the `-lsocket` switch.

### socket.error([numeric]) ⇒ `string` \| `number`
Query error information.

Returns a string containing a description of the last occurred error when
the *numeric* argument is absent or false.

Returns a positive (`errno`) or negative (`EAI_*` constant) error code number
when the *numeric* argument is `true`.

Returns `null` if there is no error information.

**Kind**: instance method of [`socket`](#module_socket)  

| Param | Type | Description |
| --- | --- | --- |
| [numeric] | `boolean` | Whether to return a numeric error code (`true`) or a human readable error message (false). |

**Example**  
```ucode
// Trigger socket error by attempting to bind IPv6 address with IPv4 socket
socket.create(socket.AF_INET, socket.SOCK_STREAM, 0).bind("::", 8080);

// Print error (should yield "Address family not supported by protocol")
print(socket.error(), "\n");

// Trigger resolve error
socket.addrinfo("doesnotexist.org");

// Query error code (should yield -2 for EAI_NONAME)
print(socket.error(true), "\n");  //
```

### socket.strerror(code) ⇒ `string`
Returns a string containing a description of the positive (`errno`) or
negative (`EAI_*` constant) error code number given by the *code* argument.

Returns `null` if the error code number is unknown.

**Kind**: instance method of [`socket`](#module_socket)  

| Param | Type | Description |
| --- | --- | --- |
| code | `number` | The error code. |

**Example**  
```ucode
// Should output 'Name or service not known'.
print(socket.strerror(-2), '\n');

// Should output 'No route to host'.
print(socket.strerror(113), '\n');
```

### socket.sockaddr(address) ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
Parses the provided address value into a socket address representation.

This function parses the given address value into a socket address
representation required for a number of socket operations. The address value
can be provided in various formats:
- For IPv4 addresses, it can be a string representing the IP address,
  optionally followed by a port number separated by colon, e.g.
  `192.168.0.1:8080`.
- For IPv6 addresses, it must be an address string enclosed in square
  brackets if a port number is specified, otherwise the brackets are
  optional. The address string may also include a scope ID in the form
  `%ifname` or `%number`, e.g. `[fe80::1%eth0]:8080` or `fe80::1%15`.
- Any string value containing a slash is treated as UNIX domain socket path.
- Alternatively, it can be provided as an array returned by
  [iptoarr()](module:core#iptoarr), representing the address octets.
- It can also be an object representing a network address, with properties
  for `address` (the IP address) and `port` or a single property `path` to
  denote a UNIX domain socket address.

**Kind**: instance method of [`socket`](#module_socket)  
**Returns**: [`SocketAddress`](#module_socket.socket.SocketAddress) - A socket address representation of the provided address value, or `null` if
the address could not be parsed.  

| Param | Type | Description |
| --- | --- | --- |
| address | `string` \| `Array.<number>` \| [`SocketAddress`](#module_socket.socket.SocketAddress) | The address value to parse. |

**Example**  
```ucode
// Parse an IP address string with port
const address1 = sockaddr('192.168.0.1:8080');

// Parse an IPv6 address string with port and scope identifier
const address2 = sockaddr('[fe80::1%eth0]:8080');

// Parse an array representing an IP address
const address3 = sockaddr([192, 168, 0, 1]);

// Parse a network address object
const address4 = sockaddr({ address: '192.168.0.1', port: 8080 });

// Convert a path value to a UNIX domain socket address
const address5 = sockaddr('/var/run/daemon.sock');
```

### socket.nameinfo(address, [flags]) ⇒ `Object`
Resolves the given network address into hostname and service name.

The `nameinfo()` function provides an API for reverse DNS lookup and service
name resolution. It returns an object containing the following properties:
- `hostname`: The resolved hostname.
- `service`: The resolved service name.

Returns an object representing the resolved hostname and service name.
Return `null` if an error occurred during resolution.

**Kind**: instance method of [`socket`](#module_socket)  
**See**

- {@link module:socket~"Socket Types"|Socket Types}
- {@link module:socket~"Name Info Constants"|AName Info Constants}

| Param | Type | Description |
| --- | --- | --- |
| address | `string` \| [`SocketAddress`](#module_socket.socket.SocketAddress) | The network address to resolve. It can be specified as: - A string representing the IP address. - An object representing the address with properties `address` and `port`. |
| [flags] | `number` | Optional flags that provide additional control over the resolution process, specified as bitwise OR-ed number of `NI_*` constants. |

**Example**  
```ucode
// Resolve a network address into hostname and service name
const result = network.getnameinfo('192.168.1.1:80');
print(result); // { "hostname": "example.com", "service": "http" }
```

### socket.addrinfo(hostname, [service], [hints]) ⇒ [`Array.<AddressInfo>`](#module_socket.AddressInfo)
Resolves the given hostname and optional service name into a list of network
addresses, according to the provided hints.

The `addrinfo()` function provides an API for performing DNS and service name
resolution. It returns an array of objects, each representing a resolved
address.

Returns an array of resolved addresses.
Returns `null` if an error occurred during resolution.

**Kind**: instance method of [`socket`](#module_socket)  
**See**

- {@link module:socket~"Socket Types"|Socket Types}
- {@link module:socket~"Address Info Flags"|Address Info Flags}

| Param | Type | Description |
| --- | --- | --- |
| hostname | `string` | The hostname to resolve. |
| [service] | `string` | Optional service name to resolve. If not provided, the service field of the resulting address information structures is left uninitialized. |
| [hints] | `Object` | Optional hints object that provides additional control over the resolution process. It can contain the following properties: - `family`: The preferred address family (`AF_INET` or `AF_INET6`). - `socktype`: The socket type (`SOCK_STREAM`, `SOCK_DGRAM`, etc.). - `protocol`: The protocol of returned addresses. - `flags`: Bitwise OR-ed `AI_*` flags to control the resolution behavior. |

**Example**  
```ucode
// Resolve all addresses
const addresses = socket.addrinfo('example.org');

// Resolve IPv4 addresses for a given hostname and service
const ipv4addresses = socket.addrinfo('example.com', 'http', { family: socket.AF_INET });

// Resolve IPv6 addresses without specifying a service
const ipv6Addresses = socket.addrinfo('example.com', null, { family: socket.AF_INET6 });
```

### socket.poll(timeout, ...sockets) ⇒ [`Array.<PollSpec>`](#module_socket.PollSpec)
Polls a number of sockets for state changes.

Returns an array of `[socket, flags]` tuples for each socket with pending
events. When a tuple is passed as socket argument, it is included as-is into
the result tuple array, with the flags entry changed to a bitwise OR-ed value
describing the pending events for this socket. When a plain socket instance
(or another kind of handle) is passed, a new tuple array is created for this
socket within the result tuple array, containing this socket as first and the
bitwise OR-ed pending events as second element.

Returns `null` if an error occurred.

**Kind**: instance method of [`socket`](#module_socket)  

| Param | Type | Description |
| --- | --- | --- |
| timeout | `number` | Amount of milliseconds to wait for socket activity before aborting the poll call. If set to `0`, the poll call will return immediately if none of the provided sockets has pending events, if set to a negative value, the poll call will wait indefinitely, in all other cases the poll call will wait at most for the given amount of milliseconds before returning. |
| ...sockets | [`socket`](#module_socket.socket) \| [`PollSpec`](#module_socket.PollSpec) | An arbitrary amount of socket arguments. Each argument may be either a plain [socket instance](#module_socket.socket) (or any other kind of handle implementing a `fileno()` method) or a `[socket, flags]` tuple specifying the socket and requested poll flags. If a plain socket (or other kind of handle) instead of a tuple is provided, the requested poll flags default to `POLLIN|POLLERR|POLLHUP` for this socket. |

**Example**  
```ucode
let x = socket.connect("example.org", 80);
let y = socket.connect("example.com", 80);

// Pass plain socket arguments
let events = socket.poll(10, x, y);
print(events); // [ [ "<socket 0x7>", 0 ], [ "<socket 0x8>", 0 ] ]

// Passing tuples allows attaching state information and requesting
// different I/O events
let events = socket.poll(10,
	[ x, socket.POLLOUT | socket.POLLHUP, "This is example.org" ],
	[ y, socket.POLLOUT | socket.POLLHUP, "This is example.com" ]
);
print(events); // [ [ "<socket 0x7>", 4, "This is example.org" ],
               //   [ "<socket 0x8>", 4, "This is example.com" ] ]
```

### socket.connect(host, [service], [hints], [timeout]) ⇒ [`socket`](#module_socket.socket)
Creates a network socket and connects it to the specified host and service.

This high level function combines the functionality of
[create()](#module_socket+create),
[addrinfo()](#module_socket+addrinfo) and
[connect()](#module_socket.socket+connect) to simplify connection
establishment with the socket module.

**Kind**: instance method of [`socket`](#module_socket)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| host | `string` \| `Array.<number>` \| [`SocketAddress`](#module_socket.socket.SocketAddress) |  | The host to connect to, can be an IP address, hostname, [SocketAddress](#module_socket.socket.SocketAddress), or an array value returned by [iptoarr()](module:core#iptoarr). |
| [service] | `string` \| `number` |  | The service to connect to, can be a symbolic service name (such as "http") or a port number. Optional if host is specified as [SocketAddress](#module_socket.socket.SocketAddress). |
| [hints] | `Object` |  | Optional preferences for the socket. It can contain the following properties: - `family`: The preferred address family (`AF_INET` or `AF_INET6`). - `socktype`: The socket type (`SOCK_STREAM`, `SOCK_DGRAM`, etc.). - `protocol`: The protocol of the created socket. - `flags`: Bitwise OR-ed `AI_*` flags to control the resolution behavior. If no hints are not provided, the default socket type preference is set to `SOCK_STREAM`. |
| [timeout] | `number` | `-1` | The timeout in milliseconds for socket connect operations. If set to a negative value, no specifc time limit is imposed and the function will block until either a connection was successfull or the underlying operating system timeout is reached. |

**Example**  
```ucode
// Resolve host, try to connect to both resulting IPv4 and IPv6 addresses
let conn = socket.connect("example.org", 80);

// Enforce usage of IPv6
let conn = socket.connect("example.com", 80, { family: socket.AF_INET6 });

// Connect a UDP socket
let conn = socket.connect("192.168.1.1", 53, { socktype: socket.SOCK_DGRAM });

// Bypass name resolution by specifying a SocketAddress structure
let conn = socket.connect({ address: "127.0.0.1", port: 9000 });

// Use SocketAddress structure to connect a UNIX domain socket
let conn = socket.connect({ path: "/var/run/daemon.sock" });
```

### socket.listen(host, [service], [hints], [backlog], [reuseaddr]) ⇒ [`socket`](#module_socket.socket)
Binds a listening network socket to the specified host and service.

This high-level function combines the functionality of
[create()](#module_socket+create),
[addrinfo()](#module_socket+addrinfo),
[bind()](#module_socket.socket+bind), and
[listen()](#module_socket.socket+listen) to simplify setting up a
listening socket with the socket module.

**Kind**: instance method of [`socket`](#module_socket)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| host | `string` \| `Array.<number>` \| [`SocketAddress`](#module_socket.socket.SocketAddress) |  | The host to bind to, can be an IP address, hostname, [SocketAddress](#module_socket.socket.SocketAddress), or an array value returned by [iptoarr()](module:core#iptoarr). |
| [service] | `string` \| `number` |  | The service to listen on, can be a symbolic service name (such as "http") or a port number. Optional if host is specified as [SocketAddress](#module_socket.socket.SocketAddress). |
| [hints] | `Object` |  | Optional preferences for the socket. It can contain the following properties: - `family`: The preferred address family (`AF_INET` or `AF_INET6`). - `socktype`: The socket type (`SOCK_STREAM`, `SOCK_DGRAM`, etc.). - `protocol`: The protocol of the created socket. - `flags`: Bitwise OR-ed `AI_*` flags to control the resolution behavior. If no hints are provided, the default socket type preference is set to `SOCK_STREAM`. |
| [backlog] | `number` | `128` | The maximum length of the queue of pending connections. |
| [reuseaddr] | `boolean` |  | Whether to set the SO_REUSEADDR option before calling bind(). |

**Example**  
```ucode
// Listen for incoming TCP connections on port 80
let server = socket.listen("localhost", 80);

// Listen on IPv6 address only
let server = socket.listen("machine.local", 8080, { family: socket.AF_INET6 });

// Listen on a UNIX domain socket
let server = socket.listen({ path: "/var/run/server.sock" });
```

### socket.create([domain], [type], [protocol]) ⇒ [`socket`](#module_socket.socket)
Creates a network socket instance.

This function creates a new network socket with the specified domain and
type, determined by one of the modules `AF_*` and `SOCK_*` constants
respectively, and returns the resulting socket instance for use in subsequent
socket operations.

The domain argument specifies the protocol family, such as AF_INET or
AF_INET6, and defaults to AF_INET if not provided.

The type argument specifies the socket type, such as SOCK_STREAM or
SOCK_DGRAM, and defaults to SOCK_STREAM if not provided. It may also
be bitwise OR-ed with SOCK_NONBLOCK to enable non-blocking mode or
SOCK_CLOEXEC to enable close-on-exec semantics.

The protocol argument may be used to indicate a particular protocol
to be used with the socket, and it defaults to 0 (automatically
determined protocol) if not provided.

Returns a socket descriptor representing the newly created socket.

Returns `null` if an error occurred during socket creation.

**Kind**: instance method of [`socket`](#module_socket)  
**Returns**: [`socket`](#module_socket.socket) - A socket instance representing the newly created socket.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [domain] | `number` | `AF_INET` | The communication domain for the socket, e.g., AF_INET or AF_INET6. |
| [type] | `number` | `SOCK_STREAM` | The socket type, e.g., SOCK_STREAM or SOCK_DGRAM. It may also be bitwise OR-ed with SOCK_NONBLOCK or SOCK_CLOEXEC. |
| [protocol] | `number` | `0` | The protocol to be used with the socket. |

**Example**  
```ucode
// Create a TCP socket
const tcp_socket = create(AF_INET, SOCK_STREAM);

// Create a nonblocking IPv6 UDP socket
const udp_socket = create(AF_INET6, SOCK_DGRAM | SOCK_NONBLOCK);
```

### socket.open([fd]) ⇒ [`socket`](#module_socket.socket)
Creates a network socket instance from an existing file descriptor.

Returns a socket descriptor representing the newly created socket.

Returns `null` if an error occurred during socket creation.

**Kind**: instance method of [`socket`](#module_socket)  
**Returns**: [`socket`](#module_socket.socket) - A socket instance representing the socket.  

| Param | Type | Description |
| --- | --- | --- |
| [fd] | `number` | The file descriptor number |

### socket.pair([type]) ⇒ `Array.<?module:socket.socket>`
Creates a connected socket instance with a pair file descriptor.

This function creates new network sockets with the specified type,
determined by one of the `SOCK_*` constants, and returns resulting socket
instances for use in subsequent socket operations.

The type argument specifies the socket type, such as SOCK_STREAM or
SOCK_DGRAM, and defaults to SOCK_STREAM if not provided. It may also
be bitwise OR-ed with SOCK_NONBLOCK to enable non-blocking mode or
SOCK_CLOEXEC to enable close-on-exec semantics.

Returns an array of socket descriptors.

Returns `null` if an error occurred during socket creation.

**Kind**: instance method of [`socket`](#module_socket)  
**Returns**: `Array.<?module:socket.socket>` - Socket instances representing the newly created sockets.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [type] | `number` | `SOCK_STREAM` | The socket type, e.g., SOCK_STREAM or SOCK_DGRAM. It may also be bitwise OR-ed with SOCK_NONBLOCK or SOCK_CLOEXEC. |

**Example**  
```ucode
// Create a TCP socket pair
const tcp_sockets = pair(SOCK_STREAM);

// Create a nonblocking IPv6 UDP socket pair
const udp_sockets = pair(SOCK_DGRAM | SOCK_NONBLOCK);
```

### socket.socket
**Kind**: static class of [`socket`](#module_socket)  
**See**: [create()](#module_socket+create)  

* [.socket](#module_socket.socket)
    * _instance_
        * [.setopt(level, option, value)](#module_socket.socket+setopt) ⇒ `boolean`
        * [.getopt(level, option)](#module_socket.socket+getopt) ⇒ `\*`
        * [.fileno()](#module_socket.socket+fileno) ⇒ `number`
        * [.connect(address, port)](#module_socket.socket+connect) ⇒ `boolean`
        * [.send(data, [flags], [address])](#module_socket.socket+send) ⇒ `number`
        * [.recv([length], [flags], [address])](#module_socket.socket+recv) ⇒ `string`
        * [.sendmsg([data], [ancillaryData], [address], [flags])](#module_socket.socket+sendmsg) ⇒ `number`
        * [.recvmsg([sizes], [ancillarySize], [flags])](#module_socket.socket+recvmsg) ⇒ [`ReceivedMessage`](#module_socket.socket.ReceivedMessage)
        * [.bind(address)](#module_socket.socket+bind) ⇒ `boolean`
        * [.listen([backlog])](#module_socket.socket+listen) ⇒ `boolean`
        * [.accept([address], [flags])](#module_socket.socket+accept) ⇒ [`socket`](#module_socket.socket)
        * [.shutdown(how)](#module_socket.socket+shutdown) ⇒ `boolean`
        * [.peercred()](#module_socket.socket+peercred) ⇒ [`PeerCredentials`](#module_socket.socket.PeerCredentials)
        * [.peername()](#module_socket.socket+peername) ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
        * [.sockname()](#module_socket.socket+sockname) ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
        * [.close()](#module_socket.socket+close) ⇒ `boolean`
        * [.error([numeric])](#module_socket.socket+error) ⇒ `string` \| `number`
    * _static_
        * [.SocketAddress](#module_socket.socket.SocketAddress) : `Object`
        * [.ControlMessage](#module_socket.socket.ControlMessage) : `Object`
        * [.ReceivedMessage](#module_socket.socket.ReceivedMessage) : `Object`
        * [.PeerCredentials](#module_socket.socket.PeerCredentials) : `Object`

#### socket.setopt(level, option, value) ⇒ `boolean`
Sets options on the socket.

Sets the specified option on the socket to the given value.

Returns `true` if the option was successfully set.

Returns `null` if an error occurred.

**Kind**: instance method of [`socket`](#module_socket.socket)  

| Param | Type | Description |
| --- | --- | --- |
| level | `number` | The protocol level at which the option resides. This can be a level such as `SOL_SOCKET` for the socket API level or a specific protocol level defined by the system. |
| option | `number` | The socket option to set. This can be an integer representing the option, such as `SO_REUSEADDR`, or a constant defined by the system. |
| value | `\*` | The value to set the option to. The type of this argument depends on the specific option being set. It can be an integer, a boolean, a string, or a dictionary representing the value to set. If a dictionary is provided, it is internally translated to the corresponding C struct type required by the option. |

#### socket.getopt(level, option) ⇒ `\*`
Gets options from the socket.

Retrieves the value of the specified option from the socket.

Returns the value of the requested option.

Returns `null` if an error occurred or if the option is not supported.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**Returns**: `\*` - The value of the requested option. The type of the returned value depends
on the specific option being retrieved. It can be an integer, a boolean, a
string, or a dictionary representing a complex data structure.  

| Param | Type | Description |
| --- | --- | --- |
| level | `number` | The protocol level at which the option resides. This can be a level such as `SOL_SOCKET` for the socket API level or a specific protocol level defined by the system. |
| option | `number` | The socket option to retrieve. This can be an integer representing the option, such as `SO_REUSEADDR`, or a constant defined by the system. |

#### socket.fileno() ⇒ `number`
Returns the UNIX file descriptor number associated with the socket.

Returns the file descriptor number.

Returns `-1` if an error occurred.

**Kind**: instance method of [`socket`](#module_socket.socket)  

#### socket.connect(address, port) ⇒ `boolean`
Connects the socket to a remote address.

Attempts to establish a connection to the specified remote address.

Returns `true` if the connection is successfully established.
Returns `null` if an error occurred during the connection attempt.

**Kind**: instance method of [`socket`](#module_socket.socket)  

| Param | Type | Description |
| --- | --- | --- |
| address | `string` \| [`SocketAddress`](#module_socket.socket.SocketAddress) | The address of the remote endpoint to connect to. |
| port | `number` | The port number of the remote endpoint to connect to. |

#### socket.send(data, [flags], [address]) ⇒ `number`
Sends data through the socket.

Sends the provided data through the socket handle to the specified remote
address, if provided.

Returns the number of bytes sent.
Returns `null` if an error occurred during the send operation.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**See**: [sockaddr()](#module_socket+sockaddr)  

| Param | Type | Description |
| --- | --- | --- |
| data | `\*` | The data to be sent through the socket. String data is sent as-is, any other type is implicitly converted to a string first before being sent on the socket. |
| [flags] | `number` | Optional flags that modify the behavior of the send operation. |
| [address] | [`SocketAddress`](#module_socket.socket.SocketAddress) \| `Array.<number>` \| `string` | The address of the remote endpoint to send the data to. It can be either an IP address string, an array returned by [iptoarr()](module:core#iptoarr), or an object representing a network address. If not provided, the data is sent to the remote endpoint the socket is connected to. |

**Example**  
```ucode
// Send to connected socket
let tcp_sock = socket.create(socket.AF_INET, socket.SOCK_STREAM);
tcp_sock.connect("192.168.1.1", 80);
tcp_sock.send("GET / HTTP/1.0\r\n\r\n");

// Send a datagram on unconnected socket
let udp_sock = socket.create(socket.AF_INET, socket.SOCK_DGRAM);
udp_sock.send("Hello there!", 0, "255.255.255.255:9000");
udp_sock.send("Hello there!", 0, {
  family: socket.AF_INET,      // optional
  address: "255.255.255.255",
  port: 9000
});
```

#### socket.recv([length], [flags], [address]) ⇒ `string`
Receives data from the socket.

Receives data from the socket handle, optionally specifying the maximum
length of data to receive, flags to modify the receive behavior, and an
optional address dictionary where the function will place the address from
which the data was received (for unconnected sockets).

Returns a string containing the received data.
Returns an empty string if the remote side closed the socket.
Returns `null` if an error occurred during the receive operation.

**Kind**: instance method of [`socket`](#module_socket.socket)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [length] | `number` | `4096` | The maximum number of bytes to receive. |
| [flags] | `number` |  | Optional flags that modify the behavior of the receive operation. |
| [address] | `Object` |  | An object where the function will store the address from which the data was received. If provided, it will be filled with the details obtained from the sockaddr argument of the underlying `recvfrom()` syscall. See the type definition of [SocketAddress](#module_socket.socket.SocketAddress) for details on the format. |

#### socket.sendmsg([data], [ancillaryData], [address], [flags]) ⇒ `number`
Sends a message through the socket.

Sends a message through the socket handle, supporting complex message
structures including multiple data buffers and ancillary data. This function
allows for precise control over the message content and delivery behavior.

Returns the number of sent bytes.

Returns `null` if an error occurred.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**Returns**: `number` - Returns the number of bytes sent on success, or `null` if an error occurred.  

| Param | Type | Description |
| --- | --- | --- |
| [data] | `\*` | The data to be sent. If a string is provided, it is sent as is. If an array is specified, each item is sent as a separate `struct iovec`. Non-string values are implicitly converted to a string and sent. If omitted, only ancillary data and address are considered. |
| [ancillaryData] | [`Array.<ControlMessage>`](#module_socket.socket.ControlMessage) \| `string` | Optional ancillary data to be sent. If an array is provided, each element is converted to a control message. If a string is provided, it is sent as-is without further interpretation. Refer to [`recvmsg()`](#module_socket.socket+recvmsg) and [ControlMessage](#module_socket.socket.ControlMessage) for details. |
| [address] | [`SocketAddress`](#module_socket.socket.SocketAddress) | The destination address for the message. If provided, it sets or overrides the packet destination address. |
| [flags] | `number` | Optional flags to modify the behavior of the send operation. This should be a bitwise OR-ed combination of `MSG_*` flag values. |

**Example**  
```ucode
// Send file descriptors over domain socket
const f1 = fs.open("example.txt", "w");
const f2 = fs.popen("date +%s", "r");
const sk = socket.connect({ family: socket.AF_UNIX, path: "/tmp/socket" });
sk.sendmsg("Hi there, here's some descriptors!", [
	{ level: socket.SOL_SOCKET, type: socket.SCM_RIGHTS, data: [ f1, f2 ] }
]);

// Send multiple values in one datagram
sk.sendmsg([ "This", "is", "one", "message" ]);
```

#### socket.recvmsg([sizes], [ancillarySize], [flags]) ⇒ [`ReceivedMessage`](#module_socket.socket.ReceivedMessage)
Receives a message from the socket.

Receives a message from the socket handle, allowing for more complex data
reception compared to `recv()`. This includes the ability to receive
ancillary data (such as file descriptors, credentials, etc.), multiple
message segments, and optional flags to modify the receive behavior.

Returns an object containing the received message data, ancillary data,
and the sender's address.

Returns `null` if an error occurred during the receive operation.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**Returns**: [`ReceivedMessage`](#module_socket.socket.ReceivedMessage) - An object containing the received message data, ancillary data,
and the sender's address.  

| Param | Type | Description |
| --- | --- | --- |
| [sizes] | `Array.<number>` \| `number` | Specifies the sizes of the buffers used for receiving the message. If an array of numbers is provided, each number determines the size of an individual buffer segment, creating multiple `struct iovec` for reception. If a single number is provided, a single buffer of that size is used. |
| [ancillarySize] | `number` | The size allocated for the ancillary data buffer. If not provided, ancillary data is not processed. |
| [flags] | `number` | Optional flags to modify the behavior of the receive operation. This should be a bitwise OR-ed combination of flag values. |

**Example**  
```ucode
// Receive file descriptors over domain socket
const sk = socket.listen({ family: socket.AF_UNIX, path: "/tmp/socket" });
sk.setopt(socket.SOL_SOCKET, socket.SO_PASSCRED, true);

const msg = sk.recvmsg(1024, 1024);
for (let cmsg in msg.ancillary)
  if (cmsg.level == socket.SOL_SOCKET && cmsg.type == socket.SCM_RIGHTS)
    print(`Got some descriptors: ${cmsg.data}!\n`);

// Receive message in segments of 10, 128 and 512 bytes
const msg = sk.recvmsg([ 10, 128, 512 ]);
print(`Message parts: ${msg.data[0]}, ${msg.data[1]}, ${msg.data[2]}\n`);

// Peek buffer
const msg = sk.recvmsg(0, 0, socket.MSG_PEEK|socket.MSG_TRUNC);
print(`Received ${length(msg.data)} bytes, ${msg.length} bytes available\n`);
```

#### socket.bind(address) ⇒ `boolean`
Binds a socket to a specific address.

This function binds the socket to the specified address.

Returns `true` if the socket is successfully bound.

Returns `null` on error, e.g. when the address is in use.

**Kind**: instance method of [`socket`](#module_socket.socket)  

| Param | Type | Description |
| --- | --- | --- |
| address | `string` \| [`SocketAddress`](#module_socket.socket.SocketAddress) | The IP address to bind the socket to. |

**Example**  
```text
const sock = socket.create(…);
const success = sock.bind("192.168.0.1:80");

if (success)
    print(`Socket bound successfully!\n`);
else
    print(`Failed to bind socket: ${sock.error()}.\n`);
```

#### socket.listen([backlog]) ⇒ `boolean`
Listen for connections on a socket.

This function marks the socket as a passive socket, that is, as a socket that
will be used to accept incoming connection requests using `accept()`.

The `backlog` parameter specifies the maximum length to which the queue of
pending connections may grow. If a connection request arrives when the queue
is full, the client connection might get refused.

If `backlog` is not provided, it defaults to 128.

Returns `true` if the socket is successfully marked as passive.
Returns `null` if an error occurred, e.g. when the requested port is in use.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**See**: [accept()](#module_socket.socket+accept)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [backlog] | `number` | `128` | The maximum length of the queue of pending connections. |

**Example**  
```text
const sock = socket.create(…);
sock.bind(…);

const success = sock.listen(10);
if (success)
    print(`Socket is listening for incoming connections!\n`);
else
    print(`Failed to listen on socket: ${sock.error()}\n`);
```

#### socket.accept([address], [flags]) ⇒ [`socket`](#module_socket.socket)
Accept a connection on a socket.

This function accepts a connection on the socket. It extracts the first
connection request on the queue of pending connections, creates a new
connected socket, and returns a new socket handle referring to that socket.
The newly created socket is not in listening state and has no backlog.

When a optional `address` dictionary is provided, it is populated with the
remote address details of the peer socket.

The optional `flags` parameter is a bitwise-or-ed number of flags to modify
the behavior of accepted peer socket. Possible values are:
- `SOCK_CLOEXEC`: Enable close-on-exec semantics for the new socket.
- `SOCK_NONBLOCK`: Enable nonblocking mode for the new socket.

Returns a socket handle representing the newly created peer socket of the
accepted connection.

Returns `null` if an error occurred.

**Kind**: instance method of [`socket`](#module_socket.socket)  

| Param | Type | Description |
| --- | --- | --- |
| [address] | `object` | An optional dictionary to receive the address details of the peer socket. See [SocketAddress](#module_socket.socket.SocketAddress) for details. |
| [flags] | `number` | Optional flags to modify the behavior of the peer socket. |

**Example**  
```text
const sock = socket.create(…);
sock.bind(…);
sock.listen();

const peerAddress = {};
const newSocket = sock.accept(peerAddress, socket.SOCK_CLOEXEC);
if (newSocket)
    print(`Accepted connection from: ${peerAddress}\n`);
else
    print(`Failed to accept connection: ${sock.error()}\n`);
```

#### socket.shutdown(how) ⇒ `boolean`
Shutdown part of a full-duplex connection.

This function shuts down part of the full-duplex connection associated with
the socket handle. The `how` parameter specifies which half of the connection
to shut down. It can take one of the following constant values:

- `SHUT_RD`: Disables further receive operations.
- `SHUT_WR`: Disables further send operations.
- `SHUT_RDWR`: Disables further send and receive operations.

Returns `true` if the shutdown operation is successful.
Returns `null` if an error occurred.

**Kind**: instance method of [`socket`](#module_socket.socket)  

| Param | Type | Description |
| --- | --- | --- |
| how | `number` | Specifies which half of the connection to shut down. It can be one of the following constant values: `SHUT_RD`, `SHUT_WR`, or `SHUT_RDWR`. |

**Example**  
```text
const sock = socket.create(…);
sock.connect(…);
// Perform data exchange…

const success = sock.shutdown(socket.SHUT_WR);
if (success)
    print(`Send operations on socket shut down successfully.\n`);
else
    print(`Failed to shut down send operations: ${sock.error()}\n`);
```

#### socket.peercred() ⇒ [`PeerCredentials`](#module_socket.socket.PeerCredentials)
Retrieves the peer credentials.

This function retrieves the remote uid, gid and pid of a connected UNIX
domain socket.

Returns the remote credentials if the operation is successful.
Returns `null` on error.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**Example**  
```text
const sock = socket.create(socket.AF_UNIX, …);
sock.connect(…);

const peerCredentials = sock.peercred();
if (peerCredentials)
    print(`Peer credentials: ${peerCredentials}\n`);
else
    print(`Failed to retrieve peer credentials: ${sock.error()}\n`);
```

#### socket.peername() ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
Retrieves the remote address.

This function retrieves the remote address of a connected socket.

Returns the remote address if the operation is successful.
Returns `null` on error.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**See**: [sockname()](#module_socket.socket+sockname)  
**Example**  
```text
const sock = socket.create(…);
sock.connect(…);

const peerAddress = sock.peername();
if (peerAddress)
    print(`Connected to ${peerAddress}\n`);
else
    print(`Failed to retrieve peer address: ${sock.error()}\n`);
```

#### socket.sockname() ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
Retrieves the local address.

This function retrieves the local address of a bound or connected socket.

Returns the local address if the operation is successful.
Returns `null` on error.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**See**: [peername()](#module_socket.socket+peername)  
**Example**  
```text
const sock = socket.create(…);
sock.connect(…);

const myAddress = sock.sockname();
if (myAddress)
    print(`My source IP address is ${myAddress}\n`);
else
    print(`Failed to retrieve peer address: ${sock.error()}\n`);
```

#### socket.close() ⇒ `boolean`
Closes the socket.

This function closes the socket, releasing its resources and terminating its
associated connections.

Returns `true` if the socket was successfully closed.
Returns `null` on error.

**Kind**: instance method of [`socket`](#module_socket.socket)  
**Example**  
```text
const sock = socket.create(…);
sock.connect(…);
// Perform operations with the socket…
sock.close();
```

#### socket.error([numeric]) ⇒ `string` \| `number`
Query error information.

Returns a string containing a description of the last occurred error when
the *numeric* argument is absent or false.

Returns a positive (`errno`) or negative (`EAI_*` constant) error code number
when the *numeric* argument is `true`.

Returns `null` if there is no error information.

**Kind**: instance method of [`socket`](#module_socket.socket)  

| Param | Type | Description |
| --- | --- | --- |
| [numeric] | `boolean` | Whether to return a numeric error code (`true`) or a human readable error message (false). |

**Example**  
```ucode
// Trigger socket error by attempting to bind IPv6 address with IPv4 socket
socket.create(socket.AF_INET, socket.SOCK_STREAM, 0).bind("::", 8080);

// Print error (should yield "Address family not supported by protocol")
print(socket.error(), "\n");

// Trigger resolve error
socket.addrinfo("doesnotexist.org");

// Query error code (should yield -2 for EAI_NONAME)
print(socket.error(true), "\n");  //
```

#### socket.SocketAddress : `Object`
**Kind**: static typedef of [`socket`](#module_socket.socket)  
**Properties**

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| family | `number` |  | Address family, one of AF_INET, AF_INET6, AF_UNIX or AF_PACKET. |
| address | `string` |  | IPv4/IPv6 address string (AF_INET or AF_INET6 only) or hardware address in hexadecimal notation (AF_PACKET only). |
| [port] | `number` |  | Port number (AF_INET or AF_INET6 only). |
| [flowinfo] | `number` |  | IPv6 flow information (AF_INET6 only). |
| [interface] | `string` \| `number` |  | Link local address scope (for IPv6 sockets) or bound network interface (for packet sockets), either a network device name string or a nonzero positive integer representing a network interface index (AF_INET6 and AF_PACKET only). |
| path | `string` |  | Domain socket filesystem path (AF_UNIX only). |
| [protocol] | `number` | `0` | Physical layer protocol (AF_PACKET only). |
| [hardware_type] | `number` | `0` | ARP hardware type (AF_PACKET only). |
| [packet_type] | `number` | `PACKET_HOST` | Packet type (AF_PACKET only). |

#### socket.ControlMessage : `Object`
Represents a single control (ancillary data) message returned
in the *ancillary* array by [`recvmsg()`](#module_socket.socket+recvmsg).

**Kind**: static typedef of [`socket`](#module_socket.socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| level | `number` | The message socket level (`cmsg_level`), e.g. `SOL_SOCKET`. |
| type | `number` | The protocol specific message type (`cmsg_type`), e.g. `SCM_RIGHTS`. |
| data | `\*` | The payload of the control message. If the control message type is known by the socket module, it is represented as a mixed value (array, object, number, etc.) with structure specific to the control message type. If the control message cannot be decoded, *data* is set to a string value containing the raw payload. |

#### socket.ReceivedMessage : `Object`
Represents a message object returned by
[`recvmsg()`](#module_socket.socket+recvmsg).

**Kind**: static typedef of [`socket`](#module_socket.socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| flags | `number` | Integer value containing bitwise OR-ed `MSG_*` result flags returned by the underlying receive call. |
| length | `number` | Integer value containing the number of bytes returned by the `recvmsg()` syscall, which might be larger than the received data in case `MSG_TRUNC` was passed. |
| address | [`SocketAddress`](#module_socket.socket.SocketAddress) | The address from which the message was received. |
| data | `Array.<string>` \| `string` | An array of strings, each representing the received message data. Each string corresponds to one buffer size specified in the *sizes* argument. If a single receive size was passed instead of an array of sizes, *data* will hold a string containing the received data. |
| [ancillary] | [`Array.<ControlMessage>`](#module_socket.socket.ControlMessage) | An array of received control messages. Only included if a non-zero positive *ancillarySize* was passed to `recvmsg()`. |

#### socket.PeerCredentials : `Object`
Represents a credentials information object returned by
[`peercred()`](#module_socket.socket+peercred).

**Kind**: static typedef of [`socket`](#module_socket.socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| uid | `number` | The effective user ID the remote socket endpoint. |
| gid | `number` | The effective group ID the remote socket endpoint. |
| pid | `number` | The ID of the process the remote socket endpoint belongs to. |

### socket.AddressInfo : `Object`
Represents a network address information object returned by
[`addrinfo()`](#module_socket+addrinfo).

**Kind**: static typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| addr | [`SocketAddress`](#module_socket.socket.SocketAddress) |  | A socket address structure. |
| [canonname] | `string` | `null` | The canonical hostname associated with the address. |
| family | `number` |  | The address family (e.g., `2` for `AF_INET`, `10` for `AF_INET6`). |
| flags | `number` |  | Additional flags indicating properties of the address. |
| protocol | `number` |  | The protocol number. |
| socktype | `number` |  | The socket type (e.g., `1` for `SOCK_STREAM`, `2` for `SOCK_DGRAM`). |

### socket.PollSpec : `Array`
Represents a poll state serving as input parameter and return value type for
[`poll()`](#module_socket+poll).

**Kind**: static typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| 0 | [`socket`](#module_socket.socket) | The polled socket instance. |
| 1 | `number` | Requested or returned status flags of the polled socket instance. |

### socket~Address Families
Constants representing address families and socket domains.

**Kind**: inner typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| AF_UNSPEC | `number` | Unspecified address family. |
| AF_UNIX | `number` | UNIX domain sockets. |
| AF_INET | `number` | IPv4 Internet protocols. |
| AF_INET6 | `number` | IPv6 Internet protocols. |
| AF_PACKET | `number` | Low-level packet interface. |

### socket~Socket Types
The `SOCK_*` type and flag constants are used by
[create()](#module_socket+create) to specify the type of socket to
open. The [accept()](#module_socket.socket+accept) function
recognizes the `SOCK_NONBLOCK` and `SOCK_CLOEXEC` flags and applies them
to accepted peer sockets.

**Kind**: inner typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| SOCK_STREAM | `number` | Provides sequenced, reliable, two-way, connection-based byte streams. |
| SOCK_DGRAM | `number` | Supports datagrams (connectionless, unreliable messages of a fixed maximum length). |
| SOCK_RAW | `number` | Provides raw network protocol access. |
| SOCK_PACKET | `number` | Obsolete and should not be used. |
| SOCK_NONBLOCK | `number` | Enables non-blocking operation. |
| SOCK_CLOEXEC | `number` | Sets the close-on-exec flag on the new file descriptor. |

### socket~Message Flags
The `MSG_*` flag constants are commonly used in conjunction with the
[send()](#module_socket.socket+send) and
[recv()](#module_socket.socket+recv) functions.

**Kind**: inner typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| MSG_CONFIRM | `number` | Confirm path validity. |
| MSG_DONTROUTE | `number` | Send without using routing tables. |
| MSG_DONTWAIT | `number` | Enables non-blocking operation. |
| MSG_EOR | `number` | End of record. |
| MSG_MORE | `number` | Sender will send more. |
| MSG_NOSIGNAL | `number` | Do not generate SIGPIPE. |
| MSG_OOB | `number` | Process out-of-band data. |
| MSG_FASTOPEN | `number` | Send data in TCP SYN. |
| MSG_CMSG_CLOEXEC | `number` | Sets the close-on-exec flag on the received file descriptor. |
| MSG_ERRQUEUE | `number` | Receive errors from ICMP. |
| MSG_PEEK | `number` | Peeks at incoming messages. |
| MSG_TRUNC | `number` | Report if datagram truncation occurred. |
| MSG_WAITALL | `number` | Wait for full message. |

### socket~IP Protocol Constants
The `IPPROTO_IP` constant specifies the IP protocol number and may be
passed as third argument to [create()](#module_socket+create) as well
as *level* argument value to [getopt()](#module_socket.socket+getopt)
and [setopt()](#module_socket.socket+setopt).

The `IP_*` constants are option names recognized by
[getopt()](#module_socket.socket+getopt)
and [setopt()](#module_socket.socket+setopt), in conjunction with
the `IPPROTO_IP` socket level.

**Kind**: inner typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| IPPROTO_IP | `number` | Dummy protocol for IP. |
| IP_ADD_MEMBERSHIP | `number` | Add an IP group membership. |
| IP_ADD_SOURCE_MEMBERSHIP | `number` | Add an IP group/source membership. |
| IP_BIND_ADDRESS_NO_PORT | `number` | Bind to the device only. |
| IP_BLOCK_SOURCE | `number` | Block IP group/source. |
| IP_DROP_MEMBERSHIP | `number` | Drop an IP group membership. |
| IP_DROP_SOURCE_MEMBERSHIP | `number` | Drop an IP group/source membership. |
| IP_FREEBIND | `number` | Allow binding to an IP address not assigned to a network interface. |
| IP_HDRINCL | `number` | Header is included with data. |
| IP_MSFILTER | `number` | Filter IP multicast source memberships. |
| IP_MTU | `number` | Path MTU discovery. |
| IP_MTU_DISCOVER | `number` | Control Path MTU discovery. |
| IP_MULTICAST_ALL | `number` | Receive all multicast packets. |
| IP_MULTICAST_IF | `number` | Set outgoing interface for multicast packets. |
| IP_MULTICAST_LOOP | `number` | Control multicast packet looping. |
| IP_MULTICAST_TTL | `number` | Set time-to-live for outgoing multicast packets. |
| IP_NODEFRAG | `number` | Don't fragment IP packets. |
| IP_OPTIONS | `number` | Set/get IP options. |
| IP_PASSSEC | `number` | Pass security information. |
| IP_PKTINFO | `number` | Receive packet information. |
| IP_RECVERR | `number` | Receive all ICMP errors. |
| IP_RECVOPTS | `number` | Receive all IP options. |
| IP_RECVORIGDSTADDR | `number` | Receive original destination address of the socket. |
| IP_RECVTOS | `number` | Receive IP TOS. |
| IP_RECVTTL | `number` | Receive IP TTL. |
| IP_RETOPTS | `number` | Set/get IP options. |
| IP_ROUTER_ALERT | `number` | Receive ICMP msgs generated by router. |
| IP_TOS | `number` | IP type of service and precedence. |
| IP_TRANSPARENT | `number` | Transparent proxy support. |
| IP_TTL | `number` | IP time-to-live. |
| IP_UNBLOCK_SOURCE | `number` | Unblock IP group/source. |

### socket~IPv6 : `Object`
The `IPPROTO_IPV6` constant specifies the IPv6 protocol number and may be
passed as third argument to [create()](#module_socket+create) as well
as *level* argument value to [getopt()](#module_socket.socket+getopt)
and [setopt()](#module_socket.socket+setopt).

The `IPV6_*` constants are option names recognized by
[getopt()](#module_socket.socket+getopt)
and [setopt()](#module_socket.socket+setopt), in conjunction with
the `IPPROTO_IPV6` socket level.

**Kind**: inner typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| IPPROTO_IPV6 | `number` | The IPv6 protocol. |
| IPV6_ADDRFORM | `number` | Turn an AF_INET6 socket into a socket of a different address family. Only AF_INET is supported. |
| IPV6_ADDR_PREFERENCES | `number` | Specify preferences for address selection. |
| IPV6_ADD_MEMBERSHIP | `number` | Add an IPv6 group membership. |
| IPV6_AUTHHDR | `number` | Set delivery of the authentication header control message for incoming datagrams. |
| IPV6_AUTOFLOWLABEL | `number` | Enable or disable automatic flow labels. |
| IPV6_DONTFRAG | `number` | Control whether the socket allows IPv6 fragmentation. |
| IPV6_DROP_MEMBERSHIP | `number` | Drop an IPv6 group membership. |
| IPV6_DSTOPTS | `number` | Set delivery of the destination options control message for incoming datagrams. |
| IPV6_FLOWINFO_SEND | `number` | Control whether flow information is sent. |
| IPV6_FLOWINFO | `number` | Set delivery of the flow ID control message for incoming datagrams. |
| IPV6_FLOWLABEL_MGR | `number` | Manage flow labels. |
| IPV6_FREEBIND | `number` | Allow binding to an IP address not assigned to a network interface. |
| IPV6_HOPLIMIT | `number` | Set delivery of the hop limit control message for incoming datagrams. |
| IPV6_HOPOPTS | `number` | Set delivery of the hop options control message for incoming datagrams. |
| IPV6_JOIN_ANYCAST | `number` | Join an anycast group. |
| IPV6_LEAVE_ANYCAST | `number` | Leave an anycast group. |
| IPV6_MINHOPCOUNT | `number` | Set the minimum hop count. |
| IPV6_MTU | `number` | Retrieve or set the MTU to be used for the socket. |
| IPV6_MTU_DISCOVER | `number` | Control path-MTU discovery on the socket. |
| IPV6_MULTICAST_ALL | `number` | Control whether the socket receives all multicast packets. |
| IPV6_MULTICAST_HOPS | `number` | Set the multicast hop limit for the socket. |
| IPV6_MULTICAST_IF | `number` | Set the device for outgoing multicast packets on the socket. |
| IPV6_MULTICAST_LOOP | `number` | Control whether the socket sees multicast packets that it has sent itself. |
| IPV6_PKTINFO | `number` | Set delivery of the IPV6_PKTINFO control message on incoming datagrams. |
| IPV6_RECVDSTOPTS | `number` | Control receiving of the destination options control message. |
| IPV6_RECVERR | `number` | Control receiving of asynchronous error options. |
| IPV6_RECVFRAGSIZE | `number` | Control receiving of fragment size. |
| IPV6_RECVHOPLIMIT | `number` | Control receiving of hop limit. |
| IPV6_RECVHOPOPTS | `number` | Control receiving of hop options. |
| IPV6_RECVORIGDSTADDR | `number` | Control receiving of the original destination address. |
| IPV6_RECVPATHMTU | `number` | Control receiving of path MTU. |
| IPV6_RECVPKTINFO | `number` | Control receiving of packet information. |
| IPV6_RECVRTHDR | `number` | Control receiving of routing header. |
| IPV6_RECVTCLASS | `number` | Control receiving of traffic class. |
| IPV6_ROUTER_ALERT_ISOLATE | `number` | Control isolation of router alert messages. |
| IPV6_ROUTER_ALERT | `number` | Pass forwarded packets containing a router alert hop-by-hop option to this socket. |
| IPV6_RTHDR | `number` | Set delivery of the routing header control message for incoming datagrams. |
| IPV6_RTHDRDSTOPTS | `number` | Set delivery of the routing header destination options control message. |
| IPV6_TCLASS | `number` | Set the traffic class. |
| IPV6_TRANSPARENT | `number` | Enable transparent proxy support. |
| IPV6_UNICAST_HOPS | `number` | Set the unicast hop limit for the socket. |
| IPV6_UNICAST_IF | `number` | Set the interface for outgoing unicast packets. |
| IPV6_V6ONLY | `number` | Restrict the socket to sending and receiving IPv6 packets only. |

### socket~Socket Option Constants
The `SOL_SOCKET` constant is passed as *level* argument to the
[getopt()](#module_socket.socket+getopt) and
[setopt()](#module_socket.socket+setopt) functions in order to set
or retrieve generic socket option values.

The `SO_*` constants are passed as *option* argument in conjunction with
the `SOL_SOCKET` level to specify the specific option to get or set on
the socket.

**Kind**: inner typedef of [`socket`](#module_socket)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| SOL_SOCKET | `number` | Socket options at the socket API level. |
| SO_ACCEPTCONN | `number` | Reports whether socket listening is enabled. |
| SO_ATTACH_BPF | `number` | Attach BPF program to socket. |
| SO_ATTACH_FILTER | `number` | Attach a socket filter. |
| SO_ATTACH_REUSEPORT_CBPF | `number` | Attach BPF program for cgroup and skb program reuseport hook. |
| SO_ATTACH_REUSEPORT_EBPF | `number` | Attach eBPF program for cgroup and skb program reuseport hook. |
| SO_BINDTODEVICE | `number` | Bind socket to a specific interface. |
| SO_BROADCAST | `number` | Allow transmission of broadcast messages. |
| SO_BUSY_POLL | `number` | Enable busy polling. |
| SO_DEBUG | `number` | Enable socket debugging. |
| SO_DETACH_BPF | `number` | Detach BPF program from socket. |
| SO_DETACH_FILTER | `number` | Detach a socket filter. |
| SO_DOMAIN | `number` | Retrieves the domain of the socket. |
| SO_DONTROUTE | `number` | Send packets directly without routing. |
| SO_ERROR | `number` | Retrieves and clears the error status for the socket. |
| SO_INCOMING_CPU | `number` | Retrieves the CPU number on which the last packet was received. |
| SO_INCOMING_NAPI_ID | `number` | Retrieves the NAPI ID of the device. |
| SO_KEEPALIVE | `number` | Enable keep-alive packets. |
| SO_LINGER | `number` | Set linger on close. |
| SO_LOCK_FILTER | `number` | Set or get the socket filter lock state. |
| SO_MARK | `number` | Set the mark for packets sent through the socket. |
| SO_OOBINLINE | `number` | Enables out-of-band data to be received in the normal data stream. |
| SO_PASSCRED | `number` | Enable the receiving of SCM_CREDENTIALS control messages. |
| SO_PASSSEC | `number` | Enable the receiving of security context. |
| SO_PEEK_OFF | `number` | Returns the number of bytes in the receive buffer without removing them. |
| SO_PEERCRED | `number` | Retrieves the credentials of the foreign peer. |
| SO_PEERSEC | `number` | Retrieves the security context of the foreign peer. |
| SO_PRIORITY | `number` | Set the protocol-defined priority for all packets. |
| SO_PROTOCOL | `number` | Retrieves the protocol number. |
| SO_RCVBUF | `number` | Set the receive buffer size. |
| SO_RCVBUFFORCE | `number` | Set the receive buffer size forcefully. |
| SO_RCVLOWAT | `number` | Set the minimum number of bytes to process for input operations. |
| SO_RCVTIMEO | `number` | Set the timeout for receiving data. |
| SO_REUSEADDR | `number` | Allow the socket to

---

# ucode module: struct

> **Live docs:** https://ucode.mein.io/module-struct.html

---

## Handle Packed Binary Data

The `struct` module provides routines for interpreting byte strings as packed
binary data.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { pack, unpack } from 'struct';

  let buffer = pack('bhl', -13, 1234, 444555666);
  let values = unpack('bhl', buffer);
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as struct from 'struct';

  let buffer = struct.pack('bhl', -13, 1234, 444555666);
  let values = struct.unpack('bhl', buffer);
  ```

Additionally, the struct module namespace may also be imported by invoking
the `ucode` interpreter with the `-lstruct` switch.

## Format Strings

Format strings describe the data layout when packing and unpacking data.
They are built up from format-characters, which specify the type of data
being packed/unpacked. In addition, special characters control the byte
order, size and alignment.

Each format string consists of an optional prefix character which describes
the overall properties of the data and one or more format characters which
describe the actual data values and padding.

### Byte Order, Size, and Alignment

By default, C types are represented in the machine's native format and byte
order, and properly aligned by skipping pad bytes if necessary (according to
the rules used by the C compiler).

This behavior is chosen so that the bytes of a packed struct correspond
exactly to the memory layout of the corresponding C struct.

Whether to use native byte ordering and padding or standard formats depends
on the application.

Alternatively, the first character of the format string can be used to indicate
the byte order, size and alignment of the packed data, according to the
following table:

| Character | Byte order             | Size     | Alignment |
|-----------|------------------------|----------|-----------|
| `@`       | native                 | native   | native    |
| `=`       | native                 | standard | none      |
| `<`       | little-endian          | standard | none      |
| `>`       | big-endian             | standard | none      |
| `!`       | network (= big-endian) | standard | none      |

If the first character is not one of these, `'@'` is assumed.

Native byte order is big-endian or little-endian, depending on the
host system. For example, Intel x86, AMD64 (x86-64), and Apple M1 are
little-endian; IBM z and many legacy architectures are big-endian.

Native size and alignment are determined using the C compiler's
`sizeof` expression. This is always combined with native byte order.

Standard size depends only on the format character; see the table in
the `format-characters` section.

Note the difference between `'@'` and `'='`: both use native byte order,
but the size and alignment of the latter is standardized.

The form `'!'` represents the network byte order which is always big-endian
as defined in `IETF RFC 1700`.

There is no way to indicate non-native byte order (force byte-swapping); use
the appropriate choice of `'<'` or `'>'`.

Notes:

(1) Padding is only automatically added between successive structure members.
    No padding is added at the beginning or the end of the encoded struct.

(2) No padding is added when using non-native size and alignment, e.g.
    with '<', '>', '=', and '!'.

(3) To align the end of a structure to the alignment requirement of a
    particular type, end the format with the code for that type with a repeat
    count of zero.

### Format Characters

Format characters have the following meaning; the conversion between C and
ucode values should be obvious given their types.  The 'Standard size' column
refers to the size of the packed value in bytes when using standard size;
that is, when the format string starts with one of `'<'`, `'>'`, `'!'` or
`'='`.  When using native size, the size of the packed value is platform
dependent.

| Format | C Type               | Ucode type | Standard size  | Notes    |
|--------|----------------------|------------|----------------|----------|
| `x`    | *pad byte*           | *no value* |                | (7)      |
| `c`    | `char`               | string     | 1              |          |
| `b`    | `signed char`        | int        | 1              | (1), (2) |
| `B`    | `unsigned char`      | int        | 1              | (2)      |
| `?`    | `_Bool`              | bool       | 1              | (1)      |
| `h`    | `short`              | int        | 2              | (2)      |
| `H`    | `unsigned short`     | int        | 2              | (2)      |
| `i`    | `int`                | int        | 4              | (2)      |
| `I`    | `unsigned int`       | int        | 4              | (2)      |
| `l`    | `long`               | int        | 4              | (2)      |
| `L`    | `unsigned long`      | int        | 4              | (2)      |
| `q`    | `long long`          | int        | 8              | (2)      |
| `Q`    | `unsigned long long` | int        | 8              | (2)      |
| `n`    | `ssize_t`            | int        |                | (3)      |
| `N`    | `size_t`             | int        |                | (3)      |
| `e`    | (6)                  | double     | 2              | (4)      |
| `f`    | `float`              | double     | 4              | (4)      |
| `d`    | `double`             | double     | 8              | (4)      |
| `s`    | `char[]`             | double     |                | (9)      |
| `p`    | `char[]`             | double     |                | (8)      |
| `P`    | `void *`             | int        |                | (5)      |
| `*`    | `char[]`             | string     |                | (10)     |
| `X`    | `char[]`             | string     |                | (11)     |
| `Z`    | `char[]`             | string     |                | (12)     |

Notes:

- (1) The `'?'` conversion code corresponds to the `_Bool` type defined by
   C99. If this type is not available, it is simulated using a `char`. In
   standard mode, it is always represented by one byte.

- (2) When attempting to pack a non-integer using any of the integer
   conversion codes, this module attempts to convert the given value into an
   integer. If the value is not convertible, a type error exception is thrown.

- (3) The `'n'` and `'N'` conversion codes are only available for the native
   size (selected as the default or with the `'@'` byte order character).
   For the standard size, you can use whichever of the other integer formats
   fits your application.

- (4) For the `'f'`, `'d'` and `'e'` conversion codes, the packed
   representation uses the IEEE 754 binary32, binary64 or binary16 format
   (for `'f'`, `'d'` or `'e'` respectively), regardless of the floating-point
   format used by the platform.

- (5) The `'P'` format character is only available for the native byte
   ordering (selected as the default or with the `'@'` byte order character).
   The byte order character `'='` chooses to use little- or big-endian
   ordering based on the host system. The struct module does not interpret
   this as native ordering, so the `'P'` format is not available.

- (6) The IEEE 754 binary16 "half precision" type was introduced in the 2008
   revision of the `IEEE 754` standard. It has a sign bit, a 5-bit exponent
   and 11-bit precision (with 10 bits explicitly stored), and can represent
   numbers between approximately `6.1e-05` and `6.5e+04` at full precision.
   This type is not widely supported by C compilers: on a typical machine, an
   unsigned short can be used for storage, but not for math operations. See
   the Wikipedia page on the `half-precision floating-point format` for more
   information.

- (7) When packing, `'x'` inserts one NUL byte.

- (8) The `'p'` format character encodes a "Pascal string", meaning a short
   variable-length string stored in a *fixed number of bytes*, given by the
   count. The first byte stored is the length of the string, or 255,
   whichever is smaller.  The bytes of the string follow.  If the string
   passed in to `pack()` is too long (longer than the count minus 1), only
   the leading `count-1` bytes of the string are stored.  If the string is
   shorter than `count-1`, it is padded with null bytes so that exactly count
   bytes in all are used.  Note that for `unpack()`, the `'p'` format
   character consumes `count` bytes, but that the string returned can never
   contain more than 255 bytes.

- (9) For the `'s'` format character, the count is interpreted as the length
   of the bytes, not a repeat count like for the other format characters; for
   example, `'10s'` means a single 10-byte string mapping to or from a single
   ucode byte string, while `'10c'` means 10 separate one byte character
   elements (e.g., `cccccccccc`) mapping to or from ten different ucode byte
   strings. If a count is not given, it defaults to 1. For packing, the
   string is truncated or padded with null bytes as appropriate to make it
   fit. For unpacking, the resulting bytes object always has exactly the
   specified number of bytes.  As a special case, `'0s'` means a single,
   empty string (while `'0c'` means 0 characters).

- (10) The `*` format character serves as wildcard. For `pack()` it will
   append the corresponding byte argument string as-is, not applying any
   padding or zero filling. When a repeat count is given, that many bytes of
   the input byte string argument will be appended at most on `pack()`,
   effectively truncating longer input strings. For `unpack()`, the wildcard
   format will yield a byte string containing the entire remaining input data
   bytes, or - when a repeat count is given - that many bytes of input data
   at most.

- (11) The `X` format character handles hexadecimal encoding of binary data.
   On `pack()`, the argument is a hexadecimal string; with no repeat count the
   entire string is decoded into binary, while a repeat count limits the
   number of output bytes (truncating longer input). On `unpack()`, the input
   binary data is converted into a hexadecimal string, using all remaining
   bytes by default, or at most the specified number of bytes when a repeat
   count is given. Decoding accepts both upper- and lowercase hex digits, but
   encoding always produces lowercase output. The encoded text length is
   exactly twice the number of processed binary bytes.

- (12) The `Z` format character behaves like `X`, but uses base64 encoding
   instead of hexadecimal. On `pack()`, the argument is a base64 string; by
   default the entire string is decoded into binary, or at most the specified
   number of bytes when a repeat count is given. On `unpack()`, the input
   binary data is converted into a base64 string, consuming all remaining
   bytes by default, or at most the repeat count if given. The encoded base64
   string is approximately 1.4 times the size of the processed binary data.

A format character may be preceded by an integral repeat count.  For example,
the format string `'4h'` means exactly the same as `'hhhh'`.

Whitespace characters between formats are ignored; a count and its format
must not contain whitespace though.

When packing a value `x` using one of the integer formats (`'b'`,
`'B'`, `'h'`, `'H'`, `'i'`, `'I'`, `'l'`, `'L'`,
`'q'`, `'Q'`), if `x` is outside the valid range for that format, a type
error exception is raised.

For the `'?'` format character, the return value is either `true` or `false`.
When packing, the truish result value of the argument is used. Either 0 or 1
in the native or standard bool representation will be packed, and any
non-zero value will be `true` when unpacking.

## Examples

Note:
   Native byte order examples (designated by the `'@'` format prefix or
   lack of any prefix character) may not match what the reader's
   machine produces as
   that depends on the platform and compiler.

Pack and unpack integers of three different sizes, using big endian
ordering:

```ucode
import { pack, unpack } from 'struct';

pack(">bhl", 1, 2, 3);  // "\x01\x00\x02\x00\x00\x00\x03"
unpack(">bhl", "\x01\x00\x02\x00\x00\x00\x03");  // [ 1, 2, 3 ]
```

Attempt to pack an integer which is too large for the defined field:

```bash
$ ucode -lstruct -p 'struct.pack(">h", 99999)'
Type error: Format 'h' requires numeric argument between -32768 and 32767
In [-p argument], line 1, byte 24:

 `struct.pack(">h", 99999)`
  Near here -------------^
```

Demonstrate the difference between `'s'` and `'c'` format characters:

```ucode
import { pack } from 'struct';

pack("@ccc", "1", "2", "3");  // "123"
pack("@3s", "123");           // "123"
```

The ordering of format characters may have an impact on size in native
mode since padding is implicit. In standard mode, the user is
responsible for inserting any desired padding.

Note in the first `pack()` call below that three NUL bytes were added after
the packed `'#'` to align the following integer on a four-byte boundary.
In this example, the output was produced on a little endian machine:

```ucode
import { pack } from 'struct';

pack("@ci", "#", 0x12131415);  // "#\x00\x00\x00\x15\x14\x13\x12"
pack("@ic", 0x12131415, "#");  // "\x15\x14\x13\x12#"
```

The following format `'ih0i'` results in two pad bytes being added at the
end, assuming the platform's ints are aligned on 4-byte boundaries:

```ucode
import { pack } from 'struct';

pack("ih0i", 0x01010101, 0x0202);  // "\x01\x01\x01\x01\x02\x02\x00\x00"
```

Use the wildcard format to extract the remainder of the input data:

```ucode
import { unpack } from 'struct';

unpack("ccc*", "foobarbaz");   // [ "f", "o", "o", "barbaz" ]
unpack("ccc3*", "foobarbaz");  // [ "f", "o", "o", "bar" ]
```

Use the wildcard format to pack binary stings as-is into the result data:

```ucode
import { pack } from 'struct';

pack("h*h", 0x0101, "\x02\x00\x03", 0x0404);  // "\x01\x01\x02\x00\x03\x04\x04"
pack("c3*c", "a", "foobar", "c");  // "afooc"
```

### struct.pack(format, ...values) ⇒ `string`
Pack given values according to specified format.

The `pack()` function creates a byte string containing the argument values
packed according to the given format string.

Returns the packed string.

Raises a runtime exception if a given argument value does not match the
required type of the corresponding format string directive or if and invalid
format string is provided.

**Kind**: instance method of [`struct`](#module_struct)  

| Param | Type | Description |
| --- | --- | --- |
| format | `string` | The format string. |
| ...values | `\*` | Variable number of values to pack. |

**Example**  
```ucode
// Pack the values 1, 2, 3 as three consecutive unsigned int values
// in network byte order.
const data = pack('!III', 1, 2, 3);
```

### struct.unpack(format, input, [offset]) ⇒ `array`
Unpack given byte string according to specified format.

The `unpack()` function interpretes a byte string according to the given
format string and returns the resulting values. If the optional offset
argument is given, unpacking starts from this byte position within the input.
If not specified, the start offset defaults to `0`, the start of the given
input string.

Returns an array of unpacked values.

Raises a runtime exception if the format string is invalid or if an invalid
input string or offset value is given.

**Kind**: instance method of [`struct`](#module_struct)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| format | `string` |  | The format string. |
| input | `string` |  | The input string to unpack. |
| [offset] | `number` | `0` | The offset within the input string to start unpacking from. |

**Example**  
```ucode
// Unpack three consecutive unsigned int values in network byte order.
const numbers =
  unpack('!III', '\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03');
print(numbers, "\n"); // [ 1, 2, 3 ]
```

### struct.new(format) ⇒ [`instance`](#module_struct.instance)
Precompile format string.

The `new()` function precompiles the given format string argument and returns
a `struct` object instance useful for packing and unpacking multiple items
without having to recompute the internal format each time.

Returns an precompiled struct format instance.

Raises a runtime exception if the format string is invalid.

**Kind**: instance method of [`struct`](#module_struct)  

| Param | Type | Description |
| --- | --- | --- |
| format | `string` | The format string. |

**Example**  
```ucode
// Create a format of three consecutive unsigned int values in network byte order.
const fmt = struct.new('!III');
const buf = fmt.pack(1, 2, 3);  // "\x00\x00\x00\x01…"
print(fmt.unpack(buf), "\n");   // [ 1, 2, 3 ]
```

### struct.buffer([initialData]) ⇒ [`buffer`](#module_struct.buffer)
Creates a new struct buffer instance.

The `buffer()` function creates a new struct buffer object that can be used
for incremental packing and unpacking of binary data. If an initial data
string is provided, the buffer is initialized with this content.

Note that even when initial data is provided, the buffer position is always
set to zero. This design assumes that the primary intent when initializing
a buffer with data is to read (unpack) from the beginning. If you want to
append data to a pre-initialized buffer, you need to explicitly move the
position to the end, either by calling `end()` or by setting the position
manually with `pos()`.

Returns a new struct buffer instance.

**Kind**: instance method of [`struct`](#module_struct)  

| Param | Type | Description |
| --- | --- | --- |
| [initialData] | `string` | Optional initial data to populate the buffer with. |

**Example**  
```ucode
// Create an empty buffer
const emptyBuf = struct.buffer();

// Create a buffer with initial data
const dataBuf = struct.buffer("\x01\x02\x03\x04");

// Read from the beginning of the initialized buffer
const value = dataBuf.get('I');

// Append data to the initialized buffer
dataBuf.end().put('I', 5678);

// Alternative chained syntax for initializing and appending
const buf = struct.buffer("\x01\x02\x03\x04").end().put('I', 5678);
```

### struct.instance
**Kind**: static class of [`struct`](#module_struct)  
**See**: [new()](#module_struct+new)  

* [.instance](#module_struct.instance)
    * [.pack(...values)](#module_struct.instance+pack) ⇒ `string`
    * [.unpack(input, [offset])](#module_struct.instance+unpack) ⇒ `array`

#### instance.pack(...values) ⇒ `string`
Pack given values.

The `pack()` function creates a byte string containing the argument values
packed according to the given format instance.

Returns the packed string.

Raises a runtime exception if a given argument value does not match the
required type of the corresponding format string directive.

**Kind**: instance method of [`instance`](#module_struct.instance)  

| Param | Type | Description |
| --- | --- | --- |
| ...values | `\*` | Variable number of values to pack. |

**Example**  
```text
const fmt = struct.new(…);
const data = fmt.pack(…);
```

#### instance.unpack(input, [offset]) ⇒ `array`
Unpack given byte string.

The `unpack()` function interpretes a byte string according to the given
format instance and returns the resulting values. If the optional offset
argument is given, unpacking starts from this byte position within the input.
If not specified, the start offset defaults to `0`, the start of the given
input string.

Returns an array of unpacked values.

Raises a runtime exception if an invalid input string or offset value is
given.

**Kind**: instance method of [`instance`](#module_struct.instance)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| input | `string` |  | The input string to unpack. |
| [offset] | `number` | `0` | The offset within the input string to start unpacking from. |

**Example**  
```text
const fmt = struct.new(…);
const values = fmt.unpack(…);
```

### struct.buffer
**Kind**: static class of [`struct`](#module_struct)  
**See**: [buffer()](#module_struct+buffer)  

* [.buffer](#module_struct.buffer)
    * [.pos([position])](#module_struct.buffer+pos) ⇒ `number` \| [`buffer`](#module_struct.buffer)
    * [.length([length])](#module_struct.buffer+length) ⇒ `number` \| [`buffer`](#module_struct.buffer)
    * [.start()](#module_struct.buffer+start) ⇒ [`buffer`](#module_struct.buffer)
    * [.end()](#module_struct.buffer+end) ⇒ [`buffer`](#module_struct.buffer)
    * [.put(format, ...values)](#module_struct.buffer+put) ⇒ [`buffer`](#module_struct.buffer)
    * [.get(format)](#module_struct.buffer+get) ⇒ `\*`
    * [.get(format)](#module_struct.buffer+get) ⇒ `array`
    * [.slice([start], [end])](#module_struct.buffer+slice) ⇒ `string`
    * [.set([value], [start], [end])](#module_struct.buffer+set) ⇒ [`buffer`](#module_struct.buffer)
    * [.pull()](#module_struct.buffer+pull) ⇒ `string`

#### buffer.pos([position]) ⇒ `number` \| [`buffer`](#module_struct.buffer)
Get or set the current position in the buffer.

If called without arguments, returns the current position.
If called with a position argument, sets the current position to that value.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: `number` \| [`buffer`](#module_struct.buffer) - If called without arguments, returns the current position.
If called with a position argument, returns the buffer instance for chaining.  

| Param | Type | Description |
| --- | --- | --- |
| [position] | `number` | The position to set. If omitted, the current position is returned. |

**Example**  
```ucode
const currentPos = buf.pos();
buf.pos(10);  // Set position to 10
```

#### buffer.length([length]) ⇒ `number` \| [`buffer`](#module_struct.buffer)
Get or set the current buffer length.

If called without arguments, returns the current length of the buffer.
If called with a length argument, sets the buffer length to that value,
padding the data with trailing zero bytes or truncating it depending on
whether the updated length is larger or smaller than the current length
respectively.

In case the updated length is smaller than the current buffer offset, the
position is updated accordingly, so that it points to the new end of the
truncated buffer data.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: `number` \| [`buffer`](#module_struct.buffer) - If called without arguments, returns the current length.
If called with a length argument, returns the buffer instance for chaining.  

| Param | Type | Description |
| --- | --- | --- |
| [length] | `number` | The length to set. If omitted, the current length is returned. |

**Example**  
```ucode
const buf = struct.buffer("abc"); // Initialize buffer with three bytes
const currentLen = buf.length();  // Returns 3

buf.length(6);                    // Extend to 6 bytes
buf.slice();                      // Trailing null bytes: "abc\x00\x00\x00"

buf.length(2);                    // Truncate to 2 bytes
buf.slice();                      // Truncated data: "ab"
```

#### buffer.start() ⇒ [`buffer`](#module_struct.buffer)
Set the buffer position to the start (0).

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: [`buffer`](#module_struct.buffer) - The buffer instance.  
**Example**  
```ucode
buf.start();
```

#### buffer.end() ⇒ [`buffer`](#module_struct.buffer)
Set the buffer position to the end.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: [`buffer`](#module_struct.buffer) - The buffer instance.  
**Example**  
```ucode
buf.end();
```

#### buffer.put(format, ...values) ⇒ [`buffer`](#module_struct.buffer)
Pack data into the buffer at the current position.

The `put()` function packs the given values into the buffer according to
the specified format string, starting at the current buffer position.
The format string follows the same syntax as used in `struct.pack()`.

For a detailed explanation of the format string syntax, refer to the
["Format Strings" section](#module_struct) in the module
documentation.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: [`buffer`](#module_struct.buffer) - The buffer instance.  
**See**: [struct.pack()](#module_struct+pack)  

| Param | Type | Description |
| --- | --- | --- |
| format | `string` | The format string specifying how to pack the data. |
| ...values | `\*` | The values to pack into the buffer. |

**Example**  
```ucode
buf.put('II', 1234, 5678);
```

#### buffer.get(format) ⇒ `\*`
Unpack a single value from the buffer at the current position.

The `get()` function unpacks a single value from the buffer according to the
specified format string, starting at the current buffer position.
The format string follows the same syntax as used in `struct.unpack()`.

For a detailed explanation of the format string syntax, refer to the
["Format Strings" section](#module_struct) in the module documentation.

Alternatively, `get()` accepts a postive or negative integer as format, which
specifies the length of a string to unpack before or after the current
position. Negative values extract that many bytes before the current offset
while postive ones extracts that many bytes after.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: `\*` - The unpacked value.  
**See**: [struct.unpack()](#module_struct+unpack)  

| Param | Type | Description |
| --- | --- | --- |
| format | `string` \| `number` | The format string specifying how to unpack the data. |

**Example**  
```ucode
const val = buf.get('I');
const str = buf.get(5);    // equivalent to buf.get('5s')
const str = buf.get(-3);   // equivalent to buf.pos(buf.pos() - 3).get('3s')
```

#### buffer.get(format) ⇒ `array`
Unpack multiple values from the buffer at the current position.

The `read()` function unpacks multiple values from the buffer according to
the specified format string, starting at the current buffer position.
The format string follows the same syntax as used in `struct.unpack()`.

For a detailed explanation of the format string syntax, refer to the
["Format Strings" section](#module_struct) in the module documentation.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: `array` - An array containing the unpacked values.  
**See**: [struct.unpack()](#module_struct+unpack)  

| Param | Type | Description |
| --- | --- | --- |
| format | `string` | The format string specifying how to unpack the data. |

**Example**  
```ucode
const values = buf.get('II');
```

#### buffer.slice([start], [end]) ⇒ `string`
Extract a slice of the buffer content.

The `slice()` function returns a substring of the buffer content
between the specified start and end positions.

Both the start and end position values may be negative, in which case they're
relative to the end of the buffer, e.g. `slice(-3)` will extract the last
three bytes of data.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: `string` - A string containing the specified slice of the buffer content.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [start] | `number` | `0` | The starting position of the slice. |
| [end] | `number` | `buffer.length()` | The ending position of the slice (exclusive). |

**Example**  
```ucode
const slice = buf.slice(4, 8);
```

#### buffer.set([value], [start], [end]) ⇒ [`buffer`](#module_struct.buffer)
Set a slice of the buffer content to given byte value.

The `set()` function overwrites a substring of the buffer content with the
given byte value, similar to the C `memset()` function, between the specified
start and end positions.

Both the start and end position values may be negative, in which case they're
relative to the end of the buffer, e.g. `set(0, -2)` will overwrite the last
two bytes of data with `\x00`.

When the start or end positions are beyond the current buffer length, the
buffer is grown accordingly.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: [`buffer`](#module_struct.buffer) - The buffer instance.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [value] | `number` \| `string` | `0` | The byte value to use when overwriting buffer contents. When a string is given, the first character is used as value. |
| [start] | `number` | `0` | The position to start overwriting from. |
| [end] | `number` | `buffer.length()` | The position to end overwriting (exclusive). |

**Example**  
```ucode
const buf = struct.buffer("abcde");
buf.set("X", 2, 4).slice();  // Buffer content is now "abXXe"
buf.set().slice();           // Buffer content is now "\x00\x00\x00\x00\x00"
```

#### buffer.pull() ⇒ `string`
Extract and remove all content from the buffer.

The `pull()` function returns all content of the buffer as a string
and resets the buffer to an empty state.

**Kind**: instance method of [`buffer`](#module_struct.buffer)  
**Returns**: `string` - A string containing all the buffer content.  
**Example**  
```ucode
const allData = buf.pull();
```

---

# ucode module: uci

> **Live docs:** https://ucode.mein.io/module-uci.html

---

## OpenWrt UCI configuration

The `uci` module provides access to the native OpenWrt
[libuci](https://github.com/openwrt/uci) API for reading and
manipulating UCI configuration files.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { cursor } from 'uci';

  let ctx = cursor();
  let hostname = ctx.get_first('system', 'system', 'hostname');
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as uci from 'uci';

  let ctx = uci.cursor();
  let hostname = ctx.get_first('system', 'system', 'hostname');
  ```

Additionally, the uci module namespace may also be imported by invoking
the `ucode` interpreter with the `-luci` switch.

### uci.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`uci`](#module_uci)  
**Example**  
```ucode
// Trigger error
const ctx = cursor();
ctx.set("not_existing_config", "test", "1");

// Print error (should yield "Entry not found")
print(ctx.error(), "\n");
```

### uci.cursor([config_dir], [delta_dir], [config2_dir], Parser) ⇒ [`cursor`](#module_uci.cursor)
Instantiate uci cursor.

A uci cursor is a context for interacting with uci configuration files. It's
purpose is to cache and hold changes made to loaded configuration states
until those changes are written out to disk or discared.

Unsaved and uncommitted changes in a cursor instance are private and not
visible to other cursor instances instantiated by the same program or other
processes on the system.

Returns the instantiated cursor on success.

Returns `null` on error, e.g. if an invalid path argument was provided.

**Kind**: instance method of [`uci`](#module_uci)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [config_dir] | `string` | `"/etc/config"` | The directory to search for configuration files. It defaults to the well known uci configuration directory `/etc/config` but may be set to a different path for special purpose applications. |
| [delta_dir] | `string` | `"/tmp/.uci"` | The directory to save delta records in. It defaults to the well known `/tmp/.uci` path which is used as default by the uci command line tool. By changing this path to a different location, it is possible to isolate uncommitted application changes from the uci cli or other processes on the system. |
| [config2_dir] | `string` | `"/var/run/uci"` | The directory to keep override config files in. Files are in the same format as in config_dir, but can individually override ones from that directory. It defaults to the uci configuration directory `/var/run/uci` but may be set to a different path for special purpose applications, or even disabled by setting this parameter to an empty string. |
| Parser | [`ParserFlags`](#module_uci.cursor.ParserFlags) |  | flags to change. |

### uci.cursor
**Kind**: static class of [`uci`](#module_uci)  
**See**: [cursor()](#module_uci+cursor)  

* [.cursor](#module_uci.cursor)
    * _instance_
        * [.load(config)](#module_uci.cursor+load) ⇒ `boolean`
        * [.unload(config)](#module_uci.cursor+unload) ⇒ `boolean`
        * [.get(config, section, [option])](#module_uci.cursor+get) ⇒ `string` \| `Array.<string>`
        * [.get_all(config, [section])](#module_uci.cursor+get_all) ⇒ `Object.<string, module:uci.cursor.SectionObject>` \| [`SectionObject`](#module_uci.cursor.SectionObject)
        * [.get_first(config, type, [option])](#module_uci.cursor+get_first) ⇒ `string` \| `Array.<string>`
        * [.add(config, type)](#module_uci.cursor+add) ⇒ `string`
        * [.set(config, section, option_or_type, [value])](#module_uci.cursor+set) ⇒ `boolean`
        * [.delete(config, section, [option])](#module_uci.cursor+delete) ⇒ `boolean`
        * [.list_append(config, section, option, value)](#module_uci.cursor+list_append) ⇒ `boolean`
        * [.list_remove(config, section, option, value)](#module_uci.cursor+list_remove) ⇒ `boolean`
        * [.rename(config, section, option_or_name, [name])](#module_uci.cursor+rename) ⇒ `boolean`
        * [.reorder(config, section, index)](#module_uci.cursor+reorder) ⇒ `boolean`
        * [.save([config])](#module_uci.cursor+save) ⇒ `boolean`
        * [.commit([config])](#module_uci.cursor+commit) ⇒ `boolean`
        * [.revert([config])](#module_uci.cursor+revert) ⇒ `boolean`
        * [.changes([config])](#module_uci.cursor+changes) ⇒ `Object.<string, Array.<module:uci.cursor.ChangeRecord>>`
        * [.foreach(config, type, callback)](#module_uci.cursor+foreach) ⇒ `boolean`
        * [.configs()](#module_uci.cursor+configs) ⇒ `Array.<string>`
        * [.error()](#module_uci.cursor+error) ⇒ `string`
    * _static_
        * [.ParserFlags](#module_uci.cursor.ParserFlags) : `Object`
        * [.ChangeRecord](#module_uci.cursor.ChangeRecord) : `Array.<string>`
        * [.SectionObject](#module_uci.cursor.SectionObject) : `Object.<string, (boolean\|number\|string\|Array.<string>)>`
        * [.SectionCallback](#module_uci.cursor.SectionCallback) : `function`

#### cursor.load(config) ⇒ `boolean`
Explicitly reload configuration file.

Usually, any attempt to query or modify a value within a given configuration
will implicitly load the underlying file into memory. By invoking `load()`
explicitly, a potentially loaded stale configuration is discarded and
reloaded from the file system, ensuring that the latest state is reflected in
the cursor.

Returns `true` if the configuration was successfully loaded.

Returns `null` on error, e.g. if the requested configuration does not exist.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to load, e.g. `"system"` to load `/etc/config/system` into the cursor. |

#### cursor.unload(config) ⇒ `boolean`
Explicitly unload configuration file.

The `unload()` function forcibly discards a loaded configuration state from
the cursor so that the next attempt to read or modify that configuration
will load it anew from the file system.

Returns `true` if the configuration was successfully unloaded.

Returns `false` if the configuration was not loaded to begin with.

Returns `null` on error, e.g. if the requested configuration does not exist.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to unload. |

#### cursor.get(config, section, [option]) ⇒ `string` \| `Array.<string>`
Query a single option value or section type.

When invoked with three arguments, the function returns the value of the
given option, within the specified section of the given configuration.

When invoked with just a config and section argument, the function returns
the type of the specified section.

In either case, the given configuration is implicitly loaded into the cursor
if not already present.

Returns the configuration value or section type on success.

Returns `null` on error, e.g. if the requested configuration does not exist
or if an invalid argument was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to query, e.g. `"system"` to query values in `/etc/config/system`. |
| section | `string` | The name of the section to query within the configuration. |
| [option] | `string` | The name of the option to query within the section. If omitted, the type of the section is returned instead. |

**Example**  
```text
const ctx = cursor(…);

// Query an option, extended section notation is supported
ctx.get('system', '@system[0]', 'hostname');

// Query a section type (should yield 'interface')
ctx.get('network', 'lan');
```

#### cursor.get\_all(config, [section]) ⇒ `Object.<string, module:uci.cursor.SectionObject>` \| [`SectionObject`](#module_uci.cursor.SectionObject)
Query a complete section or configuration.

When invoked with two arguments, the function returns all values of the
specified section within the given configuration as dictionary.

When invoked with just a config argument, the function returns a nested
dictionary of all sections present within the given configuration.

In either case, the given configuration is implicitly loaded into the cursor
if not already present.

Returns the section or configuration dictionary on success.

Returns `null` on error, e.g. if the requested configuration does not exist
or if an invalid argument was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to query, e.g. `"system"` to query values in `/etc/config/system`. |
| [section] | `string` | The name of the section to query within the configuration. If omitted a nested dictionary containing all section values is returned. |

**Example**  
```text
const ctx = cursor(…);

// Query all lan interface details
ctx.get_all('network', 'lan');

// Dump the entire dhcp configuration
ctx.get_all('dhcp');
```

#### cursor.get\_first(config, type, [option]) ⇒ `string` \| `Array.<string>`
Query option value or name of first section of given type.

When invoked with three arguments, the function returns the value of the
given option within the first found section of the specified type in the
given configuration.

When invoked with just a config and section type argument, the function
returns the name of the first found section of the given type.

In either case, the given configuration is implicitly loaded into the cursor
if not already present.

Returns the configuration value or section name on success.

Returns `null` on error, e.g. if the requested configuration does not exist
or if an invalid argument was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to query, e.g. `"system"` to query values in `/etc/config/system`. |
| type | `string` | The section type to find the first section for within the configuration. |
| [option] | `string` | The name of the option to query within the section. If omitted, the name of the section is returned instead. |

**Example**  
```text
const ctx = cursor(…);

// Query hostname in first anonymous "system" section of /etc/config/system
ctx.get_first('system', 'system', 'hostname');

// Figure out name of first network interface section (usually "loopback")
ctx.get_first('network', 'interface');
```

#### cursor.add(config, type) ⇒ `string`
Add anonymous section to given configuration.

Adds a new anonymous (unnamed) section of the specified type to the given
configuration. In order to add a named section, the three argument form of
`set()` should be used instead.

In contrast to other query functions, `add()` will not implicitly load the
configuration into the cursor. The configuration either needs to be loaded
explicitly through `load()` beforehand, or implicitly by querying it through
one of the `get()`, `get_all()`, `get_first()` or `foreach()` functions.

Returns the autogenerated, ephemeral name of the added unnamed section
on success.

Returns `null` on error, e.g. if the targeted configuration was not loaded or
if an invalid section type value was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to add the section to, e.g. `"system"` to modify `/etc/config/system`. |
| type | `string` | The type value to use for the added section. |

**Example**  
```text
const ctx = cursor(…);

// Load firewall configuration
ctx.load('firewall');

// Add unnamed `config rule` section
const sid = ctx.add('firewall', 'rule');

// Set values on the newly added section
ctx.set('firewall', sid, 'name', 'A test');
ctx.set('firewall', sid, 'target', 'ACCEPT');
…
```

#### cursor.set(config, section, option_or_type, [value]) ⇒ `boolean`
Set option value or add named section in given configuration.

When invoked with four arguments, the function sets the value of the given
option within the specified section of the given configuration to the
provided value. A value of `""` (empty string) can be used to delete an
existing option.

When invoked with three arguments, the function adds a new named section to
the given configuration, using the specified type.

In either case, the given configuration is implicitly loaded into the cursor
if not already present.

Returns the `true` if the named section was added or the specified option was
set.

Returns `null` on error, e.g. if the targeted configuration was not found or
if an invalid value was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to set values in, e.g. `"system"` to modify `/etc/config/system`. |
| section | `string` | The section name to create or set a value in. |
| option_or_type | `string` | The option name to set within the section or, when the subsequent value argument is omitted, the type of the section to create within the configuration. |
| [value] | `Array.<(string\|boolean\|number)>` \| `string` \| `boolean` \| `number` | The option value to set. |

**Example**  
```text
const ctx = cursor(…);

// Add named `config interface guest` section
ctx.set('network', 'guest', 'interface');

// Set values on the newly added section
ctx.set('network', 'guest', 'proto', 'static');
ctx.set('network', 'guest', 'ipaddr', '10.0.0.1/24');
ctx.set('network', 'guest', 'dns', ['8.8.4.4', '8.8.8.8']);
…

// Delete 'disabled' option in first wifi-iface section
ctx.set('wireless', '@wifi-iface[0]', 'disabled', '');
```

#### cursor.delete(config, section, [option]) ⇒ `boolean`
Delete an option or section from given configuration.

When invoked with three arguments, the function deletes the given option
within the specified section of the given configuration.

When invoked with two arguments, the function deletes the entire specified
section within the given configuration.

In either case, the given configuration is implicitly loaded into the cursor
if not already present.

Returns the `true` if specified option or section has been deleted.

Returns `null` on error, e.g. if the targeted configuration was not found or
if an invalid value was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to delete values in, e.g. `"system"` to modify `/etc/config/system`. |
| section | `string` | The section name to remove the specified option in or, when the subsequent argument is omitted, the section to remove entirely. |
| [option] | `string` | The option name to remove within the section. |

**Example**  
```text
const ctx = cursor(…);

// Delete 'disabled' option in first wifi-iface section
ctx.delete('wireless', '@wifi-iface[0]', 'disabled');

// Delete 'wan' interface
ctx.delete('network', 'lan');

// Delete last firewall rule
ctx.delete('firewall', '@rule[-1]');
```

#### cursor.list\_append(config, section, option, value) ⇒ `boolean`
Add an item to a list option in given configuration.

Adds a single value to an existing list option within the specified section
of the given configuration. The configuration is implicitly loaded into the
cursor if not already present.

The new value is appended to the end of the list, maintaining the existing order.
No attempt is made to check for or remove duplicate values.

Returns `true` if the item was successfully added to the list.

Returns `null` on error, e.g. if the targeted option was not found or
if an invalid value was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to modify, e.g. `"firewall"` to modify `/etc/config/firewall`. |
| section | `string` | The section name containing the list option to modify. |
| option | `string` | The list option name to add a value to. |
| value | `string` \| `boolean` \| `number` | The value to add to the list option. |

**Example**  
```text
const ctx = cursor(…);

// Add '192.168.1.1' to the 'dns' list in the 'lan' interface
ctx.add_list('network', 'lan', 'dns', '192.168.1.1');

// Add a port to the first redirect section
ctx.add_list('firewall', '@redirect[0]', 'src_dport', '8080');
```

#### cursor.list\_remove(config, section, option, value) ⇒ `boolean`
Remove an item from a list option in given configuration.

Removes a single value from an existing list option within the specified section
of the given configuration. The configuration is implicitly loaded into the
cursor if not already present.

If the specified value appears multiple times in the list, all matching occurrences
will be removed.

Returns `true` if the item was successfully removed from the list.

Returns `null` on error, e.g. if the targeted option was not foundor if an
invalid value was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to modify, e.g. `"firewall"` to modify `/etc/config/firewall`. |
| section | `string` | The section name containing the list option to modify. |
| option | `string` | The list option name to remove a value from. |
| value | `string` \| `boolean` \| `number` | The value to remove from the list option. |

**Example**  
```text
const ctx = cursor(…);

// Remove '8.8.8.8' from the 'dns' list in the 'lan' interface
ctx.delete_list('network', 'lan', 'dns', '8.8.8.8');

// Remove a port from the first redirect section
ctx.delete_list('firewall', '@redirect[0]', 'src_dport', '8080');
```

#### cursor.rename(config, section, option_or_name, [name]) ⇒ `boolean`
Rename an option or section in given configuration.

When invoked with four arguments, the function renames the given option
within the specified section of the given configuration to the provided
value.

When invoked with three arguments, the function renames the entire specified
section to the provided value.

In either case, the given configuration is implicitly loaded into the cursor
if not already present.

Returns the `true` if specified option or section has been renamed.

Returns `null` on error, e.g. if the targeted configuration was not found or
if an invalid value was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to rename values in, e.g. `"system"` to modify `/etc/config/system`. |
| section | `string` | The section name to rename or to rename an option in. |
| option_or_name | `string` | The option name to rename within the section or, when the subsequent name argument is omitted, the new name of the renamed section within the configuration. |
| [name] | `string` | The new name of the option to rename. |

**Example**  
```text
const ctx = cursor(…);

// Assign explicit name to last anonymous firewall rule section
ctx.rename('firewall', '@rule[-1]', 'my_block_rule');

// Rename 'server' to 'orig_server_list' in ntp section of system config
ctx.rename('system', 'ntp', 'server', 'orig_server_list');

// Rename 'wan' interface to 'external'
ctx.rename('network', 'wan', 'external');
```

#### cursor.reorder(config, section, index) ⇒ `boolean`
Reorder sections in given configuration.

The `reorder()` function moves a single section by repositioning it to the
given index within the configurations section list.

The given configuration is implicitly loaded into the cursor if not already
present.

Returns the `true` if specified section has been moved.

Returns `null` on error, e.g. if the targeted configuration was not found or
if an invalid value was passed.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The name of the configuration file to move the section in, e.g. `"system"` to modify `/etc/config/system`. |
| section | `string` | The section name to move. |
| index | `number` | The target index to move the section to, starting from `0`. |

**Example**  
```text
const ctx = cursor(…);

// Query whole firewall config and reorder resulting dict by type and name
const type_order = ['defaults', 'zone', 'forwarding', 'redirect', 'rule'];
const values = ctx.get_all('firewall');

sort(values, (k1, k2, s1, s2) => {
    // Get weight from type_order array
    let w1 = index(type_order, s1['.type']);
    let w2 = index(type_order, s2['.type']);

    // For unknown type orders, use type value itself as weight
    if (w1 == -1) w1 = s1['.type'];
    if (w2 == -1) w2 = s2['.type'];

    // Get name from name option, fallback to section name
    let n1 = s1.name ?? k1;
    let n2 = s2.name ?? k2;

    // Order by weight
    if (w1 < w2) return -1;
    if (w1 > w2) return 1;

    // For same weight order by name
    if (n1 < n2) return -1;
    if (n1 > n2) return 1;

    return 0;
});

// Sequentially reorder sorted sections in firewall configuration
let position = 0;

for (let sid in values)
  ctx.reorder('firewall', sid, position++);
```

#### cursor.save([config]) ⇒ `boolean`
Save accumulated cursor changes to delta directory.

The `save()` function writes consolidated changes made to in-memory copies of
loaded configuration files to the uci delta directory which effectively makes
them available to other processes using the same delta directory path as well
as the `uci changes` cli command when using the default delta directory.

Note that uci deltas are overlayed over the actual configuration file values
so they're reflected by `get()`, `foreach()` etc. even if the underlying
configuration files are not actually changed (yet). The delta records may be
either permanently merged into the configuration by invoking `commit()` or
reverted through `revert()` in order to restore the current state of the
underlying configuration file.

When the optional "config" parameter is omitted, delta records for all
currently loaded configuration files are written.

In case that neither sharing changes with other processes nor any revert
functionality is required, changes may be committed directly using `commit()`
instead, bypassing any delta record creation.

Returns the `true` if operation completed successfully.

Returns `null` on error, e.g. if the requested configuration was not loaded
or when a file system error occurred.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  
**See**

- [commit()](#module_uci.cursor+commit)
- [revert()](#module_uci.cursor+revert)

| Param | Type | Description |
| --- | --- | --- |
| [config] | `string` | The name of the configuration file to save delta records for, e.g. `"system"` to store changes for `/etc/config/system`. |

**Example**  
```text
const ctx = cursor(…);

ctx.set('wireless', '@wifi-iface[0]', 'disabled', '1');
ctx.save('wireless');
```

#### cursor.commit([config]) ⇒ `boolean`
Update configuration files with accumulated cursor changes.

The `commit()` function merges changes made to in-memory copies of loaded
configuration files as well as existing delta records in the cursors
configured delta directory and writes them back into the underlying
configuration files, persistently committing changes to the file system.

When the optional "config" parameter is omitted, all currently loaded
configuration files with either present delta records or yet unsaved
cursor changes are updated.

Returns the `true` if operation completed successfully.

Returns `null` on error, e.g. if the requested configuration was not loaded
or when a file system error occurred.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| [config] | `string` | The name of the configuration file to commit, e.g. `"system"` to update the `/etc/config/system` file. |

**Example**  
```text
const ctx = cursor(…);

ctx.set('system', '@system[0]', 'hostname', 'example.org');
ctx.commit('system');
```

#### cursor.revert([config]) ⇒ `boolean`
Revert accumulated cursor changes and associated delta records.

The `revert()` function discards any changes made to in-memory copies of
loaded configuration files and discards any related existing delta records in
the  cursors configured delta directory.

When the optional "config" parameter is omitted, all currently loaded
configuration files with either present delta records or yet unsaved
cursor changes are reverted.

Returns the `true` if operation completed successfully.

Returns `null` on error, e.g. if the requested configuration was not loaded
or when a file system error occurred.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  
**See**: [save()](#module_uci.cursor+save)  

| Param | Type | Description |
| --- | --- | --- |
| [config] | `string` | The name of the configuration file to revert, e.g. `"system"` to discard any changes for the `/etc/config/system` file. |

**Example**  
```text
const ctx = cursor(…);

ctx.set('system', '@system[0]', 'hostname', 'example.org');
ctx.revert('system');
```

#### cursor.changes([config]) ⇒ `Object.<string, Array.<module:uci.cursor.ChangeRecord>>`
Enumerate pending changes.

The `changes()` function returns a list of change records for currently
loaded configuration files, originating both from the cursors associated
delta directory and yet unsaved cursor changes.

When the optional "config" parameter is specified, the requested
configuration is implicitly loaded if it is not already loaded into the
cursor.

Returns a dictionary of change record arrays, keyed by configuration name.

Returns `null` on error, e.g. if the requested configuration could not be
loaded.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| [config] | `string` | The name of the configuration file to enumerate changes for, e.g. `"system"` to query pending changes for the `/etc/config/system` file. |

**Example**  
```text
const ctx = cursor(…);

// Enumerate changes for all currently loaded configurations
const deltas = ctx.changes();

// Explicitly load and enumerate changes for the "system" configuration
const deltas = ctx.changes('system');
```

#### cursor.foreach(config, type, callback) ⇒ `boolean`
Iterate configuration sections.

The `foreach()` function iterates all sections of the given configuration,
optionally filtered by type, and invokes the given callback function for
each encountered section.

When the optional "type" parameter is specified, the callback is only invoked
for sections of the given type, otherwise it is invoked for all sections.

The requested configuration is implicitly loaded into the cursor.

Returns `true` if the callback was executed successfully at least once.

Returns `false` if the callback was never invoked, e.g. when the
configuration is empty or contains no sections of the given type.

Returns `null` on error, e.g. when an invalid callback was passed or the
requested configuration not found.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| config | `string` | The configuration to iterate sections for, e.g. `"system"` to read the `/etc/config/system` file. |
| type | `string` | Invoke the callback only for sections of the specified type. |
| callback | [`SectionCallback`](#module_uci.cursor.SectionCallback) | The callback to invoke for each section, will receive a section dictionary as sole argument. |

**Example**  
```text
const ctx = cursor(…);

// Iterate all network interfaces
ctx.foreach('network', 'interface',
	   section => print(`Have interface ${section[".name"]}\n`));
```

#### cursor.configs() ⇒ `Array.<string>`
Enumerate existing configurations.

The `configs()` function yields an array of configuration files present in
the cursors associated configuration directory, `/etc/config/` by default.

Returns an array of configuration names on success.

Returns `null` on error, e.g. due to filesystem errors.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  
**Example**  
```text
const ctx = cursor(…);

// Enumerate all present configuration file names
const configurations = ctx.configs();
```

#### cursor.error() ⇒ `string`
Query error information.

Returns a string containing a description of the last occurred error or
`null` if there is no error information.

**Kind**: instance method of [`cursor`](#module_uci.cursor)  
**Example**  
```ucode
// Trigger error
const ctx = cursor();
ctx.set("not_existing_config", "test", "1");

// Print error (should yield "Entry not found")
print(ctx.error(), "\n");
```

#### cursor.ParserFlags : `Object`
**Kind**: static typedef of [`cursor`](#module_uci.cursor)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| strict | `boolean` | Strict parsing mode (enabled by default). Aborts parsing when encountering a parser error. |
| print_errors | `boolean` | Print parser errors to stderr. |

#### cursor.ChangeRecord : `Array.<string>`
A uci change record is a plain array containing the change operation name as
first element, the affected section ID as second argument and an optional
third and fourth argument whose meanings depend on the operation.

**Kind**: static typedef of [`cursor`](#module_uci.cursor)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| 0 | `string` | The operation name - may be one of `add`, `set`, `remove`, `order`, `list-add`, `list-del` or `rename`. |
| 1 | `string` | The section ID targeted by the operation. |
| 2 | `string` | The meaning of the third element depends on the operation. - For `add` it is type of the section that has been added - For `set` it either is the option name if a fourth element exists, or the   type of a named section which has been added when the change entry only   contains three elements. - For `remove` it contains the name of the option that has been removed. - For `order` it specifies the new sort index of the section. - For `list-add` it contains the name of the list option a new value has been   added to. - For `list-del` it contains the name of the list option a value has been   removed from. - For `rename` it contains the name of the option that has been renamed if a   fourth element exists, else it contains the new name a section has been   renamed to if the change entry only contains three elements. |
| 4 | `string` | The meaning of the fourth element depends on the operation. - For `set` it is the value an option has been set to. - For `list-add` it is the new value that has been added to a list option. - For `rename` it is the new name of an option that has been renamed. |

#### cursor.SectionObject : `Object.<string, (boolean\|number\|string\|Array.<string>)>`
A section object represents the options and their corresponding values
enclosed within a configuration section, as well as some additional meta data
such as sort indexes and internal ID.

Any internal metadata fields are prefixed with a dot which isn't an allowed
character for normal option names.

**Kind**: static typedef of [`cursor`](#module_uci.cursor)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| .anonymous | `boolean` | The `.anonymous` property specifies whether the configuration is anonymous (`true`) or named (`false`). |
| .index | `number` | The `.index` property specifies the sort order of the section. |
| .name | `string` | The `.name` property holds the name of the section object. It may be either an anonymous ID in the form `cfgXXXXXX` with `X` being a hexadecimal digit or a string holding the name of the section. |
| .type | `string` | The `.type` property contains the type of the corresponding uci section. |
| * | `string` \| `Array.<string>` | A section object may contain an arbitrary number of further properties representing the uci option enclosed in the section. All option property names will be in the form `[A-Za-z0-9_]+` and either contain a string value or an array of strings, in case the underlying option is an UCI list. |

#### cursor.SectionCallback : `function`
The sections callback is invoked for each section found within the given
configuration and receives the section object and its associated name as
arguments.

**Kind**: static typedef of [`cursor`](#module_uci.cursor)  

| Param | Type | Description |
| --- | --- | --- |
| section | [`SectionObject`](#module_uci.cursor.SectionObject) | The section object. |

---

# ucode module: uloop

> **Live docs:** https://ucode.mein.io/module-uloop.html

---

## OpenWrt uloop event loop

The `uloop` binding provides functions for integrating with the OpenWrt
[uloop library](https://github.com/openwrt/libubox/blob/master/uloop.h).

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```text
  import { init, handle, timer, interval, process, signal, task, run } from 'uloop';

  init();

  handle(…);
  timer(…);
  interval(…);
  process(…);
  signal(…);
  task(…);

  run();
  ```

Alternatively, the module namespace can be imported using a wildcard import
statement:

  ```text
  import * as uloop from 'uloop';

  uloop.init();

  uloop.handle(…);
  uloop.timer(…);
  uloop.interval(…);
  uloop.process(…);
  uloop.signal(…);
  uloop.task(…);

  uloop.run();
  ```

Additionally, the uloop binding namespace may also be imported by invoking
the `ucode` interpreter with the `-luloop` switch.

### uloop.error() ⇒ `string`
Retrieves the last error message.

This function retrieves the last error message generated by the uloop event loop.
If no error occurred, it returns `null`.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: `string` - Returns the last error message as a string, or `null` if no error occurred.  
**Example**  
```ucode
// Retrieve the last error message
const errorMessage = uloop.error();

if (errorMessage)
    printf(`Error message: ${errorMessage}\n`);
else
    printf("No error occurred\n");
```

### uloop.init() ⇒ `boolean`
Initializes the uloop event loop.

This function initializes the uloop event loop, allowing subsequent
usage of uloop functionalities. It takes no arguments.

Returns `true` on success.
Returns `null` if an error occurred during initialization.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: `boolean` - Returns `true` on success, `null` on error.  
**Example**  
```ucode
// Initialize the uloop event loop
const success = uloop.init();

if (success)
    printf("uloop event loop initialized successfully\n");
else
    die(`Initialization failure: ${uloop.error()}\n`);
```

### uloop.run([timeout]) ⇒ `number`
Runs the uloop event loop.

This function starts running the uloop event loop, allowing it to handle
scheduled events and callbacks. If a timeout value is provided and is
non-negative, the event loop will run for that amount of milliseconds
before returning. If the timeout is omitted or negative, the event loop
runs indefinitely until explicitly stopped.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: `number` - Returns a signal number or 0 on success, `null` on error.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [timeout] | `number` | `-1` | Optional. The timeout value in milliseconds for running the event loop. Defaults to -1, indicating an indefinite run. |

**Example**  
```ucode
// Run the uloop event loop indefinitely
const success = uloop.run();
if (rc == null)
    die(`Error occurred during uloop execution: ${uloop.error()}\n`);
else if (rc != 0)
    printf("uloop event loop was interrupted by a signal: %d\n", rc);

// Run the uloop event loop for 1000 milliseconds
const success = uloop.run(1000);
if (rc == null)
    die(`Error occurred during uloop execution: ${uloop.error()}\n`);
else if (rc != 0)
    printf("uloop event loop was interrupted by a signal: %d\n", rc);
```

### uloop.cancelling() ⇒ `boolean`
Checks if the uloop event loop is currently shutting down.

This function checks whether the uloop event loop is currently in the process
of shutting down.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: `boolean` - Returns `true` if uloop is currently shutting down, `false` otherwise.  
**Example**  
```ucode
// Check if the uloop event loop is shutting down
const shuttingDown = uloop.cancelling();
if (shuttingDown)
    printf("uloop event loop is currently shutting down\n");
else
    printf("uloop event loop is not shutting down\n");
```

### uloop.running() ⇒ `boolean`
Checks if the uloop event loop is currently running.

This function checks whether the uloop event loop is currently started
and running.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: `boolean` - Returns `true` if the event loop is currently running, `false` otherwise.  
**Example**  
```ucode
// Check if the uloop event loop is running
const isRunning = uloop.running();
if (isRunning)
    printf("uloop event loop is currently running\n");
else
    printf("uloop event loop is not running\n");
```

### uloop.end() ⇒ `void`
Halts the uloop event loop.

This function halts the uloop event loop, stopping its execution and
preventing further processing of scheduled events and callbacks.

Expired timeouts and already queued event callbacks are still run to
completion.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: `void` - This function does not return any value.  
**Example**  
```ucode
// Halt the uloop event loop
uloop.end();
```

### uloop.done() ⇒ `void`
Stops the uloop event loop and cancels pending timeouts and events.

This function immediately stops the uloop event loop, cancels all pending
timeouts and events, unregisters all handles, and deallocates associated
resources.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: `void` - This function does not return any value.  
**Example**  
```ucode
// Stop the uloop event loop and clean up resources
uloop.done();
```

### uloop.timer([timeout], callback) ⇒ [`timer`](#module_uloop.timer)
Creates a timer instance for scheduling callbacks.

This function creates a timer instance for scheduling callbacks to be
executed after a specified timeout duration. It takes an optional timeout
parameter, which defaults to -1, indicating that the timer is initially not
armed and can be enabled later by invoking the `.set(timeout)` method on the
instance.

A callback function must be provided to be executed when the timer expires.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: [`timer`](#module_uloop.timer) - Returns a timer instance for scheduling callbacks.
Returns `null` when the timeout or callback arguments are invalid.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [timeout] | `number` | `-1` | Optional. The timeout duration in milliseconds. Defaults to -1, indicating the timer is not initially armed. |
| callback | `function` |  | The callback function to be executed when the timer expires. |

**Example**  
```ucode
// Create a timer with a callback to be executed after 1000 milliseconds
const myTimer = uloop.timer(1000, () => {
    printf("Timer expired!\n");
});

// Later enable the timer with a timeout of 500 milliseconds
myTimer.set(500);
```

### uloop.handle(handle, callback, events) ⇒ [`handle`](#module_uloop.handle)
Creates a handle instance for monitoring file descriptor events.

This function creates a handle instance for monitoring events on a file
descriptor, file, or socket. It takes the file or socket handle, a callback
function to be invoked when the specified IO events occur, and bitwise OR-ed
flags of IO events (`ULOOP_READ`, `ULOOP_WRITE`) that the callback should be
invoked for.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: [`handle`](#module_uloop.handle) - Returns a handle instance for monitoring file descriptor events.
Returns `null` when the handle, callback or signal arguments are invalid.  

| Param | Type | Description |
| --- | --- | --- |
| handle | `number` \| `module:fs.file` \| `module:fs.proc` \| `module:socket.socket` \| `module:io.handle` | The file handle (descriptor number, file or socket instance). |
| callback | `function` | The callback function to be invoked when the specified IO events occur. |
| events | `number` | Bitwise OR-ed flags of IO events (`ULOOP_READ`, `ULOOP_WRITE`) that the callback should be invoked for. |

**Example**  
```ucode
// Create a handle for monitoring read events on file descriptor 3
const myHandle = uloop.handle(3, (events) => {
    if (events & ULOOP_READ)
        printf("Read event occurred!\n");
}, uloop.ULOOP_READ);

// Check socket for writability
const sock = socket.connect("example.org", 80);
uloop.handle(sock, (events) => {
    sock.send("GET / HTTP/1.0\r\n\r\n");
}, uloop.ULOOP_WRITE)
```

### uloop.process(executable, [args], [env], callback) ⇒ [`process`](#module_uloop.process)
Creates a process instance for executing external programs.

This function creates a process instance for executing external programs.
It takes the executable path string, an optional string array as the argument
vector, an optional dictionary describing environment variables, and a
callback function to be invoked when the invoked process ends.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: [`process`](#module_uloop.process) - Returns a process instance for executing external programs.
Returns `null` on error, e.g. due to `exec()` failure or invalid arguments.  

| Param | Type | Description |
| --- | --- | --- |
| executable | `string` | The path to the executable program. |
| [args] | `Array.<string>` | Optional. An array of strings representing the arguments passed to the executable. |
| [env] | `Object.<string, \*>` | Optional. A dictionary describing environment variables for the process. |
| callback | `function` | The callback function to be invoked when the invoked process ends. |

**Example**  
```ucode
// Create a process instance for executing 'ls' command
const myProcess = uloop.process("/bin/ls", ["-l", "/tmp"], null, (code) => {
    printf(`Process exited with code ${code}\n`);
});
```

### uloop.task(taskFunction, [outputCallback], [inputCallback]) ⇒ [`task`](#module_uloop.task)
Creates a task instance for executing background tasks.

This function creates a task instance for executing background tasks.
It takes the task function to be invoked as a background process,
an optional output callback function to be invoked when output is received
from the task, and an optional input callback function to be invoked
when input is required by the task.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: [`task`](#module_uloop.task) - Returns a task instance for executing background tasks.
Returns `null` on error, e.g. due to fork failure or invalid arguments.  

| Param | Type | Description |
| --- | --- | --- |
| taskFunction | `function` | The task function to be invoked as a background process. |
| [outputCallback] | `function` | Optional. The output callback function to be invoked when output is received from the task. It is invoked with the output data as the argument. |
| [inputCallback] | `function` | Optional. The input callback function to be invoked when input is required by the task. It is invoked with a function to send input to the task as the argument. |

**Example**  
```ucode
// Create a task instance for executing a background task
const myTask = uloop.task(
    (pipe) => {
        // Task logic
        pipe.send("Hello from the task\n");
        const input = pipe.receive();
        printf(`Received input from main thread: ${input}\n`);
    },
    (output) => {
        // Output callback, invoked when task function calls pipe.send()
        printf(`Received output from task: ${output}\n`);
    },
    () => {
        // Input callback, invoked when task function calls pipe.receive()
        return "Input from main thread\n";
    }
);
```

### uloop.interval([timeout], callback) ⇒ [`interval`](#module_uloop.interval)
Creates an interval instance for scheduling repeated callbacks.

This function creates an interval instance for scheduling repeated callbacks
to be executed at regular intervals. It takes an optional timeout parameter,
which defaults to -1, indicating that the interval is initially not armed
and can be armed later with the `.set(timeout)` method. A callback function
must be provided to be executed when the interval expires.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: [`interval`](#module_uloop.interval) - Returns an interval instance for scheduling repeated callbacks.
Returns `null` when the timeout or callback arguments are invalid.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [timeout] | `number` | `-1` | Optional. The interval duration in milliseconds. Defaults to -1, indicating the interval is not initially armed. |
| callback | `function` |  | The callback function to be executed when the interval expires. |

**Example**  
```ucode
// Create an interval with a callback to be executed every 1000 milliseconds
const myInterval = uloop.interval(1000, () => {
    printf("Interval callback executed!\n");
});

// Later arm the interval to start executing the callback every 500 milliseconds
myInterval.set(500);
```

### uloop.signal(signal, callback) ⇒ [`signal`](#module_uloop.signal)
Creates a signal instance for handling Unix signals.

This function creates a signal instance for handling Unix signals.
It takes the signal name string (with or without "SIG" prefix) or signal
number, and a callback function to be invoked when the specified Unix signal
is caught.

**Kind**: instance method of [`uloop`](#module_uloop)  
**Returns**: [`signal`](#module_uloop.signal) - Returns a signal instance representing the installed signal handler.
Returns `null` when the signal or callback arguments are invalid.  

| Param | Type | Description |
| --- | --- | --- |
| signal | `string` \| `number` | The signal name string (with or without "SIG" prefix) or signal number. |
| callback | `function` | The callback function to be invoked when the specified Unix signal is caught. |

**Example**  
```ucode
// Create a signal instance for handling SIGINT
const mySignal = uloop.signal("SIGINT", () => {
    printf("SIGINT caught!\n");
});
```

### uloop.timer
**Kind**: static class of [`uloop`](#module_uloop)  
**See**: [timer()](#module_uloop+timer)  

* [.timer](#module_uloop.timer)
    * [.set([timeout])](#module_uloop.timer+set) ⇒ `boolean`
    * [.remaining()](#module_uloop.timer+remaining) ⇒ `number`
    * [.cancel()](#module_uloop.timer+cancel) ⇒ `boolean`

#### timer.set([timeout]) ⇒ `boolean`
Rearms the uloop timer with the specified timeout.

This method rearms the uloop timer with the specified timeout value,
allowing it to trigger after the specified amount of time. If no timeout
value is provided or if the provided value is negative, the timer remains
disabled until rearmed with a positive timeout value.

**Kind**: instance method of [`timer`](#module_uloop.timer)  
**Returns**: `boolean` - Returns `true` on success, `null` on error, such as an invalid timeout argument.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [timeout] | `number` | `-1` | Optional. The timeout value in milliseconds until the timer expires. Defaults to -1, which disables the timer until rearmed with a positive timeout. |

**Example**  
```text
const timeout = uloop.timer(…);

// Rearm the uloop timer with a timeout of 1000 milliseconds
timeout.set(1000);

// Disable the uloop timer
timeout.set();
```

#### timer.remaining() ⇒ `number`
Returns the number of milliseconds until the uloop timer expires.

This method returns the remaining time until the uloop timer expires. If
the timer is not armed (i.e., disabled), it returns -1.

**Kind**: instance method of [`timer`](#module_uloop.timer)  
**Returns**: `number` - The number of milliseconds until the timer expires, or -1 if the timer is not armed.  
**Example**  
```ucode
// Get the remaining time until the uloop timer expires (~500ms)
const remainingTime = timer.remaining();
if (remainingTime !== -1)
    printf("Time remaining until timer expires: %d ms\n", remainingTime);
else
    printf("Timer is not armed\n");
```

#### timer.cancel() ⇒ `boolean`
Cancels the uloop timer, disarming it and removing it from the event loop.

This method destroys the uloop timer and releases its associated resources.

**Kind**: instance method of [`timer`](#module_uloop.timer)  
**Returns**: `boolean` - Returns `true` on success.  
**Example**  
```ucode
// Cancel the uloop timer
timer.cancel();
```

### uloop.handle
**Kind**: static class of [`uloop`](#module_uloop)  
**See**: [handle()](#module_uloop+handle)  

* [.handle](#module_uloop.handle)
    * [.fileno()](#module_uloop.handle+fileno) ⇒ `number`
    * [.handle()](#module_uloop.handle+handle) ⇒ `module:fs.file` \| `module:fs.proc` \| `module:socket.socket`
    * [.delete()](#module_uloop.handle+delete) ⇒ `void`

#### handle.fileno() ⇒ `number`
Returns the file descriptor number.

This method returns the file descriptor number associated with the underlying
handle, which might refer to a socket or file instance.

**Kind**: instance method of [`handle`](#module_uloop.handle)  
**Returns**: `number` - The file descriptor number associated with the handle.  
**Example**  
```ucode
// Get the file descriptor number associated with the uloop handle
const fd = handle.fileno();
printf("File descriptor number: %d\n", fd);
```

#### handle.handle() ⇒ `module:fs.file` \| `module:fs.proc` \| `module:socket.socket`
Returns the underlying file or socket instance.

This method returns the underlying file or socket instance associated with
the uloop handle.

**Kind**: instance method of [`handle`](#module_uloop.handle)  
**Returns**: `module:fs.file` \| `module:fs.proc` \| `module:socket.socket` - The underlying file or socket instance associated with the handle.  
**Example**  
```ucode
// Get the associated file or socket instance
const fileOrSocket = handle.handle();
printf("Handle: %s\n", fileOrSocket); // e.g. <socket 0x5> or <fs.proc …>
```

#### handle.delete() ⇒ `void`
Unregisters the uloop handle.

This method unregisters the uloop handle from the uloop event loop and frees
any associated resources. After calling this method, the handle instance
should no longer be used.

**Kind**: instance method of [`handle`](#module_uloop.handle)  
**Returns**: `void` - This function does not return a value.  
**Example**  
```ucode
// Unregister the uloop handle and free associated resources
handle.delete();
printf("Handle deleted successfully\n");
```

### uloop.process
**Kind**: static class of [`uloop`](#module_uloop)  
**See**: [process()](#module_uloop+process)  

* [.process](#module_uloop.process)
    * [.pid()](#module_uloop.process+pid) ⇒ `number`
    * [.delete()](#module_uloop.process+delete) ⇒ `boolean`

#### process.pid() ⇒ `number`
Returns the process ID.

This method returns the process ID (PID) of the operating system process
launched by {@link module:uloop#process|process().

**Kind**: instance method of [`process`](#module_uloop.process)  
**Returns**: `number` - The process ID (PID) of the associated launched process.  
**Example**  
```text
const proc = uloop.process(…);

printf("Process ID: %d\n", proc.pid());
```

#### process.delete() ⇒ `boolean`
Unregisters the process from uloop.

This method unregisters the process from the uloop event loop and releases
any associated resources. However, note that the operating system process
itself is not terminated by this method.

**Kind**: instance method of [`process`](#module_uloop.process)  
**Returns**: `boolean` - Returns `true` on success.  
**Example**  
```text
const proc = uloop.process(…);

proc.delete();
```

### uloop.pipe
**Kind**: static class of [`uloop`](#module_uloop)  
**See**: [task()](#module_uloop+task)  

* [.pipe](#module_uloop.pipe)
    * [.send(msg)](#module_uloop.pipe+send) ⇒ `boolean`
    * [.receive()](#module_uloop.pipe+receive) ⇒ `\*`
    * [.sending()](#module_uloop.pipe+sending) ⇒ `boolean`
    * [.receiving()](#module_uloop.pipe+receiving) ⇒ `boolean`

#### pipe.send(msg) ⇒ `boolean`
Sends a serialized message to the task handle.

This method serializes the provided message and sends it over the task
communication pipe. In the main thread, the message is deserialized and
passed as an argument to the output callback function registered with the
task handle.

**Kind**: instance method of [`pipe`](#module_uloop.pipe)  
**Returns**: `boolean` - Returns `true` on success, indicating that the message was successfully sent
over the pipe. Returns `null` on error, such as when there's no output
callback registered with the task handle.  

| Param | Type | Description |
| --- | --- | --- |
| msg | `\*` | The message to be serialized and sent over the pipe. It can be of arbitrary type. |

**Example**  
```ucode
// Send a message over the uloop pipe
const success = pipe.send(message);

if (success)
    printf("Message sent successfully\n");
else
    die(`Error sending message: ${uloop.error()}\n`);
```

#### pipe.receive() ⇒ `\*`
Reads input from the task handle.

This method reads input from the task communication pipe. The input callback
function registered with the task handle is invoked to return the input data,
which is then serialized, sent over the pipe, and deserialized by the receive
method.

**Kind**: instance method of [`pipe`](#module_uloop.pipe)  
**Returns**: `\*` - Returns the deserialized message read from the task communication pipe.
Returns `null` on error, such as when there's no input callback registered
on the task handle.  
**Example**  
```ucode
// Read input from the task communication pipe
const message = pipe.receive();

if (message !== null)
    printf("Received message: %s\n", message);
else
    die(`Error receiving message: ${uloop.error()}\n`);
```

#### pipe.sending() ⇒ `boolean`
Checks if the task handle provides input.

This method checks if the task handle has an input callback  registered.
It returns a boolean value indicating whether an input callback is present.

**Kind**: instance method of [`pipe`](#module_uloop.pipe)  
**Returns**: `boolean` - Returns `true` if the remote task handle has an input callback
registered, otherwise returns `false`.  
**Example**  
```ucode
// Check if the remote task handle has an input callback
const hasInputCallback = pipe.sending();

if (hasInputCallback)
    printf("Input callback is registered on task handle\n");
else
    printf("No input callback on the task handle\n");
```

#### pipe.receiving() ⇒ `boolean`
Checks if the task handle reads output.

This method checks if the task handle has an output callback registered.
It returns a boolean value indicating whether an output callback is present.

**Kind**: instance method of [`pipe`](#module_uloop.pipe)  
**Returns**: `boolean` - Returns `true` if the task handle has an output callback registered,
otherwise returns `false`.  
**Example**  
```ucode
// Check if the task handle has an output callback
const hasOutputCallback = pipe.receiving();

if (hasOutputCallback)
    printf("Output callback is registered on task handle\n");
else
    printf("No output callback on the task handle\n");
```

### uloop.task
**Kind**: static class of [`uloop`](#module_uloop)  
**See**: [task()](#module_uloop+task)  

* [.task](#module_uloop.task)
    * [.pid()](#module_uloop.task+pid) ⇒ `number`
    * [.kill()](#module_uloop.task+kill) ⇒ `boolean`
    * [.finished()](#module_uloop.task+finished) ⇒ `boolean`

#### task.pid() ⇒ `number`
Returns the process ID.

This method returns the process ID (PID) of the underlying forked process
launched by {@link module:uloop#task|task().

**Kind**: instance method of [`task`](#module_uloop.task)  
**Returns**: `number` - The process ID (PID) of the forked task process.  
**Example**  
```text
const task = uloop.task(…);

printf("Process ID: %d\n", task.pid());
```

#### task.kill() ⇒ `boolean`
Terminates the task process.

This method terminates the task process. It sends a termination signal to
the task process, causing it to exit. Returns `true` on success, indicating
that the task process was successfully terminated. Returns `null` on error,
such as when the task process has already terminated.

**Kind**: instance method of [`task`](#module_uloop.task)  
**Returns**: `boolean` - Returns `true` when the task process was successfully terminated.
Returns `null` on error, such as when the process has already terminated.  
**Example**  
```ucode
// Terminate the task process
const success = task.kill();

if (success)
    printf("Task process terminated successfully\n");
else
    die(`Error terminating task process: ${uloop.error()}\n`);
```

#### task.finished() ⇒ `boolean`
Checks if the task ran to completion.

This method checks if the task function has already run to completion.
It returns a boolean value indicating whether the task function has finished
executing.

**Kind**: instance method of [`task`](#module_uloop.task)  
**Returns**: `boolean` - Returns `true` if the task function has already run to completion, otherwise
returns `false`.  
**Example**  
```ucode
// Check if the task function has finished executing
const isFinished = task.finished();

if (isFinished)
    printf("Task function has finished executing\n");
else
    printf("Task function is still running\n");
```

### uloop.interval
**Kind**: static class of [`uloop`](#module_uloop)  
**See**: [interval()](#module_uloop+interval)  

* [.interval](#module_uloop.interval)
    * [.set([interval])](#module_uloop.interval+set) ⇒ `boolean`
    * [.remaining()](#module_uloop.interval+remaining) ⇒ `number`
    * [.expirations()](#module_uloop.interval+expirations) ⇒ `number`
    * [.cancel()](#module_uloop.interval+cancel) ⇒ `boolean`

#### interval.set([interval]) ⇒ `boolean`
Rearms the uloop interval timer with the specified interval.

This method rearms the interval timer with the specified interval value,
allowing it to trigger repeatedly after the specified amount of time. If no
interval value is provided or if the provided value is negative, the interval
remains disabled until rearmed with a positive interval value.

**Kind**: instance method of [`interval`](#module_uloop.interval)  
**Returns**: `boolean` - Returns `true` on success, `null` on error, such as an invalid interval argument.  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [interval] | `number` | `-1` | Optional. The interval value in milliseconds specifying when the interval triggers again. Defaults to -1, which disables the interval until rearmed with a positive interval value. |

**Example**  
```ucode
// Rearm the uloop interval with a interval of 1000 milliseconds
const success = interval.set(1000);

if (success)
    printf("Interval rearmed successfully\n");
else
    printf("Error occurred while rearming interval: ${uloop.error()}\n");

// Disable the uloop interval
const success = interval.set();

if (success)
    printf("Interval disabled successfully\n");
else
    printf("Error occurred while disabling interval: ${uloop.error()}\n");
```

#### interval.remaining() ⇒ `number`
Returns the milliseconds until the next expiration.

This method returns the remaining time until the uloop interval expires
and triggers again. If the interval is not armed (i.e., disabled),
it returns -1.

**Kind**: instance method of [`interval`](#module_uloop.interval)  
**Returns**: `number` - The milliseconds until the next expiration of the uloop interval, or -1 if
the interval is not armed.  
**Example**  
```ucode
// Get the milliseconds until the next expiration of the uloop interval
const remainingTime = interval.remaining();

if (remainingTime !== -1)
    printf("Milliseconds until next expiration: %d\n", remainingTime);
else
    printf("Interval is not armed\n");
```

#### interval.expirations() ⇒ `number`
Returns number of times the interval timer fired.

This method returns the number of times the uloop interval timer has expired
(fired) since it was instantiated.

**Kind**: instance method of [`interval`](#module_uloop.interval)  
**Returns**: `number` - The number of times the uloop interval timer has expired (fired).  
**Example**  
```ucode
// Get the number of times the uloop interval timer has expired
const expirations = interval.expirations();
printf("Number of expirations: %d\n", expirations);
```

#### interval.cancel() ⇒ `boolean`
Cancels the uloop interval.

This method cancels the uloop interval, disarming it and removing it from the
event loop. Associated resources are released.

**Kind**: instance method of [`interval`](#module_uloop.interval)  
**Returns**: `boolean` - Returns `true` on success.  
**Example**  
```ucode
// Cancel the uloop interval
interval.cancel();
```

### uloop.signal
**Kind**: static class of [`uloop`](#module_uloop)  
**See**: [signal()](#module_uloop+signal)  

* [.signal](#module_uloop.signal)
    * [.signo()](#module_uloop.signal+signo) ⇒ `number`
    * [.delete()](#module_uloop.signal+delete) ⇒ `boolean`

#### signal.signo() ⇒ `number`
Returns the associated signal number.

This method returns the signal number that this uloop signal handler is
configured to respond to.

**Kind**: instance method of [`signal`](#module_uloop.signal)  
**Returns**: `number` - The signal number that this handler is responding to.  
**Example**  
```ucode
// Get the signal number that the uloop signal handler is responding to
const sighandler = uloop.signal("SIGINT", () => printf("Cought INT\n"));
printf("Signal number: %d\n", sighandler.signo());
```

#### signal.delete() ⇒ `boolean`
Uninstalls the signal handler.

This method uninstalls the signal handler, restoring the previous or default
handler for the signal, and releasing any associated resources.

**Kind**: instance method of [`signal`](#module_uloop.signal)  
**Returns**: `boolean` - Returns `true` on success.  
**Example**  
```text
// Uninstall the signal handler and restore the previous/default handler
const sighandler = uloop.signal(…);
sighandler.delete();
```

### uloop~Event Mode Constants
The `ULOOP_*` constants are passed as bitwise OR-ed number to the
[handle()](#module_uloop.handle+handle) function to specify the IO
events that should be monitored on the given handle.

**Kind**: inner typedef of [`uloop`](#module_uloop)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| ULOOP_READ | `number` | File or socket is readable. |
| ULOOP_WRITE | `number` | File or socket is writable. |
| ULOOP_EDGE_TRIGGER | `number` | Enable edge-triggered event mode. |
| ULOOP_BLOCKING | `number` | Do not make descriptor non-blocking. |

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

---
