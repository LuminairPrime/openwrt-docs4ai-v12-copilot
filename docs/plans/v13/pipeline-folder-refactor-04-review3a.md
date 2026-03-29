**Findings**

1. 🔴 Critical - Manifest path migration is incomplete and would break stage 05c and 05d
- The plan locks manifests under processed/manifests at pipeline-folder-refactor-04.md and pipeline-folder-refactor-04.md, but Phase 3 only specifies moving L1/L2 paths in promote_to_staging at pipeline-folder-refactor-04.md and pipeline-folder-refactor-04.md.
- Current scripts still hard-read cross-link-registry from OUTDIR:
  - openwrt-docs4ai-05c-generate-ucode-ide-schemas.py
  - openwrt-docs4ai-05d-generate-api-drift-changelog.py
  - openwrt-docs4ai-05b-generate-agents-and-readme.py
- Risk: hard failures in 05c/05d or silent degraded output in 05b if registry path is not explicitly remapped in the plan.

2. 🔴 Critical - CI path contract contradicts the locked schema
- Locked schema says every run local or CI is run-id scoped at pipeline-folder-refactor-04.md.
- Phase 9 sets fixed CI paths pipeline-ci/downloads and pipeline-ci/staged at pipeline-folder-refactor-04.md and pipeline-folder-refactor-04.md.
- This is a logic conflict that weakens traceability and makes run-record semantics ambiguous.

3. 🟡 Important - Phase independence claim conflicts with explicit cross-phase coupling
- Plan says each phase is independently testable at pipeline-folder-refactor-04.md.
- Same document requires Phase 5 and 7 to be coupled and not pytested in-between at pipeline-folder-refactor-04.md and pipeline-folder-refactor-04.md.
- This is not fatal, but it is a planning quality issue and can mislead execution sequencing.

4. 🟡 Important - Cookbook stage reference is incorrect in two places
- Static resource table and path update note reference stage 02h at pipeline-folder-refactor-04.md and pipeline-folder-refactor-04.md.
- Actual cookbook script is stage 02i at openwrt-docs4ai-02i-ingest-cookbook.py.
- Risk: implementer touches wrong script/checklist item.

5. 🟡 Important - ZIP naming policy is internally contradictory
- The document says no run-id in zip filename at pipeline-folder-refactor-04.md.
- Later Phase 8 requires run_hex in local zip names at pipeline-folder-refactor-04.md.
- This needs one canonical policy plus matching tests/docs to avoid churn.

6. 🟢 Suggestion - pipeline-run-state write semantics still light on safety guardrails
- The plan intentionally uses atomic rename without locking at pipeline-folder-refactor-04.md.
- For local parallel runs, pointer races are still possible; at minimum, add explicit “last-writer-wins” behavior and troubleshooting notes.

**Open Questions**
1. Is CI expected to use one stable run directory per workflow, or true run-id directories exactly as the locked schema states?
2. Should manifests exist only in processed/manifests, or be duplicated in staged root for backward compatibility during migration?
3. Is local zip naming user-facing (date only) or operator-facing (date plus run id)?

## Summary Table

| Overview | Ease of Remediation | Impact | Risk | Explanation |
|---|---:|---:|---|---|
| Manifest path migration gaps across 05b/05c/05d | 3 | 5 | 🔴 High | Plan moves manifests conceptually but does not fully map all consuming scripts. |
| CI run-directory contract inconsistency | 2 | 5 | 🔴 High | Locked schema and Phase 9 instructions conflict directly. |
| Phase independence contradiction | 1 | 3 | 🟡 Medium | Execution guidance is self-contradictory and can cause wrong phase validation behavior. |
| Stage numbering mismatch 02h vs 02i | 1 | 2 | 🟡 Medium | Incorrect references can produce implementation misses. |
| ZIP naming contradiction | 1 | 2 | 🟡 Medium | Two opposing naming rules create ambiguity for implementation and tests. |
| Weak local race guardrail for run-state pointer | 2 | 2 | 🟢 Low | Non-fatal but should be documented explicitly for concurrent local runs. |

## Detailed Plan

### Overview
Resolve internal contradictions and missing migration steps in the plan so implementation is executable without silent regressions or path drift.

### Explanation
The biggest risk is path migration incompleteness for manifests and CI run roots. The plan is close to production-ready, but a few unresolved contradictions can create hard failures in telemetry/schema generation and confusing rollout behavior.

### Requirements
- Single source of truth for CI run root behavior.
- Full consumer inventory for cross-link-registry and repo-manifest reads.
- One canonical zip naming policy matrix: local, CI artifact, release upload.
- Correct stage references and phase dependency wording.

### Implementation Steps
1. Add a dedicated Manifest Consumers subsection in Phase 4 or new Phase 4b listing 05b, 05c, 05d, 06 and exact path remaps.
2. Decide and document one CI directory contract:
   - Option A: true run-id path in CI.
   - Option B: fixed pipeline-ci path, and amend locked schema wording to “local run-id, CI fixed”.
3. Replace “each phase independently testable” with a realistic statement that explicitly marks coupled phases.
4. Correct stage references from 02h to 02i in static-resource and update-path sections.
5. Reconcile ZIP naming into one policy table and align Phase 8 text with that table.
6. Add explicit concurrency note for pipeline-run-state: last-writer-wins plus recommendation to avoid parallel local runs sharing one workspace.

### Testing
- Plan lint pass: verify no conflicting statements remain for run-root policy, phase independence, and zip naming.
- Path matrix verification: list each producer/consumer of L1, L2, manifests, telemetry with before/after paths and ensure all consumers are covered.
- Dry-run checklist simulation: walk Phases 0-12 against current scripts and confirm no unresolved reader of old manifest locations remains.
- Contract sanity check: ensure plan text and workflow expectations align for CI pathing and support-tree structure.