# Deferred Features

**Version:** V13  
**Status:** Active  
**Last updated:** 2026-03-22

This document records features that were evaluated for V13 but explicitly deferred. Each entry states the feature, the reason for deferral, and the condition that would trigger re-evaluation.

---

## A2: Tiered llms.txt File Sizes

**Original spec:** Emit multiple routing file sizes: `llms-mini.txt`, `llms-small.txt`, `llms.txt` (standard), `llms-full.txt` (existing).

### Traffic Evidence (as of evaluation)

| File | Approximate monthly hits |
|------|--------------------------|
| `llms-mini.txt` | ~42 hits |
| `llms-small.txt` | ~498 hits |
| `llms-full.txt` | ~37,100 hits |
| `llms.txt` | ~116,000 hits |

### Deferral Rationale

The hit data shows that consumers primarily use the two existing files (`llms.txt` and `llms-full.txt`). There is no meaningful demand signal for intermediate sizes. Adding `llms-mini.txt` and `llms-small.txt`:

1. Introduces new format contracts that require ongoing maintenance (schema, naming, validation)
2. Would duplicate significant content generation logic in stage `06`
3. Provides no benefit until actual consumers adopt those endpoints

### Re-evaluation Condition

Re-assess if either:
- `llms-small.txt` traffic exceeds `llms.txt` traffic for two consecutive months, OR
- A major LLM tool vendor announces native support for tiered llms.txt endpoints

### Ticket / Tracking

See `docs/plans/v13/00-v13-ideas-tier-list-2026-03-22.md`, item A2.

---

## C-Tier Items

The following items were evaluated and assigned C-tier (low priority / deferred indefinitely) during V13 planning.

For full tier rationale, see `docs/plans/v13/00-v13-ideas-tier-list-2026-03-22.md`.

| Item | Summary | Deferral reason |
|------|---------|----------------|
| **C1: Wiki article grouping** | Group wiki articles by topic section in routing indexes | Requires stable wiki section taxonomy; current wiki structure changes frequently |
| **C2: Incremental extraction** | Skip unchanged files in 02* stages based on content hash | Adds significant complexity; full runs are fast enough under current corpus size |
| **C3: Language filtering** | Emit separate routing indexes per language | No non-English content exists in corpus; effort not justified |
| **C4: Markdown linting** | Run a Markdown linter on cookbook source files | Overkill for a hand-authored corpus of modest size; visual review is sufficient |
| **C5: Mermaid diagram promotion** | Promote the `templates/mermaid/` diagram templates to first-class pipeline outputs | No concrete consumer exists; templates remain available as opt-in |
| **C6: Alternative output formats** | Emit RST or AsciiDoc bundles | No demand signal from any known consumer |

---

## Known Soft Deferrals in V13 Implementation

These items are accepted limitations of the V13 implementation, tracked here to avoid re-investigation:

| Limitation | Detail |
|-----------|--------|
| `luci-app-dockerman` ucode validation warning (`REMOTE-008`) | Kept soft (truthful signal). Fix deferred until upstream stabilizes. |
| `signature-inventory.json` module metadata | Current `05d` suppresses false drift; richer schema is deferred to V14. |
| LuCI A1 dts JSON schema tooling | LuCI dts surface formally deferred to V13.1 or V14 due to tooling uncertainty. |

---

## Feature Retirement (V12 → V13)

Features that existed in V12 and are retired (not merely deferred) in V13:

| Retired feature | Reason |
|----------------|--------|
| `version` field in L2 frontmatter | Replaced by `source_commit`; stale field is soft-warned by validator |
| `upstream_path` field in L1/L2 | Replaced by `source_locator` (L1) and carry-through; stale field is soft-warned |
| `original_url` field in L1 wiki sidecar | Renamed to `source_url` for naming consistency |
| V5a release-tree-contract | Superseded by V6 contract in `docs/docs-new/output/release-tree-contract.md` |
