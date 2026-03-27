# Code Review Improvements D: Executor Prompt

Use this prompt when you want an implementation agent to execute the full improvement program, not just summarize it. This version is stricter than C: it includes ordered execution waves, required files per step, stop/go checkpoints, fallback rules, and explicit acceptance criteria.

## Prompt

You are the implementation agent for openwrt-docs4ai-pipeline. Execute the full code-review improvement program in controlled waves. The objective is to fix the current CI failures, harden the code and tests so the same regressions cannot reappear silently, and implement the broader workflow and validation improvements where they can be landed safely.

Do not treat this as a planning exercise. This is an execution brief.

## Primary Outcome

Deliver a repository state where:

1. The current GitHub Actions failure mode is fixed at the root cause.
2. The fix is protected by regression tests.
3. Workflow dependency handling is correct, pinned, and maintainable.
4. Specs and contracts reflect actual behavior.
5. The broader roadmap improvements are implemented to the largest safe extent without destabilizing the repo.

## Invariants

You must preserve these unless a listed step explicitly requires otherwise:

- The numbered pipeline stage model.
- The release-tree public contract.
- Non-lossy markdown handling.
- Existing artifact naming unless a step explicitly justifies a change.

## Non-Negotiable Constraints

- Use minimal, focused diffs.
- Do not rename numbered scripts.
- Do not redesign the layer model.
- Do not introduce a markdown parse/render path that can rewrite formatting.
- Do not add a dependency unless it is pinned, justified, and covered by tests.
- Do not leave broad roadmap items vague; either implement the safe slice or explicitly bound the deferral in code/tests/specs.
- End with a green local validation pass.

## Execution Order

Work in five waves. Do not start a later wave until the current wave reaches its stop/go checkpoint.

---

## Wave 1: Reproduce and Lock the Failing Behavior

### Step W1.1: Confirm the current failure class

Goal:

- Reconfirm the real failing path shapes that broke CI.

Required evidence:

- Identify cookbook-authored cross-module links of shape ../../module/file.md.
- Distinguish them from links already containing /chunked-reference/.
- Confirm which output paths stage 08 reported as broken.

Expected touched files:

- None required.

### Step W1.2: Add failing regression coverage before the main fix

Goal:

- Add tests that would fail against the broken implementation.

Required files:

- tests/pytest/pytest_00_pipeline_units_test.py
- tests/pytest/pytest_01_workflow_contract_test.py
- tests/pytest/pytest_09_release_tree_contract_test.py
- supporting conftest or test helper files only if needed

Required assertions:

- ../../module/file.md requires chunked-reference insertion when emitted to cookbook release-tree outputs.
- ../../module/chunked-reference/file.md passes through unchanged.
- ../module/file.md still behaves correctly where valid.
- ./file.md same-module behavior is still covered.
- Release-tree contract tests fail when the target is missing.
- Release-tree contract tests cannot silently pass on empty output trees.
- Workflow contract tests verify jsdoc-to-markdown is gated to 02c only.
- Workflow contract tests verify extract matrix does not install pandoc.

Stop/Go checkpoint for Wave 1:

- Stop if the new tests do not fail for the currently broken behavior.
- Go only once at least one new or updated test demonstrates the current bug class.

---

## Wave 2: Fix the Current CI Breakage

### Step W2.1: Fix 05a link rewriting at the root cause

Goal:

- Eliminate the cookbook broken-link class without introducing formatting loss.

Primary file:

- .github/scripts/openwrt-docs4ai-05a-assemble-references.py

Secondary file, only if needed:

- .github/scripts/openwrt-docs4ai-03-normalize-semantic.py
- a small extracted helper module if it materially improves correctness and testability

Implementation requirements:

- Correctly handle ../../module/file.md for cookbook bundled and chunked outputs.
- Do not double-rewrite ../../module/chunked-reference/file.md.
- Preserve valid ../module/file.md and ./file.md behavior.
- Do not emit malformed relative paths.
- Prefer path-aware logic over brittle regex expansion if the change remains small and non-lossy.

Decision hierarchy:

1. Smallest safe path-aware fix.
2. If not practical, smallest safe regex correction backed by tests.
3. Only if necessary, a narrowly scoped helper extraction for deterministic rewriting.

Forbidden approaches:

- Full markdown AST parse and re-render.
- Broad rewrite of cookbook content authoring in the same pass.

### Step W2.2: Fix extract workflow dependency gating

Goal:

- Remove current dependency mistakes and floating installs.

Primary file:

- .github/workflows/openwrt-docs4ai-00-pipeline.yml

Requirements:

- jsdoc-to-markdown installs only for 02c-scrape-jsdoc.py.
- Remove any 02b npm install condition.
- Pin jsdoc-to-markdown to an explicit stable version.
- Keep pandoc isolated to extract_wiki only.
- Add npm caching only if it stays easy to understand and does not obscure behavior.

Stop/Go checkpoint for Wave 2:

- Go only once the new regression tests from Wave 1 pass for the 05a and workflow fixes.

---

## Wave 3: Align Specs With Reality

### Step W3.1: Update cookbook authoring contract

Primary file:

- docs/specs/cookbook-authoring-spec.md

Required updates:

- State which cookbook cross-module link forms authors should write.
- State which forms 05a rewrites.
- State which forms already represent final output paths and therefore pass through unchanged.
- Remove or correct any spec text that contradicts the implemented behavior.

