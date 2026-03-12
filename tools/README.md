# tools — Local Support Utilities

This directory holds non-numbered maintainer tools.

The numbering contract for this repository is strict:

- numbered files under `.github/scripts/` are real pipeline stages
- a bare stage id such as `04` cannot coexist with `04a`, `04b`, or other same-family siblings
- local support tools that are not part of the hosted numbered pipeline belong here instead

## Current Tooling

| Tool | Purpose |
| --- | --- |
| `manage_ai_store.py` | Scratch-first AI summary review, validation, audit, promotion, and cleanup |

## AI Store Workflow

Use `manage_ai_store.py` for local AI-summary work that should not change the
hosted numbered pipeline surface.

```powershell
python tools/manage_ai_store.py --option review
python tools/manage_ai_store.py --option promote
python tools/manage_ai_store.py --option full --keep-scratch --max-ai-files 300
```

The CLI reuses the shared AI helper libraries in `lib/`:

- `lib/ai_enrichment.py`
- `lib/ai_store_checks.py`
- `lib/ai_store_workflow.py`

See `docs/specs/v12/ai-summary-operations-runbook.md` for the durable operator
workflow and fallback procedures.