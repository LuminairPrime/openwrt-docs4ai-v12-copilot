# V13 Enhancement Plan — Opus Max

**Recorded:** 2026-03-20
**Status:** Ready for implementation
**Scope:** Deliverable-side enhancements to the published OpenWrt documentation
corpus that make AI agents measurably better at writing correct OpenWrt software.
**Audience for this plan:** An implementation agent (Claude or similar) working
inside this repository.

---

## 1. Tier List

Ranked by direct value to the end user: an AI agent that needs to write correct,
modern, efficient OpenWrt code for embedded systems with limited RAM, limited
flash storage, and weak SSDs that should not be written to excessively.

### Tier S — Highest deliverable impact

| Enhancement | Justification |
| --- | --- |
| **Cookbook module with annotated task-oriented examples** | AI agents learn patterns through demonstration, not specification. The current corpus has API references and raw source code but no annotated "here is how you do X" guidance. This is the single highest-impact addition because it directly addresses the three failure modes that make AI-generated OpenWrt code wrong: (1) generating deprecated Lua LuCI code instead of modern JS, (2) inventing ucode syntax from JavaScript guesses, and (3) writing standard-Linux init scripts instead of procd patterns. Annotated examples with anti-patterns cure all three. |
| **Inter-component communication maps** | AI agents fail at composition — they can read individual API docs but cannot trace a call from LuCI JS through rpcd/ubus/UCI to config files. No amount of per-module reference docs fixes this. The maps must show the actual call chains (LuCI JS → uhttpd → rpcd → ubus → daemon → UCI) with concrete code at each layer so agents can write code that correctly crosses component boundaries. This is especially critical for WiFi radio configuration where misconfigured call chains can cause radio instability. |
| **Era-disambiguation guide** | AI training data is dominated by pre-2019 Lua-era OpenWrt code. Without an explicit "this is deprecated, use this instead" document that agents encounter early in navigation, they will keep generating legacy patterns. This is cheap to produce and has outsized impact. |

### Tier A — High deliverable impact

| Enhancement | Justification |
| --- | --- |
| **Expanded .d.ts typing surfaces** | The existing `ucode.d.ts` in `ucode/types/` proves the pattern works. Expanding to cover LuCI JS APIs and UCI config schemas gives agents type-level guardrails that prevent hallucinated function signatures. For embedded targets where a wrong API call wastes flash writes or crashes a service, type surfaces are a direct quality gate. |
| **`llms-mini.txt` (low-context routing surface)** | Many AI agents operate with small context windows (4K–16K). The current `llms.txt` is a good router but `llms-full.txt` is enormous. A `llms-mini.txt` under 1000 tokens that covers the most critical entry points, the era-disambiguation warning, and the cookbook module entry would let constrained agents navigate effectively. |
| **Per-module README.md and AGENTS.md** | The root AGENTS.md exists but individual modules have no agent-facing orientation. A per-module AGENTS.md (50–150 lines) that says "this module covers X, start with Y, never do Z" gives agents local context without loading the entire corpus. Especially important for the `luci` and `ucode` modules where wrong assumptions are catastrophic. |
| **Embedded-systems constraints guide** | A dedicated document covering: musl vs glibc differences, squashfs+overlay filesystem implications, flash wear-leveling constraints (minimize writes), RAM budgets for typical devices (32MB–256MB), why busybox utilities differ from GNU coreutils, and radio subsystem stability concerns. This is domain knowledge that AI agents lack entirely and that affects every architectural decision. |

### Tier B — Moderate deliverable impact

| Enhancement | Justification |
| --- | --- |
| **XML export (per-module XML packs)** | Some AI tooling (notably Repomix-style ingestion) parses XML more reliably than nested Markdown for file-boundary preservation. Useful as an alternate ingestion format, but secondary to content quality. Should be per-module first (not a single monolithic file) since the corpus exceeds most context windows. |
| **Package Makefile templates with annotations** | Currently the corpus has raw Makefile examples from official packages but no annotated templates. A set of 5–6 annotated template Makefiles (simple-C, cmake, luci-app, ucode-package, kernel-module, package-with-init-script) in the cookbook module would prevent the most common build-system mistakes. Ranked B because the raw examples already provide some coverage. |

