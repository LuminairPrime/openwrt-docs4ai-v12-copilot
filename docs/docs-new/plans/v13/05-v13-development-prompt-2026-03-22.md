# V13 Development Prompt

You are implementing the v13 upgrade for this repository. Work from the current live versions of these files and follow them as the source of truth:

- `docs/plans/v13/00-v13-ideas-tier-list-2026-03-22.md`
- `docs/plans/v13/02-v13-implementation-spec-s-tier-2026-03-22.md`
- `docs/plans/v13/03-v13-cookbook-content-spec-2026-03-22.md`
- `docs/plans/v13/04-v13-a-tier-implementation-spec-2026-03-22.md`

Implement continuously, but do the work in the phase order below. Do not skip ahead unless an earlier phase is already complete and verified.

If you are approaching your context limit or token budget before completing all phases, gracefully conclude the session at the end of the current phase. Explicitly state which phases are complete, which phase you stopped at, and that remaining phases must be executed in a fresh session. Phases 0–11 are the core infrastructure — complete those first. Phases 12 and 13 may safely run in a follow-up session.

---

## GLOBAL RULES

1. Re-read any file before editing it if it may have changed during the session.
2. Prefer small, coherent edits with validation after each phase.
3. Fix root causes, not symptoms.
4. Prefer deterministic pipeline behavior over clever heuristics.
5. Do not invent new v13 scope beyond what 00/02/03/04 already define, except for small enabling changes required to complete an existing item cleanly.
6. Keep docs contracts and implementation synchronized. If pipeline behavior changes, update the corresponding v13 docs or docs-new contract files.
7. Use skeletal authored cookbook files as live pipeline fixtures before writing heavy content.
8. Validate early and often. Do not batch many speculative changes before checking them.
9. Do not fabricate summaries, provenance, URLs, metadata, or source claims.
10. When a plan file specifies an exact field name, file path, or stage assignment, use that exact specification. If you believe the plan is wrong, note the divergence and ask — do not silently deviate.

---

## HARD GUARD RAILS

### A2 indefinite deferral
- Do not implement `llms-mini.txt`, `llms-small.txt`, or any new `llms-xyz` routing file.
- Do preserve the A2 decision record and deferred-features note.
- The routing standard remains `llms.txt` and `llms-full.txt` only.

### A8 exclusion scope
- First-pass exclusions must be path-specific, not pattern-based module suppression.
- Seed the first policy entries with exactly these reviewed wiki pages:
  - `guide-developer-luci`
  - `techref-hotplug-legacy`
  - `guide-developer-20-xx-major-changes`
- Do not add broad exclusion globs unless clearly required and justified by the plans.

### A7 dead-link scope
- Dead-link checking is limited to internal relative links in shipped release-tree output.
- Do not add external URL reachability checks.

### A6 provenance layer assignment
- Visible provenance headers are injected by stage `05a` during assembly of published output.
- L2 files must NOT contain the visible provenance block. L2 is pure data (markdown body + YAML frontmatter).
- Do not inject presentation concerns into stage `03`.

### Cookbook content boundary
- Cookbook pages are task guides, not duplicate reference manuals.
- Link to reference docs instead of copying large API sections.
- Cross-links must target eventual `release-tree/` paths, not source directories.

### Metadata contract
- Cookbook `origin_type` is `authored`, not `cookbook`. This decouples provenance from destination.
- `topic_slug` is derived by `02i` from the filename. It is NOT authored in frontmatter.
- `source_commit` is required only for git-backed `origin_type` values. `origin_type: authored` is exempt.
- The authored `description` field and the pipeline `routing_summary` field serve the same purpose. Stage 06/05a must check `routing_summary` first, then fall back to `description`.
- Stale field names (`version`, `upstream_path`, `original_url`) must be rejected by the validator after migration.

### Stage 05d
- `05d` is already occupied in the live pipeline. Do not repurpose it. If A1 needs a new sibling stage, use `05e`.

---

## CONFLICT RESOLUTION

If you find a contradiction between plan files, resolve it with this priority:
1. **Live code behavior** — if the code does something the plan doesn't account for, note it and ask
2. **Later plan files override earlier ones** — 04 > 03 > 02 > 00 on the same topic
3. **Acceptance tests** — if a plan's prose conflicts with its own acceptance test, the acceptance test wins

