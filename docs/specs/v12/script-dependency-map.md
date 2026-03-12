# Script Dependency Map — openwrt-docs4ai v12

This document maps every pipeline script: what it consumes, what it produces,
which scripts it depends on, and whether it touches AI summary data.

---

## Pipeline Overview

```
01-clone-repos          (L0 source acquisition)
  ├──▶ 02b..02h-scrape-*  (repo-backed L0 → L1 extraction)
  │
  └──────────────┐
                 │
02a-scrape-wiki  │        (wiki L0 → L1 extraction; independent branch)
    └──────────────┴──▶ 03-normalize-semantic   (L1 → L2 + staging promotion)
  ↓
04-generate-ai-summaries  (L2 → L2 AI enrichment, optional)
  ↓
  ╔════════════════════════════════════╗
  ║  05a assemble-references          ║  (L2 → L3/L4, parallelisable group)
  ║  05b generate-agents-and-readme   ║
  ║  05c generate-ucode-ide-schemas   ║
  ║  05d generate-api-drift-changelog ║
  ╚════════════════════════════════════╝
  ↓
06-generate-llm-routing-indexes  (L4 → L3 indexes)
  ↓
07-generate-web-index            (L3 → presentation)
  ↓
08-validate-output               (gatekeeper; reads all layers)
```

Hosted workflow execution uses Option B wiring: `02a` runs in its own job without waiting on `01`, while `02b` through `02h` remain gated on `01` because they require cloned repos.

Extractor diagnostics are also now explicit in workflow: per-extractor status manifests, fail-fast disabled for the repo-backed matrix, and an always-generated extract summary artifact.

The hosted workflow now exposes only the numbered `04` AI stage. Local
scratch-first review, validation, audit, and promotion live in
`tools/manage_ai_store.py`.

---

## Per-Script Detail

### `01-clone-repos.py`

| Attribute | Value |
|-----------|-------|
| Phase | Acquisition |
| Layer | L0 |
| Reads | GitHub (jow-/ucode, openwrt/luci, openwrt/openwrt) |
| Writes | `tmp/repo-ucode/`, `tmp/repo-luci/`, `tmp/repo-openwrt/` |
| Depends on | — |
| Depended on by | 02b, 02c, 02d, 02e, 02f, 02g, 02h |
| AI data | None |
| Parallelisable | In practice yes with 02a branch in hosted workflow; remains the serial prerequisite for 02b..02h |
| Key env vars | `WORKDIR`, `SKIP_BUILDROOT` |

---

### `02a-scrape-wiki.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | https://openwrt.org/docs/ (live HTTP) |
| Writes | `tmp/L1-raw/wiki/*.md`, `*.meta.json` |
| Depends on | None (network; no local repo needed) |
| Depended on by | 03 |
| AI data | None |
| Parallelisable | Yes (independent of other 02* scripts) |
| Key env vars | `WORKDIR`, `SKIP_WIKI`, `WIKI_MAX_PAGES` |

---

### `02b-scrape-ucode.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | `tmp/repo-ucode/docs/`, `tmp/repo-ucode/lib/*.c` |
| Writes | `tmp/L1-raw/ucode/*.md`, `*.meta.json` |
| Depends on | 01 |
| Depended on by | 03 |
| AI data | None directly (this module has 14 seeded files in `data/base/ucode/`) |
| Parallelisable | Yes |
| Key env vars | `WORKDIR` |

---

### `02c-scrape-jsdoc.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | `tmp/repo-luci/modules/luci-base/htdocs/luci-static/resources/*.js` |
| Writes | `tmp/L1-raw/luci/*.md`, `*.meta.json` |
| Depends on | 01 |
| Depended on by | 03 |
| AI data | None directly (this module has 10 seeded files in `data/base/luci/`) |
| Parallelisable | Yes |
| Key env vars | `WORKDIR` |

---

### `02d-scrape-core-packages.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | `tmp/repo-openwrt/package/`, `include/` |
| Writes | `tmp/L1-raw/openwrt-core/*.md`, `*.meta.json` |
| Depends on | 01 (openwrt repo, full or sparse) |
| Depended on by | 03 |
| AI data | None seeded at AI-V1 |
| Parallelisable | Yes |
| Key env vars | `WORKDIR`, `SKIP_BUILDROOT` |

---

### `02e-scrape-example-packages.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | `tmp/repo-luci/applications/` (4 curated apps) |
| Writes | `tmp/L1-raw/luci-examples/*.md`, `*.meta.json` |
| Depends on | 01 |
| Depended on by | 03 |
| AI data | None seeded at AI-V1 |
| Parallelisable | Yes |
| Key env vars | `WORKDIR`, `SKIP_BUILDROOT` |

---

