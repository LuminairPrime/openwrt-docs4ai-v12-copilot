Previous reviews analyzed the **plan document**. This one grepped the **actual codebase** and read every source file the plan references. That produced two new findings that all prior reviews missed:

### Two items to fix before implementation

1. **🔴 `lib/output_sync.py` shape constants (lines 31–55)** — Hardcodes `"L1-raw"`, `"L2-semantic"`, `"repo-manifest.json"`, `"cross-link-registry.json"` as expected at OUTDIR root. The `promote-generated` command is being removed, but these constants and `validate_generated_root()` remain as stale landmines. Need to tombstone or update them.

2. **🔴 Stage 06 reads `repo-manifest.json` from `OUTDIR` (line 89)** — The plan's Phase 4 manifest consumers section lists stages 05b, 05c, 05d but misses stage 06. After Phase 3, this path is empty. Silent failure.

### Additional test files missing from Phase 11 table

The plan lists 4 test files. My grep found at least 4 more:
- `smoke_pipeline_support.py:197` — `os.path.join(workdir, "L1-raw")`
- `pytest_05_manage_ai_store_cli_test.py:15` — `openwrt-condensed-docs`
- `pytest_09_release_tree_contract_test.py:126-127` — `outdir / "L1-raw"`
- `pytest_10_routing_provenance_test.py:241` — `OUTDIR / "L2-semantic"`

The plan's pre-audit greps would catch all of these, but the explicit table should be authoritative, not aspirational.

**Score: 9.2/10** — The plan is genuinely exceptional. The gaps are small relative to the volume of correct analysis, and the built-in pre-audit greps serve as a self-healing safety net.







# Independent Code-Validated Review: pipeline-folder-refactor-04.md

**Score: 9.2 / 10**

This review was produced by reading every source file the plan references, grepping the actual codebase for every path pattern mentioned, and cross-referencing every claim against the real code. It is not based on taking the plan's descriptions at face value.

---

## What the Plan Does (Summary)

1. **Isolates every pipeline run** into a timestamped directory (`tmp/pipeline-YYYYMMDD-HHMMutc-XXXX/`) instead of writing into a shared, flat `tmp/` and `staging/`.
2. **Creates three functional zones** inside each run: `downloads/` (stage 01–02 raw material), `processed/` (stage 02x–03 normalized L1/L2 layers + manifests), and `staged/` (stages 05–08 deliverables).
3. **Consolidates all human-authored static resources** (`content/`, `data/`, `release-inputs/`) under a single `static/` top-level folder.
4. **Introduces `config.py` run-directory resolution** with a 3-tier fallback (env var → state file → generate-new) to prevent scripts from spawning separate run directories.
5. **Partially dissolves `support-tree/`** by removing the redundant `raw/` and `semantic-pages/` copies, keeping only `manifests/` and `telemetry/`.
6. **Eliminates the `promote-generated` / `openwrt-condensed-docs` intermediate copy step** from CI, and fixes the gh-pages test preview to deploy only `release-tree/` (matching production).
7. **Moves ZIP generation** into `staged/packages/` with context-dependent naming (local: hex-suffixed, CI: date-only).
8. **Updates all downstream stage scripts** (04, 05a–d, 06, 07, 08) to read L2-semantic and manifest files from `processed/` instead of `OUTDIR`.
9. **Updates the CI workflow** to set environment variables for the new schema, remove PUBLISH_DIR, and update deploy source paths.
10. **Fixes the symlink-following bug** in `output_sync.py`.
11. **Audits and updates the full test suite** for hardcoded path assumptions.
12. **Updates `.gitignore` and documentation** with legacy grace periods and new schema descriptions.

---

## Tier List

### 🟢 S-TIER — Excellent, verified correct

1. **The `source_locator` fix is correctly scoped.** I verified `02i-ingest-cookbook.py:111` hardcodes `f"content/cookbook-source/{filename}"`. The plan correctly identifies this as a Phase 0 fix and correctly notes it propagates through `03-normalize-semantic.py:764` and `05a-assemble-references.py:173`. Ground truth confirmed.

2. **The L2-semantic reader enumeration is complete.** I grepped `.github/scripts/` for `L2-semantic` and confirmed exactly the scripts the plan lists: `04-generate-ai-summaries.py` (via `ai_enrichment.py:327`), `05a-assemble-references.py:38`, `05b-generate-agents-and-readme.py:25`, `06-generate-llm-routing-indexes.py:36`. The plan also correctly identifies `ai_store_workflow.py:60` as a fifth read-site. All confirmed in code.

3. **The `cross-link-registry.json` / `repo-manifest.json` consumer enumeration is mostly complete.** I verified: `05b:24` reads `REGISTRY_PATH = os.path.join(OUTDIR, "cross-link-registry.json")`, `05c:23` does the same, `05d:23` does the same. Stage 06 line 89 also reads `repo-manifest.json` from `OUTDIR` — **this is NOT listed in the plan's Phase 4 manifest consumers section** (see B-TIER #20).

