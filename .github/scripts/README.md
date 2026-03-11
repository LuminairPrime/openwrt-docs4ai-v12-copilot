# .github/scripts — Pipeline Scripts Reference

This directory contains all openwrt-docs4ai pipeline scripts.
Scripts are numbered 01–08 and run in order from acquisition through validation.

See [docs/specs/v12/script-dependency-map.md](../../docs/specs/v12/script-dependency-map.md)
for the full dependency graph, input/output tables, and AI data flow diagram.

---

## Quick Reference

| Script | Phase | Layer | Parallelisable | AI data |
|--------|-------|-------|----------------|---------|
| `01-clone-repos` | Acquisition | L0 | No | — |
| `02a-scrape-wiki` | Extraction | L0→L1 | Yes | — |
| `02b-scrape-ucode` | Extraction | L0→L1 | Yes | — |
| `02c-scrape-jsdoc` | Extraction | L0→L1 | Yes | — |
| `02d-scrape-core-packages` | Extraction | L0→L1 | Yes | — |
| `02e-scrape-example-packages` | Extraction | L0→L1 | Yes | — |
| `02f-scrape-procd-api` | Extraction | L0→L1 | Yes | — |
| `02g-scrape-uci-schemas` | Extraction | L0→L1 | Yes | — |
| `02h-scrape-hotplug-events` | Extraction | L0→L1 | Yes | — |
| `03-normalize-semantic` | Process | L1→L2 | No | — |
| `04-generate-ai-summaries` | AI Enrichment | L2→L2 | No | **Writes** base store |
| `05a-assemble-references` | Assembly | L2→L3/L4 | Yes | Reads AI fields |
| `05b-generate-agents-and-readme` | Indexing | L3 | Yes | Reads AI fields |
| `05c-generate-ucode-ide-schemas` | Indexing | L3 | Yes | — |
| `05d-generate-api-drift-changelog` | Telemetry | L5 | Yes | — |
| `06-generate-llm-routing-indexes` | Aggregation | L4→L3 | No | Reads AI fields |
| `07-generate-web-index` | Presentation | L3 | No | Reads AI fields |
| `08-validate-output` | Validation | L1–L5 | No | Reads AI fields |

---

## Common Environment Variables

| Variable | Default | Used by |
|----------|---------|---------|
| `WORKDIR` | `./tmp` | 01, 02*, 03, 06 |
| `OUTDIR` | `./staging` | 03, 04, 05*, 06, 07, 08 |
| `SKIP_WIKI` | `false` | 02a |
| `WIKI_MAX_PAGES` | (all) | 02a |
| `SKIP_BUILDROOT` | `false` | 01, 02d, 02e |
| `SKIP_AI` | `false` | 04 |
| `WRITE_AI` | `true` | 04 |
| `MAX_AI_FILES` | `40` | 04 |
| `GITHUB_TOKEN` | — | 04 |
| `LOCAL_DEV_TOKEN` | — | 04 |
| `AI_CACHE_PATH` | `ai-summaries-cache.json` | 04 |
| `AI_DATA_BASE_DIR` | `data/base/` | 04 |
| `AI_DATA_OVERRIDE_DIR` | `data/override/` | 04 |
| `VALIDATE_MODE` | `hard` | 08 |
| `OPENWRT_COMMIT` | (set by 01) | 03, 06 |
| `LUCI_COMMIT` | (set by 01) | 03, 06 |
| `UCODE_COMMIT` | (set by 01) | 03, 06 |

---

## Shared Libraries

All scripts import from `lib/` (two directories up):

```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config          # all scripts
from lib import extractor       # 02a–02h
from lib import ai_store        # 04 only
```

| Library | File | Description |
|---------|------|-------------|
| `config` | `lib/config.py` | Shared paths: OUTDIR, WORKDIR, L1/L2 dirs, AI data dirs |
| `extractor` | `lib/extractor.py` | L1 source extraction helpers (frontmatter normalisation, meta writing) |
| `ai_store` | `lib/ai_store.py` | AI summary data store: load, save, override resolution, legacy migration |

---

## AI Summary Feature (Script 04)

Script 04 implements the AI-V1 data store design:

- Reads pre-seeded JSON from `data/base/<module>/<slug>.json`
- Allows human overrides in `data/override/<module>/<slug>.json`
- Falls back to legacy `ai-summaries-cache.json` and migrates entries on first match
- Calls GitHub Models API (gpt-4o-mini) for files with no stored summary when `WRITE_AI=true`
- Injects `ai_summary`, `ai_when_to_use`, `ai_related_topics` into L2 YAML frontmatter

Full design: [docs/specs/v12/ai-summary-feature-spec.md](../../docs/specs/v12/ai-summary-feature-spec.md)

---

## Adding a New Script

1. Name it `openwrt-docs4ai-NN-descriptive-name.py`
2. Add a module-level docstring with Purpose, Phase, Layers, Inputs, Outputs, Environment Variables, Dependencies, Notes
3. Import `lib.config` for all path constants — never hardcode `tmp/` or `staging/` directly
4. Add it to the GitHub Actions workflow YAML in `.github/workflows/`
5. Update [docs/specs/v12/script-dependency-map.md](../../docs/specs/v12/script-dependency-map.md) with its
   input/output tables and AI data column
6. Update the quick reference table in this README
