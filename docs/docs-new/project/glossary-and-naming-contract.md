# Glossary and Naming Contract

**Version:** V13 (S7)  
**Status:** Active

Canonical name definitions for the openwrt-docs4ai pipeline. All scripts, tests, documentation, and generated outputs must use these names. When a term here conflicts with a term elsewhere, this file wins.

---

## Core Architecture Terms

| Term | Definition |
|------|-----------|
| **L0** | Upstream source clones; shallow git clones written to `tmp/repo-{name}/`. Ephemeral, never committed. |
| **L1** | Raw normalized Markdown. The output of the 02* extractor scripts. Lives in `L1-raw/{module}/`. Each file has a `.meta.json` sidecar. |
| **L2** | Semantic Markdown. The output of stage 03 (`normalize-semantic`). Lives in `L2-semantic/{module}/`. Each file has YAML frontmatter. |
| **L3** | Generated per-module output surfaces. Produced by stages 05*, 06, 07. Lives in `release-tree/{module}/`. |
| **L4** | Validated release-tree. The output of stage 08 (`validate-output`). Identical paths to L3; the term "L4" signals that gatekeeper has passed. |
| **L5** | Telemetry and drift reports. Produced by stage 05d. Lives in `support-tree/telemetry/`. |
| **WORKDIR** | The top-level ephemeral working directory for a pipeline run. On CI: `staging/`; locally: `tmp/`. |
| **OUTDIR** | The pipeline's output root (inside WORKDIR). Contains `L1-raw/`, `L2-semantic/`, and `release-tree/`. |
| **Release tree** | The published output subtree rooted at `release-tree/` inside OUTDIR. This is the only path that gets pushed to distribution targets. |
| **Support tree** | `support-tree/` inside OUTDIR. Internal pipeline state; never published. |

---

## Provenance Fields

These are the canonical V6 field names. All stale names (V5a and earlier) are forbidden in new code.

### L1 sidecar (`.meta.json`) fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `extractor` | string | Yes | Script name (e.g. `"02a-scrape-wiki"`) |
| `origin_type` | string | Yes | Canonical content origin type (see types table below) |
| `module` | string | Yes | Module name (e.g. `"wiki"`, `"ucode"`) |
| `slug` | string | Yes | File stem identifying the page within the module |
| `source_url` | string or null | Yes | Full URL to upstream source. Null for hand-authored content (cookbook). |
| `source_locator` | string or null | Conditional | For git-backed sources only: relative file path within the source repository. Null for wiki and cookbook. |
| `source_commit` | string or null | Conditional | For git-backed sources only: commit SHA at extraction time. Null for wiki and cookbook. |
| `language` | string | Yes | BCP 47 language tag (typically `"en"`) |
| `fetch_status` | string | Yes | `"ok"` or error reason string |
| `extraction_timestamp` | string | Yes | ISO 8601 UTC timestamp of extraction |
| `content_hash` | string | Yes | SHA-256 hex digest of the normalized content |

### L2 YAML frontmatter fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Human-readable content title |
| `module` | string | Yes | Module name (same as L1) |
| `origin_type` | string | Yes | Same as L1 origin type |
| `token_count` | integer | Yes | Approximate GPT token count of the content |
| `source_commit` | string | Conditional | Required for all git-backed origin types; omitted for wiki and cookbook |
| `source_url` | string | Optional | Carry-through from L1 sidecar if present |
| `source_locator` | string | Optional | Carry-through from L1 sidecar if present |
| `routing_summary` | string | Optional | AI-generated or hand-authored 1-sentence module purpose summary |
| `routing_keywords` | list[string] | Optional | Keywords for LLM routing |
| `routing_priority` | string | Optional | `"high"`, `"medium"`, or `"low"` |
| `era_status` | string | Optional | `"current"`, `"legacy"`, or `"deprecated"` |
| `audience_hint` | string | Optional | `"developer"`, `"operator"`, `"both"` |

### Stale fields (forbidden)

| Stale name | V6 replacement | When to warn |
|-----------|---------------|-------------|
| `version` | `source_commit` | Stage 08: soft warn if found in L2 frontmatter |
| `upstream_path` | `source_locator` | Stage 08: soft warn if found in L2 frontmatter |
| `original_url` | `source_url` | Stage 08: soft warn if found in L2 frontmatter |

