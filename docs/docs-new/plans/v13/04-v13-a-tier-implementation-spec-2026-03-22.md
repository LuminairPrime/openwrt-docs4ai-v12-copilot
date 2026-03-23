# V13 A-Tier Implementation Specification

**Recorded:** 2026-03-22  
**Purpose:** Implementation spec for A-tier pipeline and infrastructure enhancements  
**Predecessor:** [03-v13-cookbook-content-spec-2026-03-22.md](03-v13-cookbook-content-spec-2026-03-22.md)  
**Scope:** Items A1, A2, A5, A6, A7, A8 from [00‑v13](00-v13-ideas-tier-list-2026-03-22.md). A2 is retained here as a recorded deferral decision, not an active implementation target. Cookbook content items A3 and A4 are covered by 03‑v13.

---

## Scope and Dependencies

This spec covers six A-tier items that are all **pipeline code or infrastructure changes**, not content authoring. They share a common dependency chain:

```
S-tier work (02-v13)
  └─ S3 cookbook infra / S2 era guide must exist before...
      ├─ A5 routing metadata (enriches 06)
      ├─ A6 provenance headers (enriches 05a published output)
      ├─ A7 routing quality tests (guards A5/A6)
      ├─ A8 source-intake exclusions (improves 02* inputs)
      ├─ A1 luci-env.d.ts (extends 05c)
      └─ A2 llms-mini.txt (recorded as indefinitely deferred; no v13 implementation)
```

All A-tier items should ship with v13 but are not required for the minimum viable release. Any item not completed is deferred to `docs/docs-new/roadmap/deferred-features.md`.

## Open Investigations Before Implementation

These are explicit pre-implementation gates for the relevant A-tier items.

### A2 recorded verdict: `llms-mini.txt` / `llms-small.txt` deferred indefinitely

The investigation is complete. The result is a do-not-build decision for v13 and beyond unless the public standard and ecosystem change materially.

Recorded popularity snapshot from GitHub filename searches used during this review:

- `llms-mini.txt`: about 42 hits
- `llms-small.txt`: about 498 hits
- `llms-full.txt`: about 37100 hits
- `llms.txt`: about 116000 hits

`llmstxt.org` standardizes `llms.txt`, and the public ecosystem heavily favors `llms.txt` plus `llms-full.txt`. The smaller `llms-mini.txt` and `llms-small.txt` variants do not show enough public adoption to justify adding a repo-local extra routing format.

**Required outcome:** preserve the A2 heading as a decision record, document the indefinite deferral in deferred-features planning, and reject further v13 work on additional `llms-xyz` outputs.

### A1 parsing strategy: LuCI JS API doc structure

Before committing to a generator shape, examine `luci/chunked-reference/js_source-api-*.md` and determine whether the current `05c` parser architecture can be extended without turning into a second unrelated parser jammed into the same script.

The investigation must answer:

- whether LuCI JS docs expose stable headings, signatures, and type-like structure comparable to the ucode sources
- whether the parsing logic shares enough machinery with the current `ucode.d.ts` generator to justify extending `05c`
- whether a dedicated sibling stage is cleaner

**Required outcome:** choose one of two paths explicitly: extend `05c`, or add a new sibling stage in the `05x` family. A dedicated sibling must not reuse `05d`, which is already occupied in the live pipeline.

### A8 exclusion candidates: first policy entries

The initial review is complete. The first policy version should be seeded with path-specific wiki exclusions for the following reviewed pages:

- `guide-developer-luci` because it steers AI tools toward deprecated Lua/CBI LuCI patterns
- `techref-hotplug-legacy` because it is explicitly historical and superseded by procd
- `guide-developer-20-xx-major-changes` because it is narrow release-transition material that disproportionately poisons top-level wiki routing

These are path-specific exclusions, not pattern-based module suppression. `techref-swconfig` is intentionally not part of the first pass because it still provides truthful legacy-hardware guidance.

**Required outcome:** the first version of the policy file should contain these concrete wiki entries rather than a placeholder framework.

## Risk Register

