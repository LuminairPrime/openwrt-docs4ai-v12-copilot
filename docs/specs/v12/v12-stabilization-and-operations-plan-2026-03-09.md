# V12 Stabilization and Operations Plan

## Goal

Stabilize v12 as an engineering system that is locally correct, documented, testable, and maintainable before attempting full GitHub Actions verification. The near-term objective is not remote automation at any cost. The near-term objective is a trustworthy Windows development path, a coherent filesystem contract, and local smoke tests that exercise the actual numbered scripts.

## Primary Decisions

- Keep `openwrt-condensed-docs/` as the stable generated output root.
- Standardize on `L1-raw` and `L2-semantic` without leading dots.
- Keep the numbered `00` through `08` script family and document that numbering means execution order while letter suffixes mean deployment-time parallelizability.
- Treat old March 9 Opus bug reports as archive material, not as the live bug ledger.
- Prioritize local-first verification. Defer GitHub-only conclusions until a remote test repository exists.
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

## Expected Deliverables for the First Stage

- Clean active spec directory under `docs/specs/v12/`
- Archived historical planning under `docs/archive/v12/`
- Updated root docs with reduced duplication
- Repaired local smoke test runners
- Active local bug log
- Measured L1 and L2 output characteristics from real local runs
- Advice on whether L1 and L2 should be committed, released, or kept as debug artifacts