# V12 Stabilization and Operations Plan

## Goal

Stabilize v12 as an engineering system that is locally correct, documented, testable, and maintainable, then carry that state through real GitHub Actions verification. The near-term objective is not remote automation at any cost. The near-term objective is a trustworthy Windows development path, a coherent filesystem contract, and smoke tests that exercise the actual numbered scripts.

## 2026-03-09 Status Update

- Phases A through D are now far enough complete to support successful end-to-end GitHub Actions verification.
- Remote run `22864304564` completed `initialize`, the full `extract` matrix, `process`, and `deploy`.
- Deploy promoted generated outputs into `openwrt-condensed-docs/` via commit `3d3e6d3`.
- The successful `final-staging` artifact contained 151 L1 markdown docs, 151 L2 markdown docs, and 397 indexed symbols.
- L1 and L2 are now explicitly retained as durable generated outputs; only L0 remains transient.
- The next operational focus is warning reduction and content cleanliness, not first-pass remote bring-up.

## Primary Decisions

- Keep `openwrt-condensed-docs/` as the stable generated output root.
- Keep `L1-raw` and `L2-semantic` inside `openwrt-condensed-docs/` as durable outputs because they are small and operationally useful.
- Standardize on `L1-raw` and `L2-semantic` without leading dots.
- Keep the numbered `00` through `08` script family and document that numbering means execution order while letter suffixes mean deployment-time parallelizability.
- Treat old March 9 Opus bug reports as archive material, not as the live bug ledger.
- Prioritize local-first verification, then confirm conclusions with real GitHub Actions runs and artifacts.
- Keep AI summaries optional during development, but verify their pipeline position locally with seeded test files.

## Phases

### Phase A: Contract and documentation reset

1. Lock the canonical naming and filesystem contract.
2. Separate active specs from archival planning notes.
3. Create and maintain `docs/ARCHITECTURE.md` as the durable architecture source.
4. Rewrite implementation status so it reflects verifiable reality instead of inherited claims.
5. Refresh root docs so they match the actual script layout and active repo structure.

### Phase B: Local testing foundation

1. Rewrite the deterministic fixture smoke test around the current `03` through `08` flow and non-dotted paths.
2. Rewrite the sequential local smoke runner so it references only current script names.
3. Expand fixtures to cover YAML issues, cross-link cases, duplicate slug risks, and AI-summary insertion.
4. Add seeded AI-summary local tests to verify the optional summary path without remote model calls.

### Phase C: Local hardening and bug tracking

1. Start a new active v12 bug log and record only locally reproduced or locally verified findings.
2. Standardize path handling, subprocess behavior, logging, and failure semantics across scripts.
3. Improve shared comments, module docstrings, and helper surfaces where they directly reduce maintenance risk.
4. Generate L1 and L2 outputs under persistent local test runs so their size and shape can be measured before deciding long-term storage policy.

### Phase D: Readiness for remote testing

1. Define the local release-readiness bar.
2. Document what still requires GitHub-only verification.
3. Prepare a later remote staging and promotion model that validates generated outputs before overwrite.

### Phase E: Post-verification hardening

1. Triage the remaining soft AST warnings from generated JS and ucode docs.
2. Keep L1 and L2 committed to `openwrt-condensed-docs/` and keep L0 as CI or local transient state only.
3. Document the operating policy for auto-promoted output commits to `main`.

## Expected Deliverables for the First Stage

- Clean active spec directory under `docs/specs/v12/`
- Archived historical planning under `docs/archive/v12/`
- Updated root docs with reduced duplication
- Repaired local smoke test runners
- Active local bug log
- Measured L1 and L2 output characteristics from real local runs
- Advice on whether L1 and L2 should be committed, released, or kept as debug artifacts

## Current Outcome

- Active specs, local smoke tests, and remote GitHub Actions verification are all in place.
- Output measurement is now based on a successful remote artifact, not on estimates.
- Random output spot checks show the generated files are structurally aligned with the active layer contracts.
- Remaining work is operational tightening rather than first-pass stabilization.