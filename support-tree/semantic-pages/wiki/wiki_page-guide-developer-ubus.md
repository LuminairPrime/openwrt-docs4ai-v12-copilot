---
title: uBus IPC/RPC System
module: wiki
origin_type: wiki_page
token_count: 405
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-ubus.md
last_pipeline_run: '2026-03-23T22:14:22.429226+00:00'
language: text
---
# uBus IPC/RPC System

## uBus - IPC/RPC

uBus is the interconnect system used by most services running on a *OpenWrt* setup. Services can connect to the bus and provide methods that can be called by other services or clients.

See [uBus Technical Reference](/docs/techref/ubus)

### Reference documentation for ubus

**Path only contains the first context. E.g. network for network.interface.wan**

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
