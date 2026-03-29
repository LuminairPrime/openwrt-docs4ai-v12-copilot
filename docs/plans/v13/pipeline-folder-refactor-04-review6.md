**Findings**

1. 🔴 Critical - Phase 9 still under-specifies the CI workflow migration and leaves a large hidden blast radius.
The plan updates the high-level CI roots in pipeline-folder-refactor-04.md, but the real workflow still uses WORKDIR as the parent for cache state, extractor contracts, L1 artifact upload paths, and run summaries in many places. Concrete examples:
openwrt-docs4ai-00-pipeline.yml,
openwrt-docs4ai-00-pipeline.yml,
openwrt-docs4ai-00-pipeline.yml.
The current plan only calls out support-tree count replacements in the process-summary script, not the broader path contract changes. If implemented literally, CI will still reference WORKDIR/L1-raw and OUTDIR/L1-raw/L2-semantic in multiple places even after those move to processed, and the summary contract will still expect repo-manifest.json and cross-link-registry.json at staged root.

2. 🔴 Critical - Phase 3 still does not fully describe the producer-side move for manifests, so later phases depend on a path that Phase 3 never actually creates.
Phase 3 currently only says to redirect L1 and L2 into processed in pipeline-folder-refactor-04.md. But current stage 03 also copies cross-link-registry.json and repo-manifest.json into OUTDIR root at openwrt-docs4ai-03-normalize-semantic.py, and its partial-rerun guard still checks OUTDIR at openwrt-docs4ai-03-normalize-semantic.py. Later plan sections assume manifests are already under processed/manifests, including the config map and support-tree copy logic at pipeline-folder-refactor-04.md and pipeline-folder-refactor-04.md. That is a producer/consumer mismatch.

3. 🟡 Important - The document still carries two incompatible CI contracts, and the CI env var contract is incomplete.
The locked schema still says every local or CI run writes to a timestamped pipeline-YYYYMMDD... directory at pipeline-folder-refactor-04.md. Phase 9 now says CI intentionally uses a fixed pipeline-ci root at pipeline-folder-refactor-04.md. That is still an internal contradiction. On top of that, Phase 9 does not explicitly say to set PIPELINE_RUN_DIR, even though its own rationale says CI always takes the env-var resolution path first. As written, the plan leaves the run-record path contract ambiguous.

4. 🟡 Important - The Phase 4 manifest-consumer section is better, but still not fully true to the code.
The plan correctly added manifest consumers in pipeline-folder-refactor-04.md, and it now separately calls out the stage 06 repo-manifest fallback in pipeline-folder-refactor-04.md. But it still says stage 05d reads repo-manifest.json. Current stage 05d only reads cross-link-registry.json at openwrt-docs4ai-05d-generate-api-drift-changelog.py. The real additional repo-manifest fallback still present in code is stage 03 at openwrt-docs4ai-03-normalize-semantic.py. This is not catastrophic, but the plan positions itself as the authoritative locked design, so factual drift matters.

5. 🟢 Medium - The explicit Phase 11 test checklist still understates known breakage sites.
The pre-audit grep instruction is good, but the named checklist in pipeline-folder-refactor-04.md still omits known cases like pytest_05_manage_ai_store_cli_test.py and pytest_10_routing_provenance_test.py. This is not a blocker because the grep is the real safety net, but the table looks more exhaustive than it is.

**Open Questions / Assumptions**

1. I am assuming the intended CI design is a fixed pipeline-ci root, not a true per-run timestamped root. If that assumption is wrong, both the top schema and Phase 9 need to change together.
2. I am assuming manifests are supposed to exist only in processed/manifests after the refactor, not in both processed/manifests and staged root. The current plan reads that way, but Phase 3 does not yet encode it explicitly.
3. I am assuming the stage 07 local browse index is intended to be release-tree-focused after the new Option A text, which is now coherent.

**Score**

7/10.

The plan is strong on architecture intent, guardrails, anti-truths, and phased execution. It is materially better than earlier drafts. It is not yet implementation-safe because the two hardest parts of the refactor are still under-modeled: the producer-side manifest move in Phase 3 and the full CI workflow path migration in Phase 9.

