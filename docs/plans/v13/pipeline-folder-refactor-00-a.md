

   

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/lib/config.py#1-1), lines 1 to 50

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/workflows/openwrt-docs4ai-00-pipeline.yml#1-1), lines 1 to 50

Searched for regex `WORKDIR|OUTDIR` (`**/lib/config.py`), 16 results

Searched for regex `symlink|os\.symlink|\.symlink_to|is_symlink`, 20 results

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/lib/config.py#50-50), lines 50 to 63

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/workflows/openwrt-docs4ai-00-pipeline.yml#900-900), lines 900 to 1000

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/workflows/openwrt-docs4ai-00-pipeline.yml#1000-1000), lines 1000 to 1100

Searched for regex `OUTDIR|WORKDIR` (`**/.github/scripts/*.py`), 50 results

Searched for files matching `**/.github/scripts/openwrt-docs4ai-*.py`, 20 matches

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/scripts/openwrt-docs4ai-07-generate-web-index.py#25-25), lines 25 to 50

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/scripts/openwrt-docs4ai-07-generate-web-index.py#640-640), lines 640 to 800

Searched for regex `OUTDIR|WORKDIR|release.tree|support.tree` (`**/.github/scripts/openwrt-docs4ai-05a*.py`), 20 results

Searched for regex `OUTDIR|WORKDIR` (`**/.github/scripts/openwrt-docs4ai-06*.py`), 19 results

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/scripts/openwrt-docs4ai-07-generate-web-index.py#550-550), lines 550 to 650

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/workflows/openwrt-docs4ai-00-pipeline.yml#700-700), lines 700 to 900

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/workflows/openwrt-docs4ai-00-pipeline.yml#600-600), lines 600 to 700

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/workflows/openwrt-docs4ai-00-pipeline.yml#50-50), lines 50 to 600

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/lib/output_sync.py#245-245), lines 245 to 270

Searched for regex `OUTDIR|WORKDIR|staging|openwrt.condensed` (`**/tests/smoke/*.py`), 14 results

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/tests/smoke/smoke_01_full_local_pipeline.py#75-75), lines 75 to 100

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/tests/smoke/smoke_00_post_extract_pipeline.py#40-40), lines 40 to 85

Now I have a comprehensive picture of the entire pipeline's I/O flow, directory structure, and the inconsistencies. Let me compose the analysis.

---

## Pipeline Architecture Audit: Comprehensive I/O Map and Improvement Plan

### 1. Current Pipeline I/O Map (Every Stage, Every Folder)

