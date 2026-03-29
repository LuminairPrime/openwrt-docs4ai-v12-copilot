# pipeline-folder-refactor-04.md

**Status:** Planning — decisions locked, implementation not started  
**Date:** 2026-03-29  
**Supersedes:** pipeline-folder-refactor-03.md (earlier schema proposals)  
**Implements:** schema D/F converged (downloads / processed / staged)

This document is the authoritative planning record for the pipeline workspace
refactor to make the project file system layout more logical and pipeline output less degenerate. 
Earlier plan files (00–03) contain the design history.
Implementation should be driven from this file only.

---

## Locked Schema

Every pipeline run — local or CI — writes to exactly this structure:

```
tmp/
  pipeline-run-state.json              # mutable pointer to most recent local run
  logs/                                # smoke test logs (pre-existing location; unchanged)
    smoke-01-full-local-pipeline-log.txt

  pipeline-20260328-1425UTC-7f3c/      # format: YYYYMMDD-HHMMutc-XXXX (4 random hex chars)
    pipeline-run-record.json           # run state

    downloads/                         # stages 01, 02a — git clones, raw wiki HTML
      .cache/                          # wiki scraper cache (per-run after this refactor; WIKI_CACHE_DIR fix deferred)
        wiki-lastmod.json
      repo-ucode/
      repo-luci/
      repo-openwrt/
      wiki/
        raw/
          OpenWrt_Wiki_Main_Page.html
          UCI_system.html
          Packages.html
          ...

    processed/                         # stages 02x, 03 — L1/L2 normalized layers + manifests
      L1-raw/
        wiki/
        ucode/
        luci/
        openwrt-core/
        cookbook/
      L2-semantic/
        wiki/
        ucode/
        luci/
        openwrt-core/
        cookbook/
      manifests/
        repo-manifest.json
        cross-link-registry.json

    staged/                            # stages 05a–08 — deliverables + diagnostic bundle
      release-tree/                    # the only published surface: corpus, pages, zip
        wiki/
        ucode/
        luci/
        openwrt-core/
        cookbook/
          llms.txt
          map.md
          bundled-reference.md
          chunked-reference/
          types/                       # .d.ts IDE schemas (ucode, luci)
        llms.txt
        llms-full.txt
        AGENTS.md
        README.md
        index.html
      support-tree/                    # diagnostic bundle (stage 07; raw/ and semantic-pages/ dissolved in Phase 5)
        manifests/                     # mirror of processed/manifests
        telemetry/                     # changelog.json, CHANGES.md, signature-inventory.json
      packages/
        openwrt-docs4ai-20260328.zip
      # staged/ root also holds stage 05d outputs:
      changelog.json
      CHANGES.md
      signature-inventory.json
      # and stage 07 / 05a–05c root outputs:
      index.html
      AGENTS.md
      README.md
      llms.txt
      llms-full.txt
```

**Nothing substantial created by the pipeline lives outside `tmp/`.** Every run is isolated in its
own timestamped directory. The `logs/` folder at `tmp/` root accumulates state across runs.

**CI variant:** On CI, `PIPELINE_RUN_DIR` is set explicitly to `tmp/pipeline-ci` — no timestamped
directory is created on CI. The schema above shows the form of a *local* run. The CI run uses the
same subdirectory layout (`downloads/`, `processed/`, `staged/`) under `tmp/pipeline-ci/`.
The PIPELINE_RUN_DIR resolution logic (Phase 1) always takes path 1 (env var) on CI, bypassing
the state file and generation logic entirely.

Note: `.cache/` lands inside `downloads/` per-run after this refactor — WIKI_CACHE_DIR fix is
deferred; see the **Wiki Scraper Cache** section.

---

## Config Variable Map

All variables live in `lib/config.py`. Changes show old → new default.
`lib/config.py` stays in `lib/` — it is the shared Python module imported by every script via `from lib import config`. No relocation needed.

| Variable | Old default | New default | Env var? |
|----------|-------------|-------------|---------|
| `PIPELINE_RUN_DIR` | n/a | `tmp/pipeline-YYYYMMDD-HHMMutc-XXXX` | Yes |
| `WORKDIR` | `tmp` | `{PIPELINE_RUN_DIR}/downloads` | Yes |
| `DOWNLOADS_DIR` | n/a | `{PIPELINE_RUN_DIR}/downloads` | Yes (alias) |
| `PROCESSED_DIR` | n/a | `{PIPELINE_RUN_DIR}/processed` | Yes |
| `STAGED_DIR` | n/a | `{PIPELINE_RUN_DIR}/staged` | Yes |
| `OUTDIR` | `staging` | `{PIPELINE_RUN_DIR}/staged` | Yes (legacy compat) |
| `L1_RAW_WORKDIR` | `tmp/L1-raw` | `{PROCESSED_DIR}/L1-raw` | No (computed) |
| `L2_SEMANTIC_WORKDIR` | `tmp/L2-semantic` | `{PROCESSED_DIR}/L2-semantic` | No (computed) |
| `REPO_MANIFEST_PATH` | `tmp/repo-manifest.json` | `{PROCESSED_DIR}/manifests/repo-manifest.json` | No (computed) |
| `CROSS_LINK_REGISTRY` | `tmp/cross-link-registry.json` | `{PROCESSED_DIR}/manifests/cross-link-registry.json` | No (computed) |
| `RELEASE_TREE_DIR` | `staging/release-tree` | `{STAGED_DIR}/release-tree` | No (computed) |
| `SUPPORT_TREE_DIR` | `staging/support-tree` | `{STAGED_DIR}/support-tree` | No (computed) |
| `PACKAGES_DIR` | n/a | `{STAGED_DIR}/packages` | No (computed) |
| `RUN_RECORD_PATH` | n/a | `{PIPELINE_RUN_DIR}/pipeline-run-record.json` | No (computed) |
| `PIPELINE_RUN_STATE` | n/a | `tmp/pipeline-run-state.json` | No (constant) |

`SUPPORT_TREE_DIR` is **kept** (path updated to point under `STAGED_DIR`; `raw/` and `semantic-pages/`
subdirs dissolved in Phase 5 — `manifests/` and `telemetry/` remain — see support-tree section).

`WIKI_CACHE_DIR` is **not added** in this refactor. After the WORKDIR change, the wiki scraper cache
lands at `downloads/.cache/` inside each per-run directory. This is a known performance regression
(cache not reused between local runs). The fix is deferred — see Wiki Scraper Cache section.

---

## pipeline-run-record.json Schema

Written by `ensure_dirs()` when a new run directory is created. Updated by
stage 08 on completion or failure. Paths are relative to the repo root.

```json
{
  "schema_version": 1,
  "run_id": "pipeline-20260328-1425UTC-7f3c",
  "created_utc": "2026-03-28T14:25:37Z",
  "status": "running",
  "pipeline_run_dir": "tmp/pipeline-20260328-1425UTC-7f3c"
}
```

`status` values: `running` | `complete` | `failed`

Paths are intentionally not enumerated. Callers derive them from
`pipeline_run_dir` using the schema above. This avoids stale path records
when the schema changes.

---

## Static Resources

### What they are

These are files committed to the source repository that the pipeline reads
but does not generate. They are exclusively managed by humans locally — not
created or modified by any CI operation.

| Current location | Contents | How pipeline uses it |
|-----------------|----------|---------------------|
| `content/cookbook-source/` | 18 authored `.md` guides | Stage 02i reads, produces `processed/L1-raw/cookbook/` |
| `data/base/` | AI summary JSON store | Stage 04 reads (and writes when `--run-ai` active) |
| `data/override/` | Manual AI override files | Stage 04 reads only |
| `release-inputs/release-include/` | Static tree copied into `staged/release-tree/` | Stage 05a copies verbatim |
| `release-inputs/pages-include/` | `.nojekyll` overlay for gh-pages deploy | CI deploy step only |
| `release-inputs/release-repo-include/` | `README.md` for corpus repo root | CI deploy step only |

### Grouping decision

**Move all of the above into a single top-level `static/` folder.** The `release-inputs/` folder
keeps its internal structure intact — only the parent moves.

```
static/
  cookbook-source/          (moved from content/cookbook-source/)
  data/
    base/                   (moved from data/base/)
    override/               (moved from data/override/)
  release-inputs/           (moved intact from release-inputs/)
    release-include/        (unchanged internally)
    pages-include/          (unchanged internally)
    release-repo-include/   (unchanged internally)
```

**Pros:**
- One folder to audit everything the pipeline reads as source material.
- Clean boundary: anything not in `static/` and not in `tmp/` is pipeline code.
- `release-inputs/` internal structure can be changed at any future time without
  affecting the `static/` grouping.

**Cons:**
- `data/base/` is written by stage 04 when `--run-ai` is active, so it is not
  purely static. Accept this: it is *authored/curated* data, not generated
  output. The occasional `--run-ai` write is a human-controlled operation.
- Import paths in `config.py`, stage 02i, stage 04, and stage 05a must update.

### Alternative names logged for future consideration

For the category folder (`static/`):
- `static/` — simple, implies read-only from pipeline's view
- `pipeline-source/` — explicit but verbose
- `source-assets/` — precise
- `inputs/` — short, but `data/base/` blurs the line
- `authored/` — accurate but uncommon in pipeline projects

