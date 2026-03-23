# V13 S-Tier Implementation Specification

**Recorded:** 2026-03-22  
**Purpose:** Concrete implementation specs for S1–S7 from the v13 tier list  
**Predecessor:** [01-v13-baseline-verification-audit-2026-03-22.md](01-v13-baseline-verification-audit-2026-03-22.md)  
**Next:** 03-v13 cookbook content spec, 04-v13 A-tier spec

---

## Execution Sequence

S-tier items have dependencies. This sequence respects them:

```
S7 (glossary)  ─────────────────────────────────────────────┐
S6 (docs-new structure)  ──────────────────────────────────┐│
S5 (routing contract)  → writes to docs-new created by S6 ┘│
S1 (llms.txt descriptions)  ───────────────────────────────┘│
S2 (era content)  ─────────────────────────────────────────┐│
S4 (per-module AGENTS.md)  → uses era content from S2 ────┘│
S3 (cookbook module)  → needs glossary terms, era framing ──┘
```

**Recommended implementation order: S6 → S7 → S5 → S1 → S2 → S4 → S3**

S6 and S7 are foundations. S5 defines the schema that S1 must comply with. S2 provides era content that S4 needs to reference. S3 is the capstone that exercises all previous work.

---

## S6: Rebuild Project Documentation Tree

### Goal

Create `docs/docs-new/` with a clean topic-based directory structure. During v13, `docs/docs-new/` is the authoritative documentation target. New v13 documents should reference docs-new truth, not legacy docs that may later be deprecated. After v13, rename `docs/` → `docs-old/`, `docs/docs-new/` → `docs/`.

### Directory structure

```
docs/docs-new/
├── output/
│   └── release-tree-contract.md      ← migrated from a copy of docs/specs/v12/release-tree-contract.md; absorbs routing ownership contract
├── pipeline/
│   ├── pipeline-stage-catalog.md     ← new, ordered list of every pipeline script + stage family
│   └── regeneration-rules.md         ← new, rerun/trigger rules extracted from CLAUDE.md + architecture knowledge
├── project/
│   └── glossary-and-naming-contract.md   ← S7 deliverable
├── plans/
│   └── v13/                          ← copy of current docs/plans/v13/
└── roadmap/
    └── deferred-features.md          ← new, captures out-of-scope items from 00-v13
```

### File inventory

#### [NEW] `docs/docs-new/output/release-tree-contract.md`

Migrate and update the existing `docs/specs/v12/release-tree-contract.md` (214 lines). Changes:
- Add v13 additions: cookbook module, per-module `AGENTS.md`, expanded README
- Add delivery surface matrix (Pages, corpus repo, ZIP release)
- Add routing ownership records: which stage family produces and finalizes which files
- Rename version label from V5a to V6
- Treat docs-new as self-contained: no dependency links back into legacy docs/

#### [NEW] `docs/docs-new/pipeline/pipeline-stage-catalog.md`

Create a single ordered catalog of every script in the pipeline. Each entry must include:

- script name
- stage family in brackets, e.g. `openwrt-docs4ai-02a-scrape-wiki.py (collector)`
- one-line role summary
- inputs
- outputs
- rerun notes
- downstream consumers

This file is the durable answer to "what does each pipeline file do and why is it in that stage family?"

#### [NEW] `docs/docs-new/pipeline/regeneration-rules.md`

Extract from institutional knowledge and `CLAUDE.md`:
- What triggers pipeline reruns (commit SHA changes, content additions, schema changes)
- Which stages can be rerun independently
- Environment variable requirements per stage
- How the `release-inputs/` overlay system works, including that overlay means copy-on-top with possible override of same-path generated files

#### [NEW] `docs/docs-new/roadmap/deferred-features.md`

Capture items from the 00-v13 C-tier and out-of-scope decisions:
- Docker-based verification
- MCP server
- Compile loop
- Rationale for deferral

### Acceptance test

```
- [ ] docs/docs-new/ exists with output/, pipeline/, project/, plans/, roadmap/ subdirectories
- [ ] release-tree-contract.md has a V6 version label
- [ ] pipeline-stage-catalog.md documents every numbered script in order with a stage family label
- [ ] regeneration-rules.md documents all 02*–08 stages
- [ ] No broken internal links between docs-new files
```

---

## S7: Glossary and Naming Contract

### Goal

Lock down project terminology so that all plan files, specs, and code comments use the same words for the same things.

### File

#### [NEW] `docs/docs-new/project/glossary-and-naming-contract.md`

### Content

Must define at minimum:

