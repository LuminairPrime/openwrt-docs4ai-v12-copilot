# V13 Cookbook Content Specification

**Recorded:** 2026-03-22  
**Purpose:** Define every cookbook topic, its required evidence, authoring process, and quality gates  
**Predecessor:** [02-v13-implementation-spec-s-tier-2026-03-22.md](02-v13-implementation-spec-s-tier-2026-03-22.md)  
**Next:** 04-v13 A-tier implementation spec

---

## Scope

This document specifies the **content** of the cookbook module. The **pipeline infrastructure** (02i ingest script, 06 category entry, provenance contract) is already specified in 02-v13 §S3. This spec covers:

1. Which topics to write and in what order
2. What each topic must contain
3. How topics are authored, verified, and maintained
4. What counts as evidence

This spec does **not** cover:

- Pipeline code changes (see 02-v13)
- Routing or metadata field changes (see 02-v13 Metadata Field Hardening)
- Per-module AGENTS.md content beyond the cookbook module (see 02-v13 §S4)

The cookbook content spec therefore owns the narrative contract: what a cookbook page is, what evidence it requires, how it is reviewed, and how it should cross-link into the shipped release-tree without turning into a duplicate reference manual.

---

## Topic Inventory

### Priority 1: S-tier topics (must ship with v13)

These topics are required for v13 to meet its stated goals. They are listed in authoring order — each topic builds on the one before it.

| # | Filename | Tier | Required evidence | Estimated effort |
|---|----------|------|-------------------|-----------------|
| 1 | `openwrt-era-guide.md` | S2 | Local corpus + external human research packet | Half day |
| 2 | `common-ai-mistakes.md` | S3 | Local corpus + maintainer experience | Half day |
| 3 | `architecture-overview.md` | S3 | Local corpus + upstream repo structure | Half day |

`architecture-overview.md` was promoted from A-tier because it is a structural dependency for every cross-module cookbook topic. Without it, the procd, luci-form, and ucode-rpcd topics each have to re-explain the component stack.

### Priority 2: A-tier topics (should ship with v13)

These topics are high-value additions that address documented AI failure modes. They can ship after the S-tier topics but should be completed before v13 closes.

| # | Filename | Tier | Required evidence | Estimated effort |
|---|----------|------|-------------------|-----------------|
| 4 | `procd-service-lifecycle.md` | S3 | procd module corpus + upstream `procd.sh` | Half day |
| 5 | `minimal-openwrt-package-makefile.md` | S3 | wiki module corpus + upstream packages | Half day |
| 6 | `uci-read-write-from-ucode.md` | S3 | ucode module corpus + uci module corpus | Half day |
| 7 | `luci-form-with-uci.md` | S3 | luci module corpus + luci-examples corpus | 1 day |
| 8 | `embedded-constraints.md` | A3 | External OpenWrt hardware/build docs + maintainer experience | Half day |

### Priority 3: B-tier topics (stretch goals)

These topics are valuable but not required for v13. They should be listed in `docs/docs-new/roadmap/deferred-features.md` if not completed.

| # | Filename | Tier | Required evidence | Estimated effort |
|---|----------|------|-------------------|-----------------|
| 9 | `inter-component-communication-map.md` | A4 | Multiple module corpora + upstream call chain verification | 1–2 days |
| 10 | `uci-read-write-from-shell.md` | S3 | wiki module corpus + uci CLI docs | Half day |
| 11 | `hotplug-handler-pattern.md` | S3 | openwrt-hotplug module corpus | Half day |
| 12 | `ucode-rpcd-service-pattern.md` | S3 | ucode + luci module corpora | 1 day |

---

## Source Directory

All cookbook source files are authored in:

```
content/cookbook-source/
```

This directory does not exist yet. It should be created when the first cookbook topic is written. See 02-v13 §S7 folder-lineage rule for the full path through the pipeline:

- `content/cookbook-source/` → authored source
- `L1-raw/cookbook/` → ingested staging output
- `L2-semantic/cookbook/` → normalized staging output
- `release-tree/cookbook/` → final public delivery module

## Cookbook vs Reference Boundary

Cookbook pages exist to answer task-oriented questions such as "how do I wire a LuCI form to UCI?" They are not a second copy of the generated reference corpus.