4. **The `copy_support_tree()` analysis is exact.** I read the function at `07-generate-web-index.py:575-596`. The plan's description of what it copies (L1→raw, L2→semantic-pages, manifests, telemetry) is a line-for-line match with the actual code. The dissolution plan (remove raw/semantic-pages copies, update manifest source paths, keep telemetry unchanged) is correct.

5. **The `validate_support_tree_contract()` analysis is exact.** I read `08-validate-output.py:460-512`. Line 467 hardcodes `required_dirs = ["raw", "semantic-pages", "manifests", "telemetry"]`. Lines 473-487 validate raw/ and semantic-pages/ with mirrored-tree checks against `outdir/L1-raw` and `outdir/L2-semantic`. The plan correctly identifies all of these for removal/update.

6. **The baseline mechanism analysis is correct.** The plan's claim that CI always starts with an empty baseline (because `openwrt-condensed-docs/` is gitignored and never present on a fresh CI VM) is logically sound and architecturally accurate.

7. **The PUBLISH_PREFIX analysis is correct.** I confirmed `07-generate-web-index.py:35` hardcodes `PUBLISH_PREFIX = "./openwrt-condensed-docs"` and this string appears in the generated HTML at lines 618, 654, 761, 765. The plan correctly notes both the routing and display-string implications.

8. **The anti-truths are all verifiably true negations.** Each "FALSE" claim I cross-checked against the actual code and confirmed. For example, no stage reads `support-tree/` as input for further processing — only stage 08 validates it and CI process-summary counts it.

### 🟡 A-TIER — Good, with minor gaps or imprecisions

9. **Phase 10 symlink fix is addressing the right bug but citing imprecise lines.** The plan says "Lines 297–304: `is_dir()` returns True for symlink-to-dir." I read `output_sync.py:296-305` — the actual extraneous-deletion code at line 302 does `if dst_entry.is_dir(): shutil.rmtree(dst_entry)`. However, the copy path at lines 278-285 already handles symlinks correctly — it checks `dst_entry.is_symlink()` at line 282 and calls `unlink()`. So the symlink bug is only in the delete-extraneous path (line 302), not lines "297–304" broadly. The fix is still needed but the line citation is slightly imprecise.

10. **The `ai_enrichment.py` write-back clarification is important but buried.** The plan correctly warns that `ai_enrichment.py:327` constructs `l2_dir = os.path.join(outdir, "L2-semantic")` and uses it for both reading AND writing (line 570 writes back to the same `path` variable derived from `l2_dir`). The actual fix requires changing what stage 04 *passes* as `outdir` to `run_ai_enrichment()` (line 311 receives `outdir` as keyword argument). The plan does note this ("Fix the caller (stage 04) to pass `config.PROCESSED_DIR`") which is correct — but it's buried in a paragraph that could be easily missed during implementation.

11. **Stage 08 has more `outdir/L2-semantic` references than Phase 7 acknowledges.** I found L2-semantic references at lines 59, 231, 370, 433, 482, 587, 588, 786, 787, 1036, 1061, 1121 in `08-validate-output.py`. Many of these are in validation functions like `validate_module_llms_contract()` (line 786-787) and `validate_llms_full_contract()` which construct expected paths against `outdir/L2-semantic/`. After the refactor, L2-semantic is at `processed/L2-semantic`, not `outdir/L2-semantic`. The plan only calls out updating "L1-raw / L2-semantic / manifest references" generically in Phase 7 Step A, without enumerating the ~12 distinct hit sites in this 1182-line file. This is the largest risk of silent breakage.

### 🟠 B-TIER — Needs attention before implementation

12. **Stage 03 writes `cross-link-registry.json` to `WORKDIR`, not `OUTDIR`.** Line 809 of `03-normalize-semantic.py`: `reg_path = os.path.join(WORKDIR, "cross-link-registry.json")`. And line 907 also references `WORKDIR/repo-manifest.json`. The plan says Phase 3 changes `promote_to_staging()` to copy L1/L2 to `processed/`, but doesn't explicitly address that the registry and manifest are written to `WORKDIR` (= `downloads/` post-refactor) and then need to land in `processed/manifests/`. This is handled implicitly by the config constants (`REPO_MANIFEST_PATH`, `CROSS_LINK_REGISTRY` moving to `processed/manifests/`), but the plan doesn't state this logical chain explicitly.

13. **`smoke_pipeline_support.py:197` constructs `l1_root = os.path.join(workdir, "L1-raw")`.** This is in the test support module, not in the Phase 11 audit checklist table. It will break silently (construct a path under `downloads/` instead of `processed/`).

14. **`pytest_05_manage_ai_store_cli_test.py:15` references `openwrt-condensed-docs`.** This is identified in review0 findings but NOT in the plan's Phase 11 audit checklist table.

15. **`pytest_09_release_tree_contract_test.py:126-127` creates `outdir / "L1-raw"` and `outdir / "L2-semantic"` directly.** This is also NOT in the plan's Phase 11 audit checklist table, despite being identified in review0. The plan's table only mentions lines ~350-354 of this test file.

16. **`pytest_10_routing_provenance_test.py:241` uses `OUTDIR / "L2-semantic"`.** Identified in review0 but NOT in the plan's Phase 11 audit table.

