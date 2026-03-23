# Regeneration Rules

**Version:** V13  
**Status:** Active

Defines trigger rules, overlay behavior, and module lifecycle events that govern when the pipeline regenerates output.

---

## Trigger Categories

### Full Pipeline Run

Triggered by:
- Push to `main` branch of this repository (full CI run)
- Manual workflow dispatch with no stage restriction
- Scheduled weekly run (CRON)

A full run executes all stages 01 → 08 in order.

### Partial Rerun (Stage Targeting)

The pipeline supports `workflow_dispatch` with a `start_stage` input. Any stage from `02a` onward may be selected as the start point. All stages from `start_stage` onward run; stages before it are skipped.

**Safety constraint:** Partial reruns assume earlier-stage artifacts are valid in the working directory. Never use partial rerun after a WORKDIR flush.

### Overlay-Only Regeneration

Trigger when only `release-inputs/` files change (no code or source data change):

1. Rerun `07` (overlay application)
2. Rerun `08` (validation)

No semantic processing stages (03, 04, 05*) need to run.

---

## Overlay System

### What Overlays Are

Overlays are static files in `release-inputs/` that are merged into the pipeline output during stage `07`. They allow source-controlled hand-authored content to appear in the release-tree alongside generated content.

### Overlay Directory Structure

```text
release-inputs/
├── release-include/          Applied to all surfaces (GitHub Pages, release repo, ZIP)
│   ├── README.md             Overrides generated release-tree/README.md (if present)
│   ├── luci/
│   │   └── AGENTS.md         Per-module guidance for luci
│   ├── ucode/
│   │   └── AGENTS.md         Per-module guidance for ucode
│   └── cookbook/
│       └── AGENTS.md         Per-module guidance for cookbook
├── pages-include/            Applied to GitHub Pages surface only
│   └── (reserved for future use)
└── release-repo-include/     Applied to release-repo-only surface
    └── (reserved for future use)
```

### Overlay Merge Rules

| Scenario | Behavior |
|----------|----------|
| Overlay file exists, no generated counterpart | File is copied verbatim |
| Overlay file exists, generated counterpart exists | Overlay file wins; generated counterpart is discarded |
| Generated file exists, no overlay counterpart | Generated file stands |
| Module directory missing in release-tree | Overlay for that module is skipped with a `[07] WARN` log |

**Overlays are always idempotent.** Re-applying the same overlay to the same base state produces the same output.

---

## Module Lifecycle

### Adding a New Module

1. Create the extractor script (e.g. `02i-ingest-cookbook.py`)
2. Add `origin_type` string to `lib/source_provenance.py` constants
3. Register module name in `lib/config.py`:
   - `MODULE_ORDER` list
   - `MODULE_CATEGORIES` dict entry
   - `MODULE_DESCRIPTIONS` dict entry
4. Create `release-inputs/release-include/{module}/AGENTS.md` (if module should have one)
5. Add module to pipeline workflow YAML job matrix or as sibling step
6. Run full pipeline; confirm `08` passes

### Removing a Module

1. Remove extractor script or disable it in workflow
2. Remove module name from `lib/config.py` (all three dicts)
3. Remove or archive `release-inputs/release-include/{module}/` overlay directory
4. Remove any test fixtures referencing the module

### Renaming a Module

Renaming a module (e.g. `uci` → `openwrt-uci`) is a breaking change to the published contract. It requires:
1. A new major version label in `release-tree-contract.md`
2. A redirect entry in `pages-include/` if the Pages surface is affected
3. All consumer `llms.txt` entries for the old name become invalid at the published root

---

## AI Summary Cache Behavior

Stage `04` (`04-generate-ai-summaries.py`) optionally enriches L2 files with AI-generated metadata.

| Condition | Behavior |
|-----------|----------|
| `--run-ai` flag absent | Stage reads cache only; no external API calls |
| `--run-ai` flag present | Stage calls AI API for pages missing cache entries |
| Cache hit | Existing AI summary metadata is reused; no API call |
| Cache miss (`--run-ai` absent) | Page is left without AI enrichment; not an error |
| Cache miss (`--run-ai` present) | AI API is called; result written to `data/base/` AI store |

**Regression proof:** `--run-ai` is always absent in automated regression test runs (`run_smoke.py`, `run_pytest.py`). The cache state from `data/base/` is static test input.

---

## Determinism Contract

All stages 01–08 must be idempotent and deterministic given the same inputs:

- Running the same stage twice in a row must produce byte-for-byte identical output (modulo `extraction_timestamp` fields, which are expected to update)
- No stage may read state from a previous run unless that state was explicitly written to a defined layer directory (`L1-raw/`, `L2-semantic/`, etc.)
- Timestamps in output files use ISO 8601 UTC; stage run timestamps are acceptable sources of non-determinism and are not covered by the determinism contract
