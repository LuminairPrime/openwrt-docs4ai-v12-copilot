# AGENTS.md — AI Agent Instructions for openwrt-docs4ai

## Repository Structure
- `llms.txt` — Start here. Hierarchical index linking to each target subsystem.
- `llms-full.txt` — Exhaustive flat catalog of generated AI-facing documents and helper surfaces.
- `[module]/llms.txt` — Module-specific navigation surface with preferred entry points, tooling, and source documents.
- `[module]/*-complete-reference.md` — Monolithic L4 file best ingested if context size permits.
- `[module]/*-skeleton.md` — Structural API outlines serving as navigational aids.
- `[module]/*.d.ts` — TypeScript definitions for IDEs and static analysis.

## Conventions
- All token counts use `cl100k_base` encoding.
- Cross-references use relative Markdown links.
- Generated routing files follow the v12 Schema Definitions contract for root indexes, module indexes, and helper surfaces.

## Rules & Constraints
1. **Entry Point:** Always begin navigation at `llms.txt`. Do not guess paths.
2. **Module Routing:** Once the target subsystem is known, switch to that module's `llms.txt` before reading the flat catalog.
3. **Context Budgets:** Prefer `*-skeleton.md` files for orientation, then monolithic references, and only then individual L2 documents when deeper provenance is needed.
4. **Tooling Surfaces:** Treat generated `.d.ts` files and module `llms.txt` files as published helper surfaces, not incidental by-products.
5. **No Hallucination:** DO NOT hallucinate API parameters or functions outside of what is defined in the generated indexes or document bodies.
6. **Wiki Scraping:** DO NOT blindly scrape the live OpenWrt wiki. Use these pre-processed, deduplicated documents instead to save tokens and avoid 404s.

## Source Boundary

- This generated corpus is the published AI navigation surface.
- Maintainer implementation guidance lives in the source repository docs and is intentionally separate.
- Do not assume a separate source-repo root `llms.txt` exists for the implementation tree.

## Current Context
- **Module Count:** 8
- **Total Token Count:** ~427022
- **Indexed Symbols:** 401
