# ucode Navigation Map

> **Contains:** Headers and function signatures for ucode.
> **Generated:** 2026-03-20T01:28:16.926497+00:00

---

> **Summary:** Provides runtime introspection and tracing utilities for ucode scripts. Implements traceback() to capture the current call stack, getinfo() to inspect function and closure metadata, and memdump() for object inspection at runtime. Used primarily for structured error reporting and development-time debugging in production handlers.
> **Use Case:** Use to produce meaningful stack traces in error handlers, inspect closures during development, or emit diagnostic context information in ucode services running under procd where stderr is not easily accessible.
# ucode module: debug
## Debugger Module
### debug.memdump(file) ⇒ `boolean`
### debug.traceback([level]) ⇒ [`Array.<StackTraceEntry>`](#module_debug.StackTraceEntry)
### debug.sourcepos() ⇒ [`SourcePosition`](#module_debug.SourcePosition)
### debug.getinfo(value) ⇒ [`ValueInformation`](#module_debug.ValueInformation)
### debug.getlocal([level], variable) ⇒ [`LocalInfo`](#module_debug.LocalInfo)
### debug.setlocal([level], variable, [value]) ⇒ [`LocalInfo`](#module_debug.LocalInfo)
### debug.getupval(target, variable) ⇒ [`UpvalInfo`](#module_debug.UpvalInfo)
### debug.setupval(target, variable, value) ⇒ [`UpvalInfo`](#module_debug.UpvalInfo)
### debug.StackTraceEntry : `Object`
### debug.SourcePosition : `Object`
### debug.UpvalRef : `Object`
### debug.ValueInformation : `Object`
### debug.LocalInfo : `Object`
### debug.UpvalInfo : `Object`

> **Summary:** Provides cryptographic hash and HMAC computation for ucode. Implements new() returning a digest context with update() and final() methods, supporting MD5, SHA1, SHA256, SHA512, and HMAC variants. Enables incremental hashing of large data streams and one-shot hash computation for data integrity checking and API authentication tokens.
> **Use Case:** Use when computing checksums for config change detection, generating HMAC tokens for API authentication in ucode rpcd handlers, or verifying package integrity in custom ucode-based package management scripts.
# ucode module: digest
## Digest Functions
### digest.md5(str) ⇒ `string`
### digest.sha1(str) ⇒ `string`
### digest.sha256(str) ⇒ `string`
### digest.md2(str) ⇒ `string`
### digest.md4(str) ⇒ `string`
### digest.sha384(str) ⇒ `string`
### digest.sha512(str) ⇒ `string`
### digest.md5\_file(path) ⇒ `string`
### digest.sha1\_file(path) ⇒ `string`
### digest.sha256\_file(path) ⇒ `string`
### digest.md2\_file(path) ⇒ `string`
### digest.md4\_file(path) ⇒ `string`
### digest.sha384\_file(path) ⇒ `string`
### digest.sha512\_file(path) ⇒ `string`