Every cookbook page must follow these boundary rules:

- explain a concrete task or decision, not an entire API surface
- cite the authoritative reference pages for full API detail instead of copying large reference sections
- stay opinionated about current OpenWrt practice when the corpus shows a clear preferred path
- explicitly call out transitional or legacy cases instead of flattening them into "always" or "never"
- avoid generic Linux advice unless the page also explains the OpenWrt-specific constraint or difference

If a topic cannot be written without inventing undocumented API behavior, the topic is not ready for cookbook treatment and should instead trigger a reference-corpus or upstream-doc follow-up.

---

## Content Contract

Every cookbook topic must conform to this contract. The contract is intentionally strict because cookbook pages are the highest-signal content in the deliverable — an error here is worse than an error in auto-generated reference material.

### Required sections

Each cookbook page must include all of the following sections in this order:

1. **Title** — H1 heading, self-describing
2. **When-to-use callout** — blockquote with scenario description, key components, era status
3. **Overview** — 2–3 paragraphs: what, why, when
4. **Complete Working Example** — full annotated code with comments on every non-obvious line
5. **Step-by-Step Explanation** — walk through the example block by block
6. **Anti-Patterns** — at least one WRONG/CORRECT pair per topic
7. **Related Topics** — links to other cookbook pages and module reference docs
8. **Verification Notes** — how this page's correctness was checked

### Required page-level frontmatter

Cookbook source files should include frontmatter that the ingest script can pass through to the `.meta.json` sidecar. After `03` normalization, the L2 file will have standard frontmatter.

The following fields are authored by the maintainer in the source file header or a companion sidecar:

| Field | Required? | Purpose |
|-------|-----------|---------|
| `title` | Yes | Human-readable topic title |
| `description` | Yes | One-sentence routing summary used by map/llms surfaces |
| `module` | Yes (always `cookbook`) | Pipeline routing |
| `origin_type` | Yes (always `authored`) | Pipeline routing — indicates hand-authored provenance |
| `when_to_use` | Yes | One-sentence scenario description |
| `related_modules` | Yes | List of module names this topic references |
| `era_status` | Yes | `current`, `transitional`, or `legacy` |
| `verification_basis` | Yes | How the content was verified (e.g., "upstream procd.sh commit abc1234") |
| `reviewed_by` | Yes | Human maintainer accountable for the final page |
| `last_reviewed` | Yes | ISO 8601 date of last human review |

`topic_slug` is **not** authored in frontmatter. It is derived automatically by `02i` from the markdown filename (minus `.md`). Requiring the human to type the slug twice creates a redundant point of failure with no added information.

**Decision:** cookbook source files should carry YAML frontmatter directly in the markdown source. `02i-ingest-cookbook.py` should preserve the body content and translate the authored metadata into the normal sidecar contract instead of forcing authors to maintain a second metadata file.

### Authoring metadata mapping contract

This content spec requires the following behavior from the 02i/03 implementation described in 02-v13:

- `topic_slug` is derived by `02i` from the filename, not authored in frontmatter
- `02i-ingest-cookbook.py` should carry authored fields such as `title`, `description`, `when_to_use`, `related_modules`, `era_status`, `verification_basis`, `reviewed_by`, and `last_reviewed` into the L1 sidecar
- `03` should carry those authored fields forward into L2 where the release-tree generators need them

This keeps the filename as the sole public path authority while still letting authored metadata drive routing summaries, review accountability, and quality gates.

### Cross-link contract

Cookbook pages are authored for the final shipped release-tree location, not for the raw `content/cookbook-source/` folder view.

Within a cookbook page, links must follow these rules:

- another cookbook topic: `./other-topic.md`
- a cookbook index page: `../map.md` or `../bundled-reference.md`
- a reference page in another module: `../../luci/chunked-reference/js_source-api-form.md`
- a top-level shipped file such as root `llms.txt`: `../../llms.txt`

Never guess a future path. If a target path is not already part of the v13 contract, either add that contract first or avoid the link.

### Verification record minimum

The `Verification Notes` section is not free-form. At minimum it must record:

- exact corpus files and/or upstream files checked
- exact upstream URLs used for final verification where available
- the human reviewer named in `reviewed_by`
- `last_reviewed` date
- any known limitation, transitional caveat, or unresolved edge case that a reader should not miss

