Searched codebase for "1. pipeline map
the first problem I see is the pipeline writing to multiple folders. the pipeline only deliverable goes in one folder, so there should be no need for multiple folders. we should write to WORKDIR and there should be our whole written folder structure within that. WORKDIR for example could have an INPUT folder for the downloaded stuff, an output or outdir folder for generated stuff, and maybe within WORKDIR or within OUTPUT there would be a release-tree folder, and there could even be a temp folder in WORKDIR. you get my point. all writes should be controlled and understood in one location. and reads can of course come from many places elsewhere. I bet professional pipelines are VERY explicit about this stuff; they probably have workdir\input\, workdir\output\temp\, workdir\output\deliverables\zip\, workdir\output\deliverables\release-tree, and so on. very explicit and everyone knows that everything has its place with no room for error or assumptions. 

2. irrationalities
2a. agreed
2b. agreed
2c. agreed
2d. agreed
2e. agreed

3. symlinks
agreed. the defensive programming is fine, but we must finish that architecture and process the possibility of symlinks correctly, which presumably means that we just cut them off and they are not included. if anyone wants a symlinked document they can get it themselves or report it. we don't need to have every random document in the universe in this project. we should not get hung up on symlinks.

4. local vs ci
about folder names: my idea for the one written folder of the pipeline to be named something like pipeline-date-UTCtime so that each local test run gets its own fresh virtual environment like the CI does, with no risk of multiple runs getting the same folder.
about promotion: if it makes sense logically, we can run the same promotion step locally because it's presumably just a file more/copy, right? and then we could keep more of the pipeline the same and run the same tests at the same point? or is this esoteric?

5. rational architecture
it looks like we are closing in on the same ideas.

6. improvement plan
I like your first draft. let's work on it even more with adjustments from my comments this message.

7. let's settle on fresh timestamped dir. the pipeline output isnt very large to worry about file system usage.

8.
agreed about leaving the old tmp junk alone

good work! now develop a new fleshed out detailed plan/prompt for making all of our discussed changes. be explicit such that the implementing agent doesn't make mistakes or hallucinate its way into more illogical nonsense architecture.", no results



   

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/lib/config.py)

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/tests/support/pytest_pipeline_support.py#1-1), lines 1 to 40

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/lib/output_sync.py#245-245), lines 245 to 310

Searched for regex `PUBLISH_PREFIX|PUBLISH_DIR`, 40 results

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/tests/support/smoke_pipeline_support.py#240-240), lines 240 to 300

Searched for regex `BASELINE_DIR|baseline` (`**/.github/workflows/*.yml`), 7 results

