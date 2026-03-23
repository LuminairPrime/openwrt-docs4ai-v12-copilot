# V13 Working Checklist

**Created:** 2026-03-23  
**Purpose:** Durable implementation tracker for V13 phases. Re-read at the start of every phase. Mark `[x]` as items are completed.

---

## Assumptions and Non-Blocking Uncertainties

These were recorded at Phase 0 to avoid blocking on minor ambiguities. Revisit if evidence contradicts them.

| # | Assumption | Basis |
|---|-----------|-------|
| A1 | `source_url` for git-backed sources: `https://github.com/{org}/{repo}/blob/{commit}/{upstream_path}`. Repo bases: openwrt=`https://github.com/openwrt/openwrt`, luci=`https://github.com/openwrt/luci`, ucode=`https://github.com/nicowillis/ucode` (verify exact org in lib/source_provenance.py). | Plan says "dereferenceable upstream URL" |
| A2 | `source_commit` is omitted for `wiki_page` origin_type — wiki is scraped, not git-backed. The git-backed set: `js_source`, `c_source`, `makefile_meta`, `procd_api`, `uci_schema`, `hotplug_events`, `luci_example`, `uci_default`. | Phase 3 says "only when origin_type is in a git-backed set" |
| A3 | `REPO_BASE_URLS` removal from 03 is N/A — `03` never had such a table. URL construction moves to `lib/source_provenance.py` called from `02*` scripts. | Reading `03` source code directly |
| A4 | Stale field rejection in 08 validator will be soft warnings (not hard failures) to accommodate existing cached L2 files in the working directory. New output must not emit stale fields. | Plan says "warnings or failures" — soft is safer |
| A5 | The existing dead-link checker in `08` (lines 1011–1021) runs on `all_md` which includes L1/L2 files. Phase 9 will scope it to release-tree only. The existing regex and logic is otherwise correct. | Direct code review |
| A6 | Per-module AGENTS.md files ship as static overlay files via `release-inputs/release-include/{module}/AGENTS.md`. Stage 07 copies them. This matches the current overlay copy mechanism. | 02-v13 §S4, CLAUDE.md overlay description |
| A7 | `source_url` is not in the required L2 fields list for 08 validator (it's optional — present when available). Only `source_commit` has conditional-required behavior. | Phase 3 task 5 explicit required list |
| A8 | wiki `original_url` field → renamed to `source_url` in the L1 sidecar (it already contains the full wiki page URL, just needs renaming). | L1 sidecar inspection: `original_url: "https://openwrt.org/..."` |
| A9 | `source_locator` is retained as an optional field in the L1 sidecar for debugging (keeps `upstream_path` value under a new key name). Not required by validator. | 02-v13 glossary definition of `source_locator` |
| A10 | The dead-link checker in Phase 9 will be scoped to release-tree `.md` files only. The current `all_md` walker covers all of outdir including intermediate layers, which causes false positives on L2 cross-links. | Phase 9 guard rail: "checker runs on the release-tree, not L1 or L2" |

---

## Phase 0: Lock the Live Plan State

- [x] Read 00-v13 in full
- [x] Read 02-v13 in full  
- [x] Read 03-v13 in full
- [x] Read 04-v13 in full
- [x] Extract active requirements — see sections below
- [x] Record non-blocking assumptions above
- [x] Save checklist to `docs/plans/v13/working-checklist.md`

---

## Phase 1: Establish Baseline

- [x] Read `.github/workflows/openwrt-docs4ai-00-pipeline.yml` — stage ordering, parallelism, env vars
- [x] Read `08-validate-output.py` — gatekeeper contract
- [x] Read `tests/pytest/pytest_09_release_tree_contract_test.py` — current test assertions
- [x] Run `python tests/run_pytest.py` — confirm baseline test state → **80/80 pass**
- [x] Document pre-existing failures or warnings → **none**

---

## Phase 2: Build docs-new Scaffold

- [x] Create `docs/docs-new/output/` directory
- [x] Create `docs/docs-new/pipeline/` directory
- [x] Create `docs/docs-new/project/` directory
- [x] Create `docs/docs-new/plans/v13/` directory (copy, not symlink)
- [x] Create `docs/docs-new/roadmap/` directory
- [x] Author `docs/docs-new/output/release-tree-contract.md` (V6 label, routing ownership records, V13 additions)
- [x] Author `docs/docs-new/pipeline/pipeline-stage-catalog.md` (every script including 02i)
- [x] Author `docs/docs-new/pipeline/regeneration-rules.md` (trigger rules, overlay behavior)
- [x] Author `docs/docs-new/project/glossary-and-naming-contract.md` (S7 all terms)
- [x] Author `docs/docs-new/roadmap/deferred-features.md` (A2 deferral with exact hit data, C-tier items)
- [x] Copy `docs/plans/v13/` → `docs/docs-new/plans/v13/` (no symlinks; 12 files)
- [x] Verify no symlinks in docs-new
- [x] Verify no broken internal links between docs-new files

---

## Phase 3: Metadata Provenance Hardening

- [x] Create `lib/source_provenance.py` with helpers: `make_wiki_source_url()`, `make_git_source_url()`, `normalize_provenance()`
- [x] Update `02a-scrape-wiki.py`: rename `original_url` → `source_url` in L1 meta
- [x] Verify `02a` produces correct L1 sidecars with `source_url` (manual check or targeted test)
- [x] Update `02b-scrape-ucode.py`: add `source_url` + `source_commit`, rename/keep `upstream_path` as `source_locator`
- [x] Update `02c-scrape-jsdoc.py`: same pattern as 02b
- [x] Update `02d-scrape-core-packages.py`: same pattern
- [x] Update `02e-scrape-example-packages.py`: same pattern
- [x] Update `02f-scrape-procd-api.py`: same pattern
- [x] Update `02g-scrape-uci-schemas.py`: same pattern
- [x] Update `02h-scrape-hotplug-events.py`: same pattern
- [x] Update `03-normalize-semantic.py`: carry `source_url` and `source_commit` from L1 sidecars → L2 frontmatter; use `source_commit` instead of `version`; carry optional routing fields
- [x] Update `08-validate-output.py`: required fields list; conditional `source_commit` for git-backed; soft-warn stale fields `version`/`upstream_path`/`original_url`
- [x] Update `tests/pytest/pytest_09_release_tree_contract_test.py`: fixtures use `source_commit` not `version`
- [x] Run `python tests/run_pytest.py` — all tests pass after migration

---

## Phase 4: Create Live Cookbook Fixtures

- [x] Create `content/cookbook-source/` directory
- [x] Author `content/cookbook-source/openwrt-era-guide.md` (skeletal, all required frontmatter, all section headings)
- [x] Author `content/cookbook-source/common-ai-mistakes.md` (skeletal)
- [x] Author `content/cookbook-source/architecture-overview.md` (skeletal)
- [x] Verify frontmatter completeness: title, description, module, origin_type, when_to_use, related_modules, era_status, verification_basis, reviewed_by, last_reviewed
- [x] Verify NO `topic_slug` in frontmatter
- [x] Verify cross-links use `../../module/chunked-reference/` pattern

---

## Phase 5: Implement 02i Cookbook Ingest

- [x] Create `.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py`
- [x] Implement: read all `.md` from `content/cookbook-source/`; fail fast on missing frontmatter; derive `topic_slug` from filename; copy body to `L1-raw/cookbook/`; write `.meta.json` sidecar; print count
- [x] Add script docstring (Purpose, Phase, Layers, Inputs, Outputs, Dependencies)
- [x] Update `docs/docs-new/pipeline/pipeline-stage-catalog.md` to include `02i`
- [x] Run `02i` against the three fixture files — confirm 3 `.md` + 3 `.meta.json` in L1-raw/cookbook/
- [x] Confirm `topic_slug` matches filename
- [x] Confirm fail-fast when frontmatter removed
- [x] Syntax check: `python -c "import py_compile; py_compile.compile('.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py', doraise=True)"`

---

## Phase 6: Wire Cookbook Through Pipeline

- [x] Update `03-normalize-semantic.py`: carry cookbook authored fields into L2; do NOT synthesize `source_commit` for cookbook
- [x] Update `05a-assemble-references.py`: recognize cookbook L2; produce `map.md`, `bundled-reference.md`, `chunked-reference/` — no change needed (iterates all L2 dirs dynamically)
- [x] Update `06-generate-llm-routing-indexes.py`: add `"cookbook": "Guides"` to `MODULE_CATEGORIES`; add `"Guides"` first in `CATEGORY_ORDER`; add cookbook to `MODULE_DESCRIPTIONS`
- [x] Update pipeline workflow (`.github/workflows/`) to include `02i` in collector group (`extract_cookbook` job)
- [x] Add `02i` to `FULL_PIPELINE` in `tests/support/smoke_pipeline_support.py`
- [x] Run `python tests/run_pytest.py` — 80/80 passing

---

## Phase 7: Per-Module AGENTS.md and Root AGENTS.md

- [x] Create `release-inputs/release-include/luci/AGENTS.md` (era warning, JS API pointers)
- [x] Create `release-inputs/release-include/ucode/AGENTS.md` (not-JavaScript warning, stdlib pointers)
- [x] Create `release-inputs/release-include/cookbook/AGENTS.md` (task guide scope note, era guide pointer)
- [x] Update root AGENTS.md template in `05b`: add era awareness section, per-module AGENTS.md discovery notice
- [x] Verify overlay copy order: `07` runs after `05b` so static per-module files are not overwritten
- [x] Run `python tests/run_pytest.py` — 80/80 passing

---

## Phase 8: Fix Root Routing

- [x] Add `MODULE_DESCRIPTIONS` dict to `06-generate-llm-routing-indexes.py` with 9-module descriptions — done in Phase 6
- [x] Update `06` to prefer `MODULE_DESCRIPTIONS` over heuristic for module-level summary — done in Phase 6
- [x] Update `release-inputs/release-include/README.md` with module table using S1 curated text (expanded to ~60 lines)
- [ ] Verify root `llms.txt` no longer says "CBI declarative form framework" for luci — requires pipeline run
- [ ] Verify root `llms.txt` no longer references "21.02 release" for wiki — requires pipeline run

---

## Phase 9: Install Validation Safety Nets ✅

- [x] Scope dead-link checker in `08` to release-tree .md files only (not all_md which includes L1/L2)
- [x] Verify dead-link checker handles: anchor stripping (`file.md#section`→`file.md`), image links ignored, external links excluded
- [x] Add tests for: dead-link detection with broken fixture (4 new tests added), exclusion behavior tested
- [x] Run full test suite: `python tests/run_pytest.py` — **84/84 ✅** (was 80)

---

## Phase 10: Implement A8 Source Exclusions

- [x] Create `config/source-exclusions.yml` with 3 first-pass entries (`guide-developer-luci`, `techref-hotplug-legacy`, `guide-developer-20-xx-major-changes`)
- [x] Create `lib/source_exclusions.py` with `should_exclude(source_type, identifier)` function
- [x] Update `02a-scrape-wiki.py` to call `should_exclude()` before writing L1 output
- [x] Add exclusion reporting in `08-validate-output.py` (informational, not failure gate)
- [x] Add test verifying exclusion behavior
- [x] Verify excluded sources don't reach L1

---

## Phase 11: A5 Routing Metadata and A6 Provenance

**A5 — Routing Metadata:**
- [x] Update `03-normalize-semantic.py` to carry through: `routing_summary`, `routing_keywords`, `routing_priority`, `era_status`, `audience_hint` from L1 sidecars (if present)
- [x] Update `06` to use `routing_summary` → `description` → heuristic fallback for per-document descriptions
- [x] Update `05a` to use `routing_summary` / `description` in `map.md`

**A6 — Visible Provenance Headers:**
- [x] Update `05a-assemble-references.py`: inject provenance blockquote in `chunked-reference/` and `bundled-reference.md` from L2 frontmatter
- [x] Provenance format: `> **Source:** [url](url)` (omit if absent), `> **Kind:** origin_type`, `> **Commit:** sha` (omit if absent), `> **Normalized:** YYYY-MM-DD` (from `last_pipeline_run` or run date, omit if none)
- [x] Verify L2 files do NOT contain visible provenance block
- [x] Verify no fabricated URLs in provenance headers

---

## Phase 12: A1 LuCI Type Definitions (may be fresh session)

- [x] Read `docs/plans/v13/working-checklist.md` and 04-v13 §A1 at session start
- [x] Examine 2–3 representative `luci/chunked-reference/js_source-api-*.md` files for stable structure
- [x] Choose: extend `05c` or create `05e-generate-luci-dts.py` — created `05e-generate-luci-dts.py` (Approach 2: JS source)
- [x] If feasible: implement `luci-env.d.ts` for form, rpc, uci, view, dom, request, network — **DONE** (477 lines, all 7 namespaces)
- [x] Run `tsc --noEmit` on generated `.d.ts` — exit code 0 ✅, 120/120 tests
- [x] If infeasible: defer with rationale — N/A (was feasible)

---

## Phase 13: Expand Cookbook Content (may be fresh session)

- [x] Read `docs/plans/v13/working-checklist.md` and 03-v13 at session start
- [x] Author `openwrt-era-guide.md` full content (era table, legacy markers, version target, LuCI JS vs Lua section, when-legacy-ok, 3 working examples, 3 anti-pattern pairs) — 275 lines
- [x] Author `common-ai-mistakes.md` full content (7 mistake categories matching spec: era confusion, language, network stack, filesystem, package manager, init system, build system) — 332 lines
- [x] Author `architecture-overview.md` full content (component diagram, build-time vs runtime table, ACL details, data flow, working example) — 324 lines
- [x] Run each through pipeline (`02i` + `03`): all 3 ingested to L2-semantic/cookbook/ — verified 120/120 tests pass
- [x] A-tier topics: procd-service-lifecycle.md (~80 lines), minimal-openwrt-package-makefile.md (~130 lines), uci-read-write-from-ucode.md (~130 lines), luci-form-with-uci.md (~180 lines) — all 7 cookbook files verified through pipeline, 120/120 tests pass
- [ ] If era-guide needs external evidence not available in session: create `era-guide-evidence-needed.md`

---

## Final Success Conditions Checklist

- [x] `docs/docs-new/` exists and is populated per 02-v13 §S6 — Phase 2 done
- [x] L2 uses `source_url` / `source_commit`; stale fields rejected by `08` — Phase 3 done
- [x] `lib/source_provenance.py` exists and used by all `02*` ingest scripts — Phase 3 done
- [x] Cookbook flows correctly through `02i` → L1 → L2 → assembled output — verified Phase 13
- [x] `origin_type: "authored"` used for cookbook (confirmed from 02-v13 §S4 line 561) — Phase 5/6 done
- [ ] Root `llms.txt` descriptions fixed via `MODULE_DESCRIPTIONS` — requires full pipeline run to verify output
- [x] Per-module `AGENTS.md` files exist for `luci`, `ucode`, and `cookbook` — Phase 7 done
- [x] Stage `08` catches internal dead links in the release-tree — Phase 9 done
- [x] A8 implemented with 3 approved first-pass wiki exclusions — Phase 10 done
- [x] A2 remains deferred; no extra `llms-xyz` routing file created — confirmed
- [x] A5 routing metadata and A6 visible provenance match 04-v13 design — Phase 11 done
- [x] Visible provenance injected at stage `05a`, not `03` — Phase 11 done
- [x] Cookbook content authored only after pipeline + safety rails proven — done
- [x] At least 3 S-tier cookbook topics pass content contract — 3/3 done Phase 13
- [x] All tests pass: `python tests/run_pytest.py` — 120/120 ✅
- [ ] Stage `08` validation passes on full release-tree — requires full CI pipeline run
- [x] No symlinks in `docs/docs-new/` — Phase 2 confirmed
