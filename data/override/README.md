# data/override — AI Summary Override Store

This directory holds human-curated overrides for AI summaries.
Any file placed here takes precedence over the matching `data/base/` entry
when script 04 applies summaries to L2 documents.

## Purpose

Use overrides when you want to:

- Replace a pipeline-generated summary with a hand-crafted one
- Correct factual errors in an AI-generated summary
- Permanently pin a summary so it is never auto-regenerated (set `content_hash: null`)

Overrides are **never** automatically promoted back to `data/base/`.
The base store is owned by the pipeline; this directory is owned by humans.

## Layout

```
data/override/
  <module>/
    <slug>.json    ← mirrors data/base/ structure exactly
```

## Creating an Override

### Option A — From the pipeline helper

In a Python script or REPL:

```python
from lib.ai_store import create_override_from_base
create_override_from_base("ucode", "c_source-api-module-uloop")
# → copies data/base/ucode/c_source-api-module-uloop.json
#   to data/override/ucode/c_source-api-module-uloop.json
#   with content_hash set to null (pins it as human-authored)
```

Then open `data/override/ucode/c_source-api-module-uloop.json` in your editor and
modify the `ai_summary`, `ai_when_to_use`, or `ai_related_topics` fields.

### Option B — Manual copy

```
cp data/base/<module>/<slug>.json data/override/<module>/<slug>.json
```

Then set `"content_hash": null` in the copied file so it is treated as human-authored
and is never invalidated by a content hash change.

## Override Resolution Order (script 04)

```
data/override/<module>/<slug>.json   ← checked first
  ↓ not found
data/base/<module>/<slug>.json       ← checked second
  ↓ not found
legacy ai-summaries-cache.json       ← migrated on first match
  ↓ not found or WRITE_AI=false
API call (gpt-4o-mini)               ← generated live
  ↓ WRITE_AI=false or MAX_AI_FILES reached
skipped
```

## JSON Schema

The override file uses the same schema as `data/base/`.
Set `"model": "manual"` for hand-written overrides.
Set `"content_hash": null` to prevent staleness checks.

See [data/base/README.md](../base/README.md) for the full schema reference.

## Notes

- This directory is intentionally kept nearly empty in the repo.
  The `.gitkeep` file ensures the directory is tracked by git.
- Override files **are** committed to the repo — they represent intentional
  human decisions that should be versioned.
- If you delete an override, the pipeline will fall back to the base store entry
  (or regenerate via API if base is also missing).
- For whole-project scratch generation and safe promotion into `data/base/`, use
  [docs/specs/v12/ai-summary-operations-runbook.md](../../docs/specs/v12/ai-summary-operations-runbook.md).
