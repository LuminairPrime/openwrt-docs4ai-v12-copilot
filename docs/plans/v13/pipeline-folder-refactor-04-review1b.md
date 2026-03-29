# Master Review: pipeline-folder-refactor-04.md

**Score: 10/10**  
*(This review synthezises internal logical analysis with aggressive codebase validation, identifying silent failures, extensive test breakages, and providing actionable guardrails before implementation begins.)*

---

## 🚨 CRITICAL SEVERITY (Silent Breakages & Propagating Errors)

### 1. Missing Script Updates for Stages 04, 05b, and 06
Phase 4 of the plan specifies updating stage 05a to read from `config.PROCESSED_DIR / "L2-semantic"` instead of `OUTDIR`. However, the plan entirely overlooks other stages that depend on this path:
- **04-generate-ai-summaries.py** / **lib/ai_enrichment.py**: Line 327 reads from `os.path.join(outdir, "L2-semantic")`.
- **05b-generate-agents-and-readme.py**: Line 25 defines `L2_DIR = os.path.join(OUTDIR, "L2-semantic")`.
- **06-generate-llm-routing-indexes.py**: Line 36 defines `L2_DIR = os.path.join(OUTDIR, "L2-semantic")`.
> [!CAUTION]  
> If these scripts remain un-updated, they will silently read from an empty directory (since Phase 3 moved the content to `processed/`), resulting in empty AI summaries, empty routing indexes, and broken AI developer agents.

### 2. The `source_locator` Metadata Corruption
`02i-ingest-cookbook.py:111` writes `"source_locator": f"content/cookbook-source/{filename}"` into every cookbook `.meta.json`. This value propagates through L2 frontmatter (handled by stage 03 at `03-normalize-semantic.py:764`) and ultimately manifests in the published `chunked-reference/` files (stage 05a).
> [!WARNING]  
> After Phase 0 moves the cookbook sources to `static/cookbook-source/`, every generated output will embed a stale `source_locator` pointing to a nonexistent path. 
* **Fix:** Update `02i-ingest-cookbook.py` to emit the new `static/` path during extraction.

### 3. The `config.py` Multi-Process Instantiation Bug
The plan states `PIPELINE_RUN_DIR` defaults to `tmp/pipeline-YYYYMMDD-HHMMutc-XXXX`.
If `config.py` evaluates this string dynamically via `datetime.now()` at import time, every standalone python script execution in the pipeline will generate a completely different run directory.
- `python stage01.py` writes to `...-1111/`
- `python stage02.py` isolates itself in `...-2222/`
> [!IMPORTANT]  
> **Fix:** `config.py` initial state logic must be strictly defined:
> 1. Use the `PIPELINE_RUN_DIR` env var if set.
> 2. If unset, read the active directory from `tmp/pipeline-run-state.json`.
> 3. Only generate a new hex/timestamp if neither exist, then save it to the state file immediately.

### 4. Underestimated Test Blast Radius
Phase 11 heavily relies on updating `pytest_pipeline_support.py`, underestimating the sheer volume of hardcoded paths across the test suite:
* `pytest_01_workflow_contract_test.py:170` (Asserts `promote-generated` exists).
* `pytest_07_partial_rerun_guard_test.py:67-80` (Directly accesses `outdir / L1-raw`).
* `pytest_09_release_tree_contract_test.py:350-354` (Asserts on `./openwrt-condensed-docs/` prefixes).
* `pytest_08_output_sync_test.py:306-321` (Tests `promote-generated` CLI).
> [!CAUTION]  
> The test suite will fail massively. The plan needs an explicit checklist to audit all pytest usages of `OUTDIR` and `L1-raw/L2-semantic`.

---

## ⚠️ HIGH SEVERITY (Logic Flaws & Collisions)