If you find a contradiction between a plan file and this prompt, this prompt wins on guard rails and phase ordering. The plan files win on implementation details.

---

## WORKING METHOD

At the end of each phase:
1. Verify the affected behavior with the smallest relevant proof first.
2. Fix failures before moving on.
3. Report what changed, what was verified, and whether the next phase is safe.

Preferred verification order:
1. Targeted fixture or unit test
2. Focused pytest run
3. Affected stage rerun with stub inputs
4. Stage 08 validation
5. Broader pipeline proof only when needed

If a phase changes a Python script, check that the script is syntactically valid (`python -c "import py_compile; py_compile.compile('path', doraise=True)"`) before proceeding.

Use the repo-approved test runner (`python tests/run_pytest.py`) instead of raw `pytest` invocations. For full local validation, use `python tests/run_smoke_and_pytest.py`. See `DEVELOPMENT.md` for the complete runner inventory.

---

## PHASE 0: LOCK THE LIVE PLAN STATE

**Goal:** Build a concrete implementation checklist from the current live docs before changing code.

**Tasks:**
1. Read 00-v13, 02-v13, 03-v13, and 04-v13 in full.
2. Extract the active implementation requirements for every S-tier and A-tier item:
   - S6 docs-new structure
   - S7 glossary and naming contract
   - S5 routing ownership and regeneration rules
   - S1 root `llms.txt` descriptions
   - S2 era guide content
   - S4 per-module AGENTS.md
   - S3 cookbook ingest and content contract
   - Metadata field hardening (provenance renames, `lib/source_provenance.py`)
   - A5 routing metadata model (including `description` / `routing_summary` mapping)
   - A6 visible provenance (at stage 05a, not 03)
   - A7 routing and dead-link validation
   - A8 source-intake exclusions
   - A1 LuCI `luci-env.d.ts` (or deferral decision after investigation)
   - A2 deferral record
3. Note any ambiguity or contradictions found between plans. For blocking contradictions (two plans require incompatible behavior), ask immediately. For non-blocking uncertainties (unclear phrasing, missing detail that has a reasonable default), record the assumption in `working-checklist.md` and continue.
4. Save the checklist to a physical file at `docs/plans/v13/working-checklist.md`. Use `[ ]` / `[x]` notation. This file is your durable memory — re-read it at the start of every phase to confirm what is done and what remains. Update it with `[x]` as you complete each item.

**Exit condition:** `working-checklist.md` exists, is concrete and current, and has no unresolved blocking ambiguities. Non-blocking assumptions are recorded.

---

## PHASE 1: ESTABLISH BASELINE

**Goal:** Confirm the current pipeline works before making changes. This gives you a known-good state to diff against.

**Tasks:**
1. Read the pipeline workflow file (`.github/workflows/openwrt-docs4ai-00-pipeline.yml`) to understand stage ordering, parallelism, and environment variables.
2. Read the validator (`08-validate-output.py`) to understand the current gatekeeper contract — especially what fields it requires in L2, what it rejects, and what it reports.
3. Read the contract tests (`tests/pytest/pytest_09_release_tree_contract_test.py`) to understand the current test fixtures and assertions.
4. Confirm the existing test suite passes in its current state: `python tests/run_pytest.py`.
5. Note any pre-existing failures or warnings.

**Exit condition:** You know the current pipeline state, the test suite result, and the validator contract before making any changes.

---

## PHASE 2: BUILD THE DOCS-NEW SCAFFOLD

**Goal:** Create the clean docs destination before pipeline behavior expands.

**Tasks:**
1. Create `docs/docs-new/` with the required structure from 02-v13 §S6.
2. Add the minimum required starter files:
   - `docs/docs-new/output/release-tree-contract.md` — migrate from `docs/specs/v12/release-tree-contract.md`, update version label to V6, add v13 additions (cookbook module, per-module AGENTS.md, expanded README)
   - `docs/docs-new/pipeline/pipeline-stage-catalog.md` — ordered catalog of every pipeline script
   - `docs/docs-new/pipeline/regeneration-rules.md` — rerun triggers, stage independence, overlay system
   - `docs/docs-new/project/glossary-and-naming-contract.md` — S7 deliverable
   - `docs/docs-new/roadmap/deferred-features.md` — C-tier items and A2 deferral
