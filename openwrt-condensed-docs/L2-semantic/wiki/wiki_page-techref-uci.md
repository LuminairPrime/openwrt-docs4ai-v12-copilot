---
title: "UCI (Unified Configuration Interface) \u2013 Technical Reference"
module: wiki
origin_type: wiki_page
token_count: 3923
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-uci.md
last_pipeline_run: '2026-03-10T12:16:41.912319+00:00'
language: text
---
# UCI (Unified Configuration Interface) – Technical Reference

This is the Technical Reference. Please see **[UCI (Unified Configuration Interface) – Usage](/docs/guide-user/base-system/uci)**

Source code is available here <http://git.openwrt.org/project/uci.git>

### What is UCI?

`UCI` is a small utility written in [C](https://en.wikipedia.org/wiki/C (programming language)) (a [shell script](https://en.wikipedia.org/wiki/shell script)-wrapper is available as well) and is intended to *centralize* the whole configuration of a device running OpenWrt. UCI is the successor of the NVRAM based configuration found in the historical OpenWrt branch [White Russian](/about/history) and a wrapper for the standard configuration files programs bring with them, like e.g. `/etc/network/interfaces`, `/etc/exports`, `/etc/dnsmasq.conf`, `/etc/samba/samba.conf` etc.

> [![NOTE](../wiki/wiki_page-techref-luci2.md)]
> UCI configuration files are located in the directory **`/etc/config/`**
>
> Their documentation can be accessed online in the OpenWrt-Wiki under [UCI configuration files](/docs/guide-user/base-system/uci).

They can be altered with any text editor or with the command line utility program `uci` or through various programming APIs (like Shell, Lua and C). The WUI [luci](/docs/techref/luci) e.g. uses Lua to manipulate them.

### Dependencies of UCI

- `libuci` a small library for UCI written in [C](https://en.wikipedia.org/wiki/C (programming language))
  - `libuci-lua` is a libuci-plugin for [Lua](https://en.wikipedia.org/wiki/Lua (programming language)) which is utilized by e.g. [luci](/docs/techref/luci)

Both are maintained in the same git as UCI.

## Packages

The functionality is provided by the two packages `uci` and `libuci`. The package `libuci-lua` is also available.

| Name       | Size in Bytes | Description                                                                                                                        |
|:-----------|---------------|------------------------------------------------------------------------------------------------------------------------------------|
| uci        | 7196          | Utility for the Unified Configuration Interface (UCI)                                                                              |
| libuci     | 18765         | C library for the Unified Configuration Interface (UCI)                                                                            |
| libuci-lua | ~6000         | libuci-plugin for [Lua](https://en.wikipedia.org/wiki/Lua (programming language)), e.g. [luci](/docs/techref/luci) makes use of it |

### Installed Files

#### uci

| path/file          | file type    | Description                                         |
|:-------------------|--------------|:----------------------------------------------------|
| /sbin/uci          | binary       | uci executable                                      |
| /lib/config/uci.sh | shell script | Shell script compatibility wrappers for `/sbin/uci` |

#### libuci

| path/file                 | file type | Description              |
|:--------------------------|-----------|:-------------------------|
| /lib/libuci.so            | symlink   | symlink to libuci.so.xxx |
| /lib/libuci.so.2011-01-19 | binary    | Library                  |

#### libuci-lua

| path/file           | file type | Description |
|:--------------------|-----------|:------------|
| /usr/lib/lua/uci.so | binary    | Library     |

## CLI behaviour

All `uci set`, `uci add`, `uci rename` and `uci delete` commands are staged in `/tmp/.uci` and written to flash at once with `uci commit`. Note that subsequent calls to uci get before uci commit will return the staged value.

The reload_config script will reload the necessary configurations based on the last `uci commit`.

This obviously does not apply to people using text editors, but to scripts, GUIs and other programs working with uci files.

## CLI Usage

Let's create a new section in `/etc/config/firewall` that looks like that:

    config zone 'guest_zone'
        option enabled '1'
        option name 'guest'
        option input 'REJECT'
        option forward 'REJECT'
        option output 'ACCEPT'
        list network 'guest_network'

Execute commands:

``` bash
# delete a section 'guest_zone' if any to start from scratch
uci -q delete network.guest_dev
# creates a section called 'guest_zone'
uci add firewall guest_zone
# specify the section type
uci set firewall.guest_zone=zone
# set enabled option
uci set firewall.guest_zone.enabled=1
uci set firewall.guest_zone.name='guest'
uci set firewall.guest_zone.input='REJECT'
uci set firewall.guest_zone.forward='REJECT'
uci set firewall.guest_zone.output='ACCEPT'
# add a list option
uci add_list firewall.guest_zone.network='guest_network'
# get the enabled option of the guest_zone section
uci get firewall.guest_zone.enabled
# show the new added section
uci show firewall.guest_zone
# show the full firewall config before commit
uci show firewall
# save the changes to /etc/config/firewall
uci commit firewall
```

## ubus interface (rpcd)

If you want to access or modify uci configuration via ubus, [rpcd implements this](commit>?p=project/rpcd.git;a=blob;f=uci.c;h=3cd2b829efd055e3096da1499fbf2e70f5f1850b;hb=HEAD). It has its own set of commands which are not exactly the same as those in the CLI.

**Significantly**, it has its own apply/confirm/reload_config mechanism designed to support the LuCI frontend, and it does not do exactly the same thing as the reload_config script. Also, if provided with a ubus_rpc_session as the LuCI does, rather than storing staged changes in `/tmp/.uci` it stores them in `/tmp/run/rpcd/uci-<ubus_rpc_session>` (you can get the CLI to use or view these changes with `-t/-p/-P`).

## LuCI

The LuCI frontend most commonly interacts with UCI via [uci.js](https://openwrt.github.io/luci/jsapi/LuCI.uci.html). This pretends that it has ordinary get/set methods, but these get/set methods do not make calls of the backend, as it maintains its own staged changes (i.e. separate from the staged changes on the backend). The basic flow is:

- `uci.load('someconfig')` \# loads all of someconfig into memory via ubus
- `uci.set('someconfig', 'somesection', 'someoption', 'somevalue')` \# adds to the list of changes to someconfig (similar to how staged changes work in the backend)
- `uci.save()` \# stage the changes in the backend via ubus
- `uci.apply()` \# apply the changes in the backend, but with a 10 sec automatic rollback if not confirmed, implemented via ubus

However, the standard frontend handleSave/handleSaveApply methods do \_not\_ call uci.apply(), but instead call [ui.changes.apply](https://openwrt.github.io/luci/jsapi/LuCI.ui.changes.html). This in turn calls a separate [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) endpoint (not via uhttp-mod-ubus) implemented in lua (\<=OpenWrt 22) or ucode (\>=OpenWrt 23), which itself calls ubus.

**Warning**: as well as the backend uci maintaining staged changes, and the frontend uci.js maintaining staged changes, the form elements (AbstractValues) have their own view of the config (cfgvalue) which is used to determine if they should save changes (i.e. saves only occur if the cfgvalue is different from the formvalue).

------------------------------------------------------------------------

## Lua Bindings for UCI

For those who like lua, UCI can be accessed in your code via the package libuci-lua. Just install the package then, in your lua code do `require("uci")`

## API

The api is quite simple

### top level entry point

[uci.cursor()](../ucode/c_source-api-module-uci.md) instantiates a uci context instance, e.g:

``` lua
x = uci.cursor()
```

if you want to involve state vars:

``` lua
x = uci.cursor(nil, "/var/state")
```

if you need to work on UCI config files that are located in a non standard directory:

``` lua
x = uci.cursor("/etc/mypackage/config", "/tmp/mypackage/.uci")
```

### on that you can call the usual operations

Get value (returns `string` or `nil` if not found):

``` lua
x:get("config", "sectionname", "option")

-- real world example:
x:get("network", "lan", "proto")
```

Set simple string value:

``` lua
x:set("config", "sectionname", "option", "value")

-- real world example:
x:set("network", "lan", "proto", "dhcp")
```

Set list value:

``` lua
x:set("config", "sectionname", "option", { "foo", "bar" })

-- real world example:
x:set("system", "ntp", "server", {
  "0.openwrt.pool.ntp.org",
  "1.openwrt.pool.ntp.org",
  "2.openwrt.pool.ntp.org",
  "3.openwrt.pool.ntp.org"
})
```

Delete option:

``` lua
x:delete("config", "section", "option")

-- real world example:
x:delete("network", "lan", "force_link")
```

Delete section:

``` lua
x:delete("config", "section")

-- real world example:
x:delete("network", "wan6")
```

Add new anonymous section "type" and return its name:

``` lua
x:add("config", "type")
```

``` lua
> -- real world example from interpreter:
> name = x:add("network", "switch")
> print(name)
cfg0e3777
```

Add new section "name" with type "type":

``` lua
x:set("config", "name", "type")

-- real world example:
x:set("network", "wan6", "interface")
```

Iterate over all section of type "type" and invoke a callback function:

``` lua
x:foreach("config", "type", function(s) ... end)
```

In the preceding example, s is a table containing all options and two special properties:

     * ''s['.type']'' -> section type
     * ''s['.name']''  -> section name

If the callback function returns `false` \[NB: **not** `nil`!\], `foreach()` will terminate at that point without iterating over any remaining sections. `foreach()` returns `true` if at least one section exists and the callback function didn't raise an error for it; `false` otherwise.

Here's another example:

``` lua
> -- real world example from interpreter:
> x:foreach("system", "led", function(s)
>>     print('------------------')
>>     for key, value in pairs(s) do
>>         print(key .. ': ' .. tostring(value))
>>     end
>> end)
------------------
dev: 1-1.1
.anonymous: false
trigger: usbdev
.index: 2
name: USB1
interval: 50
.name: led_usb1
.type: led
sysfs: tp-link:green:usb1
------------------
dev: 1-1.2
.anonymous: false
trigger: usbdev
.index: 3
name: USB2
interval: 50
.name: led_usb2
.type: led
sysfs: tp-link:green:usb2
------------------
.name: led_wlan2g
.type: led
name: WLAN2G
trigger: phy0tpt
sysfs: tp-link:blue:wlan2g
.anonymous: false
.index: 4
```

Move a section to another position. Position starts at 0. This is for example handy to change the wireless config order (changing priority).

``` lua
x:reorder("config", "sectionname", position)
```

Discard any changes made to the configuration, that have not yet been committed:

``` lua
x:revert("config")
```

commits (saves) the changed configuration to the corresponding file in `/etc/config`

``` lua
x:commit("config")
```

That's basically all you need.

#### About uci structure

It took me some time to understand the difference between "section" and "type". Let's start with an example:

    #uci show system
    system.@system[0]=system
    system.@system[0].hostname=OpenWrt
    system.@system[0].timezone=UTC
    system.@rdate[0]=rdate
    system.@rdate[0].server=ac-ntp0.net.cmu.edu ptbtime1.ptb.de ac-ntp1.net.cmu.edu ntp.xs4all.nl ptbtime2.ptb.de cudns.cit.cornell.edu ptbtime3.ptb.de

Here, `x:get("system","@rdate[0]","server")` won't work. rdate is a type, not a section.

Here is the return of `x:get_all("system")`:

``` lua
{
  cfg02f02f = {
    [".name"] = "cfg02f02f",
    [".type"] = "system",
    hostname = "OpenWrt",
    [".index"] = 0,
    [".anonymous"] = true,
    timezone = "UTC"
  },
  cfg04e10c = {
    [".name"] = "cfg04e10c",
    [".type"] = "rdate",
    [".index"] = 1,
    [".anonymous"] = true,
    server = {
      "ac-ntp0.net.cmu.edu",
      "ptbtime1.ptb.de",
      "ac-tp1.net.cmu.edu",
      "ntp.xs4all.nl",
      "ptbtime2.ptb.de",
      "cudns.cit.cornell.edu",
      "ptbtime3.ptb.de"
    }
  }
}
```

`[".type"]` gives the type of the section;

`[".name"]` gives the real name of the section (note that these names are auto-generated);

`[".index"]` is the index of the list (starting from 1);

From what I know, there seem to be no way to access `"@rdate[0]"` directly. You have to iterate with `x:foreach` to list all the elements of a given type.

I use the following function:

``` lua
uci=require("uci")
function getConfType(conf,type)
   local curs=uci.cursor()
   local ifce={}
   curs:foreach(conf,type,function(s) ifce[s[".index"]]=s end)
   return ifce
end
```

`getConfType("system","rdate")` returns:

``` lua
{
  {
    [".name"] = "cfg04e10c",
    [".type"] = "rdate",
    [".index"] = 1,
    [".anonymous"] = true,
    server = {
      "ac-ntp0.net.cmu.edu",
      "ptbtime1.ptb.de",
      "ac-ntp1.net.cmu.edu",
      "ntp.xs4all.nl",
      "ptbtime2.ptb.de",
      "cudns.cit.cornell.edu",
      "ptbtime3.ptb.de"
    }
  }
}
```

So if you want to modify `system.@rdate[0].server` you need to iterate the type, retrieve the section name `[".name"]` and then call:

``` lua
x:set("system","cfg04e10c","server","zzz.com")
```

Hope this helps.

Sophana

(Luci has however a [Cursor:get_first](https://openwrt.github.io/luci/api/modules/luci.model.uci.html#Cursor.get_first) function that is similar to get except it takes a type instead as section as second argument.)

------------------------------------------------------------------------

## Usage outside of OpenWrt

If you want to use the libuci apart from OpenWrt (for e.g. you are developing an application in C on your host computer) then prepare as follows: Note that libuci depends on \[libubox\]

Grab the source.

    git clone https://git.openwrt.org/project/uci.git

Go to the source directory (where the [CMakeLists.txt](../wiki/wiki_page-guide-developer-creating-a-cmake-package-in-openwrt.md) lives) and optionally configure the build without Lua bindings:

    cd uci/; cmake [-D BUILD_LUA:BOOL=OFF] .

Build and install uci as root (this will install uci into /usr/local/, see this thread on how to install and use uci without root permissions in your home directory: <https://forum.openwrt.org/viewtopic.php?id=40547>):

    make install

**Setup library search paths using `ld.so.conf`**

Setting your system library search path can be done in many ways, and is largely out of scope of the OpenWrt wiki.

Open /etc/ld.so.conf and add the place where you installed the uci library:

    vi /etc/ld.so.conf

Add this line somewhere to /etc/ld.so.conf

    /usr/local/lib

Execute ldconfig as root to apply the changes to /etc/ld.so.conf

    ldconfig

**Setup library search paths using `Using LD_LIBRARY_PATH`**

Alternatively, just `export LD_LIBRARY_PATH=<where/you/installed/the/.so>`

**Building your own application**

To compile your application you have to link it against the uci library. Append -luci in your Makefile:

    $(CC) test.o -o test -luci

And examples on how to use UCI in C can be found in this thread: <https://forum.openwrt.org/viewtopic.php?pid=183335#p183335> To get more examples look into the source directory of uci which you got by git clone and open cli.c or ucimap-example.c

## See also

1.  [UCI command usage](https://wiki.teltonika-networks.com/view/UCI_command_usage)