For individual sub-folders (defer to future pass):
- `cookbook-source/` → `cookbook/`, `authored-guides/`, `openwrt-cookbook/`
- `data/base/` → `ai-store/`, `ai-cache/`, `summaries/`
- `release-inputs/release-include/` → `overlays/corpus/`, `corpus-static/`
- `release-inputs/pages-include/` → `overlays/pages/`, `pages-static/`
- `release-inputs/release-repo-include/` → `overlays/repo/`, `repo-static/`

---

## support-tree

### What it is (research findings)

`support-tree/` is materialized by stage 07's `copy_support_tree()` function. It is a structured
diagnostic bundle assembled from files that already exist elsewhere in the pipeline output. Its
contents:

| Subfolder | Contents | Source |
|-----------|----------|--------|
| `raw/` | Copy of all L1 markdown + meta.json files | mirrors `processed/L1-raw/` |
| `semantic-pages/` | Copy of all L2 markdown files | mirrors `processed/L2-semantic/` |
| `manifests/` | `repo-manifest.json`, `cross-link-registry.json` | mirrors `processed/manifests/` |
| `telemetry/` | `changelog.json`, `CHANGES.md`, `signature-inventory.json` | copied from `staged/` root |

**What each element is:**

`raw/` and `semantic-pages/` are verbatim copies of the L1 and L2 layers. No additional
transformation. Their only purpose in support-tree is to provide a single location where a
developer can find "all internal content" without navigating the processed/ tree.

`manifests/cross-link-registry.json` — produced by stage 03. Maps every symbol (function,
variable, heading) to its module, file path, and signature. Used by stage 05d to build the API
inventory and by stage 03 itself for cross-link resolution. Essentially "the index of everything
we extracted and normalized."

`manifests/repo-manifest.json` — produced by stage 01. Records what git repos were cloned: URLs,
commit SHAs, clone timestamps. Provides provenance: "this output was built from these exact commits."

`telemetry/signature-inventory.json` — produced by stage 05d. Snapshot of all ucode/LuCI API
function signatures extracted during this run. Used as the baseline for the NEXT run's stage 05d
to compute which functions were added, removed, or changed (API drift). See the
"signature-inventory.json" section below for deeper analysis.

`telemetry/changelog.json` and `telemetry/CHANGES.md` — produced by stage 05d. The computed diff
between this run's signature inventory and the previous run's. Answers "what changed in the OpenWrt
API surface since last run?" These files are also placed inside `release-tree/` as deliverables.

**Who reads support-tree:**

- Stage 08 validates that support-tree exists and has correct content (matching source files).
- The process-summary CI inline script counts files in `support-tree/raw/` and
  `support-tree/semantic-pages/` for the run summary artifact.
- **Nothing reads support-tree as a source for further processing.** No stage takes
  support-tree as input to produce other outputs.

### Decision: partial dissolution — dissolve raw/ and semantic-pages/, keep manifests/ and telemetry/

`raw/` and `semantic-pages/` are exact duplicates of `processed/L1-raw/` and
`processed/L2-semantic/`. After this refactor, those canonical paths exist and are stable.
Carrying redundant copies into support-tree doubles the disk footprint for no functional benefit.
**Dissolve them.**

`manifests/` and `telemetry/` are **kept**. The manifests provide useful provenance bundling.
Telemetry contains the stage 05d outputs (signature-inventory, changelog) that the CI
run-summary references. No compelling redundancy concern for these in this refactor.

**What changes (Phases 5 and 7):**

| Component | Decision | Action |
|-----------|----------|--------|
| `raw/` | Dissolve | Remove `raw/` copy from `copy_support_tree()`; remove from stage 08 validation |
| `semantic-pages/` | Dissolve | Remove `semantic-pages/` copy from `copy_support_tree()`; remove from stage 08 validation |
| `manifests/` | Keep | Update source path: `outdir/` root → `PROCESSED_DIR/manifests/` |
| `telemetry/` | Keep | Source path unchanged (stage 05d writes to `STAGED_DIR` root = `outdir/` root) |

**After dissolution, support-tree contains:**

```
support-tree/
  manifests/
    repo-manifest.json
    cross-link-registry.json
  telemetry/
    changelog.json
    CHANGES.md
    signature-inventory.json
```

**Who reads support-tree after dissolution:**

- Stage 08 validates `support-tree/manifests/` and `support-tree/telemetry/` exist with correct
  files. The `raw/` and `semantic-pages/` checks are removed.
- CI process-summary: replace `support_tree/raw/` and `support_tree/semantic-pages/` file counts
  with `processed/L1-raw/` and `processed/L2-semantic/` counts directly.
- **Nothing reads support-tree as a source for further processing.** This remains true.

### Anti-truths (false beliefs that will cause incorrect implementation)

❌ `support-tree/raw/` and `support-tree/semantic-pages/` are needed by downstream pipeline stages
→ **FALSE.** Nothing reads support-tree as input to any stage. All readers are stage 08 validation
  and the CI process-summary counter — both are updated in Phases 5/7/9.

❌ Dissolving `raw/` and `semantic-pages/` loses data
→ **FALSE.** Canonical copies live at `processed/L1-raw/` and `processed/L2-semantic/`.
  Support-tree was always a secondary copy. The processed/ layer is authoritative.

❌ Telemetry files should move to `processed/telemetry/` to eliminate the staged/ root copies
→ **FALSE (not in scope).** Stage 05d writes changelog.json, CHANGES.md, and
  signature-inventory.json directly to OUTDIR root (= STAGED_DIR). These are deliverable outputs,
  not intermediate artifacts. Do not create `processed/telemetry/`. Telemetry stays at staged/ root
  and in support-tree/telemetry/ (unchanged).

❌ `manifests/` in support-tree can be removed because `processed/manifests/` exists
→ **Not dissolved in this refactor.** Tracked in Deferred section below.

❌ Stage 07's `copy_support_tree()` reads from `support-tree/` as input
→ **FALSE.** `copy_support_tree()` only *writes* to support-tree/. It reads from `processed/` and
  `staged/` root. Removing raw/ and semantic-pages/ operations only affects write paths.

❌ Removing `raw/` from `copy_support_tree()` is safe to commit without updating stage 08
→ **FALSE.** Phase 5 and Phase 7 must be implemented and committed together. If the copy is
  removed but stage 08 still validates for `raw/`, every run will fail stage 08.

### Guardrails

- Do NOT remove `manifests/` or `telemetry/` copy operations from `copy_support_tree()` in this
  refactor. This is the partial dissolution boundary.
- Do NOT create a `processed/telemetry/` directory. Telemetry files stay at `staged/` root.
- Phase 5 (stage 07) and Phase 7 (stage 08) must be tested together. Do not run pytest between
  them — tests will fail until both phases are complete.
- **Pre-audit before Phase 5:** grep stage 07 for any references to `support_tree_dir` combined
  with `"raw"` or `"semantic"` or `"semantic-pages"` outside of `copy_support_tree()` itself
  (e.g., in `collect_sections()` or `build_html()`). If found, those refs must also be updated.
- The CI process-summary glob counts for `support_tree/raw/` and `support_tree/semantic-pages/`
  MUST be replaced in Phase 9. Leaving stale counts produces silent zeros — no error, just
  wrong numbers in the run summary artifact.

### Deferred: full support-tree dissolution

After partial dissolution ships, `manifests/` and `telemetry/` remain as copies of data available
elsewhere. Full dissolution is possible in a follow-on refactor:

| Component | Redundancy | Future option |
|-----------|-----------|---------------|
| `manifests/` | Copies from `processed/manifests/` | Remove; update stage 08 + summary step to read `processed/` directly |
| `telemetry/` | Copies of files from `staged/` root | Remove support-tree/telemetry/ copy; update stage 08 to check staged/ root |
| `SUPPORT_TREE_DIR` config var | Unused if fully dissolved | Remove after full dissolution |
| `copy_support_tree()` function | Entire function deleted if fully dissolved | Stage 08 validates processed/ and staged/ root directly |

Full dissolution additionally requires:
1. Audit `collect_sections()` and `build_html()` in stage 07 for any support-tree path dependencies
2. Remove the `support-tree/` entry from `ensure_dirs()`
3. Update `docs/specs/release-tree-contract.md` to tombstone the support-tree section

Defer until the folder schema refactor ships and is confirmed stable.

---

## Website / Deployment Surfaces

### How GitHub Pages works for this pipeline

The pipeline uses GitHub Pages in two distinct ways — a branch-based deployment on this repo, and
repo-based deployments on the distribution repos.

**Branch-based deployment (LuminairPrime test preview):**

GitHub automatically triggers `pages-build-deployment` whenever the `gh-pages` branch of a repo
is pushed. No workflow file is needed on the receiving end. The branch's contents become the
website. The CI workflow creates a git worktree pointing at the `gh-pages` branch, mirrors content
into it using `sync_tree.py`, and pushes. That push triggers GitHub's built-in deployment.

```
LuminairPrime/openwrt-docs4ai-pipeline
  ├── main    (pipeline code + CI — this is what you edit)
  └── gh-pages (website content only — no code, no workflow)
        └─ serves: https://luminairprime.github.io/openwrt-docs4ai-pipeline/
```

The `gh-pages` branch is ephemeral from the pipeline's perspective. It is overwritten each run.
It has no relationship to `main` other than living in the same repo.

**Repo-based deployments (production, external):**

