Here is my review of pipeline-folder-refactor-04.md.

1. CRITICAL: source_locator Embeds Hardcoded Path in Generated Output
02i-ingest-cookbook.py:111 writes "source_locator": f"content/cookbook-source/{filename}" into every cookbook .meta.json. This value propagates through L2 frontmatter (stage 03 reads it at 03-normalize-semantic.py:764) and into published chunked-reference/ files (stage 05a at 05a-assemble-references.py:173 writes > **Source:** \content/cookbook-source/...``).

After Phase 0 moves the directory to static/cookbook-source/, every generated cookbook output will contain a stale source_locator pointing to a nonexistent path. The plan does not address this.

Options:

Update 02i-ingest-cookbook.py to emit source_locator from the new path.
Accept that source_locator is a "where it came from at extraction time" provenance field (not a live file path) — but then document this explicitly so nobody tries to "fix" it later.
If you regenerate all cookbook output after Phase 0, the new path will be embedded naturally.
Risk: Medium. The stale path will be visible in published output and could confuse consumers. It won't break anything functionally.

2. CRITICAL: Missing Test Update References
The plan's Phase 11 only mentions pytest_pipeline_support.py and smoke_01_full_local_pipeline.py. In reality, many more test files hardcode paths that will break:

File	Hardcoded path
tests/pytest/pytest_01_workflow_contract_test.py:170	Asserts "tools/sync_tree.py promote-generated" exists in deploy block — must be removed when promotion step is removed
tests/pytest/pytest_07_partial_rerun_guard_test.py:67-80	Creates outdir / "L1-raw" and outdir / "L2-semantic" directly
tests/pytest/pytest_09_release_tree_contract_test.py:126-127	Creates outdir / "L1-raw" and outdir / "L2-semantic" directly
tests/pytest/pytest_09_release_tree_contract_test.py:240	References "Legacy root: openwrt-condensed-docs"
tests/pytest/pytest_09_release_tree_contract_test.py:350-354	Tests for "./openwrt-condensed-docs/" prefix in HTML — must be updated when PUBLISH_PREFIX changes
tests/pytest/pytest_09_release_tree_contract_test.py:410	Asserts "openwrt-condensed-docs" not in html
tests/pytest/pytest_05_manage_ai_store_cli_test.py:15-16	References openwrt-condensed-docs/
tests/pytest/pytest_08_output_sync_test.py:306-321	Tests promote-generated CLI command — needs removal/update
tests/pytest/pytest_10_routing_provenance_test.py:241	OUTDIR / "L2-semantic"
tests/support/smoke_pipeline_support.py:87	os.path.join(temp_dir, "openwrt-condensed-docs")
Risk: High. Tests will fail immediately after implementation. Plan underestimates the test blast radius.

3. LOGIC: pipeline-run-state.json Scope Mismatch
The plan says pipeline-run-state.json is at tmp/pipeline-run-state.json and is a "mutable pointer to most recent local run." But the config table says PIPELINE_RUN_STATE is a "constant" path tmp/pipeline-run-state.json.

The plan never explains who writes this file or who reads it. Is it written by ensure_dirs()? By mark_run_complete()? What happens when two concurrent local runs exist? There is no locking or atomicity described.

Additionally, the test discovery in Phase 11 says: "Two-tier resolution: env var STAGED_DIR → tmp/pipeline-run-state.json → hard error." This implies tests will read pipeline-run-state.json to find the output directory, but the plan never describes the file's schema beyond pipeline-run-record.json (which is per-run, not the global pointer).

Risk: Medium. Needs a clear write-once-per-run contract and a documented schema for the pointer file.

4. LOGIC: Phase 0 vs Phase 1 Ordering Problem
Phase 0 moves content/cookbook-source/ → static/cookbook-source/ and updates import paths. Phase 1 updates config.py to change RELEASE_INCLUDE_DIR, PAGES_INCLUDE_DIR, AI_DATA_BASE_DIR, AI_DATA_OVERRIDE_DIR.

But Phase 0's "Update import paths in config.py" overlaps with Phase 1's "Update RELEASE_INCLUDE_DIR... Same for PAGES_INCLUDE_DIR and AI_DATA_BASE_DIR / AI_DATA_OVERRIDE_DIR."

Which phase actually changes config.py? If Phase 0 changes config.py path constants and Phase 1 rewrites the whole file structure, the phases are not independently testable as claimed. Either merge them or make Phase 0 only do filesystem moves and Phase 1 do all code changes.

