# AI Summary Feature Specification — v12 (AI-V1)

Status: **Implemented**
Pipeline version: v12
Owner: openwrt-docs4ai

---

## 1. Overview

The AI Summary feature (AI-V1) enriches every L2 documentation file in the
openwrt-docs4ai corpus with three structured fields:

| Field | Description |
|-------|-------------|
| `ai_summary` | 3-5 sentence technical description; sentence 1 is comprehensive, remaining sentences add details |
| `ai_when_to_use` | 1–2 sentences describing a concrete OpenWrt use case |
| `ai_related_topics` | Array of exact symbol names related to the page |

These fields are injected into the YAML frontmatter of L2 files by
**script 04** and then propagated downstream into LLM routing indexes,
agent AGENTS.md files, and web search interfaces.

The feature is **optional** — the pipeline runs cleanly with `SKIP_AI=true` and
downstream scripts fall back gracefully when AI fields are absent.

---

## 2. Data Store Design

### 2.1 Directory layout

```
data/
  base/
    README.md               ← JSON schema + manual generation prompt
    <module>/
      <slug>.json           ← one file per L2 document
  override/
    README.md               ← override workflow docs
    .gitkeep
    <module>/               ← created on demand when an override is needed
      <slug>.json
```

The `<slug>` is the L2 filename without the `.md` extension.

### 2.2 JSON schema

```json
{
  "slug":              "<L2 filename without .md>",
  "module":            "<module name>",
  "title":             "<L2 title field>",
  "content_hash":      "<sha256[:12] of L2 body | null>",
  "ai_summary":        "<3-5 sentences: sentence 1 comprehensive, sentence 2+ details>",
  "ai_when_to_use":    "<1–2 sentences: specific OpenWrt use case>",
  "ai_related_topics": ["<exact symbol name>", "..."],
  "generated_at":      "<ISO 8601>",
  "model":             "<model string — see §2.4>",
  "pipeline_version":  "v12",
  "saved_at":          "<ISO 8601 written by persistence layer>"
}
```

### 2.2.1 Field rationale

| Field | Required in AI-V1 | Purpose in AI-V1 | Reason to keep for AI-V2 |
|-------|-------------------|------------------|---------------------------|
| `slug` | Yes | Deterministic key matching L2 filename. | Rename migrations and cross-index joins. |
| `module` | Yes | Store partitioning and disambiguation. | Module-level model policies and quotas. |
| `title` | Yes | Human review readability and sanity check. | Search/UI display and ranking metadata. |
| `content_hash` | Yes | Staleness detection (`null` for human-pinned). | Drift telemetry and stale dashboards. |
| `ai_summary` | Yes | Primary retrieval synopsis used downstream. | Quality scoring, localization variants. |
| `ai_when_to_use` | Yes | Intent routing hint for agents/LLMs. | Task-conditioned retrieval weighting. |
| `ai_related_topics` | Yes | Symbol adjacency hints for exploration. | Graph-based retrieval and related-doc expansion. |
| `generated_at` | Yes | Provenance timestamp of authoring/generation event. | Freshness policy and scheduled regeneration. |
| `model` | Yes | Provenance source (`manual`, API, migration, seed). | Per-model quality analytics. |
| `pipeline_version` | Yes | Schema/logic compatibility marker. | Versioned migrations for breaking changes. |
| `saved_at` | Auto | Last persistence time from store layer. | Conflict resolution and reconciliation logic. |

### 2.3 `content_hash` semantics

| Value | Meaning |
|-------|---------|
| `"sha256[:12]"` | Pipeline-generated. Declared stale if it no longer matches the current L2 body hash. |
| `null` | Human-authored. Always valid; the pipeline never auto-invalidates or auto-regenerates it. |

Staleness is detected at apply time (script 04 computes `sha256[:12]` of the
L2 body and compares to the stored hash).

### 2.4 Model strings

| Value | Meaning |
|-------|---------|
| `"gpt-4o-mini"` | Live API call via GitHub Models |
| `"github-copilot-seeded"` | Written by GitHub Copilot during initial data store seeding |
| `"migrated-from-legacy-cache"` | Migrated from the legacy `ai-summaries-cache.json` |
| `"manual"` | Human-authored directly in the JSON file |
| `"manual-override"` | Human-authored override cloned from base |

### 2.5 Resolution order at apply time

Script 04 resolves each slug in this order:

```
data/override/<module>/<slug>.json   ← 1st: override always wins
  ↓ not found
data/base/<module>/<slug>.json       ← 2nd: pipeline-managed base
  ↓ not found or stale + WRITE_AI=true
legacy ai-summaries-cache.json       ← 3rd: migrate on hash match
  ↓ not found or WRITE_AI=false
GitHub Models API (gpt-4o-mini)      ← 4th: generate live
  ↓ WRITE_AI=false or MAX_AI_FILES reached or quota
skipped (L2 file left unenriched)
```

