# openwrt-docs4ai v12 System Architecture

## Architecture Invariants

- All runtime path and environment defaults flow through `lib/config.py`.
- `tmp/` is scratch space and must not be treated as durable truth.
- `openwrt-condensed-docs/` is the stable generated output root.
- Path contracts must remain cross-platform.
- Local sequential verification is the first required proof of correctness.
- Lettered scripts are designed for deployment-time parallelism but do not require parallel local execution.

## Script Roles

### Extractors

- `02a` through `02h` produce L1 markdown and sidecar metadata.
- Extractors should fail loudly if the upstream source is present but zero useful outputs are produced.
- Extractors must not inject YAML frontmatter.

### Normalization and enrichment

- `03` converts L1 into L2 and writes the cross-link registry.
- `03` also promotes stable intermediates into `OUTDIR` so downstream scripts read a consistent tree.
- `04` optionally enriches staged L2 files with AI metadata.

### Assembly and maps

- `05` produces L3 skeletons and L4 monoliths from staged L2 files.
- `06a` through `06d` generate indexes, agent guidance, IDE outputs, and telemetry.
- `07` produces the HTML landing page after the map outputs exist.

### Validation

- `08` validates the whole output tree and is the final local gate.

## Local-First Testing Policy

- Local fixture-based tests must be able to exercise the L2 through L5 flow without relying on the live internet.
- Sequential local smoke tests must invoke the real numbered scripts using current names.
- AI summary integration must be verifiable locally with seeded data before any remote model usage is considered required.

## Deferred Remote Policy

The workflow YAML remains part of the repository, but GitHub-specific behavior, artifact transport, scheduled runs, and deployment promotion are not treated as verified architecture claims until a remote repository is available for testing.

## Naming Policy

- Keep long descriptive script filenames.
- Keep the numeric execution-order prefix.
- Use letter suffixes for scripts that are parallelizable within the same execution tier.
- Prefer lowercase hyphenated filenames for human-authored spec documents.
