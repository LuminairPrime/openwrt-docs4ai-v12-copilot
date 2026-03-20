# openwrt-hotplug (Skeleton Semantic Map)

> **Contains:** Headers and function signatures for openwrt-hotplug.
> **Generated:** 2026-03-12T22:39:38.602793+00:00

---

> **Summary:** Documents the standard hotplug event environment variables injected by OpenWrt's netifd and network subsystems into scripts in /etc/hotplug.d/. Covers iface subsystem events (ifup, ifdown, ifupdate) with $INTERFACE, $DEVICE, and $ACTION variables; net subsystem events for physical interface changes; and hotplug script patterns using uci_toggle_state for persistent state tracking.
> **Use Case:** Reference when writing hotplug.d scripts that react to network interface state changes, USB device insertion, or any OpenWrt system event that needs to execute logic in response to $ACTION, $INTERFACE, or $DEVICE being set by the kernel and netifd.
# OpenWrt Core Hotplug Events
## Event Category: `iface` — File: `network/config/netifd/files/etc/hotplug.d/iface/00-netstate`
# Shell Script
## Event Category: `iface` — File: `network/config/qos-scripts/files/etc/hotplug.d/iface/10-qos`
# Shell Script
#!/bin/sh
## Event Category: `ieee80211` — File: `network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/10-wifi-detect`
# Shell Script
#!/bin/sh
## Event Category: `ieee80211` — File: `network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/11-ath12k-trigger`
# Shell Script
#!/bin/sh
# Restart ath12k radios that take long time to initialize on boot
## Event Category: `atm` — File: `network/config/soloscli/files/etc/hotplug.d/atm/15-solos-init`
# Shell Script
#!/bin/sh
## Event Category: `dsl` — File: `network/utils/ltq-dsl-base/files/etc/hotplug.d/dsl/led_dsl.sh`
# Shell Script
#!/bin/sh
## Event Category: `dsl` — File: `network/utils/ltq-dsl-base/files/etc/hotplug.d/dsl/pppoa.sh`
# Shell Script
#!/bin/sh