These are separate repositories in the `openwrt-docs4ai` org. GitHub serves
`{orgname}.github.io` repos automatically as GitHub Pages. The CI workflow checks out each repo
as a transient working tree via `actions/checkout`, mirrors content into it, and pushes to its
`main` branch. GitHub then automatically deploys.

```
openwrt-docs4ai/openwrt-docs4ai.github.io   (separate repo, main branch = website)
  └─ serves: https://openwrt-docs4ai.github.io/

openwrt-docs4ai/corpus   (separate repo, main branch = corpus content + release assets)
  └─ serves: https://github.com/openwrt-docs4ai/corpus (not a pages site; just a git repo)
```

**Why the three are independent:** the gh-pages branch push and the two external repo pushes are
separate git operations with separate credentials, happening in sequence in the CI `deploy` job.
A failure in one does not prevent the others from attempting.

### Current CI deployment (3 surfaces)

1. **LuminairPrime gh-pages** (`gh-pages` branch, test preview):
   - Source: all of `$PUBLISH_DIR` (`openwrt-condensed-docs/`, which is a copy
     of OUTDIR including support-tree, L1-raw copies, etc.)
   - Bug: this mirrors the ENTIRE OUTDIR, not the website. The test preview shows a
     file-listing index including internal pipeline artifacts.
   - URL: `https://luminairprime.github.io/openwrt-docs4ai-pipeline/`

2. **openwrt-docs4ai/openwrt-docs4ai.github.io** (production pages site):
   - Source: `OUTDIR/release-tree` + `pages-include/` overlay
   - URL: `https://openwrt-docs4ai.github.io/`

3. **openwrt-docs4ai/corpus** (production corpus repo):
   - Source: `OUTDIR/release-tree` + `release-repo-include/` overlay
   - URL: `https://github.com/openwrt-docs4ai/corpus`

### Decision: fix LuminairPrime gh-pages to match production pages

Fix the gh-pages source to `staged/release-tree` + `pages-include/` overlay — identical to the
external pages deployment, different destination only. After this fix:

- The test preview website is byte-for-byte equivalent to what gets published to production pages.
- No support-tree, L1-raw, or other internal state on the test preview.
- The `PUBLISH_DIR` intermediate copy and `promote-generated` step are removed entirely
  (the gh-pages step no longer needs a separate staging copy; it reads `staged/release-tree/` directly).
- A local developer can open `staged/release-tree/index.html` and see exactly what gets deployed.

**Implementation in CI:** replace the current gh-pages mirror step (which mirrors all of
`$PUBLISH_DIR`) with the same logic as the external pages step: mirror `$STAGED_DIR/release-tree`
then apply the `pages-include/` overlay. The only difference from the external pages step is the
destination (`gh-pages` worktree on this repo vs. external pages repo checkout).

---

## Wiki Scraper Cache (.cache/)

Stage 02a (wiki scraper) maintains a cache file `wiki-lastmod.json` that tracks for each wiki
page URL:
- `last_modified`: ISO timestamp from the wiki
- `last_modified_http`: raw HTTP `Last-Modified` header value
- `raw_hash` / `content_hash`: hashes of the scraped HTML and extracted content

On re-runs, the scraper checks the last-modified timestamp and content hash to determine if a
page needs to be re-scraped. If unchanged, the page is skipped. This saves HTTP requests and
processing time during local development iteration.

**Current location:** `{WORKDIR}/.cache/wiki-lastmod.json` = `tmp/.cache/wiki-lastmod.json`

**Known regression introduced by this refactor:** After the folder refactor, `WORKDIR` =
`tmp/pipeline-XXXX/downloads/`. Stage 02a's `get_cache_dir()` returns
`os.path.join(config.WORKDIR, ".cache")`, so the cache will land at
`tmp/pipeline-XXXX/downloads/.cache/wiki-lastmod.json`. The cache is **not reused between local
runs** — each run starts from a fresh scrape. For a full wiki scrape (~200 pages at ~1.5s
delay each), this adds approximately **5 minutes per local run**. This is a performance
regression, not a correctness issue.

**CI is unaffected** — fresh VM per run always re-scrapes anyway.

**Decision: do not fix in this refactor. Note as deferred.**

**Deferred fix:** Add `WIKI_CACHE_DIR = "tmp/.cache"` to `config.py` (a constant path, outside
all run directories). Update stage 02a's `get_cache_dir()` to return `config.WIKI_CACHE_DIR`
instead of `os.path.join(config.WORKDIR, ".cache")`. This restores the shared cache across local
runs. The fix is excluded from the current implementation phases. Implement as a standalone PR
after the folder schema refactor ships.

**Notes for when the fix is implemented:**
- `tmp/.cache/` is the right home: shared scratch, not specific to any run, safely deletable.
- The cache is NOT appropriate for `static/` (tooling state, not authored content).
- The cache is NOT appropriate for `downloads/` (belongs to no single run).
- Stale entries cause a re-scrape, not an error. Cache can be deleted at any time.
- Automatic cache expiry (discard entries older than N days) is a separate deferred improvement.

---

## Downloads Zone: Management Notes

**Bonus property:** `downloads/` content can be safely deleted after any successful run.
Everything in it can be re-obtained:
- Repos: `git clone` (same shallow clone as CI)
- Wiki HTML: re-scraped from openwrt.org
- `.cache/` note: after this refactor, the wiki cache lands at `downloads/.cache/` inside each
  per-run directory — it IS deleted when you delete `downloads/`. This is a known regression.
  The deferred `WIKI_CACHE_DIR` fix will move it to a shared `tmp/.cache/` constant path.
  Until then, local runs always re-scrape all wiki pages.

**Current behavior:** the pipeline re-downloads everything on each run.
This is correct for CI (clean VM, no cache) but wasteful locally.

**Long-term note (do not implement in this refactor):** the pipeline should be
audited for incremental download support — only re-clone/scrape sources that
have actually changed since the last run. The wiki already has a `.cache/`
mechanism; git repos could be updated with `git fetch` + reset instead of
fresh clones. This is not trivial to implement correctly and is deferred.

**Disk management policy (log in README):**
- `downloads/`: delete freely, re-obtainable
- `processed/`: preserve as debugging record; small
- `staged/`: keep several versions for diff and regression; also small
- `downloads/.cache/`: deleted along with `downloads/` (per-run until WIKI_CACHE_DIR fix ships)
- Prune `downloads/` first when disk space is needed

---

## ZIP Generation: Unified Local + CI

### Current CI behavior

The zip is built in `$RUNNER_TEMP`:
```bash
release_tree="$OUTDIR/release-tree"
zip_stage="$RUNNER_TEMP/dist-zip"
zip_root="$zip_stage/openwrt-docs4ai"
zip_path="$RUNNER_TEMP/openwrt-docs4ai-YYYY-MM-DD.zip"
# mirrors release-tree → zip_root, then zips
```

It is then attached as a GitHub release asset on the corpus repo. It never
touches the pipeline output tree.

### Decision: move zip into `staged/packages/`

The zip is produced at `staged/packages/` in both contexts, with context-dependent filename:

| Context | Filename format | Example |
|---------|----------------|---------|
| Local developer run | `openwrt-docs4ai-{date}-{hex}.zip` | `openwrt-docs4ai-20260328-7f3c.zip` |
| CI GitHub release upload | `openwrt-docs4ai-{date}.zip` | `openwrt-docs4ai-20260328.zip` |

The hex suffix on local runs prevents silent overwrites when a developer iterates multiple times
in a day. CI release assets use the bare date format — release asset consumers expect a stable,
predictable filename. The packaging script uses `--ci` flag (or `CI=true` env var) to select format.
See Phase 8 for implementation details.

Inside the zip, the root directory is `openwrt-docs4ai/` (unchanged, controlled
by `DIST_ZIP_ROOT_DIR`). Contents are `staged/release-tree/`.

**CI change:** the CI zip step changes its output path from
`$RUNNER_TEMP/openwrt-docs4ai-*.zip` to `$STAGED_DIR/packages/openwrt-docs4ai-*.zip`.
The GitHub release upload step reads from the new path. Everything else is
unchanged.

**Test coverage:** add one test:
- `staged/packages/` contains exactly one `.zip` file
- The zip is non-empty (> 0 bytes)
- Filename matches expected local pattern: `openwrt-docs4ai-YYYY-MM-DD-XXXX.zip`
  (where XXXX = 4 hex chars from PIPELINE_RUN_DIR)

Do not test zip contents or file size. Both are fragile — contents grow, size
thresholds go stale.

---

## Staging openwrt-condensed-docs promotion step: remove

Currently CI does:
```
python tools/sync_tree.py promote-generated --src "$OUTDIR" --dest "$GITHUB_WORKSPACE/$PUBLISH_DIR"
```

This copies `staging/` → `openwrt-condensed-docs/`. It was introduced to
decouple the OUTDIR folder name from what gh-pages and deploys consume.

With the new schema, `staged/release-tree/` is used directly by all deploy
steps. No intermediate copy is needed. The promotion step is removed.

`PUBLISH_DIR` env var is removed. The `openwrt-condensed-docs/` gitignore
entry can be removed.

---

## Folder Structure for Static Resources: File System Change Required

The following files/folders must be moved (code and CI paths updated
accordingly):