### Tier C — Low deliverable impact or deferred

| Enhancement | Justification for exclusion or deferral |
| --- | --- |
| **Tree-sitter grammar for ucode** | High effort (weeks), benefits are indirect (better chunking, not better content), and the payoff requires downstream tool adoption. Defer until the content-quality phases (S and A tiers) are complete. |
| **Dockerized buildroot compile sandbox** | Valuable for CI validation of generated examples, but this is an internal quality tool, not a deliverable enhancement. The examples themselves are the deliverable. Defer to a validation-focused phase. |
| **MCP server hardening** | MCP tools are an access pattern, not content. They improve how agents query the corpus but don't improve the corpus itself. Defer until a concrete MCP consumer exists. |
| **Repomix adoption** | This repo's pipeline already handles domain-specific packing, routing, and chunking. Repomix would duplicate existing capability. Not adopted. |
| **Test-mining for examples** | This repo's tests are pipeline-contract tests (pytest for CI correctness), not OpenWrt programming examples. Mining them would produce misleading content. Not adopted. |
| **Fine-tuning / RAG pipeline** | Out of scope for a documentation production pipeline. These are consumption-side strategies, not deliverable improvements. |

---

## 2. Implementation Plan

### Phase overview

| Phase | Tier | What ships | New pipeline stage(s) |
| --- | --- | --- | --- |
| 1 | S | `cookbook` module in release-tree | `04b-generate-cookbook.py` |
| 2 | S | Era guide + communication maps (inside cookbook) | Content files in `release-inputs/release-include/cookbook/` |
| 3 | A | Expanded `.d.ts` surfaces | Extend `05c` |
| 4 | A | `llms-mini.txt`, per-module AGENTS.md/README.md, embedded constraints guide | `06` extension + content files |
| 5 | B | XML export, annotated Makefile templates | `05e-generate-xml-exports.py` + cookbook content |

---

### Phase 1: Cookbook module

**Goal:** Ship a new `cookbook` module in the release-tree that contains
task-oriented, annotated example documentation derived from proven OpenWrt
source code. This is the single highest-value addition.

#### 1.1 Module structure

The cookbook module follows the existing release-tree module schema exactly:

```text
release-tree/
  cookbook/
    llms.txt
    map.md
    bundled-reference.md          (or sharded if oversized)
    chunked-reference/
      era-guide.md
      common-ai-mistakes.md
      embedded-constraints.md
      architecture-overview.md
      luci-form-with-uci.md
      luci-rpcd-ubus-flow.md
      ucode-rpcd-service-pattern.md
      procd-service-lifecycle.md
      minimal-openwrt-package-makefile.md
      uci-read-write-from-ucode.md
      uci-read-write-from-shell.md
      hotplug-handler-pattern.md
      inter-component-communication-map.md
      wifi-radio-configuration.md
      luci-status-page-with-polling.md
      ubus-service-registration.md
      full-stack-vpn-toggle.md
    types/                        (empty initially, populated in Phase 3)
```

#### 1.2 Pipeline integration

Create a new pipeline script: `.github/scripts/openwrt-docs4ai-04b-generate-cookbook.py`

**Why `04b` and not `05e` or later:** The cookbook module must exist before
stage `05a` (which assembles bundled references), `06` (which generates routing
indexes), `07` (which generates HTML indexes), and `08` (which validates). The
cookbook content feeds into all downstream stages.

**Stage `04b` must:**
1. Read source content from `release-inputs/release-include/cookbook/chunked-reference/` (hand-authored source files checked into the repo).
2. Copy those files into `WORKDIR/cookbook/chunked-reference/`.
3. Generate `cookbook/map.md` from the topic files (follow the pattern in `05a` for other modules).
4. Generate `cookbook/llms.txt` with topic listing and token counts.
5. Write `.meta.json` sidecars if needed for downstream stages.
6. Log with prefix `[04b]`.

