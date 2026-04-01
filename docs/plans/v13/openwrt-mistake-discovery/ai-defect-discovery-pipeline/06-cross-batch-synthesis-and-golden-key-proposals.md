# Cross-Batch Synthesis & Golden Key Proposals

**Date:** 2026-03-30
**Evaluator Sessions:** Multiple (Gemini Flash, GPT-5.4, Claude Opus 4.6 Thinking, Claude Sonnet 4.6)
**Batches Covered:** Alpha (S01/05/07/10/13/16), Beta (S02/04/08/11/12/17)
**Note:** Gamma batch results are excluded — lost and not being reconstituted.

---

## Part 1: Executive Summary

The Alpha and Beta evaluation campaigns tested a 16-model field across 12 distinct OpenWrt development scenarios. Across ~220 scorable scenario instances, the pipeline revealed four categories of model failure, one confirmed high-performer tier, and a set of architectural blind spots that constitute P0 documentation priorities.

**TLDR:** The biggest single finding is that **zero models across both batches demonstrated correct knowledge of `ucode`'s async event model** (`uloop.handle()` + `uloop.ULOOP_READ` flags). The second-biggest finding is that **only 2 out of 10 Beta models** used the modern `L.ui` + `widgets.NetworkSelect` LuCI JS pattern — a pattern with a near-zero pass rate across both batches.

---

## Part 2: Model Performance Tier Classification

### Tier 1: Elite (Correctness-First)
Models that demonstrated mastery across multiple architectural domains, including at least one hard scenario.

| Model | Alpha | Beta | Notes |
| :--- | :--- | :--- | :--- |
| **GPT 5.2 High** | 4/6 (67%) | N/A | Only model to correctly use `rpc.declare` in Alpha. |
| **Claude Opus 4.6 (Thinking)** | 3/6 (50%) | 5/6 (83%) | Best beta score. Narrow misses only. |

### Tier 2: Standard (Competent Core)
Models that correctly handled procd, C ubus, and UCI basics but consistently failed modern LuCI JS and ucode async patterns.

| Model | Alpha | Beta | Combined |
| :--- | :--- | :--- | :--- |
| Claude Sonnet 4.6 | 3/6 | 4/6 | 7/12 (58%) |
| Gemini Flash Thinking | 3/6 | N/A | — |
| Gemini Pro | 3/6 | N/A | — |
| GLM-5 | 3/6 | 3/6 | 6/12 (50%) |
| Hearth | 3/6 | 3/6 | 6/12 (50%) |
| Kimi k2.5 | 3/6 | N/A | — |
| Qwen 3.5 Max Preview | 2/6 | 3/6 | 5/12 (42%) |
| Dola Seed 2.0 | 2/6 | 3/6 | 5/12 (42%) |
| Minimax m2.7 | 2/6 | 3/6 | 5/12 (42%) |

### Tier 3: Fragmented (Selective Knowledge)
Models that demonstrated strong knowledge in some domains but had significant architectural gaps elsewhere.

| Model | Alpha | Beta | Notes |
| :--- | :--- | :--- | :--- |
| Mimo v2 Pro | 1/6 | 3/6 | Stochastic performance — see note below. |
| Significant Otter | 1/6 | N/A | Fabricated APIs, wrong signatures. |
| Grok 4.20 | 2/6 | N/A | Missing `exit 0` across scenarios. |

**Note on Mimo v2 Pro Stochastic Anomaly:** Mimo v2 Pro scored only 1/6 on Alpha but 3/6 on Beta, and 11/17 (65%) on the full-run file. This is a significant scoring inconsistency that suggests Mimo's knowledge is highly context-dependent — it may require more contextual setup or chain-of-thought scaffolding to activate its correct architectural knowledge.

### Tier 4: Critical Gaps (Requires Remediation)
| Model | Alpha | Notes |
| :--- | :--- | :--- |
| Nvidia Nemotron | 0/6 | SysVinit throughout. PID files. Fabricated APIs. |
| DeepSeek V3 32B | 2/6 | Sentinel files. Legacy shell JSON. |

---

## Part 3: Universal Blind Spots (0% or Near-0% Pass Rates)

The following four scenarios represent the most critical documentation deficiencies across the entire model field:

