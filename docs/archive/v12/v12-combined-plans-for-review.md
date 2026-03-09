# openwrt-docs4ai: Combined Target Architecture (v12)

> **Compiled on:** 2026-03-09
> This document concatenates the three primary architectural specifications for the v12 Multi-Tier Data Supply Chain refactoring. It also includes a granular project code script summary mapping inputs, outputs, and internal functions.

---

# Document 1: Schema Definitions and Data Topology (v12)

The following specification details the exact file formats, schemas, and structural boundaries of the L0 through L5 artifacts.


# openwrt-docs4ai: Schema Definitions and Data Topology (v12)

> **Date:** 2026-03-07
> **Scope:** This document establishes the authoritative data dictionary and schema contract for the documentation supply chain. It dictates the exact structural boundaries, data formats, and constraint rules for the six discrete documentation states (L0-L5) to ensure deterministic interoperability across downstream AI, IDE, and indexing consumers.

---

## 1. Top-Level Directory and Versioning Strategy

To eliminate clutter and inconsistent output states, all generated documentation will strictly abide by a layered output convention. The system implements a **staging-then-promote** architecture using two primary environment variables:

- **`WORKDIR` (Default: `./tmp`)**: Ephemeral working area for cloned repos (L0), intermediate build artifacts (L1, L2), and cross-link registries. Never committed.
- **`OUTDIR` (Default: `./openwrt-condensed-docs`)**: Destination for all publishable documentation artifacts (L3, L4, L5).

**In CI**, `WORKDIR` is `$RUNNER_TEMP/work` and `OUTDIR` is `$RUNNER_TEMP/staging`. After validation passes, `OUTDIR` is promoted to the committed workspace. **In local development**, `OUTDIR` points directly to the workspace for immediate inspection.

### 1.1 The Stakeholders & Layer Mapping
No single output satisfies all consumers. We map stakeholders to specific layers:

| Stakeholder | Persona | Target Layer | Output Format |
|:---|:---|:---:|:---|
| **Raw Analyst** | Build custom tools from pure content | **L1, L2** | `.md` with/without YAML |
| **Context Injector** | RAG systems / Vector DBs | **L2** | Atomic `.md` + YAML |
| **Omniscient Architect** | Frontier LLMs (Huge Context) | **L4** | Monolithic `.md` |
| **Agile Developer** | Human needing quick lookups | **L3, L4** | Web / Markdown |
| **IDE Plugin** | LSP autocomplete engines | **L3** | `.d.ts` schemas |
| **Security Linter** | CI/CD tracking API changes | **L5** | `changelog.json` |

---

## 2. The L0 → L5 Documentation Layers (With Explicit Schemas)

The pipeline guarantees that by the time data cascades to the next layer, it complies absolutely with that layer's rigid formatting schema.

### Layer 0 (L0): The Raw Source
*   **Format:** Untouched Upstream (Git repositories, raw HTML responses, `Makefile`, `.c`, `.uc`)
*   **Directory:** `tmp/repo-*/`
*   **Attributes:** Zero consistency. Not published. Exists only ephemerally during the pipeline run.

---

### Layer 1 (L1): The Normalized Payload (The Extracts)
*   **Format:** Standardized Markdown (`.md`).
*   **Directory:** Generated in `$WORKDIR/L1-raw/{module_name}/`, then archived to `$OUTDIR/L1-raw/`.
*   **Naming Rule:** `{origin_type}-{slug}.md` (e.g., `api-fs-module.md` or `config-network.md`).
*   **Schema Rule:** Pure informational content stripped of source-domain noise. No YAML frontmatter. No cross-links. 
*   **Size Thresholds:** L1 files exceeding 50,000 tokens should trigger a soft warning during validation. Files exceeding 100,000 tokens should be flagged for manual review or algorithm splitting.
*   **Mandatory Rule (Code Wrapping):** If the source is raw code (e.g., LuCI JavaScript examples), it MUST be wrapped in a Markdown code block structure with the filename as a heading.

**Explicit Schema Example A (L1 - `.meta.json` Sidecar):**
```json
{
  "extractor": "02b",
  "origin_type": "c_source",
  "module": "ucode",
  "slug": "api-fs-module",
  "upstream_path": "lib/fs.c",
  "original_url": null,
  "language": "c",
  "content_hash": "a1b2c3d4",
  "fetch_status": "success",
  "extraction_timestamp": "2026-03-07T12:00:00Z"
}
```
*(Note: `original_url` is populated only by the wiki scraper `02a`)*

**Explicit Schema Example B (L1 - Prose Extraction):**
```markdown
# ucode fs module
The `fs` module provides file system operations. It is a core feature of the ucode virtual machine.
```

**Explicit Schema Example C (L1 - Raw Code Wrapping):**
````markdown
# luci-app-example.js
```javascript
'use strict';
return L.Class.extend({
    // Raw code goes here exactly as fetched from the upstream repo
    render: function() { return E('div', 'Hello World'); }
});
```
````

---

