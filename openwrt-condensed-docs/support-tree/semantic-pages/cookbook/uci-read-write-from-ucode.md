---
title: UCI Read/Write from ucode
module: cookbook
origin_type: authored
token_count: 2648
source_file: L1-raw/cookbook/uci-read-write-from-ucode.md
last_pipeline_run: '2026-03-27T07:16:36.403470+00:00'
source_locator: content/cookbook-source/uci-read-write-from-ucode.md
description: Concrete guide to reading and writing UCI configuration from a ucode
  script or rpcd plugin, covering cursor lifecycle, get/set/commit, section iteration,
  and error handling.
era_status: current
when_to_use: Use when writing a ucode script or rpcd plugin that needs to read or
  write OpenWrt configuration. UCI is the correct storage mechanism for persistent,
  user-editable config on OpenWrt -- do not read /etc/config files directly or write
  config with shell heredocs.
related_modules:
- ucode
- uci
- luci-examples
verification_basis: Corpus review of ucode/c_source-api-module-uci.md; cursor() API
  verified from ucode module docs; uci.get/set/commit signatures confirmed; luci-examples/example_app-luci-app-example-root-usr-share-rpcd-ucode-example-uc.md
  for real-world cursor pattern
reviewed_by: placeholder
last_reviewed: '2026-03-23'
---
# UCI Read/Write from ucode

> **When to use:** Use when writing a ucode script or rpcd plugin that needs to read or write OpenWrt configuration. UCI (`/etc/config/`) is the correct persistent config mechanism on OpenWrt. Reading files in `/etc/config/` directly with `open()` or writing them with string output is fragile, bypasses locking, and does not integrate with `procd_add_reload_trigger`.
> **Key components:** ucode, uci module, cursor API
> **Era:** Current (23.x+). The `cursor()` API wraps libuci and is the standard access mechanism in ucode scripts. Shell-based `uci get` calls from within ucode are never the right approach.

## Overview

OpenWrt's UCI (Unified Configuration Interface) stores all user-editable configuration in structured text files under `/etc/config/`. The ucode `uci` module exposes a `cursor()` API that reads, modifies, and commits these files with proper locking and change batching. Changes made to a cursor are staged in memory until `cursor.commit()` is called — before commit, other processes cannot see the pending changes.

The cursor pattern separates concerns cleanly: `get()` and `foreach()` for reading, `set()` and `delete()` for staging changes, and `commit()` to persist. Always call `commit()` after a write sequence. Always call `unload()` when done with a config file to release the in-memory cache.

This guide covers the four most common operations: reading a single option, iterating sections, writing an option, and adding a new section.

## Complete Working Example

```ucode
#!/usr/bin/env ucode
'use strict';

// Import cursor from the uci module. This is the standard import pattern.
import { cursor } from 'uci';

// ── Reading ──────────────────────────────────────────────────────────────────

// Create a new cursor instance. Each cursor has independent staging state.
const uci = cursor();

// get(config, section, option) -- returns the option value as a string,
// or null if the config/section/option does not exist.
const hostname = uci.get('system', '@system[0]', 'hostname');
print(`hostname: ${hostname}\n`);

// get_first(config, section_type, option) -- shorthand for the common case
// of a single anonymous section. Equivalent to get(config, '@type[0]', opt).
const tz = uci.get_first('system', 'system', 'timezone');
print(`timezone: ${tz}\n`);

// ── Iterating sections ───────────────────────────────────────────────────────

// foreach(config, section_type, callback) -- iterates every section of
// the named type in the config file. The callback receives a section object
// with all option values as properties plus '.name' (the section id).
uci.foreach('network', 'interface', function(section) {
    // section['.name'] is the UCI section id (e.g., 'loopback', 'lan', 'wan')
    const name = section['.name'];
    const proto = section['proto'] ?? 'unset';
    print(`interface ${name}: proto=${proto}\n`);
});

// ── Writing ──────────────────────────────────────────────────────────────────

// set(config, section, option, value) -- stages an option change.
// The change is NOT written to disk until commit() is called.
uci.set('myapp', 'main', 'port', '9090');
uci.set('myapp', 'main', 'enabled', '1');

// Commit the staged changes for the 'myapp' config file.
// Without commit(), the set() calls have no effect on disk.
const ok = uci.commit('myapp');
if (!ok) {
    warn(`uci.commit failed: ${uci.error()}\n`);
    // uci.error() returns a description of the last error, or null if no error.
}

// ── Adding a new section ─────────────────────────────────────────────────────

// add(config, section_type) -- creates a new anonymous section and returns
// the generated section id (e.g., 'cfg01234a').
const sid = uci.add('myapp', 'server');

// Set options on the new section using the returned id.
uci.set('myapp', sid, 'host', '203.0.113.1');
uci.set('myapp', sid, 'port', '443');

uci.commit('myapp');

// ── Cleanup ───────────────────────────────────────────────────────────────────

// unload() releases the cached state for a config file.
// Call it when you are done with a config to free memory.
// If you call get() again after unload(), it re-reads from disk.
uci.unload('system');
uci.unload('myapp');
```

## Step-by-Step Explanation

### Importing cursor

```ucode
import { cursor } from 'uci';
const uci = cursor();
```

`cursor` is a factory function, not a class. It returns a cursor object. Always use named import syntax (`import { cursor } from 'uci'`). The cursor has its own in-memory state — staged changes from one cursor are not visible to other cursor instances until `commit()` writes to disk.

### `uci.get(config, section, option)`

The three-argument form directly addresses a known named section and option. Returns the value as a string (or array of strings for UCI list options), or `null` if not found — never throws.

