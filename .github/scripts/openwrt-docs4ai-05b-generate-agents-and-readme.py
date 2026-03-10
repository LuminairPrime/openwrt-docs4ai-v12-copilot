"""
Purpose: Generates the repository interaction map (AGENTS.md) and human README.md.
Phase: Indexing
Layers: L3
Inputs: OUTDIR/L2-semantic/, OUTDIR/cross-link-registry.json
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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

OUTDIR = config.OUTDIR
REGISTRY_PATH = os.path.join(OUTDIR, "cross-link-registry.json")
L2_DIR = os.path.join(OUTDIR, "L2-semantic")
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
                fm_match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?(.*)', content, re.DOTALL)
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
- **Module Count:** {module_count}
- **Total Token Count:** ~{total_tokens}
- **Indexed Symbols:** {symbol_count}
"""

readme_content = f"""# openwrt-docs4ai Generated Pipeline Output

**Pipeline Run Date:** {TS}
**Baseline Version:** Auto-generated via CI/CD

This repository branch contains the automatically generated, stable L3, L4, and L5 documentation layers for OpenWrt. 

To ingest this repository into an AI context window (e.g. Claude, GPT-4, Cursor), begin your prompt by referencing:

```
https://openwrt.github.io/openwrt-docs4ai/llms.txt
```

For AI Agents iterating on workflows, please read [AGENTS.md](./AGENTS.md) for structural mapping and rules.
"""

with open(os.path.join(OUTDIR, "AGENTS.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(agents_content)

with open(os.path.join(OUTDIR, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme_content)

print("[05b] Complete.")
