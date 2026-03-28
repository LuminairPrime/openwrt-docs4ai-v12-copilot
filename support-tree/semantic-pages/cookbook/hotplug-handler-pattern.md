---
title: Hotplug Handler Pattern
module: cookbook
origin_type: authored
token_count: 2283
source_file: L1-raw/cookbook/hotplug-handler-pattern.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_locator: content/cookbook-source/hotplug-handler-pattern.md
description: Shows how to write narrowly-scoped OpenWrt hotplug handlers that match
  explicit event contracts, publish minimal state, and hand off heavier work to the
  right control plane.
era_status: current
when_to_use: Use when writing or reviewing scripts under /etc/hotplug.d or package
  hotplug helpers, especially for iface, device, wireless, mount, DHCP, or time-validity
  events.
related_modules:
- openwrt-core
- procd
- ubus
- uci
- wiki
verification_basis: Local OpenWrt source review against checkout 56bf67d47406bd7c64cdfc6a8610032afe7094cf
  plus archive-backed mistake review from the OpenWrt mailing list corpus
reviewed_by: placeholder
last_reviewed: '2026-03-28'
---
# Hotplug Handler Pattern

> **When to use:** Use this pattern when an OpenWrt component reacts to a kernel, interface, DHCP, storage, or wireless event through a hotplug script. A good handler is a small event filter and dispatcher. It should not become a second init system.
> **Key components:** hotplug, procd, ubus, UCI, shell
> **Era:** Current (23.x and later). Hotplug remains the right boundary for small event reactions, state publication, and targeted dispatch. It is the wrong boundary for broad boot orchestration or unguarded service restarts.

## Overview

OpenWrt hotplug handlers run because some subsystem emits a specific event and exports a small contract through environment variables such as `ACTION`, `INTERFACE`, `DEVICE`, `DEVTYPE`, or `DEVPATH`. The durable design rule is:

1. Match only the event contract you actually handle.
2. Exit immediately for everything else.
3. Do the smallest safe state change or dispatch.
4. Hand off heavier logic to ubus or a service that already owns that lifecycle.

Two recurring failures showed up in the archive review:

1. handlers assumed only `add` and `remove` events existed, then misclassified newer events such as `bind` and `unbind`
2. handlers depended on ambient shell variables instead of a deliberate event contract, which produced wrong values when the caller inherited stale environment

That is why current OpenWrt hotplug code tends to begin with tight guards and a fast exit path.

## Wrong Boundary

The common mistake is to treat hotplug as a general-purpose place to manage a daemon or rebuild unrelated system state.

### WRONG

```sh
#!/bin/sh

# Broad, weak match: every event falls through.
[ -n "$ACTION" ] || exit 0

# Rebuild service state on every event.
uci set myservice.main.last_event="$ACTION"
uci commit myservice
/etc/init.d/myservice restart
```

Why this fails:

1. it matches far more events than the script actually understands
2. it commits config and restarts a daemon even when nothing relevant changed
3. it mixes event filtering, persistence, and service lifecycle into one unsupervised shell path

### CORRECT

Use hotplug as a narrow event boundary:

1. filter specific `ACTION` and object variables first
2. update only the small piece of state the event owns
3. if heavier behavior is needed, call the proper ubus or procd-managed control path

## Pattern 1: Guard the event taxonomy first

The first lines of a good handler should make its scope obvious.

Current source examples:

```sh
# package/network/config/firewall/files/firewall.hotplug
[ "$ACTION" = ifup -o "$ACTION" = ifupdate ] || exit 0
[ "$ACTION" = ifupdate -a -z "$IFUPDATE_ADDRESSES" -a -z "$IFUPDATE_DATA" ] && exit 0
```

```sh
# package/network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/11-ath12k-trigger
[ "${ACTION}" = "add" ] || exit 0
[ $(grep -c DRIVER=ath12k_pci /sys/$DEVPATH/device/uevent) -gt 0 ] || exit 0
```

```sh
# package/system/fstools/files/mount.hotplug
[ "$ACTION" = "add" -o "$ACTION" = "remove" ] && /sbin/block hotplug
```

What these get right:

1. the accepted event set is explicit
2. irrelevant actions are discarded before any side effect
3. additional guards narrow the handler to the device or data shape it actually understands

Archive evidence shows why this matters. A `comgt` hotplug fix had to add:

```sh
[ "$ACTION" = add ] || [ "$ACTION" = remove ] || exit 0
```

because newer kernel event types were being treated like `remove`, which broke hotplugged 3G modems.

Archive source:

- https://lists.openwrt.org/pipermail/openwrt-devel/2021-January.txt (`package/comgt: Handle bind/unbind events`)
	Read: 2026-03-28

## Pattern 2: Use a deliberate event contract, not ambient shell state

If the event needs to cross a subsystem boundary, pass only the fields you mean to expose.

Current source example:

```sh
# package/network/services/dnsmasq/files/dhcp-script.sh
for var in $(env); do
	if [ "${var}" != "${var#DNSMASQ_}" ]; then
		json_add_string "" "${var%%=*}=${var#*=}"
	fi
done

case "$1" in
	add)
		json_add_string "" "ACTION=add"
		hotplugobj="dhcp"
	;;
	del)
		json_add_string "" "ACTION=remove"
		hotplugobj="dhcp"
	;;
esac

[ -n "$hotplugobj" ] && ubus call hotplug.${hotplugobj} call "$(json_dump)"
```

What this gets right:

1. it does not forward the entire inherited shell environment blindly
2. it normalizes the event into a smaller, structured payload
3. it hands off through ubus instead of sourcing unrelated shell code with implicit globals

That filtering is not just tidiness. It prevents unrelated shell variables from leaking into the event payload and keeps the receiving side bound to a smaller, deliberate namespace.

This matches the archive lesson from the `procd, possible hotplug issue?` thread: empty variables were sometimes simply not set, so stale shell state could leak into a handler and produce a wrong value. When you need cross-component delivery, build the contract explicitly.

## Pattern 3: Small state publication is fine; full service lifecycle control is not

Hotplug is a good place to publish small event-owned state.

Current source example:

```sh
# package/network/config/netifd/files/etc/hotplug.d/iface/00-netstate
[ ifup = "$ACTION" ] && {
	uci_toggle_state network "$INTERFACE" up 1
	[ -n "$DEVICE" ] && {
		uci_toggle_state network "$INTERFACE" ifname "$DEVICE"
	}
}
```

This is the right scale for a handler:

1. it reacts to one event class
2. it updates transient runtime state, not broad persistent config
3. it leaves long-lived service supervision to the subsystem that owns it

`uci_toggle_state` is a legacy helper for transient runtime state, so the main lesson here is about scope, not about copying that exact helper into new designs everywhere.

If your script is starting to own retries, respawn policy, or daemon startup order, it has crossed into procd territory and should move there.

## Pattern 4: If you must trigger a reload, make it narrow and justified

Some handlers do need to tell another subsystem to refresh, but the good examples do that behind clear preconditions.

Current source example:

```sh
# package/network/config/firewall/files/firewall.hotplug
/etc/init.d/firewall enabled || exit 0
fw3 -q network "$INTERFACE" >/dev/null || exit 0

logger -t firewall "Reloading firewall due to $ACTION of $INTERFACE ($DEVICE)"
fw3 -q reload
```

What this gets right:

1. it only runs for specific interface events because Pattern 1 already filtered them
2. it proves the affected network participates in firewall state before reloading
3. it performs a targeted control-plane action instead of using the handler as a generic restart hook

The rule is not "never reload from hotplug." The rule is "reload only when the event is narrow, the dependency is explicit, and the owner subsystem is clear."

## Keep / Avoid

Keep:

1. start with explicit `ACTION` filtering and exit early
2. add second-level guards for `INTERFACE`, `DEVICE`, `DEVTYPE`, or `DEVPATH` before any side effect
3. publish small runtime state or dispatch a structured event payload
4. use ubus or a service-owned control path when the effect belongs to another subsystem
5. make the handler cheap enough that repeated events are not dangerous

Avoid:

1. assuming the event taxonomy is only `add` and `remove`
2. depending on inherited shell variables that the event contract did not define
3. writing broad persistent config on every event
4. calling full daemon restarts from weakly filtered hooks
5. turning a hotplug script into a long-running workflow or a second service manager

## Related Pages

- [procd Service Lifecycle](./procd-service-lifecycle.md) - use this when the real problem is daemon lifecycle, respawn, or reload policy
- [Firstboot uci-defaults Pattern](./firstboot-uci-defaults-pattern.md) - use this for first-boot config mutation instead of event-driven runtime hooks
- [Architecture Overview](./architecture-overview.md) - use this to place hotplug, ubus, netifd, and procd in the broader OpenWrt control plane

## Verification Notes

- Current source examples verified from local checkout `56bf67d47406bd7c64cdfc6a8610032afe7094cf`:
  - `https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/config/firewall/files/firewall.hotplug`
  - `https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/config/netifd/files/etc/hotplug.d/iface/00-netstate`
  - `https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/config/wifi-scripts/files/etc/hotplug.d/ieee80211/11-ath12k-trigger`
  - `https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/network/services/dnsmasq/files/dhcp-script.sh`
  - `https://github.com/openwrt/openwrt/blob/56bf67d47406bd7c64cdfc6a8610032afe7094cf/package/system/fstools/files/mount.hotplug`
- Archive-backed mistake evidence reviewed 2026-03-28:
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2021-January.txt` (`package/comgt: Handle bind/unbind events`)
  - `https://lists.openwrt.org/pipermail/openwrt-devel/2024-February.txt` (`procd, possible hotplug issue?`)