3. Seed each file with truthful minimum structure and headings based on the live plans.
4. Record the A2 indefinite deferral in deferred-features with the exact popularity rationale from 04-v13.
5. Copy `docs/plans/v13/` into `docs/docs-new/plans/v13/`. Do not use symlinks — docs-new must be a self-contained durable directory, not a pointer back into legacy docs.

**Guard rails:**
- The pipeline-stage-catalog must list every numbered script including `02i`.
- docs-new must be self-contained — no dependency links back into legacy docs/.
- Do not attempt to rename `docs/` to `docs-old/` yet. That happens after v13 is complete.

**Exit condition:** The docs-new scaffold exists, is internally consistent, and has authoritative homes for routing contract, glossary, regeneration rules, and deferred features.

---

## PHASE 3: METADATA PROVENANCE HARDENING

**Goal:** Standardize provenance metadata across all ingest scripts before adding new pipeline features.

This is a foundational change that affects every `02*` script, `03`, `08`, and the contract tests. Do it early to avoid propagating stale field names into new code.

**Tasks:**
1. Create `lib/source_provenance.py` with shared helpers for normalizing `source_url`, `source_commit`, and `source_locator`.
2. Update `02a-scrape-wiki.py` first. Apply the provenance changes, then verify that `02a` produces correct L1 sidecars with `source_url`. Only after `02a` is verified, apply the exact same transformation pattern to `02b` through `02h`.
3. Update `03-normalize-semantic.py` to carry through `source_url` and `source_commit` from L1 sidecars into L2 frontmatter instead of reconstructing provenance late.
4. Remove the `REPO_BASE_URLS` derivation table from `03` if it's no longer needed.
5. Update `08-validate-output.py`:
   - Required fields: `["title", "module", "origin_type", "token_count"]`
   - Add `source_commit` to required fields only when `origin_type` is in a git-backed set
   - Exempt `origin_type: authored` from `source_commit` requirement
   - Reject stale fields: `version`, `upstream_path`, `original_url` should produce warnings or failures
6. Update `tests/pytest/pytest_09_release_tree_contract_test.py`:
   - Update mock L2 YAML fixtures to use `source_commit` instead of `version`
   - Add provenance assertions matching the new contract

**Guard rails:**
- Update `02a` first and verify it individually. Use the verified `02a` transformation as the exact pattern for `02b`–`02h`. Do not attempt to edit all 8 scripts in parallel.
- Do not remove `version` from L2 before updating the validator to expect `source_commit`.
- The contract tests must pass after the migration. If they don't, fix the tests to match the new contract, not the other way around.

**Exit condition:** All existing L2 output uses `source_url` / `source_commit` instead of `upstream_path` / `version`. The validator enforces the new contract. Contract tests pass.

---

## PHASE 4: CREATE LIVE COOKBOOK FIXTURES

**Goal:** Create minimal authored cookbook files that act as test fixtures for the pipeline.

**Tasks:**
1. Create `content/cookbook-source/`.
2. Author skeletal but contract-valid source files:
   - `openwrt-era-guide.md`
   - `common-ai-mistakes.md`
   - `architecture-overview.md`
3. Each file must include:
   - Complete YAML frontmatter per the 03-v13 content template (title, description, module, origin_type: authored, when_to_use, related_modules, era_status, verification_basis, reviewed_by, last_reviewed)
   - No `topic_slug` in frontmatter — `02i` derives it from the filename
   - H1 heading
   - When-to-use blockquote
   - Overview stub
   - All required section headings from the content contract
   - One or two conservative cross-links targeting eventual release-tree paths
4. Keep content minimal — these are fixtures first, tutorials second.

**Guard rails:**
- Do not write full tutorial content yet. Stubs with correct structure are the goal.
- Cross-links must use the `../../module/chunked-reference/file.md` pattern.
- Every frontmatter field must be filled — the pipeline should not have to handle missing required fields until the fail-fast behavior is verified.

**Exit condition:** Three skeletal cookbook files exist with valid frontmatter and correct section structure.