Risk: Low-medium. Confusing ordering but would eventually work.

5. RISK: WORKDIR and OUTDIR Backward Compat Aliases
Phase 1 says: "Keep WORKDIR and OUTDIR as aliases to DOWNLOADS_DIR and STAGED_DIR for backward compatibility with any external tooling."

This is good, but the plan doesn't clarify the semantic break: WORKDIR previously meant tmp/ (the parent of L1-raw), now it means tmp/pipeline-XXXX/downloads/. Any code that constructs paths relative to WORKDIR assuming L1-raw is a sibling (e.g., os.path.join(WORKDIR, "L1-raw")) will silently write to the wrong place.

The plan identifies specific scripts that do this (stage 01's own resolution, stage 03's promote_to_staging), but there may be others. The grep for L1_RAW_WORKDIR shows it's computed from WORKDIR in config.py:24. After Phase 1, this becomes {PROCESSED_DIR}/L1-raw — correct. But any script that bypasses config.py and constructs WORKDIR + "/L1-raw" directly will break.

Stage 01 already does this: 01-clone-repos.py:28 does WORKDIR = os.environ.get("WORKDIR", os.path.join(os.getcwd(), "tmp")) — it bypasses config.py entirely. Phase 2 addresses this.

Recommendation: After Phase 1, grep for all direct WORKDIR / OUTDIR string references in scripts to verify nothing bypasses config.py.

6. RISK: CI Workflow pages-include Path
The CI workflow at line 1189 hardcodes:

pages_include_dir="$GITHUB_WORKSPACE/release-inputs/pages-include"
The plan's Phase 9 mentions updating "static resource paths from release-inputs/ to static/release-inputs/" but doesn't call out this specific hardcoded line in the deploy job's "Publish external Pages distribution repository" step. The Phase 0 table lists .github/workflows/openwrt-docs4ai-00-pipeline.yml as needing update, but doesn't enumerate all the places.

Also, the CI workflow's ai-summaries-cache.json caching step (line 624) uses a repo-root path. If this file is supposed to persist across runs, it needs the same consideration as the wiki cache.

7. OVERSIGHT: smoke_01_full_local_pipeline.py Uses openwrt-condensed-docs as Out Dir Name
Line 87: out_dir = os.path.join(temp_dir, "openwrt-condensed-docs"). This name is baked into the smoke test. After the refactor removes the openwrt-condensed-docs concept, this needs to change. But the plan's Phase 11 only mentions work_dir and out_dir generically.

8. OVERSIGHT: PUBLISH_PREFIX in Stage 07 Hardcodes openwrt-condensed-docs
07-generate-web-index.py:35 has:

PUBLISH_PREFIX = "./openwrt-condensed-docs"
Phase 6 says "Change PUBLISH_PREFIX from './openwrt-condensed-docs' to '.'." But this string is also used in the generated HTML title (line 654) and heading (line 761). The plan doesn't mention updating those display strings. Tests at pytest_09_release_tree_contract_test.py:350-354 explicitly assert on the openwrt-condensed-docs prefix.

9. OVERSIGHT: Stage 08 Hardcoded Path Checks
Stage 08 at lines 169 and 205 checks for "./openwrt-condensed-docs/" in the browse index. Phase 7 says to "Remove the './openwrt-condensed-docs/' legacy path checks (lines 169, 205)." But lines 370 and 403 also reference openwrt-condensed-docs:

Line 370: if dir_name in {"L1-raw", "L2-semantic", "openwrt-condensed-docs", support_tree_name}:
Line 403: if "openwrt-condensed-docs" in content:
Phase 7 says "Keep the leakage guard checks (lines 370, 403)." But after the refactor, the release-tree should never contain openwrt-condensed-docs — so these checks can stay as-is as permanent leakage guards. This is correct but should be explicitly justified.

10. TRUTH: Baseline Mechanism Analysis Is Correct
The plan's analysis that CI always runs with an empty baseline is accurate. The Prepare Baseline step reads from $PUBLISH_DIR/signature-inventory.json, and since openwrt-condensed-docs/ is gitignored and never committed, the file is never present on fresh CI VMs. Removing PUBLISH_DIR causes zero regression. This section is well-reasoned.

However, the plan says "Update it to try to read from $STAGED_DIR/signature-inventory.json" — since STAGED_DIR is a per-run directory that doesn't exist before the run starts, this will always fail on CI. The plan acknowledges this but the proposed code at lines 591-598 is misleading because it implies there's a non-zero chance of finding the file. This step is essentially dead code on CI.