| From | To |
|------|----|
| `content/cookbook-source/` | `static/cookbook-source/` |
| `data/base/` | `static/data/base/` |
| `data/override/` | `static/data/override/` |
| `release-inputs/` | `static/release-inputs/` (entire folder, internal structure unchanged) |

Files that reference these paths and must be updated:
- `lib/config.py` — `AI_DATA_BASE_DIR`, `AI_DATA_OVERRIDE_DIR`, `RELEASE_INCLUDE_DIR`, `PAGES_INCLUDE_DIR`
- `.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py` — reads `content/cookbook-source/`
- `.github/scripts/openwrt-docs4ai-05a-assemble-references.py` — reads `RELEASE_INCLUDE_DIR`
- `.github/workflows/openwrt-docs4ai-00-pipeline.yml` — `pages-include` and `release-repo-include` paths in deploy steps

---

## signature-inventory.json and the Baseline Mechanism

### What signature-inventory.json is

Stage 05d reads `cross-link-registry.json` (produced by stage 03), extracts every symbol's
signature (function name + parameter list), and writes a snapshot:

```json
{
  "generated": "2026-03-28T14:25:37Z",
  "signatures": {
    "uci.get": "function(config, section, option)",
    "ucode.printf": "function(fmt, ...)",
    ...
  }
}
```

This file is the "API state of the OpenWrt codebase at this run." The NEXT run's stage 05d
compares its current inventory against this file to detect API drift: which functions were added,
removed, or had their signature changed. The diff becomes `changelog.json` and `CHANGES.md`.

### Where it lives

Stage 05d writes `signature-inventory.json` to `OUTDIR/` root. In the current pipeline that is
`staging/signature-inventory.json`. In the new schema, `OUTDIR = STAGED_DIR`, so it will be at
`staged/signature-inventory.json`. **This is a natural path change — no code change to stage 05d
is needed.** The file moves with OUTDIR.

Stage 07 then copies it from `OUTDIR/signature-inventory.json` → `support-tree/telemetry/`. This
also requires no change since it reads from `outdir/` (= STAGED_DIR).

### The baseline mechanism and why CI was always starting fresh

The CI `Prepare Baseline` step (before stage 01 runs) does:

```bash
if [ -f "$PUBLISH_DIR/signature-inventory.json" ]; then
  cp "$PUBLISH_DIR/signature-inventory.json" baseline/
fi
```

This reads the PREVIOUS run's `signature-inventory.json` from `$PUBLISH_DIR`. But
`openwrt-condensed-docs/` (PUBLISH_DIR) is gitignored — it is NOT committed to the repo. On every
fresh CI VM checkout, the folder does not exist. **The baseline was always empty on CI.** Stage
05d has always run in "first run" mode on CI, producing a null diff. This is not a bug — it is
the correct behavior since there is no cheap way to persist the file between CI runs.

**Consequence:** removing `PUBLISH_DIR` and the `promote-generated` step causes **zero regression**
to the baseline mechanism. CI baseline behavior is unchanged (always empty).

### After the refactor

The baseline step needs to be updated since `PUBLISH_DIR` no longer exists. Update it to try
to read from `$STAGED_DIR/signature-inventory.json`. Since STAGED_DIR is a per-run directory
that does not exist before the current run starts, the file will never be found on CI —
which maintains the current "no baseline on CI" behavior.

**This is deliberately dead code on CI.** The `if` branch will never be taken on a fresh CI
VM. The purpose of the check is correctness for local development runs where a developer
pre-positions a previous run's inventory file, not for CI. Documenting it as dead code prevents
a future engineer from "fixing" it by pointing it at a file that actually exists on CI,
which could introduce stale baseline comparisons.

For local development, if a developer wants baseline drift tracking between consecutive local runs,
they can manually copy `staged/signature-inventory.json` from a previous run's directory to
`baseline/` before running. Automating this via `pipeline-run-state.json` (look up previous run's
staged path) is a deferred improvement.

```bash
# Updated CI baseline step (after refactor)
if [ -f "$STAGED_DIR/signature-inventory.json" ]; then
  cp "$STAGED_DIR/signature-inventory.json" baseline/
  echo "Baseline inventory found and staged."
else
  echo "No baseline inventory found. Stage 05d will run in first-run mode."
fi
```

---

## Implementation Phases

Implement in this order. Each phase is independently testable, **except where coupling is explicitly noted:**

- **Phases 5 and 7** must be implemented and committed together — do not run pytest between them.
- **Phase 4** depends on Phase 3 (Phase 3 moves L1/L2 to `processed/`; Phase 4 updates all readers to the new location).
- **Phase 6** must be implemented AFTER the Phase 5+7 commit, despite its numbering. If Phase 6 runs first, `validate_index_html_contract()` hard-fails because the legacy `./openwrt-condensed-docs/` check (removed in Phase 7 Step C) is still present.
- **Phase 10 output_sync cleanup** (deleting `GENERATED_ROOT_REQUIRED_FILES`, `GENERATED_ROOT_REQUIRED_DIRS`, `validate_generated_root()`) must be committed in the same commit as Phase 9's `promote-generated` removal.

### Phase 0 — Static resources move

**This phase is file-system operations only.** No `config.py` code changes belong here.
All `config.py` path constant updates are in Phase 1. Keeping these separate ensures
Phase 0 is independently testable at the path level before any config logic changes.

File moves (use `git mv` to preserve history):
- `content/cookbook-source/` → `static/cookbook-source/`
- `data/base/`, `data/override/` → `static/data/base/`, `static/data/override/`
- `release-inputs/` → `static/release-inputs/` (entire folder, internal names unchanged)

**Also required in this phase — `source_locator` metadata fix:**
Stage `02i-ingest-cookbook.py` line 111 hardcodes:
```python
"source_locator": f"content/cookbook-source/{filename}"
```
This string propagates through every cookbook `.meta.json`, through stage 03's L2 frontmatter
(line 764), and into the published `chunked-reference/` files (stage 05a). After Phase 0 moves
the files, every generated output will embed a stale path even though the content is correct.
Fix: update the `source_locator` string to `f"static/cookbook-source/{filename}"` in
`02i-ingest-cookbook.py`. This is a Phase 0 fix because the path is emitted during extraction,
not in `config.py`.

Run `python tests/check_linting.py` only. Do **not** run `python tests/run_pytest.py` at the
end of Phase 0 — `config.py` still references the old paths (`data/base/`, `release-inputs/`).
Tests that exercise cookbook ingestion or AI store paths will fail until Phase 1 updates the
config constants. Linting validates the `source_locator` string change is syntactically correct.

**Post-move verification:** after the `git mv` operations, run `git status` and confirm:
- All moved files appear as renamed (not deleted + new).
- No untracked files remain in the old `content/`, `data/`, or `release-inputs/` locations.
- The working tree is clean except for the expected renames and the `source_locator` edit.

### Phase 1 — config.py restructure

Add `PIPELINE_RUN_DIR`, `DOWNLOADS_DIR`, `PROCESSED_DIR`, `STAGED_DIR`,
`PACKAGES_DIR`, `RUN_RECORD_PATH`, `PIPELINE_RUN_STATE`.
Do **not** add `WIKI_CACHE_DIR` — deferred (see Wiki Scraper Cache section).
Recompute all existing derived paths from the new roots.
Update `SUPPORT_TREE_DIR` to point to `{STAGED_DIR}/support-tree` (not removed; content changes
in Phase 5 dissolve `raw/` and `semantic-pages/` subdirs but keep `manifests/` and `telemetry/`).
Add `mark_run_complete()` and `mark_run_failed()` helpers.

Keep `WORKDIR` and `OUTDIR` as aliases to `DOWNLOADS_DIR` and `STAGED_DIR`
for backward compatibility with any external tooling.

Update `RELEASE_INCLUDE_DIR` from `release-inputs/release-include` to
`static/release-inputs/release-include`. Same for `PAGES_INCLUDE_DIR` and
`AI_DATA_BASE_DIR` / `AI_DATA_OVERRIDE_DIR`.

**PIPELINE_RUN_DIR resolution order (critical — prevents each script spawning a different run dir):**

`config.py` must NOT call `datetime.now()` unconditionally at import time. If it does, every
`python stageXX.py` invocation generates a fresh timestamped directory and the stages never
share the same run directory. Instead:

```python
# Resolution order in config.py (pseudocode)
PIPELINE_RUN_DIR = (
    os.environ.get("PIPELINE_RUN_DIR")              # 1. env var (CI sets this explicitly)
    or _read_state_file(PIPELINE_RUN_STATE)          # 2. read tmp/pipeline-run-state.json
    or _generate_and_save_new_run_dir()              # 3. new run: generate, write state file
)
```

`_generate_and_save_new_run_dir()` generates the `pipeline-YYYYMMDD-HHMMutc-XXXX` string,
writes it to `tmp/pipeline-run-state.json` immediately (before any directory is created), and
returns it. Subsequent imports in the same process see the same env or state file.

**`pipeline-run-state.json` write contract:**
- Written exclusively by `config.py` `_generate_and_save_new_run_dir()` (or `ensure_dirs()`).
- Written atomically: write to a `.tmp` file, rename into place.
- No locking beyond OS rename atomicity — local use only; CI always sets the env var.
- Format: `{"pipeline_run_dir": "tmp/pipeline-20260328-1425UTC-7f3c"}`
- `mark_run_complete()` / `mark_run_failed()` update `pipeline-run-record.json` inside the run
  dir, not this file.
