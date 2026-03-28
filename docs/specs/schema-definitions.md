# openwrt-docs4ai Schema Definitions

## Purpose

This document defines the active filesystem and data contracts for the current pipeline. It focuses on layer boundaries, sidecar and frontmatter fields, and the published routing surfaces. For the public layout contract, use [release-tree-contract.md](release-tree-contract.md). For canonical field names and terminology, use [glossary-and-naming-contract.md](glossary-and-naming-contract.md).

## Top-Level Paths

| Path | Role |
| --- | --- |
| `docs/` | Maintainer documentation only |
| `content/cookbook-source/` | Hand-authored cookbook source |
| `release-inputs/` | Overlay inputs for final publication |
| `tmp/` | Ephemeral local working area |
| `staging/` | Default local generated output root (gitignored) |
| `staging/release-tree/` | Local representation of the public output contract |
| `staging/support-tree/` | Internal support and telemetry outputs |

`WORKDIR` is ephemeral. Locally it defaults to `tmp/`. In hosted workflow runs it is set to `${{ github.workspace }}/tmp`.

`OUTDIR` is the output root for a run. It always defaults to `staging/`. Tests read from `staging/` to validate fresh pipeline output. The source repository does not track generated output.

## Documentation Boundary

The source repository and the generated corpus are separate contract surfaces:

- The source repository is the maintainer and implementation surface. Its authoritative docs live in `README.md`, `DEVELOPMENT.md`, `CLAUDE.md`, and the active files under `docs/`.
- The generated corpus under `OUTDIR/release-tree/` is the published navigation surface for humans, tools, and LLMs. Locally it generates into `staging/` (gitignored); externally it is published to distribution targets.

## Layer Contracts

| Layer | Location | Contract |
| --- | --- | --- |
| `L0` | `WORKDIR/repo-*` | Upstream clones and fetched inputs; never published |
| `L1` | `WORKDIR/L1-raw/{module}/` | Raw normalized Markdown plus `.meta.json` sidecars |
| `L2` | `OUTDIR/L2-semantic/{module}/` | Semantic Markdown with YAML frontmatter and cross-links |
| `L3/L4` | `OUTDIR/release-tree/` | Published routing, reference, and IDE surfaces |
| `L5` | `OUTDIR/support-tree/telemetry/` | Internal telemetry and drift outputs |

## L1 Sidecar Contract

Every L1 Markdown file has a same-stem `.meta.json` sidecar.

| Field | Required | Notes |
| --- | --- | --- |
| `extractor` | Yes | Stage identifier such as `02a-scrape-wiki` |
| `origin_type` | Yes | Canonical value from the glossary contract |
| `module` | Yes | Canonical module name |
| `slug` | Yes | File stem without `.md` |
| `source_url` | Yes | Full upstream URL or `null` for authored cookbook content |
| `source_locator` | Conditional | Relative path within a git-backed source repository |
| `source_commit` | Conditional | Upstream commit SHA for git-backed content |
| `language` | Yes | Typically `en` |
| `fetch_status` | Yes | `ok` or a failure reason |
| `extraction_timestamp` | Yes | ISO 8601 UTC timestamp |
| `content_hash` | Yes | SHA-256 hex digest of normalized content |

`source_locator` and `source_commit` are required for git-backed origin types and omitted for `wiki_page` and `authored` content.

## L2 Frontmatter Contract

Every L2 file is Markdown with one YAML frontmatter block.

| Field | Required | Notes |
| --- | --- | --- |
| `title` | Yes | Human-readable page title |
| `module` | Yes | Canonical module name |
| `origin_type` | Yes | Same canonical origin type used in L1 |
| `token_count` | Yes | Approximate body token count |
| `source_commit` | Conditional | Required for git-backed origin types |
| `source_url` | Optional | Carried through when present |
| `source_locator` | Optional | Carried through when present |
| `routing_summary` | Optional | Short routing summary |
| `routing_keywords` | Optional | Routing keyword list |
| `routing_priority` | Optional | `high`, `medium`, or `low` |
| `era_status` | Optional | `current`, `legacy`, `deprecated`, or authored cookbook status values |
| `audience_hint` | Optional | `developer`, `operator`, or `both` |

### AI Summary Fields

Stage `04` may also inject these optional fields into L2 frontmatter:

| Field | Notes |
| --- | --- |
| `ai_summary` | Structured technical summary |
| `ai_when_to_use` | Use-case hint |
| `ai_related_topics` | Related symbol or topic list |

## Stale Field Names

These older names are not valid for new output and should only appear in archived material or validator warnings.

| Stale name | Replacement |
| --- | --- |
| `version` | `source_commit` |
| `upstream_path` | `source_locator` |
| `original_url` | `source_url` |

## Published Routing Surfaces

| Path | Role |
| --- | --- |
| `release-tree/llms.txt` | Root routing index |
| `release-tree/llms-full.txt` | Full flat routing catalog |
| `release-tree/AGENTS.md` | Root agent navigation guide |
| `release-tree/README.md` | Root human-readable introduction |
| `release-tree/index.html` | Web landing page |
| `release-tree/{module}/llms.txt` | Module routing index |
| `release-tree/{module}/map.md` | Module navigation map |
| `release-tree/{module}/bundled-reference.md` | Module bundled reference or part index |
| `release-tree/{module}/chunked-reference/{topic}.md` | Published topic pages |
| `release-tree/{module}/types/*.d.ts` | Optional IDE declarations |

Use [release-tree-contract.md](release-tree-contract.md) for the full public layout and gatekeeper rules.

## Guaranteed Non-Public Material

These items are internal only and must not appear in the published `release-tree/` surface:

- `L1-raw/`
- `L2-semantic/`
- `support-tree/`
- `.meta.json` sidecars
- telemetry files such as `changelog.json`, `CHANGES.md`, and `signature-inventory.json`
- internal manifest files such as `repo-manifest.json` and `cross-link-registry.json`

## Related Contracts

- [release-tree-contract.md](release-tree-contract.md)
- [pipeline-stage-catalog.md](pipeline-stage-catalog.md)
- [script-dependency-map.md](script-dependency-map.md)
- [glossary-and-naming-contract.md](glossary-and-naming-contract.md)