17. **The test audit checklist is explicitly incomplete.** The plan acknowledges this ("this list is a starting point, not a complete inventory") and provides a pre-audit grep. But the gap between the explicit 4-row table and the actual ~8 affected files is material enough that an implementer who only reads the table will miss half the work.

### 🔴 C-TIER — Needs fix in the plan before implementation

18. **`lib/output_sync.py` shape constants are completely unaddressed.** Lines 31-55 of `output_sync.py` hardcode `GENERATED_ROOT_REQUIRED_FILES` (includes `"repo-manifest.json"`, `"cross-link-registry.json"`) and `GENERATED_ROOT_REQUIRED_DIRS` (includes `"L1-raw"`, `"L2-semantic"`) — all expected at the OUTDIR root level. The `validate_generated_root()` function uses these to check tree shape. After the refactor, these files/dirs move to `processed/`. The plan removes the `promote-generated` CLI command (Phase 9), so the primary caller is gone — but the constants and function remain. If any future code or tooling calls `validate_generated_root()`, it will fail against the new schema. The plan should note that these constants need updating or tombstoning alongside the `promote-generated` removal.

19. **Stage 06 reading `repo-manifest.json` from `OUTDIR` is not addressed.** `06-generate-llm-routing-indexes.py:89` does `os.path.join(OUTDIR, "repo-manifest.json")`. This is not listed in the Phase 4 manifest consumers section (which only covers 05b, 05c, 05d). After Phase 3 moves the manifest to `processed/manifests/`, stage 06 will read from a nonexistent path. The pre-audit grep *will* catch this, but an explicit enumeration exists precisely to prevent relying solely on greps.

---

## What Is Good About the Plan

- **Exhaustive research phase.** The document spent significant effort reading stage source code, tracing data flows, and documenting what each artifact is, who produces it, and who consumes it. This is rare in refactoring plans.
- **Anti-truth framework.** Explicitly stating false beliefs and why they're false is an extremely effective technique for preventing implementation drift. I verified each one against the code and they're all correct.
- **Phase decoupling with explicit coupling exceptions.** The Phase 5+7 coupling is correctly identified and guarded.
- **Pre-audit instructions.** Every phase includes a concrete `grep` command to run before editing. This is the single most important guardrail — it catches what the plan misses.
- **Deferred scope discipline.** Wiki cache, full support-tree dissolution, incremental downloads, and folder bikeshedding are all explicitly deferred with reasoning. This is mature project management.
- **CI path contract clarity.** The `pipeline-ci/` fixed name explanation (CI VMs provide isolation; env var always wins) is a clean architectural decision.
- **The schema itself is sound.** The `downloads/processed/staged` three-zone model is a well-understood pattern in data engineering. The naming is clear and the boundaries are logical.

## What Is Bad About the Plan

- **The test audit checklist is incomplete.** It lists 4 test files but my grep confirms at least 7-8 affected test files. The plan acknowledges this but the gap is material.
- **`output_sync.py` shape constants are completely unaddressed.** This is a real file with real hardcoded paths that will be stale after the refactor.
- **Stage 06's `repo-manifest.json` read is missed in the manifest consumers section.** The pre-audit grep would catch it, but the explicit enumeration is supposed to be the safety net.
- **Stage 03's write paths are only implicitly addressed.** The config constants handle it, but the plan doesn't spell out the logical chain of how manifests get from WORKDIR to processed/manifests/.
- **The stage 08 L2-semantic reference count is underestimated.** There are ~12 distinct references in that file, several in validation functions that construct expected paths. Phase 7 says "update all" but doesn't enumerate.

## What Is Good About My Interpretation

- I read every source file referenced. I didn't take the plan's line numbers or path claims at face value.
- I found real gaps (stage 06 manifest, output_sync.py constants, additional test files) that previous reviews missed because they were reviewing the plan document, not the codebase.
- I distinguished between issues the pre-audit greps will catch (mitigated) and issues that are structurally unaddressed (unmitigated).

## What Is Bad About My Interpretation

- I may have missed grep hits in files outside the directories I searched. I focused on `.github/scripts/`, `lib/`, and `tests/` but there could be path assumptions in `tools/` or documentation scripts.
- I did not run the actual pipeline to verify runtime behavior — I only did static analysis. Some paths may be constructed dynamically in ways grep cannot trace.
- I scored the plan 9.2 which may feel generous given C-TIER items exist, but the pre-audit grep instructions genuinely provide a self-healing safety net for most of the issues I found. The real question is whether an implementer will rigorously process every grep result.

---

## Final Assessment

The plan is a genuinely exceptional piece of technical writing. It is the most thorough refactoring plan I have seen for a project of this scale. The gaps I found are real but small relative to the volume of correct, verified analysis. The pre-audit grep instructions serve as a self-healing mechanism that compensates for incomplete explicit enumerations.

**Recommendation:** Fix items #18 and #19 (output_sync.py constants and stage 06 manifest) in the plan text before implementation. Everything else will be caught by the pre-audit greps if the implementer follows them rigorously.