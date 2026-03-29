# CI Failure Diagnosis — Claude Sonnet 4.6
**Run:** 23680501225 | **Date:** 2026-03-29 | **Model:** Claude Sonnet 4.6

---

## Observed Symptoms

- `process: failure`, `deploy: skipped`
- `validate_output_outcome: failure`, `contract_ok: false`
- `missing_required_files: none`
- Stage 08 is **absent from the process timings table entirely** (not slow — missing)
- Stages 03–07 all completed with suspiciously short durations

---

## Diagnosis Tier List

### 🥇 TIER 1 — Most Likely

**Stage 08 crashes at startup on a stale path inside the script itself**

Stage 08 is entirely absent from the process timings — not slow, not partial, *gone*. The old reference run (22867792862) shows stage 08 running for minutes producing uCode WARN lines. The new crash is immediate, before any logic runs.

The refactor renamed `staging/` → `tmp/pipeline-ci/staged/`. If stage 08's Python source still contains a hardcoded `"staging"` string, a stale default for `OUTDIR`, or an import-time path construction that references the old layout, it raises `FileNotFoundError` before the contract check loop ever starts.

This explains both symptoms perfectly: `missing_required_files: none` (the check never ran) + `contract_ok: false` (exception = contract not satisfied).

**Highest-yield single check:**
```
grep -n "staging" .github/scripts/08-validate-output.py
```

---

### 🥈 TIER 2 — Highly Likely

**`pipeline-run-record.json` read failure**

The refactor introduced `pipeline-run-record.json` written by `ensure_dirs()`. If stage 08 now reads this file to determine the run root, and the CI workflow's `mkdir -p` step (line 56) ran *before* any pipeline script wrote the record, stage 08 either gets `FileNotFoundError` or silently picks up a missing/empty record and derives a bad path — crashing before validation.

---

### 🥉 TIER 3 — Ruled Out

~~OUTDIR env-var collision~~ — workflow `env:` block (lines 32–36) correctly sets `OUTDIR: .../tmp/pipeline-ci/staged`. Not the cause.

---

### 4th — Plausible but Lower

**Silent structural contract failure** — stages 03–07 appear in timings but with suspiciously short durations. If any assemble step silently wrote to old `staging/` instead of `tmp/pipeline-ci/staged/`, outputs exist but the release-tree structure is wrong. Stage 08 finds all required files but fails the structural contract check. Less likely than Tier 1 since stage 08 *itself* doesn't appear in timings at all.