| Stage | Script | Reads From | Writes To | Notes |
|-------|--------|-----------|-----------|-------|
| **01** | `01-clone-repos.py` | GitHub (network) | `WORKDIR/repo-ucode/`, `WORKDIR/repo-luci/`, `WORKDIR/repo-openwrt/`, `WORKDIR/repo-manifest.json` | Shallow clones. CI uploads as `L0-repos` artifact. |
| **02a** | `02a-scrape-wiki.py` | OpenWrt wiki (network), `WORKDIR/.cache/` | `WORKDIR/L1-raw/wiki/` | Runs in parallel with 01 on CI. Uses wiki cache. |
| **02b** | `02b-scrape-ucode.py` | `WORKDIR/repo-ucode/` | `WORKDIR/L1-raw/ucode/` | Needs jsdoc-to-markdown. |
| **02c** | `02c-scrape-jsdoc.py` | `WORKDIR/repo-luci/` | `WORKDIR/L1-raw/luci/` | Needs jsdoc-to-markdown. |
| **02d** | `02d-scrape-core-packages.py` | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/openwrt-core/` | Skip-gated by SKIP_BUILDROOT. |
| **02e** | `02e-scrape-example-packages.py` | `WORKDIR/repo-luci/` | `WORKDIR/L1-raw/luci-examples/` | |
| **02f** | `02f-scrape-procd-api.py` | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/procd/` | |
| **02g** | `02g-scrape-uci-schemas.py` | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/uci/` | |
| **02h** | `02h-scrape-hotplug-events.py` | `WORKDIR/repo-openwrt/` | `WORKDIR/L1-raw/openwrt-hotplug/` | |
| **02i** | `02i-ingest-cookbook.py` | cookbook-source (repo) | `WORKDIR/L1-raw/cookbook/` | Source is in-repo, not a clone. |
| **03** | `03-normalize-semantic.py` | `WORKDIR/L1-raw/`, `WORKDIR/repo-manifest.json`, `WORKDIR/cross-link-registry.json` | `OUTDIR/L1-raw/` (copy), `OUTDIR/L2-semantic/`, `OUTDIR/repo-manifest.json`, `OUTDIR/cross-link-registry.json` | Promotes L1 into OUTDIR and generates L2. |
| **04** | `04-generate-ai-summaries.py` | `OUTDIR/L2-semantic/`, base, override | `OUTDIR/L2-semantic/` (enriched), base (AI store) | Optional. AI store is in-repo (data). |
| **05a** | `05a-assemble-references.py` | `OUTDIR/L2-semantic/` | `OUTDIR/{module}/`, `OUTDIR/release-tree/{module}/` | Flat module dirs + release-tree module dirs. |
| **05b** | `05b-generate-agents-and-readme.py` | `OUTDIR/` | `OUTDIR/AGENTS.md`, `OUTDIR/README.md`, `OUTDIR/release-tree/AGENTS.md`, `OUTDIR/release-tree/README.md` | |
| **05c** | `05c-generate-ucode-ide-schemas.py` | `OUTDIR/L2-semantic/ucode/` | `OUTDIR/ucode/`, `OUTDIR/release-tree/ucode/types/` | TypeScript `.d.ts`. |
| **05d** | `05d-generate-api-drift-changelog.py` | `OUTDIR/`, `baseline/` | `OUTDIR/CHANGES.md`, `OUTDIR/changelog.json`, `OUTDIR/signature-inventory.json` | Telemetry. |
| **05e** | `05e-generate-luci-dts.py` | `OUTDIR/L2-semantic/luci/` | `OUTDIR/luci/`, `OUTDIR/release-tree/luci/types/` | TypeScript `.d.ts`. |
| **06** | `06-generate-llm-routing-indexes.py` | `OUTDIR/` (whole tree) | `OUTDIR/llms.txt`, `OUTDIR/llms-full.txt`, `OUTDIR/{module}/llms.txt`, `OUTDIR/release-tree/llms.txt`, `OUTDIR/release-tree/llms-full.txt`, `OUTDIR/release-tree/{module}/llms.txt` | |
| **07** | `07-generate-web-index.py` | `OUTDIR/` (filesystem walk) | `OUTDIR/index.html`, `OUTDIR/release-tree/index.html`, `OUTDIR/support-tree/` (materialized) | The HTML page, release index, and support-tree copy. |
| **08** | `08-validate-output.py` | `OUTDIR/` (whole tree) | Nothing (validation only) | Validation gate. Returns exit code. |

**CI Deploy Job (post-validation):**

| Step | Reads From | Writes To |
|------|-----------|-----------|
| Download staging artifact | GHA artifact store | `OUTDIR/` (= `$GITHUB_WORKSPACE/staging`) |
| Promote staging | `OUTDIR/` | `$GITHUB_WORKSPACE/openwrt-condensed-docs` ← **THIS** |
| Mirror to gh-pages | `$GITHUB_WORKSPACE/openwrt-condensed-docs` | `gh-pages` branch |
| Mirror to corpus repo | `OUTDIR/release-tree/` | `openwrt-docs4ai/corpus` |
| Mirror to pages repo | `OUTDIR/release-tree/` | `openwrt-docs4ai/openwrt-docs4ai.github.io` |
| Build ZIP | `OUTDIR/release-tree/` | `$RUNNER_TEMP/openwrt-docs4ai-YYYY-MM-DD.zip` |

---

### 2. The Irrationalities

#### 2A. The `PUBLISH_DIR` promotion step is vestigial

The deploy job does this:
1. Downloads staging artifact → `OUTDIR` (= `$GITHUB_WORKSPACE/staging`)
2. Promotes `OUTDIR` → `$GITHUB_WORKSPACE/openwrt-condensed-docs`
3. Mirrors `$GITHUB_WORKSPACE/openwrt-condensed-docs` → `gh-pages` branch
4. Separately mirrors `OUTDIR/release-tree/` → corpus repo and pages repo
5. Separately builds ZIP from `OUTDIR/release-tree/`

Steps 4 and 5 read directly from `OUTDIR`. Only step 3 reads from `PUBLISH_DIR`. The `PUBLISH_DIR` materialization exists **solely** to serve the gh-pages mirror of the full tree (which includes L1-raw, L2-semantic, etc. for test preview purposes). Steps 4 and 5 already bypass it.

**Why this is irrational:** You're copying the entire tree to a second location in the workspace just to serve one downstream consumer (gh-pages). The gh-pages mirror step could read directly from `OUTDIR` like everything else does.

#### 2B. The root `index.html` hardcodes a display prefix disconnected from reality

07-generate-web-index.py hardcodes:
```python
PUBLISH_PREFIX = "./openwrt-condensed-docs"
```

This string appears in every link in the root `index.html`. Stage 08 then **validates** that this exact string is present. But the `index.html` is generated by walking `OUTDIR/` at runtime. The links already use `href` values relative to the current directory. The display text using a fixed prefix from a different era is cosmetic fiction — it shows link text as `./openwrt-condensed-docs/L2-semantic/wiki/...` when the file actually lives at `./L2-semantic/wiki/...` relative to the `index.html`.

**Why this is irrational:** The display prefix pretends the files are in a directory named `openwrt-condensed-docs` when they're not. The `href` is correct (relative), but the visible label lies about the path. If the output folder name matters for display, read it dynamically from the actual output location.

#### 2C. Stage 08 validates the ghost name

08-validate-output.py requires `./openwrt-condensed-docs/` to appear in root `index.html` and requires it to NOT appear in `release-tree/index.html`. This is now validating a hardcoded string that has no architectural meaning — it's just checking that stage 07 wrote the same hardcoded string that stage 08 expects.

#### 2D. Smoke test `smoke_01` hardcodes the old output name

smoke_01_full_local_pipeline.py:
```python
out_dir = os.path.join(temp_dir, "openwrt-condensed-docs")
```

Meanwhile `smoke_00` correctly uses `os.path.join(temp_dir, "out")`. The tests disagree about what to call the output directory, and `smoke_01` chose the old name for no reason.

#### 2E. Two separate directory trees (`WORKDIR` and `OUTDIR`) scattered at repo root

Currently on CI:
- `WORKDIR` = `$GITHUB_WORKSPACE/tmp`
- `OUTDIR` = `$GITHUB_WORKSPACE/staging`

Locally:
- `WORKDIR` = tmp (relative to repo root)
- `OUTDIR` = staging (relative to repo root)

These are two peer directories at the repo root. L1 data starts in `WORKDIR/L1-raw/` and then gets **copied** into `OUTDIR/L1-raw/` by stage 03. That's a full copy of all extracted markdown from one sibling directory to another. The only reason `WORKDIR` and `OUTDIR` are separate is that extractors (01-02) write to `WORKDIR` and later stages (03+) write to `OUTDIR`, so they evolved as separate roots.

---

### 3. Symlinks: Does This Project Need Them?

The answer is **no, this project does not create or use symlinks.** Every reference to "symlink" in the codebase falls into two categories:

1. **Defensive code in output_sync.py:** The sync logic skips source symlinks and handles destination symlinks defensively. This is pure safety code for dealing with cloned upstream repos or corrupted state.

2. **Documentation content:** The word "symlink" appears ~25 times in the generated wiki documentation (e.g., wiki-complete-reference.part-02.md) because OpenWrt itself uses symlinks in `/etc/rc.d/`. This is content the pipeline processes, not something the pipeline creates.

The pipeline **never creates symlinks**. No stage script calls `os.symlink()` or `Path.symlink_to()`. The defensive code in output_sync.py exists only because the upstream git repos being cloned might contain symlinks, and a robust tree-copy function should not blindly follow them.

**Recommendation:** The symlink handling in output_sync.py is correct defensive programming, but it should be complete (fix the gap). Since the pipeline never creates symlinks, the fix is about correctness of the safety layer, not about a feature the pipeline uses.

---

### 4. Local vs. CI: What Should Be Identical and What Differs

**What MUST be identical:**
- The pipeline scripts (01-08) and their behavior
- The directory structure inside the working tree (`L1-raw/`, `L2-semantic/`, `release-tree/`, `support-tree/`)
- The validation gate (08)
- The output contract (what files exist, what they contain)

**What legitimately differs:**

| Concern | CI | Local | Should they align? |
|---------|----|-|---|
| Where `WORKDIR` lives | `$GITHUB_WORKSPACE/tmp` | tmp | Already aligned (both ephemeral) |
| Where `OUTDIR` lives | `$GITHUB_WORKSPACE/staging` | staging | Problem: local staging accumulates stale data across runs |
| Clean filesystem | Fresh VM every run | **Not clean** — stale files from previous runs remain | **Must fix** |
| Post-validation promotion | `OUTDIR` → `PUBLISH_DIR` → gh-pages | Not done locally | Acceptable — local doesn't publish |

**The clean filesystem problem is the core issue.** CI gets a clean runner every time. Local runs write into staging and tmp which may have files from previous runs. This means:
- Tests may inspect stale output from a previous run
- Stage 05a has a guard against partial release-tree rebuilds, but it's checking against stale state
- The "skip if no fresh output" pattern in tests is a workaround for this problem, not a solution

---

### 5. The Rational Architecture

If building from scratch, here's how the pipeline working directories should work:

#### Single ephemeral run directory per execution

Every pipeline run — local or CI — should create one timestamped run directory under tmp:

```
tmp/
  run-YYYYMMDD-HHMMSS/          # or run-{uuid}/
    work/                        # WORKDIR - clones, L1-raw, caches
      repo-ucode/
      repo-luci/
      repo-openwrt/
      repo-manifest.json
      cross-link-registry.json
      L1-raw/
        wiki/
        ucode/
        ...
    out/                         # OUTDIR - all generated output
      L1-raw/                    # copied from work/L1-raw by stage 03
      L2-semantic/
      release-tree/
      support-tree/
      llms.txt
      llms-full.txt
      index.html
      AGENTS.md
      README.md
      ...