---

## PHASE 5: IMPLEMENT 02I COOKBOOK INGEST

**Goal:** Make cookbook source flow into L1.

**Tasks:**
1. Create `.github/scripts/openwrt-docs4ai-02i-ingest-cookbook.py` per 02-v13 §S3.
2. The script must:
   - Read all `.md` files from `content/cookbook-source/`
   - Require YAML frontmatter; fail fast if missing
   - Derive `topic_slug` from the filename (not require it in frontmatter)
   - Copy the markdown body (without frontmatter) to `L1-raw/cookbook/{filename}`
   - Write `.meta.json` sidecar with: `module: "cookbook"`, `origin_type: "authored"`, `topic_slug` from filename, and all authored metadata fields carried through
   - Fail fast if required authored metadata is missing
   - Print count of files processed
3. Add the script's docstring with Purpose, Phase, Layers, Inputs, Outputs, Dependencies.
4. Update `docs/docs-new/pipeline/pipeline-stage-catalog.md` to include `02i`.

**Guard rails:**
- Do not create a parallel metadata system. Use the universal L1 sidecar contract.
- `origin_type` must be `authored`, not `cookbook`.
- `source_url` and `source_commit` should be absent in the sidecar — cookbook content has no upstream git source.

**Verification:**
- Run `02i` against the three fixture files from Phase 4.
- Confirm L1-raw/cookbook/ contains three `.md` files and three `.meta.json` sidecars.
- Confirm `topic_slug` in each sidecar matches the filename.
- Confirm fail-fast when frontmatter is removed from a fixture.

**Exit condition:** Fixture cookbook files land in L1 with correct sidecars.

---

## PHASE 6: WIRE COOKBOOK THROUGH THE PIPELINE

**Goal:** Make cookbook behave like a real module downstream.

**Tasks:**
1. Update `03-normalize-semantic.py` to carry cookbook metadata correctly into L2. Carry through authored fields (`title`, `description`, `when_to_use`, `related_modules`, `era_status`, `verification_basis`, `reviewed_by`, `last_reviewed`). Do not synthesize `source_commit` for cookbook content.
2. Update `05a-assemble-references.py` to recognize cookbook L2 output and produce `map.md`, `bundled-reference.md`, and `chunked-reference/`.
3. Update `06-generate-llm-routing-indexes.py`:
   - Add `"cookbook": "Guides"` to `MODULE_CATEGORIES`
   - Add `"Guides"` to `CATEGORY_ORDER` — first position (also alphabetically natural)
   - Add `"cookbook": "..."` to `MODULE_DESCRIPTIONS`
4. Update the pipeline workflow to include `02i` in the collector group.
5. Update module discovery/configuration so cookbook participates without breaking existing modules.

**Guard rails:**
- Do not implement A2 output files.
- Preserve backward compatibility for all existing modules.
- The `Guides` category must appear first in `CATEGORY_ORDER`.

**Verification:**
- Run `02i` → `03` → `05a` → `06` with cookbook fixtures.
- Confirm `release-tree/cookbook/` contains `map.md`, `bundled-reference.md`, and `chunked-reference/` with the three fixture files.
- Confirm cookbook appears in root `llms.txt` under "Guides" category.
- Confirm existing modules are unaffected.

**Exit condition:** Cookbook fixtures flow through L1 → L2 → assembled output → routing surfaces without regressions.

---

## PHASE 7: PER-MODULE AGENTS.MD AND ROOT AGENTS.MD

**Goal:** Create the AI tool orientation layer per 02-v13 §S4.

**Tasks:**
1. Create per-module AGENTS.md files in `release-inputs/release-include/`:
   - `luci/AGENTS.md` — with era warning about Lua CBI, start-here pointers to JS form API
   - `ucode/AGENTS.md` — with language warning (not JavaScript), start-here pointers to stdlib docs
   - `cookbook/AGENTS.md` — with scope note (task guides, not API refs), era guide pointer
2. Update the root AGENTS.md template in `05b` to include:
   - Era awareness section
   - Per-module AGENTS.md discovery notice
3. Verify that the overlay copy step in the pipeline runs after `05b` so static per-module files are not overwritten.

