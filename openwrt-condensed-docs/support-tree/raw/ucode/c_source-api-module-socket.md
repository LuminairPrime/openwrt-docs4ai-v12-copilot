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