- **Naming distinction:** `pipeline-run-state.json` (global pointer at `tmp/` root, only
  `config.py` reads/writes it) vs. `pipeline-run-record.json` (per-run metadata, inside the run
  directory itself). Pipeline stages never read or write `pipeline-run-state.json` directly.
- **Last-writer-wins semantics:** if two local processes concurrently reach
  `_generate_and_save_new_run_dir()` at the same instant (e.g., `pytest -n 8` parallelized over
  empty `tmp/`), the last `os.rename()` caller wins and its run directory becomes the state
  pointer. For local sequential use this is acceptable. Avoid running parallel independent
  pipeline shells from the same workspace — state pointers will race. For xdist parallelism,
  set `PIPELINE_RUN_DIR` via env var before launching pytest to bypass the state file entirely.

**`ensure_dirs()` — full directory list to create:**
```
tmp/pipeline-{run_id}/
  pipeline-run-record.json    (written here)
  downloads/
    repos/
    wiki/raw/
  processed/
    L1-raw/
    L2-semantic/
    manifests/
  staged/
    release-tree/
    support-tree/
      manifests/
      telemetry/
    packages/
tmp/logs/                     (create only if absent; do not wipe)
```
All creations are `mkdir -p` equivalent. `ensure_dirs()` must not fail if dirs already exist.

**WORKDIR / OUTDIR alias fragmentation — required pre-audit before Phase 2:**
Run: `grep -rn "WORKDIR\|OUTDIR" .github/scripts/ lib/ tests/` and enumerate every usage.
Any script constructing `os.path.join(WORKDIR, "L1-raw")` or similar relative paths will
break silently — `WORKDIR` used to be `tmp/` (parent of `L1-raw`); it is now
`tmp/pipeline-XXXX/downloads/`. Every such usage must be updated to the appropriate
`config.PROCESSED_DIR` path before that script's phase runs.

### Phase 2 — stage 01 WORKDIR fix

Script 01 has its own `WORKDIR` resolution that ignores `config.py`. Fix to
import and use `config.DOWNLOADS_DIR`.

### Phase 3 — stage 03 routing

**Critical context — L1/L2 write-path after Phase 1:**
After Phase 1, `L1_RAW_WORKDIR = {PROCESSED_DIR}/L1-raw` and `L2_SEMANTIC_WORKDIR =
{PROCESSED_DIR}/L2-semantic`. All extractors (02a–02h) write L1 content via
`extractor.write_l1_markdown()`, which uses `config.L1_RAW_WORKDIR`. Stage 03 writes L2
content to `config.L2_SEMANTIC_WORKDIR`. **This means extractors and stage 03 write directly
to `processed/L1-raw/` and `processed/L2-semantic/` — the data is already at its final
location.** The current `promote_to_staging()` L1/L2 copy (from WORKDIR to OUTDIR) becomes a
self-copy after Phase 1: source == destination. `shutil.rmtree(dst)` would delete the source
before `shutil.copytree()` runs, destroying all extractor output.

**Resolution: remove the L1/L2 copy from `promote_to_staging()`.** Only the manifest copy
(cross-link-registry.json, repo-manifest.json) remains. The function is renamed or restructured
to reflect that it now only promotes manifests.

Updated `promote_to_staging()` responsibilities (after this phase):

- ~~L1 copy~~ — **REMOVED** (extractors already write to `processed/L1-raw/`)
- ~~L2 copy~~ — **REMOVED** (stage 03 already writes to `processed/L2-semantic/`)
- `cross-link-registry.json` → `config.PROCESSED_DIR/manifests/cross-link-registry.json`
- `repo-manifest.json` → `config.PROCESSED_DIR/manifests/repo-manifest.json`

**This is critical.** Omitting the manifest redirections means `cross-link-registry.json` and
`repo-manifest.json` still land at `STAGED_DIR/` root after Phase 3. Phase 4's manifest consumer
fixes (05b, 05c, 05d) and Phase 5 Step C all expect them at `PROCESSED_DIR/manifests/`. If the
manifest destinations are not updated here, those stages will hard-fail or silently return empty.

`fail_if_partial_staging_promotion()` checks whether modules already exist at the target path
before re-running a promotion. Update its `existing_root` to use `config.PROCESSED_DIR` instead
of `config.OUTDIR` — otherwise the guard will always see the old location as empty and allow
accidental re-promotions over fresh-but-valid content.

**Manifest producer clarification (stage 03 source paths):**
Stage 03 writes `cross-link-registry.json` to `WORKDIR` (line ~809 in `03-normalize-semantic.py`:
`reg_path = os.path.join(WORKDIR, "cross-link-registry.json")`) and `repo-manifest.json` to
`WORKDIR` (line ~907). After this refactor, `WORKDIR` = `downloads/`, so the intermediate
write lands at `downloads/cross-link-registry.json` and `downloads/repo-manifest.json`.
The source paths inside `promote_to_staging()` that READ these intermediate files are
`WORKDIR/` paths — **these source paths do NOT change**. Only the copy **destinations**
change (from `OUTDIR/` root to `PROCESSED_DIR/manifests/`).

**Also in this phase — stage 02i write-path fix:**
`02i-ingest-cookbook.py` line 48 constructs its output path inconsistently with all other
extractors:
```python
# 02i (BROKEN after Phase 1):
out_dir = os.path.join(config.WORKDIR, "L1-raw", "cookbook")  # → downloads/L1-raw/cookbook

# All other extractors (correct) — via extractor.write_l1_markdown():
out_dir = os.path.join(config.L1_RAW_WORKDIR, module)          # → processed/L1-raw/{module}
```
After Phase 1, `WORKDIR` = `downloads/` and `L1_RAW_WORKDIR` = `processed/L1-raw/`. These are
different paths. Cookbook content would be orphaned at `downloads/L1-raw/cookbook/` while all
other modules write to `processed/L1-raw/`.
**Fix:** Update 02i to use `config.L1_RAW_WORKDIR` (or refactor to use
`extractor.write_l1_markdown()` like the other extractors). This fix must land no later than
Phase 3 — if deferred, cookbook content silently disappears from the pipeline output.

**After Phase 3, `staged/` root must NOT contain `cross-link-registry.json` or
`repo-manifest.json`.** If those files appear at `staged/` root after any run, that is a bug
indicating the copy destination was not updated. Verify explicitly after Phase 3 by confirming
`STAGED_DIR/cross-link-registry.json` does not exist after a test run.

### Phase 4 — All L2-semantic readers

**Prerequisite: Phase 3 must be complete.** After Phase 3, L1/L2 content lives at
`processed/L1-raw/` and `processed/L2-semantic/`. Any script still reading from
`OUTDIR/L2-semantic` (= `staged/L2-semantic`) will find an empty directory.

**All five read-sites that reference `OUTDIR/L2-semantic` must be updated in this phase.**
Omitting any one of them silently reads from an empty directory (since Phase 3 moved the content
to `processed/`), producing empty AI summaries, empty routing indexes, or broken agent outputs
with no error at the script level.

Required updates:
- **stage 04** — `04-generate-ai-summaries.py` / `lib/ai_enrichment.py` line ~327:
  `os.path.join(outdir, "L2-semantic")` → `config.PROCESSED_DIR / "L2-semantic"`
- **stage 05a** — `05a-assemble-references.py`:
  `L2_DIR = os.path.join(OUTDIR, "L2-semantic")` → `config.PROCESSED_DIR / "L2-semantic"`
- **stage 05b** — `05b-generate-agents-and-readme.py` line ~25:
  `L2_DIR = os.path.join(OUTDIR, "L2-semantic")` → `config.PROCESSED_DIR / "L2-semantic"`
- **stage 06** — `06-generate-llm-routing-indexes.py` line ~36:
  `L2_DIR = os.path.join(OUTDIR, "L2-semantic")` → `config.PROCESSED_DIR / "L2-semantic"`

**Pre-audit:** `grep -rn "L2-semantic\|L2_DIR" .github/scripts/ lib/` — verify every match is
addressed here. Add any new matches to this list before proceeding.

**Known additional read-site:** `lib/ai_store_workflow.py` line ~60 constructs
`permanent_l2_root = source_outdir / "L2-semantic"`. This file is used by
`tools/manage_ai_store.py`. The pre-audit grep will catch it; list it explicitly here so it
is not skipped if the implementer only updates the four numbered scripts above.

**ai_enrichment.py write-back clarification:** `lib/ai_enrichment.py` receives `outdir` as a
function parameter (passed by stage 04) for both reading L2 files and writing enriched content
back. The Phase 4 fix changes the L2 *read* path to `config.PROCESSED_DIR / "L2-semantic"`.
Verify that the write-back path (enriched content saved to L2) also targets `PROCESSED_DIR`,
not `STAGED_DIR`. If stage 04 passes `config.OUTDIR` (= STAGED_DIR) as `outdir`, the write-back
goes to the wrong location. Fix the caller (stage 04) to pass `config.PROCESSED_DIR` when
invoking `ai_enrichment` functions that write back to L2.

**Anti-truth:**
- ❌ "Only stage 05a reads L2-semantic" → FALSE. Stages 04, 05a, 05b, 06, and `ai_store_workflow.py`
  all have L2-semantic read-sites. The pre-audit grep is authoritative — do not assume the list
  above is exhaustive. Any match not updated silently produces empty output.