Read [](file:///c%3A/Users/MC/Documents/AirSentinel/openwrt-docs4ai-pipeline/.github/workflows/openwrt-docs4ai-00-pipeline.yml#625-625), lines 625 to 640

Searched for regex `openwrt.condensed|OUTDIR|WORKDIR` (`**/tests/smoke/smoke_01*.py`), 3 results

Now I have all the details I need. Let me also check one thing about the baseline step — it reads from `PUBLISH_DIR` which is the old committed tree (now gone from main). This is another place that needs fixing. 

Searched for regex `BASELINE|baseline` (`**/.github/scripts/openwrt-docs4ai-05d*.py`), 20 results

Good. Now I have the full picture including the baseline step. Let me write the comprehensive plan.

---

## Implementation Plan: Pipeline Workspace Rationalization

This is an explicit, step-by-step plan for refactoring the pipeline's directory structure. The implementing agent must follow each step exactly. No creative interpretation. No adding features. No "improving" things not listed here.

### Goal

Unify all pipeline working state under a single timestamped run directory per execution. Eliminate scattered repo-root directories (staging, tmp as `WORKDIR`). Remove the vestigial `PUBLISH_DIR` promotion step. Make display prefixes dynamic. Fix the symlink deletion bug. Remove tracked generated output. Update docs to match the new reality.

---

### Target Directory Layout

Every pipeline run — local or CI — writes to this structure:

```
tmp/
  pipeline-YYYYMMDD-HHMMSSz/       # one per run, UTC timestamp
    input/                          # was WORKDIR: clones, L1-raw, caches
      repo-ucode/
      repo-luci/
      repo-openwrt/
      repo-manifest.json
      cross-link-registry.json
      .cache/                       # wiki cache etc
      L1-raw/
        wiki/
        ucode/
        luci/
        ...
    output/                         # was OUTDIR: all generated results
      L1-raw/                       # stage 03 copies from input/L1-raw
      L2-semantic/
      release-tree/                 # the public deliverable
        {module}/
          llms.txt
          map.md
          bundled-reference.md
          chunked-reference/
          types/                    # .d.ts files when applicable
        llms.txt
        llms-full.txt
        AGENTS.md
        README.md
        index.html
      support-tree/                 # internal support state
        raw/
        semantic-pages/
        manifests/
        telemetry/
      llms.txt                      # root routing (staging-level)
      llms-full.txt
      AGENTS.md
      README.md
      index.html
      repo-manifest.json
      cross-link-registry.json
      {module}/                     # flat module dirs (internal/legacy)
        llms.txt
      CHANGES.md
      changelog.json
      signature-inventory.json
```

**CI adapts by setting env vars:**
- `WORKDIR=$GITHUB_WORKSPACE/tmp/pipeline-ci/input`
- `OUTDIR=$GITHUB_WORKSPACE/tmp/pipeline-ci/output`

CI doesn't need timestamps because each run already gets a clean VM. The name `pipeline-ci` is fixed for simplicity on CI.

**Local runs** auto-create `tmp/pipeline-YYYYMMDD-HHMMSSz/` and set `WORKDIR` and `OUTDIR` from that.

---

### Prerequisite Context for the Implementing Agent

**Files that define current path logic (must read before editing):**

| File | What it does |
|------|-------------|
| config.py | Defines `WORKDIR`, `OUTDIR`, all computed paths. Currently defaults: `WORKDIR="tmp"`, `OUTDIR="staging"` |
| openwrt-docs4ai-00-pipeline.yml | CI workflow. Currently has `WORKDIR: ${{ github.workspace }}/tmp`, `OUTDIR: ${{ github.workspace }}/staging`, `PUBLISH_DIR: openwrt-condensed-docs` |
| openwrt-docs4ai-01-clone-repos.py | Reads `WORKDIR` directly from env, NOT from `config.WORKDIR` (line 28: `WORKDIR = os.environ.get("WORKDIR", os.path.join(os.getcwd(), "tmp"))`) |
| openwrt-docs4ai-07-generate-web-index.py | Hardcodes `PUBLISH_PREFIX = "./openwrt-condensed-docs"` on line 35. Used as display text in HTML links. |
| openwrt-docs4ai-08-validate-output.py | Validates `"./openwrt-condensed-docs/"` appears in root `index.html` (line 169). Validates it does NOT appear in release-tree `index.html` (line 205). Checks for `"openwrt-condensed-docs"` in release-tree root files (line 403). |
| output_sync.py | Tree sync logic. Symlink bug at lines 297-304. |
| sync_tree.py | CLI wrapper for output_sync. Has `promote-generated` subcommand used by CI. |
| smoke_01_full_local_pipeline.py | Hardcodes `out_dir = os.path.join(temp_dir, "openwrt-condensed-docs")` (line 87). |
| smoke_00_post_extract_pipeline.py | Correctly uses `os.path.join(temp_dir, "out")`. |
| pytest_pipeline_support.py | `OUTDIR = PROJECT_ROOT / os.environ.get("OUTDIR", "staging")` (line 13). |
| smoke_pipeline_support.py | Has `publish_root(outdir)` returning `outdir/release-tree`. |
| .gitignore | Has staging, tmp, `openwrt-condensed-docs/`. |

**Files that must NOT be changed (read-only inputs):**

| File | Why |
|------|-----|
| `content/cookbook-source/*.md` | Authored source content |
| base, override | AI store (persistent across runs) |
| release-inputs | Static overlays for release packaging |
| templates | Static templates |

---

### Step-by-Step Implementation

#### Phase 1: Core path refactor in config.py

**File: config.py**

1. **Add a `create_run_dir()` function** that:
   - Generates a UTC timestamp string: `YYYYMMDD-HHMMSSz` (example: `20260328-143052z`)
   - Creates `tmp/pipeline-{timestamp}/input/` and `tmp/pipeline-{timestamp}/output/`
   - Returns the run dir path (e.g., `tmp/pipeline-20260328-143052z/`)
   - This function is NOT called at import time. It is only called by test runners and local entry points.

2. **Change defaults:**
   - Remove the current `WORKDIR = os.environ.get("WORKDIR", "tmp")` default
   - Remove the current `OUTDIR = os.environ.get("OUTDIR", "staging")` default
   - New behavior: If `WORKDIR` env var is set, use it. If `OUTDIR` env var is set, use it. If neither is set, call `create_run_dir()` once to create a fresh timestamped directory and set both from it.
   - Guard against double-creation: use a module-level `_run_dir_created` flag.

3. **Update computed paths** — no changes needed here since they derive from `WORKDIR` and `OUTDIR` which will now point to the right places.

4. **Update `ensure_dirs()`** — it currently creates `WORKDIR`, `OUTDIR`, `L1_RAW_WORKDIR`, `L2_SEMANTIC_WORKDIR`. This stays the same, just pointing to new locations.

**Critical constraint:** config.py is imported by every pipeline script at module load time. The `WORKDIR` and `OUTDIR` module-level variables must still be set at import time. The auto-creation of run dirs should happen at import time only when env vars are not set. When env vars ARE set (CI, tests), no auto-creation happens.

#### Phase 2: Update CI workflow

**File: openwrt-docs4ai-00-pipeline.yml**

1. **Change env vars** (top-level `env:` block, currently lines 31-37):
   ```yaml
   env:
     WORKDIR: ${{ github.workspace }}/tmp/pipeline-ci/input
     OUTDIR: ${{ github.workspace }}/tmp/pipeline-ci/output
     DIST_PAGES_REPO: openwrt-docs4ai/openwrt-docs4ai.github.io
     DIST_RELEASE_REPO: openwrt-docs4ai/corpus
     DIST_TARGET_BRANCH: main
     DIST_ZIP_ROOT_DIR: openwrt-docs4ai
   ```
   - Remove `PUBLISH_DIR: openwrt-condensed-docs` entirely.

2. **Fix the "Prepare Baseline" step** (currently line 628-635):
   - It currently reads from `$PUBLISH_DIR/signature-inventory.json` — a directory that no longer exists on a clean runner.
   - Change to: Use the GHA cache or the previous run's artifact. Since the baseline comes from the *previous* CI run's output, it should be fetched from the `ai-cache` or a dedicated baseline artifact, NOT from a directory in the workspace.
   - Simplest fix: download the `final-staging` artifact from the previous successful run, or use the existing `restore-keys` cache pattern. But the current implementation already fails safely (prints "No baseline inventory found"), so the simplest correct fix is to just remove the `$PUBLISH_DIR` reference and have it always start with no baseline. The drift changelog will show "no baseline" which is truthful.
   - Replace with:
     ```yaml
     - name: Prepare Baseline
       run: |
         mkdir -p baseline
         echo "No baseline inventory; drift changelog will report a clean start."
     ```
   - **Note:** If baseline preservation across runs is important, a separate improvement can add it via GHA artifacts later. Do NOT complicate this refactor with it.

3. **Remove the "Promote staging to workspace" step** (currently line 937-940):
   - Delete the entire step. The gh-pages mirror and external distribution steps will read from `$OUTDIR` directly.

4. **Update the "Publish GitHub Pages branch mirror" step** (currently line 942+):
   - Change `publish_root="$GITHUB_WORKSPACE/$PUBLISH_DIR"` to `publish_root="$OUTDIR"`
   - All subsequent references to `publish_root` in that step remain unchanged.

5. **Update artifact upload/download paths:**
   - The `Upload L0 Repos & Manifest` step uploads from `$WORKDIR` which now includes `/input` — the glob patterns `${{ env.WORKDIR }}/repo-*` and `${{ env.WORKDIR }}/repo-manifest.json` will still work because repos are inside `input/` which is now `WORKDIR`.
   - The `Download L0` step downloads to `${{ env.WORKDIR }}` — correct.
   - The `Download all L1 results` step downloads to `${{ env.WORKDIR }}/L1-raw/` — correct.
   - The `Upload Final Staging` step uploads from `${{ env.OUTDIR }}` — correct.
   - The deploy job `Download Staging` step downloads to `${{ env.OUTDIR }}` — correct.

6. **Update the extract jobs' `mkdir` commands:**
   - The `initialize` job has `mkdir -p "$WORKDIR"`. This creates the `input/` directory. Correct.
   - Extract jobs create `$WORKDIR/L1-raw/` etc. Correct because `WORKDIR` now points to `input/`.

#### Phase 3: Fix stage 07 display prefix

**File: openwrt-docs4ai-07-generate-web-index.py**

1. **Remove the hardcoded `PUBLISH_PREFIX`** (line 35).
2. **Replace with dynamic derivation:** The root `index.html` displays the staged output tree. Since it lives at `OUTDIR/index.html` and links point to `./L2-semantic/...`, `./release-tree/...`, etc., the display prefix should simply be `"."` (current directory). There is no reason to pretend the files are elsewhere.
   - Change line 35 to: `PUBLISH_PREFIX = "."`
3. **Update `render_section`** (around line 616-620): The display path `f"{PUBLISH_PREFIX}/{rel_path}"` becomes `f"./{rel_path}"` which is truthful — the link displays the same path the `href` uses.
4. **Update the HTML title and heading** (lines 654, 761): Change `"openwrt-condensed-docs staging tree"` to `"openwrt-docs4ai pipeline output"` or similar. This is cosmetic but removes the dead name.
5. **Update the description paragraph** (line 765): Change the text referencing `PUBLISH_PREFIX` to simply say it mirrors the staged output tree.

#### Phase 4: Fix stage 08 validation

**File: openwrt-docs4ai-08-validate-output.py**

1. **Fix `validate_index_html_contract`** (line 165-175):
   - Remove the check `if "./openwrt-condensed-docs/" not in content:` — this validates a dead hardcoded string.
   - Replace with: validate that the root `index.html` contains at least one `href` and that all `href` values resolve to real files in `outdir`. The existing `actual_links` vs `expected_links` comparison already does this (lines 176-195). Just remove the hardcoded string check.

2. **Fix `validate_release_index_html_contract`** (line 200-205):
   - Remove the check `if "./openwrt-condensed-docs/" in content:` — this validates absence of a string that stage 07 no longer emits.
   - The existing link-vs-filesystem comparison already validates correctness.

3. **Fix `validate_release_tree_contract`** (line 370):
   - The check `if dir_name in {"L1-raw", "L2-semantic", "openwrt-condensed-docs", support_tree_name}:` is fine — it checks that release-tree doesn't contain legacy dirs. Keep `"openwrt-condensed-docs"` in this set as a legacy guard.

4. **Fix the root file leak check** (line 403):
   - The check `if "openwrt-condensed-docs" in content:` on release-tree root files validates that the legacy name doesn't leak into public deliverables. This check is still valid and should remain — it catches if someone accidentally introduces the old name into the release-tree output.

#### Phase 5: Fix symlink deletion bug in output_sync.py

**File: output_sync.py**

1. **Extract a helper** (add near line 245):
   ```python
   def _safe_remove_entry(path: Path) -> None:
       """Remove a filesystem entry safely, handling symlinks first."""
       if path.is_symlink():
           path.unlink()
       elif path.is_dir():
           shutil.rmtree(path)
       else:
           path.unlink()
   ```

2. **Use it in the node-type conflict branch** (lines 282-285): Replace:
   ```python
   if dst_entry.is_symlink() or not dst_is_dir:
       dst_entry.unlink()
   else:
       shutil.rmtree(dst_entry)
   ```
   with:
   ```python
   _safe_remove_entry(dst_entry)
   ```

3. **Use it in the delete-extraneous branch** (lines 300-303): Replace:
   ```python
   if dst_entry.is_dir():
       shutil.rmtree(dst_entry)
   else:
       dst_entry.unlink()
   ```
   with:
   ```python
   _safe_remove_entry(dst_entry)
   ```

4. **Add a regression test** in pytest_08_output_sync_test.py:
   - Create a test that:
     - Sets up a source dir with one file
     - Sets up a destination dir with an extraneous symlink pointing to a real directory
     - Calls `sync_tree(src, dst, delete_extraneous=True)`
     - Asserts the symlink was removed (not the target directory)
     - Asserts the target directory still exists and is unmodified

#### Phase 6: Fix smoke tests

**File: smoke_01_full_local_pipeline.py**

1. **Change line 87** from:
   ```python
   out_dir = os.path.join(temp_dir, "openwrt-condensed-docs")
   ```
   to:
   ```python
   out_dir = os.path.join(temp_dir, "output")
   ```

**File: smoke_00_post_extract_pipeline.py**

2. Already uses `os.path.join(temp_dir, "out")` — fine. No change needed.

**File: pytest_pipeline_support.py**

3. **Change line 13** from:
   ```python
   OUTDIR = PROJECT_ROOT / os.environ.get("OUTDIR", "staging")
   ```
   to: The default must find the latest pipeline run dir if no env var is set. Add a helper:
   ```python
   def _resolve_latest_outdir() -> Path:
       """Find the most recent pipeline output dir under tmp/."""
       pipeline_dirs = sorted(
           (PROJECT_ROOT / "tmp").glob("pipeline-*/output"),
           reverse=True,
       )
       if pipeline_dirs:
           return pipeline_dirs[0]
       return PROJECT_ROOT / "staging"  # fallback for old layout
   
   OUTDIR = PROJECT_ROOT / os.environ.get("OUTDIR", "") if os.environ.get("OUTDIR") else _resolve_latest_outdir()
   ```
   This way, pytest automatically inspects the latest local run.

#### Phase 7: Remove tracked generated output and fix .gitignore

1. **Remove openwrt-condensed-docs-renamed from git:**
   ```
   git rm -r --cached openwrt-condensed-docs-renamed/
   ```
   Do NOT delete the files from disk yet — `git rm --cached` only untracks them.

2. **Update .gitignore:**
   - Remove: `openwrt-condensed-docs/`
   - Remove: staging
   - Add: `openwrt-condensed-docs*/` (catches any future rename experiments)
   - Keep: tmp (already covers all pipeline run directories)
   - The staging ignore rule is no longer needed because staging is no longer a default path. But keep it as a safety net in case someone manually sets `OUTDIR=staging`.
   
   Final relevant lines:
   ```
   # Pipeline run directories
   tmp/
   
   # Legacy output roots (safety net)
   staging/
   openwrt-condensed-docs*/
   ```

#### Phase 8: Update documentation

**Files: CLAUDE.md, ARCHITECTURE.md, DEVELOPMENT.md**

Update these to reflect the new directory model. Key changes:

1. **CLAUDE.md** — Update the "Architecture: Layer Model" section:
   - `WORKDIR` default description: `tmp/pipeline-{timestamp}/input/` (auto-created fresh per local run)
   - `OUTDIR` default description: `tmp/pipeline-{timestamp}/output/` (sibling of input/)
   - Remove references to staging as the default OUTDIR
   - Remove "There is no tracked publish root" — replace with "All pipeline working state lives under tmp (gitignored). Each local run creates a fresh timestamped directory. CI uses a fixed `pipeline-ci/` subdirectory."

2. **ARCHITECTURE.md** — Update "Repository Zones" table:
   - Replace the staging row with `tmp/pipeline-*/` and describe the `input/` + `output/` structure
   - Update the Layer Model table locations

3. **DEVELOPMENT.md** — Update "Local Validation Commands":
   - Note that each run creates `tmp/pipeline-YYYYMMDD-HHMMSSz/` automatically
   - Tests inspect the latest run directory
   - Users manage tmp size themselves

---

### What NOT to change

- Do NOT rename `release-tree/` or `support-tree/` inside OUTDIR — those names are part of the published contract
- Do NOT change sync_tree.py CLI interface — it still works, just the CI no longer calls `promote-generated`
- Do NOT change the base or override AI store paths — those are persistent across runs and live in the repo
- Do NOT change release-inputs — those are static repo inputs
- Do NOT change cookbook-source — those are authored source
- Do NOT create any new markdown documentation files beyond updating the existing ones listed above
- Do NOT add a source-repo root `llms.txt` — explicitly out of scope per CLAUDE.md

---

### Verification Checklist

After all changes, the implementing agent must verify:

1. `python tests/run_pytest.py` — all tests pass (skip is OK)
2. `python tests/run_smoke.py` — smoke tests pass with new directory structure
3. `python tests/check_linting.py` — clean (ruff + pyright + actionlint)
4. `git status` — openwrt-condensed-docs-renamed is untracked, no stale files tracked
5. Grep the entire codebase for `openwrt-condensed-docs` — should only appear in:
   - .gitignore (as ignore pattern)
   - Stage 08 legacy-guard checks (in the set of forbidden directory names)
   - Historical docs under archive, plans, .specstory
   - Job logs and temp files
   - NOT in any active pipeline script, workflow env var, config default, or test

---

### Risk Assessment

| Risk | Mitigation |
|------|-----------|
| CI workflow changes break deploy | The changes are: remove one step, change one path variable. The gh-pages mirror reads from `$OUTDIR` instead of a promoted copy — functionally identical. External distribution already reads from `$OUTDIR/release-tree/`. |
| Baseline loss | Already fails safely. Current behavior says "No baseline inventory found." New behavior is identical. |
| Tests can't find output | pytest_pipeline_support.py gets a helper that finds the latest `tmp/pipeline-*/output/`. Tests already skip when no output exists. |
| config.py auto-creates dirs at import time | Only when no env vars are set. CI always sets env vars. Tests set env vars. Auto-creation only happens for ad-hoc local script runs. |
| Smoke tests break | They already create their own temp dirs. The only change is the output dir name inside their temp dir. | 

