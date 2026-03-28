---
title: 'ucode module: rtnl'
module: ucode
origin_type: c_source
token_count: 7614
source_file: L1-raw/ucode/c_source-api-module-rtnl.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_commit: unknown
source_url: https://github.com/nicowillis/ucode/blob/unknown/lib/rtnl.c
source_locator: lib/rtnl.c
language: c
ai_summary: Provides rtnetlink interface bindings for ucode to enumerate and monitor kernel network state. Implements request() to send RTM_GETLINK, RTM_GETROUTE, RTM_GETNEIGH, and RTM_GETADDR queries and receive structured attribute dictionaries from the kernel. Enables subscription to netlink multicast groups for real-time interface and route change notifications.
ai_when_to_use: Use when a ucode service needs kernel-level network interface state, live route table changes, or ARP/NDP neighbor tables without invoking the ip command or spawning subprocesses.
ai_related_topics:
- rtnl.request
- rtnl.error
- RTM_GETLINK
- RTM_GETROUTE
- RTM_GETNEIGH
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