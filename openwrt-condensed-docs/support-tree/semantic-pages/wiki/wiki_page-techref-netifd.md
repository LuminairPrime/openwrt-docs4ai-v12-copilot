---
title: netifd (Network Interface Daemon) – Technical Reference
module: wiki
origin_type: wiki_page
token_count: 1929
source_file: L1-raw/wiki/wiki_page-techref-netifd.md
last_pipeline_run: '2026-03-27T20:02:39.961617+00:00'
source_url: https://openwrt.org/docs/techref/netifd
language: text
ai_summary: Documents netifd, the OpenWrt network interface daemon responsible for managing network interfaces based on UCI config. Explains the interface/device/proto handler model, the /etc/config/network schema (interface, device, bridge, route, rule sections), protocol handler shell scripts in /lib/netifd/proto/, ifup/ifdown/ifupdate hotplug event flow, and the ubus network API exposed by netifd.
ai_when_to_use: Reference when diagnosing why an interface fails to come up, implementing a custom protocol handler (proto script in /lib/netifd/proto/), writing hotplug scripts that react to ifup/ifdown events, or calling netifd ubus methods like network.interface.status or network.interface.up.
ai_related_topics:
- netifd ubus API
- proto_run_command
- proto_export_env
- hotplug.iface
- network.interface.status
- UCI network config
- bridge
---
# netifd (Network Interface Daemon) – Technical Reference