11. TRUTH: Support-Tree Analysis Is Thorough
The support-tree section accurately describes what copy_support_tree() does, who reads it, and the source-path adjustments needed. The Phase 5 path updates are correct: after Phase 3 moves L1/L2 to processed/, stage 07 must read from PROCESSED_DIR instead of OUTDIR.

One gap: copy_support_tree() at line 592-593 reads outdir / "cross-link-registry.json" and outdir / "repo-manifest.json". After the refactor, these files will be at processed/manifests/. The plan's Phase 5 correctly identifies this.

12. DETAIL: Missing extract-status/ and extract-summary/ Path References
The CI workflow creates $WORKDIR/extract-status/ and $WORKDIR/extract-summary/ for intermediate contract checking. These are ephemeral and not part of the pipeline output schema. The plan doesn't mention them, which is fine — they're CI-only scratch. But after Phase 9 changes WORKDIR to a per-run path, these directories will also move. The behavior is unchanged but should be noted for completeness.

13. DETAIL: No Mention of run-summary/ Directory
The CI process job creates $WORKDIR/run-summary/ for process-summary artifacts. Like extract-summary/, this is CI-only scratch. No change needed but not documented.

14. RISK: Stage 06 Path Reference
06-generate-llm-routing-indexes.py:36 has L2_DIR = os.path.join(OUTDIR, "L2-semantic"). After the refactor, L2-semantic is at PROCESSED_DIR/L2-semantic, not OUTDIR/L2-semantic. The plan doesn't mention stage 06 needing an update. This will cause stage 06 to find no L2 content and produce empty routing indexes.

Risk: High. Stage 06 will silently produce broken output.

15. RISK: Stage 05b Path Reference
05b-generate-agents-and-readme.py:25 has L2_DIR = os.path.join(OUTDIR, "L2-semantic"). Same issue as stage 06 — it reads from OUTDIR/L2-semantic which will be empty after Phase 3 moves content to PROCESSED_DIR/L2-semantic.

Risk: High. Same silent breakage.

16. RISK: Stage 04 and ai_enrichment.py Path References
04-generate-ai-summaries.py reads and writes OUTDIR/L2-semantic/. lib/ai_enrichment.py:327 does l2_dir = os.path.join(outdir, "L2-semantic"). After Phase 3, this path is empty.

Risk: High. AI summaries will find nothing to process.

17. DETAIL: Phase 4 Is Redundant
Phase 4 says: "stage 05a L2_DIR = os.path.join(OUTDIR, "L2-semantic") → config.PROCESSED_DIR / "L2-semantic"." But stages 04, 05b, and 06 also read from OUTDIR/L2-semantic and are not mentioned. Phase 4 should be generalized to "update all scripts that read L1-raw or L2-semantic from OUTDIR to read from PROCESSED_DIR."

18. GUARDRAIL: No CI Dry-Run Strategy
The plan doesn't describe how to validate the refactor on CI before merging. Recommendation: implement Phases 0-1 locally first, run check_linting.py + run_pytest.py, then push to a branch and verify the full CI run completes. Only then merge.

19. GUARDRAIL: No Rollback Plan
If the refactor breaks CI, there's no rollback strategy described. The old paths (staging/, openwrt-condensed-docs/) are gitignored and don't exist in the repo, so rolling back to a previous commit is sufficient. But the plan should state this explicitly.

20. DETAIL: pyproject.toml / .ruff.toml / pyrightconfig.json Path Exclusions
These config files may have path exclusions for staging/, tmp/, openwrt-condensed-docs/. After the refactor, these exclusions need review. Not mentioned in the plan.

Summary of Issues by Severity
Severity	Count	Items
Critical	2	#1 source_locator staleness, #2 test blast radius underestimated
High	3	#14/#15/#16 stages 04/05b/06 break silently
Medium	3	#3 pipeline-run-state.json contract, #4 phase ordering, #6 CI path hardcodes
Low/Detail	5	#5 WORKDIR alias risk, #7 smoke test naming, #8 display strings, #9 stage 08 guards, #12-13 scratch dirs, #17 phase redundancy, #18-20 guardrails
The three highest-priority fixes before implementation:

Enumerate all scripts that read OUTDIR/L1-raw or OUTDIR/L2-semantic and plan to update them (stages 04, 05b, 06 are currently missed).
Add a comprehensive test update checklist beyond the two files mentioned in Phase 11.
Decide whether source_locator in cookbook metadata is a live path or a historical provenance field, and document the decision.