# AGENTS.md — AI Agent Instructions for openwrt-docs4ai

## Repository Structure
- `llms.txt` — Start here. Hierarchical index linking to each target subsystem.
- `llms-full.txt` — Flat listing of every document with token counts.
- `[module]/*-complete-reference.md` — Monolithic L4 file best ingested if context size permits.
- `[module]/*-skeleton.md` — Structural API outlines serving as navigational aids.
- `[module]/*.d.ts` — TypeScript definitions for IDEs and static analysis.

## Conventions
- All token counts use `cl100k_base` encoding.
- Cross-references use relative Markdown links.
- Files strictly adhere to the v12 Schema Definitions.

## Rules & Constraints
1. **Entry Point:** Always begin navigation at `llms.txt`. Do not guess paths.
2. **Context Budgets:** Respect your context window limits. Prefer `*-skeleton.md` files for structural understanding before fetching monolithic references.
3. **No Hallucination:** DO NOT hallucinate API parameters or functions outside of what is defined in the `*-skeleton.md` indexes or the text bodies.
4. **Wiki Scraping:** DO NOT blindly scrape the live OpenWrt wiki. Use these pre-processed, deduplicated documents instead to save tokens and avoid 404s.

## Current Context
- **Module Count:** 8
- **Total Token Count:** ~434368
- **Indexed Symbols:** 397