**CRITICAL implementation constraints:**
- The cookbook module is a **synthetic module** — it does not have an L1/L2 source like other modules. It has hand-authored content in `release-inputs/`.
- Stage `05a` must be updated to recognize `cookbook` as a module and assemble its `bundled-reference.md`.
- Stage `06` must include `cookbook` in root and per-module routing index generation.
- Stage `07` must include `cookbook` in HTML index generation.
- Stage `08` must validate `cookbook` passes all module schema checks (llms.txt, map.md, bundled-reference.md, chunked-reference/ non-empty).
- **Do NOT modify stage numbering for existing scripts.** `04b` is a new sibling in the `04` family. The existing `04` (AI summaries) becomes `04a` only if needed for ordering clarity, but the simpler path is to keep `04` as-is and add `04b` after it.

**CRITICAL: Stage `04` coexistence rule.** The CLAUDE.md and ARCHITECTURE.md
state: "A bare stage id (e.g., `04`) cannot coexist with lettered siblings."
This means adding `04b` requires renaming the current `04-generate-ai-summaries.py`
to `04a-generate-ai-summaries.py`. Update ALL references: the workflow YAML,
`docs/ARCHITECTURE.md`, `docs/specs/v12/execution-map.md`, smoke tests, and
any other files that reference the old `04-` name. Search the repo for
`04-generate-ai-summaries` and `04-generate` to find all references.

#### 1.3 Cookbook content authoring guidelines

Each cookbook topic file must follow this structure:

```markdown
---
title: <topic title>
module: cookbook
tags: [<relevant-tags>]
token_count: <approximate>
---

# <Topic Title>

> **When to use:** <one sentence describing the scenario>
> **Key components:** <list the OpenWrt subsystems involved>
> **Era:** Current (2023+). Do not use deprecated patterns listed below.

## Overview

<2-3 paragraph explanation of the pattern, what it does, and why it exists>

## Complete Working Example

<Full, annotated code example. Every non-obvious line gets a comment.
The example must be a realistic, minimal, complete working pattern —
not a toy hello-world. Use realistic variable names and values.>

## Step-by-Step Explanation

<Walk through the example code block by block, explaining WHY each
part exists and what would break if it were removed or changed.>

## Anti-Patterns

<Explicitly show what AI agents commonly generate wrong, and show the
correct alternative. Format as pairs:>

### WRONG: <description>
```<lang>
<incorrect code>
```

### CORRECT: <description>
```<lang>
<correct code>
```

## Related Topics

<Links to other cookbook pages and module reference docs that provide
deeper detail on the APIs used in this example.>
```

**Content correctness rules:**
- Every code example must be derived from or verified against actual OpenWrt
  upstream source code already present in the corpus (L1-raw or L2-semantic
  layers). Do not invent APIs or function signatures.
- ucode examples must use only functions documented in the `ucode` module's
  chunked-reference files or the `ucode.d.ts` type surface.
- LuCI JS examples must use only APIs documented in the `luci` module's
  chunked-reference files.
- Package Makefile examples must use only macros documented in the `wiki`
  module's build-system reference pages.
- Anti-patterns must be real failure modes (see the failure categories in the
  source planning document), not hypothetical.

#### 1.4 First cookbook topics — specification

These are the required first-round topics. Each description below gives an
implementing agent enough detail to write the content.

**1. `era-guide.md` — What is current vs deprecated in OpenWrt**

Purpose: Prevent agents from generating pre-2019 Lua-era code.

Must contain:
- A two-column table: "Current approach (use this)" vs "Deprecated approach (do not use)".
- Cover at minimum: LuCI views (JS not Lua), init system (procd not sysvinit),
  scripting (ucode not Lua), config access (uci module not luci.model.uci),
  package checksums (PKG_HASH not PKG_MD5SUM), JSON handling (native ucode/jshn not jsonfilter).
- Code snippets showing the deprecated pattern and the modern replacement.
- A "how to identify outdated code" section with regex-detectable markers.
- A "when legacy code is acceptable" section (modifying existing Lua apps,
  targeting old releases, user explicitly requests it).

**2. `common-ai-mistakes.md` — Explicit anti-pattern catalog**

Purpose: Directly address the documented failure modes.

Must contain four sections matching the known failure categories:
- Architectural confusion (systemd assumptions, glibc assumptions, apt/yum assumptions)
- ucode ignorance (JavaScript syntax guesses, unknown stdlib modules, wrong template syntax)
- Build system misunderstanding (wrong Makefile structure, missing PKG_* variables, manual install rules)
- Inter-component communication (not understanding the LuCI→rpcd→ubus→UCI→config chain)

