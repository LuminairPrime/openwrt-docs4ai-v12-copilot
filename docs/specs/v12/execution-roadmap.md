# openwrt-docs4ai v12 Execution Roadmap

## Scope

This roadmap describes the current development sequence for v12 stabilization. It is a development roadmap, not a claim that all remote deployment work is already verified.

## Stage 1: Repository and spec reset

1. Lock the naming contract for `WORKDIR`, `OUTDIR`, `L1-raw`, and `L2-semantic`.
2. Separate active v12 specifications from archive materials.
3. Create or refresh the durable architecture documentation.
4. Remove redundant maintainer docs and reduce root-document duplication.

## Stage 2: Local testing reset

1. Repair the deterministic fixture-based smoke test.
2. Repair the sequential local smoke runner so it references only current script names.
3. Ensure the local smoke path uses isolated output directories and current path conventions.
4. Add or improve fixture coverage for link rewriting, YAML validity, slug stability, and AI summary insertion.

## Stage 3: Local output characterization

1. Run the local pipeline enough to generate persistent L1 and L2 outputs for measurement.
2. Record file counts, size distribution, and approximate storage footprint.
3. Use those measurements to recommend whether L1 and L2 should be committed, published as release artifacts, or retained only as debug outputs.

## Stage 4: Local bug-fixing and hardening

1. Maintain an active v12 bug log that tracks only locally reproduced or locally verified issues.
2. Standardize path handling, subprocess behavior, logging, and failure semantics across scripts.
3. Improve comments and shared helper behavior where it directly reduces maintenance or verification risk.

## Stage 5: Prepare the remote phase

1. Document what cannot be proven locally.
2. Define the later GitHub-only verification checklist.
3. Defer GitHub workflow judgments until a remote test repository exists.

## Immediate Next Action

Repair the local smoke tests and use them to produce measurable L1 and L2 outputs.
