---
title: odhcpd
module: wiki
origin_type: wiki_page
token_count: 5894
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-odhcpd.md
last_pipeline_run: '2026-03-09T18:12:55.650305+00:00'
language: text
---
# odhcpd

See also: [odhcpd upstream documentation](https://github.com/openwrt/odhcpd/blob/master/README.md)

odhcpd is an embedded DHCP/DHCPv6/RA server & NDP relay.

## Abstract

odhcpd is a daemon for serving and relaying IP management protocols to configure clients and downstream routers. It tries to follow the [RFC 6204](https://datatracker.ietf.org/doc/html/rfc6204) requirements for IPv6 home routers.

odhcpd provides server services for DHCP, RA, stateless SLAAC and stateful DHCPv6, prefix delegation and can be used to relay RA, DHCPv6 and NDP between routed (non-bridged) interfaces in case no delegated prefixes are available.

## Features

### Router Discovery (RD)

Router Discovery (RD) support (solicitations and advertisements) with 2 modes of operation:

1.  RD Server mode: Router Discovery (RD) server for slave interfaces:
    1.  Automatic detection of prefixes, delegated prefix, default routes and MTU.
    2.  Automatic re-announcement of any changes in either prefixes or routes.
2.  RD Relay mode: Router Discovery (RD) relay between master and slave interfaces.
    1.  Supports rewriting of the announced DNS server addresses.

### DHCPv6

DHCPv6 support with 2 modes of operation:

1.  DHCPv6 Server mode: stateless, stateful and Prefix Delegation (PD) server mode:
    1.  Stateless and stateful address assignment.
    2.  Prefix delegation support.
    3.  Dynamic reconfiguration of any changes in Prefix Delegation.
    4.  Hostname detection and hosts-file creation.
2.  DHCPv6 Relay mode: A mostly standards-compliant DHCPv6-relay:
    1.  Supports rewriting of the announced DNS server addresses.

### DHCPv4

1.  Stateless and stateful DHCPv4 server mode.

### Neighbor Discovery Proxy (NDP)

Proxy for Neighbor Discovery solicitation and advertisement messages (NDP):

1.  Supports auto-learning of routes to the local routing table.
2.  Supports marking interfaces as "external".

Interfaces marked as "external" will not receive any proxyied NDP content and are only served with NDP for Duplicate Address Detection (DAD) and traffic to the router itself.

:!: Interfaces marked as external need additional firewall rules for security!

## Configuration

odhcpd uses a UCI configuration file in `/etc/config/dhcp` for configuration and may also receive information from ubus.

### odhcpd section

Configuration for the odhcp daemon.

| Name           | Type    | Default                   | Description                                                                                    |
|:---------------|:--------|:--------------------------|:-----------------------------------------------------------------------------------------------|
| `legacy`       | boolean | `0`                       | Enable DHCPv4 if the 'dhcp' section contains a `start` option, but no `dhcpv4` option set.     |
| `maindhcp`     | boolean | `0`                       | Use odhcpd as the main DHCPv4 service.                                                         |
| `leasefile`    | string  | `/tmp/odhcpd.leases`      | Location of the lease/hostfile for DHCPv4 and DHCPv6.                                          |
| `leasetrigger` | string  | `/usr/sbin/odhcpd-update` | Location of the lease trigger script.                                                          |
| `hostsdir`     | string  | `/tmp/hosts`              | Directory to store hosts files (IP address to hostname mapping) in. Used by e.g. dnsmasq.      |
| `piodir`       | string  | `/tmp/odhcpd-piodir`      | Directory to store IPv6 prefix information (to detect stale prefixes, see RFC9096, §3.5).      |
| `loglevel`     | integer | `4`                       | Syslog level priority (0-7). 0=emer, 1=alert, 2=crit, 3=err, 4=warn, 5=notice, 6=info, 7=debug |
| `enable_tz`    | boolean | `1`                       | Set to `0` to disable sending option 41 and 42 timezone info to clients that request them      |

\<WRAP center round important 80%\> **RFC9096 § 3.5 SLAAC compliance relies on the `piodir` option, \<color \#ed1c24\>which may wear out the flash under certain conditions\</color\>.  
For example: ISPs with dynamic IPv6 prefixes which disconnect the clients every X hours.  
\<color \#ed1c24\>Therefore, setting `dhcp.odhcpd.piodir` to persistent storage in the router flash is not advisable\</color\> and should be set to other kinds of persistent storage such as USBs, SDs, NVMEs...  
In order to prevent wearing out the router flash it's set to ephemeral storage by default:  
`uci set dhcp.odhcpd.piodir=/tmp/odhcpd-piodir`  
`uci commit dhcp`**  
  
If dhcp.odhcpd.piodir is set to persistent storage, you should also add that directory to sysupgrade.conf in order to preserve the PIOs when OpenWrt is upgraded.  
`$(uci -q get dhcp.odhcpd.piodir) >> /etc/sysupgrade.conf`  
\</WRAP\>

### dhcp section

Configuration for DHCPv4, DHCPv6, RA and NDP services.

\<sortable\>

<table>
<thead>
<tr class="header">
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Required</th>
<th style="text-align: left;">Default</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>interface</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>&lt;name of UCI section&gt;</code></td>
<td style="text-align: left;">Logical OpenWrt interface.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ifname</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>&lt;resolved from logical&gt;</code></td>
<td style="text-align: left;">Physical network interface.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>networkid</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>&lt;same as ifname&gt;</code></td>
<td style="text-align: left;">Alias of <code>ifname</code> for compatibility.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ignore</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">Do not serve this interface unless overridden by <code>ra</code>, <code>ndp</code>, <code>dhcpv4</code> or <code>dhcpv6</code> options.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>master</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">Is a master interface for relaying.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>disabled</code></td>
<td style="text-align: left;">Router Advert service. Set to <code>disabled</code>, <code>server</code>, <code>relay</code> or <code>hybrid</code>.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>dhcpv6</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>disabled</code></td>
<td style="text-align: left;">DHCPv6 service. Set to <code>disabled</code>, <code>server</code>, <code>relay</code> or <code>hybrid</code>.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dhcpv4</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>disabled</code></td>
<td style="text-align: left;">DHCPv4 service. Set to <code>disabled</code> or <code>server</code>.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ndp</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>disabled</code></td>
<td style="text-align: left;">Neighbor Discovery Proxy. Set to <code>disabled</code>, <code>relay</code> or <code>hybrid</code>.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dynamicdhcp</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">Leases for DHCPv4 and DHCPv6 are created dynamically.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>dhcpv4_forcereconf</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">Force reconfiguration by sending force renew message even if the client did not include the force renew nonce capability option (<a href="https://datatracker.ietf.org/doc/html/rfc6704">RFC 6704</a>).</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dhcpv6_assignall</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">Assign all viable DHCPv6 addresses in statefull mode. If disabled only the DHCPv6 address having the longest preferred lifetime is assigned.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>dhcpv6_hostidlength</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>12</code></td>
<td style="text-align: left;">Host ID length of dynamically created leases, allowed values: 12 - 64 (bits).</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dhcpv6_na</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">DHCPv6 stateful addressing hands out IA_NA - Internet Address - Network Address.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>dhcpv6_pd</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">DHCPv6 stateful addressing hands out IA_PD - Internet Address - Prefix Delegation.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>router</code></td>
<td style="text-align: left;">list</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>&lt;local address&gt;</code></td>
<td style="text-align: left;">Routers to announce accepts IPv4 only.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>dns</code></td>
<td style="text-align: left;">list</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>&lt;local address&gt;</code></td>
<td style="text-align: left;">DNS servers to announce on the network. IPv4 and IPv6 addresses are accepted.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dns_service</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">Announce the address of interface as DNS service if the list of DNS is empty.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>domain</code></td>
<td style="text-align: left;">list</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>&lt;local search domain&gt;</code></td>
<td style="text-align: left;">Search domains to announce on the network.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>leasetime</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>12h</code></td>
<td style="text-align: left;">DHCPv4 address leasetime</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>start</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>100</code></td>
<td style="text-align: left;">Starting address of the DHCPv4 pool.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>limit</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>150</code></td>
<td style="text-align: left;">Number of addresses in the DHCPv4 pool.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>preferred_lifetime</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>12h</code></td>
<td style="text-align: left;">Value for the preferred lifetime for a prefix.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_default</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">Override default route. Set to <code>0</code> (default), <code>1</code> (ignore, no public address) or <code>2</code> (ignore all).</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ra_flags</code></td>
<td style="text-align: left;">list</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>other-config</code></td>
<td style="text-align: left;">List of RA flags to be advertised in RA messages:<br />
<code>managed-config</code> - get address information from DHCPv6 server. If this flag is set, <code>other-config</code> flag is redundant.<br />
<code>other-config</code> - get other configuration from DHCPv6 server (such as DNS servers). See <a href="https://datatracker.ietf.org/doc/html/rfc4861#section-4.2">here</a> for details.<br />
<code>home-agent</code> - see <a href="https://datatracker.ietf.org/doc/html/rfc3775#section-7.1">here</a> for details.<br />
<code>none</code>.<br />
OpenWrt since version 21.02 configures <code>managed-config</code> and <code>other-config</code> <a href="https://github.com/openwrt/openwrt/blob/openwrt-21.02/package/network/services/odhcpd/files/odhcpd.defaults#L49-L50">by default</a>.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_slaac</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">Announce SLAAC for a prefix (that is, set the A flag in RA messages).</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ra_management</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;">no</td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">:!: This option is <a href="commit&gt;?p=project/odhcpd.git;a=commit;h=e73bf11dee1073aaaddc0dc67ca8c7d75ae3c6ad">deprecated</a>. Use <code>ra_flags</code> and <code>ra_slaac</code> options instead.<br />
RA management mode: no M-Flag but A-Flag and ra_slaac is ture (<code>0</code>) , both M and A flags and ra_slaac is ture(<code>1</code>), both M and A flags and ra_slaac is false (<code>2</code>)</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_offlink</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">Announce prefixes off-link.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ra_preference</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>medium</code></td>
<td style="text-align: left;">Route preference <code>medium</code>, <code>high</code> or <code>low</code>.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_maxinterval</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>600</code></td>
<td style="text-align: left;">Maximum time allowed between sending unsolicited Router Advertisements (RA).</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ra_mininterval</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>200</code></td>
<td style="text-align: left;">Minimum time allowed between sending unsolicited Router Advertisements (RA).</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_lifetime</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1800</code></td>
<td style="text-align: left;">Router Lifetime published in Router Advertisement (RA) messages.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ra_useleasetime</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">If set, the configured DHCPv4 <code>leasetime</code> is used both as limit for the preferred and valid lifetime of an IPv6 prefix.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_reachabletime</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">Reachable Time in milliseconds to be published in Router Advertisement (RA) messages'.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ra_retranstime</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">Retransmit Time in milliseconds to be published in Router Advertisment (RA) messages.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_hoplimit</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">The maximum hops to be published in Router Advertisement (RA) messages.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ra_mtu</code></td>
<td style="text-align: left;">integer</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">The MTU to be published in Router Advertisement (RA) messages.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ra_dns</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">Announce DNS configuration in RA messages (<a href="https://datatracker.ietf.org/doc/html/rfc8106">RFC 8106</a>).</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ndproxy_routing</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>1</code></td>
<td style="text-align: left;">Learn routes from NDP.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ndproxy_slave</code></td>
<td style="text-align: left;">boolean</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>0</code></td>
<td style="text-align: left;">NDProxy external slave.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ndproxy_static</code></td>
<td style="text-align: left;">list</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">Static NDProxy prefixes.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>prefix_filter</code></td>
<td style="text-align: left;">string</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"><code>::/0</code></td>
<td style="text-align: left;">Only advertise on-link prefixes within the provided IPv6 prefix. Others are filtered out.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>ntp</code></td>
<td style="text-align: left;">list</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">DHCPv6 stateful option 56 to Announce NTP servers</td>
</tr>
</tbody>
</table>

\</sortable\>

### host section

The `host` section is where static leases are defined.

| Name        | Type   | Required | Default  | Description          |
|-------------|--------|----------|----------|----------------------|
| `ip`        | string | yes      | *(none)* | IP address to lease  |
| `mac`       | string | no       | *(none)* | MAC address          |
| `duid`      | string | no       | *(none)* | DUID in base16       |
| `hostid`    | string | no       | *(none)* | IPv6 host identifier |
| `name`      | string | no       | *(none)* | Hostname             |
| `leasetime` | string | no       | *(none)* | DHCPv4/v6 leasetime  |

Example `hostid='105ee0badc0de`' =\> IPv6 '::1:5ee:bad:c0de'

## ubus API

Replace dnsmasq with odhcpd to access IPv4 leases.

``` bash
ubus -v list dhcp
ubus call dhcp ipv4leases
ubus call dhcp ipv6leases
ubus call dhcp ipv6ra
```

## Compiling

odhcpd uses cmake.

``` bash
# Prepare
cmake .

# Build/install
make
make install

# Build DEB/RPM packages
make package
```