### Content template

```markdown
---
title: [Topic Title]
description: [one-sentence routing summary]
module: cookbook
origin_type: authored
when_to_use: [one-sentence scenario description]
related_modules: [luci, ucode, uci]
era_status: current
verification_basis: [short summary of evidence basis]
reviewed_by: [maintainer name]
last_reviewed: [ISO 8601 date]
---

# [Topic Title]

> **When to use:** [one-sentence scenario description]
> **Key components:** [OpenWrt subsystems involved]
> **Era:** Current (23.x+). Do not use deprecated patterns.

## Overview

[2–3 paragraphs: what, why, when]

## Complete Working Example

[Full annotated code. Every non-obvious line gets a comment.
Must be derived from or verified against actual upstream OpenWrt code.]

## Step-by-Step Explanation

[Walk through the example block by block]

## Anti-Patterns

### WRONG: [description]
```[lang]
[incorrect code]
```

### CORRECT: [description]
```[lang]
[correct code]
```

## Related Topics

- [Link to other cookbook page](./other-topic.md)
- [Link to module reference](../../luci/chunked-reference/js_source-api-form.md)

## Verification Notes

- Example verified against: [upstream source file or corpus file]
- Verified URL(s): [dereferenceable upstream URL or shipped corpus path]
- Anti-pattern observed in: [real AI failure or upstream deprecation notice]
- Reviewed by: [maintainer name]
- Last reviewed: [ISO 8601 date]
```

---

## Evidence Rules

### Rule 1: No ungrounded claims

Every factual claim in a cookbook page must be traceable to at least one of:

- Current corpus material (L1/L2 layers)
- Current upstream OpenWrt git repository code
- Official OpenWrt wiki content
- External human research packet (for era guide only)

If a claim cannot be traced, it must either be removed or explicitly marked as "unverified assumption — needs upstream confirmation."

### Rule 2: No fabricated URLs

If the page links to an upstream file, the URL must be dereferenceable. If the exact commit is unknown, link to the main branch. Never construct a URL by guessing a path that "probably exists."

### Rule 3: Anti-patterns must be real

Anti-pattern examples should be either:

- Observable AI failure modes documented by the maintainer
- Deprecated patterns documented in upstream OpenWrt sources
- Known community confusion patterns from forum/GitHub analysis

Do not invent hypothetical anti-patterns.

### Rule 4: Code examples must be verifiable

- ucode examples must use only functions documented in `ucode/chunked-reference/` or `ucode.d.ts`
- LuCI JavaScript examples must use only APIs documented in `luci/chunked-reference/`
- Shell/UCI examples must use only commands available in standard OpenWrt busybox + UCI CLI
- Makefile examples must conform to the OpenWrt buildroot Makefile contract as documented in `wiki/` or upstream `include/`

### Rule 5: Cookbook pages must not outrun the contract

If a page needs a new shipped path, a new output artifact, or a new metadata field to make its links or evidence work, that change belongs in 02-v13 or docs-new contract work first. 03-v13 can require those contracts but should not silently invent them.

---

## Topic Specifications

### Topic 1: openwrt-era-guide.md

**File:** `content/cookbook-source/openwrt-era-guide.md`  
**Tier:** S2 — highest-signal single document  
**Ships as:** `release-tree/cookbook/chunked-reference/openwrt-era-guide.md`

**Purpose:** Help AI tools distinguish between current (post-2019) and legacy (pre-2019) OpenWrt patterns. This is the single most impactful document in the cookbook because it directly addresses the #1 documented AI failure mode: generating Lua-era code.

**Must include:**

| Area | Current (use this) | Deprecated (do NOT use) |
|------|-------------------|------------------------|
| LuCI web views | JavaScript client-side views (`view.extend({...})`) | Lua CBI models (`SimpleForm`, `Map`) |
| Scripting language | ucode (`{% ... %}`) | Lua |
| Init system | procd (`start_service()`, `service_triggers()`) | SysVinit (`start()`, `stop()`) |
| Config access (script) | `uci.cursor()` module | `luci.model.uci` |
| Package checksums | `PKG_HASH` (sha256) | `PKG_MD5SUM` |
| JSON handling | Native ucode / `jshn` | `jsonfilter` |

