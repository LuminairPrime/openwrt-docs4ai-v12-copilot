# openwrt-docs4ai v12 Schema Definitions

## Purpose

This document defines the active filesystem and data contracts for the v12 pipeline.

## Top-Level Paths

- `WORKDIR` defaults to `tmp`
- `OUTDIR` defaults to `openwrt-condensed-docs`
- `docs/` is for maintainer documentation only

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
