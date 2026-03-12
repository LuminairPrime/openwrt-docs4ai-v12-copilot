# openwrt-docs4ai v12 System Architecture

## Architecture Invariants

- All runtime path and environment defaults flow through `lib/config.py`.
- `tmp/` is scratch space and must not be treated as durable truth.
- `openwrt-condensed-docs/` is the stable generated output root.
- Path contracts must remain cross-platform.
- Local sequential verification is the first required proof of correctness.
- Remote GitHub Actions verification and deployment promotion are now proven second-stage checks rather than hypothetical future behavior.
- Lettered scripts are designed for deployment-time parallelism but do not require parallel local execution.
- Helper surfaces that need direct unit coverage must remain import-safe instead of executing full script bodies at import time.

## Script Roles

### Extractors

- `02a` through `02h` produce L1 markdown and sidecar metadata.
- Extractors should fail loudly if the upstream source is present but zero useful outputs are produced.
- Extractors must not inject YAML frontmatter.
- `02b` is expected to keep its fenced-block normalization and known-example fixup helpers import-safe so ucode parsing regressions can be tested directly.

### Normalization and enrichment

- `03` converts L1 into L2 and writes the cross-link registry.
- `03` also promotes stable intermediates into `OUTDIR` so downstream scripts read a consistent tree.
- `03` may apply module-specific semantic cleanup during L1-to-L2 conversion when raw-source retention is still preserved in L1. The current live example is wiki-only cleanup of residual `WRAP`, `color`, duplicate lead-heading, and repeated HTML-table artifacts.
- `04` optionally enriches staged L2 files with AI metadata and performs its own AI-store preflight.

### Assembly and maps

- `05a` through `05d` produce publishable references, agent guidance, IDE outputs, and telemetry from staged L2 files.
- `06` generates routing indexes after the publishable reference assets exist.
- `07` produces the HTML landing page after the map outputs exist.

### Validation

- `08` validates the whole output tree and is the final local gate.
- `08` should keep parsing and validation helpers import-safe so markdown fence extraction, ucode import discovery, and output-tree validation logic can be covered independently.

## Local-First Testing Policy

- Local fixture-based tests must be able to exercise the L2 through L5 flow without relying on the live internet.
- Sequential local smoke tests must invoke the real numbered scripts using current names.
- AI summary integration must be verifiable locally with seeded data before any remote model usage is considered required.
- `tests/pytest/pytest_00_pipeline_units_test.py` is the focused regression suite for brittle helper surfaces in `02b`, `03`, and `08`.
- `tests/pytest/pytest_03_wiki_corpus_sanity_test.py` provides the lightweight committed-corpus sanity snapshot for `openwrt-condensed-docs/L2-semantic/wiki`; run it with `pytest -s` when you want the readable artifact summary in the console.

## Verified Remote Policy

- The workflow YAML is now part of the verified operating model, not just a speculative future target.
- The `process` job builds into `staging/`, uploads `final-staging`, and the `deploy` job promotes that tree into `openwrt-condensed-docs/` with `rsync -a --delete`.
- Push, schedule, and manual workflow runs may produce bot-authored `docs: v12 auto-update YYYY-MM-DD` commits when generated outputs changed.
- GitHub Pages publishes a `public/` copy that excludes `L1-raw` and `L2-semantic`.

## Debugging Entry Points

- Wiki cache trust, redirect handling, and short-page reuse issues start in `02a`.
- Wiki semantic-cleanup and staged L2 promotion issues start in `03`.
- Ucode fence classification and known-example normalization issues start in `02b`.
- Markdown code-block parsing, import extraction, and final gate behavior start in `08`.
- When debugging committed wiki output quality, compare the focused helper tests with the committed-corpus sanity snapshot before deciding whether the problem is stale published output or a fresh normalization regression.

## Naming Policy

- Keep long descriptive script filenames.
- Keep the numeric execution-order prefix.
- Use letter suffixes for scripts that are parallelizable within the same execution tier.
- Do not mix a bare stage id with same-family lettered siblings. Use either `04` or `04a` plus `04b`, never both.
- Keep non-pipeline maintainer helpers under `tools/`, not in the numbered stage surface.
- Prefer lowercase hyphenated filenames for human-authored spec documents.