| Term | Definition |
|------|-----------|
| release-tree | The published output directory delivered to consumers |
| deliverable | The validated user-facing artifact set produced for publication |
| deploy target | A concrete publication destination for the deliverable |
| release org | The GitHub organization/account that owns the public delivery surfaces |
| corpus repo | The public-facing repository that receives published user-facing files |
| pipeline repo | The development repository where extraction, normalization, validation, and publication logic live |
| development repo | Same practical meaning as pipeline repo; use one term consistently in docs-new and cross-reference the other |
| module | A named subdirectory in the release-tree containing bundled/chunked reference content |
| L1-raw | Stage 02 output: markdown files with `.meta.json` sidecars |
| L2-semantic | Stage 03 output: normalized markdown with YAML frontmatter |
| L3 | Navigational surfaces: `llms.txt`, `map.md`, skeleton files |
| L4 | Assembled reference outputs shipped under the public `bundled-reference.md` contract |
| bundled-reference | The same authoritative module content as `chunked-reference/`, but packaged as one stable bundled file or bundle index |
| chunked-reference | The same authoritative module content as `bundled-reference.md`, but packaged as separate topic files for targeted lookup |
| routing index | `llms.txt` files that serve as entry points for AI tools |
| era | The distinction between pre-2019 (Lua/CBI/swconfig) and post-2019 (JS/form/DSA) OpenWrt patterns |
| cookbook | The final published task-oriented guidance module under `release-tree/cookbook/` |
| cookbook source | Human-authored upstream markdown stored in `content/cookbook-source/` before ingest |
| cookbook staged output | Pipeline-staged cookbook material in `L1-raw/cookbook/` and `L2-semantic/cookbook/` |
| collector / ingest | A stage family that reads source material and writes L1 sidecars + markdown |
| normalizer | A stage family that transforms L1 into normalized L2 outputs |
| AI enricher | A stage family that adds optional AI-derived metadata |
| assembler | A stage family that packages normalized content into publishable reference forms |
| router | A stage family that writes AI routing indexes |
| finalizer | A stage family that applies overlays and materializes the shipped release-tree |
| validator | A stage family that blocks promotion of broken outputs |
| source_url | Provenance field containing the dereferenceable upstream URL for the source artifact |
| source_commit | Provenance field containing the upstream git commit SHA when applicable |
| source_locator | Optional operational locator such as a repo-relative path or source identifier retained for debugging/intake traceability |
| delivery surface | A distribution channel: GitHub Pages, corpus repo, ZIP release |
| overlay | A source-controlled directory tree copied on top of generated output; this can add files and also override same-path generated files |
| gatekeeper | Stage 08 validation checks that prevent broken outputs from being promoted |

### Naming rules

- Module names: lowercase, hyphenated (`openwrt-core`, `luci-examples`, `cookbook`)
- Script names: `openwrt-docs4ai-{NN}{letter}-{verb}-{noun}.py` with `02i-ingest-cookbook.py` as the v13 cookbook choice
- Plan files: `{NN}-v{version}-{topic}-{date}.md`
- L2 filenames: follow the owning stage's documented naming contract; v13 should preserve current stable names unless there is a deliberate migration plan

### Folder-lineage rule

When a concept appears in multiple pipeline layers, docs-new must define each folder's role explicitly rather than assume the repeated name is self-explanatory. For cookbook content, the minimum lineage is:

- `content/cookbook-source/` → authored source
- `L1-raw/cookbook/` → ingested staging output
- `L2-semantic/cookbook/` → normalized staging output
- `release-tree/cookbook/` → final public delivery module

### Acceptance test

```
- [ ] File exists at docs/docs-new/project/glossary-and-naming-contract.md
- [ ] All terms listed above are defined
- [ ] Naming rules section covers modules, scripts, plans, and L2 files
```

---

## S5: Routing Ownership Contract

### Goal

Document which pipeline stage family owns which output file, so that developers know where to look when a file needs modification.

### File

