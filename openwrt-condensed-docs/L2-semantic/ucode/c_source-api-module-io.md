---
title: 'ucode module: io'
module: ucode
origin_type: c_source
token_count: 4058
version: 591d1f6
source_file: L1-raw/ucode/c_source-api-module-io.md
last_pipeline_run: '2026-03-12T22:39:22.932543+00:00'
upstream_path: lib/io.c
language: c
ai_summary: Provides buffered I/O stream primitives for ucode. Implements open() and fdopen() returning stream objects with read(), write(), readline(), flush(), seek(), tell(), and close() methods. Exposes io.stdin, io.stdout, and io.stderr as pre-opened streams, and pipe() for creating connected stream pairs for subprocess communication.
ai_when_to_use: Use for line-oriented reading of large files or when piped subprocess output needs to be consumed incrementally rather than loaded entirely into memory with fs.readfile(); also use io.stderr for error output in scripts run under procd.
ai_related_topics:
- io.open
- io.fdopen
- io.pipe
- io.stdin
- io.stdout
- io.stderr
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
- An [fs.file](../ucode/c_source-api-module-fs.md), [fs.proc](../ucode/c_source-api-module-fs.md), or socket resource
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