# ucode module: fs
## Filesystem Access
### fs.error() ⇒ `string`
### fs.popen(command, [mode]) ⇒ [`proc`](#module_fs.proc)
### fs.open(path, [mode], [perm]) ⇒ [`file`](#module_fs.file)
### fs.fdopen(fd, [mode]) ⇒ `Object`
### fs.dup2(oldfd, newfd) ⇒ `boolean`
### fs.opendir(path) ⇒ [`dir`](#module_fs.dir)
### fs.readlink(path) ⇒ `string`
### fs.stat(path) ⇒ [`FileStatResult`](#module_fs.FileStatResult)
### fs.lstat(path) ⇒ [`FileStatResult`](#module_fs.FileStatResult)
### fs.statvfs(path) ⇒ [`StatVFSResult`](#module_fs.StatVFSResult)
### fs.mkdir(path) ⇒ `boolean`
### fs.rmdir(path) ⇒ `boolean`
### fs.symlink(target, path) ⇒ `boolean`
### fs.unlink(path) ⇒ `boolean`
### fs.getcwd() ⇒ `string`
### fs.chdir(path) ⇒ `boolean`
### fs.chmod(path, mode) ⇒ `boolean`
### fs.chown(path, [uid], [gid]) ⇒ `boolean`
### fs.rename(oldPath, newPath) ⇒ `boolean`
### fs.glob(...pattern) ⇒ `Array.<string>`
### fs.dirname(path) ⇒ `string`
### fs.basename(path) ⇒ `string`
### fs.lsdir(path) ⇒ `Array.<string>`
### fs.mkstemp([template]) ⇒ [`file`](#module_fs.file)
### fs.mkdtemp([template]) ⇒ `string`
### fs.access(path, [mode]) ⇒ `boolean`
### fs.readfile(path, [limit]) ⇒ `string`
### fs.writefile(path, data, [limit]) ⇒ `number`
### fs.realpath(path) ⇒ `string`
### fs.pipe() ⇒ [`Array.<file>`](#module_fs.file)
### fs.proc
#### proc.close() ⇒ `number`
#### proc.read(length) ⇒ `string`
#### proc.write(data) ⇒ `number`
#### proc.flush() ⇒ `boolean`
#### proc.fileno() ⇒ `number`
#### proc.error() ⇒ `string`
### fs.file
#### file.close() ⇒ `boolean`
#### file.read(length) ⇒ `string`
#### file.write(data) ⇒ `number`
#### file.seek([offset], [position]) ⇒ `boolean`
#### file.truncate([offset]) ⇒ `boolean`
#### file.lock([op]) ⇒ `boolean`
#### file.tell() ⇒ `number`
#### file.isatty() ⇒ `boolean`
#### file.flush() ⇒ `boolean`
#### file.fileno() ⇒ `number`
#### file.ioctl(direction, type, num, [value]) ⇒ `number` \| `string`
#### file.error() ⇒ `string`
### fs.dir
#### dir.fileno() ⇒ `number`
#### dir.read() ⇒ `string`
#### dir.tell() ⇒ `number`
#### dir.seek(offset) ⇒ `boolean`
#### dir.close() ⇒ `boolean`
#### dir.error() ⇒ `string`
### fs.FileStatResult : `Object`
### fs.StatVFSResult : `Object`
### fs.ST\_FLAGS

> **Summary:** Provides buffered I/O stream primitives for ucode. Implements open() and fdopen() returning stream objects with read(), write(), readline(), flush(), seek(), tell(), and close() methods. Exposes io.stdin, io.stdout, and io.stderr as pre-opened streams, and pipe() for creating connected stream pairs for subprocess communication.
> **Use Case:** Use for line-oriented reading of large files or when piped subprocess output needs to be consumed incrementally rather than loaded entirely into memory with fs.readfile(); also use io.stderr for error output in scripts run under procd.
# ucode module: io
## I/O Operations
### io.error() ⇒ `string`
### io.new(fd) ⇒ [`handle`](#module_io.handle)
### io.open(path, [flags], [mode]) ⇒ [`handle`](#module_io.handle)
### io.pipe() ⇒ [`Array.<handle>`](#module_io.handle)
### io.from(value) ⇒ [`handle`](#module_io.handle)


### io.handle
#### handle.ptsname() ⇒ `string`
#### handle.tcgetattr() ⇒ `object`
#### handle.tcsetattr(attrs, [when]) ⇒ `boolean`

#### handle.grantpt() ⇒ `boolean`
#### handle.unlockpt() ⇒ `boolean`
#### handle.read(length) ⇒ `string`
#### handle.write(data) ⇒ `number`
#### handle.seek([offset], [whence]) ⇒ `boolean`
#### handle.tell() ⇒ `number`
#### handle.dup() ⇒ [`handle`](#module_io.handle)
#### handle.dup2(newfd) ⇒ `boolean`
#### handle.fileno() ⇒ `number`
#### handle.fcntl(cmd, [arg]) ⇒ `number` \| [`handle`](#module_io.handle)
#### handle.ioctl(direction, type, num, [value]) ⇒ `number` \| `string`
#### handle.isatty() ⇒ `boolean`
#### handle.close() ⇒ `boolean`
#### handle.error() ⇒ `string`