```

**Rationale:**
- One parent directory per run, always clean, always isolated
- `work/` and `out/` are siblings inside the run directory — no scattered repo-root directories
- No risk of stale data contamination
- User can inspect any previous run by browsing `tmp/run-*/`
- User manages tmp size themselves (delete old runs as needed)
- CI behaves identically: `WORKDIR=$GITHUB_WORKSPACE/tmp/run-$RUN_ID/work`, `OUTDIR=$GITHUB_WORKSPACE/tmp/run-$RUN_ID/out`
- Gitignore covers tmp already

#### Eliminate the `PUBLISH_DIR` promotion step

The deploy job should mirror directly from `OUTDIR`:
- gh-pages mirror: read from `OUTDIR` directly
- External repos: already read from `OUTDIR/release-tree/` directly
- ZIP: already reads from `OUTDIR/release-tree/` directly

This eliminates the entire `PUBLISH_DIR` concept, the `openwrt-condensed-docs` name from the workflow, and the confusing documentation about "no tracked publish root" vs. "CI materializes a temporary publish root."

#### Make the display prefix dynamic

Stage 07 should derive the display prefix from the actual output directory name, or simply not use a display prefix at all since the `href` values are already relative. If a display prefix is desired for human readability, read it from config or derive it from `OUTDIR`.

Stage 08 should validate that links work (relative hrefs resolve to real files), not that a specific hardcoded string appears in the HTML.

#### Eliminate staging as a repo-root directory

With per-run directories under tmp, there's no need for staging at the repo root. One less gitignore rule, one less directory to explain, one less source of confusion.

---

### 6. Improvement Plan

**Phase 1: Clean filesystem guarantee (the most impactful fix)**

1. Add a run-directory factory to config.py:
   - `create_run_dir()` → creates `tmp/run-YYYYMMDD-HHMMSS/` with `work/` and `out/` subdirs
   - Sets `WORKDIR` and `OUTDIR` to point inside it
   - Returns the run dir path
   - If env vars are already set (CI), use those instead
2. Update smoke tests to use the factory (smoke_00 already does something similar with `tempfile.mkdtemp`)
3. Update config.py defaults: `WORKDIR` and `OUTDIR` should not default to repo-root peers; they should default to a fresh run dir under tmp

**Phase 2: Eliminate `PUBLISH_DIR` from CI**

1. Change the gh-pages mirror step to read from `$OUTDIR` directly instead of from `$GITHUB_WORKSPACE/$PUBLISH_DIR`
2. Remove the "Promote staging to workspace" step entirely
3. Remove `PUBLISH_DIR` from workflow env vars
4. Remove `openwrt-condensed-docs` from .gitignore (no longer needed)

**Phase 3: Make display prefix dynamic and fix validation**

1. In stage 07: derive `PUBLISH_PREFIX` from `OUTDIR` or make it a config constant, or (best) remove it entirely and display paths relative to the index.html location
2. In stage 08: remove the `./openwrt-condensed-docs/` string check from `validate_index_html_contract`; replace with a check that all hrefs in root index.html resolve to real files in `OUTDIR`
3. In stage 08: remove the `openwrt-condensed-docs` reference from `validate_release_tree_contract`'s legacy-name check (it's checking for its own display prefix, not a real legacy artifact)

**Phase 4: Cleanup**

1. Remove openwrt-condensed-docs-renamed from git tracking
2. Fix the symlink deletion gap in output_sync.py (trivial)
3. Fix `smoke_01` to not hardcode `openwrt-condensed-docs` as its output dir name
4. Update docs (CLAUDE.md, ARCHITECTURE.md) to describe the run-directory model
5. Widen .gitignore to `openwrt-condensed-docs*/` as interim protection

---

### 7. Trade-off: Fresh directory per run vs. delete-and-recreate

| Approach | Pros | Cons |
|----------|------|------|
| **Fresh timestamped dir** (`tmp/run-YYYYMMDD-HHMMSS/`) | Always clean, previous runs preserved for inspection, no deletion risk, matches CI model exactly | tmp grows over time; user must prune |
| **Delete target before run** (`rm -rf staging/ && mkdir staging/`) | Simple, no accumulation | Destructive — one wrong path and you delete real files; doesn't match CI model (CI never deletes); loses previous run output; can't diff between runs |

**Recommendation: Fresh timestamped directory.** The whole point of your argument is that CI uses clean filesystems every time. The way to replicate that locally is to create a new directory every time, not to simulate it by deleting the old one. If users want to inspect a previous run, it's still there. If they want to save space, `rm -rf tmp/run-2026*/` is safe and obvious.

The only convenience question is "which run should `pytest` inspect?" The answer: the latest one. A `get_latest_run_dir()` helper can find the most recent `tmp/run-*/out/` directory, or tests can skip if none exists (which they already do).

---

### 8. What About the Existing tmp Contents?

The tmp directory already exists and contains a mix of CI artifact downloads, old test runs, manual debugging output, and other scratch. The new run-directory model would coexist cleanly:

```
tmp/
  run-20260328-143000/    # new structure
    work/
    out/
  ci/                     # existing CI artifact downloads
  deleted-files/          # existing backup
  ...                     # other existing scratch
```

No conflict. Old patterns keep working until they're migrated.

---

### Summary

The core architectural changes needed, in priority order:

1. **Per-run directory under tmp** — guarantees clean local runs, eliminates stale data, matches CI
2. **Remove `PUBLISH_DIR` indirection** — gh-pages mirror reads from `OUTDIR` directly
3. **Dynamic display prefix or remove it** — stage 07 shouldn't hardcode a dead directory name
4. **Align validation** — stage 08 checks link validity, not hardcoded strings
5. **Cleanup** — remove tracked renamed tree, fix symlink gap, fix smoke_01 naming, update docs

Every one of these changes makes the pipeline more rational, more testable, and easier to explain. None of them change what the pipeline produces — they only change where and how it stages files during execution. 