| Risk | Severity | Mitigation |
|------|----------|------------|
| Era guide evidence quality | High | External research packet before finalizing. Do not rely on AI priors alone. |
| `luci-env.d.ts` parsing complexity | Medium | Run the A1 parsing investigation first; if L2 markdown parsing is too brittle, fall back to parsing JS source files directly from the cloned repo. Use a sibling stage if LuCI doc parsing diverges too far from `05c`. |
| Cookbook content drift over time | Medium | Enforce `last_reviewed` plus maintenance policy, while acknowledging this is ultimately a human-discipline problem. |
| Dead-link checker scope | Low | Start with internal relative links only. External URL checking is deferred. |

---

## A5 — Routing Metadata Model

**Goal:** Let curated routing metadata override heuristic summaries in `llms.txt` and module orientation surfaces, fixing routing quality at the source instead of hand-tuning output text.

### Design

Stage `06` currently generates module descriptions by inference. A5 introduces optional authored fields that, when present, override heuristic generation:

**New optional L2 frontmatter fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `routing_summary` | string | One-sentence curated description for `llms.txt` and `map.md` |
| `routing_keywords` | list | Search/navigation keywords |
| `routing_priority` | int (1–10) | Relative importance within the module for routing surface ordering |
| `era_status` | enum: `current`, `transitional`, `legacy` | Temporal relevance signal |
| `audience_hint` | string | Target audience (e.g., `beginner`, `advanced`, `reference`) |

These fields are optional for all L2 documents. When present, downstream stages must prefer them over heuristics.

### Field mapping: `description` vs `routing_summary`

The cookbook content spec (03-v13) defines an authored frontmatter field called `description` — a one-sentence routing summary. The routing metadata model here calls the pipeline-level field `routing_summary`. These are the same concept at different layers.

The mapping rule is:

- **Cookbook content:** authors write `description` in frontmatter. `02i` carries it into the L1 sidecar as `description`. `03` carries it into L2 as `description`.
- **Stage 06/05a:** when building routing surfaces, check for `routing_summary` first, then fall back to `description`. Both serve the same purpose — curated one-sentence summary that overrides heuristic extraction.
- **Non-cookbook content:** if routing metadata is added to L1 sidecars for scraped modules in the future, use `routing_summary` as the field name.

This avoids forcing cookbook authors to learn pipeline-internal terminology while keeping the routing metadata model consistent for all content types.

### Implementation

#### [MODIFY] `.github/scripts/openwrt-docs4ai-03-normalize-semantic.py`

Carry through routing metadata fields from L1 sidecars into L2 frontmatter without modification. If a field is absent in L1, omit it from L2 — do not synthesize defaults.

#### [MODIFY] `.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py`

Three changes:

1. When building per-module `llms.txt` entries, prefer `routing_summary` over heuristic first-line extraction when the field exists; fall back to `description` if `routing_summary` is absent
2. When ordering entries within a module, use `routing_priority` when present (higher = more prominent)
3. The `MODULE_DESCRIPTIONS` dict (from S1) remains the authority for module-level descriptions; `routing_summary` / `description` governs per-document descriptions within a module

#### [MODIFY] `.github/scripts/openwrt-docs4ai-05a-assemble-references.py`

When generating `map.md`, use `routing_summary` (or `description`) if present for the one-liner next to each topic. Fall back to existing heuristic.

### Rule

```
If routing_summary exists → use it
Else if description exists → use it
Else → use existing heuristic
If heuristic produces a low-confidence result → use a conservative fallback ("See topic for details")
```

### Acceptance test

```text
- [ ] L2 frontmatter may carry optional routing_summary, routing_keywords, routing_priority, era_status, audience_hint
- [ ] Stage 06 uses routing_summary (or description) for per-document descriptions when present
- [ ] Stage 05a uses routing_summary (or description) in map.md when present
- [ ] Absent routing metadata does not cause errors — existing heuristic behavior is preserved
- [ ] At least one cookbook source file has description and it appears verbatim in the shipped llms.txt entry
```