> **Summary:** Provides syslog integration for ucode scripts via the POSIX syslog API. Exposes openlog(), syslog(), and closelog() with facility constants (LOG_DAEMON, LOG_USER, LOG_LOCAL0–LOG_LOCAL7) and priority constants (LOG_DEBUG, LOG_INFO, LOG_NOTICE, LOG_WARNING, LOG_ERR, LOG_CRIT). Enables structured kernel-level log emission from ucode services.
> **Use Case:** Use in ucode daemons and init handlers to emit structured syslog entries that appear in OpenWrt's logread output alongside other system services, rather than writing to stdout or a plain file.
# ucode module: log
## System logging functions
## Constants
### Syslog Options
### Syslog Facilities
### Syslog Priorities
### Ulog channels
### log.openlog([ident], [options], [facility]) ⇒ `boolean`
### log.syslog(priority, format, [...args]) ⇒ `boolean`
### log.closelog()
### log.ulog\_open([channel], [facility], [ident]) ⇒ `boolean`
### log.ulog(priority, format, [...args]) ⇒ `boolean`
### log.ulog\_close()
### log.ulog\_threshold([priority]) ⇒ `boolean`
### log.INFO(format, [...args]) ⇒ `boolean`
### log.NOTE(format, [...args]) ⇒ `boolean`
### log.WARN(format, [...args]) ⇒ `boolean`
### log.ERR(format, [...args]) ⇒ `boolean`
### log.LogOption : `enum`
### log.LogFacility : `enum`
### log.LogPriority : `enum`
### log.UlogChannel : `enum`

> **Summary:** Provides standard mathematical functions for ucode scripts, mirroring the JavaScript Math object surface. Implements abs(), atan2(), ceil(), cos(), exp(), floor(), log(), max(), min(), pow(), round(), sin(), sqrt(), and tan() along with the constants math.PI and math.E for floating-point arithmetic.
> **Use Case:** Use for numerical calculations in LuCI view scripts, configuration validators, and network metric processors that need floating-point math beyond basic arithmetic operators available in ucode natively.
# ucode module: math
## Mathematical Functions
### math.abs(number) ⇒ `number`
### math.atan2(y, x) ⇒ `number`
### math.cos(x) ⇒ `number`
### math.exp(x) ⇒ `number`
### math.log(x) ⇒ `number`
### math.sin(x) ⇒ `number`
### math.sqrt(x) ⇒ `number`
### math.pow(x, y) ⇒ `number`
### math.rand([a], [b]) ⇒ `number`
### math.srand(seed)
### math.isnan(x) ⇒ `boolean`

> **Summary:** Provides netlink 802.11 wireless configuration API bindings for ucode. Implements request() to send and receive nl80211 commands including NL80211_CMD_GET_INTERFACE, NL80211_CMD_GET_STATION, NL80211_CMD_TRIGGER_SCAN, and regulatory domain queries. Returns structured attribute dictionaries parsed from kernel nl80211 netlink messages.
> **Use Case:** Use in ucode-based wireless management handlers that need direct kernel-level 802.11 interface control, station enumeration, or scan triggering beyond what iwinfo or standard UCI wireless config expose.
# ucode module: nl80211
## Wireless Netlink
### nl80211.listener
### nl80211~Netlink message flags
### nl80211~nl80211 commands
### nl80211~Scan flags
### nl80211~BSS status constants
### nl80211~BSS use-for and cannot-use-reasons constants
### nl80211~HWSIM commands
### nl80211~Interface types

> **Summary:** Provides DNS name resolution for ucode scripts using the system resolver. Implements query() for raw DNS record lookups (A, AAAA, MX, TXT, etc.) and getaddrinfo() for hostname-to-address resolution returning both IPv4 and IPv6 results in a structured array.
> **Use Case:** Use in ucode-based network management scripts that must resolve hostnames to IP addresses before establishing connections, checking reachability, or populating firewall rules — replaces spawning nslookup or dig subprocesses.
# ucode module: resolv
## DNS Resolution Module
## Record Types
## Response Codes
## Response Format
### Record Format by Type
## Examples
### resolv.query(names, [options]) ⇒ `object`
### resolv.error() ⇒ `string` \| `null`