**Guard rails:**
- Per-module AGENTS.md must be behavioral (what to do / avoid), not routing (file listings). That's what `llms.txt` is for.
- Use the exact content templates from 02-v13 §S4 as starting points.
- Do not generate per-module AGENTS.md dynamically in v13 — they are static overlay files.

**Exit condition:** Three per-module AGENTS.md files exist in release-inputs, the root AGENTS.md references them and the era guide, and overlay ordering is correct.

---

## PHASE 8: FIX ROOT ROUTING

**Goal:** Repair the highest-frequency routing problem before authoring expands.

**Tasks:**
1. Implement the S1 root module description improvement in `06-generate-llm-routing-indexes.py`.
2. Add the `MODULE_DESCRIPTIONS` dictionary with curated one-sentence summaries for each module.
3. Ensure root `llms.txt` no longer inherits misleading descriptions from bad upstream pages.
4. Confirm descriptions for at least `luci`, `ucode`, `wiki`, and `cookbook` are stable and accurate.
5. Update `release-inputs/release-include/README.md` with the module table using S1 curated text.

**Guard rails:**
- Do not solve this by adding more output files.
- `MODULE_DESCRIPTIONS` is the authoritative source for module-level summaries. Per-document `routing_summary` / `description` overrides happen at the document level, not the module level.

**Exit condition:** Root `llms.txt` no longer surfaces deprecated Lua/CBI or narrow transition material as primary module summaries.

---

## PHASE 9: INSTALL VALIDATION SAFETY NETS

**Goal:** Install validation rails before heavy content writing.

**Tasks:**
1. Implement the internal relative-link dead-link checker in `08-validate-output.py`:
   - Detect all internal relative markdown links in shipped release-tree `.md` files, excluding external URLs (starting with `http://` or `https://`) and anchor-only links (starting with `#`)
   - For each relative link, use `pathlib.Path` to resolve the absolute target path from the source file's parent directory, then check `path.exists()`
   - Fail validation if any relative link points to a non-existent file
   - Emit clear error messages identifying the source file and broken link target
2. Add or extend tests for:
   - Cookbook fixture flow (02i → L1 → L2 → assembled output)
   - Routing metadata precedence (`routing_summary` > `description` > heuristic)
   - Dead-link detection (test with a fixture containing a broken link)
   - Exclusion application behavior (Phase 10)
3. Run the full test suite and fix any failures.

**Guard rails:**
- Internal relative links only — no external network checks, no `requests.get()`
- Use `pathlib.Path` for relative path resolution, not string manipulation
- Dead-link failures must be deterministic and easy to diagnose
- The dead-link checker runs on the release-tree, not on L1 or L2 intermediate output
- Handle markdown link edge cases: ignore anchor-only links (`#section`), strip anchor suffixes from file references (`file.md#section` → check `file.md`), ignore image links (`![alt](path)`) unless they reference `.md` files

**Exit condition:** Broken internal links fail reliably, good fixtures pass, and the project has a safe base for larger content authoring.

---

## PHASE 10: IMPLEMENT A8 SOURCE EXCLUSIONS

**Goal:** Improve source quality before more routing and content amplify bad inputs.

**Tasks:**
1. Create `config/source-exclusions.yml` with the three reviewed first-pass entries:
   - `guide-developer-luci` — deprecated Lua/CBI tutorial
   - `techref-hotplug-legacy` — historical Hotplug2 page
   - `guide-developer-20-xx-major-changes` — narrow release-transition material
2. Create `lib/source_exclusions.py` with `should_exclude(source_type, identifier)`.
3. Apply exclusion checks in `02a-scrape-wiki.py` (and other `02*` scripts only if they have relevant exclusion candidates — wiki is the primary target for v13).
4. Add exclusion reporting in `08-validate-output.py` (informational, not a failure gate).
5. Add a test in the test suite verifying exclusion behavior.

**Guard rails:**
- Path-specific entries only — no broad globs
- Every exclusion has a `reason` field
- Exclusions are transparent and auditable
- `techref-swconfig` is intentionally NOT excluded — it provides truthful legacy-hardware guidance

**Exit condition:** Excluded sources do not reach L1. Unaffected sources process normally. Exclusion reasons are logged.

---

