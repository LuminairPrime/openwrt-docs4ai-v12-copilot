---
title: LuCI2 (OpenWrt web user interface)
module: wiki
origin_type: wiki_page
token_count: 1821
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-luci2.md
last_pipeline_run: '2026-03-20T04:40:03.869041+00:00'
language: text
ai_summary: LuCI2 is an experimental web user interface for OpenWrt, designed to replace the older Lua-based LuCI. It utilizes static HTML and JavaScript XHR for client-side rendering, significantly reducing resource consumption on devices with limited CPU and RAM. Communication with OpenWrt subsystems is handled through `ubus`, and a custom `rpcd` plugin extends `ubus` namespaces for additional functionality. The menu and views are dynamically generated, allowing for a flexible and user-specific interface.
ai_when_to_use: Use LuCI2 when developing or testing web interfaces on OpenWrt devices, especially when resource efficiency is a concern. It is suitable for environments where the traditional LuCI interface may be too demanding.
ai_related_topics:
- ubus
- uhttpd-mod-ubus
- rpcd
- luci.model.uci
- nixio.fs
---
# LuCI2 (OpenWrt web user interface)

![outdated&noheader&nofooter&noeditbtn](/page>meta/infobox/outdated&noheader&nofooter&noeditbtn)

### NOTE: This page currently mixes the five+ years old abandoned original "luci2" and the new JavaScript based standard LuCI implementation. Information on this page can be partially misleading