> **Summary:** Provides rtnetlink interface bindings for ucode to enumerate and monitor kernel network state. Implements request() to send RTM_GETLINK, RTM_GETROUTE, RTM_GETNEIGH, and RTM_GETADDR queries and receive structured attribute dictionaries from the kernel. Enables subscription to netlink multicast groups for real-time interface and route change notifications.
> **Use Case:** Use when a ucode service needs kernel-level network interface state, live route table changes, or ARP/NDP neighbor tables without invoking the ip command or spawning subprocesses.
# ucode module: rtnl
## Routing Netlink
### rtnl.error() ⇒ `string`
### rtnl.request(cmd, flags, payload) ⇒ `\*`
### rtnl.listener(callback, [commands], [groups]) ⇒ [`listener`](#module_rtnl.listener)
### rtnl.listener
#### listener.set\_commands(commands) ⇒ `boolean`
#### listener.close() ⇒ `boolean`
### rtnl~Netlink message flags
### rtnl~IPv6 address generation modes
### rtnl~MACVLAN modes
### rtnl~MACVLAN MAC address commands
### rtnl~MACsec validation levels
### rtnl~MACsec offload modes
### rtnl~IPVLAN modes
### rtnl~VXLAN data frame flags
### rtnl~Geneve data frame flags
### rtnl~GTP roles
### rtnl~Port request types
### rtnl~Port VDP responses
### rtnl~Port profile responses
### rtnl~IPoIB modes
### rtnl~HSR protocols
### rtnl~Link extended statistics types
### rtnl~XDP attach types
### rtnl~FDB notification bits
### rtnl~Route commands
### rtnl~Route types
### rtnl~Route scopes
### rtnl~Route tables
### rtnl~Route metrics
### rtnl~Prefix types
### rtnl~Neighbor discovery user option types
### rtnl~Multicast groups
### rtnl~Route flags
### rtnl~Address families
### rtnl~Generic Routing Encapsulation flags
### rtnl~Tunnel encapsulation types
### rtnl~Tunnel encapsulation flags
### rtnl~IPv6 tunnel flags
### rtnl~Interface flags
### rtnl~Neighbor states
### rtnl~Address flags
### rtnl~FIB rule flags
### rtnl~FIB rule actions
### rtnl~Network configuration indices
### rtnl~Bridge flags
### rtnl~Bridge modes
### rtnl~Bridge VLAN information flags

> **Summary:** Provides low-level socket programming for ucode via POSIX socket API bindings. Implements create() for AF_INET, AF_INET6, and AF_UNIX socket creation, plus connect(), bind(), listen(), accept(), send(), recv(), recvfrom(), sendto(), close(), setsockopt(), and getsockopt() for full network and IPC socket lifecycle management.
> **Use Case:** Use when a ucode service must open a raw or domain socket for custom IPC, network monitoring daemons, or protocol implementation that does not go through ubus and requires direct kernel socket access.
# ucode module: socket
## Socket Module
### socket.error([numeric]) ⇒ `string` \| `number`
### socket.strerror(code) ⇒ `string`
### socket.sockaddr(address) ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
### socket.nameinfo(address, [flags]) ⇒ `Object`
### socket.addrinfo(hostname, [service], [hints]) ⇒ [`Array.<AddressInfo>`](#module_socket.AddressInfo)
### socket.poll(timeout, ...sockets) ⇒ [`Array.<PollSpec>`](#module_socket.PollSpec)
### socket.connect(host, [service], [hints], [timeout]) ⇒ [`socket`](#module_socket.socket)
### socket.listen(host, [service], [hints], [backlog], [reuseaddr]) ⇒ [`socket`](#module_socket.socket)
### socket.create([domain], [type], [protocol]) ⇒ [`socket`](#module_socket.socket)
### socket.open([fd]) ⇒ [`socket`](#module_socket.socket)
### socket.pair([type]) ⇒ `Array.<?module:socket.socket>`
### socket.socket
#### socket.setopt(level, option, value) ⇒ `boolean`
#### socket.getopt(level, option) ⇒ `\*`
#### socket.fileno() ⇒ `number`
#### socket.connect(address, port) ⇒ `boolean`
#### socket.send(data, [flags], [address]) ⇒ `number`
#### socket.recv([length], [flags], [address]) ⇒ `string`
#### socket.sendmsg([data], [ancillaryData], [address], [flags]) ⇒ `number`
#### socket.recvmsg([sizes], [ancillarySize], [flags]) ⇒ [`ReceivedMessage`](#module_socket.socket.ReceivedMessage)
#### socket.bind(address) ⇒ `boolean`
#### socket.listen([backlog]) ⇒ `boolean`
#### socket.accept([address], [flags]) ⇒ [`socket`](#module_socket.socket)
#### socket.shutdown(how) ⇒ `boolean`
#### socket.peercred() ⇒ [`PeerCredentials`](#module_socket.socket.PeerCredentials)
#### socket.peername() ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
#### socket.sockname() ⇒ [`SocketAddress`](#module_socket.socket.SocketAddress)
#### socket.close() ⇒ `boolean`
#### socket.error([numeric]) ⇒ `string` \| `number`
#### socket.SocketAddress : `Object`
#### socket.ControlMessage : `Object`
#### socket.ReceivedMessage : `Object`
#### socket.PeerCredentials : `Object`
### socket.AddressInfo : `Object`
### socket.PollSpec : `Array`
### socket~Address Families
### socket~Socket Types
### socket~Message Flags
### socket~IP Protocol Constants
### socket~IPv6 : `Object`
### socket~Socket Option Constants

