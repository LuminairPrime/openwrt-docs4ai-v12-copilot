The updated plan is substantially improved. Here is my second-pass review, focused only on remaining issues and new concerns introduced by the changes.

1. REMAINING: pipeline-run-state.json vs pipeline-run-record.json Naming Collision Risk
These two files exist in different locations but have nearly identical names:

tmp/pipeline-run-state.json — global pointer to most recent run
tmp/pipeline-{run_id}/pipeline-run-record.json — per-run metadata
The plan's Phase 1 schema for the state file ({"pipeline_run_dir": "..."}) is clear, and the record file schema (schema_version, run_id, status, etc.) is also clear. But no reader distinguishes them by function. A developer grepping for "pipeline-run" will find both. The plan should explicitly note that these serve different purposes and that pipeline-run-state.json is never a stage input/output — only config.py reads/writes it.

Risk: Low. Confusion only, no functional breakage.

2. REMAINING: Stage 05a Reads OUTDIR/L2-semantic AND RELEASE_INCLUDE_DIR
Phase 4 correctly identifies that 05a-assemble-references.py has L2_DIR = os.path.join(OUTDIR, "L2-semantic"). But the plan's static resources table says stage 05a also reads RELEASE_INCLUDE_DIR. Phase 0 moves release-inputs/ to static/release-inputs/, and Phase 1 updates RELEASE_INCLUDE_DIR in config.py. This chain is correct.

However, the Phase 0 table at line 593 says .github/scripts/openwrt-docs4ai-05a-assemble-references.py — reads RELEASE_INCLUDE_DIR — but the plan never checks whether stage 05a constructs the path itself or imports it from config.py. If it hardcodes a path, Phase 1's config.py update won't fix it.

Check: 05a-assemble-references.py imports RELEASE_INCLUDE_DIR from config.py (verified from lib/config.py:42). This is fine — Phase 1's update propagates automatically.

No issue. The plan is correct here.

3. REMAINING: Phase 4 Lists Four Stages but ai_enrichment.py Is a Library, Not a Script
Phase 4 correctly identifies lib/ai_enrichment.py:327 as a read-site for L2-semantic. But ai_enrichment.py is a shared library, not a numbered pipeline script. The phase's title says "All L2-semantic readers" and lists "stages 04, 05a, 05b, 06" — the library is imported by stage 04 but isn't itself a stage.

This is a minor organizational point: the grep pre-audit will catch the library file, but someone implementing Phase 4 from the script list alone might miss it. The plan does explicitly call out lib/ai_enrichment.py in the required updates list, so this is adequately documented.

No issue.

4. REMAINING: lib/ai_store_workflow.py Also References L2-semantic
From my grep results, lib/ai_store_workflow.py:60 does:

permanent_l2_root=source_outdir / "L2-semantic",
This file is used by tools/manage_ai_store.py. The Phase 4 pre-audit grep (grep -rn "L2-semantic\|L2_DIR" .github/scripts/ lib/) would catch this. But the plan doesn't explicitly list it.

Risk: Low. The pre-audit grep will catch it. But if someone only updates the four listed files and skips the grep, manage_ai_store.py --option review will silently fail to find L2 content.

5. REMAINING: lib/ai_enrichment.py outdir Parameter vs config.PROCESSED_DIR
ai_enrichment.py:327 does l2_dir = os.path.join(outdir, "L2-semantic"). The outdir parameter is passed by stage 04 (which gets it from config.OUTDIR). Phase 4 says to change this to config.PROCESSED_DIR / "L2-semantic".

But if ai_enrichment.py receives outdir as a function parameter, the fix should either:

Change the caller (stage 04) to pass config.PROCESSED_DIR instead of config.OUTDIR, or
Change ai_enrichment.py to use config.PROCESSED_DIR directly.
The plan says the latter ("os.path.join(outdir, 'L2-semantic') → config.PROCESSED_DIR / 'L2-semantic'"). This is correct but means ai_enrichment.py stops using its outdir parameter for L2 lookup. The parameter may still be used for other paths (writing enriched content back to L2). The plan should clarify whether the write-back path also changes.

Risk: Low-medium. If stage 04 writes enriched content to outdir/L2-semantic/ (which is now STAGED_DIR), the writes go to the wrong place. But checking 04-generate-ai-summaries.py, it likely writes back through the same outdir parameter. Need to verify the write path also points to PROCESSED_DIR.

6. REMAINING: Stage 02a Wiki Cache — Acknowledged Regression, But Local Dev Pain
The plan now correctly defers the WIKI_CACHE_DIR fix and documents it as a known performance regression. This is honest. However, the plan doesn't quantify the impact: for a full wiki scrape (~200 pages at 1.5s delay each), each local run adds ~5 minutes of wasted time. This should be stated so developers know the cost.

Also, the plan's deferred fix section says "Implement as a standalone PR after the folder schema refactor ships." A one-line fix (WIKI_CACHE_DIR = "tmp/.cache" + updating one function in stage 02a) could reasonably be included in Phase 2 or a Phase 2.5 to avoid the regression entirely. The plan should at least note this option.