**Stage 06 fallback path for `repo-manifest.json`:**
`06-generate-llm-routing-indexes.py` lines ~88–89 contain:
```python
config.REPO_MANIFEST_PATH,
os.path.join(OUTDIR, "repo-manifest.json"),   # fallback
```
After Phase 1, `config.REPO_MANIFEST_PATH` = `{PROCESSED_DIR}/manifests/repo-manifest.json`
(correct). But the fallback `os.path.join(OUTDIR, "repo-manifest.json")` points to a
non-existent path after Phase 3. Update or remove the fallback. The pre-audit grep will catch
this line.

**Also in this phase — manifest path consumers:**

Three scripts read `cross-link-registry.json` and/or `repo-manifest.json` directly from
`OUTDIR/` root. After Phase 3 moves these files to `processed/manifests/`, any script still
constructing the path from `OUTDIR` will fail silently or hard-fail:

- **stage 05b** — `05b-generate-agents-and-readme.py`: verify cross-link-registry read site.
  If hardcoded from `OUTDIR`, update to `config.CROSS_LINK_REGISTRY` (or
  `config.PROCESSED_DIR / "manifests" / "cross-link-registry.json"`).
- **stage 05c** — `05c-generate-ucode-ide-schemas.py`: same check for cross-link-registry read.
- **stage 05d** — `05d-generate-api-drift-changelog.py`: reads `cross-link-registry.json`
  only (confirmed by code read — `05d:23` constructs only the cross-link-registry path).
  Update to use `config.CROSS_LINK_REGISTRY`. Stage 05d does **not** read `repo-manifest.json`.

**Pre-audit for manifests:** `grep -rn "cross-link-registry\|repo-manifest" .github/scripts/ lib/`
— enumerate every read-site before editing. Any inline path construction from `OUTDIR` or
`outdir` must be updated. If all consuming scripts already import the config constants, only the
config variable values change in Phase 1 and no script edits are needed here.

**Anti-truths:**
- ❌ "The manifest paths are only used by stage 05a and stage 03" → FALSE. Stages 05b, 05c,
  and 05d all read `cross-link-registry.json`. Any one left reading from `OUTDIR` silently
  reads a non-existent path after Phase 3.
- ❌ "Stage 05d reads repo-manifest.json" → FALSE (confirmed by code read). Stage 05d only
  reads `cross-link-registry.json`. Stage 06's fallback at lines ~88–89 and stage 03 itself
  (line ~907, WORKDIR source) are the only other repo-manifest read-sites outside the config
  constant; both are addressed in Phase 4 (stage 06) and Phase 3 (stage 03 source path).

### Phase 5 — stage 07 support-tree partial dissolution

**Prerequisite: Phase 3 must be complete before this phase. Implement Phase 5 and Phase 7 together.**

**Pre-audit (do before any edits):**
Grep stage 07 for `support_tree_dir` combined with `"raw"` / `"semantic"` / `"semantic-pages"`
outside of `copy_support_tree()`. If `collect_sections()` or `build_html()` reference these
paths, update them to read from `config.PROCESSED_DIR / "L1-raw"` (for raw/) or
`config.PROCESSED_DIR / "L2-semantic"` (for semantic-pages/) respectively. Remove any
references that were purely assembling the support-tree copy rather than pipeline logic.

Stage 07's `copy_support_tree()` currently copies:
- `outdir/L1-raw/` → `support_tree_dir/raw/`
- `outdir/L2-semantic/` → `support_tree_dir/semantic-pages/`
- `outdir/cross-link-registry.json`, `outdir/repo-manifest.json` → `support_tree_dir/manifests/`
- `outdir/changelog.json`, `outdir/CHANGES.md`, `outdir/signature-inventory.json` → `support_tree_dir/telemetry/`

**Step A — Remove raw/ copy operation:**
Delete the block in `copy_support_tree()` that copies `outdir/L1-raw` → `support_tree_dir/raw`.

**Step B — Remove semantic-pages/ copy operation:**
Delete the block in `copy_support_tree()` that copies `outdir/L2-semantic` → `support_tree_dir/semantic-pages`.

**Step C — Update manifests/ source paths:**
- `outdir / "cross-link-registry.json"` → `config.PROCESSED_DIR / "manifests" / "cross-link-registry.json"`
- `outdir / "repo-manifest.json"` → `config.PROCESSED_DIR / "manifests" / "repo-manifest.json"`

**Step D — Telemetry source paths (no change):**
Telemetry copies (CHANGES.md, changelog.json, signature-inventory.json) still read from
`outdir/` root (= STAGED_DIR root where stage 05d writes them). No code change needed.

**Anti-truths:**
- ❌ "`outdir/L1-raw` still exists after Phase 3" → FALSE. Phase 3 moves L1/L2 to `processed/`.
  After Phase 3, `outdir/L1-raw` does not exist. This phase MUST run after Phase 3.
- ❌ "support-tree/raw/ is the authoritative L1 source" → FALSE. `processed/L1-raw/` is
  authoritative. Support-tree/raw/ was always a secondary copy.
- ❌ "it is safe to commit Phase 5 without Phase 7" → FALSE. If the copy is removed but stage 08
  still validates for `raw/`, every run will fail stage 08. Commit both together.

**Guardrails:**
- Do NOT remove the `manifests/` or `telemetry/` copy operations.
- Do NOT run `python tests/run_pytest.py` between Phase 5 and Phase 7. Tests will fail.

### Phase 6 — stage 07 web index

- Change `PUBLISH_PREFIX` from `"./openwrt-condensed-docs"` to `"."` .
- **Note:** `PUBLISH_PREFIX` is not only used for file routing — it is also embedded in generated
  HTML `<title>` tags and heading labels in `build_html()`. Update the display/title logic
  independently of the routing change. After the change, verify the generated `index.html` title
  and breadcrumb labels are sensible (not empty strings or bare dots).
- Write `index.html` to `config.RELEASE_TREE_DIR` (it already writes to OUTDIR root too;
  `finalize_release_tree()` copies it into release-tree. Verify both copies are correct).
- **L1-raw and L2-semantic will NOT appear in the web index after Phase 3.** Stage 07's
  `build_html()` is called with `STAGED_DIR` as root; `collect_sections()` iterates that
  directory's immediate children. After Phase 3, `L1-raw` and `L2-semantic` live at
  `processed/`, which is a sibling of `staged/`, not a child. They silently disappear from
  the index — no error, just absent sections. **Choose one resolution and implement it:**

  **Option A (recommended — accept removal):** Remove the dead code. In stage 07, remove
  `"L1-raw"` and `"L2-semantic"` from `TOP_LEVEL_ORDER` (lines ~47–48), their corresponding
  entries in `SECTION_DESCRIPTIONS` (lines ~63–70), and the `section_file_sort_key()` branches
  that check `parts[0] in {"L1-raw", "L2-semantic"}` (lines ~155–165). After dissolution the
  index no longer contains these internal sections — which is correct, since the web index
  publishes only `release-tree/` content.

  **Option B (preserve diagnostic view):** Extend `main()` to call `collect_sections()` over
  both `STAGED_DIR` and `PROCESSED_DIR`, merging results into a single index. More complex;
  defer to a follow-on PR unless the diagnostic view is actively used.

  The plan defaults to **Option A**. If a developer relies on the L1/L2 sections of the local
  index for debugging, document the workaround: open `processed/` directly in a file browser.
- `copy_support_tree()` source path updates are in Phase 5.

### Phase 7 — stage 08 validation

**Prerequisite: implement and commit together with Phase 5.**

**Step A — Update OUTDIR → PROCESSED_DIR references:**
- Update all `OUTDIR/L1-raw` references to `PROCESSED_DIR/L1-raw`.
- Update all `OUTDIR/L2-semantic` references to `PROCESSED_DIR/L2-semantic`.
- Update `OUTDIR/cross-link-registry.json` and `OUTDIR/repo-manifest.json` references
  to `PROCESSED_DIR/manifests/`.

**Warning — stage 08 has approximately 12 distinct L2-semantic reference sites.** Do not assume
there are only a few. A targeted grep will find occurrences at lines ~59, ~231, ~370, ~433,
~482, ~587, ~786, ~787, ~1036, ~1061, ~1121 and more — in functions such as
`validate_module_llms_contract()`, `validate_llms_full_contract()`, and other validators that
construct expected paths against `outdir/L2-semantic/`. Run:
```
grep -n "L2-semantic\|L1-raw\|OUTDIR\|outdir" .github/scripts/openwrt-docs4ai-08*.py
```
before editing and update every hit. Any missed occurrence silently validates against a
non-existent path (false pass — validation reports OK when the file does not exist).

**Step B — support-tree dissolution validation update:**
In `validate_support_tree_contract()`, remove the checks for:
- `support_tree_dir / "raw"` existence and file count
- `support_tree_dir / "semantic-pages"` existence and file count

**Also remove `"raw"` and `"semantic-pages"` from the `required_dirs` list at line ~467:**
```python
# Before:
required_dirs = ["raw", "semantic-pages", "manifests", "telemetry"]
# After:
required_dirs = ["manifests", "telemetry"]
```

**Coverage note — `validate_processed_contract()` does not exist.** Do not assume it does.
When the support-tree raw/ and semantic-pages/ validation checks are removed, the structural
integrity of `processed/L1-raw/` and `processed/L2-semantic/` becomes unvalidated at the
stage 08 level. Before removing the old checks, either:

