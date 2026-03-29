# OpenWrt Golden Answers & Truth Schema

## The Truth-Checking Methodology

**Subproject Purpose:** The overarching purpose of this pipeline is to build custom documentation about OpenWrt specifically for AI. We do this by reverse-engineering working code scenarios, pushing various frontier LLMs through them, and analyzing the outputs to discover exactly what architectural paradigms modern AI tools mathematically fail at. We collect these "bad situations" (taxonomic errors) and use them as undeniable, data-driven proof to author new guides for the `openwrt-docs4ai` project.

Because our primary project is an authoritative OpenWrt documentation pipeline, we already possess the absolute structural truth regarding the OS architecture. Grading AI responses relies on our documented authority, not abstract LLM reasoning.

> **Project Authority:** For authoritative OpenWrt development knowledge, always refer to the **openwrt-docs4ai** project deliverables located in this repository's documentation tree.

### Workflow & Evaluation Rules
Evaluation works via a strict **Falsification Engine**:
1. We maintain a database of undeniable General Truths and General Falsenesses.
2. Each Scenario contains Question-Specific Truths and Falses.
3. **The Golden Rule (One Strike):** When an AI generates an answer, we scan it against these lists. If the AI answer contains even *one* Falseness (General or Specific), correctness checking ends immediately and the answer is recorded as a FAIL (0).
4. **Iterative Refinement (Concept-by-Concept):** We grade the AI conceptually, not line-by-line. A perfectly functioning 30-line script scores an instant 0 if its foundational concept uses a Falseness (e.g. using `bash &` instead of `uloop`). As we analyze AI results, new truths and falsenesses are injected back into this file.
5. **Score Recording:** All final binary grading must be permanently logged in the `results/` subdirectory as a new file. **Rule:** The file must be named identically to the raw AI test output being evaluated, but suffixed with `-score` and the current date/time (e.g., `model-name-score-20260328-655pm.md`). This scoresheet artifact must contain the numerical scoring breakdown alongside the conversational synthesis detailing the discovered truths and falses.

### Redundancy & Similarity Refinement
To optimize pipeline speed, we continuously analyze output similarities:
*   **Model Redundancy:** If the outputs of two different models are 90%+ identical across a test batch, we drop one model from the routine test matrix.
*   **Test Redundancy:** If a specific scenario yields 90%+ identical outputs across *all* tested models, the scenario is marked redundant and pruned.

---

## 1. Universal General Truths
*(Any valid OpenWrt snippet must inherently align with these)*
*   Daemons must be managed by `procd` (`USE_PROCD`).
*   Configuration files must be natively managed via the `uci` system. Shell configuration parsing must rely on the `/lib/functions.sh` native `config_load` / `config_get` APIs.
*   Inter-process communication and system state queries must go through `ubus`.
*   Event-driven C code or native scripts must utilize the `uloop` asynchronous event system.
*   Modern LuCI frontend views must map to UCI configurations using JavaScript.
*   `jshn.sh` (`/usr/share/libubox/jshn.sh`) with `json_init`, `json_load`, `json_get_var` is a valid native OpenWrt JSON parsing API at the shell level (intermediate tier, below `ucode` but above `jsonfilter`).
*   `L.ready()` and the modern LuCI JS runtime (`rpc.declare`, `E()` DOM helper, `view.extend`) is the correct client-side entry point for LuCI views.

