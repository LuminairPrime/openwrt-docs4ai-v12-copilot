# openwrt-docs4ai v12 Schema Definitions

## Purpose

This document defines the active filesystem and data contracts for the v12 pipeline.

## Contract Status

This document defines the active V5a release-tree contract. Legacy `openwrt-condensed-docs/{module}/...` filenames and paths are mentioned only when needed to explain historical mappings or retained internal staging evidence.

For the standalone V5a contract reference, see [release-tree-contract.md](release-tree-contract.md).

## Top-Level Paths

- `WORKDIR` defaults to `tmp`
- `OUTDIR` defaults to `openwrt-condensed-docs`
- `docs/` is for maintainer documentation only

## Dual-Role Documentation Boundary

The repository has two distinct documentation surfaces:

- The source tree is the maintainer and implementation surface. Its authoritative material lives in `README.md`, `DEVELOPMENT.md`, and `docs/specs/v12/`.
- The generated corpus under `OUTDIR` is the published LLM and IDE navigation surface.

This document defines the generated-corpus contract only. A source-repo root `llms.txt` is intentionally deferred and is not part of the active v12 contract.

The active publication policy keeps L1 and L2 in internal staging form for inspection, debugging, and AI-context use. L0 remains unpublished because raw clones and raw fetched inputs are materially larger and are not needed as durable outputs.

The `openwrt-condensed-docs` name is internal to the source repo only. It must not appear in any public path, URL, or visible label. Public surfaces expose only the `release-tree/` direct-root layout. The staged `openwrt-condensed-docs` working root remains present as internal CI state and materializes `support-tree/` for non-public outputs.

## Layer Contracts

### L0

- Location: `tmp/repo-*`
- Contents: untouched upstream clones or raw fetched inputs
- Publication: none; treat as transient local or CI-only build state

### L1

- Location during build: `tmp/L1-raw/{module}/`
- Retained output location: `support-tree/raw/{module}/` — not published to any public surface
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
- Retained output location: `support-tree/semantic-pages/{module}/` — not published directly; L2 topic pages are redistributed into each module's `chunked-reference/` folder inside `release-tree/`
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

- Location: `release-tree/` root and `release-tree/{module}/` subdirectories

Primary outputs:

- `llms.txt`
- `llms-full.txt`
- `AGENTS.md`
- `README.md`
- `index.html`
- `{module}/map.md` — replaces `{module}-skeleton.md`; provides a navigation map for the module
- `{module}/types/{module}.d.ts` — IDE schema, moved into per-module `types/` subdirectory

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
  - each `{module}/map.md`
  - each `{module}/bundled-reference.md`
  - each `{module}/bundled-reference.part-{NN}.md` when sharding is present
  - each published `{module}/types/{module}.d.ts`
  - every `{module}/chunked-reference/{topic}.md`
- bullet format:

```text
- [<relative-path>](./<relative-path>): <short description> (~<tokens> tokens, <kind>)
```

Typical `kind` values include `l2-source`, `l3-agent-guide`, `l3-generated-readme`, `l3-module-index`, `l3-skeleton`, `l3-ide-schema`, `l4-monolith`, and `l4-monolith-part`.

`l3-skeleton` entries reference `map.md`; `l4-monolith` entries reference `bundled-reference.md`; `l2-source` entries reference `{module}/chunked-reference/{topic}.md`.

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

- `Recommended Entry Points` lists the module navigation map, the stable bundled-reference index, and any sharded part files when present
- `Tooling Surfaces` lists generated `.d.ts` or other IDE-oriented helper files when present
- `Source Documents` lists each L2 document for the module

Bullet formats:

```text
- [map.md](./map.md): <short description> (~<tokens> tokens, l3-skeleton)
- [bundled-reference.md](./bundled-reference.md): <short description> (~<tokens> tokens, l4-monolith)
- [bundled-reference.part-01.md](./bundled-reference.part-01.md): <short description> (~<tokens> tokens, l4-monolith-part)
- [<module>.d.ts](./types/<module>.d.ts): <short description> (~<tokens> tokens, l3-ide-schema)
- [<filename>.md](./chunked-reference/<filename>.md): <short description> (~<tokens> tokens, l2-source)
```

