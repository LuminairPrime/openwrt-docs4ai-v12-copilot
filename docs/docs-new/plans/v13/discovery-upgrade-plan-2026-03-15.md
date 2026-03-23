# V13 Discovery Upgrade Plan

**Recorded:** 2026-03-15
**Status:** Planning baseline
**Scope:** Add structured discovery and queryability to the existing corpus
pipeline without turning the project into a DevDocs-style browser runtime.
**Relationship:** Complements
[the public distribution mirror plan](../v12/public-distribution-mirror-plan-2026-03-14-V2.md).
The mirror should consume V13 artifacts later; it should not define the first
V13 slice.

---

## 1. Purpose

This document saves the current recommended V13 direction to project disk as a
durable planning baseline.

The recommended V13 theme is an additive discovery-contract release:

- keep the repository as a documentation production pipeline
- keep the current L1/L2/L3/L4/L5 model intact
- add machine-readable discovery artifacts, stronger metadata, and optional
  static search surfaces
- defer any runtime-style rewrite, server-side search service, or heavy offline
  browser application behavior

The comparison with DevDocs was useful, but the best-fit reuse is at the
generator and artifact-contract level rather than direct scraper or UI code
reuse.

---

## 2. Executive Recommendation

### 2.1 Core recommendation

Ship V13 in two clearly separated scopes:

| Scope | Goal | Recommendation |
| --- | --- | --- |
| V13A | Add inner-corpus discovery contracts | Recommended for the first implementation slice |
| V13B | Add public distribution consumer UX over those contracts | Optional later slice |

V13A should include:

- a machine-readable corpus catalog
- normalized per-document provenance and freshness metadata
- static search and query data with tightly defined semantics
- only targeted transform modularization where it reduces maintenance risk

V13B may later include:

- a minimal browser search box or search-first landing experience
- public-root discovery surfaces for the distribution mirror
- release-root search and landing-page integration for non-maintainer users

### 2.2 First-slice exclusions

The first V13 slice should explicitly exclude:

- server-side search infrastructure
- embeddings or vector search
- live upstream crawling at query time
- command execution or command validation at search time
- service worker install flows and IndexedDB-backed per-user doc selection
- broad rewrite of the numbered pipeline or layer model

### 2.3 Why this is the right shape

This approach keeps the project aligned with its current strengths:

- deterministic generation
- static outputs
- CI-friendly validation
- low operational overhead
- strong compatibility with the current release and publication flow

---

## 3. Topic Summary

| Topic | Why it is worthwhile | Implementation difficulty | Release complexity | Primary risk | Recommendation |
| --- | --- | --- | --- | --- | --- |
| 1. Machine-readable corpus catalog | Highest leverage; creates the shared data contract for everything else | Low to medium | Low to medium | Freezing a public schema too casually | Start here |
| 2. Provenance and freshness metadata | Makes the corpus more trustworthy and machine-usable | Medium | Medium | Overstating freshness or source certainty | Do after catalog |
| 3. Lightweight search and query surfaces | First clear user-visible discovery feature | Medium to high | Medium to high | Scope expansion into full-text or hosted search | Do after metadata baseline |
| 4. Modular transform pipeline | Lowers long-term maintenance cost | High | High | Regressing brittle normalization behavior | Defer until contracts are stable |

The practical implication is simple: V13 gets much easier if the release is
treated as a contract-first upgrade rather than a feature buffet.

---

## 4. Topic 1: Machine-Readable Corpus Catalog

### 4.1 Objective

Create one canonical structured catalog for the published corpus so downstream
tools, LLM consumers, IDE integrations, and later public-mirror UX do not need
to parse `llms.txt` or crawl the filesystem to understand what exists.

### 4.2 Why this is worth doing

- It is the best foundation for every later discovery feature.
- It gives maintainers a stable contract to validate and diff between runs.
- It lets downstream tooling discover artifacts without scraping markdown.
- It provides one place to record artifact kind, preferred entry points, and
  stable paths.

