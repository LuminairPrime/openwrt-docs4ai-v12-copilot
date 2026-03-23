# V13 Baseline Verification Audit

**Recorded:** 2026-03-22  
**Purpose:** Verify the 00-v13 tier list's claims against actual codebase and outputs before writing implementation specs  
**Status:** Complete — all checks resolved  
**Predecessor:** [00-v13-ideas-tier-list-2026-03-22.md](00-v13-ideas-tier-list-2026-03-22.md)  
**Next:** [02-v13-implementation-spec-s-tier-2026-03-22.md](02-v13-implementation-spec-s-tier-2026-03-22.md)

---

## Why This Audit Exists

The 00-v13 tier list makes specific claims about the current codebase, pipeline behavior, output structure, and feature gaps. If any of those claims are wrong, writing detailed implementation specs on top of them would magnify the error. This document systematically checks every implementable claim before proceeding.

In project management terms, this is a **baseline verification gate** — the equivalent of a code review on the requirements document, performed against the actual system rather than just the prose.

---

## Findings Summary

| Item | 00-v13 Claim | Status | Notes |
|------|-------------|--------|-------|
| Release-tree structure | 8 modules, root routing files, one `.d.ts` | ✅ Confirmed | Exact match to V5a contract |
| S1: `llms.txt` descriptions misleading | luci says "CBI declarative form" | ✅ Confirmed | Root cause: alphabetical first-file wins in `06` |
| S2: No era content anywhere | Zero era framing in deliverable | ✅ Confirmed | "deprecated" only in upstream passthrough |
| S3: `02i` for cookbook ingest is available | `02h` is highest ingest script | ✅ Confirmed | `02i` letter is free |
| S3: Pipeline auto-discovers modules | Claims minimal pipeline change | ✅ Confirmed | `03`, `05a`, `06` all use dynamic L1/L2 discovery |
| S4: No per-module `AGENTS.md` | Not present in release-tree | ✅ Confirmed | |
| S5: No routing contract exists | Ownership rules are implicit | ✅ Confirmed | `ARCHITECTURE.md` has partial coverage only |
| S6: Doc sprawl | Claims overlapping generations | ✅ Confirmed | 23 plan files in v12 alone |
| S6: `docs/docs-new/` doesn't exist | Claims it's a new tree | ✅ Confirmed | Directory does not exist |
| S7: No glossary exists | Terms not locked down | ⚠️ Partially | `ARCHITECTURE.md` covers layers but not routing/cookbook terms |
| A5: No routing metadata fields | Claims heuristic-only descriptions | ✅ Confirmed | See §2 root cause analysis |
| A6: No visible provenance | Internal metadata only | ✅ Confirmed | L2 has `upstream_path` (repo-relative), no user-visible header |
| Stage `03` module handling | Not originally audited | ✅ Now confirmed | Fully dynamic via `os.walk(L1_DIR)` — one hardcoded commit map |
| Stage `05a` module handling | Not originally audited | ✅ Now confirmed | Fully dynamic via `os.listdir(L2_DIR)` |
| Stage `05b` AGENTS.md generation | Not originally audited | ✅ Now confirmed | Root-only; per-module extension is additive |

**Overall: No incorrect claims found in 00-v13. All structural and pipeline claims verified.**

---

## 1. Release-Tree Output Structure ✅

Actual release-tree at `openwrt-condensed-docs/release-tree/`:

- **Root files (5):** `AGENTS.md`, `README.md`, `index.html`, `llms-full.txt`, `llms.txt`
- **Modules (8):** luci, luci-examples, openwrt-core, openwrt-hotplug, procd, uci, ucode, wiki
- **Type surface:** `ucode/types/ucode.d.ts` (only `.d.ts` in the tree)
- **Sharded modules:** luci-examples (2 parts), wiki (3 parts)

Matches V5a release-tree-contract exactly. No correction needed.

---

## 2. S1 Root Cause: How `llms.txt` Descriptions Are Generated ✅

**This is the most important finding in this audit.**