> **Summary:** Provides binary data packing and unpacking for ucode using a Python struct-style format string syntax. Implements pack() to encode values into a binary string and unpack() to decode a binary buffer into an array of typed values. Supports format codes for unsigned/signed integers of all widths (B, H, I, Q), floats, and byte strings.
> **Use Case:** Use when parsing binary kernel netlink messages, reading custom binary protocol headers from raw sockets, or inspecting C struct layouts read through /proc or /sys files in ucode scripts.
# ucode module: struct
## Handle Packed Binary Data
## Format Strings
### Byte Order, Size, and Alignment
### Format Characters
## Examples
### struct.pack(format, ...values) ⇒ `string`
### struct.unpack(format, input, [offset]) ⇒ `array`
### struct.new(format) ⇒ [`instance`](#module_struct.instance)
### struct.buffer([initialData]) ⇒ [`buffer`](#module_struct.buffer)
### struct.instance
#### instance.pack(...values) ⇒ `string`
#### instance.unpack(input, [offset]) ⇒ `array`
### struct.buffer
#### buffer.pos([position]) ⇒ `number` \| [`buffer`](#module_struct.buffer)
#### buffer.length([length]) ⇒ `number` \| [`buffer`](#module_struct.buffer)
#### buffer.start() ⇒ [`buffer`](#module_struct.buffer)
#### buffer.end() ⇒ [`buffer`](#module_struct.buffer)
#### buffer.put(format, ...values) ⇒ [`buffer`](#module_struct.buffer)
#### buffer.get(format) ⇒ `\*`
#### buffer.get(format) ⇒ `array`
#### buffer.slice([start], [end]) ⇒ `string`
#### buffer.set([value], [start], [end]) ⇒ [`buffer`](#module_struct.buffer)
#### buffer.pull() ⇒ `string`

> **Summary:** Provides direct ucode bindings for OpenWrt libuci to read and write UCI configuration. Exposes cursor() to create a UCI cursor with methods get(), set(), unset(), commit(), revert(), sections(), foreach(), delete(), and add() for complete UCI config management from ucode scripts. Supports transactional reads and staged writes with explicit commit.
> **Use Case:** Use when writing ucode-based services or rpcd handlers that need to read or modify OpenWrt system configuration without spawning a uci subprocess; cursor() provides a transactional session for safe concurrent config access.
# ucode module: uci
## OpenWrt UCI configuration
### uci.error() ⇒ `string`
### uci.cursor([config_dir], [delta_dir], [config2_dir], Parser) ⇒ [`cursor`](#module_uci.cursor)
### uci.cursor
#### cursor.load(config) ⇒ `boolean`
#### cursor.unload(config) ⇒ `boolean`
#### cursor.get(config, section, [option]) ⇒ `string` \| `Array.<string>`
#### cursor.get\_all(config, [section]) ⇒ `Object.<string, module:uci.cursor.SectionObject>` \| [`SectionObject`](#module_uci.cursor.SectionObject)
#### cursor.get\_first(config, type, [option]) ⇒ `string` \| `Array.<string>`
#### cursor.add(config, type) ⇒ `string`
#### cursor.set(config, section, option_or_type, [value]) ⇒ `boolean`
#### cursor.delete(config, section, [option]) ⇒ `boolean`
#### cursor.list\_append(config, section, option, value) ⇒ `boolean`
#### cursor.list\_remove(config, section, option, value) ⇒ `boolean`
#### cursor.rename(config, section, option_or_name, [name]) ⇒ `boolean`
#### cursor.reorder(config, section, index) ⇒ `boolean`
#### cursor.save([config]) ⇒ `boolean`
#### cursor.commit([config]) ⇒ `boolean`
#### cursor.revert([config]) ⇒ `boolean`
#### cursor.changes([config]) ⇒ `Object.<string, Array.<module:uci.cursor.ChangeRecord>>`
#### cursor.foreach(config, type, callback) ⇒ `boolean`
#### cursor.configs() ⇒ `Array.<string>`
#### cursor.error() ⇒ `string`
#### cursor.ParserFlags : `Object`
#### cursor.ChangeRecord : `Array.<string>`
#### cursor.SectionObject : `Object.<string, (boolean\|number\|string\|Array.<string>)>`
#### cursor.SectionCallback : `function`