---

## Origin Types

| `origin_type` value | Source | Stage |
|--------------------|--------|-------|
| `"wiki_page"` | OpenWrt wiki HTTP scrape | 02a |
| `"ucode_source"` | Ucode source file in git repo | 02b |
| `"luci_source"` | LuCI source file in git repo | 02c |
| `"luci_example"` | LuCI example file in git repo | 02d |
| `"openwrt_core_doc"` | OpenWrt core documentation file | 02e |
| `"procd_doc"` | Procd documentation file | 02f |
| `"openwrt_hotplug_doc"` | OpenWrt hotplug documentation file | 02g |
| `"uci_doc"` | UCI documentation file | 02h |
| `"authored"` | Hand-authored cookbook entry | 02i |

**Git-backed origin types** (require `source_commit` in L2): all except `"wiki_page"` and `"cookbook_entry"`.

---

## Module Names

The canonical module names used in directory paths, config dicts, and routing indexes:

| Module name | Description | L1 origin |
|------------|-------------|-----------|
| `wiki` | OpenWrt wiki pages | 02a |
| `ucode` | Ucode interpreter API | 02b |
| `luci` | LuCI web interface source | 02c |
| `luci-examples` | LuCI usage examples | 02d |
| `openwrt-core` | OpenWrt core documentation | 02e |
| `procd` | Procd process manager | 02f |
| `openwrt-hotplug` | OpenWrt hotplug system | 02g |
| `uci` | UCI configuration interface | 02h |
| `cookbook` | Task-oriented guides (`origin_type: "authored"`) | 02i |

---

## File Naming Conventions

| Pattern | Rule |
|---------|------|
| L1 content files | `{slug}.md` (lowercase, hyphens) |
| L1 sidecar files | `{slug}.meta.json` (same stem as `.md` counterpart) |
| L2 content files | `{slug}.md` (same stem as L1 counterpart) |
| L3 module root | `{module-name}/` (exactly matches module name in table above) |
| L3 chunk files | `{topic-slug}.md` inside `chunked-reference/` |
| Bundled reference parts | `bundled-reference.part-{NN:02d}.md` (zero-padded) |

---

## Pipeline Naming Conventions

| Term | Definition |
|------|-----------|
| **Stage family** | A group of scripts at the same ordinal level sharing a common purpose (e.g. all 02* scripts are the L1 extractor family) |
| **Extractor** | A 02* script that produces L1 output |
| **Normalizer** | Stage 03; L1 → L2 |
| **Assembler** | Stage 05a; L2 → L3 reference surfaces |
| **Router** | Stage 06; L2 → L3 routing indexes |
| **Finalizer** | Stage 07; applies overlays, materializes support tree |
| **Validator** | Stage 08; gatekeeper; fails build on violations |
| **AI store** | The `data/base/` directory containing cached AI-generated summaries; read by stage 04 |
| **Overlay** | A file in `release-inputs/` that overrides or supplements generated output at finalization time |
| **Sidecar** | A `.meta.json` file paired with each `.md` file in `L1-raw/` |

---

## Versioning Vocabulary

| Term | Definition |
|------|-----------|
| **Pipeline version** | The major revision of the openwrt-docs4ai pipeline (e.g. V12, V13). Increments with breaking contract changes. |
| **Release tree version** | The version label on `release-tree-contract.md` (e.g. V5a, V6). May increment independently of pipeline version. |
| **`source_commit`** | A git commit SHA from an upstream repo, recorded at L1 extraction time and carried to L2. Not the pipeline version. |
| **Provenance** | The complete set of source location fields (`source_url`, `source_locator`, `source_commit`) that trace a generated output back to its upstream origin. |

---

## Test and Development Vocabulary

| Term | Definition |
|------|-----------|
| **Smoke test** | A focused subprocess-based integration test that executes a pipeline stage in isolation against sample inputs |
| **Pytest suite** | The `tests/pytest/` collection; covers contracts, validators, and library function behavior |
| **Fixture** | A static test file in `tests/` that provides synthetic L1 or L2 input for tests |
| **Baseline** | The state of passing tests before any code change (`python tests/run_pytest.py` → all pass) |
| **Working checklist** | `docs/plans/v13/working-checklist.md`; the per-phase checkbox tracker for an implementation session |