In `06-generate-llm-routing-indexes.py`, line 433:

```python
module_description = next(
    (entry["description"] for entry in l2_entries if entry["description"] != DESCRIPTION_FALLBACK),
    DESCRIPTION_FALLBACK,
)
```

**The module description is the `ai_summary` from the first L2 file (alphabetically) that has one.** For `luci`, that's `js_source-api-cbi.md` — the CBI compatibility layer — not the primary framework.

**Fix:** Add a `MODULE_DESCRIPTIONS` override dict in `06` with curated per-module descriptions. Later, the A5 routing metadata model can supersede this with frontmatter-driven descriptions.

---

## 3. S2: Zero Era Content ✅

No project-authored era guidance exists. The root `AGENTS.md` has zero era warnings. "Deprecated" appears only in upstream content passthrough. S2 is greenfield work with no conflicts.

---

## 4. S3 Pipeline Auto-Discovery ✅

All three key pipeline scripts use fully dynamic module discovery:

| Script | Discovery method | Line | Hardcoded module refs |
|--------|-----------------|------|----------------------|
| `03-normalize-semantic.py` | `os.walk(L1_DIR)` | 712 | `resolve_pipeline_commits()` line 694: module→commit SHA mapping |
| `05a-assemble-references.py` | `os.listdir(L2_DIR)` | 478 | None |
| `06-generate-llm-routing-indexes.py` | `os.listdir(L2_DIR)` | 326 | `MODULE_CATEGORIES` dict line 42, `CATEGORY_ORDER` line 52 |

**Total hardcoded changes needed for a new `cookbook` module:**

| Script | Change |
|--------|--------|
| `03` | Add `"cookbook": "N/A"` to `resolve_pipeline_commits()` — cookbook content has no upstream commit SHA |
| `06` | Add `"cookbook": "Guides"` to `MODULE_CATEGORIES` and `"Guides"` to `CATEGORY_ORDER` |

Everything else auto-propagates.

### Why `02i-ingest-cookbook.py` and not something else

The v13 direction is to use `02i-ingest-cookbook.py` for cookbook content. The `02*` scripts are all **ingest/collector scripts that read source material and write to `L1-raw/`**. The existing `02a` through `02h` pull external sources (wiki, git repos). `02i-ingest-cookbook.py` would copy from a project-internal `content/cookbook-source/` directory to `L1-raw/cookbook/`, generating `.meta.json` sidecars.

**This is correct placement in the pipeline even though cookbook content is not scraped from an external source,** because:

1. The `02*` stage contract is "produce L1-raw modules" — not "scrape external sites." The distinction is between what produces L1 input and what processes it. Stage `03` processes; stage `02*` produces.
2. A `02i` ingest script can run in the same parallel group as the other ingest scripts on CI without any workflow changes.
3. The alternative — putting cookbook handling directly in `03` — would break `03`'s single responsibility (normalize, not source).
4. The `.meta.json` sidecar contract is the same regardless of whether content was scraped or hand-authored. The `origin_type` field would be `cookbook` or `manual` instead of `wiki` or `js_source`.

`02i-write-cookbook.py` is a plausible alternate name, but `ingest` is preferred because the stage is staging existing authored content into the pipeline contract, not authoring that content.

### Stage family taxonomy to carry forward into docs-new

The audit supports a more explicit stage-family vocabulary for the rebuilt docs:

- **source preparation**: acquires upstream repositories and other prerequisite inputs without writing L1 content (`01`)
- **collector / ingest**: reads source material and writes L1 sidecars + markdown (`02a`-`02i`)
- **normalizer**: transforms L1 into L2 semantic outputs (`03`)
- **AI enricher**: adds optional AI-derived metadata (`04`)
- **assembler**: packages normalized content into publishable reference forms (`05a`)
- **publication companion generator**: writes non-reference companion artifacts such as root AI guidance and IDE surfaces (`05b`, `05c`, `05d`)
- **router**: writes AI routing indexes (`06`)
- **finalizer**: applies overlays/overrides and materializes the shipped release-tree (`07`)
- **validator / gatekeeper**: enforces publishability checks (`08`)

