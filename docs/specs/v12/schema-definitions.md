# openwrt-docs4ai v12 Schema Definitions

## Purpose

This document defines the active filesystem and data contracts for the v12 pipeline.

## Top-Level Paths

- `WORKDIR` defaults to `tmp`
- `OUTDIR` defaults to `openwrt-condensed-docs`
- `docs/` is for maintainer documentation only

## Dual-Role Documentation Boundary

The repository has two distinct documentation surfaces:

- The source tree is the maintainer and implementation surface. Its authoritative material lives in `README.md`, `DEVELOPMENT.md`, and `docs/specs/v12/`.
- The generated corpus under `OUTDIR` is the published LLM and IDE navigation surface.

This document defines the generated-corpus contract only. A source-repo root `llms.txt` is intentionally deferred and is not part of the active v12 contract.

The active publication policy keeps L1 and L2 under `openwrt-condensed-docs` for inspection, debugging, and AI-context use. L0 remains unpublished because raw clones and raw fetched inputs are materially larger and are not needed as durable outputs.

## Layer Contracts

### L0

- Location: `tmp/repo-*`
- Contents: untouched upstream clones or raw fetched inputs
- Publication: none; treat as transient local or CI-only build state

### L1

- Location during build: `tmp/L1-raw/{module}/`
- Retained output location: `openwrt-condensed-docs/L1-raw/{module}/`
- File naming: `{origin_type}-{slug}.md`
- Sidecar naming: `{origin_type}-{slug}.meta.json`
- Rules:
  - markdown only
  - no YAML frontmatter
  - no injected cross-links
  - code blocks must carry explicit language identifiers

#### L1 sidecar fields

Required or expected fields:

- `extractor`
- `origin_type`
- `module`
- `slug`
- `content_hash`

Recommended fields when known:

- `upstream_path`
- `original_url`
- `language`
- `fetch_status`
- `extraction_timestamp`

### L2

- Location during build: `tmp/L2-semantic/{module}/`
- Retained output location: `openwrt-condensed-docs/L2-semantic/{module}/`
- Format: markdown with YAML frontmatter
- Rules:
  - YAML must be parsed and written safely
  - cross-links must not be injected inside code fences or inline code
  - cross-links must remain relative Markdown links that resolve within the published output tree
  - file or path references intended as navigation aids should be emitted as Markdown links rather than inline code spans
  - inline code remains appropriate for commands, environment variables, symbol names, and syntax literals
  - token counts describe body content, not frontmatter

#### Required L2 frontmatter fields

- `title`
- `module`
- `origin_type`
- `token_count`
- `version`

#### Recommended L2 frontmatter fields

- `source_file`
- `upstream_path`
- `language`
- `description`
- `last_pipeline_run`

#### Optional AI fields

- `ai_summary`
- `ai_when_to_use`
- `ai_related_topics`

### L3

- Location: `openwrt-condensed-docs/` root and module subdirectories
- Primary outputs:
  - `llms.txt`
  - `llms-full.txt`
  - `AGENTS.md`
  - `README.md`
  - `index.html`
  - `*-skeleton.md`
  - `*.d.ts`

### L3 LLM Routing Contract

The generated corpus is both a published documentation product and a navigation surface for tools and models. Its LLM-facing outputs must therefore be deterministic, link-safe, and self-describing.

#### Root `llms.txt`

Required characteristics:

- single H1 title line for the routing index
- introductory blockquote lines that point to `llms-full.txt`, state the version banner, and state the total underlying L2 token count
- one or more H2 category sections
- category bullet lines that point only to module indexes
- bullet format:

```text
- [<module>](./<module>/llms.txt): <short description> (~<module_l2_tokens> tokens)
```

Rules:

- root `llms.txt` is a routing tree, not the exhaustive catalog
- the displayed token count represents underlying L2 content for the module rather than duplicated L3 or L4 helper files
- descriptions should prefer `ai_summary`, then `description`, then a first-sentence body fallback
- placeholder descriptions such as `No description` are not valid output

#### Root `llms-full.txt`

Required characteristics:

- single H1 title line for the flat catalog
- optional introductory blockquote lines are allowed
- flat bullet list sorted by relative path
- catalog entries must include all generated AI-facing helper files and all L2 markdown documents that belong to the published corpus
- required catalog coverage:
  - `AGENTS.md`
  - generated `README.md`
  - each module `llms.txt`
  - each `*-skeleton.md`
  - each `*-complete-reference.md`
  - each published `.d.ts`
  - every `L2-semantic/{module}/*.md`
- bullet format:

```text
- [<relative-path>](./<relative-path>): <short description> (~<tokens> tokens, <kind>)
```

Typical `kind` values include `l2-source`, `l3-agent-guide`, `l3-generated-readme`, `l3-module-index`, `l3-skeleton`, `l3-ide-schema`, and `l4-monolith`.

#### Module `llms.txt`

Required characteristics:

- H1 title in the form `# <module> module`
- introductory blockquote lines for module description and total underlying L2 token count
- deterministic H2 section order
- allowed sections:
  - `Recommended Entry Points`
  - `Tooling Surfaces`
  - `Source Documents`
- empty sections must be omitted

Preferred section semantics:

- `Recommended Entry Points` lists the module skeleton and monolithic reference when present
- `Tooling Surfaces` lists generated `.d.ts` or other IDE-oriented helper files when present
- `Source Documents` lists each L2 document for the module

Bullet formats:

```text
- [<module>-skeleton.md](./<module>-skeleton.md): <short description> (~<tokens> tokens, l3-skeleton)
- [<module>-complete-reference.md](./<module>-complete-reference.md): <short description> (~<tokens> tokens, l4-monolith)
- [<module>.d.ts](./<module>.d.ts): <short description> (~<tokens> tokens, l3-ide-schema)
- [<filename>.md](../L2-semantic/<module>/<filename>.md): <short description> (~<tokens> tokens, l2-source)
```

#### `AGENTS.md`

`AGENTS.md` must remain consistent with the routing contract above.

Required guidance points:

- begin at root `llms.txt`
- prefer module `llms.txt` once the target subsystem is known
- prefer `*-skeleton.md` before monolithic references when context is tight
- treat generated module indexes, skeletons, monoliths, and `.d.ts` files as published navigation surfaces
- avoid implying that a separate source-repo root `llms.txt` already exists

### L4

- Location: `openwrt-condensed-docs/{module}/`
- Format: monolithic markdown files
- Rule: one top-level YAML block per monolith, not repeated L2 frontmatter sections

### L5

- Location: `openwrt-condensed-docs/`
- Outputs:
  - `CHANGES.md`
  - `changelog.json`
  - `signature-inventory.json`

## Enumerated Origin Types

- `c_source`
- `js_source`
- `wiki_page`
- `makefile_meta`
- `readme`
- `uci_schema`
- `hotplug_event`
- `example_app`
- `header_api`

## Stakeholder Mapping

| Stakeholder | Primary layers |
| --- | --- |
| Raw analyst | L1, L2 |
| Context injector | L2 |
| Human developer | L3, L4 |
| IDE tooling | L3 |
| Drift and telemetry tooling | L5 |
| Pipeline maintainer | all layers plus local logs |