### Blind Spot 1: ucode Native JSON Parsing (Alpha S13 — 0% pass)
**Every model** in both batches used `jsonfilter`, `jshn`, `jq`, or `awk` instead of native `ucode` `fs.readfile()` + `json()`. This is the single largest confirmed training data gap.

**Required pattern:**
```js
import * as fs from 'fs';
const data = json(fs.readfile('/path/to/file.json'));
```

### Blind Spot 2: ucode Async Event Loop (Alpha S16 — 0% pass)
**Every model** used shell `&` background jobs, FIFOs, or `while read` loops instead of native `uloop` integration with correct event flags.

**Required pattern:**
```js
uloop.handle(proc, callback, uloop.ULOOP_READ);  // event flags MANDATORY
```

### Blind Spot 3: Modern LuCI JS Frontend (Alpha S05 — 6%; Beta S04 — 20%)
The `rpc.declare` / `L.ui` / `widgets.NetworkSelect` pattern remains near-absent across all model outputs. Legacy Lua CBI dominates.

### Blind Spot 4: C Daemon Init Order / `ubus_add_uloop` (Beta S12 — 40% pass; 60% failure)
The `ubus_add_uloop()` call after `ubus_connect()`, required to register the ubus socket with the event loop, was omitted by the majority of models. Without it, the daemon enters `uloop_run()` but never receives ubus calls.

---

## Part 4: Confirmed Golden Key Additions

The following entries were validated by the evaluation pipeline and should be treated as authoritative additions to `03-golden-answers-key.md`:

### New General Truths
1. `jshn.sh` with `json_init`, `json_load`, `json_get_var` is a valid **shell-tier** JSON API (one level below ucode, one level above raw `jsonfilter`).
2. `L.ready()` and the modern LuCI JS runtime (`rpc.declare`, `E()`, `view.extend`) are the correct client-side entry points for LuCI views.
3. The correct C daemon initialization order is: `uloop_init()` → `ubus_connect()` → `ubus_add_uloop()` → `uloop_run()`.

### New General Falsenesses
1. **FIFO-based parallel processing** — `mkfifo` + `while read` loops — is a Shell Hacks Falseness.
2. **Standalone CGI scripts** in `/www/cgi-bin/` bypass LuCI architecture entirely.
3. **`blobmsg_add_json_from_string()` double-wrap** — building JSON with `json-c` then injecting as a blob string — is a C RPC Falseness.
4. **Fabricated ubus API functions** — `ubus_request_set_result()`, `ubus_add_workhandler()` — do not exist in the real `libubus` API.
5. **PID file management** — `echo $! > /var/run/daemon.pid` — is a SysVinit-era Falseness replaced by procd.
6. **`/tmp` lockfile for first-boot** — `/tmp` is cleared every reboot; this runs the script on every boot.
7. **Self-deleting `uci-defaults` scripts** — manual `rm -f $0` shows misunderstanding of the `exit 0` deletion contract.
8. **Non-existent ubus methods** — `network.get_wireless_clients` is fabricated.
9. **Missing `ubus_add_uloop()`** — entering `uloop_run()` without it means ubus calls are never received.
10. **Calling `ubus_connect()` before `uloop_init()`** — incorrect initialization order for C daemons.
11. **Omitting `uloop.ULOOP_READ` event flags** from `uloop.handle()` calls in ucode async scripts.
12. **Inventing `fs.read(proc, len)` for async process I/O** — `fs.popen()` is the process handle API; raw descriptor reads are not exposed.

---

## Part 5: Golden Key Proposals for New Documentation

Based on the identified blind spots, the following documentation pages are proposed as P0 and P1 priorities for the `openwrt-docs4ai` project:

### P0: `uci_load_validate` Complete Cookbook Page
- Current state: Mentioned in existing procd docs, but no standalone page with complete validation schema examples.
- Required: Full example showing `validate_*_section` + `uci_load_validate` + typed field specifications.
- Evidence: Beta `ubus_add_uloop` gap is adjacent — the validation contract is equally unknown.