### 4.3 Stakeholders who benefit

| Stakeholder | Benefit |
| --- | --- |
| Maintainers and pipeline operators | One contract to validate, diff, and review |
| Downstream tooling authors | Deterministic discovery without markdown scraping |
| LLM and agent consumers | Compact map of corpus surfaces and preferred starting points |
| IDE and editor tooling | Clean inventory of modules, indexes, symbol registries, and references |
| Casual public users | Indirect benefit until a browser shell consumes the catalog |

### 4.4 Current repo seams to reuse

- [docs/ARCHITECTURE.md](../../ARCHITECTURE.md)
- [docs/specs/v12/schema-definitions.md](../../specs/v12/schema-definitions.md)
- [openwrt-docs4ai-06-generate-llm-routing-indexes.py](../../../.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py)
- [openwrt-docs4ai-07-generate-web-index.py](../../../.github/scripts/openwrt-docs4ai-07-generate-web-index.py)
- [repo-manifest.json](../../../openwrt-condensed-docs/repo-manifest.json)
- [cross-link-registry.json](../../../openwrt-condensed-docs/cross-link-registry.json)

### 4.5 DevDocs inspiration

- [DevDocs `doc.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/doc.rb)
- [DevDocs `manifest.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/manifest.rb)
- [DevDocs `docs.thor`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/tasks/docs.thor)
- [DevDocs `app.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/app.rb)
- [DevDocs `models/doc.js`](https://github.com/freeCodeCamp/devdocs/blob/main/assets/javascripts/models/doc.js)

### 4.6 Recommended artifact model

Publish a root `corpus-catalog.json` under `openwrt-condensed-docs/` with:

- `schema_version`
- `generated_at`
- `pipeline_version`
- upstream manifest summary
- module list
- total token counts
- stable artifact records with explicit `kind` values
- `recommended_entry_points` at root and module scope

Optional per-module `module-catalog.json` files can reduce consumer cost when a
tool only needs one module.

### 4.7 Implementation difficulty, risk, and release complexity

**Difficulty:** low to medium. Most of the required source data already exists
in the current generation flow.

**Primary risks:**

- choosing unstable `kind` names too early
- publishing order-unstable JSON that makes diffs noisy
- treating the first catalog draft as a permanent API before validation and
  versioning are defined

**Release complexity added:**

- one new root JSON artifact, possibly per-module JSON artifacts
- new schema validation in the output validator
- new fixture coverage for deterministic ordering and path validity
- release-note surface explaining the new discovery contract

### 4.8 Recommendation

This should be the first implemented V13 topic. It is the lowest-risk,
highest-leverage addition.

---

## 5. Topic 2: Per-Document Provenance and Freshness Metadata

### 5.1 Objective

Normalize and publish richer per-document metadata so the corpus can answer not
just what exists, but where it came from, how fresh it is, and how trustworthy
the source attribution is.

### 5.2 Why this is worth doing

- It converts the corpus from a file collection into a more trustworthy dataset.
- It improves downstream ranking and retrieval quality without needing AI.
- It gives maintainers better stale-data and override-triage visibility.

### 5.3 Stakeholders who benefit

| Stakeholder | Benefit |
| --- | --- |
| LLM and agent consumers | Better provenance and recency signals |
| Downstream tooling | Reliable `source_url`, `upstream_ref`, and integrity fields |
| Drift and telemetry tooling | Fields that can be compared across runs |
| Maintainers and curators | Better evidence when documents are stale, overridden, or manually curated |
| Casual public users | Mostly indirect benefit unless surfaced in UI later |

### 5.4 Current repo seams to reuse

- [ai-summary-feature-spec.md](../../specs/v12/ai-summary-feature-spec.md)
- [ai-tooling-user-stories-and-test-plan.md](../../specs/v12/ai-tooling-user-stories-and-test-plan.md)
- [openwrt-docs4ai-03-normalize-semantic.py](../../../.github/scripts/openwrt-docs4ai-03-normalize-semantic.py)
- [openwrt-docs4ai-06-generate-llm-routing-indexes.py](../../../.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py)
- [ai_corpus.py](../../../lib/ai_corpus.py)
- [ai_store.py](../../../lib/ai_store.py)
- [repo-manifest.json](../../../openwrt-condensed-docs/repo-manifest.json)

### 5.5 DevDocs inspiration

- [DevDocs `doc.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/doc.rb)
- [DevDocs scraper reference](https://github.com/freeCodeCamp/devdocs/blob/main/docs/scraper-reference.md)
- [DevDocs attribution filter](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/filters/core/attribution.rb)
- [DevDocs `manifest.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/manifest.rb)
- [DevDocs MDN scraper](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/scrapers/mdn/mdn.rb)

### 5.6 Recommended metadata model

Required published fields should stay small and deterministic:

- `module`
- `slug`
- `title`
- `origin_type`
- `version`
- `upstream_path`
- `source_kind`
- `generated_at`
- `last_pipeline_run`
- `repo_ref_set`
- `content_hash`
- `publication_kind`

Optional fields can include:

- `original_url`
- `source_url`
- `license`
- `attribution_text`
- `freshness_basis`
- `freshness_value`
- `summary_quality_hint`
- `curated_by_human`

AI-derived fields should remain optional hints, never correctness requirements.

### 5.7 Implementation difficulty, risk, and release complexity

**Difficulty:** medium. The field plumbing is manageable; the hard part is
semantic discipline.

**Primary risks:**

- overpromising freshness for wiki or generated content
- blending human curation, pipeline facts, and AI hints into one ambiguous
  field set
- turning internal AI store assumptions into a public contract too quickly

**Release complexity added:**

- broader schema definitions and validator coverage
- more fixture cases for missing optional fields and AI-disabled runs
- more release notes explaining what metadata is authoritative versus advisory
- possible later licensing and attribution follow-up work

### 5.8 Recommendation

This should be the second V13 topic, immediately after the catalog baseline.

---

## 6. Topic 3: Lightweight Search and Query Surfaces

### 6.1 Objective

Add a static search surface that helps humans, app authors, tooling, and
LLM-integrated clients find the right document, symbol, command, config key, or
hook without turning the project into a hosted search application.

### 6.2 What the search surface should actually do

The search surface should answer practical discovery questions such as:

- what command should I type to configure or inspect a subsystem?
- what API hook or callable surface exists when writing an app?
- what UCI key, section, environment variable, or hotplug field do I need?
- what document should I read first for this module?

The search surface should return typed entries, not just paragraph matches.

Recommended V13 entry families:

- document entries
- symbol entries
- command entries from high-confidence structured contexts
- config entries
- event entries
- alias entries

### 6.3 What the search surface should not promise

The first slice should not promise:

- arbitrary semantic paragraph search across the full corpus
- server-side search infrastructure
- natural-language answering from indexes alone
- execution or verification of returned shell commands
- user-specific offline installation behavior

### 6.4 Stakeholders who benefit

| Stakeholder | Benefit |
| --- | --- |
| Human developers | Faster lookup across modules and artifact layers |
| App authors | Direct lookup of LuCI APIs, ubus or rpcd hooks, ucode symbols, hotplug events, procd helpers, and examples |
| LLM and agent consumers | Smaller and more queryable retrieval surface than `llms-full.txt` |
| Downstream tooling | Typed query index that can be embedded into editors or local tools |
| Casual visitors | Major benefit only if a browser UI is added later |
| Maintainers | Better diagnostic and discovery surface over published outputs |

### 6.5 Current repo seams to reuse

- [signature-inventory.json](../../../openwrt-condensed-docs/signature-inventory.json)
- [cross-link-registry.json](../../../openwrt-condensed-docs/cross-link-registry.json)
- [openwrt-docs4ai-06-generate-llm-routing-indexes.py](../../../.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py)
- [openwrt-docs4ai-07-generate-web-index.py](../../../.github/scripts/openwrt-docs4ai-07-generate-web-index.py)

### 6.6 DevDocs inspiration

- [DevDocs `entry_index.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/entry_index.rb)
- [DevDocs entries filter](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/filters/core/entries.rb)
- [DevDocs `page_db.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/page_db.rb)
- [DevDocs `entry.js`](https://github.com/freeCodeCamp/devdocs/blob/main/assets/javascripts/models/entry.js)
- [DevDocs `searcher.js`](https://github.com/freeCodeCamp/devdocs/blob/main/assets/javascripts/app/searcher.js)
- [DevDocs service worker](https://github.com/freeCodeCamp/devdocs/blob/main/views/service-worker.js.erb)

### 6.7 Recommended artifact model

V13A should generate static search data such as `search-index.json` or sharded
per-module search JSON.

Each entry should expose at least:

- `kind`
- `label`
- `description`
- `module`
- `path`
- `aliases`
- optional ranking hints

Ranking guidance:

- prefer module entry points over raw L2 pages for broad queries
- prefer exact symbols, commands, config keys, and aliases over prose for exact
  lookups
- use AI fields only as secondary ranking hints

### 6.8 Implementation difficulty, risk, and release complexity

**Difficulty:** medium to high. The data generation is feasible, but precise and
useful query behavior requires strong scope control.

**Primary risks:**

- expanding from typed discovery into vague full-text search expectations
- extracting commands from low-confidence prose and surfacing misleading hits
- adding UI before the data contract is stable

**Release complexity added:**

- at least one new index artifact and matching validator logic
- fixture coverage for representative command, symbol, config, event, and alias
  queries
- optional browser UI testing if V13A includes UI, which is not recommended
- clearer release notes about what search can and cannot do

### 6.9 Recommendation

Implement the search data contract in V13A only after catalog and metadata are
stable. Keep any browser UI as an optional later step.

---

## 7. Topic 4: Modular Transform Pipeline

### 7.1 Objective

Reduce maintenance risk by refactoring the most brittle normalization paths into
ordered named transforms instead of continuing to grow large monolithic
scripts.

### 7.2 Why this is worth doing

- It lowers the cost of future source-family additions.
- It reduces duplication in extraction, normalization, and discovery emission.
- It makes search-entry and metadata extraction logic easier to test and reuse.

### 7.3 Stakeholders who benefit

| Stakeholder | Benefit |
| --- | --- |
| Pipeline maintainers | Easier reasoning, extension, and testing |
| Future source-family implementers | Shared transforms with narrow source overrides |
| Raw analysts and context injectors | More consistent L1 and L2 outputs |
| Casual public users | Mostly indirect reliability benefit |

### 7.4 Current repo seams to reuse

- [openwrt-docs4ai-02a-scrape-wiki.py](../../../.github/scripts/openwrt-docs4ai-02a-scrape-wiki.py)
- [openwrt-docs4ai-03-normalize-semantic.py](../../../.github/scripts/openwrt-docs4ai-03-normalize-semantic.py)
- [pytest_04_wiki_scraper_test.py](../../../tests/pytest/pytest_04_wiki_scraper_test.py)
- [implementation-status.md](../../specs/v12/implementation-status.md)

### 7.5 DevDocs inspiration

- [DevDocs scraper reference](https://github.com/freeCodeCamp/devdocs/blob/main/docs/scraper-reference.md)
- [DevDocs filter reference](https://github.com/freeCodeCamp/devdocs/blob/main/docs/filter-reference.md)
- [DevDocs `scraper.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/scraper.rb)
- [DevDocs `filter_stack.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/filter_stack.rb)
- [DevDocs `filter.rb`](https://github.com/freeCodeCamp/devdocs/blob/main/lib/docs/core/filter.rb)

### 7.6 Recommended modularization model

Do not copy DevDocs' Ruby or DOM stack literally.

Instead:

- define a Python-side transform registry for document records or content blocks
- separate shared transforms from source-family transforms
- pilot the approach in stage `03` first
- only touch `02a` after cache and failure behavior remain fully protected by
  tests

Candidate shared transforms:

- source-path normalization
- heading cleanup
- link canonicalization
- attribution injection
- summary extraction
- symbol extraction
- command extraction
- config-key extraction
- search-entry emission

### 7.7 Implementation difficulty, risk, and release complexity

**Difficulty:** high. This touches brittle, already-verified code paths.

**Primary risks:**

- changing verified output shape accidentally
- mixing refactor work with user-visible contract changes in the same release
- making failure or cache behavior harder to reason about

**Release complexity added:**

- more internal moving parts to explain and test
- broader regression surface across extraction and normalization
- higher rollback cost if done in the same wave as new public artifacts

### 7.8 Recommendation

Treat this as a V13.x or late-V13 task unless it becomes necessary to support
the catalog or search contracts cleanly.

---

## 8. Release-Wide Risk, Difficulty, and Complexity

### 8.1 Scope packages

| Scope package | Implementation difficulty | Release complexity | Main additional burden | Recommendation |
| --- | --- | --- | --- | --- |
| Catalog only | Low to medium | Low to medium | New schema, validator rules, fixture expectations | Very good first slice |
| Catalog + metadata | Medium | Medium | Stronger semantics and more validator coverage | Recommended V13A baseline |
| Catalog + metadata + search data | Medium to high | Medium to high | New index generation and query-contract testing | Good if time allows |
| Add browser search UI | High | High | UI maintenance, ranking expectations, compatibility testing | Optional follow-up |
| Add transform modularization | High | High | Refactor risk across verified pipeline behavior | Defer |
| Add public mirror consumer UX | High | High | Cross-repository release coordination | Separate V13B |

### 8.2 Main risks by release dimension

| Dimension | Risk |
| --- | --- |
| Schema design | Publishing unstable field names or semantics too early |
| Determinism | JSON ordering or ranking drift causing noisy releases |
| Verification | Insufficient fixture coverage for new catalog or search artifacts |
| Release messaging | Users misunderstanding search as command execution or full-text QA |
| Operational burden | More generated files to inspect and more contracts to keep aligned |
| Mirror integration | Treating the mirror as a blocker for core V13 artifacts |

### 8.3 Complexity added to the release

V13 will add real release complexity even if the implementation stays static and
generator-first.

The main new complexity areas are:

- **Artifact surface growth.** The release stops being only markdown and helper
  files and becomes a versioned discovery contract with new JSON surfaces.
- **Validation growth.** The validator and tests must move from file-presence
  checking into schema, ordering, and semantics checking.
- **Documentation growth.** Release notes and specs must explain the new data
  contracts and what search does not do.
- **Consumer compatibility.** Once downstream tools consume the catalog or index,
  schema changes must be intentional and versioned.
- **Triage growth.** Maintainers will need to inspect not only corpus outputs but
  also catalog health, metadata fidelity, and search-entry correctness.

This complexity is manageable if the scope stays additive and the rollout order
stays disciplined. It becomes much harder if V13 tries to ship catalog,
metadata, search UI, refactors, and public-mirror UX all at once.

---

## 9. Likely Release Documentation Set and Stakeholders

The table below describes the documents this release will likely need if V13 is
approved and implemented in a disciplined way.

| Document | Status | Purpose | Likely stakeholders or users |
| --- | --- | --- | --- |
| `docs/plans/v13/discovery-upgrade-plan-2026-03-15.md` | New | Planning baseline, scope, and sequencing | Maintainers, reviewers, architectural decision-makers |
| `docs/specs/v13/system-architecture.md` | New | V13 architecture delta from v12 | Maintainers, contributors, reviewers |
| `docs/specs/v13/schema-definitions.md` | New | Authoritative schema for catalog, metadata, and search outputs | Pipeline maintainers, downstream tooling, LLM and IDE integrators |
| `docs/specs/v13/execution-map.md` | New | Stage placement and data handoff rules | Pipeline maintainers, contributors |
| `docs/specs/v13/implementation-status.md` | New | What is implemented, verified, deferred, or out of scope | Release operators, maintainers, reviewers |
| `docs/specs/v13/search-and-discovery-contract.md` | New | Search entry families, ranking rules, supported queries, exclusions | App authors, downstream tooling, LLM and agent consumers |
| `docs/specs/v13/verification-and-rollout.md` | New | Local proof, smoke, and remote validation gates | Release operators, CI maintainers |
| `README.md` | Update | High-level project summary and links to V13 docs | New contributors, evaluators, maintainers |
| `DEVELOPMENT.md` | Update | Maintainer workflow and validation changes | Maintainers, contributors |
| `openwrt-condensed-docs/README.md` | Generated update | Public corpus usage guidance and entry points | Public users, LLM operators, downstream tooling |
| `openwrt-condensed-docs/CHANGES.md` | Generated update | Publicly visible artifact delta summary | Release operators, power users, downstream tooling |
| `templates/distribution-shell/README.md` | Conditional new file if V13B proceeds | Public-root explanation for the mirror repo | Casual visitors, public users |
| `templates/distribution-shell/llms.txt` | Conditional new file if V13B proceeds | Root-level routing for mirror consumers | LLM operators, agents, downstream tooling |
| `templates/distribution-shell/index.html` | Conditional new file if V13B proceeds | Search-first or browse-first public landing page | Casual visitors, evaluators, public users |

Two points matter here:

- V13A can ship without the conditional mirror-shell documents.
- The strongest release-document burden is in `docs/specs/v13`, not at the
  public shell.

---

## 10. Recommended Implementation Order

1. Approve the V13A scope boundary and fix current documentation drift before
   touching stage behavior.
2. Create the V13 spec set under `docs/specs/v13/`.
3. Implement Topic 1, the machine-readable corpus catalog.
4. Implement Topic 2, provenance and freshness metadata.
5. Implement Topic 3, search and query data.
6. Add browser UI only if the search data contract is already stable.
7. Defer Topic 4 modularization unless it becomes necessary for clean contract
   implementation.
8. Treat the public distribution mirror as a consumer proof, not a dependency,
   unless V13B is explicitly approved.

---

## 11. Verification Expectations

At minimum, each accepted V13 slice should:

- add fixture-backed tests before remote workflow proof
- prove deterministic output ordering
- prove AI-disabled fallback behavior where relevant
- keep current routing surfaces valid unless the release intentionally changes
  them
- pass the supported local verification paths documented in
  [tests/README.md](../../../tests/README.md)

Recommended verification anchors:

- [pytest_01_workflow_contract_test.py](../../../tests/pytest/pytest_01_workflow_contract_test.py)
- [pytest_02_fixture_pipeline_contract_test.py](../../../tests/pytest/pytest_02_fixture_pipeline_contract_test.py)
- [pytest_04_wiki_scraper_test.py](../../../tests/pytest/pytest_04_wiki_scraper_test.py)
- [pytest_06_warning_regression_test.py](../../../tests/pytest/pytest_06_warning_regression_test.py)
- [smoke_pipeline_support.py](../../../tests/support/smoke_pipeline_support.py)

---

## 12. Final Recommendation

The best V13 release is not a search product rewrite. It is a disciplined
upgrade to the corpus contract.

If only one V13 feature is approved, it should be the machine-readable catalog.
If two are approved, add provenance metadata. If three are approved, add static
search data. Only after those are real and verified should the project absorb
search UI, deeper transform refactors, or public-mirror UX work.