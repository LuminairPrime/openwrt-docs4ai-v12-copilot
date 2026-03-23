---
module: wiki
total_token_count: 4858
section_count: 4
is_monolithic: false
is_sharded_part: true
part_number: 3
part_count: 3
generated: '2026-03-23T22:14:37.218591+00:00'
---

# wiki Bundled Reference (Part 3 of 3)

> **Contains:** 4 documents
> **Tokens:** ~4858 (cl100k_base)
> **Index:** [./bundled-reference.md](./bundled-reference.md)

---

# unetd

unetd is a WireGuard based VPN daemon that simplifies creating and managing fully-meshed VPN connections between OpenWrt routers.

Source: [project/unetd.git](commit>project/unetd.git)

## Features

      * Splits network setup into network config (shared across all participating nodes) and local config (limited mostly to local private key, public signing device key, optionally tunnel device names)
      * Supports automatic replication of peer IP addresses
      * Supports automatic replication of network config updates
        * network config data is secure and protected by a Ed25519 signature
        * network config data replication is encrypted and only available to members of the network, even during bootstrap
      * Fully meshed (all nodes connect to each other directly unless configured otherwise)
      * Supports automatic VXLAN setup with multiple peers
        * automatically installs eBPF program to deal with MTU limitations and avoid fragmentation
      * Automatic setup of routes / IP addresses based on network config data
      * Supports direct connection through double-NAT, as long as the network has one node with a public IP address
      * Simple CLI for creating and updating networks between OpenWrt hosts with very few commands
      * Builds and runs on regular Linux distributions as well, and also macOS (with some limitations)
      * Automatically assigns an IPv6 address for each host, which is generated from the host public key
      * writes a host file containing entries for all configured hosts
        * can be used with dnsmasq for local lookup
        * configurable domain suffix
      * allows creating freeform service definitions, which allows services to query member IP addresses using ubus
      * Supports peer discovery via BitTorrent 'Mainline' DHT, which works even through double-NAT

## Building

### OpenWrt

TBC

### Linux

The following build dependencies are required:

      * cmake, pkg-config
      * libelf-dev, zlib1g-dev, libjson-c-dev

To build:

    git clone https://git.openwrt.org/project/unetd.git
    cd unetd
    ./build.sh

## Example setup

#### Preparation

This set of example commands assumes two OpenWRT routers with the IP addresses `192.168.1.13` and `192.168.1.15` which have **not** been configured for unetd yet, each has `unetd`, `unet-cli` and `unet-tool` installed. `vxlan` (and its implied `kmod-vxlan`) are also installed. The assumption here is that the local host, here say `192.168.1.2` has these installed, and also forms a unet node.

Note: `unetd` is not yet capable of installing these prerequisites above via `opkg`.

#### Example

