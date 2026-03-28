---
title: uBus IPC/RPC System
module: wiki
origin_type: wiki_page
token_count: 405
source_file: L1-raw/wiki/wiki_page-guide-developer-ubus.md
last_pipeline_run: '2026-03-28T11:59:43.422282+00:00'
source_url: https://openwrt.org/docs/guide-developer/ubus
language: text
ai_summary: Practical guide for using ubus from shell scripts, C code, and Lua/ucode. Covers the ubus CLI (ubus call, ubus listen, ubus wait_for), calling ubus from C (ubus_lookup_id, ubus_invoke, ubus_send_event), registering a new ubus object in a C daemon (ubus_add_object, ubus_method definitions), and the ACL permission file format for granting rpcd access to specific ubus paths.
ai_when_to_use: Reference when calling an existing ubus service from a shell script (ubus call system board), writing a C daemon that needs to expose methods over ubus, or configuring rpcd ACL files to allow a LuCI JavaScript view to invoke a ubus path without root privileges.
ai_related_topics:
- ubus_invoke
- ubus_add_object
- ubus_method
- ubus call
- rpcd ACL
- ubus_send_event
- libubox
---

> **Source:** [https://openwrt.org/docs/guide-developer/ubus](https://openwrt.org/docs/guide-developer/ubus)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-28

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