**Additional requirements:**

- Regex-detectable markers for each deprecated pattern (so tooling can scan for legacy code)
- "When legacy code is acceptable" section: modifying existing Lua apps, targeting old releases, user explicitly requests
- Explicit OpenWrt version family target statement: "This guide targets current OpenWrt development in the 23.x/24.x family"
- Must be reviewed when the project changes its supported-current release family

**Evidence requirements:**

1. **Local corpus evidence:** Each "Current" recommendation must be traceable to current corpus files. Each "Deprecated" recommendation must be backed by current docs or observable repo history.
2. **External human research packet:** Maintainer must gather and synthesize forum/Reddit/GitHub evidence using the search terms specified in 02-v13 §S2 before the guide is finalized.
3. **Transitional honesty:** If a pattern is transitional rather than clearly deprecated, the guide must say so explicitly rather than forcing a false binary.

**Downstream linkage (specified in 02-v13 §S4):**

- Root `AGENTS.md` must point to this guide
- `luci/AGENTS.md` and `ucode/AGENTS.md` must link to it directly
- Cookbook pages that show historically confusing patterns must link back to the relevant section

---

### Topic 2: common-ai-mistakes.md

**File:** `content/cookbook-source/common-ai-mistakes.md`  
**Tier:** S3  
**Ships as:** `release-tree/cookbook/chunked-reference/common-ai-mistakes.md`

**Purpose:** Document the most common errors AI tools make when generating OpenWrt code. This is the defensive complement to the era guide — it tells the AI what NOT to do.

**Must include at minimum:**

| Mistake category | Wrong pattern | Correct pattern | Why it fails |
|-----------------|---------------|-----------------|--------------|
| Era confusion | Lua CBI form generation | JavaScript `view.extend()` | CBI is pre-2019; modern LuCI uses JS |
| Language confusion | Node.js APIs in ucode | ucode stdlib modules | ucode is not JavaScript |
| Network stack confusion | `swconfig` on modern targets | DSA-aware config patterns | Modern OpenWrt switched to DSA on most targets |
| Filesystem assumptions | Writing to `/etc/` directly | Using UCI for config | `/etc/` is read-only on squashfs |
| Package management | `apt-get` / `yum` | `opkg` | OpenWrt uses its own package manager |
| Init system | `systemctl` / `service` | `procd` service scripts | OpenWrt does not use systemd |
| Build system | Standard cmake/make | OpenWrt Makefile contract | Buildroot has its own Makefile DSL |

**Evidence requirements:**

- Each mistake should be traceable to real AI failure modes observed by the maintainer or documented in community forums
- The "Correct pattern" column must reference specific corpus files

---

### Topic 3: architecture-overview.md

**File:** `content/cookbook-source/architecture-overview.md`  
**Tier:** S3  
**Ships as:** `release-tree/cookbook/chunked-reference/architecture-overview.md`

**Purpose:** Give AI tools a structural mental model of how OpenWrt components interact. Without this, AI tools treat each module as an isolated API and fail at cross-component tasks.

**Must include:**

- High-level component diagram: LuCI → uhttpd → rpcd → ubus → daemons → UCI → config files
- What each layer does and which module documents it
- The data flow for a typical configuration change (user clicks UI → config file modified)
- Which components run on the router vs which are build-time only
- Where ACLs and permissions fit between LuCI, rpcd, and ubus

**Evidence requirements:**

- Component relationships must be verifiable by tracing through the existing corpus modules
- Build-time vs runtime distinction must be accurate for current OpenWrt

---

### Topic 4: procd-service-lifecycle.md

**File:** `content/cookbook-source/procd-service-lifecycle.md`  
**Tier:** S3  
**Ships as:** `release-tree/cookbook/chunked-reference/procd-service-lifecycle.md`

**Purpose:** Document the complete lifecycle of a procd-managed service from init script to running process.

**Must include:**

- Complete example init script with annotations
- Instance lifecycle calls such as `procd_open_instance`, `procd_set_param`, and `procd_close_instance`
- `start_service()` / `stop_service()` / `service_triggers()` contract
- How procd monitors and restarts services
- How to trigger service restart on UCI config change
- Anti-pattern: SysVinit-style `start()`/`stop()` functions

**Evidence requirements:**