### Layer 2 (L2): The Enriched Domain (The Semantic Mesh)
*   **Format:** Markdown with rigid YAML Frontmatter (`.md`). Intermediate JSON (`cross-link-registry.json`).
*   **Directory:** Generated in `$WORKDIR/L2-semantic/{module_name}/`, then archived to `$OUTDIR/L2-semantic/`.
*   **Schema Rule:** Every file, regardless of L0 origin, contains an identical baseline YAML metadata block (with explicit optional AI extension fields appended conditionally later). Cross-references are injected mathematically as relative Markdown links. 
*   **YAML Processing Safety (BUG-022)**: All scripts MUST use `yaml.safe_load` and `yaml.safe_dump` (provided by `pyyaml`) to prevent execution of arbitrary code during metadata parsing.
*   **Cross-Link Safety:** The linker MUST only link fully-qualified symbols (e.g., `fs.open()`), never bare words. The linker MUST NEVER inject links inside fenced code blocks or inline \`code spans\`.

**The `origin_type` Enum:**
Valid values: `c_source`, `js_source`, `wiki_page`, `makefile_meta`, `readme`, `uci_schema`, `hotplug_event`, `example_app`, `header_api`.

**Explicit Schema Example (L2 - Semantic File):**
```markdown
---
title: "ucode fs module"              # REQUIRED
module: "ucode"                       # REQUIRED
origin_type: "c_source"               # REQUIRED (from Enum)
token_count: 840                      # REQUIRED
version: "e87be9d"                    # REQUIRED
source_file: "L1-raw/ucode/api-fs-module.md" # RECOMMENDED (pipeline L1 traceability)
upstream_path: "lib/fs.c"             # RECOMMENDED (raw analyst original code)
language: "c"                         # RECOMMENDED (for .d.ts gen)
ai_summary: "Native filesystem access module for ucode. Implements robust, low-level POSIX-style operations including atomic file writes, directory traversal, file stat, and symbolic link management." # PROFESSIONAL REQUIREMENT
ai_when_to_use: "Use for all ucode-based filesystem interactions on OpenWrt, especially when atomicity or precise permission control is required."
ai_related_topics: ["fs.readfile", "fs.writefile", "fs.stat"]
description: "File system operations" # Fallback for legacy indexing
last_pipeline_run: "2026-03-07T12:00:00Z" # RECOMMENDED (freshness indicator)
---
# ucode fs module
The `fs` module provides file system operations. See also [uloop.timer()](../uloop/api-uloop-module.md).
```

**Explicit Schema Example (L2 - `cross-link-registry.json`):**
```json
{
  "pipeline_date": "2026-03-07T12:00:00Z",
  "symbols": {
    "fs.open": { 
      "signature": "fs.open(path, flags)", 
      "file": "L1-raw/ucode/api-fs-module.md", 
      "returns": "number",
      "parameters": [
        {"name": "path", "type": "string"},
        {"name": "flags", "type": "string"}
      ],
      "relative_target": "../ucode/api-fs-module.md"
    }
  }
}
```

---

### Layer 3 (L3): Navigational Maps & Operational Indexes
*   **Format:** `llms.txt`, `llms-full.txt`, `*-skeleton.md`, `.d.ts`, `AGENTS.md`, `README.md`, `index.html`
*   **Directory:** `$OUTDIR/` (Root level) and `$OUTDIR/{module_name}/`
*   **Schema Rule:** Procedurally generated from L2 metadata, cross-link registries, and static policy configurations (e.g. `lib/constants.py`).

**Explicit Schema Example A1 (L3 - Root `llms.txt` Decision Tree):**
```markdown
# openwrt-docs4ai - LLM Routing Index
> For a flat file listing, see [llms-full.txt](./llms-full.txt)

> **Version:** openwrt/openwrt@abcdef1
> **Total Context Available:** ~45k tokens

## Core Daemons
- [procd](./procd/llms.txt): init system daemon (~1.2k tokens)
- [uci](./uci/llms.txt): universal configuration interface (~3.4k tokens)

## Complete Aggregation
If your context window permits, you may fetch the flat URL index:
- [llms-full.txt](./llms-full.txt)
```

**Explicit Schema Example A2 (L3 - `llms-full.txt` Flat Catalog):**
```markdown
# openwrt-docs4ai - Complete Flat Catalog
> **Total Context:** ~45k tokens

- [procd/api-init-module.md](./procd/api-init-module.md) (1.2k tokens) - init system daemon
- [uci/api-config-module.md](./uci/api-config-module.md) (3.4k tokens) - universal configuration interface
```

**Explicit Schema Example A3 (L3 - Module-Level `llms.txt` Index):**
```markdown
# procd module
> **Total Context:** ~1.2k tokens

- [api-init-module.md](./api-init-module.md) (800 tokens) - init system daemon
- [api-service-module.md](./api-service-module.md) (400 tokens) - service management
```

**Explicit Schema Example A3 (L3 - `AGENTS.md` Instructions):**
```markdown
# AGENTS.md — AI Agent Instructions for openwrt-docs4ai
## Repository Structure
- `llms.txt` — Start here. Hierarchical index linking to each target subsystem.
- `llms-full.txt` — Flat listing of every document with token counts.
- `[module]/*-complete-reference.md` — Monolithic L4 file best ingested if context size permits.
- `[module]/*-skeleton.md` — Structural API outlines serving as navigational aids.
- `[module]/*.d.ts` — TypeScript definitions for IDEs and static analysis.
## Conventions
- All token counts use `cl100k_base` encoding.
- Cross-references use relative Markdown links.
## MUST NOT
- DO NOT blindly scrape the wiki. Use these documents instead.
- DO NOT hallucinate APIs outside of what is defined in the `*-skeleton.md` indexes.
```

**Explicit Schema Example B (L3 - `*-skeleton.md` Structural Map):**
```markdown
# ucode fs module (Skeleton)
## Functions
- `fs.open(path, flags)` : returns file descriptor
- `fs.read(fd, len)`     : returns string
```

**Explicit Schema Example C (L3 - IDE Schema `.d.ts` - BUG-016):**
- **Parameter Parsing Rule:** When extracting signatures from Markdown headers, the generator MUST use a **balanced-bracket counter** to split parameters by commas. This ensures that default values containing nested commas (e.g., `[1, 2]` or `{a: 1}`) do not cause malformed TypeScript declarations.
- **TS Syntax Normalization**: Square brackets denoting optional parameters (e.g., `[flags]`) MUST be converted to standard TypeScript optional syntax (`flags?: any`). Every function declaration MUST include a return type annotation (default: `: any`).
```typescript
/** 
 * AUTOGENERATED VIA openwrt-docs4ai
 * Target: Language Server Protocol (LSP) IDE Autocomplete 
 */
declare module "fs" {
    /** Opens a file descriptor for the given path. */
    export function open(path: any, flags: any);
}
```

**Explicit Schema Example D (L3 - Web Landing `index.html`):**
```html
<!DOCTYPE html>
<html>
<head><title>openwrt-docs4ai Navigation</title></head>
<body>
    <h1>openwrt-docs4ai API Documentation</h1>
    <p>Select a view format below:</p>
    <ul>
        <li><a href="llms.txt">AI Index (llms.txt)</a></li>
        <li><a href="ucode/ucode-complete-reference.md">ucode L4 Monolith</a></li>
    </ul>
