---
title: Network scripts
module: wiki
origin_type: wiki_page
token_count: 3764
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-network-scripting.md
last_pipeline_run: '2026-03-23T22:14:22.429226+00:00'
language: text
---
# Network scripts

netifd can (probably) bring up a wired, static ip configuration without shell scripts. For everything else (PPPoE or 3G) it needs *protocol handlers* implemented as sets of shell functions.

## Writing protocol handlers

Each protocol handler is a shell script in `/lib/netifd/proto/`. It is run (or maybe sourced) when netifd daemon starts. Changes made to the scripts do not take effect until netifd restarts. The name of the file usually matches `option proto` in `/etc/config/network`.

To be able to access the network functions, the script needs to include the necessary shell scripts at the beginning:

``` bash
#!/bin/sh

[ -n "$INCLUDE_ONLY" ] || {
    . /lib/functions.sh
    . ../netifd-proto.sh
    init_proto "$@"
}
```

Current working directory is `/lib/netifd/proto/` when the handler is sourced.

At the end of the script a handler should register itself by calling `add_protocol protocolname`.

A handler should at least define 2 shell functions: `proto_protocolname_init_config` and `proto_protocolname_setup`.

netifd then calls the script with a JSON blob of the configuration parameters:

    /bin/sh ..../<protocolname>.sh <protocolname> setup <interfacename> '{"proto":"<protocolname>","a":true,"b":["192.0.2.10"],...}'

    ubus call network.interface notify_proto '{ "action": 0, "link-up": true, "keep": false, "interface": "<interfacename>" }'

### init_config

The main purpose of this function is to let netifd know which parameters this protocol has. These parameters stored in `/etc/config/network` are referenced for use by the proto handler. This is what netifd monitors. If any of these parameters change via rpcd/ubus, netifd can trigger a reload or restart of the interface whose parameters have changed.

``` bash
proto_protocolname_init_config() {
    proto_config_add_string "stringparam"
    proto_config_add_int "intparam"
    proto_config_add_boolean "boolparam"
    ...
}
```

e.g. It will 'validate' the following: i.e. monitor them for changes, and update the interface with them when they do.

``` bash
config interface 'foo'
    option proto 'protocolname'
    option stringparam 'f00'
    option intparam '12345'
    option boolparam '1'
    ...
}
```

As you may have noticed, this is good for monitoring properties of an interface. What if an interface has various peer type entries also in the network config? netifd won't see when any of those peer entries related to the interface have changed. It doesn't 'validate' those.

This is why changes to peers and most WireGuard interface properties are not put into operation until a manual interface restart.

One can employ a work-around: have the proto script 'validate' an option which stores a hash of the peers, a hash which is simultaneously updated when peers are modified and written e.g. in luci, so when the hash of the peers is saved, netifd will notice the interface property change and reload the interface. Note that changes via uci command line go unnoticed by netifd.

Another approach is to use a procd handler which can monitor when changes occur to `/etc/config/network` in general, and trigger a reload of the interface.

### Setup

The setup procedure implements the actual protocol specific configuration logic and interface bring-up.

When called, one or two parameters are passed:

1.  Config (the UCI section name suitable for `config_get` calls)
2.  Interface name (only if `no_device=0`)

``` bash
proto_protocolname_setup() {
    local config="$1"
    # set up the interface
}
```

This function must be implemented by any protocol back-end.

There's usually no need to call `ifconfig iface up` at the end of this function. If `no_device=0`, netifd won't even try to start our profile until the device is already up. It waits for `operstate=up` and `carrier=1`, then starts the profile.

If `no_device=1`, netifd will bring it up, when it receives a notification from us:

``` bash
proto_protocolname_setup () {
    ...
    proto_init_update "$iface" 1
    proto_send_update "$config"
    ...
}
```

This only works once, however. If someone called `ifconfig iface down`, netifd won't try to bring it up again (at least in BB), so just in case you may put the "up" command in the function.

### renew

The renew procedure implements logic for when an interface or daemon config has changed and it might need a restart or reload, or SIGHUP to reload its config.

When called, one or two parameters are passed:

1.  Config (the UCI section name suitable for `config_get` calls)
2.  Interface name (only if `no_device=0`)

``` bash
proto_protocolname_renew() {
    local config="$1"
    # reload the interface
}
```

This function can be implemented by any protocol back-end.

### Teardown

Protocols that need special shutdown handling, for example to kill associated daemons, may implement a stop procedure. This procedure is called when an interface is brought down before the associated UCI state is cleared.

The function is called when we do `ifdown profile` or when `no_device=0` and netifd detects link connectivity loss.

When called, two parameters are passed:

1.  Config (the UCI section name suitable for `config_get` calls)
2.  interface (the network device)