- [Project's git](http://git.openwrt.org/?p=project/netifd.git;a=summary)
- netifd is available in OpenWrt since [R28499 (trunk)](https://dev.openwrt.org/changeset/28499) and published under the GPLv2.
- [commits to OpenWrt trunk regarding netifd](https://dev.openwrt.org/search?changeset=on&milestone=on&wiki=on&q=netifd&page=1&noquickjump=1)
- [Design of netifd](http://git.openwrt.org/?p=project/netifd.git;a=blob;f=DESIGN)

### What is netifd?

`netifd` is an [RPC](https://en.wikipedia.org/wiki/Remote procedure call)-capable [daemon](https://en.wikipedia.org/wiki/Daemon (computing)) written in [C](https://en.wikipedia.org/wiki/C (programming language)) for better access to kernel APIs with the ability to listen on [netlink events](https://en.wikipedia.org/wiki/Netlink). `Netifd` has replaced the old *OpenWrt-network configuration scripts*, the actual scripts that configured the network, e.g.

- `/lib/network/*.sh`,
- `/sbin/ifup`
- some scripts in `/etc/hotplug.d`.)

`netifd` is intended to stay compatible with the existing format of `/etc/config/network`, the only exceptions being rare special cases like aliases or the overlay variables in `/var/state` (though even most of those can be easily emulated).

### Debugging

- Add the switch `-l <level>` to */etc/init.d/network*
  - Level is specified as an integer:
    - 0 = L_CRIT
    - 1 = L_WARNING
    - 2 = L_NOTICE (default)
    - 3 = L_INFO
    - 4 = L_DEBUG
- For the L_DEBUG level, there is another option `-d <mask>` to set a mask:
  - Options are:
    - 1 = DEBUG_SYSTEM
    - 2 = DEBUG_DEVICE
    - 4 = DEBUG_INTERFACE
    - 8 = DEBUG_WIRELESS
  - Add your favorite options together to obtain the `<mask>`.

      * In order for the output to be seen you'll need to modify /etc/init.d/network to add:
        * [procd_set_param](../cookbook/procd-service-lifecycle.md) stdout 1
        * [procd_set_param](../cookbook/procd-service-lifecycle.md) stderr 1
      * to start_service so that procd doesn't send netifd hotplug script output to /dev/null.

### Help with the development of netifd

1.  test what has been ported
2.  review of the code
3.  help porting more of our protocol handler scripts (so far, static, ppp, pppoe, pppoa and dhcp are supported)

### Why do we want netifd?

One thing that `netifd` does much better then old *OpenWrt-network configuration scripts* is handling configuration changes. With `netifd`, when the file `/etc/config/network` changes, you no longer have to restart all interfaces. Simply run **`/etc/init.d/network reload`**. This will issue an `ubus`-call to `netifd`, telling it to figure out the difference between runtime state and the new config and apply only that. This works on a per-interface level, even with protocol handlers written as shell scripts.

It boils down to the fact that the current network and interface setup mechanisms (via network configuration scripts) are rather constrained and inflexible:

- lack of statefulness
- tendency for raceconditions
- inability to properly nest protocols
- limited featureset of the ash shell which will not allow for complex interface operations like e.g. calculating [ULAs](https://en.wikipedia.org/wiki/Unique local address)
- you name it

`Netifd` will be able to manage even complex interface configurations with a mix of bonding, vlans, bridges, etc. and handle the dependencies between interfaces properly - and of course all that without adding unnecessary bloat.
AFAIK there are no alternatives to netifd, e.g. [connman](https://connman.net/) seems to be centered around one specifific use case only: having a mobile device access the internet through multiple connections. Connman is based on dbus.

The following is a brief conversation from IRC regarding hints on how netifd is involved with wifi interface startup and variables used. It 'documents' my frustration with trying to add a new uci variable (utf8_ssid), and I don't think the answers contained should be lost:

    [20:20:06]  <jow> ldir: its complicated
    [20:20:29]  <jow>   ldir: upon start, netifd scans all wireless handlers in /lib/netifd/wireless/
    [20:21:08]  <jow>   ldir: so for mac80211 that'd be /lib/netifd/wireless/mac80211.sh
    [20:22:33]  <jow>   ldir: the handler tells netifd about which options it recognized, for mac80211.sh this can be seen in drv_mac80211_init_device_config() (for config wifi-device) and drv_mac80211_init_iface_config() (for config wifi-iface)
    [20:27:26]  <jow>   ldir: netifd reads /etc/config/wireless, converts it into json and eventually passes it via various indirections back to the script
    [20:28:07]  <jow>   ldir: it will execute something like  /lib/netifd/wireless/mac80211.sh mac80211 setup radio0 '{ lots of json encoded uci options }'
    [20:29:20]  <jow>   ldir: this invocation is catched by `init_wireless_driver "$@"` in /lib/netifd/wireless/mac80211.sh (declared in the shared /lib/netifd/netifd-wireless.sh)
    [20:31:03]  <ldir>  jow: thank you - I shall try to digest this.
    [20:31:38]  <jow>   ldir: init_wireless_driver() will parse the passed json into shell variables and dispatch back to one of the drv_*() functions in /lib/netifd/wireless/mac80211.sh
    [20:32:02]  <jow>   e.g. /lib/netifd/wireless/mac80211.sh mac80211 setup radio0 '{ lots of json encoded uci options }'  will eventually call  drv_mac80211_setup()
    [20:32:48]  <jow>   drv_mac80211_setup() will have access to all the uci config variables via the loaded jshn environment so you can accesss them using json_get_vars, json_select etc.
    [20:33:15]  <jow>   the radio we're operating on is passed as "$1" and will contain the uci wifi-device section name, e.g. "radio0"
    [20:35:11]  <jow>   from then on its "just" shell magic translating things back and forth, writing temporary hostapd config etc. and eventually instructing netifd to launch a hostapd process using wireless_add_process()
    [20:35:50]  <jow>   executive summary
    [20:36:03]  <ldir>  that's hell on a stick :-)
    [20:36:26]  <ldir>  btw the executive summary was 'it's complicated' ;-)
    [20:36:33]  <jow>   - register new config options in /lib/netifd/wireless/mac80211.sh using either drv_mac80211_init_device_config or drv_mac80211_init_iface_config - for utf8ssid you likely want drv_mac80211_init_iface_config
    [20:38:32]  <jow>   correction; register it in hostapd_common_add_bss_config() of /lib/netifd/hostapd.sh
    [20:39:07]  <jow>   - and process it in hostapd_set_bss_options()
    [20:39:12]  <jow>   thats it
    [20:39:19]  <ldir>  jow: in theory I've done that - I noticed mac80211.sh has a 'common' set options
    [20:39:36]  <jow>   you most likely need to restart netifd for it to become aware of the new option
    [20:39:50]  <jow>   du to the uci->blob->json->string->jshn call chain
