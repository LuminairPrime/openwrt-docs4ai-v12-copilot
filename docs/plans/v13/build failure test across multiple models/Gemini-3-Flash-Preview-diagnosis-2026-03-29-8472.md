# Gemini 3 Flash (Preview) Diagnosis - 2026-03-29

I have analyzed the recent CI failure following the `pipeline-folder-refactor-04.md` implementation. The failure is driven by a mismatch between the **refactored Python configuration** and the **hand-rolled Shell logic** in the GitHub Actions workflow.

### Tier 1: Highly Likely (Root Cause)
**Workflow Path Mismatch in `.github/workflows/openwrt-docs4ai-00-pipeline.yml`**
*   **Diagnosis:** While `lib/config.py` was updated to the new nested structure (`tmp/pipeline-ci/processed/L1-raw/`), several steps in the GitHub Actions workflow use hardcoded shell logic or Python one-liners to validate contracts. These checks still expect files in the old flat structure (`tmp/L1-raw/` or `staging/`).
*   **Evidence:** The `Evaluate extractor output contract` and `Validate staging contract` steps fail because they cannot find `AGENTS.md` or `llms.txt` where they used to be. The `PROCESSED_DIR` and `OUTDIR` variables in the workflow have not been synchronized with the new `L1-raw` and `release-tree` nesting levels.
*   **Impact:** This prevents the pipeline from progressing to the final validation and upload stages, even if the scripts themselves ran correctly.

### Tier 2: Likely (Regression)
**AI Store Path Inconsistency in `04-generate-ai-summaries.py`**
*   **Diagnosis:** The refactor moved the AI store to `static/data/base/`. If the workflow still attempts to cache or restore this from the old `data/base/` path, the enrichment stage will fail to find existing summaries or fail to persist new ones.
*   **Evidence:** Stage `04` shows very short execution times (~1s) in some logs, indicating it might be failing silently or skipping work because it cannot resolve the `L2-semantic` workdir provided by stage `03`.

### Tier 3: Possible (Edge Case)
**Environment Variable (ENV) Shadowing**
*   **Diagnosis:** The refactor introduced new path resolutions in `lib/config.py` that depend on `RUN_DIR` or `PIPELINE_WORKDIR`. If the GA workflow exports these variables with trailing slashes or inconsistent casing, the `os.path.join` logic in Python might differ from the string concatenation used in the Shell steps.
*   **Evidence:** Discrepancies between `tmp/pipeline-ci` (Python) and `./tmp/pipeline-ci` (Shell) can cause `if [ -d ... ]` checks to fail on runners while the Python scripts successfully write to those locations.

### Suggested Fixes
1.  **Update [.github/workflows/openwrt-docs4ai-00-pipeline.yml](.github/workflows/openwrt-docs4ai-00-pipeline.yml):** Synchronize all Shell `if [ -f ... ]` and `ls` commands with the new nested paths defined in `lib/config.py`.
2.  **Verify Staging Logic:** Ensure `Validate staging contract` points to `tmp/pipeline-ci/staged/release-tree/` instead of the old `staging/` root.
3.  **Local Check:** Run `python tests/run_smoke_and_pytest.py` to confirm the refactored paths work locally before pushing.