``` bash
proto_protocolname_teardown() {
    local config="$1"
    local iface="$2"
    # tear down the interface
}
```

This function is optional.

### Coldplug

By default, only interfaces present in `/proc/net/dev`, like *eth0*, are brought up on boot. Protocols which use virtual interfaces must set two variables at the beginning of init_config.

``` bash
proto_protocolname_init_config() {
    no_device=1
    available=1
    ...
}
```

### Keep config

Use `proto_set_keep()` to maintain configuration across updates, by keeping the proto process alive.

``` bash
proto_set_keep 1
```

An example in context:

``` bash
...
    proto_init_update ppp0 1
    proto_set_keep 1
    proto_add_ipv4_address "192.168.2.1" 32
    proto_add_dns_server "192.168.2.2"
    proto_add_ipv4_route "0.0.0.0" 0 192.168.2.2
    proto_add_data
    json_add_string "ppp-type" "pppoe"
    proto_close_data
    proto_send_update "$interface"

    proto_init_update ppp0 1
    proto_set_keep 1
    proto_add_ipv6_address "fe80::2" 64
    proto_add_ipv6_route "::0" 0 "fe80::1"
    proto_add_data
    json_add_string "ppp-type" "pppoe"
    proto_close_data
    proto_send_update "$interface"
...
```

### Debugging

- STDERR in protos is redirected to the syslog. `echo "message" > 2>&1` can be used to print.
- As `set -x` also prints to STDERR, it can be used to trace which commands are called inside the proto. However this is very spammy.
- There is a pending patch: <https://patchwork.ozlabs.org/project/openwrt/patch/20201229233319.164640-1-me@irrelefant.net/>.

### Available proto flags

Flags can be added to a proto handler in `proto_protoname_init_config`, by setting their value to `1`. The information about all loaded protocols can be obtained by calling *ubus call network get_proto_handlers*.

| Name | Name in *ubus call network get_proto_handlers* | Meaning |
| --- | --- | --- |
|   | force_link_default | Instruct netifd to prefer link-based default routing behavior for the interface (affects how link state influences routing selection). |
|   | immediate | Protocol should be started/processed immediately upon attach instead of waiting for link or other conditions (useful for static/always-on protos). |
| available | init_available | Indicates the protocol handler is present/usable on the system (1 = available, 0 = not). |
| lasterror | last_error | True when the last setup attempt failed and the handler wants to expose that state. |
| no_device | no_device | Protocol does not create/use a kernel network device. Example: PPP uses a logical proto and does not provide a physical device. |
| no_device_config | no_device_config | Protocol has no device-specific configuration (config applies to the protocol itself). |
| no_proto_task | no_task | Protocol does not spawn a long-running background task. Mainly for protocols like xl2tpd in which control commands are sent to another daemon xl2tpd to start L2TP negotiation and pppd process who is not under netifd's control as proto_task as is the case in other ppp related protocols like pppoe, pptp, etc.; As an example, WireGuard is built into the kernel and has no running daemon, so it has no daemon or 'proto task'. |
| peer_detect | peer_detect | netifd calls renew when it detects that a \_peer in the config changed. |
| renew_handler | renew_available | Protocol implements the "renew" action/handler `proto_*_renew()`, which can be called by netifd. |
| teardown_on_l3_link_down | teardown_on_l3_link_down | If the l3 device receives state down (e.g. ifdown), call the `proto_*_teardown()`. Mainly for shell protocols that have no_proto_task so that we can still do teardown and setup of the interface on l3_dev link lost instead of depending on the running state of proto_task |

### Error codes

If errors for interfaces occur, the json object in *ifstatus interfacename* or in *ubus call network.interface dump* have an attribute *"error"*. If there are no errors, this attribute is not existing.

| CODE                | Meaning                                                                                                                                                                                                                                                                                                                                                                                        |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| NO_DEVICE           | The configured device in ifname is not found.                                                                                                                                                                                                                                                                                                                                                  |
| DEVICE_CLAIM_FAILED | One of the reasons for this is, that the device configured by ifname does not exist. Usually this would result in NO_DEVICE as the device is only claimed when it is available. However when the proto flags *available=1* and *no_device=0* are set, the device specified by ifname is tried to be claimed directly. TBD: Is this the only case? Is this correct? |
| SETUP_FAILED        | TBD                                                                                                                                                                                                                                                                                                                                                                |

Custom error codes can be thrown from the proto scripts aswell. This is done via `proto_notify_error "$config" MY_CUSTOM_ERROR_ID`.

### How does it work internally?

``` bash
init_proto $proto $cmd $interface $data $ifname
```

This function takes all all arguments from the *proto.sh* file, interprets them and then defines the implementation of *add_protocol()*.

If `$cmd = "dump"` then *add_protocol()* will do the following:

