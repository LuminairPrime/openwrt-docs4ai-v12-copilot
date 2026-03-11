---
title: ubus (OpenWrt micro bus architecture)
module: wiki
origin_type: wiki_page
token_count: 6656
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-ubus.md
last_pipeline_run: '2026-03-11T12:37:15.044626+00:00'
language: text
ai_summary: Explains the OpenWrt ubus inter-process communication bus, which provides a Unix-socket-based RPC mechanism for daemons to expose services and receive method calls. Covers ubus object and method registration, the ubusd broker, ubus_context lifecycle, blob_buf message encoding, ubus_lookup, ubus_invoke, ubus_register_event_handler, and the acl JSON permission system.
ai_when_to_use: Reference when implementing a new daemon that needs to expose RPC methods to other processes or to LuCI via rpcd, or when a script needs to call an existing ubus service using the ubus CLI or the ubus ucode/Lua binding.
ai_related_topics:
- ubusd
- ubus_context
- blob_buf
- ubus_invoke
- ubus_register_event_handler
- rpcd
- libubox
---
# ubus (OpenWrt micro bus architecture)

See also: [What is UBUS?](https://hackmd.io/@rYMqzC-9Rxy0Isn3zClURg/H1BY98bRw)

To provide [Inter-process communication](https://en.wikipedia.org/wiki/Inter-process_communication) between various daemons and applications in OpenWrt a project called `ubus` has been developed. It consists of several parts including daemon, library and some extra helpers.

The heart of this project is the `ubusd` daemon. It provides an interface for other daemons to register themselves as well as sending messages. For those curious, this interface is implemented using Unix sockets and it uses [TLV (type-length-value)](https://en.wikipedia.org/wiki/Type-length-value) messages.

To simplify development of software using `ubus` (connecting to it) a library called `libubus` has been created.

Every daemon registers a set of paths under a specific namespace. Every path can provide multiple procedures with any number of arguments. Procedures can reply with a message.

The code is published under [LGPL 2.1 license](https://en.wikipedia.org/wiki/GNU_Lesser_General_Public_License) and can be found via git at <https://git.openwrt.org/project/ubus.git>.

## Command-line ubus tool

The `ubus` command line tool allows to interact with the `ubusd` server (with all currently registered services). It's useful for investigating/debugging registered namespaces as well as writing shell scripts. For calling procedures with parameters and returning responses it uses the user-friendly JSON format. Below is an explanation of its commands.

### Help output

    # ubus
    Usage: ubus [<options>] <command> [arguments...]
    Options:
     -s <socket>:       Set the unix domain socket to connect to
     -t <timeout>:      Set the timeout (in seconds) for a command to complete
     -S:            Use simplified output (for scripts)
     -v:            More verbose output
     -m <type>:     (for monitor): include a specific message type
                (can be used more than once)
     -M <r|t>       (for monitor): only capture received or transmitted traffic

    Commands:
     - list [<path>]            List objects
     - call <path> <method> [<message>] Call an object method
     - listen [<path>...]           Listen for events
     - send <type> [<message>]      Send an event
     - wait_for <object> [<object>...]  Wait for multiple objects to appear on ubus
     - monitor              Monitor ubus traffic

### list

To find out which services are currently running on the bus simply use the `ubus list` command. This will show a complete list of all namespaces registered with the RPC server:

    # ubus list
    dhcp
    dnsmasq
    file
    iwinfo
    log
    luci
    luci-rpc
    network
    network.device
    network.interface
    network.interface.lan
    network.interface.loopback
    network.interface.wan
    network.interface.wan6
    network.rrdns
    network.wireless
    service
    session
    system
    uci

You can filter the list by specifying a service path:

    # ubus list network.interface.*
    network.interface.lan
    network.interface.loopback
    network.interface.wan
    network.interface.wan6

To find out which procedures/methods and their argument signatures a specific service provides add `-v` in addition to the namespace path:

    # ubus -v list network.interface.lan
    'network.interface.lan' @099f0c8b
        "up": {  }
        "down": {  }
        "status": {  }
        "prepare": {  }
        "add_device": { "name": "String" }
        "remove_device": { "name": "String" }
        "notify_proto": {  }
        "remove": {  }
        "set_data": {  }

### call

Calls a given procedure within a given namespace and optionally pass arguments to it:

``` bash
# ubus call network.interface.wan status
{
    "up": true,
    "pending": false,
    "available": true,
    "autostart": true,
    "uptime": 86017,
    "l3_device": "eth1",
    "device": "eth1",
    "address": [
        {
            "address": "178.25.65.236",
            "mask": 21
        }
    ],
    "route": [
        {
            "target": "0.0.0.0",
            "mask": 0,
            "nexthop": "178.25.71.254"
        }
    ],
    "data": {

    }
}
```

The arguments must be a valid JSON string, with keys and values set according to the function signature:

``` bash
# ubus call network.device status '{ "name": "eth0" }'
{
    "type": "Network device",
    "up": true,
    "link": true,
    "mtu": 1500,
    "macaddr": "c6:3d:c7:90:aa:da",
    "txqueuelen": 1000,
    "statistics": {
        "collisions": 0,
        "rx_frame_errors": 0,
        "tx_compressed": 0,
        "multicast": 0,
        "rx_length_errors": 0,
        "tx_dropped": 0,
        "rx_bytes": 0,
        "rx_missed_errors": 0,
        "tx_errors": 0,
        "rx_compressed": 0,
        "rx_over_errors": 0,
        "tx_fifo_errors": 0,
        "rx_crc_errors": 0,
        "rx_packets": 0,
        "tx_heartbeat_errors": 0,
        "rx_dropped": 0,
        "tx_aborted_errors": 0,
        "tx_packets": 184546,
        "rx_errors": 0,
        "tx_bytes": 17409452,
        "tx_window_errors": 0,
        "rx_fifo_errors": 0,
        "tx_carrier_errors": 0
    }
}
```

### listen

Set up a listening socket and observe incoming events:

``` bash
# ubus listen &
# ubus call network.interface.wan down
{ "network.interface": { "action": "ifdown", "interface": "wan" } }
# ubus call network.interface.wan up
{ "network.interface": { "action": "ifup", "interface": "wan" } }
{ "network.interface": { "action": "ifdown", "interface": "he" } }
{ "network.interface": { "action": "ifdown", "interface": "v6" } }
{ "network.interface": { "action": "ifup", "interface": "he" } }
{ "network.interface": { "action": "ifup", "interface": "v6" } }
```

### send

Send an event notification:

``` bash
# ubus listen &
# ubus send foo '{ "bar": "baz" }'
{ "foo": { "bar": "baz" } }
```

## Access to ubus over HTTP

There is an `uhttpd` plugin called `uhttpd-mod-ubus` that allows `ubus` calls using [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) protocol. For example this is used in [LuCI2](/docs/techref/luci2). Requests have to be sent to the `/ubus` URL (unless changed by `ubus_prefix` option) using the `POST` method. This interface uses [jsonrpc v2.0](https://www.jsonrpc.org/specification) There are a few steps that you will need to understand.

If uhttpd-mod-ubus is installed, uhttpd automatically configures it and enables it, by default at /ubus, but you can [configure this](/docs/guide-user/services/webserver/uhttpd) Also if you want to use the `/ubus` directly from a web client you need to specify `ubus_cors=1` option.

If you are using Nginx then you may try [nginx-ubus-module](https://github.com/Ansuel/nginx-ubus-module). For other web servers like Lighttpd you may use the [ubus as CGI](https://github.com/yurt-page/cgi-ubus).

See the [Postman collection](https://documenter.getpostman.com/view/5972215/TVzNHeej#154b5d84-4065-4887-a5a8-c1f3b51fe9a6) with some examples of calling UBUS over [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md)

### ACLs

While logged in via ssh, you have direct, full access to ubus. When you're accessing the `/ubus` url in uhttpd however, uhttpd first queries whether your call is allowed, and whoever is providing the ubus `session.*` namespace is in charge of implementing the access control:

``` bash
ubus call session access '{ "ubus_rpc_session": "xxxxx", "object": "requested-object", "function": "requested-method" }'
```

This happens to be `rpcd` at the moment, with the `http-json` interface, for friendly operation with browser code, but this is just one possible implementation. Because we're using rpcd to implement the ACLs at this time, this allows/requires (depending on your point of view) ACLs to be configured in `/usr/share/rpcd/acl.d/*.json`. The **names** of the files in `/usr/share/rpcd/acl.d/*.json` don't matter, but the top level keys define roles. The default ACL, listed below, **only** defines the login methods, so you can log in, but you still wouldn't be able to do anything.

``` yaml
{
        "unauthenticated": {
                "description": "Access controls for unauthenticated requests",
                "read": {
                        "ubus": {
                                "session": [ "access", "login" ]
                        }
                }
        }
}
```

An example of a complicated ACL, allowing quite fine grained access to different ubus modules and methods is [available in the Luci2 project](https://git.openwrt.org/?p=project/luci2/ui.git;a=blob;f=luci2/share/acl.d/luci2.json)

An example of a "security is for suckers" config, where a `superuser` ACL group is defined, allowing unrestricted access to everything, is shown below. This illustrates the usage of `*` definitions in the ACLs, but keep reading for better examples.

Placing this file in `/usr/share/rpcd/acl.d/superuser.json` will help you move forward to the next steps.

``` yaml
{
        "superuser": {
                "description": "Super user access role",
                "read": {
                        "ubus": {
                                "*": [ "*" ]
                        },
                        "uci": [ "*" ],
                        "file": {
                                "*": ["*"]
                        }
                },
                "write": {
                        "ubus": {
                                "*": [ "*" ]
                        },
                        "uci": [ "*" ],
                        "file": {
                                "*": ["*"]
                        },
                        "cgi-io": ["*"]
                }
        }
}
```

Below is an example of an ACL definition that only allows access to some specific ubus modules, rather than unrestricted access to everything.

``` yaml
{
        "lesssuperuser": {
                "description": "not quite as super user",
                "read": {
                        "ubus": {
                                "file": [ "*" ],
                                "log": [ "*" ],
                                "service": [ "*" ],
                        },
                },
                "write": {
                        "ubus": {
                                "file": [ "*" ],
                                "log": [ "*" ],
                                "service": [ "*" ],
                        },
                }
        }
}
```

**Note:** Before we leave this section, you may have noticed that there's both a `ubus` and a `uci` section, even though ubus has a uci method. The `uci` scope is used for the [uci api](/docs/techref/uci) provided by rpcd to allow defining per-file permissions because using the ubus scope you can only say `uci set` is allowed or not, but not specify that it is allowed to e.g. modify `/etc/config/system` but not `/etc/config/network`. If your application/ACL doesn't need UCI access, you can just leave out the UCI section altogether.

### Authentication

Now that we have an ACL that allows operations beyond just logging in, we can actually try this out. As mentioned, `rpcd` is handling this, so you need an entry in `/etc/config/rpcd`

``` bash
config login
    option username 'root'
    option password '$p$root'
    list read '*'
    list write '*'

config login
        option username 'blaer'
        option password '$p$blaer'
        list read lesssuperuser
        list write lesssuperuser
```

The `$p` magic means to look in `/etc/shadow` and the `$root` part means to use the password for the root user in that file. The list of read and write sections, those map ACL roles to user accounts. So `list read *` means the read credential of any group listed in the merged ACLs. Write implies read.

You can also use `$1$<hash>` which is a [crypt](https://en.wikipedia.org/wiki/Crypt_(Unix)) hash, using SHA1, exactly as used in `/etc/shadow`. You can generate these with `uhttpd -m secret`.

### Session management

To login and receive a session id:

``` bash
$ curl -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "00000000000000000000000000000000", "session", "login", { "username": "root", "password": "secret"  } ] }'  http://your.server.ip/ubus

{"jsonrpc":"2.0","id":1,"result":[0,{"ubus_rpc_session":"c1ed6c7b025d0caca723a816fa61b668","timeout":300,"expires":299,"acls":{"access-group":{"superuser":["read","write"],"unauthenticated":["read"]},"ubus":{"*":["*"],"session":["access","login"]},"uci":{"*":["read","write"]}},"data":{"username":"root"}}]}
```

The session id `00000000000000000000000000000000` (32 zeros) is a special null-session which only has the rights from the `unauthenticated` access group, only enabling the `session.login` ubus call. A session has a timeout that can be specified when you login, otherwise it defaults to 5 minutes.

If you ever receive a response like `{"jsonrpc":"2.0","id":1,"result":[6]}`, that is a valid jsonrpc response, 6 is the ubus code for `UBUS_STATUS_PERMISSION_DENIED` (you'll get this if you try and login before setting up the `superuser` file, or any file that gives you more rights than just being allowed to attempt logins).

To list all active sessions, try `ubus call session list`

The session timeout is automatically reset on every use. There are plans to use these sessions even for luci1, but at present, if you use this interface in a luci1 environment, you'll need to manage sessions yourself.

### Actually making calls

Now that you have a `ubus_rpc_session` you can make calls, based on your ACLs and the available ubus services. `ubus -v list` is your primary documentation on what can be done, but see the rest of this page for more information. For example, `ubus -v list file` returns

``` javascript
'file' @ff0a2c92
    "read":{"path":"String","base64":"Boolean"}
    "write":{"path":"String","data":"String","append":"Boolean","mode":"Integer","base64":"Boolean"}
    "list":{"path":"String"}
    "stat":{"path":"String"}
    "md5":{"path":"String"}
    "exec":{"command":"String","params":"Array","env":"Table"}
```

The RPC-JSON container format is:

``` javascript
{ "jsonrpc": "2.0",
  "id": <unique-id-to-identify-request>,
  "method": "call",
  "params": [
             <ubus_rpc_session>, <ubus_object>, <ubus_method>,
             { <ubus_arguments> }
            ]
}
```

The "id" key is merely echo'ed by the server, so it needs not be strictly unique, it's mainly intended for client software to easily correlate responses to previously made requests. Its type is either a string or a number, so it can be an UUID, sha1 hash, md5 sum, sequence counter, unix timestamp, etc.

An example request to read a file `/etc/board.json` which contains device info would be:

``` bash
$ curl -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "c1ed6c7b025d0caca723a816fa61b668", "file", "read", { "path": "/etc/board.json" } ] }'  http://your.server.ip/ubus
{"jsonrpc":"2.0","id":1,"result":[0,{"data":"{\n\t\"model\": {\n\t\t\"id\": \"innotek-gmbh-virtualbox\",\n\t\t\"name\": \"innotek GmbH VirtualBox\"\n\t},\n\t\"network\": {\n\t\t\"lan\": {\n\t\t\t\"ifname\": \"eth0\",\n\t\t\t\"protocol\": \"static\"\n\t\t}\n\t}\n}\n"}]}
```

Here the first param `c1ed6c7b025d0caca723a816fa61b668` is the `ubus_rpc_session` received during the login call. If you received a response like `{"jsonrpc":"2.0","id":1,"error":{"code":-32002,"message":"Access denied"}}` then probably your session token was expired and you need to request a new one.

To beautify output you can use [jq](https://stedolan.github.io/jq/) utility:

``` bash
curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "c1ed6c7b025d0caca723a816fa61b668", "file", "read", { "path": "/etc/board.json" } ] }'  http://your.server.ip/ubus | jq
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    0,
    {
      "data": "{\n\t\"model\": {\n\t\t\"id\": \"innotek-gmbh-virtualbox\",\n\t\t\"name\": \"innotek GmbH VirtualBox\"\n\t},\n\t\"network\": {\n\t\t\"lan\": {\n\t\t\t\"ifname\": \"eth0\",\n\t\t\t\"protocol\": \"static\"\n\t\t}\n\t}\n}\n"
    }
  ]
}
```

In the response JSON document in the `result[1].data` field contains escaped JSON with the `model` and `network` objects. To fetch the concrete model name you can parse the response with the [jq](https://stedolan.github.io/jq/) program:

    curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "c1ed6c7b025d0caca723a816fa61b668", "file", "read", { "path": "/etc/board.json" } ] }'  http://your.server.ip/ubus | jq -r '.result[1].data' | jq .model.name
    "innotek GmbH VirtualBox"

As you can see in the example the router model is in fact just a OpenWrt runned on [virtual machine in VirtualBox](/docs/guide-user/virtualization/virtualbox-vm).

## Lua module for ubus

This is even possible to use `ubus` in `lua` scripts. Of course it's not possible to use native libraries directly in `lua`, so an extra module has been created. It's simply called `ubus` and is a simple interface between `lua` scripts and the `ubus` (it uses `libubus` internally).

``` lua
-- Load module
require "ubus"
-- Establish connection
local conn = ubus.connect()
if not conn then
    error("Failed to connect to ubusd")
end

-- Iterate all namespaces and procedures
local namespaces = conn:objects()
for i, n in ipairs(namespaces) do
    print("namespace=" .. n)
    local signatures = conn:signatures(n)
    for p, s in pairs(signatures) do
        print("\tprocedure=" .. p)
        for k, v in pairs(s) do
            print("\t\tattribute=" .. k .. " type=" .. v)
        end
    end
end

-- Call a procedure
local status = conn:call("network.device", "status", { name = "eth0" })
for k, v in pairs(status) do
    print("key=" .. k .. " value=" .. tostring(v))
end

-- Close connection
conn:close()
```

Optional arguments to `connect()` are a path to use for sockets (pass nil to use the default) and a per call timeout value (in milliseconds)

``` lua
local conn = ubus.connect(nil, 500) -- default socket path, 500ms per call timeout
```

## Namespaces & Procedures

As explained earlier, there can be many different daemons (services) registered in `ubus`. Below you will find a list of the most common projects with namespaces, paths and procedures they provide.

**Path only contains the first context, e.g. network for network.interface.wan**

| path                                          | Description                     | Package      |
|-----------------------------------------------|---------------------------------|--------------|
| [dhcp](/docs/guide-developer/ubus/dhcp)       | dhcp server                     | odhcpd       |
| [file](/docs/guide-developer/ubus/file)       | file                            | rpcd         |
| [hostapd](/docs/guide-developer/ubus/hostapd) | acesspoints                     | wpad/hostapd |
| [iwinfo](/docs/guide-developer/ubus/iwinfo)   | wireless informations           | rpcd iwinfo  |
| [log](/docs/guide-developer/ubus/log)         | logging                         | procd        |
| [mdns](/docs/guide-developer/ubus/mdns)       | mdns avahi replacement          | mdnsd        |
| [network](/docs/guide-developer/ubus/network) | network                         | netifd       |
| [service](/docs/guide-developer/ubus/service) | init/service                    | procd        |
| [session](/docs/guide-developer/ubus/session) | Session management              | rpcd         |
| [system](/docs/guide-developer/ubus/system)   | system misc                     | procd        |
| [uci](/docs/guide-developer/ubus/uci)         | Unified Configuration Interface | rpcd         |

### procd

Project [procd: Procd system init and daemon management](/docs/techref/procd)

![system&nofooter](/page>docs/guide-developer/ubus/system&nofooter) ![service&nofooter](/page>docs/guide-developer/ubus/service&nofooter) ![log&nofooter](/page>docs/guide-developer/ubus/log&nofooter)

### netifd

Project [netifd: Network Interface Daemon](/docs/techref/netifd)

![network&nofooter](/page>docs/guide-developer/ubus/network&nofooter)

### rpcd

Project [rpcd: OpenWrt ubus RPC daemon for backend server](/docs/techref/rpcd) is a set of small plugins providing sets of `ubus` procedures in separated namespaces. These plugins are not strictly related to any particular software (like `netifd` or `dhcp`) so it wasn't worth it to implement them as separated projects. rpcd and the desired plugins must be available or installed via opkg. After installing remember to enable and start the service via `service rpcd enable` and `service rpcd start` .

![file&nofooter](/page>docs/guide-developer/ubus/file&nofooter) ![iwinfo&nofooter](/page>docs/guide-developer/ubus/iwinfo&nofooter)

Always included in `rpcd`:

![session&nofooter](/page>docs/guide-developer/ubus/session&nofooter) ![uci&nofooter](/page>docs/guide-developer/ubus/uci&nofooter)

## What's the difference between ubus vs dbus?

[D-Bus](https://en.wikipedia.org/wiki/D-Bus) is bloated, its C API is very annoying to use and requires writing large amounts of boilerplate code. In fact, the pure C API is so annoying that its own API documentation states: "If you use this low-level API directly, you're signing up for some pain."

`ubus` is tiny and has the advantage of being easy to use from regular C code, as well as automatically making all exported API functionality also available to shell scripts with no extra effort.

## Examples

### FHEM

#### User mapping

In this example we map username `root` to `fhem_acl` for [FHEM](/docs/guide-user/services/automation/fhem) server. Edit `/etc/config/rpcd`:

``` bash
# /etc/config/rpcd
config login
    option username 'root'
    option password '$p$root'
    list read '*'
    list write '*'

config login
    option username 'fhem'
        #
        # '$p$<username> => reference to user passowrd on /etc/shadow
        # '$1$<hash>' => crypt() hash, using SHA1. generate via 'uhttpd -m fhem'
        #
        # password: fhem
        #
    option password '$1$$xEODf2fNSQ0ArfkJu4L2i1'
    #
        # map username to rpcd acl name "fhem_acl"
        #
        list read 'fhem_acl'
    list write ''
```

Then reload rpcd config:

``` bash
uci commit rpcd
```

#### User ACL

All files under `/usr/share/rpcd/acl.d/` will be merge by `rpcd` to one config file!!

``` bash
ubus call hostapd.wlan0 get_clients
ubus call hostapd.wlan1 get_clients
```

Example permissions to run ubus calls remote by fhem over http/json.

``` yaml
{
        "fhem_acl": {
                "description": "FHEM PRESENCE Module User.. https://github.com/janLo/OpenWRT-Wifi-Clients-POC",
                "read": {
                        "ubus": {
                                "hostapd.wlan0": [ "get_clients" ],
                                "hostapd.wlan1": [ "get_clients" ]
                        }
                }
        }
}
```

FHEM Server - show all connected wireless clients:

``` bash
$ python wifi_clients.py
Usage: wifi_clients.py.orig <OpenWrt_Host> <User> <Pass> <WiFi_1> [<WiFi2> ...]
$ python wifi_clients.py 192.168.1.71 fhem fhem wlan0 wlan1
c8:f6:50:e1:a9:10, 2c:f0:a2:e2:c0:15, 8c:a9:82:f1:9c:2a, 7c:c3:a1:b8:d2:1e, 64:9a:be:6a:6c:13, 00:1d:63:a3:8f:4a
```

### Getting firmware version

Get firmware version with [JSON RPC](https://github.com/openwrt/luci/wiki/JsonRpcHowTo).

``` bash
luci_rpc() {
local LIB="${1}"
local DATA="${2}"
local URL="https://${HOST}/\
cgi-bin/luci/rpc/${LIB}?auth=${TOKEN}"
curl -s -k -d "${DATA}" "${URL}" \
| jsonfilter -e "$['result']"
}
HOST="localhost"
USER="root"
PASS=""
DATA="{ \"id\": 1, \"method\": \"login\",
\"params\": [ \"${USER}\", \"${PASS}\" ] }"
TOKEN="$(luci_rpc auth "${DATA}")"
DATA="{ \"id\": 2, \"method\": \"exec\",
\"params\": [ \"ubus call system board\" ] }"
VERSION="$(luci_rpc sys "${DATA}" \
| jsonfilter -e "$['release']['version']")"
echo "${VERSION}"
```

Get firmware version with ubus RPC.

``` bash
ubus_rpc() {
local DATA="${1}"
local URL="https://${HOST}/ubus"
curl -s -k -d "${DATA}" "${URL}" \
| jsonfilter -e "$['result']"
}
HOST="localhost"
USER="root"
PASS=""
DATA="{ 'jsonrpc': '2.0', 'id': 1, 'method': 'call',
'params': [ '00000000000000000000000000000000', 'session',
'login', { 'username': '${USER}', 'password': '${PASS}' } ] }"
SESSION="$(ubus_rpc "${DATA}" \
| jsonfilter -e "$[*]['ubus_rpc_session']")"
DATA="{ 'jsonrpc': '2.0', 'id': 2, 'method': 'call',
'params': [ '${SESSION}', 'system', 'board', {} ] }"
VERSION="$(ubus_rpc "${DATA}" \
| jsonfilter -e "$[*]['release']['version']")"
echo "${VERSION}"
```
