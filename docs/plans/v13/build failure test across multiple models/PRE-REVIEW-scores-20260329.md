# PRE-REVIEW — Bug Diagnosis Quality Scores

**Reviewer:** Claude Opus 4.6 (Thinking)  
**Date:** 2026-03-29  
**Context:** Each diagnosis file attempts to identify why the GitHub Actions pipeline failed after `pipeline-folder-refactor-04.md` was implemented. This review cross-references each diagnosis against the actual codebase as it exists on disk right now.

---

## Confirmed Ground Truth (from codebase inspection)

Before scoring, here is what the code actually shows:

1. **The indentation bug is REAL and is the active failure cause.** Lines 759-761 and 765-770 of `.github/workflows/openwrt-docs4ai-00-pipeline.yml` use **12 spaces** of indentation inside the `python - <<'PY'` heredoc, while the surrounding code uses **10 spaces**. Python will raise `IndentationError` immediately, crashing the "Validate staging contract" step before it produces any summary output.

2. **The `${{ }}` expression on line 732 IS expanded by GitHub Actions.** Minimax's claim that `${{ }}` is not expanded inside `<<'PY'` heredocs is **FALSE**. GitHub Actions performs `${{ }}` substitution at the YAML level, before the shell ever runs. The single-quoted heredoc delimiter prevents *shell* variable expansion (`$VAR`), not GitHub Actions expression expansion. The variable `validate_output_outcome` receives the actual step outcome string.

3. **Stage 08 has no stale `"staging"` string.** `grep` for `staging` in `08-validate-output.py` returns zero hits. Stage 08 correctly uses `config.OUTDIR`, `config.PROCESSED_DIR`, `config.L2_SEMANTIC_WORKDIR`, `config.L1_RAW_WORKDIR`, etc. The `validate_processed_layer()` function exists and uses the correct config paths. There are zero `L2-semantic` hardcoded references -- all are via config constants.

4. **Stage 09 script exists** (`openwrt-docs4ai-09-build-packages.py` -- 4246 bytes). This was a prior-run issue, already resolved.

5. **No `PUBLISH_DIR`, no `promote-generated`, no `openwrt-condensed-docs`** references remain in the workflow or stage 08. The refactor was thorough in cleaning these out.

6. **The broken cookbook link claim (GPT-5.4, Raptor mini)** -- `rewrite_release_relative_links` and `rewrite_release_chunked_links` do not exist as named functions in `05a-assemble-references.py` (grep returned zero hits). The claim about `../../module/file.md` link patterns failing is not substantiated by the current code. The `check_dead_links()` function in stage 08 does validate relative links in release-tree, but the primary failure pathway is the indentation crash which prevents stage 08's contract step from ever running.

7. **The `continue-on-error: true` + Enforce pattern is correct.** The "Validate staging contract" step (line 720) has `continue-on-error: true`. The "Enforce staging contract" step (line 916) checks `if: steps.process_contract.outcome != 'success'`. When the heredoc crashes with `IndentationError`, outcome = `'failure'`, enforce fires -> `exit 1` -> job fails.

8. **Config.py is well-structured.** The `_resolve_pipeline_run_dir()` resolution order works exactly as the plan specified. `PIPELINE_RUN_DIR` is set via env var in CI (line 32 of workflow), so it always takes path 1. No `pipeline-run-record.json` read failure pathway exists for this bug.

---

## Individual Scores

### 1. mimo-v2-pro -- Score: 95/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 98 | Correctly identifies the **indentation error** as the root cause. Pinpoints exact lines (759-761, 765-770). |
| Evidence quality | 95 | Cites the diff showing 10->12 space change, explains the heredoc->Python pipeline correctly. |
| Mechanism explanation | 95 | Correctly explains `continue-on-error: true` -> outcome=failure -> enforce fires -> exit 1 chain. |
| Tier structure | 95 | Clean separation: Tier 1 (active), Tier 2 (prior run, already fixed), Tier 3 (side effects). |
| False claims | 5 pts off | Minor: "After bash heredoc processing strips the common leading whitespace" -- bash heredocs do NOT strip common leading whitespace unless using `<<-` (tab-only stripping). The `<<'PY'` form preserves all whitespace exactly. The bug still produces an IndentationError, but the mechanism description is slightly wrong -- it's not about stripping, it's about the raw inconsistency. |

