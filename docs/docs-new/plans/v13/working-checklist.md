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

- [ ] Read `.github/workflows/openwrt-docs4ai-00-pipeline.yml` — stage ordering, parallelism, env vars
- [ ] Read `08-validate-output.py` — gatekeeper contract
- [ ] Read `tests/pytest/pytest_09_release_tree_contract_test.py` — current test assertions
- [ ] Run `python tests/run_pytest.py` — confirm baseline test state
- [ ] Document pre-existing failures or warnings

---

## Phase 2: Build docs-new Scaffold

- [ ] Create `docs/docs-new/output/` directory
- [ ] Create `docs/docs-new/pipeline/` directory
- [ ] Create `docs/docs-new/project/` directory
- [ ] Create `docs/docs-new/plans/v13/` directory (copy, not symlink)
- [ ] Create `docs/docs-new/roadmap/` directory
- [ ] Author `docs/docs-new/output/release-tree-contract.md` (migrate from v12, V6 label, add routing ownership records, add v13 additions)
- [ ] Author `docs/docs-new/pipeline/pipeline-stage-catalog.md` (every script including 02i)
- [ ] Author `docs/docs-new/pipeline/regeneration-rules.md` (trigger rules, overlay behavior)
- [ ] Author `docs/docs-new/project/glossary-and-naming-contract.md` (S7 all terms)
- [ ] Author `docs/docs-new/roadmap/deferred-features.md` (A2 deferral, C-tier items)
- [ ] Copy `docs/plans/v13/` → `docs/docs-new/plans/v13/` (no symlinks)
- [ ] Verify no symlinks in docs-new
- [ ] Verify no broken internal links between docs-new files

---

## Phase 3: Metadata Provenance Hardening

- [ ] Create `lib/source_provenance.py` with helpers: `make_wiki_source_url()`, `make_git_source_url()`, `normalize_provenance()`
- [ ] Update `02a-scrape-wiki.py`: rename `original_url` → `source_url` in L1 meta
- [ ] Verify `02a` produces correct L1 sidecars with `source_url` (manual check or targeted test)
- [ ] Update `02b-scrape-ucode.py`: add `source_url` + `source_commit`, rename/keep `upstream_path` as `source_locator`
- [ ] Update `02c-scrape-jsdoc.py`: same pattern as 02b
- [ ] Update `02d-scrape-core-packages.py`: same pattern
- [ ] Update `02e-scrape-example-packages.py`: same pattern
- [ ] Update `02f-scrape-procd-api.py`: same pattern
- [ ] Update `02g-scrape-uci-schemas.py`: same pattern
- [ ] Update `02h-scrape-hotplug-events.py`: same pattern
- [ ] Update `03-normalize-semantic.py`: carry `source_url` and `source_commit` from L1 sidecars → L2 frontmatter; use `source_commit` instead of `version`; carry optional routing fields
- [ ] Update `08-validate-output.py`: required fields list; conditional `source_commit` for git-backed; soft-warn stale fields `version`/`upstream_path`/`original_url`
- [ ] Update `tests/pytest/pytest_09_release_tree_contract_test.py`: fixtures use `source_commit` not `version`
- [ ] Run `python tests/run_pytest.py` — all tests pass after migration

---

## Phase 4: Create Live Cookbook Fixtures

- [ ] Create `content/cookbook-source/` directory
- [ ] Author `content/cookbook-source/openwrt-era-guide.md` (skeletal, all required frontmatter, all section headings)
- [ ] Author `content/cookbook-source/common-ai-mistakes.md` (skeletal)
- [ ] Author `content/cookbook-source/architecture-overview.md` (skeletal)
- [ ] Verify frontmatter completeness: title, description, module, origin_type, when_to_use, related_modules, era_status, verification_basis, reviewed_by, last_reviewed
- [ ] Verify NO `topic_slug` in frontmatter
- [ ] Verify cross-links use `../../module/chunked-reference/` pattern

---