---

## A6 — User-Visible Provenance Headers

**Goal:** Make shipped cleaned documents visibly source-verifiable so outsiders can check claims against upstream without knowing the repo internals.

### Design

Every shipped document in the release-tree should carry a short visible provenance block near the top, rendered from the L2 frontmatter metadata. This is not new metadata — it is a presentation layer for the `source_url`, `source_commit`, `origin_type`, and pipeline run metadata already stamped at ingest time.

**Required visible provenance for shipped documents:**

| Field | Source | Example |
|-------|--------|---------|
| Source | `source_url` | `https://github.com/openwrt/luci/blob/.../app.js` |
| Source kind | `origin_type` | `js_source`, `wiki_page`, `authored` |
| Upstream commit | `source_commit` | `abc1234` (if git-backed) |
| Normalized | pipeline run date | `2026-03-22` |
| Method | derived from `origin_type` | `scraped`, `normalized`, `hand-authored` |

### Implementation

#### [MODIFY] `.github/scripts/openwrt-docs4ai-05a-assemble-references.py`

During assembly of `chunked-reference/` and `bundled-reference.md`, inject a short visible provenance header block into the published output immediately after the YAML frontmatter. The provenance block is rendered from L2 frontmatter metadata:

```markdown
> **Source:** [source_url](source_url)  
> **Kind:** origin_type | **Commit:** source_commit  
> **Normalized:** YYYY-MM-DD
```

If `source_url` is absent (e.g., some authored content initially), omit the Source line rather than fabricating a URL. This follows the existing evidence rule: no fabricated URLs.

**Why 05a and not 03:** Stage `03` produces L2 semantic files — pure markdown body plus YAML frontmatter. The provenance block is a presentation concern (a rendered UI element for human readers), not semantic data. Injecting it at `03` would bleed presentation into the data layer. Stage `05a` is the assembly/publishing stage that builds the shipped `chunked-reference/` output — it already transforms L2 into published form, so this is the correct place to add visible rendering of metadata.

The L2 files remain clean data. The provenance block appears only in the published output.

### Guardrails

- Never fabricate a URL. If `source_url` is absent, publish the best truthful fallback (`source_locator` or slug).
- The header must be a standard markdown blockquote so it renders correctly in all viewers.
- The header is generated by `05a` from L2 frontmatter, not hand-authored — it cannot drift from the actual metadata.
- L2 files must NOT contain the visible provenance block. It is a publication-time injection only.

### Acceptance test

```text
- [ ] Every shipped document in release-tree/*/chunked-reference/ has a visible provenance header block
- [ ] L2 files in the work directory do NOT contain the visible provenance block
- [ ] The header renders correctly in standard markdown viewers
- [ ] No fabricated URLs appear in provenance headers
- [ ] The header is auto-generated from L2 frontmatter, not hand-authored
- [ ] Documents with authored origin_type show the appropriate provenance (no source_commit, method: hand-authored)
```

---

## A8 — Configurable Source-Intake Exclusions

**Goal:** Allow maintainers to exclude known-bad or low-value upstream files from the pipeline at download/extract time, preventing misleading content from reaching L1/L2/routing/release-tree.

### Design

A source-intake policy file controls which upstream files are excluded. This is a transparent policy control, not a hidden heuristic.

**Policy file:** `config/source-exclusions.yml` (or `.json`)

```yaml
# Source-intake exclusion policy
# Each entry blocks a specific upstream file from being ingested
exclusions:
  - source: wiki
    match_type: slug
    identifier: "guide-developer-luci"
    reason: "Deprecated Lua/CBI LuCI tutorial that misroutes modern AI generation"
    added: "2026-03-22"
    added_by: "maintainer"

  - source: wiki
    match_type: slug
    identifier: "techref-hotplug-legacy"
    reason: "Historical Hotplug2 page superseded by procd; low-value for current routing corpus"
    added: "2026-03-22"
    added_by: "maintainer"

  - source: wiki
    match_type: slug
    identifier: "guide-developer-20-xx-major-changes"
    reason: "Release-transition page that disproportionately distorts wiki routing summaries"
    added: "2026-03-22"
    added_by: "maintainer"
```