---

## 3. Library: `lib/ai_store.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_summary` | `(module, slug, current_hash=None) → (status, data)` | Returns `("ok", data)`, `("stale", data)`, or `(None, None)`. Checks override before base. Hash check skipped when stored hash is null. |
| `save_summary` | `(module, slug, summary_data, to_override=False)` | Writes JSON to base (default) or override. Adds `saved_at` timestamp. |
| `create_override_from_base` | `(module, slug)` | Copies `data/base/…` → `data/override/…` with `content_hash` set to null and `model=manual-override`. Returns `False` if base is missing or override already exists. |
| `list_all` | `(store="base") → [(module, slug, data)]` | Lists all JSON records in base or override. |
| `stats` | `() → (base_count, override_count)` | Returns count of JSON files in each store. |

Config values added to `lib/config.py`:

```python
_REPO_ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_DATA_BASE_DIR  = os.environ.get("AI_DATA_BASE_DIR",
                        os.path.join(_REPO_ROOT, "data", "base"))
AI_DATA_OVERRIDE_DIR = os.environ.get("AI_DATA_OVERRIDE_DIR",
                        os.path.join(_REPO_ROOT, "data", "override"))
```

---

## 4. Script 04 Behaviour

### 4.1 Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKIP_AI` | `true` for direct script execution | Skip the entire step; exit 0. Hosted workflow and manual dispatch set this explicitly. |
| `WRITE_AI` | `true` | `false` = apply stored summaries only, never call the API. Useful for local preview. |
| `MAX_AI_FILES` | `40` | Maximum number of live API calls per run. Prevents runaway quota spend. |
| `GITHUB_TOKEN` | — | GitHub Models API bearer token. |
| `LOCAL_DEV_TOKEN` | — | Fallback token for local development. |
| `AI_CACHE_PATH` | `ai-summaries-cache.json` | Optional override path for legacy hash cache migration input. |
| `AI_DATA_BASE_DIR` | `data/base/` | Override base store path. |
| `AI_DATA_OVERRIDE_DIR` | `data/override/` | Override override store path. |
| `AI_VALIDATE_PAYLOAD` | `true` | Reject empty or unsafe payloads before injecting AI fields into L2. |

### 4.2 Counter output

Example output:
```
[04] Complete: 142 enriched (3 API-generated, 6 migrated from legacy cache,
               0 applied stale), 0 already had summaries, 2 too short.
[04] Data store: 39 base records, 0 override records.
```

### 4.3 Legacy migration

On startup, script 04 loads `ai-summaries-cache.json` (the legacy flat hash-keyed
cache). When processing an L2 file whose body hash matches a legacy entry, the
script migrates that entry to `data/base/<module>/<slug>.json` automatically with
`model = "migrated-from-legacy-cache"`. The legacy file is left in place and will
shrink to zero active lookups over time.

### 4.4 Stale handling

If a stored entry's `content_hash` no longer matches the current L2 body and
`WRITE_AI=true`, the script will call the API to regenerate the summary and
overwrite the base store entry. If `WRITE_AI=false`, the stale entry is applied
anyway with `stale_applied` counter incremented and a log warning.

### 4.5 Manual prompt contract

Manual seeding prompts in script 04 and `data/base/README.md` follow this rule:

- `ai_summary` sentence 1 must be a comprehensive one-sentence overview.
- `ai_summary` sentences 2+ must add concrete implementation details and clarifications.
- `ai_related_topics` must contain exact symbols from the source text (no hallucinated names).

This structure improves routing quality because sentence 1 serves as a dense
high-level retrieval snippet while later sentences preserve low-level details
for tool/action planning.

### 4.6 Store-write safety and local support tooling

When script `04` writes new base records, it now:

- preserves the L2 `title` field instead of falling back to the slug
- auto-writes `generated_at` when the caller does not provide it
- rejects payloads that omit `ai_related_topics`

Script `04` now performs a library-backed AI-store preflight before it applies
or generates summaries:

- schema and integrity validation for the selected base and override roots
- coverage and hygiene audit reporting for current, pinned, stale, missing,
  orphaned, and invalid records
- hard failure on malformed store state or unreadable L2 inputs, while missing
  or stale coverage remains informational because AI enrichment is optional

The maintained scratch-first support CLI is:

- `tools/manage_ai_store.py` with `--option review`, `--option promote`,
  `--option full`, and focused sub-operations (`prepare`, `generate`,
  `validate`, `audit`, `cleanup`)

