# v12 Bug Log

This is the active bug log for the current stabilization pass.

Rules:

- Only log issues that were reproduced locally or verified directly in the current repository state.
- Treat `docs/archive/v12/v12-bugs-3-9-opus.md` and `docs/archive/v12/v12-bugs-3-9.md` as historical context only.
- Track status transitions clearly: `open`, `fixed-pending-test`, `fixed-and-verified`, `deferred`, `not-reproduced`.

## Active Entries

| ID | Status | Area | Summary | Notes |
| --- | --- | --- | --- | --- |
| LOCAL-001 | fixed-and-verified | local-tests | `tests/openwrt-docs4ai-00-smoke-test.py` referenced obsolete script names and phase numbers | Rewritten as a sequential fixture-backed runner for the current `03` through `08` flow. Verified with `python tests/openwrt-docs4ai-00-smoke-test.py`. |
| LOCAL-002 | fixed-and-verified | local-tests | `tests/00-smoke-test.py` seeded `tmp/.L1-raw` instead of `tmp/L1-raw` | Rewritten as a deterministic fixture-backed harness using the current non-dotted path contract. Verified with `python tests/00-smoke-test.py`. |
| LOCAL-003 | fixed-and-verified | documentation | Root documentation authority boundaries were unclear and active specs lived beside archival planning material | Fixed by the docs/specs and docs/archive reorganization in the current milestone. |
| LOCAL-004 | fixed-and-verified | documentation | `CONTRIBUTING.md` duplicated maintainer guidance without providing meaningful contributor process | Removed and folded into `DEVELOPMENT.md` as part of repo simplification. |
| LOCAL-005 | fixed-and-verified | normalization | `03-normalize-semantic.py` over-protected document bodies during cross-link injection and over-broadened deprecation detection across sections | Fixed by narrowing header protection, protecting frontmatter explicitly, and limiting deprecation scans to the current section. Verified by both smoke runners. |
| LOCAL-006 | fixed-and-verified | assembly-indexing | `05-assemble-references.py`, `06b-generate-agents-md.py`, and `06c-generate-ide-schemas.py` contained runtime or output-shape defects surfaced by fixture tests | Fixed by correcting monolith assembly, rebuilding AGENTS summary generation, and repairing the ucode `.d.ts` generator. Verified by both smoke runners. |
| LOCAL-007 | fixed-and-verified | ai-enrichment | `04-generate-ai-summaries.py` only worked safely in skip mode and could not be exercised locally without external tokens | Fixed by adding a cache-backed local enrichment path and verifying it with `python tests/00-smoke-test.py --run-ai` and `python tests/openwrt-docs4ai-00-smoke-test.py --run-ai`. |
| LOCAL-008 | fixed-and-verified | validation-windows | `08-validate.py` wrote AST-check scratch files using the platform default encoding, which raised `UnicodeEncodeError` on Windows when generated docs contained non-ASCII characters | Fixed by forcing UTF-8 temp-file writes. Verified with `python .github/scripts/openwrt-docs4ai-08-validate.py --warn-only`. |
| REMOTE-001 | fixed-and-verified | initialize | `01-clone-repos.py` referenced `datetime` without importing it, causing the first remote `initialize` job to fail | Fixed in commit `75892ee`. Verified by the next run progressing past `initialize`. |
| REMOTE-002 | fixed-and-verified | extract-wiki | `02a-scrape-wiki.py` had a broken `load_cache()` block that raised `IndentationError` remotely | Fixed in commit `ed9b9be`. Verified by the next run completing the full extract matrix. |
| REMOTE-003 | fixed-and-verified | validation | `08-validate.py` over-matched relative `.md` links across adjacent markdown links and prose, creating 14 false blocking failures | Fixed in commit `f6a16f2`. Verified by successful remote run `22864304564`. |
| REMOTE-004 | fixed-pending-test | validation-warnings | Successful remote validation emitted 143 soft AST warnings because AST checks were running across duplicated L1, L2, and monolithic outputs | Scoped AST checks to canonical L2 docs only, which reduced the local warning count to 48. Pending remote confirmation. |
| CONTENT-001 | open | wiki-conversion | Some wiki-derived outputs still retain DokuWiki or pandoc artifacts such as `<WRAP>` markers, duplicated top headings, and raw HTML table fragments | Observed during the 2026-03-09 random output slice audit. L1 raw retention is intentional; the open question is how much additional cleanup should be applied to L2. |

## Verification Notes

- Update this file when a bug is reproduced, fixed, or explicitly not reproduced.
- When a bug is fixed, note the validation command or smoke test that proved it.