### `02f-scrape-procd-api.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | `tmp/repo-openwrt/package/system/procd/files/procd.sh` |
| Writes | `tmp/L1-raw/procd/header_api-procd-api.md`, `*.meta.json` |
| Depends on | 01 |
| Depended on by | 03 |
| AI data | None directly (this module has 1 seeded file in `data/base/procd/`) |
| Parallelisable | Yes |
| Key env vars | `WORKDIR` |

---

### `02g-scrape-uci-schemas.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | `tmp/repo-openwrt/package/**/etc/config/*` |
| Writes | `tmp/L1-raw/uci/*.md`, `*.meta.json` |
| Depends on | 01 |
| Depended on by | 03 |
| AI data | None directly (this module has 1 seeded file in `data/base/uci/`) |
| Parallelisable | Yes |
| Key env vars | `WORKDIR` |

---

### `02h-scrape-hotplug-events.py`

| Attribute | Value |
|-----------|-------|
| Phase | Extraction |
| Layer | L0 → L1 |
| Reads | `tmp/repo-openwrt/package/**/etc/hotplug.d/*` |
| Writes | `tmp/L1-raw/openwrt-hotplug/*.md`, `*.meta.json` |
| Depends on | 01 |
| Depended on by | 03 |
| AI data | None directly (this module has 1 seeded file in `data/base/openwrt-hotplug/`) |
| Parallelisable | Yes |
| Key env vars | `WORKDIR` |

---

### `03-normalize-semantic.py`

| Attribute | Value |
|-----------|-------|
| Phase | Process |
| Layer | L1 → L2 + staging |
| Reads | `tmp/L1-raw/**/*.md` |
| Writes | `staging/L1-raw/`, `staging/L2-semantic/`, `staging/cross-link-registry.json` |
| Depends on | All 02* scripts |
| Depended on by | 04, 05a, 05b, 05c, 05d, 06, 08 |
| AI data | None (produces L2 without AI fields; script 04 adds them) |
| Parallelisable | No (aggregates all 02* outputs; serial) |
| Key env vars | `WORKDIR`, `OUTDIR`, `OPENWRT_COMMIT`, `LUCI_COMMIT`, `UCODE_COMMIT` |

---

### `04-generate-ai-summaries.py` ← **AI WRITER**

| Attribute | Value |
|-----------|-------|
| Phase | AI Enrichment |
| Layer | L2 → L2 (in-place) |
| Reads | `OUTDIR/L2-semantic/**/*.md`, `data/base/**/*.json`, `data/override/**/*.json`, `ai-summaries-cache.json` (legacy) |
| Writes | `OUTDIR/L2-semantic/**/*.md` (adds `ai_*` frontmatter fields), `data/base/**/*.json` (new entries when `WRITE_AI=true`) |
| Depends on | 03 |
| Depended on by | 05a, 05b, 05c, 05d, 06, 07, 08 |
| AI data | **Writes** base store; reads base + override; migrates legacy cache; performs built-in preflight; direct downstream AI-field consumers are 05a, 05c, and 06 |
| Parallelisable | No (serial; API rate-limit aware) |
| Key env vars | `SKIP_AI`, `WRITE_AI`, `MAX_AI_FILES`, `GITHUB_TOKEN`, `LOCAL_DEV_TOKEN`, `AI_CACHE_PATH`, `AI_DATA_BASE_DIR`, `AI_DATA_OVERRIDE_DIR` |
| Library deps | `lib.ai_enrichment`, `lib.ai_store`, `lib.ai_corpus`, `lib.ai_store_checks`, `lib.config`, `requests`, `pyyaml` |

---

### `tools/manage_ai_store.py`

| Attribute | Value |
|-----------|-------|
| Phase | AI Operations |
| Layer | Store + L2 scratch workspace |
| Reads | committed `data/base/`, committed `data/override/`, `OUTDIR/L2-semantic/`, optional token env vars |
| Writes | scratch copies under `tmp/ai-summary-run/`, optional promoted JSON into `data/base/` |
| Depends on | current L2 corpus plus AI store roots |
| Depended on by | local operators |
| AI data | reuses `lib.ai_enrichment`, `lib.ai_store_checks`, and `lib.ai_store_workflow`; promotes reviewed scratch JSON into base |
| Parallelisable | No |
| Key env vars | `OUTDIR`, `AI_DATA_BASE_DIR`, `AI_DATA_OVERRIDE_DIR`, `LOCAL_DEV_TOKEN`, `GITHUB_TOKEN` |

---

### `05a-assemble-references.py`

| Attribute | Value |
|-----------|-------|
| Phase | Assembly |
| Layer | L2 → L3/L4 |
| Reads | `OUTDIR/L2-semantic/**/*.md` (includes AI fields if 04 ran) |
| Writes | `OUTDIR/{module}/{module}-complete-reference.md`, `{module}-skeleton.md` |
| Depends on | 03 (04 recommended but optional) |
| Depended on by | 06, 08 |
| AI data | **Reads** `ai_summary`, `ai_when_to_use` from L2 frontmatter |
| Parallelisable | Yes (independent of 05b, 05c, 05d) |
| Key env vars | `OUTDIR` |