### P0: Modern LuCI JS Forms (Expand Existing)
- Current state: Some LuCI JS content exists but `L.ui` and `widgets.NetworkSelect` patterns are not prominently documented.
- Required: Standalone example showing `form.Map` + `form.ListValue` + `widgets.NetworkSelect` complete view.
- Evidence: Both Alpha S05 and Beta S04 near-zero pass rates.

### P1: C ubus/libubox Service Skeleton
- Current state: No complete cookbook page with correct `uloop_init` + `ubus_add_uloop` + `uloop_run` boilerplate.
- Required: Fully working C daemon skeleton with annotated initialization order.
- Evidence: Beta S12 40% pass rate; `ubus_add_uloop` universally unknown.

### P1: ucode Async/Native JSON Task Patterns
- Current state: No complete page covering `uloop.handle()` + `uloop.ULOOP_READ` patterns.
- Required: Full async parallel processing example with event flags and `fs.popen()`.
- Evidence: Alpha S13 and S16 both 0% pass rate.

---

## Part 6: AI Agent Cookbook — Critical OpenWrt Development Lessons

The following lessons are distilled from the evaluation pipeline findings. Each entry maps a specific AI failure pattern to the correct canonical code reference. These are intended as targeted documentation additions for AI agent training.

### Category: procd / Init System

**1. `uci_load_validate` is mandatory in procd services — not optional config validation.**
The `config_load` + `config_get` shell pattern is insufficient for modern procd services. Every `start_service()` implementation must call `uci_load_validate` with a typed field specification before accessing any configuration values. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 01 canonical answer.

**2. `procd_set_param respawn` replaces all manual watchdog loops.**
Setting `procd_set_param respawn` inside `procd_open_instance` / `procd_close_instance` instructs procd to automatically restart the daemon on crash. Never implement a `while(1) { if ! pgrep ...; then restart; fi; sleep 5; }` watchdog. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 01 canonical answer.

**3. `service_triggers` with `procd_add_reload_trigger` enables config-driven reload.**
The `service_triggers()` shell function must call `procd_add_reload_trigger "package_name"` to wire UCI config changes to automatic service reload. Without it, `uci commit` changes do not propagate to running services.

### Category: uci-defaults / First-Boot

**4. `exit 0` is the deletion contract — omitting it makes the script run on every boot.**
A script in `/etc/uci-defaults/` is deleted ONLY IF it exits with code 0. Omitting `exit 0` causes the script to re-execute on every boot. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 10 canonical answer.

**5. Sentinel files in `uci-defaults` defeat the entire pattern.**
Creating a file like `/etc/firstboot_done` to track whether a `uci-defaults` script has already run is architecturally wrong. The `uci-defaults` directory itself IS the state machine — once a script exits 0, it is deleted. The absence of the script IS the record of successful execution. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 10, Falseness section.

**6. `/etc/init.d/service reload` must NOT be called from `uci-defaults`.**
A `uci-defaults` script runs during early boot, before services are fully started. Calling `/etc/init.d/network reload` from within a `uci-defaults` script violates the configuration-mutation boundary. Apply UCI values only; let normal boot sequencing apply them. Reference: `results/beta/mimo-v2-pro-20260328-0901am-score-20260328-0554pm.md` — Scenario 10 failure.

### Category: LuCI JavaScript Frontend

**7. `rpc.declare` is the ONLY correct way to call ubus from a LuCI JS view.**
Direct `fetch()`, `XMLHttpRequest`, or custom REST calls from a LuCI view are architectural Falsenesses. All system data must flow through `rpc.declare({ object, method, expect })`. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 05 canonical answer.

**8. `L.resolveDefault()` is mandatory when calling RPC in a LuCI view's `load()` method.**
Without `L.resolveDefault(callMyRpc(), fallback)`, a null response from ubus (e.g., service not running) will crash the view render. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 05 canonical answer.

**9. LuCI form views must use `form.Map`, not raw HTML `<form>` elements.**
`form.Map('package', 'Title')` is the LuCI binding class that wires a form to a UCI package. Building raw HTML `<form>` tags or `<input>` elements bypasses the entire LuCI form lifecycle (load, save, apply). Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 04 canonical answer.

**10. `widgets.NetworkSelect` provides the dynamic interface dropdown — do not `fetch()` interface names manually.**
The `widgets.NetworkSelect` form option type automatically queries the available network interfaces from netifd via the LuCI RPC layer. Calling `fetch('/cgi-bin/interfaces')` or hardcoding interface names is a Falseness. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 04 canonical answer.

