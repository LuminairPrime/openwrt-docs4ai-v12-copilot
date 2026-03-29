# MODEL-diagnosis-2026-03-29-4827.md

**AI Model:** minimax/minimax-m2.5:free (kilo/MC)

## Tier List - Pipeline Failure Analysis

### 🔴 TIER 1: Critical Bug (Root Cause)

**Location:** `.github/workflows/openwrt-docs4ai-00-pipeline.yml:732`

```yaml
validate_output_outcome = "${{ steps.validate_output.outcome }}" or "unknown"
```

**Problem:** The `${{ }}` expression is inside a Python heredoc (`python - <<'PY'`), but GitHub Actions does NOT expand `${{ }}` inside inline Python scripts at runtime. The expression is treated as a literal string, so the line evaluates to:
```python
validate_output_outcome = "success"  # because "success" or "unknown" always = "success"
```

This is a **constant string**, not the actual step outcome. The bug has likely existed since the script was written.

---

### 🔴 TIER 2: Why the Contract Fails

Looking at lines 823-824:
```python
payload = {
    "contract_ok": (not missing) and validate_output_outcome == "success",
```

- Stage 08 actually **passed** (0 hard failures, confirmed in logs)
- But `missing` list likely contains `packages/*.zip` - the zip was not generated or is empty
- Since `validate_output_outcome` is incorrectly hardcoded to "success", contract success depends entirely on `missing` being empty
- The zip generation may have failed silently, or the script tried to run before stage 09 existed

---

### 🟡 TIER 3: Historical Issue (Already Fixed)

**Run 23707972944** failed at extractor contracts due to "digest-mismatch" errors. The extractors couldn't download L0 artifacts. This appears resolved in the latest run.

---

## Fix Plan

1. **Fix the workflow bug** - Use proper shell variable for GitHub Actions step outcome:
   ```python
   validate_output_outcome = os.environ.get("VALIDATE_OUTPUT_OUTCOME", "unknown")
   ```
   And set it in the workflow step:
   ```yaml
   - name: Validate published output (08)
     id: validate_output
     run: python .github/scripts/openwrt-docs4ai-08-validate-output.py
   - name: Validate staging contract
     env:
       VALIDATE_OUTPUT_OUTCOME: ${{ steps.validate_output.outcome }}
   ```

2. **Verify package generation** - Ensure stage 09 runs correctly and produces non-empty zip

---

## Investigation Notes

**Run ID:** 23716885470 (latest failure)
**Commit:** 24cabd460bfe3c99c56b3098cbc194b647e39fc2

### Evidence from logs:

1. **Stage 08 passed:** "Hard Failures: 0" in validation output
2. **Process contract check:** `validate_output_outcome = "success"` (hardcoded, not actual value)
3. **All extractors reported as `extractor_failed`** but this was due to L0 artifact download issues (digest-mismatch)
4. **`PIPELINE_RUN_DIR` env var is set** in workflow (lines 33), so Phase 1 path resolution should work correctly
5. **Static resources moved** - `static/` directory exists with all resources (verified locally)

### Key workflow line causing bug:
```yaml
validate_output_outcome = "${{ steps.validate_output.outcome }}" or "unknown"
```

The `${{ }}` syntax is NOT evaluated inside a `python - <<'PY'` heredoc block. This is a GitHub Actions limitation - ${{ }} expressions only work in YAML values, not inside inline script content.