</body>
</html>
```

**Explicit Schema Example E (Category D - Self-Documenting `README.md`):**
```markdown
# openwrt-docs4ai Generated Pipeline Output
**Pipeline Run Date:** 2026-03-07T12:00:00Z
**Baseline Version:** abcd123

This repository branch contains the automatically generated, stable L3, L4, and L5 layers.
To ingest this repository into an LLM context, begin at `llms.txt`.
```

---

### Layer 4 (L4): The Assembled Monoliths
*   **Format:** Massive Markdown (`.md`)
*   **Directory:** `$OUTDIR/{module_name}/`
*   **Schema Rule:** A concatenation of L2 Markdown bodies. Internal L2 YAML is stripped and replaced with a single unified L4 monolith YAML block.
*   **Link Rewriting (BUG-015)**: During assembly, all relative Markdown links MUST be rewritten to ensure they remain valid in the new L4 directory context (e.g., `./foo.md` -> `../L2-semantic/{module}/foo.md`).

**Explicit Schema Example (L4 - Monolithic Context):**
```markdown
---
module: "ucode"
total_token_count: 1460
section_count: 2
---
# ucode Complete Reference

## Table of Contents
1. [ucode fs module](#ucode-fs-module) (840 tokens)
2. [ucode uloop module](#ucode-uloop-module) (620 tokens)

## ucode fs module
The `fs` module provides file system operations.

## ucode uloop module
The `uloop` module provides the event loop implementation.
```

---

### Layer 5 (L5): Telemetry & Differential Flow
*   **Format:** `.md` (Human readable diff), `.json` (Machine readable diff)
*   **Directory:** `$OUTDIR/` (Root level)
*   **Schema Rule:** Standardized audit trails tracking API changes between pipeline runs.
*   **Baseline Retrieval:** The prior run's `signature-inventory.json` is fetched from the latest GitHub Release. If missing (first run), tracking defaults to "no baseline" mode.

**Explicit Schema Example A (L5 - `CHANGES.md`):**
```markdown
# API Drift Report (2026-03-07)
## ucode module
- [REMOVED] `fs.deprecated_function()`
- [ADDED] `fs.new_feature(param)`
```

**Explicit Schema Example B (L5 - `changelog.json`):**
```json
{
  "pipeline_date": "2026-03-07T12:00:00Z",
  "commit_hash": "e87be9d",
  "changes": {
    "ucode": {
      "dropped_signatures": ["fs.deprecated_function()"],
      "added_signatures": ["fs.new_feature(param)"]
    }
  }
}
```

**Explicit Schema Example C (L5 - `signature-inventory.json`):**
```json
{
  "pipeline_date": "2026-03-07T12:00:00Z",
  "modules": {
    "ucode": {
      "fs.open": { "signature": "fs.open(path, flags)", "returns": "number", "file": "L1-raw/ucode/api-fs-module.md" },
      "fs.read": { "signature": "fs.read(fd, len)", "returns": "string", "file": "L1-raw/ucode/api-fs-module.md" }
    }
  }
}
```

---

## 3. Pipeline Script Mapping (The "Algorithm Upgrade Plan")

| Script | Assigned Function | Output Layer | Data Mutation |
| :--- | :--- | :--- | :--- |
| `01-clone-repos.py` | Source Fetcher | **L0** | Remote Server to Local Disk |
| `02*-scrape-*.py` | Domain Normalizers | **L1** | HTML/Code Block to Pure `.md` |
| `03-normalize-semantic.py` | Semantic Enricher | **L2** | `L1 + YAML Frontmatter + Markdown Links` |
| `04-generate-ai-summaries.py` | AI Enricher (Opt) | **L2 (Meta)** | Augments L2 YAML with AI metadata |
| `05-assemble-references.py`| The Aggregator | **L3, L4** | `L2` Concatenation → Monoliths (`L4`) & Skeletons (`L3`) |
| `06a-generate-llms-txt.py` | Routing Indexes | **L3** | `L2 Metadata` → `llms.txt` / `llms-full.txt` |
| `06b-generate-agents-md.py` | Routing Indexes | **L3** | Generates `AGENTS.md` & `README.md` |
| `06c-generate-ide-schemas.py`| IDE Definition | **L3** | Extracts signatures → `.d.ts` schemas |
| `06d-generate-changelog.py` | Telemetry Builder | **L5** | Generates `CHANGES.md` and `changelog.json` |
| `07-generate-index-html.py` | HTML Landing | **L3** | Combines L3 maps into `index.html` |
| `08-validate.py` | Quality Gate | **N/A** | Hard fails on invalid schemas |

*Note: Alphabetical suffixes (e.g., `06a`, `06b`) denote tasks that execute in strict parallel. Because `07` mathematically consumes the output of `06a` (`llms.txt`), it increments to the next integer to signify a sequential stage barrier. `08` runs last to validate the final output.*

---

## 4. Archiving & Artifact Release Strategy

1.  **GitHub Releases (ZIP files):**
    *   `openwrt-docs4ai-L1-raw.zip` (Contents of `L1-raw/`)
    *   `openwrt-docs4ai-L2-semantic.zip` (Contents of `L2-semantic/`)
    *   `signature-inventory.json` (Baseline for the next pipeline run)
2.  **GitHub Pages (Live Hosting):**
    *   Deploys only **L3**, **L4**, and **L5**. (The navigational maps, the monoliths, and the changes).
    *   Must include `.nojekyll` in the root output to disable Jekyll filtering of hidden folders and YAML frontmatter.
    *   The `index.html` file provides human navigation to these specific layers.


---

# Document 2: System Architecture and Implementation Design (v12)

The implementation specification dictates how the extraction, normalization, and generation logic must execute mathematically.


# openwrt-docs4ai: System Architecture and Implementation Design (v12)

> **Date:** 2026-03-07
> **Scope:** The definitive technical architecture for the v12 multi-tier data supply chain. This document maps the sequence of extractor algorithms, defining normalization mechanics, validation constraints, the overarching continuous integration topology, and the exact environment vectors governing runtime execution.

---

## 1. Executive Summary

Version 12 represents a profound paradigm shift from "Data Extraction" to a "Data Supply Chain." 

We are rebuilding the internal pipeline topology to produce strict, categorized layers of documentation. By decoupling the extraction logic (scraping) from the presentation logic (metadata injection + formatting), we can generate exact, schema-validated documentation tailored for vastly different stakeholders (Raw Analysts, Vector DBs, IDEs, and LLMs). A given stakeholder can now point an ingestion tool at a specific layer (e.g., L2) and guarantee that *every* file conforms to the strict YAML schema defined in our topology.

---

## 2. Core Architectural Refactoring (The Supply Chain)

### 2.0 Architectural Invariants (Mandatory)
- **Centralized Configuration**: All scripts MUST import constants (dirs, modules, regex patterns) from `lib/config.py`. Hardcoded paths in scripts are a hard failure.
- **Staging-First Build**: Scripts MUST write to isolated `staging/` or `tmp/` directories. Atomic promotion to the repository branch occurs ONLY after the validation suite (`08`) passes.
- **Resource Management**: Every file operation MUST use a context manager (`with open(...) as f:`). Bare `open().read()` calls are prohibited to prevent file handle exhaustion in high-concurrency environments.
- **Cross-Platform Pathing**: All internal references (links, manifests) MUST use POSIX forward-slashes (`/`). Scripts running on Windows must normalize paths before storage.

The pipeline scripts will be aggressively refactored to align with the explicit schema examples defined in `v12-documentation-topology-tech-spec.md`.

### 2.1 Standardizing the Extractors (L1 Target)
- **Target Scripts:** `02a` through `02h` (The Scraper Suite).
- **Implementation:** Strip all YAML frontmatter injection from extractors. The scripts fetch data, write to `$WORKDIR/L1-raw/`, and emit a companion `.meta.json` sidebar containing origin context.
- **Content Integrity:** Every L1 file MUST have a `content_hash` (truncated SHA256) calculated during the write process and stored in its `.meta.json`.
- **Wiki Rate Limiting & Sniper Targets:** The wiki scraper (`02a`) MUST enforce a hard 1.5-second delay to defend against global bot rate-limits. Additionally, `02a` MUST maintain an internal `MANDATORY_PAGES` list (e.g., `/docs/techref/ubus`). These "sniper" targets MUST always be attempted and MUST bypass any age-based cutoff logic (`CUTOFF`) to ensure critical API context is never lost during pruning cycles.
- **DokuWiki Ghost Pages:** Scrapers targeting DokuWiki MUST check for the "This topic does not exist" string in raw exports to catch 200 OK responses for non-existent pages.
- **Extractor Failure Modes:** Individual file extraction failures (e.g. 404, bad markup) are handled as *soft warnings*—the script logs, skips the file, and proceeds. However, if a script processes the upstream target and yields **zero output files**, it must exit non-zero (hard fail), signaling that the upstream structure likely changed and the scraper is broken.
- **Subprocess Safety (BUG-043)**: All calls to external tools (Pandoc, JSDoc, Node) MUST use `subprocess.run` with a mandatory `timeout=120` and MUST check `res.returncode`. Silent failures are prohibited.
- **Filename Collision Resolution (BUG-011)**: To prevent slug collisions when multiple subdirectories contain files with identical names (e.g., `main.js`), slugs MUST be derived from the relative path (e.g., `api-luci-base-main`) or include an unique identifier.
- **The Code Wrapper Compliance Check:** Scripts fetching raw code must conform to the **L1 Raw Code Schema**. They will wrap the code in markdown fences (```` ```javascript ````) prepended with an `H1` denoting the file name.

### 2.2 The Normalization & Promotion Engine (L2 Target, Modular Three-Phase)
- **Target Script:** `03-normalize-semantic.py`.
- **Integrated Pipeline Role:** This script functions as the primary state-machine for documentation enrichment. It natively handles metadata injection, cross-linking, and the final atomic promotion to the staging area to guarantee that only fully-processed artifacts reach the output directory.
- **Modular Internal Structure:** The script MUST be partitioned into discrete, testable functions for (1) `pass_1_normalize_all`, (2) `pass_2_link_all`, and (3) `promote_to_staging`.
- **Reproducible Determinism:** Iterate over modules and files in sorted alphabetical order. Output YAML keys in identical deterministic sequences via a robust YAML serializer (`pyyaml`). 
- **Performance Constraints:** All regex patterns used for symbol replacement MUST be pre-compiled *once* outside the file processing loops.
- **Implementation (Pass 1 - Stamping):** Ingest `L1-raw/` and `.meta.json` files. Calculate tokens for the Markdown *body only*. Apply the **L2 Semantic Schema**. Extract signatures to a JSON registry (`cross-link-registry.json`). 
- **Pass 1 Failure Boundary:** If the corresponding `.meta.json` is missing or malformed, `03-normalize-semantic.py` MUST trigger a fatal error and exit non-zero immediately.
- **Implementation (Pass 3 - Deprecation):** Scan `ucode` and `luci` API docs for symbols followed by "Deprecated" markers. Tag these in the registry. For wiki pages referencing these symbols, inject a `[!WARNING]` callout to alert the agent/user of upcoming API breakage.
- **Implementation (Promotion):** Once the three passes are clean, atomically copy the stage layers from `WORKDIR` to `OUTDIR`. Clear existing `OUTDIR` staging subdirectories first to ensure build purity.
- **Optional AI Extractor (`04`):** If `SKIP_AI=false`, script `04` appends the `ai_summary` field in-place within the staged layer. 
- **Manual AI Override Pattern:** The script docstring MUST include a "Manual Override" prompt. This prompt is designed as an **operational mission plan** (pseudocode) that allows a human to paste the prompt and file content into a frontier LLM (Claude/GPT) to achieve a 1-to-1 functional replacement for the script when API credits are exhausted or the environment is isolated.
- **Prompt Content Standards:** The prompt MUST specify the exact YAML tags to generate (`ai_summary`, `ai_when_to_use`, `ai_related_topics`), enforce "No Hallucination" rules (only naming symbols present in the text), and mandate a "Clean Copy" response format (Markdown block with modified content only).

**Explicit Schema Example (Manifest - `repo-manifest.json` - BUG-035):**
```json
{
  "ucode": "e87be9d",
  "luci": "1a2b3c4",
  "openwrt": "abcdef1",
  "timestamp": "2026-03-07T12:00:00Z"
}
```
*(Note: Manifest MUST be generated in Phase 1 and uploaded as a CI artifact to persist commit context across isolated matrix jobs)*

### 2.3 Formalizing the Indexes (L3 & L5 Targets)
- **Target Scripts:** `06a` through `06d` (Parallel Generators), `07` (Sequential HTML generator).
- **Implementation:** The index generators validate and aggregate YAML metadata from the `L2-semantic/` directory to build the `llms.txt` maps, `.d.ts` schemas, and HTML indexes into the root `$OUTDIR`.
- **IDE TypeScript Generics:** Extract function definitions via `cross-link-registry.json` (authoritative inventory list), parsing parameter types from the associated L2 Markdown headings. For v12, `.d.ts` generation is strictly scoped to `ucode` module APIs only (`$OUTDIR/ucode/ucode.d.ts`); LuCI JS is deferred. The pipeline MUST map types as follows: `string`->`string`, `int`/`double`->`number`, `bool`->`boolean`, `array`->`any[]`, `object`->`Record<string, any>`, `resource`->`object`, `null`->`null`, `unknown`->`any`.
- **L5 Telemetry Expansion:** Output both the `CHANGES.md` human diff and the `changelog.json` schema. Baseline retrieval fallback chain: (1) try `github-release` with token, (2) if token empty/API fails, check for local `signature-inventory.json` in the committed workspace, (3) operate in "no baseline" mode. Log which path was taken.

---

## 3. Agentic Web Enhancements (Migrated from v11 Plan)

These features ensure that autonomous agents can grok the repository instantly without blind scraping.

### 3.1 `AGENTS.md` and Dual-Faceted Routing
- Automatically synthesize a root `AGENTS.md` specifying repository interaction rules, test suite commands, and the documentation taxonomy.
- Restructure the top-level `/llms.txt` into an optimal "Decision Tree" (guiding an Agent to the correct subfolder).
- Create a secondary `/llms-full.txt` that functions as a flat aggregate catalog for automated ingestors.

### 3.2 Visual Architecture Mapping (Mermaid.js)
- Enhance the L2 normalization engine (`03`) to recognize target architecture files and statically inject curated ````mermaid` sequence diagram templates from the `templates/mermaid/` directory into the headers of relevant core daemons (e.g., `procd`, `hotplug`). *Note: Dynamic/Automatic diagram rendering is explicitly out of scope for v12 due to hallucination risks.*

---

## 4. Pipeline Execution & Delivery Updates

### 4.1 Artifact Splitting
- Modify `openwrt-docs4ai-00-pipeline.yml` to bundle `L1-raw/` and `L2-semantic/` as downloadable `.zip` release artifacts attached to the monthly run.
- GitHub Pages will exclusively host the L3, L4, and L5 layers as the "human and agent front-door."

### 4.2 Incremental Cost Reduction
- **Wiki Scraping Cache (`If-Modified-Since`):** Modify `02a-scrape-wiki.py` to store and check local HTTP `Last-Modified` metadata logic in `.cache/wiki-lastmod.json`, persisting across CI runs via `actions/cache`.
- **AI Summary Caching (`content_hash`):** Script `04` MUST utilize `ai-summaries-cache.json`. Before calling the LLM, the script MUST calculate the `content_hash` of the L1 source. If the hash exists in the cache, the summary is reused instantly. This reduces processing time from minutes to seconds.
- **Graceful API Failure (Hard Halt):** If the AI API returns a **401 (Unauthorized)** or **403 (Quota Exceeded)**, the script MUST immediately return a `STOP` signal. The processing loop MUST break, and the pipeline MUST proceed with any cached summaries. Redundant retries on a dead API are prohibited.
- **Concurrency & Push Triggers:** Enforce workflow concurrency to cancel in-progress runs on branch pushes using `concurrency: { group: docs-pipeline-${{ github.ref }}, cancel-in-progress: true }`. Restrict `push` triggers to `.github/scripts/**`, template folders, and `.yaml` workflow files.
- **Diff Commits:** Execute a diff comparison mapping of the generated output vs existing branch output. If no diff exists, the pipeline simply skips committing instead of creating an empty bump commit.

---

## 5. Security and Validation
- **Two-Tier Validation Engine (`08-validate.py`):** Validation is split into Hard Fails and Soft Warns.
- **Hard Checks (Fails CI):** 
  - Missing `llms.txt` or zero-byte files.
  - Files exceeding a **2.0MB Size Ceiling** (indicates crawler loops or binary leak).
  - Malformed YAML frontmatter anywhere globally.
  - Strict JSON schema validation failures for the pipeline control files (`repo-manifest.json`, `cross-link-registry.json`, `signature-inventory.json`).
  - **Broken Link Detection:** The validator MUST use a **negative-lookahead regex** to identify relative Markdown links while ignoring external protocols: `\[.*?\]\(((?!https?:\/\/|mailto:|[a-z0-9]+:).*?\.md)\)`. This ensures that sibling links without `./` or `../` prefixes are correctly validated.
  - **HTML Leak Protection (BUG-017):** The script MUST check L1 files against this explicit signature list: `404 Not Found`, `Cloudflare`, `Access Denied`, `Just a moment...`, `Checking your browser`, `captcha`, `Service Temporarily Unavailable`, and `Rate limit exceeded`. **CRITICAL:** To avoid false positives on documentation *about* these errors, a leak is only flagged if structural HTML tags (`<!DOCTYPE` or `<html>`) are also detected in the content.
- **The AST Linter Guardrail (Soft Warn Mode):** Validates the code blocks embedded within the generated markdown syntactically against standard tools (e.g. `node --check`, `ucode -c`). Since code extracts are often partial expressions or isolated, this runs as a *soft warning* rather than a hard failure to avoid brittle CI pipelines.

---

## 6. Development Standards & Environment

### 6.1 Logging and Header Specifications
- **Script Headers:** Every pipeline script MUST begin with a standardized docstring block declaring: Purpose, Phase, Layers, Environment Variables, Inputs, Outputs, Dependencies, and Notes. *(Refer explicitly to Addendum Section A5 from the Opus review for the exact 10-line Python template.)*
- **Logging Format:** All scripts must emit logs conforming to `[SCRIPT_ID] LEVEL: message` (e.g. `[02a] OK: Scraped 15 pages`).

### 6.2 Environment Variable Matrix
| Variable | Default Value | Scripts Utilizing | Purpose |
|:---|:---|:---|:---|
| `WORKDIR` | `tmp` | All | Ephemeral dir for repo clones & intermediate outputs. |
| `OUTDIR` | `openwrt-condensed-docs` | `03`, `04`, `05`, `06*`, `07`, `08` | Stable dir for final deliverable publishing. |
| `SKIP_WIKI` | `false` | `02a` | Bypasses the wiki scraper (which takes ~10m) if true. |
| `SKIP_AI` | `true` | `04` | AI enrichment is opt-in (costs money). Set to false to run. |
| `WIKI_MAX_PAGES` | `300` | `02a` | Breadth safety limit for scraper traversal graph. |
| `MAX_AI_FILES` | `40` | `04` | Quota budget limit defining how many files to hit the LLM with. |
| `VALIDATE_MODE` | `hard` | `08` | Strict validation enforcement mode. `warn` permits failures. Supports `--warn-only` CLI flag. |
| `MERMAID_INJECT`| `true` | `03` | Toggle curated template diagram injection. |
| `GITHUB_TOKEN` | (Empty) | `06d` | Required to fetch previous Releases for signature baseline. |
| `LOCAL_DEV_TOKEN` | (Empty) | `04` | Local dev override for querying the upstream LLM inference API. |
| `LLM_BUDGET_LIMIT`| `$5.00`| `04` | Hard-coded circuit breaker terminating `04` to prevent infinite loop billing overruns. |
| `TOKENIZER` | `cl100k_base` | `03`, `04` | Specifies the tokenizer target for token cost sizing. |
| `DTS_GENERATE` | `true` | `06c` | Kill-switch toggle for experimental TypeScript definitions. |
| `BASELINE_SOURCE`| `github-release`| `06d` | Options: `github-release`, `local`, `none`. Drives diff tests. |
| `AI_CACHE_PATH` | `ai-summaries-cache.json` | `04` | Path to the persistent JSON archive of generated AI metadata. |
| `RUNNER_TEMP` | (CI Built-in) | CI YAML, `WORKDIR` | GitHub absolute path to runner temporary volume. |
| `GITHUB_WORKSPACE` | (CI Built-in) | CI YAML | GitHub standard workspace path where repo is executed. |


---

# Document 3: Execution Roadmap and Rollout Milestones (v12)

The execution strategy outlines the sequential development checkpoints for bringing V12 online safely.


# openwrt-docs4ai: Execution Roadmap and Rollout Milestones (v12)

> **Date:** 2026-03-07
> **Scope:** A sequential project management roadmap detailing the iterative refactoring and implementation of the L0-L5 topology. This document serves as the tactical milestone checklist for the v12 development sprint, guaranteeing stability by deploying changes iteratively across validated checkpoints.

---

## The Strategic Sequence

To minimize downtime and avoid breaking the existing GitHub Pages deployment during the transition, we must refactor the scripts sequentially—from extraction (L1) through normalization (L2) and finally into presentation (L3-L5). 

We will *not* merge to `main` until the entire 6-checkpoint sequence is running successfully locally.

### Checkpoint 0: Shared Lib & The Smoke Test Suite
**Goal:** Establish the foundational utilities and a rapid local feedback loop before refactoring extractors.
1.  **Create Mock Fixtures (`tests/fixtures/`):** Generate 100% frozen HTML and C-source mocks. This guarantees the smoke test is **deterministic, offline-capable, and independent** of upstream network or repository changes.
2.  **Create `tests/00-smoke-test.py`:** A runner that executes the entire pipeline logic (L2-L5) using the seeded mocks. It MUST include a dedicated test case for **sibling link validation** and **balanced-bracket parameter parsing**.
3.  **Mandatory Config Library:** Build `lib/config.py` as the **Single Source of Truth**. All scripts MUST import their paths and constants from this library.
4.  **Manual Repositories:** Write `CONTRIBUTING.md` (instructions for adding new scrapers) and `docs/ARCHITECTURE.md` (layer definitions mapping).

### Checkpoint 1: The L1 Extractor Refactor (Scripts `02a` to `02h`)
**Goal:** Strip all metadata injection from scrapers so they output pure markdown text to `$WORKDIR/L1-raw/`.
1.  **Refactor `02a` (Wiki Scraper) First:** Start with the hardest and most complex script. Ensure wiki logic implements network caching (`.cache/wiki-lastmod.json`), maintains a `MANDATORY_PAGES` target list, and outputs pure prose to `L1-raw/wiki/`.
2.  **Refactor `02b` (ucode C API):** Implement the known `jsdoc2md` bug workaround. (The C transpiler plugin ignores explicit files and recursively scans directories, so each `.c` file must be physically copied into an isolated temporary directory before invoking `jsdoc2md`). Output to `L1-raw/ucode/`.
3.  **Refactor Remaining `02x`:** Update the rest in dependency order. Point outputs to `$WORKDIR/L1-raw/{module}/`. Do NOT allow any script to inject YAML (enforce this via validation). Provide parallel validation outputs via `.meta.json` sidebar metadata files.

### Checkpoint 2: The L2 Normalization & Promotion Engine (Script `03`)
**Goal:** Implement the three-phase modular transformation and natively integrated staging promotion logic.
1.  **Phase 1 (YAML & Registry):** Program `03` to iterate over `L1-raw/`. Inject the **L2 Semantic Schema**, count tokens globally (Fallback: word count * 1.35), and build the symbol registry. Ensure **fatal exits** on missing or malformed `.meta.json`.
2.  **Phase 2 (Cross-linking):** Safely resolve Markdown links across text bodies. MUST protect headers (`#`), code blocks, and existing link/diagram syntax from mutation. 
3.  **Phase 3 (Deprecation Warnings):** Scan API docs for `**Deprecated**` symbols and inject warning callouts into wiki pages that reference them.
4.  **Phase 4 (Promotion):** Atomically promote intermediate layers (`L1-raw`, `L2-semantic`, `cross-link-registry.json`, `repo-manifest.json`) from ephemeral `WORKDIR` to the stable `OUTDIR` staging area.

### Checkpoint 2.7: The Optional AI Enricher (Script `04`)
**Goal:** Run the cost-gated AI summarization against the stable `OUTDIR` files explicitly after promotion.
1.  **Optional AI Ext (`04`):** Define `04-generate-ai-summaries.py` to optionally append `ai_summary` tags to the new L2 schemas *in place* in `$OUTDIR/L2-semantic/` if enabled via `SKIP_AI=false`.

### Checkpoint 3: The L4 Monolithic Assembler (Script `05`)
**Goal:** Stitch the clean L2 arrays together into context-window files, and produce structural sketches.
1.  **Concatenation Logic:** Point at `L2-semantic/`. Strip internal YAML, insert TOCs with token budgets, and construct **L4 Monoliths**. During the same iteration across grouped modules, output the **L3 Skeletons** (`*-skeleton.md`) as compact navigational aids. Warn if a monolith exceeds 100,000 tokens.

### Checkpoint 4: The L3 & L5 Map Generators (Scripts `06a-d` & `07`)
**Goal:** Split the overgrown indexer into a suite of single-responsibility generators directly outputting to `$OUTDIR`.
1.  **`06a-generate-llms-txt.py`:** Generates both the decision tree `llms.txt` and the `llms-full.txt` lists. **REQUIREMENT (BUG-031)**: These indexes MUST explicitly include the newly generated L3 skeletons and L4 monoliths as entry points.
2.  **`06b-generate-agents-md.py`:** Synthesizes the machine-readable repository interaction map `AGENTS.md` and generates the human-readable `openwrt-condensed-docs/README.md` (output self-documentation).
3.  **`06c-generate-ide-schemas.py`:** For v12, extracts signatures and generates `.d.ts` schemas strictly for the `ucode` module only. Outputs to `$OUTDIR/ucode/ucode.d.ts`.
4.  **`06d-generate-changelog.py`:** Generates telemetry tracking API drift (`changelog.json`), failing safely on the "first run" missing baseline scenario.
5.  **`07-generate-index-html.py`:** Outputs the frontend landing payload. Because this script requires `llms.txt` to inject dynamic lists, it is incremented to a new sequential integer (`07`) to mathematically separate it from the parallelizable `06a-d` group.

### Checkpoint 5: The Security & Quality Enforcer (Script `08`)
**Goal:** Build the strict CI/CD gatekeeper `08-validate.py` before touching the workflow files.
1.  **Two-Tier Design:** Build a validation tool that supports `hard_fail()` and `soft_warn()`. Support both `VALIDATE_MODE` and `--warn-only`.
2.  **Hard Checks:** Block CI if `llms.txt` is missing, files are 0 bytes, **exceed 2MB**, YAML is corrupted, or wiki pages crawl Cloudflare/404 HTML text.
3.  **Index Reconciliation (BUG-008)**: The validator MUST verify that every unique Markdown file present in `L2-semantic/` is accounted for in the `llms-full.txt` flat catalog.
4.  **Global Syntax Gate (BUG-023)**: AST validation MUST be applied to code blocks across ALL generated markdown files, not just example snippets.
5.  **Soft Checks:** Log non-fatal AST parsing warnings from embedded `c`/`javascript` subsets against `node --check` / `ucode -c`.

### Checkpoint 6: CI/CD Pipeline Configuration
**Goal:** Update GitHub Actions (`00-pipeline.yml`) to correctly route our new layered output.
1.  **Dependencies:** Cache pip (`tiktoken`, `pyyaml`, `requests`, `lxml`) and npm (`jsdoc2md`) via `actions/cache`. Use a multi-tier cache strategy for Wiki and AI metadata to reduce runtime from 20m to <8m.
2.  **Matrix Extractors:** Configure GitHub Actions to execute `02a`-`02h` in parallel. Parallel jobs MUST upload their isolated `L1-raw/` artifacts, and a subsequent synchronization job MUST download and merge them into a unified `$WORKDIR/L1-raw/` directory.
3.  **Workspace Promotion & Concurrency:** Build layers in isolation. Utilize GitHub Actions `concurrency` groups to prevent simultaneous push collisions. Implement a retry-on-conflict logic for the final `git push`. Execute promotion back to the repository branch ONLY if validation (`08`) passes.
4.  **Failure Artifact Flow:** On validation failure (`08-validate.py`), strictly upload `$OUTDIR` (staging) as a downloadable artifact (`actions/upload-artifact`) with 7-day retention for debugging.
5.  **Targeted Parallel Indexes:** Ensure generators `06a, 06b, 06c, 06d` run in parallel. Ensure `07-generate-index-html.py` waits for `06a` to complete, as it mathematically consumes the L3 Map.
6.  **Pages Deployment:** Utilize `actions/configure-pages@v5` with `enablement: true` to automate environment setup. Push exclusively the final L3, L4, and L5 layers to GitHub Pages.

---

## Immediate Next Steps (For the Developer)

When development begins, construct **Checkpoint 0** (the Smoke Test and Shared Libs) to allow testing `WORKDIR` mutations locally. After that, move onto **Checkpoint 1 (02a Wiki Scraper)** and steadily work down the checklist, matching the output schemas requested by Opus.


---
# Document 4: Project Code Summary (Target State)
The following is an architectural mapping of the intended internal script behaviors required to execute the v12 specs. All python scripts run within `.github/scripts/`.

## External Dependencies (`requirements.txt`)
- `requests` (Wiki HTTP calls)
- `beautifulsoup4` (HTML parsing for wiki metadata)
- `lxml` (Fast C-based HTML parsing backend for BeautifulSoup)
- `pyyaml` (L2 frontmatter stamping)
- `tiktoken` (Token counting across layers)

## Foundational Utilities
*(Note: To import `lib/` modules from within `.github/scripts/`, scripts must append their parent directory to `sys.path` or be executed strictly with `.github/scripts/` as the CWD.)*
- `lib/config.py` (Shared Config)
  - **Inputs:** `os.environ` (`WORKDIR`, `OUTDIR`, `TOKENIZER`, etc.)
  - **Outputs:** Python constants for all scripts.
  - **Functions:** `env_bool()`, `env_int()`, `get_work_dir()`, `get_out_dir()`
- `lib/extractor.py` (Shared Extractor Logic)
  - **Inputs:** Extracted text from scrapers.
  - **Outputs:** L1 file and `.meta.json` filesystem writes.
  - **Functions:** `write_l1_file()`, `wrap_code_block()`, `slugify()`
- `lib/constants.py` (Enums & Tokens)
  - **Outputs:** Shared string maps.
  - **Constants:** `{ c_source, js_source, wiki_page, makefile_meta, readme, uci_schema, hotplug_event, example_app, header_api }`
- `lib/metadata.py` (L2 YAML & Semantics)
  - **Functions:** `count_tokens()`, `stamp_yaml_frontmatter()`
- `lib/validation.py` (Shared Quality Gate)
  - **Functions:** `detect_html_errors()`, `verify_utf8()`

## The Smoke Test Runner
- `tests/00-smoke-test.py` (Local Testing)
  - **Inputs:** Local environment (`tests/fixtures/`) and CLI arguments.
  - **Outputs:** Ephemeral `WORKDIR` pipeline execution, persistent log file `tests/smoke-test-log.txt`.
  - **Flags:** `--keep-temp` (preserve working dir), `--skip-wiki` (bypasses 10m run), `--only SCRIPT` (isolate).
  - **Functions:** `main()`, `run_pipeline_stage()`, `verify_output()`

## Phase 1: Emitting Raw L1 Extractions
- `01-clone-repos.py`
  - **Inputs:** Upstream GitHub Repos.
  - **Outputs:** `$WORKDIR/repo-*/`, `$WORKDIR/repo-manifest.json`
  - **Functions:** `main()`, `clone_repo()`, `write_manifest()`
- `02a-scrape-wiki.py`
  - **Inputs:** openwrt.org wiki endpoints, `.cache/wiki-lastmod.json`
  - **Outputs:** `$WORKDIR/L1-raw/wiki/*.md`, `*.meta.json`
  - **Functions:** `main()`, `fetch_page_cached()`, `parse_to_md()`, `write_payload()`
- `02*-scrape-[module].py` (02b through 02h)
  - **Reads:** `$WORKDIR/repo-[module]/` files
  - **Writes:** `$WORKDIR/L1-raw/[module]/*.md`, `*.meta.json`
  - **Functions:** Domain-specific parsers.

## Phase 2: L2 Normalization Engine 
- `03-enrich-semantics.py`
  - **Inputs:** `$WORKDIR/L1-raw/`, `*.meta.json`, `$WORKDIR/repo-manifest.json`
  - **Outputs:** `$WORKDIR/L2-semantic/`, `$WORKDIR/cross-link-registry.json`
  - **Functions:** `main()`, `pass_1_stamp_metadata()`, `count_tokens()`, `pass_2_inject_links()`, `write_l2_yaml()`
- `04-generate-summaries.py` (Optional / Target: OUTDIR)
  - **Inputs:** `$OUTDIR/L2-semantic/` (Executes after Checkpoint 4 promotion to staging)
  - **Outputs:** Mutates `$OUTDIR/L2-semantic/` directly in place, establishing the authoritative Layer 2 output.
  - **Functions:** `main()`, `invoke_llm()`, `append_yaml()`

## Phase 3: L3, L4, and L5 Assembly & Indexes
- `05-assemble-references.py`
  - **Inputs:** `$OUTDIR/L2-semantic/`
  - **Outputs:** `$OUTDIR/{module}/*-complete-reference.md` (L4), `$OUTDIR/{module}/*-skeleton.md` (L3)
  - **Functions:** `main()`, `group_by_module()`, `concatenate_monolith()`
- `06a-generate-llms-txt.py`
  - **Inputs:** `$OUTDIR/L2-semantic/`
  - **Outputs:** `$OUTDIR/llms.txt`, `$OUTDIR/llms-full.txt` (L3), `$OUTDIR/{module}/llms.txt` (L3 module indexes)
  - **Functions:** `main()`, `build_decision_tree()`, `build_flat_catalog()`
- `06b-generate-agents-md.py`
  - **Inputs:** `lib/constants.py` , `$OUTDIR/L2-semantic/` limits.
  - **Outputs:** `$OUTDIR/AGENTS.md` (L3), `$OUTDIR/README.md` (Category D)
  - **Functions:** `main()`, `write_agent_instructions()`, `write_human_readme()`
- `06c-generate-ide-schemas.py`
  - **Inputs:** `$OUTDIR/L2-semantic/`, `$OUTDIR/cross-link-registry.json`
  - **Outputs:** `$OUTDIR/ucode/ucode.d.ts` (L3 - Scoped strictly to ucode for v12)
  - **Functions:** `main()`, `extract_ts_signatures()`, `write_schema()`
- `06d-generate-changelog.py`
  - **Inputs:** `$OUTDIR/L2-semantic/`, Network (GitHub Releases Baseline)
  - **Outputs:** `$OUTDIR/CHANGES.md`, `$OUTDIR/changelog.json`, `$OUTDIR/signature-inventory.json` (L5)
  - **Functions:** `main()`, `fetch_baseline()`, `calculate_drift()`, `write_telemetry()`
- `07-generate-index-html.py` (Runs AFTER 06a)
  - **Inputs:** `$OUTDIR/llms.txt`
  - **Outputs:** `$OUTDIR/index.html` (L3 Web Landing), `$OUTDIR/.nojekyll` (L3 Override)
  - **Functions:** `main()`, `render_html_template()`

## Phase X: Validation & Quality Control
- `08-validate.py`
  - **Inputs:** `$OUTDIR/` (All final published layers)
  - **Outputs:** stdout reports, exit code 0 or 1.
  - **Functions:** `main()`, `hard_fail()`, `soft_warn()`, `check_yaml_schema()`, `detect_html_corruption()`, `lint_code_blocks()`
