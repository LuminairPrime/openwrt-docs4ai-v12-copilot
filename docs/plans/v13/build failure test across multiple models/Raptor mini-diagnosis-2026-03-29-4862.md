# Raptor mini diagnosis 2026-03-29

## Context
- Project: openwrt-docs4ai-pipeline
- Branch: main
- Failure stage: process -> Validate published output (08)
- Root cause: broken relative links from release-tree cookbook pages (e.g. `../../wiki/wiki_page-guide-developer-packages.md`) not rewritten into chunked paths

## Tier list (likelihood and impact)

1. Critical (most likely + high impact)
   - `rewrite_release_relative_links` and `rewrite_release_chunked_links` did not convert `../../<module>/<file>.md` into chunked path.
   - CI fails due path check in `openwrt-docs4ai-08-validate-output.py`, enforcing strict existence.

2. High
   - `config.RELEASE_TREE_DIR / config.SUPPORT_TREE_DIR` path mismatches after folder refactor (root/ relative references may resolve wrong if not aligned with new STAGED/OUTDIR semantics).

3. Medium
   - `process` contract generation may be missing generated package `openwrt-docs4ai-pipeline-*.zip` in `outdir/packages` due staged path mismatch.

4. Low
   - Potential script dependency handoff: `05a` to `07` missing L2/L3 next-step resync; regressions in a subset run (non-full) where `--allow-partial` semantics block coverage.

## Implemented fix
- Updated link rewrite rules in `openwrt-docs4ai-05a-assemble-references.py`.
- Added/updated pytest tests in `pytest_00_pipeline_units_test.py`.
- Local validation passes: `34 passed`.

## Next step
- Re-run full pipeline in CI to confirm stage 08 passes now.
