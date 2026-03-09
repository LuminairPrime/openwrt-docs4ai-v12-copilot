# openwrt-docs4ai v12 Execution Map

## Layer Locations

- `L0`: `tmp/repo-*`
- `L1`: `tmp/L1-raw/{module}/` during build, optionally copied to `openwrt-condensed-docs/L1-raw/{module}/`
- `L2`: `tmp/L2-semantic/{module}/` during build, optionally copied to `openwrt-condensed-docs/L2-semantic/{module}/`
- `L3`: `openwrt-condensed-docs/` root and per-module subdirectories
- `L4`: `openwrt-condensed-docs/{module}/`
- `L5`: `openwrt-condensed-docs/`

## Ordered Script Flow

1. `01-clone-repos.py`
2. `02a` through `02h`
3. `03-normalize-semantic.py`
4. `04-generate-ai-summaries.py` when AI enrichment is enabled
5. `05-assemble-references.py`
6. `06a-generate-llms-txt.py`
7. `06b-generate-agents-md.py`
8. `06c-generate-ide-schemas.py`
9. `06d-generate-changelog.py`
10. `07-generate-index-html.py`
11. `08-validate.py`

Letter suffixes denote scripts that are parallelizable in deployment. Local smoke tests may still execute them sequentially.

## Key Handoffs

- `01` produces cloned repositories and any repo manifest data required by downstream stages.
- `02*` scripts write L1 markdown plus `.meta.json` sidecars.
- `03` reads only L1 plus metadata and writes L2 plus a cross-link registry before promoting stable intermediates into `OUTDIR`.
- `04` mutates staged L2 files in place when enabled.
- `05` consumes staged L2 files and emits skeletons plus monolithic references.
- `06*` scripts consume staged L2 metadata and generated references to emit maps, agent instructions, IDE schemas, and telemetry.
- `07` consumes the map outputs and writes the HTML landing page.
- `08` validates the full `OUTDIR` tree.

## Required Environment Variables

- `WORKDIR`
- `OUTDIR`
- `SKIP_WIKI`
- `SKIP_AI`
- `WIKI_MAX_PAGES`
- `MAX_AI_FILES`
- `VALIDATE_MODE`

## Required Schema Facts

- L1 files are pure markdown and must not begin with YAML frontmatter.
- L1 sidecars are `.meta.json` files stored beside the markdown file.
- L2 files require YAML frontmatter with at least `title`, `module`, `origin_type`, `token_count`, and `version`.
- L4 files use one top-level YAML block for the full monolith rather than reusing L2 frontmatter inline.

## Local Verification Priority

The first verified execution path is local and sequential. GitHub Actions behavior is an additional future verification layer and is not assumed by this execution map.
