# Code Review Improvements C: Execution Prompt

Use this prompt to execute the pipeline stabilization work end-to-end in one focused implementation pass.

## Prompt

You are the implementation agent for openwrt-docs4ai-pipeline. Execute the CI stabilization and hardening work in this exact order, committing only minimal, targeted changes that preserve current architecture and public contracts.

### Mission

1. Unblock GitHub Actions failures immediately.
2. Fix root-cause link rewriting in stage 05a without introducing formatting regressions.
3. Correct extractor dependency gating in workflow.
4. Add regression tests that fail before fix and pass after fix.
5. Update docs/specs to reflect the true behavior.

### Scope

- Primary files:
  - .github/scripts/openwrt-docs4ai-05a-assemble-references.py
  - .github/workflows/openwrt-docs4ai-00-pipeline.yml
  - tests/pytest/pytest_00_pipeline_units_test.py
  - tests/pytest/pytest_01_workflow_contract_test.py
  - tests/pytest/pytest_09_release_tree_contract_test.py
  - docs/specs/cookbook-authoring-spec.md
  - docs/specs/script-dependency-map.md
- Do not redesign the pipeline stage model.
- Do not rename scripts or modules.
- Do not introduce lossy markdown re-rendering.

### Implementation Plan

#### Phase 1: Immediate CI Unblock (blocking)

1. Fix 05a cross-module relative link rewriting for cookbook paths.
   - Ensure links of shape ../../module/file.md are correctly transformed for release-tree targets.
   - Ensure links already containing /chunked-reference/ are not double-rewritten.
   - Keep existing behavior for ../module/file.md and ./file.md where applicable.
   - Prevent malformed rewrites such as preserving unresolved traversal in transformed outputs.

2. Fix extract workflow dependency gating.
   - In extract matrix, install jsdoc-to-markdown only for 02c-scrape-jsdoc.py.
   - Remove unnecessary 02b npm install gating.
   - Pin jsdoc-to-markdown to a stable explicit version.
   - Keep pandoc installation isolated to extract_wiki only.

#### Phase 2: Regression Tests (required in same change set)

3. Add/extend unit tests for 05a rewrite helpers.
   - Include cases for:
     - ../../module/file.md that requires chunked-reference insertion.
     - ../../module/chunked-reference/file.md pass-through behavior.
     - ../module/file.md behavior.
     - ./file.md same-module behavior.

4. Add/extend release-tree contract tests.
   - Include a realistic cookbook -> cross-module link case that mirrors current CI failures.
   - Ensure tests assert broken links are detected when target truly missing.
   - Guard against false positives by asserting minimum required structure/files before loop-based checks.

5. Add/extend workflow contract tests.
   - Assert jsdoc-to-markdown install step exists and is conditionally gated to 02c.
   - Assert extract matrix does not perform unnecessary apt/pandoc install.
   - Prefer YAML structural assertions over brittle substring-only checks.

#### Phase 3: Spec and Contract Alignment

6. Update cookbook authoring spec.
   - Clarify expected cross-module authoring format.
   - Explicitly document which links are rewritten by 05a and which are pass-through.

7. Update script dependency map.
   - Add explicit external tools column.
   - Record jsdoc-to-markdown dependency for 02c.
   - Record pandoc dependency for 02a.
   - Mark non-dependent extractors as none.

### Quality and Safety Constraints

- Use minimal diffs; avoid unrelated refactors.
- Preserve existing output contracts under release-tree/.
- Avoid introducing new runtime dependencies unless strictly required.
- If introducing a dependency is unavoidable, justify it and pin version.
- No destructive git operations.

### Validation Checklist (must run)

Run these and ensure clean results:

1. python tests/run_pytest.py
2. python tests/check_linting.py
3. python -c "import yaml; yaml.safe_load(open('.github/workflows/openwrt-docs4ai-00-pipeline.yml', encoding='utf-8'))"

Also perform focused functional checks:

4. Verify 05a transformation with representative cookbook links:
   - ../../luci-examples/<file>.md
   - ../../wiki/<file>.md
   - ../../ucode/chunked-reference/<file>.md
5. Verify no stage 08 broken-link regressions in local pipeline simulation path.

### Definition of Done

- CI-blocking broken relative links are resolved.
- Workflow dependency gating is correct and minimal.
- New regression tests cover the exact failing patterns and pass.
- Docs/specs align with implemented behavior.
- No unrelated file churn.

### Optional Follow-up (deferred, not required now)

- Evaluate extractor manifest (extractors.yaml) as single source of truth for matrix/deps.
- Evaluate composite action extraction for repeated artifact upload/download blocks.
- Evaluate strict-mode fast-fail toggle for extract matrix.