## PHASE 11: IMPLEMENT A5 ROUTING METADATA AND A6 PROVENANCE

**Goal:** Improve routing quality and visible trust signals.

**Tasks — A5:**
1. Update `03-normalize-semantic.py` to carry through optional routing fields from L1 sidecars: `routing_summary`, `routing_keywords`, `routing_priority`, `era_status`, `audience_hint`.
2. Update `06-generate-llm-routing-indexes.py` to prefer `routing_summary`, fall back to `description`, then fall back to heuristic.
3. Update `05a-assemble-references.py` to use `routing_summary` (or `description`) in `map.md`.

**Tasks — A6:**
4. In `05a-assemble-references.py`, during assembly of `chunked-reference/` and `bundled-reference.md`, inject a visible provenance header block from L2 frontmatter metadata. The exact output contract is:

   ```
   > **Source:** [source_url](source_url)
   > **Kind:** origin_type_value
   > **Commit:** source_commit_value
   > **Normalized:** pipeline_date
   ```

   Field sources:
   - **Source**: `source_url` from L2 frontmatter. Omit this entire line if `source_url` is absent.
   - **Kind**: `origin_type` from L2 frontmatter, rendered as-is (e.g., `js_source`, `wiki_page`, `authored`).
   - **Commit**: `source_commit` from L2 frontmatter. Omit this line if `source_commit` is absent (e.g., for `origin_type: authored`).
   - **Normalized**: date from `last_pipeline_run` in L2 frontmatter if available, otherwise the current pipeline run date from environment. If neither is available, omit the line rather than fabricating a date.

5. No fabricated URLs, dates, or metadata. Every line in the provenance block must trace to a specific L2 frontmatter field or a pipeline environment variable.

**Guard rails:**
- No fabricated provenance
- L2 files must NOT contain the visible block — it is publication-time only
- `description` / `routing_summary` mapping: cookbook authors write `description`, pipeline uses it as the routing summary. See 04-v13 §A5 field mapping section.

**Exit condition:** Published output shows provenance headers. Routing surfaces prefer curated metadata when present. L2 files remain clean data.

---

## PHASE 12: A1 INVESTIGATION AND IMPLEMENTATION

**Goal:** Extend the `.d.ts` type surface to LuCI if feasible.

**Session boundary:** This phase may run in a fresh session if the previous phases exhausted the context budget. If starting a fresh session, re-read `docs/plans/v13/working-checklist.md` and 04-v13 §A1 before proceeding.

**Tasks:**
1. Run the A1 investigation gate from 04-v13:
   - Examine `luci/chunked-reference/js_source-api-*.md` structure — read at most 2–3 representative files, not all of them
   - Determine whether headings, signatures, and type-like structure are stable enough for markdown-to-dts parsing
   - Alternatively examine raw LuCI JS source files from the cloned repo for JSDoc annotations
   - Choose: extend `05c` or create `05e-generate-luci-dts.py`
2. If feasible, implement the chosen approach.
3. Generate `release-tree/luci/types/luci-env.d.ts`.
4. Verify it passes `tsc --noEmit`.

**Guard rails:**
- If the investigation shows LuCI docs/source are too unstructured for reliable parsing, defer A1 to the deferred-features backlog rather than shipping unreliable output.
- `05d` is occupied. Use `05e` if a new script is needed.
- Limit scope to the core API surface: form, rpc, uci, view, dom, request, network.
- Do not greedily read large reference files. Read selectively to conserve context budget.

**Exit condition:** Either `luci-env.d.ts` exists and passes validation, or A1 is explicitly deferred with rationale in deferred-features.

---

## PHASE 13: EXPAND REAL COOKBOOK CONTENT

**Goal:** Write actual cookbook content once the pipeline and safety rails are proven.

**Session boundary:** This phase may run in a fresh session if the previous phases exhausted the context budget. If starting a fresh session, re-read `docs/plans/v13/working-checklist.md` and 03-v13 before proceeding.

Author S-tier topics first, then A-tier as time allows:
1. `openwrt-era-guide.md` — era transition table, legacy markers, research packet evidence
2. `common-ai-mistakes.md` — at least 7 mistake categories with WRONG/CORRECT pairs
3. `architecture-overview.md` — component diagram, data flow, ACL/permission boundaries