This is a section within the release-tree-contract (S6's `docs/docs-new/output/release-tree-contract.md`), not a separate file. Routing ownership belongs inside the release-tree contract because it defines what the release-tree must contain.

### Content to add

Use a normalized record format instead of a wide ASCII matrix. Each record should include these fields:

- artifact path
- artifact family
- stage family
- generated by
- finalized by
- inputs
- overlay / override behavior
- independent rerun scope
- validation owner

Minimum records to include:

#### Record: root routing indexes

- artifact path: `release-tree/llms.txt`, `release-tree/llms-full.txt`
- artifact family: root routing indexes
- stage family: router
- generated by: `06`
- finalized by: `06`
- inputs: `L2-semantic/`
- overlay / override behavior: none
- independent rerun scope: rerun `06`
- validation owner: `08`

#### Record: root companion docs

- artifact path: `release-tree/AGENTS.md`, `release-tree/README.md`
- artifact family: root companion outputs
- stage family: publication companion generator → finalizer
- generated by: `05b`
- finalized by: `07`
- inputs: `L2-semantic/`, `cross-link-registry.json`, `release-inputs/release-include/`
- overlay / override behavior: overlay may override the generated root file with a source-controlled replacement
- independent rerun scope: rerun `05b`, then `07`
- validation owner: `08`

#### Record: root web index

- artifact path: `release-tree/index.html`
- artifact family: root web entrypoint
- stage family: finalizer
- generated by: `07`
- finalized by: `07`
- inputs: `release-tree/`, `release-inputs/release-include/`
- overlay / override behavior: overlay may replace the generated index with an override file
- independent rerun scope: rerun `07`
- validation owner: `08`

#### Record: module routing indexes

- artifact path: `release-tree/{module}/llms.txt`
- artifact family: module routing indexes
- stage family: router
- generated by: `06`
- finalized by: `06`
- inputs: `L2-semantic/{module}/`
- overlay / override behavior: none unless a future contract explicitly allows it
- independent rerun scope: rerun `06`
- validation owner: `08`

#### Record: module reference surfaces

- artifact path: `release-tree/{module}/map.md`, `release-tree/{module}/bundled-reference.md`, `release-tree/{module}/chunked-reference/`
- artifact family: module reference outputs
- stage family: assembler
- generated by: `05a`
- finalized by: `05a`
- inputs: `L2-semantic/{module}/`
- overlay / override behavior: none in the current contract
- independent rerun scope: rerun `05a`
- validation owner: `08`

#### Record: typed IDE surfaces

- artifact path: `release-tree/{module}/types/*.d.ts`
- artifact family: IDE type surfaces
- stage family: publication companion generator
- generated by: `05c`
- finalized by: `05c`
- inputs: `cross-link-registry.json`
- overlay / override behavior: none in the current contract
- independent rerun scope: rerun `05c`
- validation owner: `08`

#### Record: per-module AGENTS guidance

- artifact path: `release-tree/{module}/AGENTS.md`
- artifact family: per-module AI guidance
- stage family: finalizer
- generated by: notional / unresolved for v13 planning
- finalized by: `07`
- inputs: `release-inputs/release-include/{module}/AGENTS.md`
- overlay / override behavior: shipped as overlay-provided files that may override generated placeholders if placeholders ever exist
- independent rerun scope: rerun `07`
- validation owner: `08`

### Acceptance test

```
- [ ] Routing ownership records are present in release-tree-contract.md
- [ ] Every file in the current release-tree is accounted for
- [ ] Every record includes rerun scope, overlay behavior, and validation owner
```

---

## S1: Fix Root `llms.txt` Module Descriptions

### Goal

Replace the alphabetical-first-file heuristic with curated module descriptions so that `llms.txt` accurately describes each module.

### File to modify

#### [MODIFY] `.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py`

### Changes

Add a `MODULE_DESCRIPTIONS` dict after the existing `MODULE_CATEGORIES` dict (around line 52):

```python
MODULE_DESCRIPTIONS = {
    "procd": "OpenWrt process manager and init system: procd init scripts, service registration, and supervised process lifecycle.",
    "uci": "Unified Configuration Interface: UCI CLI tool, API bindings, and default configuration schemas for OpenWrt packages.",
    "openwrt-hotplug": "Hotplug event subsystem: netifd-injected environment variables and /etc/hotplug.d/ script interfaces.",
    "ucode": "ucode scripting language: standard library, runtime modules (fs, ubus, uci, uloop, nl80211, rtnl), and C API.",
    "luci": "LuCI web interface framework: JavaScript client API for forms, UCI bindings, RPC, DOM, and UI widgets.",
    "openwrt-core": "OpenWrt buildroot core packages: early boot firmware, kernel module infrastructure, and base-files.",
    "luci-examples": "LuCI community application examples: full plugin source code for Docker, statistics, DDNS, and more.",
    "wiki": "OpenWrt project documentation: developer guides, architecture references, release notes, and hardware support.",
}
```

Then modify the module description selection (around line 433) to prefer the override dict:

```python
module_description = MODULE_DESCRIPTIONS.get(
    module,
    next(
        (entry["description"] for entry in l2_entries if entry["description"] != DESCRIPTION_FALLBACK),
        DESCRIPTION_FALLBACK,
    ),
)
```

### Why not new metadata fields?

The unresolved design decision is where curated module descriptions should live long term. The likely homes are:

- temporary implementation detail in `06`
- dedicated module metadata file in docs-new or repo config

This S-tier spec does **not** settle that storage question permanently. It only requires that curated module descriptions exist, are human-reviewed, and are auditable against actual module scope. This keeps the implementation moving without pretending the governance question is fully solved.

### Description governance requirements

- Descriptions must be human-authored or AI-assisted but human-reviewed
- The review criterion is module truthfulness, not marketing polish
- The storage location for these descriptions is still notional in v13 and must be documented explicitly in docs-new before v13 closes
- New modules (like `cookbook`) must declare their module description at creation time rather than relying on alphabetical fallback

### Acceptance test

```
- [ ] Root llms.txt no longer says "CBI declarative form framework" for luci
- [ ] Root llms.txt no longer says "21.02 release" for wiki
- [ ] Each of the 8 module descriptions is a single sentence that accurately describes the module scope
- [ ] New modules without an override entry still get the alphabetical-first fallback (no crash)
```

---

## S2: Era Content — Current vs Legacy OpenWrt Patterns

### Goal

Create explicit guidance documents that help AI tools distinguish between current (post-2019) and legacy (pre-2019) OpenWrt patterns.

### Key era transitions

| Area | Legacy (pre-2019) | Current (post-2019+) |
|------|-------------------|---------------------|
| Web UI | Lua CBI templates | JavaScript ES module views (`require form`, `require uci`) |
| Config API scripting | `lua`, `ash` + `uci` CLI | `ucode` + `uci` module |
| Network stack | `swconfig` | `DSA` (distributed switch architecture) |
| Init system | `procd` (same, but scripts evolved) | `procd` with modern service patterns |
| WiFi backend | `madwifi`, `broadcom-wl` → `mac80211` | `mac80211` (standard since 19.07) |

### Files

#### [NEW] `content/cookbook-source/openwrt-era-guide.md`

Hand-authored guide (part of the cookbook module, delivered via `02i`) covering:
- The 2019–2020 modernization summary
- "If you see X, use Y instead" table
- Why wiki pages may reference legacy patterns
- Links to the relevant current-pattern reference files in other modules

This file ships in the release-tree as `cookbook/chunked-reference/openwrt-era-guide.md`.

### Research grounding requirements

This guide must be grounded in:

1. the local generated documentation corpus already produced by the pipeline
2. an external human research packet gathered by the maintainer from the OpenWrt forum, Reddit, and GitHub issues/discussions/comments

Minimum suggested search terms to gather and synthesize before the guide is finalized:

- `site:forum.openwrt.org LuCI JavaScript CBI deprecated form.Map`
- `site:forum.openwrt.org swconfig DSA legacy current recommendation`
- `site:reddit.com/r/openwrt LuCI JavaScript CBI`
- `site:reddit.com/r/openwrt swconfig DSA`
- `site:github.com/openwrt/luci/issues CBI JavaScript form.Map`
- `site:github.com/openwrt/openwrt/issues swconfig DSA`
- `site:github.com/openwrt/luci/discussions JavaScript views ucode rpcd`

This external research packet is a required human input to v13. It is not something the pipeline can infer on its own.

### Integration with AGENTS.md (S4)

The root `AGENTS.md` gets an era warning section referencing this guide. Per-module `AGENTS.md` files for `luci` and `ucode` add module-specific era notes.

### Acceptance test

```
- [ ] content/cookbook-source/openwrt-era-guide.md exists and covers all 5 era transitions above
- [ ] The guide references specific files in other modules (e.g., js_source-api-form.md)
- [ ] After pipeline run, openwrt-era-guide.md appears in release-tree under cookbook/
```

---

## S4: Per-Module AGENTS.md Files

### Goal

Give AI tools module-specific behavioral orientation: what to start with, what to avoid, era concerns.

### Files to create

Immediate v13 assumption: per-module `AGENTS.md` files are shipped from `release-inputs/release-include/{module}/AGENTS.md` and overlaid into the release-tree during the existing copy step.

This is still a **notional governance area**. The v13 docs must later specify:

- who authors these files
- whether AI assistance is allowed and how it is disclosed
- how human review works
- why each module-specific file exists
- whether these files remain static or later become generated from metadata

Priority modules (must have for v13):

#### [NEW] `release-inputs/release-include/luci/AGENTS.md`

```markdown
# AGENTS.md — luci module

## Scope
Modern JavaScript LuCI framework for building OpenWrt web interfaces.

## Era Warning
Do NOT generate Lua CBI templates. The current LuCI framework uses JavaScript ES modules.
Legacy patterns like `require("luci.model.cbi")` are pre-2019 and will not work on modern OpenWrt.

## Start Here
- `map.md` → structural overview of all API surfaces
- `chunked-reference/js_source-api-form.md` → primary form framework (use this, not CBI)
- `chunked-reference/js_source-api-uci.md` → UCI config bindings

## Avoid
- `js_source-api-cbi.md` is a legacy compatibility layer. Reference it only for maintaining existing Lua views.
```

#### [NEW] `release-inputs/release-include/ucode/AGENTS.md`

```markdown
# AGENTS.md — ucode module

## Scope
ucode is a lightweight scripting language for OpenWrt, similar to JavaScript but NOT JavaScript.

## Language Warning
ucode has JavaScript-like syntax but is a distinct language. Do NOT use Node.js APIs, browser APIs, or ES module syntax.
The runtime is C-based with embedded modules: fs, ubus, uci, uloop, nl80211, rtnl.

## Start Here
- `map.md` → overview of all ucode stdlib and module APIs
- `chunked-reference/c_source-api-module-uci.md` → ucode UCI bindings
- `types/ucode.d.ts` → IDE type definitions for autocompletion
```

#### [NEW] `release-inputs/release-include/cookbook/AGENTS.md`

```markdown
# AGENTS.md — cookbook module

## Scope
Task-oriented guides maintained by project contributors. Unlike reference modules, these are human-authored.

## Usage
These are "how to do X" guides, not API references. Start with `map.md` for the topic list.
Cross-reference with the relevant reference module for API details.

## Era Guide
`chunked-reference/openwrt-era-guide.md` documents the 2019–2020 OpenWrt modernization.
Read this before generating any configuration or scripting code.
```

### Modify `05b` to skip overwriting static AGENTS.md

Currently `05b` writes `AGENTS.md` to both `OUTDIR` and `RELEASE_TREE_DIR`. The root `AGENTS.md` should still be generated by `05b`, but per-module files placed by the overlay should not be overwritten. Since the overlay copy happens after `05b` runs, this is already the case with the existing pipeline ordering. Verify by checking the workflow step order.

### Modify root AGENTS.md template in `05b`

Add an era warning section and per-module AGENTS.md discovery notice to the release-tree AGENTS.md template (the `release_agents_content` f-string around line 137 of `05b`):

```markdown
## Era Awareness
OpenWrt underwent a major modernization in 2019–2020. Many wiki pages and code examples reference
legacy patterns (Lua CBI, swconfig, ash scripting). Prefer current patterns (JavaScript views,
DSA, ucode). See `cookbook/chunked-reference/openwrt-era-guide.md` for details.

## Per-Module Instructions
Some modules include their own `AGENTS.md` with module-specific guidance.
Check `[module]/AGENTS.md` before beginning work on a specific subsystem.
```

### Acceptance test

```
- [ ] release-inputs/release-include/luci/AGENTS.md exists
- [ ] release-inputs/release-include/ucode/AGENTS.md exists
- [ ] release-inputs/release-include/cookbook/AGENTS.md exists
- [ ] Root release-tree AGENTS.md references openwrt-era-guide and per-module AGENTS.md
- [ ] Per-module AGENTS.md content is distinct from llms.txt (behavioral, not routing)
- [ ] No per-module AGENTS.md duplicates llms.txt file listings
```

---

## S3: Cookbook Module Integration

### Goal

Add a `cookbook` module to the pipeline for hand-authored, task-oriented guides. The first guide is the era guide (S2).

### Files

#### [NEW] `content/cookbook-source/openwrt-era-guide.md`

See S2 above for content specification. This is the first cookbook document.

The `content/` directory is a project-root authoring area for hand-authored content that enters the pipeline via ingest scripts, parallel to how `.github/scripts/` holds pipeline code.

#### [NEW] `.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py`

**Why `02i` and not another stage:** The `02*` scripts all produce `L1-raw/{module}/` output with `.meta.json` sidecars. The distinction is producer/collector (02*) vs processor (03+). A cookbook ingest script is a producer — it reads from `content/cookbook-source/` and writes to `L1-raw/cookbook/` with the same sidecar contract as other ingest scripts. This lets it run in parallel with all other collectors during CI.

Script behavior (~60 lines):

1. Read all `.md` files from `content/cookbook-source/`
2. Require YAML frontmatter in each authored file; derive `topic_slug` from the markdown basename (do not require it in frontmatter)
3. For each file, copy the markdown body to `L1-raw/cookbook/{filename}`
4. Generate `.meta.json` sidecar with:
   - `module: "cookbook"`
   - `origin_type: "authored"`
   - `slug`: derived from filename
    - authored routing/review fields carried from source frontmatter: `title`, `description`, `when_to_use`, `related_modules`, `era_status`, `verification_basis`, `reviewed_by`, `last_reviewed`
    - `source_url`: absent for local-only authored content unless a public canonical URL exists later
    - `source_commit`: absent unless the source area later gets its own versioned publication contract
    - `source_locator`: local authoring path or slug if operationally useful
5. Fail fast if required authored metadata is missing or inconsistent
6. Print count of files processed

The `.meta.json` sidecar is not cookbook-specific — it is the universal L1 contract. Every `02*` ingest script produces the same sidecar format. Stage `03` should normalize and carry through metadata; it should not invent cookbook provenance later.

```python
"""
Purpose: Ingest hand-authored cookbook content into L1-raw.
Phase: Collection
Layers: content/cookbook-source/ -> L1-raw/cookbook/
Inputs: content/cookbook-source/
Outputs: L1-raw/cookbook/*.md, L1-raw/cookbook/*.meta.json
Dependencies: lib.config
"""
```

#### [MODIFY] `.github/scripts/openwrt-docs4ai-03-normalize-semantic.py`

Do **not** synthesize a cookbook commit sentinel in `03`. Cookbook content has no upstream git commit SHA, so `02i` should omit `source_commit`, `03` should carry through only the authored fields and provenance that actually exist, and `08` should treat `source_commit` as not required for `origin_type: authored`.

#### [MODIFY] `.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py`

Two changes:
1. Add `"cookbook": "Guides"` to `MODULE_CATEGORIES` (line 42)
2. Add `"Guides"` to `CATEGORY_ORDER` (line 52) — position it first (also alphabetically natural among current categories)
3. Add `"cookbook": "..."` to the new `MODULE_DESCRIPTIONS` dict (S1)

#### [MODIFY] `.github/workflows/openwrt-docs4ai-00-pipeline.yml`

Add `02i` invocation in the same parallel group as other collectors.

### Acceptance test

```
- [ ] content/cookbook-source/ directory exists with at least openwrt-era-guide.md and architecture-overview.md
- [ ] Running 02i produces L1-raw/cookbook/openwrt-era-guide.md and L1-raw/cookbook/openwrt-era-guide.meta.json
- [ ] 02i derives topic_slug from filename and fails fast if required authored frontmatter fields are missing
- [ ] 02i carries authored cookbook metadata fields into the L1 sidecar for downstream use
- [ ] Running the full pipeline produces release-tree/cookbook/ with map.md, bundled-reference.md, chunked-reference/
- [ ] Running the full pipeline with the minimum S-tier cookbook ships openwrt-era-guide.md, common-ai-mistakes.md, and architecture-overview.md
- [ ] cookbook appears in root llms.txt under "Guides" category (first position)
- [ ] cookbook/llms.txt lists openwrt-era-guide with accurate description
```

---

## Product README Expansion

### Goal

Expand the shipped README from 10 lines to ~60 lines. This is a consumer-facing document, not an internal spec.

### File to modify

#### [MODIFY] `release-inputs/release-include/README.md`

### Proposed content structure

```markdown
# openwrt-docs4ai

OpenWrt programming documentation packaged for AI tools, IDE integration, and developer reference.

## What This Is

A curated collection of OpenWrt API references, configuration schemas, and developer guides
optimized for AI ingestion. Auto-generated from official OpenWrt, LuCI, and ucode source
repositories.

## Quick Start

Point your AI coding tool (Copilot, Cursor, Claude, etc.) at this directory:
- Start with `llms.txt` for module routing
- Or open a module's `map.md` for structural orientation
- Or read `AGENTS.md` for AI tool navigation rules

## What's Inside

| Module | Description |
|--------|-------------|
| luci | JavaScript LuCI web interface framework ... |
| ucode | ucode scripting language runtime ... |
| ... | ... |

## File Layout

[explanation of llms.txt → module/llms.txt → map.md → bundled/chunked hierarchy]

## Era Note

OpenWrt underwent significant modernization in 2019–2020. Some documentation references
legacy patterns. See `cookbook/chunked-reference/openwrt-era-guide.md` for guidance on current vs
legacy approaches.

## How This Was Generated

[brief provenance: source repos, pipeline, commit SHAs, pipeline date]

## License

[attribution to OpenWrt project sources]
```

### The README vs output contract distinction

The README is the label on the box — what this is, who it's for, how to use it. The output contract (`docs/docs-new/output/release-tree-contract.md`) is the engineering spec — exact file schema, invariants, gatekeeper rules. They serve different audiences and should remain separate.

- **README** → ships with the product, consumer-facing
- **Output contract** → stays in the dev repo, maintainer-facing
- **AGENTS.md** → ships with the product, AI-tool-facing

### Acceptance test

```
- [ ] release-inputs/release-include/README.md is 50–80 lines (not strict)
- [ ] README contains no internal pipeline terminology (L1, L2, L3, L4, OUTDIR, staging)
- [ ] README contains a module table with accurate descriptions (using S1 curated text)
- [ ] README contains an era warning pointing to cookbook/chunked-reference/openwrt-era-guide.md
- [ ] README renders correctly on GitHub when viewed at openwrt-docs4ai/corpus
```

---

## Metadata Field Hardening

### Goal

Standardize provenance metadata across all ingest scripts and stamp final provenance as early as possible. This is a pre-release window to get the metadata contract right before it becomes a stable interface.

### Architecture decision

See 01-v13 §7 for the full architecture comparison. The decision is **ingest-time provenance stamping**:

- All `02*` ingest scripts stamp the best available `source_url` during collection
- Git-backed `02*` scripts stamp `source_commit` during collection
- `source_locator` is optional operational metadata for raw repo-relative paths, slugs, or source identifiers
- `03` carries `source_url` and `source_commit` through into L2 instead of reconstructing them late
- `03` no longer owns a repository-URL derivation table for provenance

### Files to modify

#### [NEW] `lib/source_provenance.py`

Create a shared provenance helper used by the ingest family. Responsibilities:

- normalize final dereferenceable `source_url`
- normalize `source_commit` for git-backed sources
- normalize optional `source_locator`
- keep the provenance contract out of `03`

#### [MODIFY] `.github/scripts/openwrt-docs4ai-02a-scrape-wiki.py`

In `write_page_output()`, stop writing the wiki URL under a one-off field name. Write it as final provenance at ingest time:

```python
"source_url": url,
"source_locator": source_path,
```

The value stays the same (full `https://openwrt.org/...` URL). `source_path` may remain as lower-level operational data if still useful, but the canonical provenance field becomes `source_url`.

#### [MODIFY] `.github/scripts/openwrt-docs4ai-02b-*.py` through `.github/scripts/openwrt-docs4ai-02h-*.py`

Unify the git-backed ingest scripts around the same provenance contract:

- `source_url`: final dereferenceable GitHub source URL
- `source_commit`: commit SHA for the checked-out source
- `source_locator`: repo-relative path if operationally useful

Do not leave final source URLs to be synthesized later in `03`.

#### [MODIFY] `.github/scripts/openwrt-docs4ai-03-normalize-semantic.py`

Reframe `03` as a carry-through stage for provenance rather than a provenance synthesis stage.

Minimum behavior changes:

```python
for key in ["source_url", "source_commit", "language", "description"]:
    if meta.get(key):
        y_meta[key] = meta[key]
```

This removes the need for `REPO_BASE_URLS` provenance logic in `03` and avoids duplicating ingest knowledge in a later stage.

### Why not keep `upstream_path` and `version` in L2?

v13 is correcting the semantics of both fields:

- `source_url` is the final dereferenceable upstream address
- `source_commit` is the exact upstream commit SHA when applicable
- `source_locator` is the optional raw locator if the pipeline still needs it operationally

Not renaming keeps misleading historical field names alive in the new contract. Since v13 is already revisiting the metadata model, this is the right time to normalize the contract.

### Downstream propagation

The provenance contract must also be propagated to:

#### [MODIFY] `.github/scripts/openwrt-docs4ai-08-validate-output.py`

Update the L2 required-fields check to require `source_commit` where the contract expects a git-backed document and to reject stale `version`.

```python
required_fields = ["title", "module", "origin_type", "token_count"]

if origin_type in GIT_BACKED_ORIGIN_TYPES:
    required_fields.append("source_commit")
```

The validator should also explicitly reject stale `original_url`, `upstream_path`, and `version` fields in L2 after the migration is complete.

Additionally, add a programmatic dead-link checker for internal relative links within the release-tree. This replaces the previous incorrect assumption that `08` already had one. The checker should:

- scan all `.md` files in the release-tree for relative markdown links
- resolve each link against the release-tree directory structure
- fail the validation if any relative link points to a non-existent file
- emit a clear error message identifying the source file and broken link target

#### [MODIFY] `tests/pytest/pytest_09_release_tree_contract_test.py`

Update mock L2 YAML fixtures to use `source_commit` instead of `version`, and add provenance assertions that match the new ingest-time contract.

### Acceptance test

```
- [ ] L1 sidecars for git-backed modules contain `source_url` and `source_commit`
- [ ] L1 sidecars for wiki files contain `source_url`
- [ ] L2 frontmatter carries through `source_url` unchanged for luci and wiki files
- [ ] L2 frontmatter carries through `source_commit` unchanged for git-backed files
- [ ] L2 frontmatter does NOT contain a field named `version`
- [ ] Stage `08` validator requires `source_commit` for git-backed origins, exempts `origin_type: authored`, and rejects stale `version`
- [ ] Stage `08` validator includes programmatic dead-link checker for internal relative links in the release-tree
- [ ] Contract test fixtures use `source_commit` in mock L2 YAML
- [ ] `03` no longer owns a repo-base URL derivation table for provenance
```

---

## Summary of All File Changes

### New files

| File | Created by | Purpose |
|------|-----------|---------|
| `docs/docs-new/output/release-tree-contract.md` | S6 | Migrated and updated output contract |
| `docs/docs-new/pipeline/regeneration-rules.md` | S6 | Pipeline rerun documentation |
| `docs/docs-new/project/glossary-and-naming-contract.md` | S7 | Terminology definitions |
| `docs/docs-new/roadmap/deferred-features.md` | S6 | C-tier and out-of-scope items |
| `content/cookbook-source/openwrt-era-guide.md` | S2/S3 | Era transition guide |
| `.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py` | S3 | Cookbook ingest script |
| `lib/source_provenance.py` | Metadata | Shared provenance helper for the ingest family |
| `release-inputs/release-include/luci/AGENTS.md` | S4 | LuCI-specific AI orientation |
| `release-inputs/release-include/ucode/AGENTS.md` | S4 | ucode-specific AI orientation |
| `release-inputs/release-include/cookbook/AGENTS.md` | S4 | Cookbook-specific AI orientation |

### Modified files

| File | Modified by | Change |
|------|-----------|--------|
| `.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py` | S1, S3 | Add `MODULE_DESCRIPTIONS`, add cookbook category |
| `.github/scripts/openwrt-docs4ai-05b-generate-agents-and-readme.py` | S4 | Add era warning and per-module AGENTS.md notice to root template |
| `.github/scripts/openwrt-docs4ai-02a-scrape-wiki.py` | Metadata | Stamp final `source_url` during ingest |
| `.github/scripts/openwrt-docs4ai-02b-*.py` through `.github/scripts/openwrt-docs4ai-02h-*.py` | Metadata | Stamp final `source_url` and `source_commit` during ingest |
| `.github/scripts/openwrt-docs4ai-03-normalize-semantic.py` | S3, metadata | Carry through `source_url` and `source_commit` instead of deriving provenance late |
| `.github/scripts/openwrt-docs4ai-08-validate-output.py` | Metadata | Require `source_commit` in L2 where applicable and reject stale `version` |
| `tests/pytest/pytest_09_release_tree_contract_test.py` | Metadata | Update L2 fixtures to `source_commit` and align provenance assertions |
| `release-inputs/release-include/README.md` | README expansion | Expand from 10 lines to ~60 lines |
| `.github/workflows/openwrt-docs4ai-00-pipeline.yml` | S3 | Add `02i` invocation |

### Files NOT changed

| File | Why not |
|------|---------|
| `05a-assemble-references.py` | Fully dynamic module discovery — no changes needed |
| `docs/specs/v12/release-tree-contract.md` | Superseded by docs-new version, left in place for reference |
| `ARCHITECTURE.md` | Add a pointer to docs-new glossary, but content stays in glossary |
| `CLAUDE.md` | Add a pointer to docs-new pipeline docs, but content stays there |

---

## Verification Plan

### Automated

After implementing all changes, run the full CI-equivalent pipeline in order. The sequence below must include source preparation, all ingest stages, normalization, assembly, routing/finalization, and validation so the verification actually covers the new provenance and release-tree contracts:

```bash
# Full pipeline — CI-equivalent proof, including prerequisite source preparation and all ingest families
python .github/scripts/openwrt-docs4ai-01-clone-repos.py
python .github/scripts/openwrt-docs4ai-02a-scrape-wiki.py
python .github/scripts/openwrt-docs4ai-02b-extract-ucode.py
python .github/scripts/openwrt-docs4ai-02c-extract-luci.py
python .github/scripts/openwrt-docs4ai-02d-extract-openwrt-core.py
python .github/scripts/openwrt-docs4ai-02e-extract-uci.py
python .github/scripts/openwrt-docs4ai-02f-extract-procd.py
python .github/scripts/openwrt-docs4ai-02g-extract-openwrt-hotplug.py
python .github/scripts/openwrt-docs4ai-02h-extract-luci-examples.py
python .github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py
python .github/scripts/openwrt-docs4ai-03-normalize-semantic.py
python .github/scripts/openwrt-docs4ai-05a-assemble-references.py
python .github/scripts/openwrt-docs4ai-05b-generate-agents-and-readme.py
python .github/scripts/openwrt-docs4ai-05c-generate-ucode-ide-schemas.py
python .github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py
python .github/scripts/openwrt-docs4ai-07-generate-web-index.py
python .github/scripts/openwrt-docs4ai-08-validate-output.py
```

Stages `07` and `08` are required because:
- `07` applies the `release-inputs/release-include/` overlay, which is how shipped `README.md` and per-module `AGENTS.md` reach the release-tree after the generated outputs are assembled
- the root `AGENTS.md` is still generated by `05b` and then carried forward into the finalized release-tree
- `08` runs gatekeeper validation that catches structural errors

Then verify:
1. `release-tree/llms.txt` has curated descriptions for all modules
2. `release-tree/cookbook/` exists with `map.md`, `bundled-reference.md`, `chunked-reference/openwrt-era-guide.md`
3. `release-tree/luci/AGENTS.md`, `release-tree/ucode/AGENTS.md`, `release-tree/cookbook/AGENTS.md` exist (placed by `07` overlay)
4. Root `release-tree/AGENTS.md` references openwrt-era-guide and per-module AGENTS.md
5. `release-tree/README.md` is the expanded version (placed by `07` overlay from `release-inputs/release-include/README.md`)
6. L1 sidecars use `source_url` and `source_commit` according to the new ingest-time provenance contract
7. L2 frontmatter carries through `source_url` and `source_commit` without late derivation
8. `release-tree/ucode/types/ucode.d.ts` exists (generated by `05c`)
9. The new docs-new pipeline catalog and glossary are self-contained and internally consistent
10. Stage `08` passes all gatekeeper checks

### Manual

- Open the deployed corpus repo and verify the README renders correctly
- Ask an AI tool to "explain how to create a LuCI view" — verify it references the JS form API, not CBI
- Verify that `docs/docs-new/` is self-contained and has no broken cross-links

---
