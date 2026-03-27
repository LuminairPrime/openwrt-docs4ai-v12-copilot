# Plan: 02c 05a Refactor Doc

Draft a new planning document called  `docs/plans/v13/02c-05a-refactor-sonnet.md` that consolidates this file and the existing `02c-refactor.md` and `05a-refactor.md` concepts, expands them into a fuller option matrix, and adds adjacent low-risk hardening ideas. The recommended approach is to treat this as one cross-cutting reliability note with two primary problem areas: `02c` CI dependency/runtime efficiency and `05a` link-rewrite correctness/contract design. The document should separate immediate low-risk fixes from contract cleanup and structural rework so maintainers can choose a narrow patch or staged hardening path.

## Steps

1. Review and reuse the current focused notes in `docs/plans/v13/02c-refactor.md` and `docs/plans/v13/05a-refactor.md` as the seed problem statements.
2. Frame the new document as a consolidated refactor memo rather than a replacement architecture spec: preserve the current pipeline model and enumerate options by risk/effort.
3. Add a `Current Evidence` section summarizing the known behavior:
   `02c`: extract matrix still installs `pandoc` and `jsdoc-to-markdown` unconditionally for all matrix legs.
   `05a`: release-tree link rewriting currently depends on three regex-based transforms and fails on cookbook `../../module/file.md` style links.
4. Add a `Root Causes` section that distinguishes symptom from design fault:
   `02c`: dependency installation is encoded in workflow shell steps instead of a reusable per-extractor contract.
   `05a`: link semantics are split across authoring rules, normalization assumptions, assembly-time regex rewrites, and validator behavior.
5. Add a `Fix Matrix` section with flat option groups.
   `02c Immediate Fixes`:
   remove unconditional `pandoc` from repo-backed extract matrix; install `jsdoc-to-markdown` only for `02c`; move extract timing start before dependency install or split timing into install vs extract.
   `02c Medium Reworks`:
   add matrix metadata flags such as `needs_pandoc` and `needs_jsdoc_to_markdown`; add workflow contract tests covering those flags; document extractor tool dependencies in specs.
   `02c Structural Options`:
   move extractor dependency declarations into a checked-in manifest consumed by workflow/docs/tests; optionally add tool bootstrap helpers or reusable composite actions.
   `05a Immediate Fixes`:
   tighten regex to reject `..` as a module; add regression tests for `../../module/file.md`; ensure all three rewrite helpers are covered.
   `05a Medium Reworks`:
   replace duplicated regexes with a single shared link-rewrite helper; use path-aware logic instead of pattern substitution where possible; add pre-assembly validation for malformed cross-module links.
   `05a Structural Options`:
   define one canonical internal cross-link contract for authored/L2 content and map it to release surfaces in one place; alternatively normalize cookbook authored links into canonical L2 form during `02i` or `03`; align generator and validator to shared resolution rules.
6. Add a `Contract Conflicts To Resolve` section.
   Cookbook authoring spec says cookbook pages are authored for final shipped release-tree paths.
   Actual cookbook source currently uses cross-module links without `chunked-reference/`.
   Bundled-reference and chunked-reference outputs require different relative paths, so a single source-relative string format cannot safely serve every output surface without an explicit translation layer.
7. Add a `Recommended Path` section with staged tiers.
   Tier 0: documentation-only clarification of current issues and stopgap recommendations.
   Tier 1: low-risk production fixes only.
   Tier 2: contract cleanup and test hardening.
   Tier 3: structural refactor if maintainers want fewer hidden assumptions.
8. Add an `Adjacent Low-Risk Improvements` section.
   Update workflow/spec docs to record extractor external tool dependencies.
   Add tests for dependency-install conditions in workflow contract tests.
   Add tests for cookbook authored-link examples in unit tests.
   Add validator tests for the exact broken-link shapes observed.
   Ensure pipeline summary captures both install and extraction duration for performance work.
   Consider surfacing dependency/tool metadata in generated process or extract summaries for easier triage.
9. Add a `Not Recommended` section to reduce accidental over-engineering.
   Do not rename pipeline stages or script filenames.
   Do not redesign the full layer model.
   Do not add network-heavy validation or external URL checking as part of this work.
   Do not rewrite all authored cookbook content unless the canonical contract decision requires it.
10. Add an `Implementation Targets` section listing the likely touched files for each option family.
11. Add a `Verification` section that covers both code-level proof and doc consistency.
12. Keep the final document explicit about parallel vs sequential adoption paths so maintainers can cherry-pick narrow fixes.

## Relevant files

- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\docs\plans\v13\02c-05a-refactor-gpt.md` — target new consolidated planning document.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\docs\plans\v13\02c-refactor.md` — seed note for extract-matrix dependency inefficiency.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\docs\plans\v13\05a-refactor.md` — seed note for release-tree link rewrite bug.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\.github\workflows\openwrt-docs4ai-00-pipeline.yml` — current unconditional extractor dependency installation and timing boundaries.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\.github\scripts\openwrt-docs4ai-05a-assemble-references.py` — current link rewrite implementation and duplication point.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\.github\scripts\openwrt-docs4ai-08-validate-output.py` — dead-link validation behavior and shared semantics candidate.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\docs\specs\cookbook-authoring-spec.md` — current cookbook link contract that conflicts with observed source usage.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\docs\specs\script-dependency-map.md` — current per-script contract doc that can absorb extractor dependency metadata.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\tests\pytest\pytest_01_workflow_contract_test.py` — place to add workflow dependency-install contract checks.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\tests\pytest\pytest_09_release_tree_contract_test.py` — place to add exact regression tests for broken relative-link cases.
- `c:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\tests\pytest\pytest_00_pipeline_units_test.py` — place for unit tests around shared path/link rewrite helpers and `02c` support logic.

## Verification

1. Confirm the new document clearly separates immediate fixes from medium reworks and structural options.
2. Confirm every recommendation maps to an existing file or contract location, rather than floating as an abstract idea.
3. Confirm the document calls out the cookbook contract mismatch explicitly.
4. Confirm the document includes both `02c` performance/CI observations and `05a` correctness/contract observations.
5. Confirm low-risk adjacent improvements stay within current v13 boundaries and do not imply a layer-model redesign.

## Decisions

- Include both bug-fix and design-hardening options in one document because the two issues share a theme: hidden contracts encoded outside a single source of truth.
- Recommend staged adoption rather than one big refactor.
- Keep scope to low-risk improvements plus clearly labeled structural options; no broad renames or unrelated cleanup.

## Further Considerations

1. Prefer a canonical internal link contract over surface-specific authored links. This lowers future rewrite complexity even if maintainers keep a compatibility shim during transition.
2. Prefer machine-readable dependency declarations for extractors over shell-step tribal knowledge. This makes workflow behavior testable and documentation less likely to drift.
3. If the user wants repo output instead of planning-only handoff, the next execution session should create `docs/plans/v13/02c-05a-refactor-gpt.md` from this plan and then optionally align the adjacent spec files.