This creates a new JSON file `test.json` locally and also generates a signing key in `test.json.key` locally (if it doesn't exist already):

    # unet-cli test.json create

Result:

    test.json:
    {
        "config": {
            "port": 51830,
            "keepalive": 10,
            "peer-exchange-port": 51831
        },
        "hosts": {
        },
        "services": {
        }
    }

This creates a VXLAN tunnel definition in `test.json` and predicates hosts that are to be members of it via the `ap` group:

    # unet-cli test.json add-service l2-tunnel type=vxlan members=@ap

Result:

    test.json:
    {
        ...
        "services": {
            "l2-tunnel": {
                "config": {
                },
                "members": [
                    "@ap"
                ],
                "type": "vxlan"
            }
        }
    }

This connects to 192.168.1.13 over SSH, and on 192.168.1.13, generates an unetd interface named `unet`, along with new host keys, puts in the signing key and also tells it to create the `vx0` VXLAN device connected to the `l2-tunnel` service description we created in the last command, storing its public key in the local `test.json`, along with its endpoint address `192.168.1.13`:

    # unet-cli test.json add-ssh-host ap1 root@192.168.1.13 endpoint=192.168.1.13 tunnels=vx0:l2-tunnel groups=ap

Note: you will authenticate via SSH, either user:pass or key based, if that was set up in advance.

Result:

    test.json:
    {
        ...
        "hosts": {
            "ap1": {
                "key": "....=",
                "endpoint": "192.168.1.13",
                "groups": [
                    "ap"
                ]
            }
        },
        ...
    }

This does the same for the other host:

    # unet-cli test.json add-ssh-host ap2 root@192.168.1.15 endpoint=192.168.1.15 tunnels=vx0:l2-tunnel groups=ap

Result:

    test.json:
    {
        ...
        "hosts": {
            ...
            "ap2": {
                "key": "...=",
                "endpoint": "192.168.178.1",
                "groups": [
                    "ap"
                ]
            }
        },
        ...
    }

This signs the network data and uploads it to unetd running on 192.168.1.13:

    # unet-cli test.json sign upload=192.168.1.13

By now, uploading the data to one of the two hosts is enough, because once it (192.168.1.13) has processed the update, it (192.168.1.13) will find the endpoint address of the other host (192.168.1.15) and sync the network data with it automatically. After that last command, the unetd network should be up on both sides, and the VXLAN tunnel created as well.

## Configuration

### UCI network interface

Configuration of a `interface` section in /etc/config/network for unetd.

| Name       | Type    | Required | Description                                                                                                          |
|------------|---------|----------|----------------------------------------------------------------------------------------------------------------------|
| `proto`    | string  | required | Needs to be `unet`                                                                                                   |
| `device`   | string  | required | Name of the tunnel device                                                                                            |
| `key`      | string  | required | Local wireguard key                                                                                                  |
| `auth_key` | string  | required | Key used to sign network config                                                                                      |
| `tunnels`  | list    |          | List of tunnel devices mapped to VXLAN service definitions in the network config (format: `<device>=<servicename>`). |
| `connect`  | list    |          | List of external unetd host IP addresses to download network config updates from                                     |
| `domain`   | string  |          | Domain suffix for hosts in the generated hosts file                                                                  |
| `dht`      | boolean |          | Enable DHT peer discovery for this network                                                                           |

The `connect` option only needs to be used for bootstrapping the setup in case you're not uploading the network data to the node directly. Once unetd has a working peer connection, it will always replicate updates over the tunnel.

### Network config data

Network config is written as a JSON file.

##### Example:

    {
            "config": {
                    "port": 51830,
                    "keepalive": 10,
                    "peer-exchange-port": 51831,
                    "stun-servers": [
                            "stun.l.google.com:19302",
                            "stun1.l.google.com:19302"
                    ]
            },
            "hosts": {
                    "ap1": {
                            "key": "yB3V0Wz37qheZoZiG0KNFAqfuI2TetO4sfXgqO/Gd0c=",
                            "endpoint": "192.168.1.13",
                            "groups": [
                                    "ap"
                            ]
                    },
                    "ap2": {
                            "key": "aGNcyMLrN+C4WW0nJBUGwqw8ifIleUVefv/9vh+d1Fw=",
                            "endpoint": "192.168.1.15",
                            "groups": [
                                    "ap"
                            ]
                    }
            },
            "services": {
                    "l2-tunnel": {
                            "config": {
                            },
                            "members": [
                                    "@ap"
                            ],
                            "type": "vxlan"
                    }
            }
    }

##### Config properties:

| Name                 | Type             | Description                                                                |
|:---------------------|:-----------------|:---------------------------------------------------------------------------|
| `port`               | int              | Wireguard tunnel port (can be overriden for individual hosts)              |
| `keepalive`          | int              | Interval (in seconds) for keepalive and forcing peer reconnection attempts |
| `peer-exchange-port` | int              | Port for exchanging peer messages on the WireGuard tunnel (0: disabled)    |
| `stun-servers`       | array of strings | List of STUN servers written as hostname:port strings                      |

##### Host properties:

| Name                 | Type             | Description                                                                                                              |
|:---------------------|:-----------------|:-------------------------------------------------------------------------------------------------------------------------|
| `key`                | string           | Wireguard public key                                                                                                     |
| `groups`             | array of strings | Names of groups that the host is a member of                                                                             |
| `ipaddr`             | array of strings | Local IP addresses of the host (IPv4 or IPv6)                                                                            |
| `subnet`             | array of strings | Subnets routed by the host (IPv4 or IPv6) (format: `<addr>/<mask>`)                                                      |
| `port`               | int              | Wireguard tunnel port (overrides `config` property)                                                                      |
| `peer-exchange-port` | int              | Host specific port for exchanging peer messages on the WireGuard tunnel (0: disabled)                                    |
| `endpoint`           | string           | Public endpoint address (format: `<addr>` for IPv4, `[<addr>]` for IPv6 with optional `:<port>` suffix)                  |
| `gateway`            | string           | Name of another host to use as gateway (can be used for avoiding direct connections with all other peers from this host) |

##### Service properties

| Name      | Type             | Description                                                 |
|:----------|:-----------------|:------------------------------------------------------------|
| `type`    | string           | Service type                                                |
| `config`  | object           | Service type specific config options                        |
| `members` | array of strings | Members assigned to this service (use `@<name>` for groups) |

### CLI usage

    Usage: unet-cli [<flags>] <file> <command> [<args>] [<option>=<value> ...]

         Commands:
          - create:                                 Create a new network file
          - set-config:                             Change network config parameters
          - add-host <name>:                        Add a host
          - add-ssh-host <name> <host>:             Add a remote OpenWrt host via SSH
                                                    (<host> can contain SSH options as well)
          - set-host <name>:                        Change host settings
          - set-ssh-host <name> <host>:             Update local and remote host settings
          - add-service <name>:                     Add a service
          - set-service <name>:                     Change service settings
          - sign                                    Sign network data

         Flags:
          -p:                                       Print modified JSON instead of updating file

         Options:
          - config options (create, set-config):
            port=<val>                              set tunnel port (default: 51830)
            pex_port=<val>                          set peer-exchange port (default: 51831, 0: disabled)
            keepalive=<val>                         set keepalive interval (seconds, 0: off, default: 10)
            stun=[+|-]<host:port>[,<host:port>...]  set/add/remove STUN servers
          - host options (add-host, add-ssh-host, set-host):
            key=<val>                               set host public key (required for add-host)
            port=<val>                              set host tunnel port number
            pex_port=<val>                          set host peer-exchange port (default: network pex_port, 0: disabled)
            groups=[+|-]<val>[,<val>...]            set/add/remove groups that the host is a member of
            ipaddr=[+|-]<val>[,<val>...]            set/add/remove host ip addresses
            subnet=[+|-]<val>[,<val>...]            set/add/remove host announced subnets
            endpoint=<val>                          set host endpoint address
            gateway=<name>                          set host gateway (using name of other host)
         - ssh host options (add-ssh-host, set-ssh-host)
            auth_key=<key>                          use <key> as public auth key on the remote host
            priv_key=<key>                          use <key> as private host key on the remote host (default: generate a new key)
            interface=<name>                        use <name> as interface in /etc/config/network on the remote host
            domain=<name>                           use <name> as hosts file domain on the remote host (default: unet)
            connect=<val>[,<val>...]                set IP addresses that the host will contact for network updates
            tunnels=<ifname>:<service>[,...]        set active tunnel devices
         - service options (add-service, set-service):
            type=<val>                              set service type (required for add-service)
            members=[+|-]<val>[,<val>...]           set/add/remove service member hosts/groups
         - vxlan service options (add-service, set-service):
            id=<val>                                set VXLAN ID
            port=<val>                              set VXLAN port
            mtu=<val>                               set VXLAN device MTU
            forward_ports=[+|-]<val>[,<val>...]     set members allowed to receive broadcast/multicast/unknown-unicast
         - sign options:
            upload=<ip>[,<ip>...]                   upload signed file to hosts

### DHT support

For DHT peer discovery, the unet-dht package needs to be installed, and dht enabled in the interface on the nodes. For NAT support, you also need to configure at least one working STUN server in the network data. While peers can find each other through DHT directly, STUN is needed for figuring out the external wireguard port and establishing a network connection over it. Please note that DHT based discovery needs some time for peers to actually discover each other, sometimes 1-3 minutes.

---

# Wireless Modes

FIXME This needs to indicate the UCI values for `option mode` to have any value

# Wireless Modes

For setting up the wireless modes see [Documentation](/docs/start)

    iw list

has a section with `Supported interface modes`

## AP

AP ... Access Point Also called "master" mode.

## AP/vlan

Dynamic VLAN tagging support in hostapd. see Kernel: [hostapd](https://wireless.wiki.kernel.org/en/users/documentation/hostapd#dynamic_vlan_tagging) see [ML](http://comments.gmane.org/gmane.linux.kernel.wireless.general/58064)

## IBSS (Ad-Hoc)

## MESH POINT (802.11s)

see [80211s](/docs/guide-user/network/wifi/mesh/80211s)

## MONITOR

radiotap headers package survey and injection

## OCB

Outside Context of a BSS

## P2P Client

P2P (Peer-to-peer) client

## P2P-GO

P2P (Peer-to-peer) Group Owner

## Station (Client)

Alternative name: managed mode Mode when connected to an AP.

## WDS

4address/4-address mode see: [IEEE 4-address](http://www.ieee802.org/1/files/public/802_architecture_group/802-11/4-address-format.doc)

## Links

     * Mode list taken from [[http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/nl80211.h|include/uapi/linux/nl80211.h]]
     * linux-wireless mailing list

---

# Wireless Standards

This article lists common standards and basic features that are relevant to OpenWrt.

## 802.11a

Old standard that operates in 5GHz [frequency band](https://en.wikipedia.org/wiki/Frequency_band)

[IEEE_802.11a-1999](https://en.wikipedia.org/wiki/IEEE_802.11a-1999)

## 802.11b

[IEEE_802.11b-1999](https://en.wikipedia.org/wiki/IEEE_802.11b-1999) Operates in 2.4GHz Band Old standard.

## 802.11g

[](https://en.wikipedia.org/wiki/IEEE_802.11g-2003) Operates in 2.4GHz Band Old standard.

## 802.11n

[IEEE_802.11n-2009](https://en.wikipedia.org/wiki/IEEE_802.11n-2009)

## 802.11ac

[IEEE_802.11ac](https://en.wikipedia.org/wiki/IEEE_802.11ac) Also called "Wifi 5"

## 802.11ad

[IEEE_802.11ad](https://en.wikipedia.org/wiki/IEEE_802.11ad) Not very common in OpenWrt.

## 802.11ax

[IEEE_802.11ax](https://en.wikipedia.org/wiki/IEEE_802.11ax)

Also called "Wifi 6"

### Features in Drivers

Each hardware has certain features that can be queried in OpenWrt by using `iw phy <phy interface> info `

Mismatching features result in compatibility problems and possibly reduced data transfer rates.

example:

    RX LDPC
    HT20/HT40
    SM Power Save disabled
    RX HT20 SGI
    RX HT40 SGI
    TX STBC
    RX STBC 1-stream
    Max AMSDU length: 3839 bytes
    DSSS/CCK HT40

#### MIMO multiple-input and multiple-output

Technology that uses multiple antennas to increase data transfer rates. see also MCS tables

[STBC](https://en.wikipedia.org/wiki/Space%E2%80%93time_block_code) is part of MIMO.

[MU-MIMO](https://en.wikipedia.org/wiki/Multi-user_MIMO)

#### HT, VHT, HE

Required for higher throughput - 802.11n, 802.11ac, 802.11ax standards. HT ... 802.11n , VHT ... 802.11ac, HE ... 802.11ax

HT20 : 20 MHz wide channels HT40: 40 MHz VHT80 : 80 MHz VHT160: 160MHz

see also MCS table

#### MCS Modulation and Coding Scheme

often visualized as a table. The MCS Index is a value that the hardware supports and uses when communicating.

:!: Low data rates mean the higher indexes are not used. Reasons might be configuration or interference.

#### RSDB DBDC

Acronym for Radio Simultan Dual Band, Dual Band Dual Concurrent

Use two frequency bands at the same time by one endpoint.

Supported by: mt76 and potentially brcmfmac ([BCM4359](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/drivers/net/wireless/broadcom?id=d4aef159394d5940bd7158ab789969dab82f7c76) )

Normally radios operate in Single Band Single Concurrent (SBSC) (OpenWrt: 802.11an, 802.11bgn) or are capable of Dual Band Single Concurrent (DBSC): having 2 frequency bands selectable (OpenWrt: 802.11abgn capable).

#### WOW Wake On Wlan

[Wake-on-LAN](https://en.wikipedia.org/wiki/Wake-on-LAN)

## Links

[some MCS Tables](https://www.semfionetworks.com/blog/mcs-table-updated-with-80211ax-data-rates)

---

# Xenomai - real-time framework inside OpenWrt

![cleanup&noheader&nofooter&noeditbtn](/page>meta/infobox/cleanup&noheader&nofooter&noeditbtn) ![wip&noheader&nofooter&noeditbtn](/page>meta/infobox/wip&noheader&nofooter&noeditbtn)

# Xenomai - real-time framework inside OpenWrt

This techref describe a work in progress finalize to support Xenomai (<http://www.xenomai.org/>) real-time framework inside OpenWrt.

:!: This article describe a WIP activity. Don't rely on it. :!:

Thanks to Adeos, Xenomai will receive the interrupts first and decide to handle them or not. If not, they will then be transfered to the regular Linux kernel. Also, Xenomai provides a framework to develop applications which can be easily moved between the Real Time Xenomai environment and the regular Linux system. Moreover, Xeno provides a set of APIs (called "skins") that emulate traditional RTOSes such as VxWorks and pSOS and implement other APIs such as POSIX. Thus, porting third party real time applications to Xenomai is a fairly simple process.[^1]

An example of usage is available on xenomai.org website.

## Pre-condition

Xenomai framework run only on some architecture and generally isn't needed for your purpose; the 2.5.3 version can be used for arm\|x86\|powerpc and only for a specific linux kernel version. Here follows a table that can help you to choise the couple xenomai versione/kernel version per arch.

|                 |         |               |
|:----------------|:--------|--------------:|
| Xenomai version | Arch    | linux version |
| 2.5.3           | arm     |        2.6.33 |
| 2.5.3           | powerpc |        2.6.34 |
| 2.5.3           | x86     |    2.6.34-rc5 |

## Status

Xenomai is intended to be used only for specific purpose and OpenWrt community generally don't support it directly.

[^1]: from <http://www.armadeus.com/wiki/index.php?title=Xenomai>