### Implementation

#### [NEW] `config/source-exclusions.yml`

The policy file. Ships in the development repo, not the release-tree.

#### [NEW] `lib/source_exclusions.py`

Shared library that loads the policy file and provides a `should_exclude(source_type, identifier)` function.

#### [MODIFY] `.github/scripts/openwrt-docs4ai-02a-scrape-wiki.py` through `02h`

Each ingest script calls `should_exclude()` before writing L1 output. If excluded, log the skip and reason, but do not write the file.

#### [MODIFY] `.github/scripts/openwrt-docs4ai-08-validate-output.py`

Add a diagnostic check that reports how many files were excluded and why (informational, not a failure gate).

### Guardrails

- By default, scrape broadly. Exclusions are the exception, not the rule.
- Each exclusion must have a `reason` field so the policy is auditable.
- The exclusion policy should be reviewed when the project changes its upstream baseline.
- Exclusions apply only at ingest time — they do not retroactively remove already-processed files from existing release-trees.
- The first implementation should be seeded with concrete current-corpus candidates, not an empty mechanism waiting for hypothetical future use.

### Acceptance test

```text
- [ ] config/source-exclusions.yml exists and is parseable
- [ ] lib/source_exclusions.py loads the policy and exposes should_exclude()
- [ ] At least one exclusion is applied during a pipeline run
- [ ] At least one first-pass exclusion entry is justified by a reviewed current wiki corpus candidate
- [ ] Excluded files do not appear in L1-raw/
- [ ] Exclusion is logged with the reason from the policy file
- [ ] Stage 08 reports exclusion statistics
```

---

## A1 — LuCI Environment Type Definitions (`luci-env.d.ts`)

**Goal:** Extend the proven `ucode.d.ts` pattern to the LuCI JavaScript framework, preventing hallucinated LuCI API calls.

### Design

The existing `ucode.d.ts` generated by stage `05c` is one of the strongest features of the deliverable. A1 replicates this for the LuCI JS client-side framework. The target API surface includes:

- `LuCI.form.Map`, `LuCI.form.TypedSection`, `LuCI.form.Value` — the form binding API
- `LuCI.rpc.declare` — the RPC call mechanism
- `LuCI.uci.load`, `LuCI.uci.get`, `LuCI.uci.set` — the UCI config access API
- `LuCI.view.extend` — the view lifecycle
- `LuCI.dom`, `LuCI.request`, `LuCI.network` — common utility APIs

Estimated size: 300–500 lines of TypeScript declarations.

### Parsing strategy

The A1 investigation gate (see Open Investigations) must resolve the input source before implementation. There are two viable approaches:

1. **Parse L2 markdown** (`luci/chunked-reference/js_source-api-*.md`): Follows the established `05c` pattern but is inherently brittle — generated markdown headings and narrative structure can drift across upstream LuCI releases. If the investigation finds stable, structured headings with consistent function signatures in the L2 docs, this approach is acceptable.

2. **Parse LuCI JS source files directly** from the cloned `luci` repo: More robust because JS source files expose actual function signatures, JSDoc annotations, and class structures that can be parsed with AST-level tools or structured regex. This avoids the markdown-to-TypeScript roundtrip brittleness. The tradeoff is that it requires reading from the cloned repo (`WORKDIR/luci/`) rather than from L2 output, adding a direct dependency on the clone step.

If approach 1 proves fragile during the investigation, fall back to approach 2. If approach 2 is chosen, limit the scope to a predefined set of essential API namespaces rather than attempting to auto-discover the full LuCI API surface.

### Implementation

#### [MODIFY] `.github/scripts/openwrt-docs4ai-05c-generate-ucode-ide-schemas.py`

Extend (or create a sibling function) to parse LuCI JS source docs or JS source files and emit `luci-env.d.ts`.

Alternatively, create a dedicated `05e-generate-luci-dts.py` if the logic is sufficiently different from ucode `.d.ts` generation that combining them would be forced.

