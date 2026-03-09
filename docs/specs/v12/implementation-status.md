# v12 Implementation Status

## Current State

v12 now has fresh local and remote verification from the 2026-03-09 stabilization pass, but it is still in a final hardening phase rather than declared fully finished.

The current authoritative position is:

- code exists for the numbered pipeline stages
- documentation and test surfaces were realigned with the current script layout on 2026-03-09
- local smoke, sequential local verification, and cache-backed AI verification paths are passing
- GitHub Actions behavior is verified through run `22870498903`, including `initialize`, all `extract` jobs, `process`, and `deploy`
- the latest fully verified remote run completed with `0` hard failures and `1` soft warning
- L1 and L2 are intentionally retained under `openwrt-condensed-docs`; only L0 remains transient
- remaining risk is concentrated in one residual dockerman ucode soft warning and wiki-conversion cleanliness, not in broad pipeline instability

## Verification Matrix

| Area | Status | Notes |
| --- | --- | --- |
| Script implementation surface | present | `.github/scripts/` contains the numbered v12 pipeline family |
| Active spec structure | complete | Active specs moved to `docs/specs/v12/` on 2026-03-09 |
| Archive separation | complete | Historical planning and bug notes moved to `docs/archive/v12/` |
| Root documentation accuracy | complete | Root docs now point to the current architecture, specs, and local smoke paths |
| Deterministic local smoke test | verified | `python tests/00-smoke-test.py` passes locally |
| Sequential local smoke runner | verified | `python tests/openwrt-docs4ai-00-smoke-test.py` passes locally |
| Local AI-summary integration | verified | Cache-backed local AI path passes via `--run-ai` without requiring a live token |
| GitHub Actions remote verification | verified | Latest fully checked run `22870498903` passed end to end on 2026-03-09 |
| Remote output measurement | verified | Successful staging artifact contained 151 L1 markdown docs, 151 L2 markdown docs, and 397 indexed symbols |
| Generated output promotion | verified | Deploy produced commit `3d3e6d3` (`docs: v12 auto-update 2026-03-09`) |
| L1/L2 retention policy | decided | L1 and L2 remain committed under `openwrt-condensed-docs`; L0 remains transient only |
| Remote warning reduction | verified | Remote soft warnings were reduced from 48 to 1 across the 2026-03-09 hardening passes |
| Latest local follow-up patch | verified | Remote run `22870498903` cleared the `nl80211` warning and left only one residual dockerman soft warning |

## Historical Note

Older status claims from early March 2026 described the pipeline as fully complete and production-ready. Those claims are preserved as historical context only and are not the active engineering position unless supported by fresh local or remote verification.

## 2026-03-09 Milestone Log

### Milestone 1: Documentation and authority reset

- Created `docs/ARCHITECTURE.md` as the durable repository architecture reference.
- Split active v12 specifications into `docs/specs/v12/`.
- Moved historical planning and bug-review material into `docs/archive/v12/`.
- Removed `CONTRIBUTING.md` and consolidated maintainer guidance into `DEVELOPMENT.md`.
- Added an active stabilization plan and an active bug log under `docs/specs/v12/`.

### Milestone 2: Local smoke repair and runtime hardening

- Rewrote `tests/00-smoke-test.py` into a deterministic fixture-backed regression harness for the current L1 to L5 contract.
- Rewrote `tests/openwrt-docs4ai-00-smoke-test.py` into a sequential local runner with fixture-backed default mode and optional extractor mode.
- Repaired runtime issues in `03`, `04`, `05`, `06b`, and `06c` that were surfaced by the local smoke path.
- Verified local AI enrichment in cache-backed mode without external model calls.

### Milestone 3: Remote GitHub Actions verification

- Fixed a missing `datetime` import in `01-clone-repos.py` that blocked the `initialize` job in the first remote run.
- Restored the broken `load_cache()` function in `02a-scrape-wiki.py`, allowing the full extract matrix to complete remotely.
- Tightened relative markdown link validation in `08-validate.py` so it no longer over-matches across adjacent links and prose.
- Verified successful run `22864304564`, which completed `initialize`, all extractor jobs, `process`, and `deploy`.
- Confirmed that the deploy stage promoted generated outputs into `openwrt-condensed-docs/` via commit `3d3e6d3`.

### Milestone 4: ucode warning hardening

- Introduced real CI-backed `ucode` validation and treated the resulting warning spike as a truthfulness problem to investigate, not something to suppress.
- Fixed false positives caused by missing ucode module context, naive unlabeled fence relabeling, and regex-only parsing of indented fenced blocks.
- Reclassified non-runnable pseudocode and bare response-shape examples so prose and structural examples are no longer misvalidated as executable ucode.
- Added targeted cleanup for clearly invalid upstream examples that leaked into generated docs.
- Verified warning reduction across remote runs from `67` to `10`, then `4`, then `2`, then `1` while keeping hard failures at `0`.

### Milestone 5: final warning verification

- Pushed the follow-up hardening commit `ba60a8e` (`fix: harden final ucode warning handling`).
- Verified remote run `22870498903`, which completed successfully with `0` hard failures and `1` soft warning.
- Confirmed that the `nl80211` example rewrite resolved the last `ucode` module-documentation parser warning.
- Investigated the remaining `docker_rpc.uc` warning and found that the file is consumed by LuCI as multiple rpc objects such as `docker`, `docker.container`, `docker.image`, and `docker.network`, which supports the intentional direct `return methods;` shape.
- Current evidence indicates that the remaining warning is a standalone `ucode` validation mismatch for a dual-mode rpcd script, not a broad documentation quality failure.

## Remote Output Snapshot

Measured from the `final-staging` artifact produced by run `22864304564`.

| Layer | Markdown docs | Metadata files | Total bytes | Notes |
| --- | --- | --- | --- | --- |
| L1 | 151 | 151 | 1,799,704 | Largest module by document count is `wiki` with 90 docs |
| L2 | 151 | 0 | 1,796,690 | Mirrors L1 document count after normalization |
| Registry | 397 symbols | n/a | n/a | Count taken from `cross-link-registry.json` |

## Sample Output Audit

A random slice audit of 10 generated files on 2026-03-09 found that the outputs broadly match the active layer contracts:

- L1 samples were raw converted source documents without YAML frontmatter and with source-style structure intact.
- L2 samples carried the required YAML frontmatter and preserved relative links into the generated corpus.
- The primary remaining content issue is cleanliness in some wiki-derived pages, where legacy DokuWiki or pandoc artifacts still appear (for example `<WRAP>` markers, duplicated top headings, and raw HTML table fragments).

### Next Priority

Decide whether the remaining dockerman soft warning is worth any further validator modeling, or leave it as one truthful non-blocking warning and shift attention to wiki-conversion cleanup.