Module names are not repeated in child filenames inside the module folder. `map.md` and `bundled-reference.md` are fixed filenames, not module-prefixed. Source document links resolve relative to the module folder via `chunked-reference/`.

#### `AGENTS.md`

`AGENTS.md` must remain consistent with the routing contract above.

Required guidance points:

- begin at root `llms.txt`
- prefer module `llms.txt` once the target subsystem is known
- prefer `map.md` before `bundled-reference.md` or part files when context is tight; `map.md` is the stable per-module navigation entry point
- treat generated module indexes, navigation maps, bundled references, part files, and `.d.ts` files as published navigation surfaces
- `bundled-reference.md` and `map.md` are fixed filenames inside each module folder; they are not module-prefixed
- avoid implying that a separate source-repo root `llms.txt` already exists

### L4

- Location: `release-tree/{module}/`
- Format: one stable `bundled-reference.md` per module plus optional sharded `bundled-reference.part-{NN}.md` files for oversized modules; sharded parts sit alongside `bundled-reference.md`, not inside `chunked-reference/`
- Rule: one top-level YAML block per generated L4 file, not repeated L2 frontmatter sections

### L5

- Location: `support-tree/telemetry/` — not published to any public surface
- Outputs:
  - `CHANGES.md`
  - `changelog.json`
  - `signature-inventory.json`

## Output Topology

The pipeline main output root contains two distinct subtrees. Only `release-tree/` is publishable. `support-tree/` is internal CI state and must never appear in any public surface.

### `release-tree/` — publishable output, direct-root layout

The `release-tree/` subtree is the complete public product. It uses a direct-root layout where every module folder sits at root with no wrapper directory. The `release-tree/` root itself becomes the repository root for GitHub Pages and the ZIP expansion root.

```text
release-tree/
├── README.md
├── AGENTS.md
├── llms.txt
├── llms-full.txt
├── index.html
├── {module}/
│   ├── llms.txt
│   ├── map.md
│   ├── bundled-reference.md
│   ├── chunked-reference/
│   │   └── {topic}.md ...
│   └── types/           (optional)
│       └── {module}.d.ts
└── ... (more modules)
```

Items guaranteed absent from `release-tree/`:

- `L1-raw/`
- `L2-semantic/`
- `openwrt-condensed-docs/` (any reference or path segment)
- `*-skeleton.md`
- `*-complete-reference.md`
- Any `.meta.json` sidecar
- `CHANGES.md`, `changelog.json`, `signature-inventory.json`, `repo-manifest.json`, `cross-link-registry.json`

### `support-tree/` — ephemeral CI support artifacts

`support-tree/` holds all artifacts that are useful for debugging and CI inspection but are intentionally excluded from the public product. Its internal layout may change without notice and is not a stable contract.

Typical contents:

| Path | Former location (pre-V5a) |
| --- | --- |
| `support-tree/raw/` | `openwrt-condensed-docs/L1-raw/` |
| `support-tree/semantic-pages/` | `openwrt-condensed-docs/L2-semantic/` |
| `support-tree/telemetry/CHANGES.md` | `openwrt-condensed-docs/CHANGES.md` |
| `support-tree/telemetry/changelog.json` | `openwrt-condensed-docs/changelog.json` |
| `support-tree/telemetry/signature-inventory.json` | `openwrt-condensed-docs/signature-inventory.json` |
| `support-tree/manifests/repo-manifest.json` | `openwrt-condensed-docs/repo-manifest.json` |
| `support-tree/manifests/cross-link-registry.json` | `openwrt-condensed-docs/cross-link-registry.json` |

For the full V5a layout contract and phased implementation plan, see [release-tree-contract.md](release-tree-contract.md) and the source plan at `docs/plans/v12/public-distribution-mirror-plan-2026-03-15-V5a.md`.

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
