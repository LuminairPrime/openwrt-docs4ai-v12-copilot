# openwrt-docs4ai v12 Execution Roadmap

## Scope

This roadmap describes the current development sequence for v12 after the initial stabilization pass. It records what is already done, what is currently being hardened, and what remains worth doing.

## Stage 1: Repository and spec reset

1. Lock the naming contract for `WORKDIR`, `OUTDIR`, `L1-raw`, and `L2-semantic`.
2. Separate active v12 specifications from archive materials.
3. Create or refresh the durable architecture documentation.
4. Remove redundant maintainer docs and reduce root-document duplication.

Status: complete

## Stage 2: Local testing reset

1. Repair the deterministic fixture-based smoke test.
2. Repair the sequential local smoke runner so it references only current script names.
3. Ensure the local smoke path uses isolated output directories and current path conventions.
4. Add or improve fixture coverage for link rewriting, YAML validity, slug stability, and AI summary insertion.

Status: complete

## Stage 3: Local output characterization

1. Run the local pipeline enough to generate persistent L1 and L2 outputs for measurement.
2. Record file counts, size distribution, and approximate storage footprint.
3. Use those measurements to recommend whether L1 and L2 should be committed, published as release artifacts, or retained only as debug outputs.

Status: complete

## Stage 4: Local bug-fixing and hardening

1. Maintain an active v12 bug log that tracks only locally reproduced or locally verified issues.
2. Standardize path handling, subprocess behavior, logging, and failure semantics across scripts.
3. Improve comments and shared helper behavior where it directly reduces maintenance or verification risk.

Status: complete

## Stage 5: Prepare the remote phase

1. Document what cannot be proven locally.
2. Define the later GitHub-only verification checklist.
3. Verify the workflow against a live repository and record the promotion contract once confirmed.

Status: complete

## Stage 6: Post-verification hardening

1. Harden verified weak points without regressing the now-stable remote path.
2. Keep the dockerman warning deferred unless stronger evidence appears.
3. Tighten wiki-only L2 cleanup instead of mutating L1 raw retention.
4. Keep brittle helper surfaces in `02b`, `03`, and `08` directly unit-testable.
5. Add only lightweight corpus sanity checks unless a stronger telemetry need is proven.

Status: in progress

## Current Focus

1. Push the local wiki-cleanup and helper-testability patch through live GitHub Actions verification.
2. Use the committed-corpus sanity snapshot as a quick read on whether wiki artifact levels look bounded, improved, or abnormal.
3. Close `CONTENT-001` only after a regenerated corpus or remote run confirms the committed outputs reflect the new `03` cleanup behavior.

## Immediate Next Action

Commit the current post-verification hardening pass, run a live workflow, and compare the resulting committed wiki corpus against the sanity snapshot baseline.