- (a) Add a new `validate_processed_layer()` function in stage 08 that asserts `processed/L1-raw/`
  and `processed/L2-semantic/` contain non-empty module subdirectories. Call it from `main()`
  before `validate_support_tree_contract()`. Then remove the old checks safely.
- (b) Update the mirror source paths in `validate_mirrored_tree()` from `os.path.join(outdir, "L1-raw")`
  to `config.PROCESSED_DIR / "L1-raw"` and keep the mirror count assertions — just redirect
  them to validate against the `processed/` source instead of the now-dissolved support-tree copies.

Option (a) is preferred. Option (b) requires keeping the mirror logic intact but with updated
source roots.

**validate_mirrored_file() source paths — also break after Phase 3:**
`validate_support_tree_contract()` line ~495–500 calls:
```python
validate_mirrored_file(os.path.join(outdir, file_name), ...)
```
with `file_name` = `"cross-link-registry.json"` and `"repo-manifest.json"`. After Phase 3
these files are at `PROCESSED_DIR/manifests/`, not at `outdir/`. The source paths must be
updated to `config.PROCESSED_DIR / "manifests" / file_name`.

**validate_outdir() also breaks — stage 08 lines ~963–974:**
`validate_outdir()` has a `core_files` list that includes BOTH `"repo-manifest.json"` AND
`"cross-link-registry.json"` at outdir root. After Phase 3, both files live at
`PROCESSED_DIR/manifests/`. Update both entries:
- `os.path.join(outdir, "cross-link-registry.json")` → `config.PROCESSED_DIR / "manifests" / "cross-link-registry.json"`
- `os.path.join(outdir, "repo-manifest.json")` → `config.PROCESSED_DIR / "manifests" / "repo-manifest.json"`

Keep checks for:
- `support_tree_dir / "manifests"` existence and expected files
- `support_tree_dir / "telemetry"` existence and expected files
  (`signature-inventory.json`, `changelog.json`, `CHANGES.md`)

**Step C — Remove legacy path checks:**
- Remove the `"./openwrt-condensed-docs/"` legacy path checks (lines 169, 205 in current file).
- Keep the leakage guard checks (lines 370, 403).

**Anti-truths:**
- ❌ "The validate_support_tree_contract() raw/ check can stay since it's just a warning" →
  FALSE. If the copy was removed in Phase 5 but the validation check remains, stage 08 will
  fail every run. Remove the check when the copy is removed.
- ❌ "Replace the raw/ count check with a check against processed/L1-raw/ instead" →
  NOT the right approach because option (a) above (`validate_processed_layer()`) provides
  cleaner, purpose-built coverage. After Phase 7 Step B removes the support-tree raw/ check,
  **no other existing stage 08 function validates `processed/L1-raw/` content** — option (a)
  is therefore required, not optional.

**Guardrails:**
- After completing Phases 5 and 7, run the full smoke test: `python tests/run_smoke.py`.
  The smoke test exercises end-to-end and will catch any missed validation references.
- The telemetry filenames checked in `support-tree/telemetry/` must match what stage 05d
  actually writes: `signature-inventory.json`, `changelog.json`, `CHANGES.md`. Do not rename.

### Phase 8 — ZIP generation

Extract zip build logic from CI workflow into a Python script
(`.github/scripts/openwrt-docs4ai-09-build-packages.py` or add to stage 08).
Output path varies by context to avoid same-day local run collisions:
- **Local runs:** `config.PACKAGES_DIR / f"openwrt-docs4ai-{date}-{run_hex}.zip"`
  (e.g., `openwrt-docs4ai-20260328-7f3c.zip`). The run hex comes from `PIPELINE_RUN_DIR`.
- **CI release upload:** strip the hex suffix — use the bare `{date}.zip` naming that consumers
  of GitHub release assets expect. The packaging script receives a `--ci` flag (or detects
  `CI=true` env var) to select the correct filename format.

`DIST_ZIP_ROOT_DIR` (interior root directory name) remains `openwrt-docs4ai/` unchanged.
CI workflow `distribution_zip` step calls the same script instead of inline
bash. Run zip locally as part of full local pipeline run.
Add test: packages dir contains one non-empty zip with correct filename format.

### Phase 9 — CI workflow

- Remove `PUBLISH_DIR` env var and the `promote-generated` step.
- Set `PIPELINE_RUN_DIR` to `{github.workspace}/tmp/pipeline-ci` — this is what makes the
  "takes path 1" resolution in Phase 1 actually true. Without this, CI falls through to
  path 3 (`_generate_and_save_new_run_dir()`), spawning a timestamped dir while WORKDIR and
  STAGED_DIR point to `pipeline-ci/`. `RUN_RECORD_PATH` would then live in a different root
  from all the data paths. Always set this explicitly on CI.
- Update `WORKDIR` to `{github.workspace}/tmp/pipeline-ci/downloads`.
- Update `OUTDIR` to `{github.workspace}/tmp/pipeline-ci/staged`.
- Set `PROCESSED_DIR`, `STAGED_DIR`. Do **not** set `WIKI_CACHE_DIR` (deferred — see Wiki Scraper Cache section).
- **Why `pipeline-ci/` instead of a per-run timestamped directory:** CI VMs are ephemeral
  and fresh per run. A fixed directory name is intentional — no run isolation is needed when
  the VM itself provides isolation. The PIPELINE_RUN_DIR resolution order (Phase 1) always
  takes path 1 (env var) on CI, bypassing the state file and generation logic entirely —
  **but only because `PIPELINE_RUN_DIR` is set explicitly as shown above.**
- Update gh-pages mirror step to source from `$STAGED_DIR/release-tree` +
  `pages-include/` overlay (same as external pages distribution step).
- Update corpus distribution step to source from `$STAGED_DIR/release-tree`.
- Update pages distribution step to source from `$STAGED_DIR/release-tree` (currently uses `$OUTDIR/release-tree`).
- Update baseline step: read from `$STAGED_DIR/signature-inventory.json` instead of
  `$PUBLISH_DIR/signature-inventory.json`. Behavior unchanged: file will not exist on a
  fresh CI run, so stage 05d will run in first-run mode, same as always.
- Update static resource paths from `release-inputs/` to `static/release-inputs/`.
- **CI workflow hardcoded path:** the deploy job contains a hardcoded string
  `pages_include_dir="$GITHUB_WORKSPACE/release-inputs/pages-include"` that bypasses
  `config.py` entirely. This must be updated to `static/release-inputs/pages-include` in
  the same commit as the `PAGES_INCLUDE_DIR` constant update. If missed, the overlay will
  silently be skipped (source dir not found), producing a pages deployment without `.nojekyll`.
- Process-summary inline script (workflow lines ~720–900) — **full path migration required:**

  **CI path migration matrix for the process-summary step:**

  | Workflow location | Current assumption | Required update |
  |---|---|---|
  | Lines ~89–114: extractor contract check | `$WORKDIR/L1-raw/$MODULE_NAME` | **Changed** — extractors now write to `$PROCESSED_DIR/L1-raw/` (via `config.L1_RAW_WORKDIR`); update to `$PROCESSED_DIR/L1-raw/$MODULE_NAME` |
  | Lines ~143–144, ~254–255, ~411–412, ~483–484: scratch dirs | `$WORKDIR/extract-status/`, `$WORKDIR/extract-summary/`, `$WORKDIR/run-summary/` | **Unchanged** — ephemeral per-job scratch; intentionally lives under `downloads/` |
  | Lines ~187, ~296, ~455, ~463: artifact uploads | `${{ env.WORKDIR }}/L1-raw/` | **Changed** — extractor output is now at `$PROCESSED_DIR/L1-raw/`; update upload paths to `${{ env.PROCESSED_DIR }}/L1-raw/` |
  | Lines ~728–736: `required_paths` at outdir root | `Path("repo-manifest.json")`, `Path("cross-link-registry.json")` | **Remove** both entries — they no longer live at `staged/` root after Phase 3; the support-tree mirror versions already in `required_paths` provide the same check |
  | Lines ~752–755: L1/L2 glob counts | `outdir / "L1-raw"`, `outdir / "L2-semantic"` | Change to `processed_dir / "L1-raw"` and `processed_dir / "L2-semantic"`; add `processed_dir = Path(os.environ["PROCESSED_DIR"])` near top of inline script |
  | Lines ~757–758: support-tree raw/semantic counts | `(support_tree / "raw").glob(...)`, `(support_tree / "semantic-pages").glob(...)` | **Remove** and replace with `processed_dir / "L1-raw"` and `processed_dir / "L2-semantic"` glob counts |
  | Line ~897: process-summary artifact upload | `${{ env.WORKDIR }}/run-summary/` | **Unchanged** — scratch dir under downloads/ |

  **After updating the inline script:**
  - Add `processed_dir = Path(os.environ["PROCESSED_DIR"])` at the top of the inline Python block.
  - `l1_md`, `l1_meta` calculations must use `processed_dir / "L1-raw"`, not `outdir / "L1-raw"`.
  - `l2_md` calculation must use `processed_dir / "L2-semantic"`, not `outdir / "L2-semantic"`.
  - `repo-manifest.json` and `cross-link-registry.json` must be removed from the outdir-based
    `required_paths` list (they are no longer at staged root after Phase 3). The existing
    `support-tree/manifests/...` entries in `required_paths` continue to provide the same
    provenance check.
  - `support_raw_md` and `support_semantic_md` must be removed and their payload keys replaced
    with `l1_raw_md` and `l2_semantic_md` from `processed_dir`.
  - All other `required_paths` entries referencing `outdir / "..."` remain valid (staged/ still
    contains release-tree, support-tree, packages, and stage 05d outputs).
  - Leaving stale `support_tree/raw/` counts produces silent zeros — no error, just wrong
    numbers in the run summary artifact. Leaving stale `outdir / "repo-manifest.json"`
    in `required_paths` produces a silent false-fail on every run after Phase 3.

