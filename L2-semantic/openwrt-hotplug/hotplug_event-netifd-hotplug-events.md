---
title: OpenWrt Core Hotplug Events
module: openwrt-hotplug
origin_type: hotplug_event
token_count: 1412
source_file: L1-raw/openwrt-hotplug/hotplug_event-netifd-hotplug-events.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/openwrt/blob/unknown/package/**/etc/hotplug.d/*
source_locator: package/**/etc/hotplug.d/*
language: bash
ai_summary: Documents the standard hotplug event environment variables injected by OpenWrt's netifd and network subsystems into scripts in /etc/hotplug.d/. Covers iface subsystem events (ifup, ifdown, ifupdate) with $INTERFACE, $DEVICE, and $ACTION variables; net subsystem events for physical interface changes; and hotplug script patterns using uci_toggle_state for persistent state tracking.
ai_when_to_use: Reference when writing hotplug.d scripts that react to network interface state changes, USB device insertion, or any OpenWrt system event that needs to execute logic in response to $ACTION, $INTERFACE, or $DEVICE being set by the kernel and netifd.
ai_related_topics:
- $ACTION
- $INTERFACE
- $DEVICE
- uci_toggle_state
- hotplug.iface
- hotplug.net
---
# OpenWrt Core Hotplug Events

> **Extracted from:** default `etc/hotplug.d/` scripts across the OpenWrt repository

> **Note for LLMs:** Developers building apps use these scripts as templates. Analyze the `$ACTION`, `$INTERFACE`, and subsystem blocks to understand exactly which environment variables OpenWrt injects during hotplug events.

---

## Event Category: `iface` — File: `network/config/netifd/files/etc/hotplug.d/iface/00-netstate`

# Shell Script
```bash
[ ifup = "$ACTION" ] && {
	uci_toggle_state network "$INTERFACE" up 1
	[ -n "$DEVICE" ] && {
		uci_toggle_state network "$INTERFACE" ifname "$DEVICE"
	}
}
```


---

## Event Category: `iface` — File: `network/config/qos-scripts/files/etc/hotplug.d/iface/10-qos`

# Shell Script
```bash
#!/bin/sh
[ "$ACTION" = ifup ] && /etc/init.d/qos enabled && /usr/lib/qos/generate.sh interface "$INTERFACE" | sh
```


---

## Event Category: `ieee80211` — File: `network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/10-wifi-detect`

# Shell Script
```bash
#!/bin/sh

[ "${ACTION}" = "add" ] && {
	/sbin/wifi config
	ubus call network.wireless retry
}
```


---

## Event Category: `ieee80211` — File: `network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/11-ath12k-trigger`

# Shell Script
```bash
#!/bin/sh

# Restart ath12k radios that take long time to initialize on boot

[ "${ACTION}" = "add" ] || exit 0
[ $(grep -c DRIVER=ath12k_pci /sys/$DEVPATH/device/uevent) -gt 0 ] || exit 0

. /usr/share/libubox/jshn.sh

restart_radio() {
	radio=$1
	arg="{\"radio\": \"$radio\"}"
	ubus call network reload
	ubus call network.wireless down "$arg"
	ubus call network.wireless up "$arg"
}

json_init
json_load "$(ubus -S call network.wireless status)"
json_get_keys radios
for radio in $radios; do
	json_select $radio
	json_get_vars up
	json_get_vars retry_setup_failed

	json_select config
	json_get_vars path
	json_select ..

	if [ $up = 0 -a $retry_setup_failed = 1 ] &&
	   [ $(iwinfo nl80211 phyname "path=$path") = "$DEVICENAME" ]; then
		restart_radio $radio
	fi

	json_select ..
done
```


---

## Event Category: `atm` — File: `network/config/soloscli/files/etc/hotplug.d/atm/15-solos-init`

# Shell Script
```bash
#!/bin/sh

dialog() {
	local tag="$(echo "$1" | cut -d= -f1)"
	local value="$(echo "$1" | cut -d= -f2-)"
	local response
	
	response="$(soloscli -s "$port" "$tag" "$value")"
	[ $? -ne 0 ] && {
		logger "soloscli($port): $tag '$value' returns $response"
	}
}

if [ "$ACTION" = "add" ]; then
	include /lib/network
	scan_interfaces

	case $DEVICENAME in
	solos-pci[0-3])
		port="${DEVICENAME#solos-pci}"
		device="solos${port}"

		config_list_foreach wan "$device" dialog
		;;
	esac
fi
```


---

## Event Category: `dsl` — File: `network/utils/ltq-dsl-base/files/etc/hotplug.d/dsl/led_dsl.sh`

# Shell Script
```bash
#!/bin/sh

[ "$DSL_NOTIFICATION_TYPE" = "DSL_INTERFACE_STATUS" ] || exit 0

. /lib/functions.sh
. /lib/functions/leds.sh

led_dsl_up() {
	case "$(config_get led_dsl trigger)" in
	"netdev")
		led_set_attr $1 "trigger" "netdev"
		led_set_attr $1 "device_name" "$(config_get led_dsl dev)"
		for m in $(config_get led_dsl mode); do
			led_set_attr $1 "$m" "1"
		done
		;;
	*)
		led_on $1
		;;
	esac
}

config_load system
config_get led led_dsl sysfs
if [ -n "$led" ]; then
	case "$DSL_INTERFACE_STATUS" in
	  "HANDSHAKE")  led_timer $led 500 500;;
	  "TRAINING")   led_timer $led 200 200;;
	  "UP")		led_dsl_up $led;;
	  *)		led_off $led
	esac
fi
```


---

## Event Category: `dsl` — File: `network/utils/ltq-dsl-base/files/etc/hotplug.d/dsl/pppoa.sh`

# Shell Script
```bash
#!/bin/sh

[ "$DSL_NOTIFICATION_TYPE" = "DSL_INTERFACE_STATUS" ] || exit 0

. /usr/share/libubox/jshn.sh
. /lib/functions.sh

include /lib/network
scan_interfaces

interfaces=$(ubus list network.interface.\* | cut -d"." -f3)
for ifc in $interfaces; do

	json_load "$(ifstatus $ifc)"

	json_get_var proto proto
	if [ "$proto" != "pppoa" ]; then
		continue
	fi

	json_get_var up up
	config_get_bool auto "$ifc" auto 1
	if [ "$DSL_INTERFACE_STATUS" = "UP" ]; then
		if [ "$up" != 1 ] && [ "$auto" = 1 ]; then
			( sleep 1; ifup "$ifc" ) &
		fi
	else
		if [ "$up" = 1 ] && [ "$auto" = 1 ]; then
			( sleep 1; ifdown "$ifc" ) &
		else
			json_get_var autostart autostart
			if [ "$up" != 1 ] && [ "$autostart" = 1 ]; then
				( sleep 1; ifdown "$ifc" ) &
			fi
		fi
	fi
done
```


---