The v13 docs-new set should define every script in order using this stage-family vocabulary so that future additions can be placed by contract rather than by intuition.

---

## 5. S4: Per-Module AGENTS.md — Justification vs `llms.txt` ✅

No per-module `AGENTS.md` files exist. Root `AGENTS.md` is 28 lines of generic routing instructions.

**Why `AGENTS.md` files are not redundant with `llms.txt`:**

`llms.txt` and `AGENTS.md` serve different functions and are consumed differently by AI tools:

| Aspect | `llms.txt` | `AGENTS.md` |
|--------|-----------|-------------|
| **Purpose** | URL routing index — "here are the files" | Behavioral orientation — "here is how to think about this module" |
| **Content** | File list with token counts and one-line descriptions | Scope warnings, era concerns, anti-pattern alerts, "start here" guidance |
| **Format** | Flat list of `- [file](url): description (tokens)` entries | Prose sections with imperative instructions |
| **AI tool discovery** | Copilot/Cursor read it for file routing | Copilot, Claude Code, and Codex auto-discover `AGENTS.md` as agent persona/instruction files |
| **What it cannot say** | Cannot warn "do NOT use Lua CBI patterns" — it's a routing index, not an instruction file | Does not list every file with token counts |

A per-module `AGENTS.md` for `luci/` would say: *"This module covers the modern JavaScript LuCI framework. Do NOT generate Lua CBI patterns. Start with `map.md`. The key API reference is `js_source-api-form.md`."* That information has no natural home in `llms.txt`, which is a file catalog.

As many `AGENTS.md` files should be created as have genuinely distinct orientation content. The priority modules are `luci` (era confusion), `ucode` (language confusion — not JavaScript), and `cookbook` (task-oriented vs reference usage). Other modules may benefit from `AGENTS.md` files but with less urgency.

The exact authorship and maintenance workflow for per-module `AGENTS.md` files is still undecided. During v13 planning, those files should be treated as **notional deliverables whose governance must be documented before v13 closes**: who authors them, whether AI assistance is allowed, how human review works, and why each file exists.

---

## 6. S5/S6/S7: Documentation State ✅

- `docs/docs-new/` does not exist
- No dedicated routing contract document exists
- No explicit regeneration trigger matrix exists
- `ARCHITECTURE.md` defines layers and naming but is not a glossary
- 23 files in `docs/plans/v12/`, 13 files in `docs/specs/v12/`

### docs/docs-new/ migration plan

`docs/docs-new/` will be created during v13 to hold a clean rebuilt version of the project documentation. During v13 development, `docs/docs-new/` is the **authoritative target documentation set**: new files should point to docs-new truth, not to legacy docs that may later be retired. After v13 development is complete, the old `docs/` folder will be renamed to `docs-old/` and `docs/docs-new/` will become the new `docs/`.

This also means the numbered v13 plan files stay living and valid while v13 is in flight. `00-v13` through the final `xx-v13` files may still be consulted during implementation, so if a later plan changes an earlier assumption, the earlier plan should be corrected rather than left stale.

---

## 7. A5/A6: Metadata and Provenance Baseline ✅

Sample L2 frontmatter (`luci/js_source-api-cbi.md`, current v12 output):

```yaml
title: 'LuCI API: cbi'
module: luci
origin_type: js_source
token_count: 3075
version: 18e0538
source_file: L1-raw/luci/js_source-api-cbi.md
last_pipeline_run: '2026-03-20T04:40:03.869041+00:00'
upstream_path: modules/luci-base/htdocs/luci-static/resources/cbi.js
language: javascript
ai_summary: ...
```

### L1 provenance field audit

The L1 `.meta.json` sidecars currently have an inconsistency in provenance field naming:

| Extractor | `original_url` value | `upstream_path` value |
|-----------|---------------------|----------------------|
| `02a` (wiki) | `https://openwrt.org/...` (full URL) | ❌ absent |
| `02b-h` (git-backed) | `None` | repo-relative path |