- All API calls must reference the procd module corpus
- Example must be derivable from actual upstream init scripts

---

### Topic 5: minimal-openwrt-package-makefile.md

**File:** `content/cookbook-source/minimal-openwrt-package-makefile.md`  
**Tier:** S3  
**Ships as:** `release-tree/cookbook/chunked-reference/minimal-openwrt-package-makefile.md`

**Purpose:** Provide the minimal correct Makefile for the most common OpenWrt package types.

**Must include:**

- Minimal C package Makefile (annotated)
- Why `PKG_HASH` not `PKG_MD5SUM`
- The `include $(INCLUDE_DIR)/package.mk` contract
- One minimal `Package/install` example so the page shows how files actually land in the image
- Anti-pattern: standard cmake/make Makefiles that bypass the buildroot

**Evidence requirements:**

- Makefile structure must match current `include/package.mk` contract
- Example packages should reference real upstream packages from the wiki or openwrt-core corpus

---

### Topic 6: uci-read-write-from-ucode.md

**File:** `content/cookbook-source/uci-read-write-from-ucode.md`  
**Tier:** S3  
**Ships as:** `release-tree/cookbook/chunked-reference/uci-read-write-from-ucode.md`

**Purpose:** Show the correct ucode pattern for reading and writing UCI configuration.

**Must include:**

- Complete ucode example: `uci.cursor()` → `get()` / `set()` → `commit()`
- Error handling pattern
- How to load, modify, and save a UCI section
- Anti-pattern: using Lua `luci.model.uci` or shell `uci` CLI from ucode

**Evidence requirements:**

- All API calls must be verified against `ucode/chunked-reference/c_source-api-module-uci.md`
- Function signatures must match `ucode.d.ts`

---

### Topic 7: luci-form-with-uci.md

**File:** `content/cookbook-source/luci-form-with-uci.md`  
**Tier:** S3  
**Ships as:** `release-tree/cookbook/chunked-reference/luci-form-with-uci.md`

**Purpose:** Show the correct pattern for building a LuCI settings page that reads/writes UCI config.

**Must include:**

- Complete JavaScript view example: `view.extend()` → `form.Map` → `form.TypedSection` → `form.Value`
- How the form framework auto-binds to UCI config
- How to add validation
- How custom RPC calls work alongside form bindings
- Which parts belong in ACL/rpcd declarations versus the page's form code
- Anti-pattern: Lua CBI `Map`/`SimpleForm` and `luci.model.cbi`

**Evidence requirements:**

- All API calls must be verified against `luci/chunked-reference/js_source-api-form.md` and `js_source-api-uci.md`
- Example should be structurally comparable to real LuCI apps in `luci-examples/` corpus

---

### Topic 8: embedded-constraints.md

**File:** `content/cookbook-source/embedded-constraints.md`  
**Tier:** A3  
**Ships as:** `release-tree/cookbook/chunked-reference/embedded-constraints.md`

**Purpose:** Document the embedded-systems constraints that make OpenWrt different from server Linux since AI tools trained on server-side Linux assume glibc, unlimited RAM, and standard GNU tools.

**Must include:**

- musl vs glibc: what works, what breaks
- Flash storage: squashfs + overlay, wear considerations, why not to write frequently to `/etc/`
- RAM budgets: 32–256MB typical device, why background services need to be lightweight
- busybox vs GNU coreutils: missing flags, different behavior
- Package size considerations: why to prefer ucode over Lua+LuCI dependencies

**Evidence requirements:**

- Hardware constraints should be traceable to OpenWrt device documentation or community knowledge
- Software differences should be verifiable against upstream musl/busybox documentation

---

## Authoring Process

### Step 1: Draft

For each topic, use an AI tool with a large context window. Load the relevant module's `bundled-reference.md` and any `.d.ts` files.

For cross-component topics (e.g., `architecture-overview.md`, `inter-component-communication-map.md`) that span multiple subsystems, the author should load the root `llms-full.txt` or a tailored aggregation of multiple modules' `bundled-reference.md` files instead of a single module reference.

The draft phase should also collect the exact shipped paths the page will link to so cross-links are checked while writing rather than patched later.