The permanent scratch-first workflow for these tools is documented in
[ai-summary-operations-runbook.md](./ai-summary-operations-runbook.md).

### 4.7 Hosted AI stage contract

The hosted `process` job now exposes only one numbered AI stage: `04`.

After `03-normalize-semantic.py`, script `04` performs its own preflight against
the configured AI store and staged L2 corpus before it applies stored summaries
or attempts live API generation.

This keeps the hosted pipeline surface consistent with the numbering contract:
numbered scripts are real pipeline stages, while local review and promotion
workflows live in non-numbered support tooling.

---

## 5. Override Workflow

To customise an AI summary without modifying the pipeline-owned base store:

1. **Create the override** (Python):
   ```python
   from lib.ai_store import create_override_from_base
   create_override_from_base("ucode", "c_source-api-module-uloop")
   ```
   Or manually copy `data/base/<module>/<slug>.json` → `data/override/<module>/<slug>.json`
   and set `"content_hash": null`.

2. **Edit** the override file: update `ai_summary`, `ai_when_to_use`,
   `ai_related_topics`, and set `"model": "manual"`.

3. **Commit** the override file. Pipeline runs will pick it up immediately because
   override resolution happens before base lookup.

Overrides are **never** auto-promoted to base. To propagate a human edit back to
base, copy it manually and set an appropriate model string.

---

## 6. Seed Data

Script 04 ships with a curated, high-value pre-seeded subset of base JSON files
(not the full L2 corpus). The seeded files use `"model": "github-copilot-seeded"`.

| Module | Seeded files |
|--------|-------------|
| `ucode` | 14 (all C source module docs) |
| `procd` | 1 (header API doc) |
| `uci` | 1 (network QoS schema doc) |
| `luci` | 10 (JS framework, CBI, form, UI, UCI, fs, firewall, protocol-static, tools-prng, tools-widgets) |
| `openwrt-hotplug` | 1 (netifd hotplug events) |
| `wiki` | 12 (key techref and developer guide pages) |

Total: **39 seeded records** at AI-V1 release.

---

## 7. Downstream Consumers of AI Fields

| Script | Consumes | How |
|--------|----------|-----|
| `05a-assemble-references.py` | `ai_summary`, `ai_when_to_use` | Written into module skeleton callouts (`Summary`, `Use Case`) |
| `05c-generate-ucode-ide-schemas.py` | `ai_summary` (fallback) | Uses `ai_summary` or `description` for generated declaration comments |
| `06-generate-llm-routing-indexes.py` | `ai_summary` (fallback) | Uses `ai_summary` or `description` for `llms*.txt` entry snippets |
| `07-generate-web-index.py` | indirect (`ai_summary` via `llms.txt`) | Displays snippets already composed by script 06 |

Notes:

- `05b-generate-agents-and-readme.py` does not currently parse `ai_*` fields directly.
- `08-validate-output.py` does not currently enforce AI-field presence checks.

---

## 8. Local Development Workflow

Real AI-summary generation is scratch first. Use
[ai-summary-operations-runbook.md](./ai-summary-operations-runbook.md) for the
whole-project workflow, including validation, promotion, and cleanup.

The preferred whole-project helper is:

```powershell
python tools/manage_ai_store.py --option review
python tools/manage_ai_store.py --option promote
```

The direct commands below are intentionally scoped fallback runs, not the
recommended promotion workflow.

```powershell
# Apply stored summaries only (no API calls):
$env:SKIP_AI="false"
$env:WRITE_AI="false"
python .github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py

# Apply stored + generate up to 5 new ones via API:
$env:SKIP_AI="false"
$env:WRITE_AI="true"
$env:MAX_AI_FILES="5"
$env:LOCAL_DEV_TOKEN="<your token>"
python .github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py

# Skip entirely:
$env:SKIP_AI="true"
python .github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py

# Validate and audit the prepared scratch store:
python tools/manage_ai_store.py --option validate
python tools/manage_ai_store.py --option audit
```

---

## 9. AI-V2 Ideas (Future Work)

The following enhancements are deferred to AI-V2:

- **Multi-model support**: allow per-module model overrides (e.g. use Claude for wiki pages)
- **Auto-promote overrides**: detect when a human override diverges significantly from a
  newly regenerated base entry and surface it for review rather than silently discarding
- **Batch API mode**: group multiple short docs into one API call to reduce round trips
- **Incremental/hash-diff mode**: target only changed L2 documents instead of reviewing the full corpus every time
- **Summary quality scoring**: use a second LLM call to self-evaluate summary quality and
  flag entries below a threshold for human review
- **Localisation**: generate summaries in multiple languages for non-English deployments