**Tier List Suggestions**

**S Tier**
- Expand Phase 9 from a deploy-focused checklist into a full CI path migration matrix. It should enumerate every workflow use of WORKDIR/L1-raw, OUTDIR/L1-raw, OUTDIR/L2-semantic, staged-root manifest files, cache paths, artifact upload/download paths, extract-status, extract-summary, and run-summary.
- Amend Phase 3 so it explicitly moves cross-link-registry.json and repo-manifest.json into processed/manifests, and explicitly changes the partial-rerun guard from OUTDIR to PROCESSED_DIR.

**A Tier**
- Reconcile the CI contract in one place: either split the locked schema into local and CI variants, or document pipeline-ci as the CI PIPELINE_RUN_DIR and list PIPELINE_RUN_DIR explicitly in Phase 9.
- Correct the Phase 4 truth claims: remove the statement that stage 05d reads repo-manifest.json, and add stage 03 fallback cleanup explicitly alongside stage 06.

**B Tier**
- Extend the explicit test checklist to include the already-known pytest_05 and pytest_10 cases, plus workflow contract assertions that will change when L1/L2/manifests move.
- Add one short “workflow scratch policy” note saying whether extract-status, extract-summary, and run-summary intentionally live under downloads in CI or should stay at the pipeline root.

**C Tier**
- Tighten wording where the plan says “independently testable” and “authoritative” so it better matches the fact that some phases are coupled and some code truths are still being discovered.
- Add a one-line note near the top saying the anti-truth sections are normative and take precedence over earlier historical plan files.

**What The Plan Does**

1. It restructures pipeline output into three zones per run: downloads, processed, and staged, all under tmp.
2. It introduces a run-state pointer and a per-run record so local runs can share one current pipeline root while CI can override it through env vars.
3. It moves authored/static inputs into a single static tree, including cookbook source, AI store data, and release overlays.
4. It moves L1 and L2 into processed and keeps staged for deliverables, release-tree, support-tree, telemetry, and packages.
5. It dissolves the redundant support-tree raw and semantic-pages copies while keeping manifests and telemetry bundled.
6. It aligns the LuminairPrime gh-pages preview with the production pages deployment so both publish release-tree rather than the whole generated tree.
7. It defers the wiki cache fix and incremental download work instead of mixing those concerns into the folder refactor.
8. It moves packaging into staged/packages and standardizes zip naming separately for local and CI contexts.
9. It removes the openwrt-condensed-docs promotion step and treats release-tree as the direct deployment surface.
10. It plans the required updates across scripts, CI, tests, gitignore, and architecture docs to make the new layout the source of truth.

**What Is Good About The Plan**

- It is unusually explicit about intent, not just mechanics. The anti-truths and guardrails are a real strength.
- It distinguishes local and CI behavior thoughtfully, even where the wording still needs reconciliation.
- It identifies silent-failure risks, not just hard failures.
- It does a good job separating in-scope refactor work from deferred work like wiki cache and incremental downloads.
- It is strong on operational consequences: support-tree rationale, deployment surfaces, baseline behavior, and zip handling are all better-than-average planning.

**What Is Bad About The Plan**

- The most failure-prone area, the CI workflow path contract, is still not described with the same rigor as the script-level changes.
- The producer-side side of the manifest move is still implicit when it needs to be explicit.
- The top-level schema and the Phase 9 CI policy still contradict each other.
- A few factual claims are still slightly off, especially around manifest consumers.
- Some checklists look exhaustive while still depending on a grep pass to catch important cases.

**What Is Good About My Interpretation Of The Plan**

- It is code-grounded, not just document-grounded. The review cross-checks the plan against current scripts and the workflow.
- It is strongest where the plan is weakest: producer/consumer path alignment, workflow blast radius, and silent contract breaks.
- It distinguishes truth errors from style disagreements, which matters in a refactor plan review.

**What Is Bad About My Interpretation Of The Plan**