**Verdict: Excellent.** Best diagnosis in the set. Correctly identified the real bug with precise line numbers and a clear causation chain.

---

### 2. GPT-5.3-Codex -- Score: 82/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 85 | S-tier correctly identifies the inline Python indentation issue. References `l1_md/l1_meta/l2_md/package_zips/if len(package_zips)` as the problematic variables -- accurate. |
| Evidence quality | 75 | Mentions "inconsistent indentation" but doesn't provide exact line numbers or the specific 10-vs-12 space count. |
| Mechanism explanation | 80 | Correctly identifies the `process_contract -> Enforce staging contract` flow but less precise than mimo. |
| Tier structure | 85 | Good A/B/C tier structure. A-tier (required_paths too strict) and B-tier (outcome/conclusion mismatch) are reasonable secondary concerns, though the A-tier isn't the active bug. |
| False claims | 0 pts off | No outright false statements. |
| Context accuracy | 85 | References run numbers (#68, #69) and differentiates between prior and current failure -- good situational awareness. |

**Verdict: Good.** Identified the real bug but with less precision than mimo-v2-pro. Good reasoning about the secondary possibilities.

---

### 3. Gemini 3 Flash Preview -- Score: 40/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 35 | Tier 1 claim: "hardcoded shell logic still expects files in the old flat structure (`tmp/L1-raw/` or `staging/`)." This is **FALSE**. The workflow already uses `$PROCESSED_DIR/L1-raw/$MODULE_NAME` (confirmed on line 116, 236, 384). No stale `tmp/L1-raw/` path exists. |
| Evidence quality | 25 | Claims "Evaluate extractor output contract and Validate staging contract steps fail because they cannot find AGENTS.md or llms.txt where they used to be" -- **not substantiated**. Extractors reference `$PROCESSED_DIR/L1-raw/` correctly. |
| False claims | -20 | Tier 2 ("AI Store Path Inconsistency") -- claims workflow caches from old `data/base/` path. The workflow's AI cache key is just `ai-cache-{os}-{run_id}` on `ai-summaries-cache.json` -- has nothing to do with `data/base/`. Tier 3 ("environment variable shadowing with trailing slashes or inconsistent casing") -- completely fabricated concern with no evidence. |
| Tier structure | 45 | Has a clear structure but all tiers are wrong. |
| Usefulness | 30 | Suggested fixes are generic ("synchronize shell commands with new paths") -- would lead nowhere since the paths are already synchronized correctly. |

**Verdict: Poor.** Generic "path mismatch" diagnosis without verifying actual workflow content. Every tier is wrong. The real bug (indentation error) is completely missed.

---

### 4. Gemini 3.1 Pro Preview -- Score: 35/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 30 | S-tier: "workflow still references old folder paths." Specifically claims it might look for `openwrt-condensed-docs-renamed/` or `tmp/pipeline-ci/L1-raw/` -- **FALSE**. There is no `openwrt-condensed-docs-renamed/` string anywhere in the codebase. The L1-raw paths are already correct. |
| Evidence quality | 20 | No specific line numbers, no file content verification, no log analysis. References a wrong workflow filename (`openwrt-docs4ai-pipeline.yml` vs. actual `openwrt-docs4ai-00-pipeline.yml`). |
| False claims | -25 | A-tier: "`lib/config.py` or associated path resolution logic (like `repo_manifest.py`)" -- `repo_manifest.py` does not exist. B-tier: "test fixtures in `tests/artifacts/`, `tests/sample-inputs/`" -- neither directory exists. C-tier: "Moving pipeline scripts broke relative imports" -- no scripts were moved; they stayed in `.github/scripts/`. The filename `tests/conftest.py` -- doesn't exist (test support is in `tests/support/`). |
| Tier structure | 40 | Structure is organized but filled with fabricated file references. |
| Usefulness | 25 | Steps suggest inspecting the "first FileNotFoundError" and linting -- reasonable generic advice but based on false premises. |

**Verdict: Poor.** Multiple fabricated filenames and paths that don't exist in the codebase. Classic hallucination of plausible-sounding but non-existent targets. Missed the actual bug entirely.

---

### 5. Claude Sonnet 4.6 -- Score: 55/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 50 | Tier 1: "Stage 08 crashes at startup on a stale path inside the script itself." This is **WRONG** -- stage 08 has no stale paths (confirmed: zero `staging` hits, uses config constants correctly). However, the symptom reading ("stage 08 absent from process timings") is astute -- just the wrong explanation. |
| Evidence quality | 60 | The diagnostic command `grep -n "staging" .github/scripts/08-validate-output.py` is sensible and would quickly disprove the hypothesis. Points for self-falsifiability. |
| Mechanism explanation | 65 | "missing_required_files: none (the check never ran) + contract_ok: false (exception = contract not satisfied)" -- this chain of reasoning is actually correct for how the indentation bug manifests, even though the mechanism cited (stale path in stage 08) is wrong. The real crash is in the contract summary step, not stage 08 itself. |
| Tier structure | 55 | Clean structure, good "ruled out" section for OUTDIR env var. Tier 2 (pipeline-run-record.json read failure) is plausible but wrong -- stage 08 doesn't read this file. |
| Usefulness | 50 | The grep command would quickly rule out the hypothesis, which is valuable. |

**Verdict: Mixed.** Right symptom analysis, wrong root cause. Stage 08 itself runs fine -- it's the *contract summary* step (inline Python in the workflow) that crashes from the indentation bug. Close but aimed at the wrong target.

---

### 6. GPT-5.4 -- Score: 25/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 20 | S-tier: "cookbook release-tree pages contain broken relative links" and blames `rewrite_release_relative_links` and `rewrite_release_chunked_links` in 05a. **Both function names don't exist** in the current `05a-assemble-references.py` (grep returned zero hits). |
| Evidence quality | 15 | References `[process_log.txt](process_log.txt#L875)` and `[run_details.txt](run_details.txt#L1)` -- these files don't exist in the diagnosis folder. Claims "The run breakdown confirms everything through stage 07 passed" but the actual bug prevents the contract summary from running at all. |
| False claims | -20 | The entire 05a link-rewriting regression narrative is fabricated. References `openwrt-docs4ai-05a-assemble-references.py#L103` and names two non-existent functions. References `code-review-improvements-b.md#L56` -- unverifiable claim building a narrative from phantom sources. |
| Tier structure | 30 | B-tier correctly notes the refactor-related stage 08 contract drift is "a real risk" but deprioritizes it -- ironic since that general area IS where the real bug lives. |
| Usefulness | 15 | Would send a developer on a wild goose chase through non-existent functions in 05a. |

**Verdict: Bad.** Confidently wrong. The diagnosis reads as a plausible-sounding narrative backed by invented function names and phantom log files. The "very high diagnostic quality" self-assessment is especially concerning.

---

### 7. Raptor mini -- Score: 30/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 25 | Tier 1: "`rewrite_release_relative_links` and `rewrite_release_chunked_links` did not convert `../../<module>/<file>.md`" -- **same fabricated function names as GPT-5.4**. These functions don't exist. |
| Evidence quality | 20 | Extremely terse -- no line numbers, no file content, no log analysis. |
| False claims | -15 | Claims "Implemented fix" and "Updated link rewrite rules" with "Local validation passes: 34 passed" -- but was instructed to diagnose only, not fix. Even as a claimed fix, it would be fixing non-existent functions. |
| Tier structure | 35 | Tier 2 (path mismatches after folder refactor) and Tier 3 (missing package zip) are reasonable but generic. |
| Usefulness | 20 | Too brief. "L2/L3 next-step resync" in Tier 4 is vague to the point of meaningless. |

**Verdict: Bad.** Shares the same core hallucination as GPT-5.4 (fabricated function names). Additionally claims to have implemented a fix, which isn't what was asked. Shortest and least useful diagnosis.

---

### 8. Minimax M2.5 -- Score: 30/100

| Aspect | Score | Notes |
|--------|-------|-------|
| Root cause identification | 15 | Tier 1: Claims `${{ }}` is NOT expanded inside `python - <<'PY'` heredocs -- **FALSE**. GitHub Actions processes `${{ }}` at the YAML level before bash sees it. The single-quoted heredoc delimiter prevents *shell* `$VAR` expansion, not GitHub Actions expression expansion. This is a fundamental misunderstanding of the GitHub Actions execution model. |
| Evidence quality | 30 | Does reference specific line numbers (732, 823-824) and provides a concrete fix proposal. The fix pattern (pass via env var) is actually a valid improvement, but for the wrong reason. |
| False claims | -25 | The core mechanism claim is wrong: "`${{ steps.validate_output.outcome }}` is treated as a literal string" -- no, it's expanded. The claim "This is a GitHub Actions limitation" is false. |
| Tier structure | 35 | Tier 2 reasoning about `missing` list containing `packages/*.zip` is plausible as a secondary concern. Tier 3 (historical, already fixed) is correct. |
| Usefulness | 25 | The proposed fix (using `os.environ.get()` instead of inline `${{ }}`) is a genuinely good practice, but it's solving a non-problem since the expression already works correctly. |

**Verdict: Bad.** Built on a fundamentally false premise about GitHub Actions expression evaluation. The model confidently explains a "bug" that doesn't exist while missing the real one (indentation). The irony: the model correctly notes there's something wrong with the inline Python but diagnoses the wrong thing entirely.

---

## Tier List Summary

### S Tier -- Correctly identified root cause with evidence
| Model | Score | Key Strength |
|-------|-------|-------------|
| **mimo-v2-pro** | **95** | Pinpointed exact lines, exact mechanism, clean tier structure |

### A Tier -- Identified root cause, less precise  
| Model | Score | Key Strength |
|-------|-------|-------------|
| **GPT-5.3-Codex** | **82** | Correctly identified indentation as S-tier, good secondary analysis |

### B Tier -- Partial insight, wrong primary diagnosis
| Model | Score | Key Strength |
|-------|-------|-------------|
| **Claude Sonnet 4.6** | **55** | Right symptom reading, wrong target (stage 08 vs. contract step) |

### C Tier -- Wrong diagnosis, generic reasoning
| Model | Score | Key Weakness |
|-------|-------|-------------|
| **Gemini 3 Flash Preview** | **40** | All tiers wrong; generic "path mismatch" without verification |
| **Gemini 3.1 Pro Preview** | **35** | Fabricated filenames (`repo_manifest.py`, `tests/artifacts/`, wrong workflow name) |

### D Tier -- Fabricated evidence, confidently wrong
| Model | Score | Key Weakness |
|-------|-------|-------------|
| **Raptor mini** | **30** | Fabricated function names, claims to have "fixed" it |
| **Minimax M2.5** | **30** | Built on false premise about `${{ }}` expansion |
| **GPT-5.4** | **25** | Fabricated function names + phantom log files, self-rates as "very high diagnostic quality" |

---

## Key Takeaways

1. **Only 2 of 8 models** identified the actual root cause (indentation error in lines 759-770 of the CI workflow).
2. **3 of 8 models** fabricated function names or file paths that don't exist in the codebase -- a classic hallucination pattern where models generate plausible-sounding technical artifacts.
3. **The `${{ }}` expansion misconception** (Minimax) reveals a common gap in understanding the GitHub Actions execution model (YAML-level expansion vs. shell-level expansion).
4. **GPT-5.4's self-assessment** of "very high diagnostic quality" while citing non-existent functions is a cautionary example of confidence != correctness.
5. **mimo-v2-pro** stands out for providing exact line numbers, the exact indentation count (10 vs 12 spaces), and a clean explanation of the failure chain -- this is what good diagnosis looks like.