**11. `L.ui` must be called when performing UI-level actions in a LuCI view render.**
`L.ui.addNotification()`, `L.ui.showModal()`, and related functions handle UI state management within the LuCI SPA framework. Skipping `L.ui` and manipulating the DOM directly is an architectural Falseness. Reference: `results/beta/mimo-v2-pro-score-20260330.md` — Scenario 04 analysis.

**12. The LuCI menu system uses JSON files in `/usr/share/luci/menu.d/` — not Lua `index.lua` controllers.**
A menu entry must be a JSON file under `/usr/share/luci/menu.d/` defining `title`, `action`, and `type: "view"`. The legacy `index.lua` controller pattern is deprecated and a Falseness for new development. Reference: `scenarios/03-golden-answers-key.md` — Scenario 14.

### Category: ucode Language

**13. `import * as ubus from 'ubus'` — this exact import form is required for native ubus access.**
Using any variant like `const ubus = require('ubus')` or executing `ubus call` as a subprocess inside ucode is a Falseness. The import module system is mandatory. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 02 canonical answer.

**14. `ubus.conn()` creates the ubus connection — there is no other constructor.**
Models frequently invent alternative constructors like `new ubus.Client()` or `ubus.open()`. The only correct call to establish a ubus connection in ucode is `ubus.connect()`. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 02 canonical answer.

**15. `import * as uci from 'uci'` — the uci module import pattern for ucode.**
Must be followed by `uci.cursor()` to get a cursor object. No other instantiation method exists. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 08 canonical answer.

**16. `cursor.save()` then `cursor.commit()` — both calls are required for persistent UCI changes.**
`cursor.set()` modifies in-memory state only. `cursor.save()` writes to the staging run-time files. `cursor.commit()` flushes to flash. Omitting `cursor.commit()` means changes survive until reboot only. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 08 canonical answer.

**17. `fs.readfile(path)` returns the file contents as a string — no shell subprocess needed.**
The ucode `fs` module provides native file I/O. There is no correct use case for calling `popen('cat /path/to/file')` to read a file. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 13 canonical answer.

**18. `json(string)` is the native ucode JSON parser — `jq`, `jsonfilter`, and `jshn` are all Falsenesses in ucode context.**
When operating inside a ucode script, use `json(fs.readfile('/path/to/data.json'))`. Executing external JSON parsers as subprocesses defeats the purpose of native ucode. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 13 canonical answer.

### Category: ucode Async / uloop

**19. `uloop.init()` must be called before any uloop handles are registered.**
The uloop event loop must be initialized before `uloop.handle()` or any async operation is registered. There is no lazy initialization — calling `uloop.handle()` before `uloop.init()` produces undefined behavior. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 16 canonical answer.

**20. `uloop.handle(handle, callback, uloop.ULOOP_READ)` — the third argument (event flags) is MANDATORY.**
Every model that attempted `uloop.handle()` omitted the `uloop.ULOOP_READ` flag. Without it, the callback is never triggered when data arrives. This is the single most common uCode async failure. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 16 canonical answer.

**21. `fs.popen(cmd)` returns a process handle, not a raw file descriptor.**
Models frequently attempt to call `fs.read(proc, bytes)` after `fs.popen()`, inventing a raw descriptor read API that does not exist. The correct pattern is to pass the `proc` handle to `uloop.handle()` and use `proc.read('line')` inside the callback. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 16 canonical answer.

**22. Shell `&` background jobs in ucode are a Falseness for parallel async work.**
Using `system('ping -c1 host &')` or similar shell backgrounding from within ucode is the exact anti-pattern that `uloop` was designed to replace. All async parallelism must flow through `uloop.handle()`. Reference: `scenarios/03-golden-answers-key.md` — Universal General Falseness section.

**23. `uloop.run()` is the blocking entry point — it returns only on `uloop.cancel()` or signal.**
After registering all handles, `uloop.run()` must be called to enter the event loop. Code after `uloop.run()` is cleanup code, not normal flow.

### Category: C libubus / libubox