## 2. Universal General Falseness
*(If an AI outputs any of these concepts, it is an instant FAIL)*
*   **Init Systems:** `systemd`, `upstart`, or generic `LSB` bash scripts. Also: SysVinit-style `start()`/`stop()` without `USE_PROCD=1`, PID file management (`echo $! > /var/run/daemon.pid`), or manual watchdog loops.
*   **Networking:** Modifying `/etc/network/interfaces`, using `netplan`, or relying purely on raw `ip` / `ifconfig` commands for persistent config.
*   **Frontend:** Using deprecated Lua CBI (`m = Map(...)`), standalone React/Vue structures ignoring the `luci.view` architecture, or standalone CGI scripts (`/www/cgi-bin/`) that bypass LuCI entirely.
*   **Data Parsing:** Using `awk`, `grep`, `sed`, heavy shell pipes, or `jsonfilter`/`jshn` bash wrappers when modern `ucode` native JSON mapping is available.
*   **Asynchronous Logic:** Using shell backgrounding `&` jobs, FIFOs (`mkfifo`), named pipes with `while read` loops, and manual process management for parallel processing. These are legacy "Shell Hacks" replaced by native `uloop` integration in `ucode`.
*   **C RPC Anti-Patterns:** Building raw JSON strings manually (`sprintf`, `strdup("{\"status\":\"ok\"}")`), using `blobmsg_add_json_from_string()` to double-wrap `json-c` output, or using fabricated API functions (`ubus_request_set_result`, `ubus_add_workhandler`) that do not exist in the real `libubus` API.
*   **First-Boot Anti-Patterns:** Using `/etc/rc.local` with sentinel/lockfiles in `/tmp/` (cleared every reboot — runs every boot, not just first boot), creating redundant marker files (`/etc/firstboot_done`), or having `uci-defaults` scripts manually `rm -f` themselves instead of relying on the framework's `exit 0` deletion contract.
*   **Fabricated APIs:** Inventing plausible-sounding but non-existent ubus methods (e.g., `network.get_wireless_clients`), non-existent C macros (`BLOB_BUF_INIT`, `UBUS_METHOD_BUF`), or incorrect function signatures for `libubus` handlers.

---

## 3. Question-Specific Truths and Falses

### Scenario 01: Procd Daemon & Config Validation
**Truths:**
*   Must contain `USE_PROCD=1`.
*   Must contain `procd_open_instance`.
*   Must contain `uci_load_validate`.
**Falses:**
*   Running the daemon in the background manually with `&`, or parsing the config file directly using `cat /etc/config/my_daemon | grep hostname`.

### Scenario 02: uCode Network Interfaces
**Truths:**
*   Must explicitly `import * as ubus from 'ubus'`.
*   Must use `ubus.conn()`.
**Falses:**
*   Using `ubus call network.interface dump | jsonfilter` inside a bash wrapper instead of native ucode.
*   Using raw `ip`, `/sys/class/net`, or `jq` shell parsing instead of native ucode access to the OpenWrt network state via `ubus`.

### Scenario 03: C libubus Plugin
**Truths:**
*   Must include `#include <libubus.h>`.
*   Must use `ubus_add_object()`.
**Falses:**
*   Opening local sockets natively (`sys/socket.h`) to bypass the system bus for IPC.

### Scenario 04: LuCI JS Dynamic Form
**Truths:**
*   Must use `luci.view` architecture.
*   Must utilize `L.ui`, `form.Map`, and UI widgets like `form.ListValue` or `widgets.NetworkSelect`.
**Falses:**
*   Writing raw HTML `<form>` tags manually.

### Scenario 05: LuCI JS Live Status Table
**Truths:**
*   Must use `L.resolveDefault`.
*   Must use standard DOM helpers like `E('table')`.
*   Must use `rpc.declare` to fetch the live `ubus` data.
**Falses:**
*   Making standard generic `fetch()` or `XMLHttpRequest` calls to an external REST API.

### Scenario 06: Procd Validation Function
**Truths:**
*   Must use `uci_load_validate` framework structure for validations.
**Falses:**
*   Writing a custom regex parser in the start shell script.

### Scenario 07: C ubus RPC Handler
**Truths:**
*   Must safely build a return object using `struct blob_buf`.
*   Must populate data using `blobmsg_add_string()`.
*   Must finalize and respond via `ubus_send_reply()`.
**Falses:**
*   Using standard `printf` or building a raw JSON string `"{ \"status\": \"ok\" }"` manually in C.