`02b-h` all write both fields — `original_url: None` plus `upstream_path: <path>`. Only `02a` is the outlier: it writes `original_url: <url>` but no `upstream_path`.

### Hardened architecture decision: ingest-time provenance stamping, not late reconstruction

**Architecture A (late reconstruction in 03):** Keep provenance incomplete in L1, then reconstruct dereferenceable URLs and commit identifiers later during normalization. Risk: duplicated repository knowledge, extra mapping logic in `03`, and silent provenance drift if a source extractor changes before the normalizer is updated.

**Architecture B (preferred):** Stamp the final dereferenceable provenance as early as possible during ingest. Each `02*` script should write the best available provenance into the sidecar at collection time:

- `source_url`: the dereferenceable upstream URL for the file/page that was ingested
- `source_commit`: the exact upstream commit SHA for git-backed sources when available
- `upstream_path`: optional raw upstream locator if it is still useful operationally

Then `03` carries these fields through into L2 rather than inventing provenance late.

**Decision: Architecture B.** Provenance should be captured at the boundary where the pipeline actually knows the source, not reconstructed later from partial hints.

### L2 field contract (v13)

Two L2 frontmatter fields should be normalized around this ingest-time provenance model:

| L2 field (v12) | L2 field (v13) | Reason |
|----------------|----------------|--------|
| `version` | `source_commit` | Contains a commit SHA, not a semantic version |
| derived or ambiguous source locator | `source_url` | Should be the final dereferenceable upstream URL |

Sample L2 frontmatter after v13:

```yaml
title: 'LuCI API: cbi'
module: luci
origin_type: js_source
token_count: 3075
source_commit: 18e0538
source_file: L1-raw/luci/js_source-api-cbi.md
last_pipeline_run: '2026-03-20T04:40:03.869041+00:00'
source_url: https://github.com/openwrt/luci/blob/18e0538/modules/luci-base/htdocs/luci-static/resources/cbi.js
language: javascript
ai_summary: ...
```

This changes the responsibility split:

- `02*` ingest scripts own provenance discovery and stamping
- `03` owns normalization and carry-through
- `08` validates that provenance fields are present where the contract requires them

This avoids metadata bloat while still making provenance explicit. One L2 provenance URL field (`source_url`) serves both the internal traceability need and the user-visible provenance need.

### Era evidence requirements for v13

The era guide must not be treated as something that can be inferred from model priors alone. The audit supports a two-part evidence requirement:

1. **Local corpus evidence** from the generated OpenWrt/LuCI/ucode documentation already ingested by the pipeline
2. **External human research packet** gathered by the maintainer from real-world discussion sources such as the OpenWrt forum, Reddit, and GitHub issues/discussions/comments

Suggested search terms for the maintainer to gather and synthesize:

- `site:forum.openwrt.org LuCI JavaScript CBI deprecated form.Map`
- `site:forum.openwrt.org swconfig DSA legacy current recommendation`
- `site:reddit.com/r/openwrt LuCI JavaScript CBI`
- `site:reddit.com/r/openwrt swconfig DSA`
- `site:github.com/openwrt/luci/issues CBI JavaScript form.Map`
- `site:github.com/openwrt/openwrt/issues swconfig DSA`
- `site:github.com/openwrt/luci/discussions JavaScript views ucode rpcd`

The v13 plan should require that this external research packet be reviewed and distilled by a human before `openwrt-era-guide.md` is treated as settled project guidance.

---

## 8. Product README vs Output Contract Architecture

### Three distinct roles, three separate documents

| Document | Purpose | Location | Shipped? |
|----------|---------|----------|----------|
| **Product README** | Consumer-facing: what this is, who it's for, how to use it | `release-inputs/release-include/README.md` → ships as `release-tree/README.md` | ✅ Yes |
| **Output contract** | Maintainer-facing: exact file schema, invariants, gatekeeper rules | `docs/docs-new/output/release-tree-contract.md` → eventually `docs/output/release-tree-contract.md` | ❌ No |
| **AGENTS.md** | AI tool orientation: navigation rules, module discovery, constraints | Generated by `05b` → ships as `release-tree/AGENTS.md` | ✅ Yes |