**24. C daemon initialization order is strict: `uloop_init()` → `ubus_connect()` → `ubus_add_uloop()` → `uloop_run()`.**
Inverting the first two calls (calling `ubus_connect()` before `uloop_init()`) is architecturally incorrect. `ubus_add_uloop()` is required to register the ubus socket file descriptor with the event loop — without it, the daemon runs but never processes any ubus calls. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 12 canonical answer.

**25. `ubus_add_uloop(ctx)` is the binding call that makes ubus work inside `uloop_run()`.**
This is the single most commonly omitted call in C daemon skeletons. Without it, `uloop_run()` runs the event loop but the ubus socket is not registered as a monitored file descriptor, so no ubus method calls are ever dispatched. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 12 canonical answer; `results/beta/beta-batch-scoring-summary-20260330.md` — S12 analysis.

**26. `blob_buf_init(&b, 0)` must precede all `blobmsg_add_*` calls in C RPC handlers.**
Failing to initialize the blob buffer before populating it is undefined behavior in C. The initialization call is `blob_buf_init(&b, 0)` — not zero-initialization of the struct alone.

**27. `blobmsg_add_string()` and `blobmsg_add_u32()` are the correct field-population APIs — never build raw JSON strings.**
Using `sprintf(buf, "{\"status\":\"ok\"}")` and then attempting to send it as a ubus reply is a C RPC Falseness. All reply data must be built through the `blobmsg_add_*` family. Reference: `scenarios/03-golden-answers-key.md` — Universal General Falseness, C RPC Anti-Patterns.

**28. `ubus_send_reply(ctx, req, b.head)` is the final and only send call — no alternative.**
Models frequently invent non-existent functions like `ubus_request_set_result()` or `ubus_reply_object()`. The only correct call is `ubus_send_reply(ctx, req, b.head)`. Reference: `scenarios/01a-batch-slice-alpha-answer-key-sonnet46.md` — Scenario 07 canonical answer.

**29. `blob_buf_free(&b)` must be called after `ubus_send_reply()` to release memory.**
The blob buffer allocates heap memory. Failing to call `blob_buf_free()` after the reply creates a memory leak in long-running RPC handlers.

**30. `blobmsg_parse()` with a registered `blobmsg_policy` array is the ONLY correct way to parse incoming ubus message arguments.**
Attempting to blindly cast the `struct blob_attr *msg` pointer or iterate raw memory bytes is a C RPC Falseness. Reference: `scenarios/03-golden-answers-key.md` — Scenario 15.

**31. `ubus_add_object()` registers a ubus object — prerequisite for any method to be callable.**
Without `ubus_add_object(ctx, &my_object)`, the object's methods are defined in the code but are not registered with the ubus daemon, making them unreachable from other processes.

### Category: OpenWrt Makefile / Package System

**32. `include $(TOPDIR)/rules.mk` must be the first include — it defines cross-compilation variables.**
Placing other includes before `$(TOPDIR)/rules.mk` will cause undefined variable errors during build since target compiler paths and flags are set by this file.

**33. `DEPENDS:=+libubus` is the correct runtime dependency for applications linking against libubus.**
Omitting it means the package may install cleanly on a system that happens to have libubus but will fail on a minimal system. The `+` prefix indicates a runtime dependency.

**34. `PKG_HASH` is the current field for source integrity — `PKG_MD5SUM` is deprecated.**
Using `PKG_MD5SUM` in a modern OpenWrt Makefile produces a build warning and may fail validation in strict environments. Reference: `scenarios/03-golden-answers-key.md` — Scenario 11.

**35. `$(eval $(call BuildPackage,pkg_name))` is the mandatory final line of every OpenWrt package Makefile.**
Without this macro invocation, the package is defined but never registered with the build system — it will not appear in `make menuconfig`.

### Category: Hotplug / Event System

**36. Hotplug scripts must read `$ACTION` and `$INTERFACE` environment variables — these are pushed by netifd.**
The values are not in any config file or ubus object. They are injected into the hotplug script's environment by the kernel/netifd hotplug mechanism. Polling or querying for them is incorrect. Reference: `scenarios/03-golden-answers-key.md` — Scenario 09.

