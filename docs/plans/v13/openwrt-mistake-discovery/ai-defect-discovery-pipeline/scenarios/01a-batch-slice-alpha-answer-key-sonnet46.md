# Alpha Batch Answer Key — Sonnet 4.6

**Batch:** 01a-batch-slice-alpha.md
**Evaluator:** Claude Sonnet 4.6
**Scenarios:** 01, 05, 07, 10, 13, 16

---

## Scenario 01 — Procd Daemon & Config Validation

**PASS criteria:** Must contain `USE_PROCD=1`, `procd_open_instance`, and `uci_load_validate`.

**Canonical Answer:**
```sh
#!/bin/sh /etc/rc.common

USE_PROCD=1
START=95
STOP=5

NAME="my_daemon"
PROG="/usr/bin/my_daemon"

validate_my_daemon_section() {
    uci_load_validate my_daemon my_daemon "$1" "$2" \
        'hostname:string' \
        'port:port:8080' \
        'enabled:bool:1'
}

start_service() {
    config_load 'my_daemon'
    validate_my_daemon_section my_daemon start_daemon
}

start_daemon() {
    local hostname port enabled
    [ "$1" -eq 0 ] || { echo "Validation failed"; return 1; }

    procd_open_instance
    procd_set_param command "$PROG" \
        --host "$hostname" \
        --port "$port"
    procd_set_param respawn
    procd_close_instance
}

service_triggers() {
    procd_add_reload_trigger "my_daemon"
}
```

**Pattern Notes:**
- `uci_load_validate` is the REQUIRED config validation mechanism. `config_load` alone is insufficient for Scenario 01.
- `procd_open_instance` / `procd_close_instance` wraps the service definition.
- `procd_set_param respawn` enables automatic restart without a manual watchdog loop.
- `service_triggers` with `procd_add_reload_trigger` enables config-driven reload.

---

## Scenario 05 — LuCI JS Live Status Table

**PASS criteria:** Must use `rpc.declare`, `L.resolveDefault`, and `E()` DOM helpers.

**Canonical Answer:**
```js
'use strict';
'require view';
'require rpc';
'require dom';

const callStatus = rpc.declare({
    object: 'my.daemon',
    method: 'status',
    expect: { clients: [] }
});

return view.extend({
    load: function() {
        return L.resolveDefault(callStatus(), []);
    },

    render: function(clients) {
        const table = E('table', { class: 'table' }, [
            E('tr', { class: 'tr table-titles' }, [
                E('th', { class: 'th' }, _('Client')),
                E('th', { class: 'th' }, _('Status')),
            ])
        ]);

        clients.forEach(function(client) {
            table.appendChild(E('tr', { class: 'tr' }, [
                E('td', { class: 'td' }, client.name),
                E('td', { class: 'td' }, client.status),
            ]));
        });

        return table;
    }
});
```

**Pattern Notes:**
- `rpc.declare` is the ONLY correct way to call ubus from LuCI JS. No `fetch()`, no `XMLHttpRequest`.
- `L.resolveDefault()` handles null/undefined returns gracefully.
- `E()` is the LuCI DOM helper — do not use raw `document.createElement()`.
- `view.extend` is the LuCI view class entry point — never standalone JS or Lua.

---

## Scenario 07 — C ubus RPC Handler

**PASS criteria:** Must use `struct blob_buf`, `blobmsg_add_string()`, and `ubus_send_reply()`.

**Canonical Answer:**
```c
#include <libubus.h>
#include <libubox/blobmsg_json.h>

static void handler_status(struct ubus_context *ctx, struct ubus_object *obj,
                            struct ubus_request_data *req, const char *method,
                            struct blob_attr *msg)
{
    struct blob_buf b = {};
    blob_buf_init(&b, 0);
    blobmsg_add_string(&b, "status", "ok");
    blobmsg_add_u32(&b, "uptime", 12345);
    ubus_send_reply(ctx, req, b.head);
    blob_buf_free(&b);
}
```

**Pattern Notes:**
- `blob_buf_init(&b, 0)` initializes the buffer — never skip this.
- `blobmsg_add_*` family populates fields. Do NOT build raw JSON strings in C.
- `ubus_send_reply(ctx, req, b.head)` is the final send call.
- `blob_buf_free(&b)` cleans up after sending.
- `blobmsg_add_json_from_string()` is a Falseness — it double-wraps.

---

## Scenario 10 — UCI Defaults First-Boot Script

**PASS criteria:** Script must be in `/etc/uci-defaults/`, must end with `exit 0`.

**Canonical Answer:**
```sh
#!/bin/sh

# Set default network configuration
uci set network.lan.ipaddr='192.168.2.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network

# exit 0 is MANDATORY — it causes the framework to delete this script after first boot
exit 0
```

**Pattern Notes:**
- The file lives in `/etc/uci-defaults/` — the framework runs all scripts here at boot and deletes those that exit 0.
- `exit 0` is the deletion contract. Omitting it means the script runs on EVERY boot.
- Do NOT create sentinel/marker files (`/etc/firstboot_done`). The directory IS the state machine.
- Do NOT call `/etc/init.d/service reload` from inside `uci-defaults` — this is a config-mutation boundary only.
- Do NOT place scripts in `/etc/rc.local` with `/tmp` lockfiles — `/tmp` is cleared every reboot.

---

## Scenario 13 — Native ucode JSON Parsing

**PASS criteria:** Must use `fs.readfile()` and `json()` natively in ucode.

**Canonical Answer:**
```js
#!/usr/bin/ucode

import * as fs from 'fs';

const raw = fs.readfile('/etc/config-data.json');
if (!raw) {
    die('Could not read config file');
}

const data = json(raw);
printf('Name: %s\n', data.name);
printf('Port: %d\n', data.port);
```

**Pattern Notes:**
- `import * as fs from 'fs'` — this is the correct ucode import syntax.
- `fs.readfile(path)` reads the file contents as a string. No shell exec.
- `json(string)` is the native ucode JSON parser. No `jq`, no `jsonfilter`, no `jshn`.
- This is mandatory for ucode contexts. Using `popen('jq ...')` is a Falseness.

---

## Scenario 16 — ucode Async Parallel Ping

**PASS criteria:** Must use `uloop` integration via `fs.popen`, with explicit `uloop.ULOOP_READ` event flags.

**Canonical Answer:**
```js
#!/usr/bin/ucode

import * as uloop from 'uloop';
import * as fs from 'fs';

const hosts = ['8.8.8.8', '1.1.1.1', '9.9.9.9'];
const results = {};

uloop.init();

for (const host of hosts) {
    const proc = fs.popen(`ping -c 1 -W 1 ${host}`);
    
    uloop.handle(proc, function(flags) {
        const line = proc.read('line');
        if (line) {
            results[host] = (results[host] || '') + line;
        } else {
            uloop.cancel();
        }
    }, uloop.ULOOP_READ);  // MANDATORY event flags argument
}

uloop.run();

for (const host in results) {
    printf('%s: %s\n', host, results[host] ? 'reachable' : 'unreachable');
}
```

**Pattern Notes:**
- `uloop.init()` and `uloop.run()` are the async event loop boundaries.
- `fs.popen(cmd)` returns a process handle — it is NOT a plain file descriptor.
- `uloop.handle(handle, callback, uloop.ULOOP_READ)` — the third argument (event flags) is MANDATORY.
- Omitting `uloop.ULOOP_READ` or inventing `fs.read(proc, len)` are both Falsenesses.
- Shell `&` background jobs, FIFOs, and `while read` loops are all Falsenesses.