**Decision point:** Whether to extend `05c` or create `05e` should be resolved during implementation based on code complexity and the A1 parsing investigation. Both approaches are acceptable. `05d` is already occupied in the live pipeline and must not be repurposed.

#### Output location

`release-tree/luci/types/luci-env.d.ts`

### Acceptance test

```text
- [ ] release-tree/luci/types/luci-env.d.ts exists after full pipeline run
- [ ] The file declares the core form API (Map, TypedSection, Value)
- [ ] The file declares rpc.declare and uci access methods
- [ ] The file is valid TypeScript (passes tsc --noEmit)
- [ ] The file references are consistent with luci/chunked-reference/ API docs
- [ ] The parsing strategy chosen during investigation is documented in the script docstring
```

---

## A2 — `llms-mini.txt` Sub-1000-Token Routing Surface

**Status:** Deferred indefinitely.

The project will not add `llms-mini.txt`, `llms-small.txt`, or any other extra `llms-xyz` routing format in v13. The public evidence gathered for this plan shows heavy ecosystem use of `llms.txt` and `llms-full.txt`, but weak adoption of smaller-name variants, and `llmstxt.org` does not define `llms-mini.txt` or `llms-small.txt` as standard companion outputs.

Recorded popularity snapshot from GitHub filename searches during this decision:

1. `llms-mini.txt`: about 42 hits
2. `llms-small.txt`: about 498 hits
3. `llms-full.txt`: about 37100 hits
4. `llms.txt`: about 116000 hits

For v13 planning, that gap is large enough to reject further development of additional routing filenames. The project standard stays:

1. `llms.txt`
2. `llms-full.txt`

If the ecosystem changes later, the feature can be reconsidered from the deferred-features backlog. Until then, the correct implementation decision is to avoid extra routing noise.

### Acceptance test

```text
- [ ] No `release-tree/llms-mini.txt` or `release-tree/llms-small.txt` is generated in v13
- [ ] v13 routing surfaces remain aligned to `llms.txt` and `llms-full.txt`
- [ ] The deferred-features planning notes record the spec and popularity rationale for indefinite deferral
```

---

## A7 — Routing Quality Tests

**Goal:** Protect A5, A6, A8, and the S-tier routing work from silent regression.

### Design

Test coverage focused on pipeline processing behavior, not upstream content quality. These tests validate that the pipeline does what the contract says, not whether OpenWrt upstream documentation is editorially perfect.

### Good v13 tests

| Test | Validates |
|------|-----------|
| Routing metadata override | `routing_summary` replaces heuristic when present |
| Conservative fallback | Absent routing metadata uses existing heuristic, not empty string |
| Provenance header emission | Published documents (not L2) have visible source header when `source_url` exists |
| No fabricated URLs | Provenance header omits Source line when `source_url` is absent |
| AGENTS.md module metadata | Per-module AGENTS.md respects module naming and era notes |
| Exclusion policy application | Excluded files do not appear in L1-raw |
| Dead-link validation | Relative links in release-tree resolve to existing files |

For v13, dead-link validation scope is intentionally limited to internal relative links inside the shipped release-tree. External URL reachability checks are out of scope for this phase.

### Bad v13 tests (explicitly excluded)

- Tests that fail because an upstream wiki page contains outdated advice
- Tests that fail because scraped content is imperfect but truthfully processed
- Tests that try to make this repo the editorial authority for OpenWrt documentation

### Implementation

#### [MODIFY] `tests/pytest/pytest_09_release_tree_contract_test.py`

Add fixture-based tests for the new routing metadata, provenance header, and exclusion behaviors.

#### [NEW] `tests/pytest/pytest_10_routing_quality_test.py` (if 09 becomes too large)

Alternatively, extend 09. The decision should be based on test file size after adding the new cases.

### Acceptance test