Each failure must show: what the AI typically generates, what is actually correct,
and WHY the incorrect version fails (e.g., "this fails because musl libc does
not implement X" or "this fails because procd ignores start()/stop() functions
and only calls start_service()").

**3. `architecture-overview.md` — OpenWrt component stack**

Purpose: Give agents the system-level mental model they lack.

Must contain:
- The ASCII architecture diagram showing the full stack: LuCI JS → uhttpd/rpcd → ubus → daemons (netifd, procd, rpcd, etc.) → UCI/config files → C libraries (libubox, libubus, libuci).
- A section on each major daemon: what it does, what ubus objects it exposes, what config files it owns.
- The filesystem layout: squashfs root + overlay, /etc/config/, /tmp/ (tmpfs), /var/ (symlink to /tmp/).
- Memory and storage constraints for typical devices.

**4. `embedded-constraints.md` — Hardware-aware programming guide**

Purpose: Teach agents about the physical constraints of OpenWrt target devices.

Must contain:
- Typical device specs: 32MB–256MB RAM, 4MB–128MB flash, MIPS/ARM/x86.
- musl libc vs glibc: which POSIX functions are missing or behave differently.
- Flash wear: why minimizing writes matters (NAND/NOR flash endurance limits,
  JFFS2/UBIFS wear leveling, tmpfs for transient data).
- RAM budgets: why a daemon that uses 50MB is unacceptable on most targets.
- busybox: reduced utility behavior vs GNU coreutils.
- WiFi radio stability: why misconfigured hostapd restarts cause client
  disconnects, why channel scanning during operation degrades throughput,
  why DFS channels require careful handling.
- Data structure guidance: prefer compact representations, avoid deep object
  nesting, use flat UCI config sections over complex hierarchies.

**5. `inter-component-communication-map.md` — Cross-layer call flows**

Purpose: Show agents the actual call chains for the five most common operations.

Must contain these flows with concrete code at each layer:

1. **LuCI form → UCI config change:**
   LuCI JS `form.Map('config')` → `handleSaveApply()` → RPC POST →
   uhttpd → rpcd → `uci set/commit` ubus calls → `/etc/config/<name>`

2. **LuCI status page → runtime data:**
   LuCI JS `rpc.declare({object:'X', method:'Y'})` → RPC POST →
   uhttpd → rpcd → ubus call → target daemon → JSON response

3. **procd service lifecycle:**
   `service myservice enable` → symlink in `/etc/rc.d/` →
   boot → procd reads init scripts → `start_service()` →
   `procd_open_instance` / `procd_set_param` → procd supervises process →
   `service_triggers()` → config-change auto-restart

4. **hotplug event chain:**
   kernel event → procd hotplug handler → `/etc/hotplug.d/<subsystem>/NN-script` →
   environment variables (`ACTION`, `INTERFACE`, `DEVICE`) → script logic

5. **WiFi configuration change:**
   UCI edit `/etc/config/wireless` → `wifi reload` or
   `ubus call network.wireless down/up` → netifd → hostapd restart →
   radio reconfiguration → client reassociation

**6. `luci-form-with-uci.md` — Building a LuCI settings page**

Complete working example of a LuCI JS form that reads and writes UCI config.
Must include: the JS view file, the menu JSON, the ACL JSON, the UCI config
template, and the package Makefile snippet that installs them all.

**7. `ucode-rpcd-service-pattern.md` — Writing a ubus-exposed ucode service**

Complete working example of a ucode script that registers on ubus, exposes
methods, and can be called from LuCI. Must include the ucode script, the rpcd
ACL, and a LuCI JS snippet showing how to call it.

**8. `procd-service-lifecycle.md` — Writing a procd init script**

Complete annotated procd init script with: `start_service()`, `stop_service()`,
`service_triggers()`, `validate_section()`, respawn config, stdout/stderr logging.
Must show anti-patterns (sysvinit-style start()/stop()).

**9. `minimal-openwrt-package-makefile.md` — Package Makefile reference**

Complete annotated Makefile for a simple C package. Every line gets a comment
explaining what it does and what breaks if it's wrong. Must include PKG_HASH,
PKG_LICENSE, DEPENDS syntax (+pkg, +FEATURE:pkg), install macros, and the
critical "$(eval) must be last line" rule.

**10. `uci-read-write-from-ucode.md` — UCI operations in ucode**

Complete examples of: cursor creation, load, get (single value, list, section
type), foreach iteration, set, add section, delete, commit. Must show
anti-patterns (reading config files directly with fs.readfile, forgetting
load() before get(), forgetting commit()).

**11. `uci-read-write-from-shell.md` — UCI operations from shell**

Complete examples using the `uci` CLI: `uci get`, `uci set`, `uci add`,
`uci delete`, `uci commit`, `uci show`. Include `uci batch` for atomic
multi-operation changes. Show the jshn library for JSON handling in shell.

**12. `hotplug-handler-pattern.md` — Writing hotplug scripts**

Complete example of a hotplug script for the `iface` subsystem. Must show:
file naming convention, available environment variables, typical patterns
for interface-up/down events, and integration with UCI config.

**13. `wifi-radio-configuration.md` — WiFi radio management**

Guide to WiFi configuration: `/etc/config/wireless` structure, radio vs
interface sections, common options (channel, htmode, country, txpower),
DFS channel handling, band steering, and the `wifi` CLI. Must emphasize
stability: avoid unnecessary radio restarts, understand client reassociation
cost, handle DFS radar detection gracefully.

**14. `full-stack-vpn-toggle.md` — Complete multi-layer feature walkthrough**

End-to-end example building a simple VPN toggle feature across all layers:
UCI config, init script, ucode ubus service (optional), LuCI settings page,
LuCI status page. This demonstrates how all the cookbook topics compose
into a real feature.

---

### Phase 2: Era guide and communication maps

These are listed separately because they are the most critical Tier S content
and should be written first even if other cookbook topics take longer.

**Implementation:** The content files for Phase 1 topics 1–5 (era-guide,
common-ai-mistakes, architecture-overview, embedded-constraints,
inter-component-communication-map) should be authored and merged first,
before the remaining cookbook topics.

The pipeline script (`04b`) does not need to change between Phase 1 and Phase 2
— it simply processes whatever content files exist in the source directory.

---

### Phase 3: Expanded .d.ts typing surfaces

**Goal:** Extend the existing `05c-generate-ucode-ide-schemas.py` to produce
additional type surfaces.

#### 3.1 New outputs

```text
release-tree/
  cookbook/types/
    luci-form.d.ts     — LuCI form.Map, form.TypedSection, form.Option types
    luci-rpc.d.ts      — LuCI rpc.declare() signature types
    uci-schemas.d.ts   — UCI config section/option types for core packages
  ucode/types/
    ucode.d.ts         — (existing, enhanced if needed)
```

#### 3.2 Implementation

Option A (preferred): Extend `05c` to generate additional `.d.ts` files from
the existing extracted signatures in `ucode/` and `luci/` chunked-reference
content. This keeps all type generation in one place.

Option B: Create a sibling `05e-generate-extended-type-surfaces.py` if `05c`
becomes too complex.

**For `luci-form.d.ts`:** Parse the LuCI JS API docs in
`luci/chunked-reference/js_source-api-form.md` and
`luci/chunked-reference/js_source-api-cbi.md` to extract class hierarchies,
method signatures, and option types.

**For `uci-schemas.d.ts`:** Parse UCI config documentation from
`wiki/chunked-reference/` pages covering `/etc/config/network`,
`/etc/config/wireless`, `/etc/config/firewall`, `/etc/config/dhcp`,
`/etc/config/system`. Express config sections and options as TypeScript
interfaces so agents get autocompletion-style guidance on valid option names
and value types.

**Constraints:**
- Generated `.d.ts` files must include a header comment stating they are
  auto-generated and listing the source files they were derived from.
- Unknown or ambiguous signatures must be annotated with `// TODO: verify`
  rather than omitted silently.
- Type files must be included in the module's `llms.txt` routing surface.

---

### Phase 4: Low-context surface and per-module navigation

#### 4.1 `llms-mini.txt`

A new root-level file in the release-tree, under 1000 tokens, containing:

1. A 2-line project description.
2. The era-disambiguation warning (3 lines: "use JS not Lua for LuCI, use
   ucode not Lua for scripting, use procd not sysvinit for init").
3. Module listing with one-line descriptions and direct links to each
   module's `llms.txt`.
4. A pointer to `cookbook/llms.txt` as the recommended starting point for
   agents writing new code.

**Generation:** Extend stage `06` to produce `llms-mini.txt` alongside the
existing `llms.txt` and `llms-full.txt`.

**Validation:** Extend stage `08` to verify `llms-mini.txt` exists and is
under 1500 tokens (measured with cl100k_base encoding).

**Contract:** Update `docs/specs/v12/release-tree-contract.md` Root Files table
to include `llms-mini.txt`.

#### 4.2 Per-module AGENTS.md

Each module directory in the release-tree gets an `AGENTS.md` (50–150 lines)
that provides module-specific agent orientation:

- What the module covers (2-3 sentences).
- Recommended reading order (which files to read first).
- Critical warnings specific to this module (e.g., for `luci`: "Do NOT generate
  Lua CBI code. Modern LuCI uses client-side JavaScript.").
- Links to the most relevant cookbook topics.

**Generation:** Extend stage `05b-generate-agents-and-readme.py` to produce
per-module `AGENTS.md` files in addition to the root `AGENTS.md` and `README.md`.

**Validation:** Extend stage `08` to verify each module has an `AGENTS.md` file.

**Contract:** Update the Module Schema table in `release-tree-contract.md` to
include `AGENTS.md` as a required file.

#### 4.3 Per-module README.md

Same pattern as per-module AGENTS.md but oriented toward human readers who
browse the published corpus on GitHub. Lighter content, focused on navigation
rather than behavioral rules.

**Generation:** Same extension to `05b`.

---

### Phase 5: XML export and Makefile templates

#### 5.1 XML export

Create `05e-generate-xml-exports.py` that produces per-module XML packs:

```text
release-tree/
  cookbook/cookbook.xml
  luci/luci.xml
  ucode/ucode.xml
  ...
```

Each XML file wraps the module's content in a structured format:

```xml
<module name="cookbook">
  <file path="chunked-reference/era-guide.md">
    <content>...</content>
  </file>
  <file path="types/luci-form.d.ts">
    <content>...</content>
  </file>
</module>
```

**Constraints:**
- XML files are an alternate access format, not the primary. The Markdown
  files remain authoritative.
- XML packs should include token counts as attributes for budget-aware agents.
- Stage `08` must validate that XML packs are well-formed.

#### 5.2 Annotated Makefile templates

Add to the cookbook module's chunked-reference:
- `template-simple-c-package.md`
- `template-cmake-package.md`
- `template-luci-app-package.md`
- `template-ucode-package.md`
- `template-kernel-module-package.md`
- `template-package-with-init-script.md`

Each template is a complete, heavily annotated Makefile wrapped in a cookbook
topic page (following the standard topic structure from §1.3). The annotations
explain every line and call out the most common mistakes.

---

## 3. File change map

This section lists every file that must be created or modified, organized by
phase, so the implementing agent can work through changes systematically.

### Phase 1 files

**New files:**
- `.github/scripts/openwrt-docs4ai-04b-generate-cookbook.py` — cookbook assembly script
- `release-inputs/release-include/cookbook/chunked-reference/*.md` — 14 topic source files (see §1.4)

**Modified files:**
- `.github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py` → **rename** to `openwrt-docs4ai-04a-generate-ai-summaries.py`
- `.github/workflows/openwrt-docs4ai-pipeline.yml` — add `04b` step, update `04` → `04a` reference
- `.github/scripts/openwrt-docs4ai-05a-assemble-references.py` — recognize `cookbook` as a module
- `.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py` — include `cookbook` in routing
- `.github/scripts/openwrt-docs4ai-07-generate-web-index.py` — include `cookbook` in HTML index
- `.github/scripts/openwrt-docs4ai-08-validate-output.py` — validate `cookbook` module schema
- `docs/ARCHITECTURE.md` — update stage table (04 → 04a, add 04b)
- `docs/specs/v12/execution-map.md` — update stage dependency map
- `tests/` — update any tests that reference `04-generate-ai-summaries` by name

### Phase 3 files

**Modified files:**
- `.github/scripts/openwrt-docs4ai-05c-generate-ucode-ide-schemas.py` — extend for new .d.ts outputs
- `docs/specs/v12/release-tree-contract.md` — document cookbook/types/ contents

### Phase 4 files

**Modified files:**
- `.github/scripts/openwrt-docs4ai-05b-generate-agents-and-readme.py` — per-module AGENTS.md + README.md
- `.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py` — add `llms-mini.txt` generation
- `.github/scripts/openwrt-docs4ai-08-validate-output.py` — validate `llms-mini.txt` and per-module AGENTS.md
- `docs/specs/v12/release-tree-contract.md` — add `llms-mini.txt` to root files, `AGENTS.md` to module schema

### Phase 5 files

**New files:**
- `.github/scripts/openwrt-docs4ai-05e-generate-xml-exports.py` — XML pack generator
- `release-inputs/release-include/cookbook/chunked-reference/template-*.md` — 6 Makefile template topics

**Modified files:**
- `.github/workflows/openwrt-docs4ai-pipeline.yml` — add `05e` step
- `.github/scripts/openwrt-docs4ai-08-validate-output.py` — validate XML well-formedness
- `docs/ARCHITECTURE.md` — add `05e` to stage table
- `docs/specs/v12/execution-map.md` — add `05e` dependency

---

## 4. Testing strategy

Each phase must pass the existing validation gates before merging:

```powershell
python tests/run_smoke_and_pytest.py          # full local validation
python tests/check_linting.py                  # Ruff + Pyright + actionlint
```

Phase-specific validation:

- **Phase 1:** After running the pipeline, verify:
  - `openwrt-condensed-docs/release-tree/cookbook/` exists with all required files
  - `cookbook` appears in root `llms.txt` and `llms-full.txt`
  - `cookbook` appears in `index.html`
  - Stage `08` passes without new failures
  - Module count in `AGENTS.md` increments by 1

- **Phase 3:** Verify new `.d.ts` files appear in `cookbook/types/` and are
  syntactically valid TypeScript (can be checked with `tsc --noEmit` or a
  simple parse check).

- **Phase 4:** Verify `llms-mini.txt` exists, is under 1500 tokens, and
  contains all module names. Verify per-module AGENTS.md files exist.

- **Phase 5:** Verify XML files are well-formed (`python -c "import xml.etree.ElementTree; xml.etree.ElementTree.parse('file.xml')"`).

---

## 5. Guardrails for implementing agents

These rules prevent common implementation failures:

1. **Do not reorganize existing modules.** The existing module structure
   (`luci`, `luci-examples`, `openwrt-core`, `openwrt-hotplug`, `procd`,
   `uci`, `ucode`, `wiki`) is fixed. The cookbook is a NEW module added
   alongside them, not a reorganization.

2. **Do not rename existing scripts** except the `04` → `04a` rename required
   by the stage-naming constraint. All other scripts keep their current names.

3. **Do not create new root-level release-tree files** beyond `llms-mini.txt`
   (Phase 4). The root file set is contractual.

4. **Do not modify content in existing modules.** Existing chunked-reference
   files, bundled-reference files, and type surfaces are generated by the
   existing pipeline and must not be hand-edited.

5. **Follow the existing script patterns.** Read at least one existing stage
   script (e.g., `05a` or `05b`) before writing `04b`. Match the logging
   style (`[04b] OK:`, `[04b] FAIL:`), the argparse pattern, the WORKDIR/OUTDIR
   convention, and the error handling approach.

6. **Cookbook content goes in `release-inputs/release-include/cookbook/`**, not
   in `openwrt-condensed-docs/` directly. The pipeline copies/generates the
   final output. Never hand-edit `openwrt-condensed-docs/`.

7. **All cross-references in cookbook content use relative Markdown links** to
   other release-tree files (e.g., `../ucode/chunked-reference/topic.md`),
   not absolute paths or internal-only paths.

8. **Token counts in llms.txt files** must use cl100k_base encoding. The
   existing pipeline helper for token counting should be reused.

9. **The cookbook YAML frontmatter** must include `module: cookbook` so
   downstream stages can identify it correctly.

10. **Windows path compatibility:** Use `pathlib.Path` or `os.path.join`,
    never hardcoded forward-slash paths in Python scripts. The primary
    development environment is Windows.