## Phase 5: Implement 02i Cookbook Ingest

- [ ] Create `.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py`
- [ ] Implement: read all `.md` from `content/cookbook-source/`; fail fast on missing frontmatter; derive `topic_slug` from filename; copy body to `L1-raw/cookbook/`; write `.meta.json` sidecar; print count
- [ ] Add script docstring (Purpose, Phase, Layers, Inputs, Outputs, Dependencies)
- [ ] Update `docs/docs-new/pipeline/pipeline-stage-catalog.md` to include `02i`
- [ ] Run `02i` against the three fixture files — confirm 3 `.md` + 3 `.meta.json` in L1-raw/cookbook/
- [ ] Confirm `topic_slug` matches filename
- [ ] Confirm fail-fast when frontmatter removed
- [ ] Syntax check: `python -c "import py_compile; py_compile.compile('.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py', doraise=True)"`

---

## Phase 6: Wire Cookbook Through Pipeline

- [ ] Update `03-normalize-semantic.py`: carry cookbook authored fields into L2; do NOT synthesize `source_commit` for cookbook
- [ ] Update `05a-assemble-references.py`: recognize cookbook L2; produce `map.md`, `bundled-reference.md`, `chunked-reference/`
- [ ] Update `06-generate-llm-routing-indexes.py`: add `"cookbook": "Guides"` to `MODULE_CATEGORIES`; add `"Guides"` first in `CATEGORY_ORDER`; add cookbook to `MODULE_DESCRIPTIONS`
- [ ] Update pipeline workflow (`.github/workflows/`) to include `02i` in collector group
- [ ] Verify cookbook appears in release-tree and root `llms.txt` under "Guides"
- [ ] Verify existing modules unaffected
- [ ] Run `python tests/run_pytest.py`

---

## Phase 7: Per-Module AGENTS.md and Root AGENTS.md

- [ ] Create `release-inputs/release-include/luci/AGENTS.md` (era warning, JS API pointers)
- [ ] Create `release-inputs/release-include/ucode/AGENTS.md` (not-JavaScript warning, stdlib pointers)
- [ ] Create `release-inputs/release-include/cookbook/AGENTS.md` (task guide scope note, era guide pointer)
- [ ] Update root AGENTS.md template in `05b`: add era awareness section, per-module AGENTS.md discovery notice
- [ ] Verify overlay copy order: `07` runs after `05b` so static per-module files are not overwritten

---

## Phase 8: Fix Root Routing

- [ ] Add `MODULE_DESCRIPTIONS` dict to `06-generate-llm-routing-indexes.py` with 8-module descriptions
- [ ] Update `06` to prefer `MODULE_DESCRIPTIONS` over heuristic for module-level summary
- [ ] Update `release-inputs/release-include/README.md` with module table using S1 curated text
- [ ] Verify root `llms.txt` no longer says "CBI declarative form framework" for luci
- [ ] Verify root `llms.txt` no longer references "21.02 release" for wiki

---

## Phase 9: Install Validation Safety Nets

- [ ] Scope dead-link checker in `08` to release-tree .md files only (not all_md which includes L1/L2)
- [ ] Verify dead-link checker handles: anchor stripping (`file.md#section`→`file.md`), image links ignored, external links excluded
- [ ] Add tests for: cookbook fixture flow, routing metadata precedence, dead-link detection with broken fixture, exclusion behavior
- [ ] Run full test suite: `python tests/run_pytest.py`

---

## Phase 10: Implement A8 Source Exclusions

- [ ] Create `config/source-exclusions.yml` with 3 first-pass entries (`guide-developer-luci`, `techref-hotplug-legacy`, `guide-developer-20-xx-major-changes`)
- [ ] Create `lib/source_exclusions.py` with `should_exclude(source_type, identifier)` function
- [ ] Update `02a-scrape-wiki.py` to call `should_exclude()` before writing L1 output
- [ ] Add exclusion reporting in `08-validate-output.py` (informational, not failure gate)
- [ ] Add test verifying exclusion behavior
- [ ] Verify excluded sources don't reach L1

