---
title: 'ucode module: fs'
module: ucode
origin_type: c_source
token_count: 11211
source_file: L1-raw/ucode/c_source-api-module-fs.md
last_pipeline_run: '2026-03-28T11:59:43.422282+00:00'
source_commit: unknown
source_url: https://github.com/nicowillis/ucode/blob/unknown/lib/fs.c
source_locator: lib/fs.c
language: c
---

> **Source:** [https://github.com/nicowillis/ucode/blob/unknown/lib/fs.c](https://github.com/nicowillis/ucode/blob/unknown/lib/fs.c)
> **Kind:** c_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

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

### fs.statvfs(path) ⇒ [`StatVFSResult`](#module_fs.StatVFSResult)
Query filesystem statistics for a given pathname.

The returned object mirrors the members of `struct statvfs`.
Convenience properties `freesize` and `totalsize` are added,
which are calculated as:
- `frsize * bfree` to provide the free space in bytes and
- `frsize * blocks` to provide the total size of the filesystem.

On Linux an additional `type` field (magic number from `statfs`) is
provided if the call succeeds.

Returns `null` on failure (and sets `fs.last_error`).

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type | Description |
| --- | --- | --- |
| path | `string` | The path to the directory or file with which to query the filesystem. |

**Example**  
```ucode
// Get filesystem statistics for a path
const stats = statvfs('path/to/directory');
print(stats.bsize); // file system block size
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

### fs.glob(...pattern) ⇒ `Array.<string>`
Takes an arbitrary number of glob patterns and
resolves matching files for each one. In case of multiple patterns,
no efforts are made to remove duplicates or to globally sort the combined
match list. The list of matches for each individual pattern is sorted.
Returns an array containing all matched file paths.

**Kind**: instance method of [`fs`](#module_fs)  

| Param | Type |
| --- | --- |
| ...pattern | `Arguments` | 

**Example**  
```ucode
import { chdir, glob } from 'fs';
chdir('/etc/ssl/certs/');
for (let cert in glob('*.crt', '*.pem')) {
	if (cert != null)
		print(cert, '\n');
}
// ACCVRAIZ1.crt
// AC_RAIZ_FNMT-RCM.crt
// AC_RAIZ_FNMT-RCM_SERVIDORES_SEGUROS.crt
// ...
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

### fs.StatVFSResult : `Object`
**Kind**: static typedef of [`fs`](#module_fs)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| bsize | `number` | file system block size |
| frsize | `number` | fragment size |
| blocks | `number` | total blocks |
| bfree | `number` | free blocks |
| bavail | `number` | free blocks available to unprivileged users |
| files | `number` | total file nodes (inodes) |
| ffree | `number` | free file nodes |
| favail | `number` | free nodes available to unprivileged users |
| fsid | `number` | file system id |
| flag | [`ST\_FLAGS`](#module_fs.ST_FLAGS) | mount flags |
| namemax | `number` | maximum filename length |
| freesize | `number` | free space in bytes (calculated as `frsize * bfree`) |
| totalsize | `number` | total size of the filesystem (calculated as `frsize * blocks`) |
| type | `number` | (Linux only) magic number of the filesystem, obtained from `statfs` |

### fs.ST\_FLAGS
Bitmask flags used at volume mount time (¹ - Linux only).

**Kind**: static typedef of [`fs`](#module_fs)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| ST_MANDLOCK | `number` | Mandatory locking.¹ |
| ST_NOATIME | `number` | Do not update access times.¹ |
| ST_NODEV | `number` | Do not allow device files.¹ |
| ST_NODIRATIME | `number` | Do not update directory access times.¹ |
| ST_NOEXEC | `number` | Do not allow execution of binaries.¹ |
| ST_NOSUID | `number` | Do not allow set-user-identifier or set-group-identifier bits. |
| ST_RDONLY | `number` | Read-only filesystem. |
| ST_RELATIME | `number` | Update access times relative to modification time.¹ |
| ST_SYNCHRONOUS | `number` | Synchronous writes.¹ |
| ST_NOSYMFOLLOW | `number` | Do not follow symbolic links.¹ |