- A json output dump of the results of `proto_protocolname_init_config` will be printed.
- Other parameters than `$cmd` will be ignored.

If `$cmd ∈ {"setup", "teardown", "renew"}` *add_protocol()* will do the following:

- If `$proto ≠ protoname` nothing will be done.
- `$data` is loaded via *json_load*
- `proto_protoname_... $interface $ifname` will be called.

Otherwise the script will fail with something like:

- `add_protocol: not found`

## API

The following functions are defined in `/lib/netifd/netifd-proto.sh`.

### netifd functions

#### initialization functions

- `add_protocol`
- `init_proto`
- `proto_config_add_boolean`
- `proto_config_add_int`
- `proto_config_add_string`
- `proto_config_add_array` (for uci config ''list xxx 'value' '' types

#### notification functions

Note: some of these function exit immediately. These functions are dispatched to ubus and arrive [here](commit>?p=project/netifd.git;a=blob;f=proto-shell.c;hb=c00c8335d6188daa326ecfe5a62da15a9b9987e1#l792)

- `proto_block_restart $interface`
- `proto_init_update $ifname $up [$external]`
- `proto_kill_command $interface [$signal]`
- `proto_notify_error $interface $str1 [$str2] [$str3] ...`
- `proto_run_command`

We can start a daemon that maintains the connection asynchronously by calling `proto_run_command "$config" custom_script`. Netifd remembers its pid. It can be killed manually by calling `proto_kill_command "$config"`. Netifd can automatically kill it, when the profile stopped.

\* `proto_add_host_dependency`

It seems to avoid race conditions in protos. We can register the following type of dependencies by calling:

- `proto_add_host_dependency "$config" "$host" "$ifname"`
- `proto_add_host_dependency "$config" \'\' "$ifname"` (only wait for an iface)
- (maybe more?)

Only if `$iface` is up, the corresponding `$config` will be loaded. So we need another proto to be completed, we can use this here.

From some observations I think it looks like technically the `$config` is initially loaded, then the `proto_add_host_dependency` is called inside the proto handler and then the `$config` is removed again until `$iface` is available, up, ... or so. However, currently I do not know where to find the source code, so this is only a vague idea of what happens.

- ''proto_send_update \$interface ''
- '' proto_set_available \$interface \$state''

### common functions

- '' json_add_string ''
- '' json_dump ''
- '' json_init ''
- '' [json_get_var](../../wiki/chunked-reference/wiki_page-guide-developer-jshn.md) ''
- '' json_get_vars ''

## Examples

[Network functions](https://github.com/openwrt/openwrt/blob/master/package/base-files/files/lib/functions/network.sh) rely on runtime configuration and can return unexpected result if you are using MWAN or VPN. Replace automatic WAN detection with explicit interface definition if necessary.

### Get LAN address

``` bash
# Runtime configuration
NET_IF="lan"
. /lib/functions/network.sh
network_flush_cache
network_get_ipaddr NET_ADDR "${NET_IF}"
network_get_ipaddr6 NET_ADDR6 "${NET_IF}"
echo "${NET_ADDR}"
echo "${NET_ADDR6}"
```

### Get WAN interface

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
echo "${NET_IF}"
echo "${NET_IF6}"
```

### Get WAN L2 device

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_physdev NET_L2D "${NET_IF}"
network_get_physdev NET_L2D6 "${NET_IF6}"
echo "${NET_L2D}"
echo "${NET_L2D6}"
```

### Get WAN L3 device

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_device NET_L3D "${NET_IF}"
network_get_device NET_L3D6 "${NET_IF6}"
echo "${NET_L3D}"
echo "${NET_L3D6}"

# Persistent configuration
uci get network.wan.device
uci get network.wan6.device
```

### Get WAN address

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_ipaddr NET_ADDR "${NET_IF}"
network_get_ipaddr6 NET_ADDR6 "${NET_IF6}"
echo "${NET_ADDR}"
echo "${NET_ADDR6}"

# Persistent static configuration
uci get network.wan.ipaddr
uci get network.wan6.ip6addr
```

### Get WAN gateway

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_gateway NET_GW "${NET_IF}"
network_get_gateway6 NET_GW6 "${NET_IF6}"
echo "${NET_GW}"
echo "${NET_GW6}"

# Persistent static configuration
uci get network.wan.gateway
uci get network.wan6.ip6gw
```

### Get WAN prefix

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan6 NET_IF6
network_get_prefix6 NET_PFX6 "${NET_IF6}"
echo "${NET_PFX6}"

# Persistent static configuration
uci get network.wan6.ip6prefix
```

### Get WAN gateway for unmanaged default route

``` bash
# Runtime configuration
ubus call network.interface dump \
| jsonfilter -e "$['interface'][*]['inactive']
['route'][*]['target'='0.0.0.0','mask'='0','nexthop']"
```