**37. Hotplug scripts must exit early for unrelated `$ACTION` values before causing any side effects.**
A hotplug script in `/etc/hotplug.d/iface/` is called for EVERY interface event. Failing to filter on `$ACTION == "ifup"` (for example) before executing payload code causes the side effects to run on `ifdown`, `ifupdate`, and every other event type.

### Category: ucode Import/Export System

**38. `import * as module from 'module'` is the ucode import syntax — CommonJS `require()` does not exist.**
ucode uses ES module-like syntax with `import * as name from 'name'`. There is no `require()`, no `module.exports`, and no CommonJS-style loading. Reference: `scenarios/01b-batch-slice-beta-answer-key-sonnet46.md` — Scenario 02 canonical answer.

**39. Built-in ucode modules are imported by name — `'ubus'`, `'uci'`, `'fs'`, `'uloop'`, `'nl80211'`, `'rtnl'`.**
These module names are fixed and correspond to compiled C extension modules shipped with ucode. Inventing names like `'network'` or `'system'` will produce import errors.

### Category: Architecture / Era Awareness

**40. OpenWrt has a "modern era" boundary (approximately 2019–2022) that separates deprecated from current patterns.**
Code written for OpenWrt 18.x or earlier used Lua CBI, swconfig, ash shell scripts, and `jsonfilter`. Modern OpenWrt (21.02+) uses LuCI JS views, DSA, ucode, and `uloop`. Generating pre-2022 patterns for modern OpenWrt is a Falseness.

**41. Lua CBI (`m = Map(...)`) is deprecated for new LuCI development.**
While Lua CBI still works on existing installations, all new LuCI views must be written in JavaScript using `view.extend`, `form.Map`, and the `rpc.declare` family. Generating Lua CBI for a "new page" request is a Falseness. Reference: `scenarios/03-golden-answers-key.md` — Universal General Falseness, Frontend.

**42. `systemd` does not exist on OpenWrt — procd is the init system.**
Generating `systemd` unit files, `ExecStart`, `WantedBy=multi-user.target` or any `systemctl` commands is an immediate universal Falseness. Reference: `scenarios/03-golden-answers-key.md` — Universal General Falseness, Init Systems.

**43. `ip` and `ifconfig` commands do not persist network configuration on OpenWrt.**
Using `ip addr add` or `ifconfig eth0 192.168.1.1` configures the kernel interface in memory only. Persistent network configuration on OpenWrt requires `uci set network...` + `uci commit network` + `ifup/netifd` reload. Reference: `scenarios/03-golden-answers-key.md` — Universal General Falseness, Networking.

**44. The OpenWrt UCI system, not `/etc/network/interfaces`, manages persistent network configuration.**
Writing to `/etc/network/interfaces` (Debian/Ubuntu convention) does not work on OpenWrt. The authoritative network configuration file is `/etc/config/network`, managed exclusively through the `uci` CLI or the `uci` C/ucode API.

**45. `ubus` is the only correct IPC mechanism between OpenWrt services — UNIX sockets opened directly are a Falseness.**
Implementing IPC by opening raw UNIX sockets (`AF_UNIX / SOCK_STREAM`) bypasses the access control, service discovery, and event notification capabilities of the ubus daemon. All inter-process communication must go through `ubus`. Reference: `scenarios/03-golden-answers-key.md` — Scenario 03, Falseness.

---

## Part 7: Recommended Documentation Roadmap

| Priority | Document Title | Rationale |
| :--- | :--- | :--- |
| **P0** | `uci_load_validate` Complete Reference | 0% models used it correctly in Alpha S01 beta rescore |
| **P0** | Modern LuCI JS Forms with `L.ui` and Widgets | <15% pass rate across S04 and S05 combined |
| **P1** | C ubus Daemon Boilerplate with Correct Init Order | 40% pass rate Beta S12; `ubus_add_uloop` universally unknown |
| **P1** | ucode Async Processing with `uloop.handle()` and Event Flags | 0% pass rate Alpha S16 |
| **P2** | ucode Native JSON and File I/O Patterns | 0% pass rate Alpha S13; adjacent to ucode async page |
| **P2** | OpenWrt Era Guide: Modern vs. Legacy Pattern Reference | Cited by nearly every Tier 2 failure |