Prompt template:
```text
Write an annotated cookbook entry for [topic] using ONLY the APIs documented
in this reference. Include anti-patterns that an AI would typically generate.
Follow the section contract: Overview, Complete Working Example,
Step-by-Step Explanation, Anti-Patterns, Related Topics, Verification Notes.
```

### Step 2: Verify

Every code example must be manually verified against:

- The corpus material already generated by the pipeline (L1/L2 layers)
- The actual upstream OpenWrt git repository source code
- The `ucode.d.ts` type definitions (for ucode examples)

### Step 3: Review

- The committed page is a maintainer-reviewed artifact
- AI may draft or revise text, but the maintainer must confirm factual accuracy
- The `verification_basis` and `last_reviewed` fields must be filled before the page is considered complete
- If AI assistance was used, the verification notes should disclose it in the form `AI-drafted by [tool], verified by [maintainer] against [evidence]`

### Step 4: Ingest

After authoring, the page enters the pipeline via `02i-ingest-cookbook.py` and is processed through L1 → L2 → release-tree like any other content.

---

## Maintenance Policy

- Cookbook pages are **not** regenerated every pipeline run by default
- They are re-reviewed when:
  - Upstream APIs they depend on materially change
  - The era guide changes
  - Repeated AI failures indicate the page is stale
- The project should track cookbook review cadence as manual maintenance, not pretend it is fully automatic
- The generation prompt/spec for AI-assisted drafting should live in `docs/docs-new/pipeline/` once that tree exists

---

## Release-Tree Output Structure

After a full pipeline run with all S-tier topics authored, the cookbook module appears as:

```
release-tree/cookbook/
  AGENTS.md                           ← overlaid from release-inputs/release-include/cookbook/AGENTS.md
  llms.txt                            ← auto-generated by stage 06
  map.md                              ← auto-generated by stage 05a
  bundled-reference.md                ← auto-generated by stage 05a
  chunked-reference/
    openwrt-era-guide.md              ← S2 topic 1 (S-tier, must ship)
    common-ai-mistakes.md             ← S3 topic 2 (S-tier, must ship)
    architecture-overview.md          ← S3 topic 3 (S-tier, must ship)
    procd-service-lifecycle.md        ← S3 topic 4 (A-tier)
    minimal-openwrt-package-makefile.md  ← S3 topic 5 (A-tier)
    uci-read-write-from-ucode.md      ← S3 topic 6 (A-tier)
    luci-form-with-uci.md             ← S3 topic 7 (A-tier)
    embedded-constraints.md           ← A3 topic 8 (A-tier)
```

B-tier stretch topics (inter-component-communication-map, uci-read-write-from-shell, hotplug-handler-pattern, ucode-rpcd-service-pattern) ship if completed before v13 closes; otherwise they are listed in `docs/docs-new/roadmap/deferred-features.md`.

---

## Acceptance Criteria

### Minimum viable v13 cookbook (S-tier gate)

```text
- [ ] content/cookbook-source/ directory exists
- [ ] openwrt-era-guide.md exists and passes the content contract (all required sections present)
- [ ] openwrt-era-guide.md includes the era transition table with all 6 rows
- [ ] openwrt-era-guide.md includes external research packet evidence (not just AI priors)
- [ ] openwrt-era-guide.md includes regex-detectable legacy markers and a "when legacy code is acceptable" section
- [ ] common-ai-mistakes.md exists and passes the content contract
- [ ] common-ai-mistakes.md includes at least 7 mistake categories with WRONG/CORRECT pairs
- [ ] common-ai-mistakes.md ties each mistake to a real failure mode or community confusion source and points to specific corpus references for the correct path
- [ ] architecture-overview.md exists and passes the content contract
- [ ] architecture-overview.md includes component diagram, data flow, and ACL/permission boundaries
- [ ] All 3 S-tier files have all required frontmatter fields filled, including description and reviewed_by
- [ ] All 3 S-tier files have verification_basis and last_reviewed populated
- [ ] All 3 S-tier files use final release-tree-valid cross-links
- [ ] Pipeline run produces release-tree/cookbook/ with all expected generated artifacts
- [ ] cookbook appears in root llms.txt under "Guides" category
- [ ] cookbook/AGENTS.md references openwrt-era-guide.md
```

### Full v13 cookbook (A-tier gate)