- In earlier passes, I over-attributed repo-manifest usage to stage 05d. The current code shows that was too broad.
- Some earlier risk calls were based on likely future config behavior rather than only the plan text itself. That was useful for catching edge cases, but it also made a few points sound more certain than the code justified.
- Because the plan is evolving fast, some prior findings were fixed between passes, so the interpretation needs constant revalidation against the current file, not memory of the previous one.

I rechecked the current draft against stage 03 and the workflow. Two issues remain at true merge-blocker level; the earlier Phase 6 and PIPELINE_RUN_DIR issues are fixed in the current plan and drop out of blocker tier.Addendum: Merge-Blocker-Only Review

I’m using a strict bar here: a merge blocker means following the plan as written is likely to produce a broken implementation, failing CI, or a producer/consumer path contract that cannot work end to end.

🔴 Merge blocker - Phase 9 still under-specifies the CI path migration enough that the workflow would remain broken even if the script changes land.
The plan updates the CI roots in pipeline-folder-refactor-04.md:1058-1092, but it only explicitly calls out the process-summary support-tree count replacements. The real workflow still assumes:
openwrt-docs4ai-00-pipeline.yml:89-114
for cache and extractor contract paths under WORKDIR,
openwrt-docs4ai-00-pipeline.yml:187-195
for artifact uploads from WORKDIR/L1-raw,
and openwrt-docs4ai-00-pipeline.yml:728-760
for required_paths, L1/L2 counts, and support-tree raw/semantic counts rooted in OUTDIR.
Those assumptions all change under the new schema. If the plan is implemented literally, CI contract checks and summaries will still look in the old places.
What to add before merge:

A full Phase 9 path matrix for workflow uses of WORKDIR, OUTDIR, PROCESSED_DIR, STAGED_DIR.
Explicit updates for extractor contract checks, cache paths, artifact upload/download paths, run-summary and extract-summary scratch dirs, and required_paths in the inline Python summary step.
Explicit update of staged-root manifest expectations in the workflow summary step, since repo-manifest.json and cross-link-registry.json are no longer supposed to live at OUTDIR root.
🔴 Merge blocker - Phase 3 still does not explicitly move the manifest producers, but later phases depend on that move having happened.
Phase 3 currently only says to redirect L1 and L2 into processed in pipeline-folder-refactor-04.md:785-788. But current stage 03 still copies cross-link-registry.json and repo-manifest.json into OUTDIR root at openwrt-docs4ai-03-normalize-semantic.py:900-908, and its partial-rerun guard still checks OUTDIR at openwrt-docs4ai-03-normalize-semantic.py:924-932.
Later sections of the plan already assume manifests are under processed/manifests, including the config map at pipeline-folder-refactor-04.md:114-115 and the support-tree copy update at pipeline-folder-refactor-04.md:919-924. That producer-side move is not optional; it is the prerequisite for Phase 4, Phase 5, Phase 7, and the workflow summary logic.
What to add before merge:

In Phase 3, explicitly move:
cross-link-registry.json to PROCESSED_DIR/manifests
repo-manifest.json to PROCESSED_DIR/manifests
In Phase 3, explicitly change fail_if_partial_staging_promotion to validate against PROCESSED_DIR, not OUTDIR.
In Phase 3, state whether staged root should no longer contain those manifest files at all. The rest of the plan reads as if the answer is yes, so that should be made explicit.
Not In Blocker Tier On The Current Draft

The Phase 9 PIPELINE_RUN_DIR issue is fixed. The plan now explicitly sets it in pipeline-folder-refactor-04.md:1060-1065.
The Phase 6 web-index issue is fixed. The plan now explicitly chooses Option A and explains that L1-raw and L2-semantic disappear from the index after Phase 3 in pipeline-folder-refactor-04.md:936-961.
The statement that stage 05d reads repo-manifest is still factually sloppy in pipeline-folder-refactor-04.md:884-891, but I would not block merge on that if the two items above are fixed.
No other issues in the current draft rise to merge-blocker level for me.