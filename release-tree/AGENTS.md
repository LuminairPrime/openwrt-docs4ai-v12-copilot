# AGENTS.md — AI Agent Instructions for the openwrt-docs4ai release tree

## Repository Structure
- `llms.txt` — Start here. Root router covering every published module.
- `llms-full.txt` — Exhaustive flat catalog of published module routes and chunked-reference topics.
- `[module]/llms.txt` — Module-specific router with preferred entry points and topic pages.
- `[module]/map.md` — Navigation map for quick orientation within one module.
- `[module]/bundled-reference.md` — Broad bundled reference for one module.
- `[module]/chunked-reference/` — Targeted topic pages copied from the semantic layer.
- `[module]/types/*.d.ts` — Optional IDE schema surface when a module exports types.

## Conventions
- All token counts use `cl100k_base` encoding.
- Cross-references use relative Markdown links.
- `chunked-reference/` and `bundled-reference.md` contain the same authoritative programming content in different packaging forms.

## Rules & Constraints
1. **Entry Point:** Always begin navigation at `llms.txt`.
2. **Module Routing:** Once the target subsystem is known, switch to that module's `llms.txt` before reading the flat catalog.
3. **Context Budgets:** Prefer `map.md` for orientation, `bundled-reference.md` for broad ingestion, and `chunked-reference/` topic files for targeted lookups.
4. **Tooling Surfaces:** Treat generated `types/*.d.ts` files as published helper surfaces, not incidental by-products.
5. **No Hallucination:** DO NOT invent APIs, parameters, or configuration rules that do not appear in the published module files.

## Era Awareness
OpenWrt underwent a major modernization in 2019–2020. Many wiki pages and code examples reference
legacy patterns (Lua CBI, swconfig, ash scripting). Prefer current patterns (JavaScript views,
DSA, ucode). See `cookbook/chunked-reference/openwrt-era-guide.md` for details.

## Per-Module Instructions
Some modules include their own `AGENTS.md` with module-specific guidance.
Check `[module]/AGENTS.md` before beginning work on a specific subsystem.

## Current Context
- **Module Count:** 9
- **Total Token Count:** ~439660
- **Indexed Symbols:** 414