```text
- [ ] At least one test verifies routing_summary override behavior
- [ ] At least one test verifies provenance header is generated from L2 metadata
- [ ] At least one test verifies no fabricated URLs in provenance output
- [ ] At least one test verifies source-exclusion policy is applied
- [ ] At least one test verifies dead-link checker catches a broken relative link
- [ ] No test in the suite fails on truthfully processed upstream content
```

---

## Summary of All File Changes

### New files

| File | Section | Purpose |
|------|---------|---------|
| `config/source-exclusions.yml` | A8 | Source-intake exclusion policy |
| `lib/source_exclusions.py` | A8 | Shared exclusion library |
| `release-tree/luci/types/luci-env.d.ts` | A1 | LuCI JS framework type declarations |

### Modified files

| File | Modified by | Change |
|------|-----------|--------|
| `.github/scripts/openwrt-docs4ai-03-normalize-semantic.py` | A5 | Carry through routing metadata fields into L2 frontmatter |
| `.github/scripts/openwrt-docs4ai-05a-assemble-references.py` | A5, A6 | Prefer `routing_summary` / `description` in `map.md`, inject visible provenance header in published output |
| `.github/scripts/openwrt-docs4ai-05c-generate-ucode-ide-schemas.py` | A1 | Extend for `luci-env.d.ts` generation (or create `05e`) |
| `.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py` | A5 | Prefer `routing_summary` for per-doc descriptions |
| `.github/scripts/openwrt-docs4ai-08-validate-output.py` | A7, A8 | Add exclusion statistics and dead-link checker |
| `.github/scripts/openwrt-docs4ai-02a-scrape-wiki.py` through `02h` | A8 | Call `should_exclude()` before writing L1 |
| `tests/pytest/pytest_09_release_tree_contract_test.py` | A7 | Add routing metadata, provenance, and exclusion tests |

---

## Verification Plan

### Automated

After implementing all A-tier changes alongside the S-tier changes from 02-v13, run the full CI-equivalent pipeline:

```bash
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
pytest tests/pytest/
```

Then verify:

1. `release-tree/luci/types/luci-env.d.ts` exists and is valid TypeScript
2. No unsupported extra `llms-xyz` routing file was added beyond `llms.txt` and `llms-full.txt`
3. At least one shipped L2 document has `routing_summary` appearing verbatim in its `llms.txt` entry
4. Every shipped published document has a visible provenance header block (L2 files do NOT)
5. The source-exclusion policy blocked at least one file from L1
6. No internal relative links in the release-tree point to non-existent files
7. All new tests pass
8. Stage `08` passes all gatekeeper checks including dead-link validation

### Manual

- Open a shipped L2 document and verify the provenance header renders correctly and the source URL is dereferenceable
- Verify `luci-env.d.ts` provides correct autocomplete for LuCI form API in a TypeScript-aware editor

---

## Implementation Notes

### Recommended implementation order

| Priority | Item | Effort | Dependencies |
|----------|------|--------|-------------|
| 1 | A5 routing metadata | Medium | S-tier complete |
| 2 | A6 provenance headers | Medium | A5 (uses same metadata path) |
| 3 | A7 routing quality tests | Low-medium | A5, A6 (tests what they build) |
| 4 | A8 source-intake exclusions | Medium | Independent of A5/A6 but benefits from A7 test coverage |
| 5 | A1 luci-env.d.ts | 1–2 days | Independent — can be parallelized with A5/A6 |
| 6 | A2 deferral record | 15 minutes | Preserve the decision and keep extra `llms-xyz` formats out of the implementation backlog |

### Risk notes

- **A1 (luci-env.d.ts)** has the highest implementation risk because LuCI JS API docs are less structured than ucode C source docs. The 05c generator may need a different parsing strategy.
- **A2 (`llms-mini.txt`)** is closed as an indefinite deferral. The ecosystem evidence supports `llms.txt` and `llms-full.txt`, not extra `llms-xyz` variants. Do not reopen this without materially stronger public adoption and spec support.
- **A8 (source-intake exclusions)** has a scope risk — the exclusion policy must be narrow and transparent. Over-exclusion silently reduces corpus coverage. Under-exclusion defeats the purpose.

---
