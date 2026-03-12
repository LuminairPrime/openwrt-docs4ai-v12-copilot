# V12 Stabilization and Operations Plan

## Goal

Stabilize v12 as an engineering system that is locally correct, documented, testable, and maintainable, then carry that state through real GitHub Actions verification. The near-term objective is not remote automation at any cost. The near-term objective is a trustworthy Windows development path, a coherent filesystem contract, and smoke tests that exercise the actual numbered scripts.

## 2026-03-10 Status Update

- Phases A through E are now far enough complete to support repeated end-to-end GitHub Actions verification and auto-published generated outputs.
- Remote runs `22877164042` and `22877413563` both completed `initialize`, the full `extract` matrix, `process`, and `deploy` with `0` hard failures and `1` soft warning.
- The second run explicitly proved the hardened wiki warm-cache path with `0` fetched, `92` unchanged, `5` too short, `0` reused-cache, and `0` failed pages.
- Deploy promoted generated outputs into `openwrt-condensed-docs/` via bot-authored commits `e13fb46` and `ffe48ad`.
- The successful `final-staging` artifact measurements remain 151 L1 markdown docs, 151 L2 markdown docs, and 397 indexed symbols.
- L1 and L2 remain durable generated outputs, while the public Pages copy excludes `L1-raw` and `L2-semantic`.
- The remaining operational focus is to keep the dockerman warning intentionally deferred, finish validating the bounded wiki cleanliness cleanup, and use only a lightweight committed-corpus sanity snapshot rather than broader new telemetry.

## 2026-03-11 Closeout Update

- The bounded wiki-cleanup closeout gate completed: `pytest -s tests/pytest/pytest_03_wiki_corpus_sanity_test.py -q` now reports `status=clean` for the committed wiki L2 corpus (`92` files; `wrap=0`, `color=0`, `html_table=0`, `sortable=0`, `footnote_aside=0`, `duplicate_lead_heading=0`).
- Local stabilization checks are currently green: `python tests/run_pytest.py` and `python tests/smoke/smoke_00_post_extract_pipeline.py` passed.
- Hosted verification remains healthy after stage-family alignment and hygiene follow-through: runs `22901356504` and `22901854476` completed successfully.
- `CONTENT-001` is now closed as fixed-and-verified in the active bug log.
- First-stage stabilization is considered complete; the next work is post-stabilization optimization and explicit AI-summary state separation.

## Primary Decisions

- Keep `openwrt-condensed-docs/` as the stable generated output root.
- Keep `L1-raw` and `L2-semantic` inside `openwrt-condensed-docs/` as durable outputs because they are small and operationally useful.
- Standardize on `L1-raw` and `L2-semantic` without leading dots.
- Keep the numbered `00` through `08` script family and document that numbering means execution order while letter suffixes mean deployment-time parallelizability.
- Treat old March 9 Opus bug reports as archive material, not as the live bug ledger.
- Prioritize local-first verification, then confirm conclusions with real GitHub Actions runs and artifacts.
- Keep AI summaries optional during development, but verify their pipeline position locally with seeded test files.
- Treat `REMOTE-008` as a truthful non-blocking warning and leave validator behavior unchanged unless stronger evidence appears.
- Auto-promote generated outputs from `staging/` into `openwrt-condensed-docs/` on push, schedule, and manual workflow runs using `rsync -a --delete`, with bot-authored commit messages in the form `docs: v12 auto-update YYYY-MM-DD`.

## Auto-Publish Policy

- The `process` job builds into `staging/` (`OUTDIR`) and uploads that tree as the `final-staging` artifact.
- The `deploy` job downloads `final-staging`, syncs it into `openwrt-condensed-docs/` with `rsync -a --delete`, and commits only generated-output changes when the staged tree differs from the repository copy.
- The auto-generated commit message format is `docs: v12 auto-update YYYY-MM-DD`.
- GitHub Pages is published from a `public/` copy of staging that excludes `L1-raw` and `L2-semantic`.
- Human-authored code and maintainer-doc changes should stay separate from these generated-output commits whenever practical.

## Lightweight Corpus Sanity Policy

- The project now keeps a lightweight committed-corpus sanity snapshot in `tests/pytest/pytest_03_wiki_corpus_sanity_test.py` instead of adding a broader telemetry subsystem.
- The intent is fast human triage, not a new enforcement regime: the snapshot prints current wiki L2 artifact levels and classifies them as `clean`, `bounded-stale`, or `abnormal`.
- Run it with `pytest -s tests/pytest/pytest_03_wiki_corpus_sanity_test.py -q` when you want the readable summary in terminal output.
- Treat `bounded-stale` as a signal that committed outputs may simply need regeneration after a logic fix; treat `abnormal` as a stronger indication that the normalization or promotion logic regressed.

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

- Active specs, local smoke tests, repeated remote GitHub Actions verification, and the generated-output promotion path are all in place.
- Output measurement is now based on a successful remote artifact, not on estimates.
- Random output spot checks and corpus sanity checks show the generated files are structurally aligned with the active layer contracts, and the bounded wiki cleanup now has clean committed-corpus evidence.
- First-pass stabilization is complete; remaining work is a controlled backlog centered on optimization, maintenance ergonomics, and AI-summary storage architecture.