### Phase 10 — symlink fix (lib/output_sync.py)

Lines 297–304: `is_dir()` returns True for symlink-to-dir, so `shutil.rmtree()`
follows the symlink and deletes target contents.
Fix: add `_safe_remove_entry(path)` that checks `os.path.islink(path)` first
and calls `os.unlink()` for symlinks, `shutil.rmtree()` for real directories.

**Note:** in Python 3.8+, `shutil.rmtree()` automatically deletes a symlink
to a directory (the symlink itself, not target contents). The `_safe_remove_entry()`
fix remains valid as an explicit, version-independent guard.

**`lib/output_sync.py` shape constants — cleaned up in Phase 9 (not here):**
Lines 31–55 of `output_sync.py` define:
- `GENERATED_ROOT_REQUIRED_FILES` — includes `"repo-manifest.json"`, `"cross-link-registry.json"`
- `GENERATED_ROOT_REQUIRED_DIRS` — includes `"L1-raw"`, `"L2-semantic"`

All expected at OUTDIR root. `validate_generated_root()` uses these to check tree shape.
After Phase 3, those files/dirs move to `processed/manifests/` and `processed/` respectively.
The `promote-generated` CLI command (the primary external caller) is removed in Phase 9.
**Delete `GENERATED_ROOT_REQUIRED_FILES`, `GENERATED_ROOT_REQUIRED_DIRS`, and
`validate_generated_root()` in the same Phase 9 commit** (see coupling constraints at the
top of Implementation Phases). Do not defer to Phase 10 — leaving dead constants between
Phase 9 and 10 produces confusing test failures.
If left unchanged, any call to `validate_generated_root()` will always pass silently
(all paths it checks will simply not exist).

### Phase 11 — test discovery update

`tests/support/pytest_pipeline_support.py`:
- `OUTDIR` → `STAGED_DIR` from `pipeline-run-state.json` or env var.
- Two-tier resolution: env var `STAGED_DIR` → `tmp/pipeline-run-state.json`
  → hard error.

`tests/smoke/smoke_01_full_local_pipeline.py`:
- `work_dir` → inside `downloads/`
- `out_dir` → `staged/`
- Remove the hardcoded `"openwrt-condensed-docs"` string literal used as the output directory.
  Replace with the resolved `STAGED_DIR` path from config or state file.

**Test blast radius — explicit audit checklist:**

These test files contain hardcoded paths or assumptions that will break after the refactor.
Audit each before declaring Phase 11 complete:

| File | What breaks | Fix |
|------|-------------|-----|
| `pytest_01_workflow_contract_test.py` line ~170 | Asserts `promote-generated` step exists | Remove assertion; step is deleted in Phase 9 |
| `pytest_05_manage_ai_store_cli_test.py` line ~15 | Hardcodes `repo_root / "openwrt-condensed-docs"` | Update to `STAGED_DIR` path |
| `pytest_05_manage_ai_store_cli_test.py` line ~16 | Hardcodes `source_outdir / "L2-semantic"` | Update to `PROCESSED_DIR / "L2-semantic"` |
| `pytest_07_partial_rerun_guard_test.py` lines ~67–80 | Directly accesses `outdir / "L1-raw"` | Update to `PROCESSED_DIR / "L1-raw"` |
| `pytest_08_output_sync_test.py` lines ~306–321 | Tests `promote-generated` CLI command | Update or remove; command is deleted |
| `pytest_09_release_tree_contract_test.py` lines ~350–354 | Asserts on `./openwrt-condensed-docs/` prefixes | Update to `staged/release-tree/` prefix |
| `pytest_09_release_tree_contract_test.py` lines ~126–127 | Creates test fixtures at `outdir / "L1-raw"` and `outdir / "L2-semantic"` | Update fixture paths to `PROCESSED_DIR / "L1-raw"` and `PROCESSED_DIR / "L2-semantic"` |
| `pytest_10_routing_provenance_test.py` line ~241 | Uses `OUTDIR / "L2-semantic"` | Update to `PROCESSED_DIR / "L2-semantic"` |
| `tests/support/smoke_pipeline_support.py` line ~197 | Constructs `l1_root = os.path.join(workdir, "L1-raw")` | Update to `config.PROCESSED_DIR / "L1-raw"` |

**Pre-audit:** `grep -rn "openwrt-condensed-docs\|promote-generated\|OUTDIR\|L1-raw\|L2-semantic" tests/`
and enumerate every match. This list is a starting point, not a complete inventory.

### Phase 12 — gitignore and docs

- Do **not** hard-remove `staging/` and `openwrt-condensed-docs/` from `.gitignore`.
  Append a legacy comment instead:
  ```
  staging/                   # Legacy (Pre-V13) — safe to remove after all devs migrate
  openwrt-condensed-docs/    # Legacy (Pre-V13) — safe to remove after all devs migrate
  ```
  Hard-removing them immediately corrupts every active developer's `git status` with thousands
  of untracked files from older pipeline runs still on disk.
  **Removal criterion:** these legacy entries can be deleted once the next release ships with
  the new schema and no active branches still reference the old layout. Before deleting, verify:
  `git branch -r | xargs -I{} git log --oneline -1 {}` and check for any branches still using
  `staging/` or `openwrt-condensed-docs/`.
- Add `tmp/pipeline-run-state.json` and `tmp/.cache/` to `.gitignore`.
- Do **not** add `tmp/pipeline-*/` — the existing `tmp/` entry already covers all
  subdirectories. Adding `tmp/pipeline-*/` explicitly is redundant `.gitignore` bloat.
- Keep `tmp/` entry (covers logs/ and all run directories).
- Update `CLAUDE.md`, `DEVELOPMENT.md`, `docs/ARCHITECTURE.md`,
  `docs/specs/schema-definitions.md` to reflect new folder layout.
- Update `docs/specs/release-tree-contract.md`: update support-tree section to reflect that
  `raw/` and `semantic-pages/` subdirs have been dissolved. Support-tree now contains only
  `manifests/` and `telemetry/`. Note it now lives under `staged/` root.
- Delete the now-empty repo-root `content/` and `release-inputs/` parent directories
  after Phase 0 moves their contents. **Before deleting:** run `git ls-files content/ release-inputs/`
  to check for tracked `.gitkeep` files or orphaned image subdirectories. Delete only after
  confirming the tree is empty.

---

## Verification Commands (run after each phase)

```powershell
python tests/check_linting.py
python tests/run_pytest.py
python tests/run_smoke.py         # phase 8+ only (requires full run)
```

---

## Open Items / Deferred

- **support-tree partial dissolution (in scope — Phases 5 and 7):** `raw/` and `semantic-pages/`
  are dissolved in this refactor. `manifests/` and `telemetry/` are kept. Full dissolution
  (removing `manifests/` and `telemetry/` copies too) is a separate tracked task after this
  refactor ships — see Deferred section in the support-tree section above.
- **signature-inventory.json baseline for local dev:** currently the baseline step will never
  find the file on CI (no regression). For local development, automating the lookup of the
  previous run's staged dir via `pipeline-run-state.json` would enable local API drift tracking.
  Deferred — not blocking.
- **Incremental downloads:** long-term, the pipeline should only re-clone/scrape changed sources.
  Currently re-downloads everything. Defer — complex to implement correctly, low priority.
- **`data/base/` (AI store) write-back:** stage 04 writes to `static/data/base/`
  when `--run-ai` is active. This is the one exception to the "static is read-only" rule.
  Document explicitly in `static/README.md`. Future option: move the AI store to its own
  top-level folder outside `static/`.
- **Wiki scraper cache location (`WIKI_CACHE_DIR`, deferred):** after this refactor, the wiki
  scraper cache lands inside `downloads/.cache/` per-run (side effect of WORKDIR change). This
  breaks incremental scraping between local runs — every run re-scrapes all pages from scratch.
  Fix is documented in the Wiki Scraper Cache section (add `WIKI_CACHE_DIR` to `config.py`,
  update stage 02a's `get_cache_dir()`). Implement as standalone PR after this refactor ships.
  **Wiki cache expiry:** once the shared cache is at `tmp/.cache/`, a cache-bust policy
  (discard entries older than N days) is a further deferred improvement.
- **Folder name bikeshedding (deferred):** see "Alternative names" sections.
  Do not rename individual static sub-folders in this refactor.
- **`content/` and `release-inputs/` parent dirs:** after Phase 0 moves their contents into
  `static/`, the empty repo-root `content/` and `release-inputs/` directories are deleted.
  Run `git ls-files content/ release-inputs/` first to verify no tracked `.gitkeep` files or
  orphaned image subdirectories remain. See Phase 12 cleanup step.