### 5. `WORKDIR` & `OUTDIR` Alias Fragmentation
Phase 1 dictates keeping `WORKDIR` and `OUTDIR` as backward-compatible aliases to `DOWNLOADS_DIR` and `STAGED_DIR`.
However, any script bypassing `config.py` to construct relative paths (e.g., `os.path.join(WORKDIR, "L1-raw")`) will break silently. `WORKDIR` used to be `tmp/` (the parent of `L1-raw`); it is now `tmp/pipeline-XXXX/downloads/`. 
> [!TIP]  
> Do a hard `grep` across the codebase for `WORKDIR` and `OUTDIR` string literals inside scripts to ensure absolute usage of `config.PROCESSED_DIR` is standard.

### 6. The `$STAGED_DIR` Baseline Paradox
Phase 9 alters the CI baseline check to: `if [ -f "$STAGED_DIR/signature-inventory.json" ]; then cp ...`
`$STAGED_DIR` represents the *current* run. It is mathematically impossible for the previous run's inventory to exist inside the brand new run's empty folder before the pipeline executes.
> [!NOTE]  
> This acts as dead CI code (which properly enforces an empty CI baseline), but logically, it's a paradox. It should either be explicitly documented as dead code to enforce an empty baseline, or updated to check `pipeline-run-state.json` to logically simulate historical runs.

### 7. Local ZIP Generation Collisions
Phase 8 routes ZIP outputs to `config.PACKAGES_DIR / f"openwrt-docs4ai-{date}.zip"`.
Over the course of a day, multiple local runs will generate identically named zip files. While the initial generation isolates them into daily run directories correctly, pulling those zip files out onto a local desktop for comparison creates instant namespace collisions.
* **Fix:** Embed the run's hex ID (`XXXX`) into the zip filename for local executions, while modifying CI to truncate it to the standard `{date}.zip` during the final GitHub upload.

---

## 🟨 MEDIUM SEVERITY (Guardrails & Clarifications)

### 8. Phase 0 vs Phase 1 Ordering Conflict
Phase 0 instructs moving paths and updates `config.py` imports (`RELEASE_INCLUDE_DIR`). Phase 1 then rewrites `config.py` with the new schema, effectively overlapping the work. 
* **Fix:** Confine Phase 0 strictly to file system `mv` commands. Move all `config.py` code modifications to Phase 1 exclusively.

### 9. `.gitignore` Developer Workspace UX
Removing `openwrt-condensed-docs/` and `staging/` from `.gitignore` will immediately corrupt every active developer's `git status` with thousands of untracked files from earlier pipeline runs.
* **Fix:** Maintain the legacy paths in `.gitignore` for a grace period, appending a `# Legacy (Pre-V13)` comment.

### 10. `pipeline-run-state.json` Ambiguity
The document states `pipeline-run-state.json` is a mutable pointer, but also refers to it as a constant path in the config table. Its contract (who writes it, atomicity, concurrent lock conditions) is undefined.
* **Fix:** Formalize the execution wrapper to lock/write the global pointer exclusively, ensuring local scripts cleanly latch onto the designated state.

### 11. `ensure_dirs()` Depth Validation
When updating `ensure_dirs` to materialize the run schema, ensure it executes deeply nested creations natively (`processed/manifests`, `staged/packages`, `downloads/repos`, `downloads/wiki/raw`).

---

## ℹ️ LOW SEVERITY (Details & Exclusions)

* **CI Workflow Hardcoded Path:** The CI deploy job specifies `pages_include_dir="$GITHUB_WORKSPACE/release-inputs/pages-include"`. This hardcoded string bypasses `config.py` and must be updated to `static/release-inputs/pages-include`.
* **Stage 07 Display Strings:** `PUBLISH_PREFIX = "./openwrt-condensed-docs"` in Stage 07 is not only used for file routing but is hard-baked into HTML `<title>` tags and heading labels. Update the display logic independently of the file routing.
* **Smoke Test Constants:** `smoke_01` rigidly injects the string literal `openwrt-condensed-docs` as the output directory. This needs generic abstraction.
* **Deleting `content/`:** Validate the absence of `.gitkeep` binaries or orphaned image sub-directories before executing `rm -rf content/` at the root.
* **Ephemeral Workspaces:** While not breaking, it should be noted that CI-only artifacts (`extract-status/`, `extract-summary/`, `run-summary/`) will also structurally migrate downward into the new run directory mappings.