---

### `05b-generate-agents-and-readme.py`

| Attribute | Value |
|-----------|-------|
| Phase | Indexing |
| Layer | L3 |
| Reads | `OUTDIR/L2-semantic/**/*.md`, `OUTDIR/cross-link-registry.json` |
| Writes | `OUTDIR/AGENTS.md`, `OUTDIR/README.md` |
| Depends on | 03 (04 recommended but optional) |
| Depended on by | — (terminal output artefact) |
| AI data | None directly |
| Parallelisable | Yes |
| Key env vars | `OUTDIR` |

---

### `05c-generate-ucode-ide-schemas.py`

| Attribute | Value |
|-----------|-------|
| Phase | Indexing |
| Layer | L3 |
| Reads | `OUTDIR/cross-link-registry.json` |
| Writes | `OUTDIR/ucode/ucode.d.ts` |
| Depends on | 03 |
| Depended on by | — (terminal output artefact) |
| AI data | **Reads** `ai_summary` (fallback to `description`) from registry metadata |
| Parallelisable | Yes |
| Key env vars | `OUTDIR` |

---

### `05d-generate-api-drift-changelog.py`

| Attribute | Value |
|-----------|-------|
| Phase | Telemetry |
| Layer | L5 |
| Reads | `OUTDIR/` (current run), `baseline/signature-inventory.json` |
| Writes | `OUTDIR/changelog.json`, `OUTDIR/CHANGES.md`, `OUTDIR/signature-inventory.json` |
| Depends on | 03 |
| Depended on by | — (terminal output artefact) |
| AI data | None |
| Parallelisable | Yes |
| Key env vars | `OUTDIR` |

---

### `06-generate-llm-routing-indexes.py`

| Attribute | Value |
|-----------|-------|
| Phase | Aggregation / Indexing |
| Layer | L4 → L3 |
| Reads | `OUTDIR/` (L4 references from 05a) |
| Writes | `OUTDIR/llms.txt`, `OUTDIR/llms-full.txt`, `OUTDIR/{module}/llms.txt` |
| Depends on | 05a (04 recommended for richer entries) |
| Depended on by | 07, 08 |
| AI data | **Reads** `ai_summary` (fallback to `description`) for routing snippets |
| Parallelisable | No (depends on 05a output) |
| Key env vars | `OUTDIR`, `OPENWRT_COMMIT`, `LUCI_COMMIT`, `WORKDIR` |

---

### `07-generate-web-index.py`

| Attribute | Value |
|-----------|-------|
| Phase | Presentation |
| Layer | L3 |
| Reads | `OUTDIR/llms.txt` |
| Writes | `OUTDIR/index.html` |
| Depends on | 06 |
| Depended on by | — (terminal output artefact) |
| AI data | Indirect (renders snippets generated by script 06) |
| Parallelisable | No (depends on 06 output) |
| Key env vars | `OUTDIR` |

---

### `08-validate-output.py`

| Attribute | Value |
|-----------|-------|
| Phase | Validation |
| Layer | L1, L2, L3, L4, L5 |
| Reads | `OUTDIR/**` |
| Writes | Validation report to stdout only |
| Depends on | All prior scripts |
| Depended on by | CI gate |
| AI data | None directly |
| Parallelisable | No (must run last) |
| Key env vars | `OUTDIR`, `VALIDATE_MODE` |

---

## AI Data Flow Summary

```
data/base/<module>/<slug>.json   ← seeded by humans / Copilot
data/override/<module>/<slug>.json  ← human overrides
         │
         │  (read + write during enrichment)
         ▼
04-generate-ai-summaries.py
         │
         │  (injects ai_* into L2 frontmatter YAML)
         ▼
OUTDIR/L2-semantic/<module>/<slug>.md
         │
         ├──▶ 05a  (ai_summary, ai_when_to_use in L4 references)
         ├──▶ 05c  (ai_summary fallback in generated declaration comments)
         ├──▶ 06   (ai_summary fallback in llms.txt routing index)
         └──▶ 07   (indirect snippet rendering via 06 output)
```

`04a` and `04b` also read the AI store plus L2 documents. They remain local
maintainer tools, but the hosted `process` job now invokes them as a committed
store gate when a push changes `data/base/` or `data/override/`.

`04c` is the preferred local wrapper for scratch-first review, promotion, and
cleanup.

---

## Libraries

| Library | Used by | Purpose |
|---------|---------|---------|
| `lib/config.py` | All scripts | Shared paths (OUTDIR, WORKDIR, AI_DATA_BASE_DIR, AI_DATA_OVERRIDE_DIR) |
| `lib/extractor.py` | 02a–02h | L1 frontmatter + body extraction helpers |
| `lib/ai_store.py` | 04 | AI summary data store (load, save, override, migrate) |