Then A-tier:
4. `procd-service-lifecycle.md`
5. `minimal-openwrt-package-makefile.md`
6. `uci-read-write-from-ucode.md`
7. `luci-form-with-uci.md`
8. Remaining B-tier topics as time allows

**Authoring process per topic (from 03-v13):**
1. **Draft:** Use an AI tool with large context window. Load the relevant module's `bundled-reference.md` and `.d.ts` files. For cross-component topics (architecture-overview, inter-component-communication-map), load `llms-full.txt` or a multi-module aggregation instead. When loading reference material, read no more than 2 chunked reference files at a time to conserve context budget.
2. **Verify:** Check every code example against corpus or upstream source. Verify every anti-pattern is traceable to a real failure mode. Confirm cross-links resolve.
3. **Review:** Run through the pipeline. Check stage 08 validation including dead-link checker.
4. **Ingest:** Content enters the pipeline via `02i` and flows through normally.

Author one topic at a time. Complete the full draft-verify-review-ingest cycle for one topic before starting the next.

**Rules for each topic:**
- Must satisfy the cookbook content contract from 03-v13 (all required sections, frontmatter, evidence rules)
- Must be evidence-backed — no AI priors as sole authority
- Must include anti-patterns with WRONG/CORRECT pairs
- Must cross-link to reference material instead of duplicating it
- Must pass internal-link validation after landing in the release-tree
- AI-assisted drafting must be disclosed in verification notes

**Guard rails:**
- Do not write content that outpaces the reference corpus. If a cookbook page references a feature not covered in the generated reference docs, that’s a content contract violation.
- The era guide requires external evidence beyond AI priors and corpus content. Forum posts, Reddit threads, and GitHub commits/PRs must support the era transition claims. If you have web-search capability, use it to gather evidence and cite sources. If you do not have web access, create `content/cookbook-source/era-guide-evidence-needed.md` listing the specific claims that require human-verified external sources, and proceed with the structural content only.

**Exit condition:** At least the three S-tier cookbook topics exist with full content, pass the content contract, and flow through a validated pipeline. If the era guide could not be fully evidence-verified due to tool limitations, the evidence gaps are explicitly documented.

---

## MANDATORY VERIFICATION LOOP

After every significant slice:
1. Run the smallest relevant proof first
2. Fix failures immediately
3. Only then move forward

If a test fails:
1. Read the test to understand what it actually asserts
2. Determine whether the test is correct and implementations is wrong, or vice versa
3. If the test reflects the v13 contract, fix the implementation
4. If the test reflects the stale v12 contract, update the test with a comment explaining why

---

## FINAL SUCCESS CONDITIONS

The run is successful only if ALL of these are true:

1. `docs/docs-new/` exists and is populated per 02-v13 §S6
2. Metadata provenance is hardened: L2 uses `source_url` / `source_commit`, stale fields are rejected by `08`
3. `lib/source_provenance.py` exists and is used by all `02*` ingest scripts
4. Cookbook source fixtures flow correctly through `02i` → L1 → L2 → assembled output
5. `origin_type: authored` is used for cookbook content, not `origin_type: cookbook`
6. Root `llms.txt` descriptions are fixed through `MODULE_DESCRIPTIONS` dict
7. Per-module `AGENTS.md` files exist for `luci`, `ucode`, and `cookbook`
8. Stage `08` catches internal dead links in the release-tree
9. A8 is implemented with the three approved first-pass wiki exclusions
10. A2 remains deferred and no extra `llms-xyz` routing file was created
11. A5 routing metadata and A6 visible provenance match the current 04-v13 design
12. Visible provenance is injected at stage `05a`, not stage `03`
13. Cookbook content is authored only after the pipeline and safety rails are proven
14. At least the three S-tier cookbook topics pass the content contract from 03-v13
15. Implementation remains aligned with 00-v13 through 04-v13 instead of inventing a parallel plan
16. All tests pass (`python tests/run_pytest.py`)
17. Stage `08` validation passes on the full release-tree
18. No symlinks exist in `docs/docs-new/` — all content is copied, not linked

If there is a tradeoff between "more content" and "better validated scaffolding," choose validated scaffolding first.

---
