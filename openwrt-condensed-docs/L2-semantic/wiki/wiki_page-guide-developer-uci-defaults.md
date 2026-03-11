---
title: UCI defaults
module: wiki
origin_type: wiki_page
token_count: 1137
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-uci-defaults.md
last_pipeline_run: '2026-03-11T12:37:15.044626+00:00'
language: text
---
# UCI defaults

See also: [The UCI system](/docs/guide-user/base-system/uci)

*OpenWrt* relies on UCI, the *Unified Configuration Interface*, to configure its core services. UCI defaults provides a way to preconfigure your images, using UCI.

To set some system defaults the first time the device boots, create a script in the directory `/etc/uci-defaults`.

All scripts in that directory are automatically executed by the `boot` service:

- If they exit with code 0 they are deleted afterwards.
- Scripts that exit with non-zero exit code are not deleted and will be re-executed at the next boot until they also successfully exit.

In a live router you can see the existing UCI defaults scripts in `/rom/etc/uci-defaults` , as `/etc/uci-defaults` itself is typically empty (after all scripts have been run successfully and have been deleted).

UCI defaults scripts can be created by packages or they can be inserted into the build manually as custom files.

## Integrating custom settings

See also: [Build system - Custom files](/docs/guide-developer/toolchain/use-buildsystem#custom_files), [Image builder - Custom files](/docs/guide-user/additional-software/imagebuilder#custom_files)

Easiest way to include uci-defaults scripts in your firmware may be as custom files. You can preload custom settings by adding batch scripts containing UCI commands into the `/files/etc/uci-defaults` directory. The path is identical for the buildroot and the image generator. The scripts will be run **after** the flashing process - in case of upgrading, that also includes appending the existing configuration to the JFFS2 partition (mounted as `/overlay`). Scripts should not be executable. To ensure your scripts are not interfering with any other scripts, make sure they get executed last by giving them a high prefix (e.g. *xx_custom*). A basic script that creates the actual uci-defaults script could look like this:

``` bash
cat << "EOF" > /etc/uci-defaults/99-custom
uci -q batch << EOI
set network.lan.ipaddr='192.168.178.1'
set wireless.@wifi-device[0].disabled='0'
set wireless.@wifi-iface[0].ssid='OpenWrt0815'
add dhcp host
set dhcp.@host[-1].name='bellerophon'
set dhcp.@host[-1].ip='192.168.2.100'
set dhcp.@host[-1].mac='a1:b2:c3:d4:e5:f6'
rename firewall.@zone[0]='lan'
rename firewall.@zone[1]='wan'
rename firewall.@forwarding[0]='lan_wan'
EOI
EOF
```

Naturally the script can be created by any text editor, too. The uci-defaults script itself is:

``` bash
uci -q batch << EOI
set network.lan.ipaddr='192.168.178.1'
set wireless.@wifi-device[0].disabled='0'
set wireless.@wifi-iface[0].ssid='OpenWrt0815'
add dhcp host
set dhcp.@host[-1].name='bellerophon'
set dhcp.@host[-1].ip='192.168.2.100'
set dhcp.@host[-1].mac='a1:b2:c3:d4:e5:f6'
rename firewall.@zone[0]='lan'
rename firewall.@zone[1]='wan'
rename firewall.@forwarding[0]='lan_wan'
EOI
```

This is a simple example to set up the LAN IP address, SSID, enable Wi-Fi, configure a static DHCP lease, rename firewall zone and forwarding sections. Once the script has run successfully and exited cleanly (exit status 0), it will be removed from `/etc/uci-defaults`. You can still consult the original in `/rom/etc/uci-defaults` if needed.

## Ensuring scripts don’t overwrite custom settings: implementing checks

Scripts in `/etc/uci-defaults` will get executed at every first boot (i.e. after a clean install or an upgrade), possibly overwriting already existing values. If this behaviour is undesired, we recommend you implement a test at the top of your script - e.g. probe for a custom setting your script would normally configure:

``` bash
[ "$(uci -q get system.@system[0].zonename)" = "America/New York" ] && exit 0
```

This will make sure, when the key has the correct value set, that the script exits cleanly and gets removed from `/etc/uci-defaults` as explained above.

## Examples

- [Restricting root access](/docs/guide-user/additional-software/imagebuilder#restricting_root_access)
- [uci-defaults @ base-files](https://github.com/openwrt/openwrt/tree/master/package/base-files/files/etc/uci-defaults)
- [uci-defaults @ Freifunk Berlin](https://github.com/freifunk-berlin/firmware-packages/tree/master/defaults)
- [uci-defaults @ Freifunk Ulm](https://github.com/ffulm/firmware/blob/master/files/etc/uci-defaults/50_freifunk-setup)
- [config-openwrt @ richb-hanover](https://github.com/richb-hanover/OpenWrtScripts/blob/main/config-openwrt.sh)