### Scenario 08: uCode UCI Modification
**Truths:**
*   Must explicitly `import * as uci from 'uci'`.
*   Must use cursor methods: `cursor.set()`, `cursor.save()`, and `cursor.commit()`.
**Falses:**
*   Appending text directly using filesystem writes to `/etc/config/network`.

### Scenario 09: Hotplug.d Event Trigger
**Truths:**
*   Must read the `$ACTION` and `$INTERFACE` environment variables pushed by the hotplug system.
*   Must filter accepted `$ACTION` values first and exit early for unrelated hotplug events before causing side effects.
**Falses:**
*   Setting up a cron job or manual `while true` polling loop to watch the interface.

### Scenario 10: UCI Defaults First-Boot
**Truths:**
*   The script must be placed in `/etc/uci-defaults/` and MUST exit with `0` so it deletes itself.
*   `uci-defaults` is a configuration-mutation boundary only; normal boot or later procd triggers should apply the resulting state.
**Falses:**
*   Placing the script in `/etc/init.d/` and trying to track state manually.
*   Omitting the explicit `exit 0` at the end of the script (prevents the system from deleting the file).
*   Creating redundant "marker" or "sentinel" files (e.g., `/etc/firstboot_done`) to track state, as the `uci-defaults` directory itself is the state machine.
*   Calling `/etc/init.d/...` from inside the `/etc/uci-defaults/` script to start or reload services immediately.

### Scenario 11: C Package Makefile
**Truths:**
*   Must `include $(TOPDIR)/rules.mk`.
*   Must `include $(INCLUDE_DIR)/package.mk`.
*   Must use `DEPENDS:=+libubus`.
**Falses:**
*   Writing a standard `cmake` or `gcc` Makefile without the OpenWrt cross-compilation boilerplate.
*   Using deprecated `PKG_MD5SUM` instead of `PKG_HASH` in a current-era OpenWrt package Makefile.

### Scenario 12: C uloop Initialization
**Truths:**
*   Must initialize context with `uloop_init()`.
*   Must bind the bus with `ubus_connect()` and `ubus_add_uloop()`.
*   Must run the blocking `uloop_run()` at the end of `main()`.
**Falses:**
*   Using standard `sleep()` loops.

### Scenario 13: uCode Native fs/json Parsing
**Truths:**
*   Must natively call `fs.readfile()`.
*   Must natively parse using `json()`.
**Falses:**
*   Executing external binaries like `jq` to parse the file.

### Scenario 14: LuCI JSON Menu Router
**Truths:**
*   Must define the node using OpenWrt's JSON menu mapping schema (in `/usr/share/luci/menu.d/`).
*   Must explicitly define `"title"`, `"action"`, and `"type": "view"`.
**Falses:**
*   Writing a legacy `index.lua` controller to register the node.
*   Installing the menu JSON under `/usr/share/luci/menus.d/` (plural) or using noncanonical fields instead of the `"action"` + `"type": "view"` contract.

### Scenario 15: C blobmsg Dictionary Parsing
**Truths:**
*   Must explicitly use `blobmsg_parse()` with a registered `blobmsg_policy` array.
**Falses:**
*   Trying to blindly cast the void pointer or parse raw memory bytes.

### Scenario 16: uCode Parallel Async Ping
**Truths:**
*   Must execute the commands through `uloop` integration (e.g., async `fs.popen`).
*   Must pass explicit event flags to `uloop.handle(..., uloop.ULOOP_READ)` when wiring asynchronous process output.
*   Must treat `fs.popen()` as a process-handle API rather than inventing raw descriptor reads.
**Falses:**
*   Running the ping commands sequentially, or using bash `&` background jobs wrapper.
*   Omitting the `events` argument to `uloop.handle()`, or inventing `fs.read(fd, len)`-style APIs for async process output.

### Scenario 17: Diagnostic Check
**Truths:**
*   Must identify `ucode` as a lightweight script language replacing Lua, utilizing JavaScript-like syntax native to C structures.
**Falses:**
*   Classifying `ucode` as a unicode converter, or claiming Lua is the modern flagship framework.