```text
- [ ] All 8 priority 1 + 2 topics pass the content contract
- [ ] Every code example has been verified against corpus or upstream source
- [ ] Every anti-pattern is traceable to real failure modes
- [ ] No cookbook page links to a non-existent corpus file
- [ ] Inter-module cross-references resolve correctly after pipeline run
- [ ] No cookbook page duplicates large reference sections that belong in generated module docs
```

---

## Resolved Questions

1. **Cookbook routing priority:** Resolved — `Guides` category should appear first in `CATEGORY_ORDER`. "Guides" also sorts first alphabetically among the current categories, so this is both the intentional and the natural order. Updated in 02-v13.

2. **A-tier cut line:** Resolved — `architecture-overview.md` promoted to S-tier. It is a structural dependency for every cross-module cookbook topic.

---

## Addendum: External Review Response

The following responds to an external senior engineer's review of this specification.

### Accepted: `topic_slug` redundancy (Logic Error)

**Criticism:** Requiring the human to type the slug in frontmatter when it must mathematically match the filename creates a redundant failure point.

**Response:** Accepted. `topic_slug` has been removed from required authored frontmatter. `02i` now derives it from the filename. The 02-v13 `02i` spec has been updated to match.

### Accepted: Dead-link checker reliance

**Criticism:** Cross-links authored for eventual `release-tree/cookbook/chunked-reference/` paths are brittle if the pipeline topology changes.

**Response:** Accepted. Upon verification, stage `08` does **not** currently include a dead-link checker for internal relative links — my initial response incorrectly claimed it did. The 02-v13 spec has been updated to add a programmatic dead-link checking requirement to `08-validate-output.py` as part of the v13 validation work. The S-tier acceptance gate already requires "release-tree-valid cross-links" — this fix ensures that requirement is enforced by CI, not just a human checkbox.

### Accepted: `origin_type` conflation

**Criticism:** Using `origin_type: cookbook` conflates destination routing with data provenance. Existing `origin_type` values (`wiki_page`, `js_source`, `c_source`, `readme`, `header_api`, etc.) all describe how the content was produced, not where it lives.

**Response:** Accepted. `origin_type` has been changed to `authored` throughout the spec. This cleanly separates "how it was made" (authored by hand) from "where it lives" (cookbook module), and future-proofs the pipeline for hand-authored content in any module. Updated in 02-v13 and 03-v13.

### Noted but not adopted: Scope/capacity concern

**Criticism:** 12 hand-authored topics (~5 days of work) threatens to bog down pipeline development. Ship only S-tier (2 topics) for v13.

**Response:** This is a valid project management observation, but the spec already handles it correctly. The tier system is exactly this triage mechanism: S-tier topics *must* ship (now 3 with architecture-overview promotion), A-tier topics *should* ship, B-tier topics are stretch goals. The spec explicitly says B-tier goes to `deferred-features.md` if not completed. The reviewer is recommending a practice the document already prescribes. The decision of how many A-tier topics actually get written is a runtime capacity call, not a spec deficiency.

### Noted but not adopted: Research packet formality concern

**Criticism:** The "external human research packet" mandate is over-engineered for a hobby project. Drop the formal gathering requirement.

**Response:** The reviewer underestimates the risk being mitigated. The era guide is the single highest-signal document in the deliverable. If its claims about "current vs deprecated" are wrong, every downstream consumer gets bad guidance. The research packet is not busywork — it is the evidence that distinguishes "AI hallucinated what 'current' means" from "human verified against real community sources." That said, the spec already says "gather and synthesize" — it does not require a formal document. The maintainer can do the searches, note what they found, and record the evidence in the verification notes. The process is proportional.

### Noted but not adopted: AI-deficiency coupling concern

**Criticism:** `common-ai-mistakes.md` addresses today's AI weaknesses. Those weaknesses may be solved in future model generations, making the file stale.

**Response:** True but acceptable. The maintenance policy already states pages are re-reviewed "when repeated AI failures indicate the page is stale." If models stop making these mistakes, the page becomes less useful but not harmful — a "don't do X" guide that's already followed correctly is inert. This is a low-severity staleness risk, not an architectural flaw. And the practical reality is that AI tools hallucinating `systemctl` and `apt-get` on OpenWrt will persist for at least several more model generations because those patterns dominate training data.

---