The `@type[0]` syntax addresses anonymous sections by type and index. `@system[0]` is the first section of type `system` in the `system` config file. This is the standard way to access single-section config files like `/etc/config/system`.

### `uci.get_first(config, type, option)`

Shorthand that is equivalent to `uci.get(config, '@type[0]', option)`. Use this for config files that always have exactly one section of the given type.

### `uci.foreach(config, type, callback)`

Iterates all sections of `type` in `config`. The callback receives a plain object with all option names as keys plus the special key `.name` (the section identifier). If `type` is `null`, iterates all sections regardless of type.

### `uci.set(config, section, option, value)`

Stages an in-memory change. The section must already exist — to create a new section, use `uci.add()` first. `value` can be a string (for options) or an array of strings (for UCI lists). Staged changes are private to this cursor until `commit()`.

### `uci.commit(config)`

Writes all staged changes for `config` to disk. Returns `true` on success, `false` on failure. On failure, `uci.error()` returns a description. **Always check the return value from commit**; write failures to `/etc/config/` can occur on read-only overlayfs under certain conditions.

### `uci.unload(config)`

Releases the in-memory cache for `config`. If you call `uci.get()` after `unload()`, the cursor re-reads from disk, picking up changes made by other processes since the last read. Always unload after a write sequence to keep memory usage bounded.

## Anti-Patterns

### WRONG: Reading /etc/config/ with open()

```ucode
// DO NOT DO THIS
import { open } from 'fs';
const f = open('/etc/config/myapp', 'r');
const content = f.read('all');
f.close();
// ...parse UCI text format manually
```

**Why it fails:** UCI files are not simple key=value text. The format has named sections, anonymous sections, type declarations, and list syntax that must be parsed correctly. Direct file reads bypass UCI's locking mechanism, meaning concurrent `uci commit` from another process can produce torn reads. Use `cursor().get()` instead.

### CORRECT: Read with cursor

```ucode
import { cursor } from 'uci';
const uci = cursor();
const value = uci.get('myapp', 'main', 'option');
uci.unload('myapp');
```

### WRONG: Writing config with shell UCI calls from ucode

```ucode
// DO NOT DO THIS
import { popen } from 'fs';
popen(`uci set myapp.main.port=${port}`, 'r');
popen('uci commit myapp', 'r');
```

**Why it fails:** Spawning a shell process for each UCI operation is expensive (fork + exec for every call). It also bypasses transaction semantics — if a set succeeds but the commit process fails to spawn, the config is partially written. The cursor API batches all changes in memory and writes atomically on commit.

### CORRECT: Use cursor set + commit

```ucode
import { cursor } from 'uci';
const uci = cursor();
uci.set('myapp', 'main', 'port', port);
uci.commit('myapp');
```

### WRONG: Forgetting commit()

```ucode
import { cursor } from 'uci';
const uci = cursor();
uci.set('myapp', 'main', 'enabled', '1');
// Missing: uci.commit('myapp');
// The change is lost when the cursor object is garbage collected.
```

**Why it fails:** `set()` is a staging operation. Without `commit()`, no bytes are written to disk. The configuration appears to succeed (no error is returned from `set()`) but the change does not survive process exit.

## Using uci in an rpcd plugin

In an rpcd ucode plugin, the cursor pattern is the same but code lives inside method call handlers:

```ucode
'use strict';
import { cursor } from 'uci';

const uci = cursor();

const methods = {
    get_config: {
        call: function() {
            const port = uci.get('myapp', 'main', 'port') ?? '8080';
            const enabled = uci.get('myapp', 'main', 'enabled') ?? '0';
            uci.unload('myapp');
            return { port, enabled };
        }
    },

    set_port: {
        args: { port: '0' },  // declares expected argument with type hint
        call: function(req) {
            uci.set('myapp', 'main', 'port', req.args.port);
            const ok = uci.commit('myapp');
            uci.unload('myapp');
            return { result: ok ? 'ok' : 'error', error: ok ? null : uci.error() };
        }
    }
};

return { 'luci.myapp': methods };
```

The ACL file for this plugin must grant `uci` write access to the `myapp` config:

```json
{
  "luci-app-myapp": {
    "description": "My application LuCI access",
    "read": { "uci": ["myapp"] },
    "write": { "uci": ["myapp"] }
  }
}
```

See [Architecture Overview](./architecture-overview.md) §ACL for the ACL file placement and format.

## Related Topics

- [ucode UCI module reference](../ucode/c_source-api-module-uci.md) — full cursor API with all method signatures
- [LuCI Form with UCI](./luci-form-with-uci.md) — how the browser form save triggers a ucode plugin that calls this pattern
- [Architecture Overview](./architecture-overview.md) — where the ucode/rpcd/UCI layer fits in the full stack
- [procd Service Lifecycle](./procd-service-lifecycle.md) — `service_triggers` / `procd_add_reload_trigger` for UCI-driven service reload

## Verification Notes

- `cursor()` factory function import syntax verified from `ucode/c_source-api-module-uci.md`
- `get(config, section, option)`, `get_first()`, `foreach()`, `set()`, `commit()`, `unload()`, `add()`, `error()` all verified from ucode UCI module corpus
- `@type[0]` anonymous section syntax verified from ucode module docs
- `import { cursor } from 'uci'` as standard import pattern confirmed from luci-examples corpus (`example.uc`)
- rpcd plugin return format (`return { 'luci.myapp': methods }`) confirmed from `example_app-luci-app-example-root-usr-share-rpcd-ucode-example-uc.md`
