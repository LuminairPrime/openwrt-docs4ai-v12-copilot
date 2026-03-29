# CI Failure Diagnosis — mimo-v2-pro (2026-03-29)

**Model:** xiaomi/mimo-v2-pro:free
**Diagnosis date:** 2026-03-29
**Analyzed runs:** 23716885470 (HEAD=24cabd46), 23707972944 (HEAD=cd369b5f)
**Plan:** pipeline-folder-refactor-04.md

---

## Failure Diagnosis Tier List

### Tier 1 — Root Cause (confirmed, definitive)

**Indentation error in the inline Python heredoc in the workflow file**

`.github/workflows/openwrt-docs4ai-00-pipeline.yml`, lines 759-761 and 765-770 use **12 spaces** of indentation, while the surrounding heredoc code uses **10 spaces**. This was introduced by the refactor when replacing `outdir/L1-raw` paths with `processed_dir/L1-raw` paths and adding the `packages/*.zip` check.

```
Line 757:  missing = [...]    ← 10 spaces (correct)
Line 759:    l1_md = ...      ← 12 spaces (WRONG)
Line 760:    l1_meta = ...    ← 12 spaces (WRONG)
Line 761:    l2_md = ...      ← 12 spaces (WRONG)
Line 762:  release_tree = ... ← 10 spaces (correct)
Line 765:    package_zips = ...← 12 spaces (WRONG)
Line 767:    if len(...)      ← 12 spaces (WRONG)
```

After bash heredoc processing strips the common leading whitespace, these lines end up at inconsistent indentation levels. Python raises `IndentationError`, which fails the "Validate staging contract and build process summary" step.

The step has `continue-on-error: true`, so the job doesn't immediately fail. But `steps.process_contract.outcome` is `"failure"`, and the subsequent **"Enforce staging contract"** step checks `if: steps.process_contract.outcome != 'success'` — evaluates to true → `exit 1`.

**Evidence:**
- Run 23716885470 log: "Enforce staging contract" fires with `exit 1`
- The step also reports `PROC_TIMER_09: 0` (stage 09's timer never got written to `$GITHUB_ENV` because the heredoc script crashed before reaching that line)
- The diff clearly shows these lines changed from 10-space to 12-space indentation

**Fix:** Align lines 759-761 and 765-770 to use exactly 10 spaces of indentation, matching the rest of the heredoc.

---

### Tier 2 — Secondary Issue (was the failure on the *previous* run)

**Missing stage 09 script in commit cd369b5f**

The first refactor commit didn't include `.github/scripts/openwrt-docs4ai-09-build-packages.py`. The workflow referenced it, causing an immediate `No such file or directory` error. This was fixed in commit `24cabd46` ("fix(ci): add missing static assets and stage-09 script"). This issue is already resolved.

---

### Tier 3 — Potential Risk (not yet failing, but fragile)

**Stage 09 timer not recorded in process summary**

Because the heredoc crash prevents `PROC_TIMER_09` from being written to `$GITHUB_ENV`, the process summary builder's stage_timings won't include `"09-packages"`. This is cosmetic — it doesn't cause failure, but means timing data is lost. Once the indentation is fixed, this resolves automatically.

**`validate_processed_layer()` checking paths that depend on correct config**

The new `validate_processed_layer()` function in `08-validate-output.py` checks `config.L1_RAW_WORKDIR` and `config.L2_SEMANTIC_WORKDIR`. These depend on `PROCESSED_DIR` being correct. The env vars are set correctly in the workflow, so this isn't currently at risk — but if `PROCESSED_DIR` is misconfigured, stage 08 will now hard-fail with a clear message rather than silently producing empty output.

---

## Summary

| Tier | Issue | Status |
|------|-------|--------|
| 1 | **Indentation error** in workflow heredoc (lines 759-761, 765-770) | **Active failure cause** |
| 2 | Missing `09-build-packages.py` in first commit | Already fixed in `24cabd46` |
| 3 | Stage 09 timer missing from summary | Side effect of Tier 1; auto-resolves |