### What the product README should contain

The current shipped README is 10 lines. It should grow to ~60–80 lines:

1. What this is (2 sentences)
2. Who it's for (AI tools + OpenWrt developers using AI tools)
3. Quick start: how to point your AI tool at this folder
4. What's inside: module list with accurate 1-line descriptions
5. File layout explanation: `llms.txt` → `module/llms.txt` → `map.md` → `chunked-reference/`
6. Era warning: "OpenWrt modernized in 2019–2020. See `cookbook/chunked-reference/openwrt-era-guide.md`"
7. How it was generated: brief provenance statement + link to source pipeline repo
8. License / attribution

The README is the label on the box. It should not contain internal pipeline terminology, validation rules, layer model references, or schema definitions.

### What the output contract should contain

The output contract (currently `docs/specs/v12/release-tree-contract.md`, migrating to `docs/docs-new/output/release-tree-contract.md`) is the maintainer-facing engineering definition:

- Exact file schema with required/optional markers
- Gatekeeper validation rules (the 6 checks in stage `08`)
- Sharding contract
- Guaranteed-absent items
- Delivery surface matrix (Pages, corpus repo, ZIP)
- Module schema invariants
- Naming rules for generated files
- Routing ownership matrix (who generates what)
- Regeneration trigger matrix (what changes require what reruns)

### Corpus repo README

The corpus release repo (`openwrt-docs4ai/corpus`) currently shows the generic `release-include/README.md`. The `release-repo-include/` overlay can carry a repo-specific wrapper that adds "This repo is auto-updated by CI" + link back to the pipeline dev repo. The core product README stays the same across all surfaces.

### Repo rename consideration

The user asks whether `openwrt-docs4ai/corpus` should be renamed to `openwrt-docs4ai/release-tree`. The term "release-tree" is used consistently throughout the project's internal documentation. However, consider:

- "corpus" is a public name that conveys "collection of documents" to outsiders
- "release-tree" is an internal project term that conveys the output contract structure
- GitHub repo renames create redirects, so existing links would still work

Either name works. "release-tree" is more consistent with internal terminology; "corpus" is more self-explanatory to newcomers. This is a preference call.

---

## Recommended Filing Sequence for V13 Plans

| File | Purpose | Blocked on |
|------|---------|------------|
| `00-v13-ideas-tier-list` | ✅ Done. Strategic tier list and implementation frameworks | — |
| `01-v13-baseline-verification-audit` | ✅ This file. Verified claims against codebase | 00-v13 |
| `02-v13-implementation-spec-s-tier` | Concrete S1–S7 specs: exact file paths, code changes, acceptance tests | 01-v13 |
| `03-v13-cookbook-content-spec` | Cookbook authoring governance: prompts, verification rules, content contract | 02-v13 |
| `04-v13-implementation-spec-a-tier` | Concrete A1–A8 specs | 02-v13 |
| `05-v13-test-plan` | Consolidated test matrix across all implementations | 02-v13 + 04-v13 |

### What does NOT need a numbered plan file

These are **deliverables** of the implementation, not planning docs:

- Routing ownership records → section within `docs/docs-new/output/release-tree-contract.md` (not a separate file — routing ownership defines what the release-tree must contain, so it belongs in the same contract)
- Regeneration rules → `docs/docs-new/pipeline/regeneration-rules.md` (then `docs/pipeline/regeneration-rules.md`)
- Ordered pipeline catalog → `docs/docs-new/pipeline/pipeline-stage-catalog.md` (then `docs/pipeline/pipeline-stage-catalog.md`)
- Glossary → `docs/docs-new/project/glossary-and-naming-contract.md` (then `docs/project/glossary-and-naming-contract.md`)
- Deferred features → `docs/docs-new/roadmap/v13/deferred-features.md` (then `docs/roadmap/v13/deferred-features.md`)

---
