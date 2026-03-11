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

Status: complete

## Stage 7: Operational Observability And Contract Hardening

1. Emit a per-run timing and status summary that includes each pipeline member duration, key output counters, and final run result.
2. Keep script-level execution contracts explicit (mutability, dependencies, atomicity scope, and abort power) so stage placement remains auditable.
3. Keep optional stages explicitly optional (`SKIP_AI`) and avoid hidden implicit tolerances.
4. Preserve deploy isolation so only approved staged outputs can modify committed published artifacts.
5. Keep long-lived local scratch and legacy-review material in gitignored locations while keeping the public repo surface minimal.

Status: in progress

### 2026-03-11 Non-AI Option B Slice (implemented)

1. Parallelized extraction topology so `02a` runs independently while `02b` through `02h` remain clone-gated.
2. Added extractor contract diagnostics: matrix fail-fast disabled, per-extractor status manifests, and always-run extract summary artifact.
3. Added process and pipeline summary artifacts plus staging/public contract checks for faster operational triage.
4. Added workflow concurrency and timeout guardrails.
5. Added AI-stage timer logging and summary integration while still deferring deeper AI storage/persistence architecture changes.

## Current Focus

1. Preserve the now-verified stabilization baseline while continuing to treat `REMOTE-008` as a truthful deferred warning unless stronger evidence appears.
2. Formalize AI-summary state architecture so expensive optional enrichment remains isolated from normal output generation.
3. Add lightweight timing and run-state observability so performance and regressions are visible without deep log forensics.
4. Keep public-repo hygiene tight while retaining local legacy backups in gitignored paths.

## Immediate Next Action

Ratify and implement the AI-summary storage and promotion contract in a dedicated follow-up slice, then align AI-stage observability details with the new run-summary framework without regressing the stabilized non-AI path.