For years OpenWrt was using [LuCI](LuCI), a web user interface written in [Lua](http://en.wikipedia.org/wiki/Lua_(programming_language)). It required several Lua extensions (like `ubus`, `luci.model.uci`, `nixio.fs`, etc.) to access system info and settings. Unfortunately this solution appeared to be quite resource consuming and didn't work well on devices with slow CPU and little amount of RAM.

This led to developing LuCI2, a new web interface with a different architecture. It doesn't use Lua anymore, but static HTML page and [JavaScript XHR](http://en.wikipedia.org/wiki/XMLHttpRequest) method. It means building HTML pages is done on client (browser) side offloading OpenWrt device. To access any kind of system data [ubus](ubus) is used (with the help of [uhttpd-mod-ubus](ubus#access_to_ubus_over_http) to provide [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) based API).

LuCI2 is still experimental. Its predecessor is still used by default in all builds, including the trunk.

## Implementation details

As explained above, LuCI2 uses `ubus` to communicate with OpenWrt subsystems (that includes for example `network` and `service` but also many others). Unfortunately not every major OpenWrt tool registers itself with `ubus`. For example it's not possible to use `opkg` (packages management) that way. LuCI2 resolves this problem providing it's own `rpcd` plugin which adds extra `ubus` namespaces. For the previous example of `opkg` it registers new `luci2.opkg` path in the `ubus`.

To sum up, LuCI2 consists of two things: a pack of HTML/CSS/JS files (`htdocs`) and few extra small tools working in the OpenWrt environment.

In next sections you will find details about various LuCI2 parts that should help in the development.

### Menu

The first thing to know about LuCI2 menu is that it is not hardcoded in any file received by a browser. Instead of that, it's provided by `ubus` using `luci2.ui` path and `menu` method. For debugging purposes menu layout can be verified using:

    ubus call luci2.ui menu '{ "ubus_rpc_session": "invalid" }'

Internally `rpcd` plugin parses all files located in `/usr/share/rpcd/menu.d`, joins them and removes entries that are not available for a current user (based on a passed `ubus_rpc_session`). This results in a two-level menu limited to entries that current has rights to.

Top level entries are defined using following JSON:

    "foo": {
        "title": "Foo",
        "index": 12
    }

(and ordered using `index` values).

Second level entries are defined in a similar way:

    "foo/bar": {
        "title": "Bar",
        "acls": [ "baz", "qux" ],
        "view": "foo/bar",
        "index": 5
    }

Please note that second level entries may be located in separated files. This allows easy addition of new entries without modifying existing files.

### Templates

Every LuCI2 subpage has to have it's template located in `/www/luci2/template/`. These are very simple HTML files providing place for a content. Please note they don't contain references to any variables, it's JavaScript role to access them and fill with a content. The only special syntax in these files is for internationalization (i18n) system that uses following special tags:

    <p><%:Hello world%></p>

### Views

Apart from a template, every LuCI2 subpage requires also it's view to be defined and placed in `/www/luci2/view/`. Views are JavaScript files extending `L.ui.view` using subpage specific object. They are obligated to provide `execute` method that will be called after loading a template. Optionally they may also provide subpage `title` and `description`.

A bit of attention requires `execute` method. Building a view may fail because of various reasons, especially when it requires loading extra data using `ubus`. So it makes sense for `execute` method to provide info if it succeed or failed. Unfortunately it can't simply return `true` of `false`, as loading extra data is done asynchronously. To resolve this problem a `Promise` object should be returned which allows to postpone taking a decision about a success or failure.

The simplest view could look like this:

    L.ui.view.extend({
        title: L.tr('Foo'),         /* Optional title */
        description: 'Bar',         /* Optional description */

        execute: function() {
            var deferred = $.Deferred();    /* Create a new Deferred object */
            deferred.resolve();     /* Resolve it immediately, there is nothing that could fail */
            return deferred.promise();  /* Return Promise object (a subset of Deferred) */
        }
    });

### Communication with ubus

Before starting, please know that LuCI2 provides many helpers for accessing [UCI](UCI) system. To write a simple view managing config files in `/etc/config/`, the full understanding of `ubus` calls is not required and this section can be skipped.

For more complicated LuCI2 views it's good to first figure out all needed `ubus` calls. A complete list of objects and methods can be listed using `ubus -v list` command.

Below is an example of simple call to `log` object and `write` method. It requires `event` parameter to be passed as an argument. When using `ubus` command-line tool, this call could be done with:

    ubus call log write '{ "event": "Foo" }'

LuCI2 provides a helper for `ubus` communication called `L.rpc.declare`. This is JavaScript helper magically creating a function that will call specified `ubus` method. Please note that at declaring time no call is executed and no arguments are passed. This is only preparing a function that will be used later. Below is an example function calling `log` object and it's `write` method:

    var writeToLog = L.rpc.declare({
        object: 'log',
        method: 'write',
        params: [ 'event' ]
    })

Once declared such a function, it can be called at anytime simply using:

    writeToLog('Foo');

In the above example result of the call was silently ignored. It's not an option if view has to access data returned by an `ubus` call. The next example will access `info` method of the `system` object. In the command-line this would be following call:

    # ubus call system info
    {
        "uptime": 123,
        "localtime": 1234567890,
        "load": [
            1,
            2,
            3
        ],
        "memory": {
            "total": 67108864,
            "free": 33554432,
            "shared": 0,
            "buffered": 16777216
        },
        "swap": {
            "total": 0,
            "free": 0
        }
    }

When using LuCI2 (and JavaScript) declaration for the above call should look like this:

    var readSystemInfo = L.rpc.declare({
        object: 'system',
        method: 'info',
        expect: { memory: { } }         /* Optional, extracts only part of the result */
    })

Accessing result of the call requires using a simple `.then` function:

    readSystemInfo().then(function(memory) {
        console.log(memory);
    });

### Dependencies of LuCI2

- `libubox` (~ 12KiB) is a general purpose library which provides things like an event loop, binary blob message formatting and handling, the Linux linked list implementation, and some JSON helpers. The functions in `libubox` are used to write the other software in LuCI2
- `ubox`
- `ubus` (~ 13KiB) is an [IPC](https://en.wikipedia.org/wiki/Inter-process_communication) daemon similar to D-Bus but with a much friendlier C API
- `mountd`
- `rpcd`