---

## Phase 11: A5 Routing Metadata and A6 Provenance

**A5 — Routing Metadata:**
- [ ] Update `03-normalize-semantic.py` to carry through: `routing_summary`, `routing_keywords`, `routing_priority`, `era_status`, `audience_hint` from L1 sidecars (if present)
- [ ] Update `06` to use `routing_summary` → `description` → heuristic fallback for per-document descriptions
- [ ] Update `05a` to use `routing_summary` / `description` in `map.md`

**A6 — Visible Provenance Headers:**
- [ ] Update `05a-assemble-references.py`: inject provenance blockquote in `chunked-reference/` and `bundled-reference.md` from L2 frontmatter
- [ ] Provenance format: `> **Source:** [url](url)` (omit if absent), `> **Kind:** origin_type`, `> **Commit:** sha` (omit if absent), `> **Normalized:** YYYY-MM-DD` (from `last_pipeline_run` or run date, omit if none)
- [ ] Verify L2 files do NOT contain visible provenance block
- [ ] Verify no fabricated URLs in provenance headers

---

## Phase 12: A1 LuCI Type Definitions (may be fresh session)

- [ ] Read `docs/plans/v13/working-checklist.md` and 04-v13 §A1 at session start
- [ ] Examine 2–3 representative `luci/chunked-reference/js_source-api-*.md` files for stable structure
- [ ] Choose: extend `05c` or create `05e-generate-luci-dts.py`
- [ ] If feasible: implement `luci-env.d.ts` for form, rpc, uci, view, dom, request, network
- [ ] Run `tsc --noEmit` on generated `.d.ts`
- [ ] If infeasible: defer with rationale in `docs/docs-new/roadmap/deferred-features.md`

---

## Phase 13: Expand Cookbook Content (may be fresh session)

- [ ] Read `docs/plans/v13/working-checklist.md` and 03-v13 at session start
- [ ] Author `openwrt-era-guide.md` full content (era table, legacy markers, version target, research evidence)
- [ ] Author `common-ai-mistakes.md` full content (7+ mistake categories, WRONG/CORRECT pairs)
- [ ] Author `architecture-overview.md` full content (component diagram, data flow)
- [ ] Run each through pipeline; verify 08 validation passes
- [ ] A-tier topics (if time): procd-service-lifecycle.md, minimal-openwrt-package-makefile.md, uci-read-write-from-ucode.md, luci-form-with-uci.md
- [ ] If era-guide needs external evidence not available in session: create `era-guide-evidence-needed.md`

---

## Final Success Conditions Checklist

- [ ] `docs/docs-new/` exists and is populated per 02-v13 §S6
- [ ] L2 uses `source_url` / `source_commit`; stale fields rejected by `08`
- [ ] `lib/source_provenance.py` exists and used by all `02*` ingest scripts
- [ ] Cookbook flows correctly through `02i` → L1 → L2 → assembled output
- [ ] `origin_type: authored` used for cookbook (not `cookbook`)
- [ ] Root `llms.txt` descriptions fixed via `MODULE_DESCRIPTIONS`
- [ ] Per-module `AGENTS.md` files exist for `luci`, `ucode`, and `cookbook`
- [ ] Stage `08` catches internal dead links in the release-tree
- [ ] A8 implemented with 3 approved first-pass wiki exclusions
- [ ] A2 remains deferred; no extra `llms-xyz` routing file created
- [ ] A5 routing metadata and A6 visible provenance match 04-v13 design
- [ ] Visible provenance injected at stage `05a`, not `03`
- [ ] Cookbook content authored only after pipeline + safety rails proven
- [ ] At least 3 S-tier cookbook topics pass content contract
- [ ] All tests pass: `python tests/run_pytest.py`
- [ ] Stage `08` validation passes on full release-tree
- [ ] No symlinks in `docs/docs-new/`