### Step W3.2: Update dependency contract documentation

Primary file:

- docs/specs/script-dependency-map.md

Required updates:

- Add explicit external tools tracking if absent.
- Record pandoc for 02a.
- Record jsdoc-to-markdown for 02c.
- Mark other relevant extractors as none where accurate.

Stop/Go checkpoint for Wave 3:

- Go only once the docs/specs describe the implementation that now exists, not the prior assumption.

---

## Wave 4: Land the Broader Workflow Improvements Safely

These items come from the broader roadmap. Implement them to the largest safe extent. If a full version is too invasive, implement the safe contract-improving subset and keep the repo green.

### Step W4.1: Improve extractor matrix maintainability

Preferred outcome:

- Centralize extractor metadata in a manifest used by the workflow.

Acceptable safe subset:

- Keep workflow-driven matrix, but reduce duplication and make dependency conditions explicit and test-covered.

If you implement a manifest:

- Keep it small and obvious.
- Include script, module, skip behavior, and external tools.
- Add workflow/tests validation so manifest and workflow cannot silently drift.

Suggested touched files, if chosen:

- .github/workflows/openwrt-docs4ai-00-pipeline.yml
- new manifest file under .github/ or docs/specs-supported workflow location
- tests/pytest/pytest_01_workflow_contract_test.py

### Step W4.2: Reduce repeated artifact boilerplate if safe

Preferred outcome:

- Extract repeated upload/download artifact logic into a composite action.

Guardrails:

- Do not change artifact names unless required.
- Do not make debugging harder.
- Skip this if the abstraction adds more indirection than value.

### Step W4.3: Improve extractor failure policy

Preferred outcome:

- Add a strict-mode or explicit fail-fast switch for extractor failures.

Guardrails:

- Do not break current default behavior unless the existing contract clearly needs changing.
- Prefer additive control over silent semantic replacement.

### Step W4.4: Pin and cache external tooling

Required outcome:

- No floating latest installs for critical external tools where avoidable.

Guardrails:

- Keep setup logic readable.
- Prefer standard Actions support.

Stop/Go checkpoint for Wave 4:

- Go only once any broader workflow changes remain understandable, validated, and do not alter release or artifact contracts accidentally.

---

## Wave 5: Strengthen Test Robustness Beyond the Immediate Bug

### Step W5.1: Remove empty-tree false positives

Required outcome:

- Integration tests fail loudly when upstream stages produced no meaningful output.

### Step W5.2: Improve fixture isolation

Required outcome:

- Prefer tmp_path or equivalent isolated test fixtures over real tmp/ci filesystem coupling where practical.

### Step W5.3: Evaluate HTTP mocking for wiki extraction tests

Preferred outcome:

- Introduce mocked or recorded HTTP behavior for wiki-related tests only if the repo already has, or can safely support, the required testing pattern.

Fallback:

- If full HTTP mocking is too invasive for this pass, add the smallest seam or helper change that makes it easier to do later, without introducing a half-finished framework.

Stop/Go checkpoint for Wave 5:

- Stop if the robustness improvement starts to expand scope without a clear payoff.
- Go only if the added tests materially reduce false positives or fragility.

---

## Validation Gates

You must run these and get clean results before finishing:

1. python tests/run_pytest.py
2. python tests/check_linting.py
3. python -c "import yaml; yaml.safe_load(open('.github/workflows/openwrt-docs4ai-00-pipeline.yml', encoding='utf-8'))"

You must also perform focused verification for the repaired failure class:

4. Verify cookbook link handling for:
   - ../../luci-examples/<file>.md
   - ../../wiki/<file>.md
   - ../../procd/<file>.md
   - ../../ucode/chunked-reference/<file>.md
5. Confirm the release-tree validator no longer reports the current broken-link class.
6. If manifest or composite-action work was added, verify workflow structure still matches current job and artifact contracts.

## Required Deliverables By Wave

Wave 1 deliverables:

- Regression tests that expose the broken 05a/workflow behavior.

Wave 2 deliverables:

- 05a fix.
- Workflow dependency gating fix.
- Passing regression tests for the immediate bug class.

Wave 3 deliverables:

- Updated cookbook authoring spec.
- Updated dependency map.

Wave 4 deliverables:

- Safest landed subset of workflow maintainability improvements, with tests if behavior changes.

Wave 5 deliverables:

- Safer integration test structure and fixture isolation improvements where practical.

## Acceptance Criteria

The task is complete only when all are true:

- The current CI-blocking cookbook broken-link failures are fixed.
- The fix is covered by regression tests for rewrite and pass-through behavior.
- Workflow dependency gating is correct, pinned, and test-covered.
- Workflow/release-tree tests are materially harder to fool with empty-output or substring-only false positives.
- cookbook-authoring-spec.md and script-dependency-map.md match the implemented behavior.
- The broader roadmap items were either implemented safely or reduced to the largest safe validated subset.
- No unrelated churn or public contract regressions were introduced.

## Explicit Non-Goals

- Do not rename numbered scripts.
- Do not redesign the whole architecture.
- Do not add lossy markdown serialization.
- Do not create broad new design docs.
- Do not leave broad roadmap items as hand-wavy future work without either landing a safe subset or bounding the deferral clearly.

## Final Execution Rule

If a broader improvement conflicts with repo stability, choose the smallest coherent safe slice that preserves correctness, lands test coverage, and keeps the repository green. If a fix is not verified, it is not done.