> **Summary:** Provides ucode bindings for the OpenWrt libubox uloop event loop. Implements asynchronous programming primitives including timer(), interval(), handle(), process(), signal(), task(), and run() for single-threaded event-driven applications. Supports file descriptor watching, child process lifecycle management, and UNIX signal handling within ucode scripts.
> **Use Case:** Use in any ucode script that must perform non-blocking I/O, schedule periodic timers, or manage child processes — the standard approach for background daemons and hotplug handlers in OpenWrt.
# ucode module: uloop
## OpenWrt uloop event loop
### uloop.error() ⇒ `string`
### uloop.init() ⇒ `boolean`
### uloop.run([timeout]) ⇒ `number`
### uloop.cancelling() ⇒ `boolean`
### uloop.running() ⇒ `boolean`
### uloop.end() ⇒ `void`
### uloop.done() ⇒ `void`
### uloop.timer([timeout], callback) ⇒ [`timer`](#module_uloop.timer)
### uloop.handle(handle, callback, events) ⇒ [`handle`](#module_uloop.handle)
### uloop.process(executable, [args], [env], callback) ⇒ [`process`](#module_uloop.process)
### uloop.task(taskFunction, [outputCallback], [inputCallback]) ⇒ [`task`](#module_uloop.task)
### uloop.interval([timeout], callback) ⇒ [`interval`](#module_uloop.interval)
### uloop.signal(signal, callback) ⇒ [`signal`](#module_uloop.signal)
### uloop.timer
#### timer.set([timeout]) ⇒ `boolean`
#### timer.remaining() ⇒ `number`
#### timer.cancel() ⇒ `boolean`
### uloop.handle
#### handle.fileno() ⇒ `number`
#### handle.handle() ⇒ `module:fs.file` \| `module:fs.proc` \| `module:socket.socket`
#### handle.delete() ⇒ `void`
### uloop.process
#### process.pid() ⇒ `number`
#### process.delete() ⇒ `boolean`
### uloop.pipe
#### pipe.send(msg) ⇒ `boolean`
#### pipe.receive() ⇒ `\*`
#### pipe.sending() ⇒ `boolean`
#### pipe.receiving() ⇒ `boolean`
### uloop.task
#### task.pid() ⇒ `number`
#### task.kill() ⇒ `boolean`
#### task.finished() ⇒ `boolean`
### uloop.interval
#### interval.set([interval]) ⇒ `boolean`
#### interval.remaining() ⇒ `number`
#### interval.expirations() ⇒ `number`
#### interval.cancel() ⇒ `boolean`
### uloop.signal
#### signal.signo() ⇒ `number`
#### signal.delete() ⇒ `boolean`
### uloop~Event Mode Constants

> **Summary:** Provides zlib compression and decompression bindings for ucode. Implements compress() and uncompress() for raw deflate/inflate over in-memory byte strings, and deflate()/inflate() for streaming compression contexts. Supports gzip-format data via gzip_compress() and gzip_uncompress() for HTTP transfer-encoding and configuration snapshot handling.
> **Use Case:** Use when a ucode service must compress or decompress data for HTTP chunked transfer, configuration backup archives, or firmware payload inspection where gzip format is expected.
# ucode module: zlib
## Zlib bindings
### zlib.deflate(str_or_resource, [gzip], [level]) ⇒ `string`
### zlib.inflate(str_or_resource) ⇒ `string`
### zlib.deflater([gzip], [level]) ⇒ [`deflate`](#module_zlib.deflate)
### zlib.inflater() ⇒ [`inflate`](#module_zlib.inflate)
### zlib.deflate
#### deflate.write(src, [flush]) ⇒ `boolean`
#### deflate.read() ⇒ `string`
#### deflate.error() ⇒ `string`
### zlib.inflate
#### inflate.write(src, [flush]) ⇒ `boolean`
#### inflate.read() ⇒ `string`
#### inflate.error() ⇒ `string`
### zlib~Compression levels
### zlib~flush options
