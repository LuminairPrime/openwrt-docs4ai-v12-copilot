"""
Purpose: Generates the repository interaction map (AGENTS.md) and human README.md.
Phase: Indexing
Layers: L3
Inputs: PROCESSED_DIR/L2-semantic/, PROCESSED_DIR/manifests/cross-link-registry.json
Outputs: OUTDIR/AGENTS.md, OUTDIR/README.md
Environment Variables: OUTDIR
Dependencies: lib.config, pyyaml
Notes: Provides machine-readable guidelines for AI agents and human-readable docs.
"""

import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

OUTDIR = config.OUTDIR
REGISTRY_PATH = config.CROSS_LINK_REGISTRY
L2_DIR = config.L2_SEMANTIC_WORKDIR
RELEASE_TREE_DIR = config.RELEASE_TREE_DIR
TS = datetime.datetime.now(datetime.UTC).isoformat()

print("[05b] Generating AGENTS.md and README.md")

try:
    import yaml
except ImportError:
    print("[05b] FAIL: 'pyyaml' package not installed")
    sys.exit(1)


def load_registry_summary():
    symbol_count = 0
    if not os.path.isfile(REGISTRY_PATH):
        return symbol_count
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as handle:
            registry = json.load(handle)
        return len(registry.get("symbols", {}))
    except Exception as exc:
        print(f"[05b] WARN: Could not parse cross-link-registry.json: {exc}")
        return symbol_count


def load_l2_summary():
    modules = set()
    total_tokens = 0
    if not os.path.isdir(L2_DIR):
        return modules, total_tokens

    for module in sorted(os.listdir(L2_DIR)):
        mod_dir = os.path.join(L2_DIR, module)
        if not os.path.isdir(mod_dir):
            continue
        modules.add(module)
        for name in sorted(os.listdir(mod_dir)):
            if not name.endswith(".md"):
                continue
            file_path = os.path.join(mod_dir, name)
            try:
                with open(file_path, "r", encoding="utf-8") as handle:
                    content = handle.read()
                fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)", content, re.DOTALL)
                if not fm_match:
                    continue
                fm_data = yaml.safe_load(fm_match.group(1)) or {}
                total_tokens += int(fm_data.get("token_count", 0))
            except Exception as exc:
                print(f"[05b] WARN: Could not inspect {file_path}: {exc}")

    return modules, total_tokens


modules, total_tokens = load_l2_summary()
module_count = len(modules)
symbol_count = load_registry_summary()

os.makedirs(OUTDIR, exist_ok=True)

agents_content = f"""# AGENTS.md — AI Agent Instructions for openwrt-docs4ai

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
- **Module Count:** {module_count}
- **Total Token Count:** ~{total_tokens}
- **Indexed Symbols:** {symbol_count}
"""

readme_content = f"""# openwrt-docs4ai Generated Pipeline Output

**Pipeline Run Date:** {TS}
**Baseline Version:** Auto-generated via CI/CD

This repository branch contains the automatically generated, stable L3, L4, and L5 documentation layers for OpenWrt.

To ingest this generated corpus into an AI context window, begin at [llms.txt](./llms.txt).

If you already know the target subsystem, continue from that module's `llms.txt`. Use [llms-full.txt](./llms-full.txt) only when you need the exhaustive flat catalog.

For a human-readable, filesystem-derived browse view of the published tree, open [index.html](./index.html).

For AI agents navigating the published output tree, read [AGENTS.md](./AGENTS.md) for routing rules, context budgeting guidance, and source-boundary notes.
"""

release_agents_content = f"""# AGENTS.md — AI Agent Instructions for the openwrt-docs4ai release tree

## Repository Structure
- `llms.txt` — Start here. Root router covering every published module.
- `llms-full.txt` — Exhaustive flat catalog of published module routes and chunked-reference topics.
- `[module]/llms.txt` — Module-specific router with preferred entry points and topic pages.
- `[module]/{config.MODULE_MAP_FILENAME}` — Navigation map for quick orientation within one module.
- `[module]/{config.MODULE_BUNDLED_REF_FILENAME}` — Broad bundled reference for one module.
- `[module]/{config.MODULE_CHUNKED_REF_DIRNAME}/` — Targeted topic pages copied from the semantic layer.
- `[module]/{config.MODULE_TYPES_DIRNAME}/*.d.ts` — Optional IDE schema surface when a module exports types.

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
- **Module Count:** {module_count}
- **Total Token Count:** ~{total_tokens}
- **Indexed Symbols:** {symbol_count}
"""

release_readme_content = f"""# openwrt-docs4ai Release Tree

**Pipeline Run Date:** {TS}
**Baseline Version:** Auto-generated via CI/CD

This release tree packages the OpenWrt programming corpus for humans, IDE tooling, and LLM workflows.

Start at [llms.txt](./llms.txt) for root routing across modules. If you already know the target subsystem, continue from that module's `llms.txt`.

Within each module, use `map.md` for orientation, `bundled-reference.md` for broad context, and `chunked-reference/` for targeted lookups.

For a human-readable, filesystem-derived browse view of the published tree, open [index.html](./index.html).

For AI agents navigating the published output tree, read [AGENTS.md](./AGENTS.md) for routing rules and context-budget guidance.
"""

with open(os.path.join(OUTDIR, "AGENTS.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(agents_content)

with open(os.path.join(OUTDIR, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme_content)

os.makedirs(RELEASE_TREE_DIR, exist_ok=True)
with open(os.path.join(RELEASE_TREE_DIR, "AGENTS.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(release_agents_content)

with open(os.path.join(RELEASE_TREE_DIR, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(release_readme_content)

print("[05b] Complete.")