Risk: Low correctness, high annoyance factor for local development.

7. REMAINING: Phase 5+7 Atomicity — The Plan Says "Commit Together" But Git Doesn't Enforce This
Phase 5 and Phase 7 must be implemented and committed together. The plan states this clearly in the guardrails. But there's no mechanical enforcement — a developer could commit Phase 5 alone and break CI.

Recommendation: The plan should suggest implementing both phases in a single working session and running python tests/run_smoke.py before committing. The smoke test exercises stage 07 and 08 end-to-end, so it would catch a Phase-5-without-Phase-7 breakage.

The plan already has this guardrail at line 903 ("run the full smoke test"). This is adequate.

8. REMAINING: .nojekyll Overlay Behavior After gh-pages Fix
The current gh-pages step at line 979 does:

touch "$branch_dir/.nojekyll"
After the refactor, the gh-pages step mirrors $STAGED_DIR/release-tree + pages-include/ overlay. The pages-include/ directory contains .nojekyll. If the overlay application is correct, the touch is redundant but harmless.

However, the plan says the hardcoded pages_include_dir path (line 1189) must be updated to static/release-inputs/pages-include. If this is missed, the overlay silently fails (source dir not found), and .nojekyll comes only from the touch command — which still works. So the failure mode is: overlay content (not just .nojekyll) is silently dropped.

Risk: Medium. The plan correctly identifies this at lines 938-942. No additional issue.

9. REMAINING: CI WORKDIR Is Not Per-Run
Phase 9 says: "Update WORKDIR to {github.workspace}/tmp/pipeline-ci/downloads." This hardcodes a single run directory name (pipeline-ci) for all CI runs. This is fine for CI (fresh VM each time), but it means the pipeline-run-state.json resolution order in Phase 1 (env var → state file → generate new) will always take path 1 (env var) on CI, never generating a per-run directory.

The plan should explicitly document that CI uses a fixed run directory name and that this is intentional — CI doesn't need per-run isolation because the VM is fresh.

Risk: Low. The plan implies this but doesn't state it.

10. REMAINING: .gitignore Legacy Entries — When Do They Actually Get Removed?
Phase 12 says to keep staging/ and openwrt-condensed-docs/ as legacy comments. The plan doesn't specify when these can be removed. "Safe to remove after all devs migrate" is vague.

Recommendation: Add a concrete removal criterion: "Remove these entries after the next release ships with the new schema and no active branches reference the old layout. Check with git branch -r for any feature branches."

11. NEW CONCERN: Anti-Truth Sections Are Excellent But Could Be Over-Indexed
The plan now has 10+ anti-truth statements across the support-tree and Phase 4/5/7 sections. These are valuable, but some are restating the same truth from different angles (e.g., "support-tree raw/ is not authoritative" appears in multiple places). This risks the anti-truths becoming noise rather than signal.

Recommendation: Keep anti-truths only where the false belief is likely to be held by someone unfamiliar with the codebase. Remove redundant restatements.

12. NEW CONCERN: ensure_dirs() Creates support-tree/manifests/ and support-tree/telemetry/
Phase 1's ensure_dirs() tree (lines 753-770) creates support-tree/manifests/ and support-tree/telemetry/. After Phase 5 dissolves raw/ and semantic-pages/, the ensure_dirs() tree should not create those directories. The plan correctly excludes them from the tree. But the tree also doesn't create downloads/.cache/ — stage 02a creates this via os.makedirs(get_cache_dir(), exist_ok=True). This is fine; ensure_dirs() doesn't need to create every possible subdirectory.

No issue.

13. NEW CONCERN: Phase 0 Lint Check Will Fail
Phase 0 says "Run python tests/check_linting.py and python tests/run_pytest.py." After Phase 0 moves files but before Phase 1 updates config.py, the codebase is in an inconsistent state: config.py still references release-inputs/release-include but the directory is now at static/release-inputs/release-include. Linting will pass (Ruff and Pyright don't check path existence), but pytest will fail because tests that exercise config paths will break.

The plan should clarify: after Phase 0, only check_linting.py should pass. run_pytest.py should be run after Phase 1 when config.py paths are updated.

Summary of Remaining Issues
Severity	Count	Items
Medium	2	#5 ai_enrichment.py write-back path, #8 overlay silent failure
Low	6	#1 naming confusion, #4 ai_store_workflow.py, #6 wiki cache pain, #9 CI fixed dir, #10 gitignore removal timing, #12 ensure_dirs scope
Nit	3	#2 stage 05a verified OK, #3 library vs script, #7 atomicity guardrail adequate
The plan is now in much better shape. The two medium items to address:

Clarify whether ai_enrichment.py's write-back path (writing enriched content back to L2) also needs to change from outdir to PROCESSED_DIR.
Phase 0's verification command should be check_linting.py only — not run_pytest.py.

