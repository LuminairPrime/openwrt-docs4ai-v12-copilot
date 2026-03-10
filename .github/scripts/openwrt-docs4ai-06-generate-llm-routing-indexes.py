"""
Purpose: Generates the L3 navigational maps (llms.txt and llms-full.txt).
Phase: Aggregation / Indexing
Layers: L4 -> L3
Inputs: OUTDIR/ 
Outputs: OUTDIR/llms.txt, OUTDIR/llms-full.txt, OUTDIR/{module}/llms.txt
Environment Variables: OUTDIR, OPENWRT_COMMIT, LUCI_COMMIT, WORKDIR
Dependencies: pyyaml, lib.config
Notes: Creates both the hierarchical entry point and the flat global catalog.
"""

import os
import re
import glob
import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, repo_manifest

sys.stdout.reconfigure(line_buffering=True)

try:
    import yaml
except ImportError:
    print("[06] FAIL: 'pyyaml' package not installed")
    sys.exit(1)

OUTDIR = config.OUTDIR
L2_DIR = os.path.join(OUTDIR, "L2-semantic")

CATEGORIES = {
    "Core Daemons": ["procd", "uci", "openwrt-hotplug"],
    "Scripting & Logic": ["ucode", "luci"],
    "Ecosystem": ["openwrt-core", "luci-examples"],
    "Manuals": ["wiki"]
}



def build_version_string(env=None):
    env_snapshot = env if env is not None else {key: os.environ.get(key) for key in repo_manifest.COMMIT_ENV_TO_MANIFEST_KEY}
    missing = [key for key, value in env_snapshot.items() if not value]
    commits, manifest_path = repo_manifest.resolve_commit_environment(
        env=env_snapshot,
        extra_manifest_paths=[config.REPO_MANIFEST_PATH, os.path.join(OUTDIR, "repo-manifest.json")],
    )

    versions = [
        f"openwrt/openwrt@{commits['OPENWRT_COMMIT']}",
        f"openwrt/luci@{commits['LUCI_COMMIT']}",
        f"jow-/ucode@{commits['UCODE_COMMIT']}"
    ]
    return ", ".join(versions), missing, manifest_path


def main():
    if not os.path.isdir(L2_DIR):
        print(f"[06] FAIL: L2 directory not found: {L2_DIR}")
        return 1

    version_str, missing, manifest_path = build_version_string()
    if missing and manifest_path:
        print(f"[06] INFO: Loaded missing commit versions from {manifest_path}")

    global_tokens = 0
    global_files = []
    module_registry = {}

    print("[06] Generating L3 Navigational Maps (llms.txt)")

    for module in sorted(os.listdir(L2_DIR)):
        mod_dir = os.path.join(L2_DIR, module)
        if not os.path.isdir(mod_dir):
            continue

        mod_files = []
        mod_tokens = 0
        mod_desc = module

        for fpath in sorted(glob.glob(os.path.join(mod_dir, "*.md"))):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                fm_match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?(.*)', content, re.DOTALL)
                if not fm_match:
                    print(f"[06] WARN: Invalid L2 schema in {fpath}")
                    continue

                fm_text = fm_match.group(1)
                fm = yaml.safe_load(fm_text) or {}

                tokens = fm.get("token_count", 0)
                desc = fm.get("ai_summary") or fm.get("description", "No description")

                global_tokens += tokens
                mod_tokens += tokens

                rel_path = f"L2-semantic/{module}/{os.path.basename(fpath)}"
                record = {
                    "rel_path": rel_path,
                    "tokens": tokens,
                    "desc": desc
                }
                mod_files.append(record)
                global_files.append(record)

                if mod_desc == module and desc != "No description":
                    mod_desc = desc

            except Exception as e:
                print(f"[06] WARN: Skipping {fpath}: {e}")

        if not mod_files:
            continue

        out_mod_dir = os.path.join(OUTDIR, module)
        os.makedirs(out_mod_dir, exist_ok=True)

        with open(os.path.join(out_mod_dir, "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# {module} module\n")
            f.write(f"> **Total Context:** ~{mod_tokens} tokens\n\n")
            for rec in mod_files:
                target = f"../L2-semantic/{module}/{os.path.basename(rec['rel_path'])}"
                f.write(f"- [{os.path.basename(rec['rel_path'])}]({target}) ({rec['tokens']} tokens) - {rec['desc']}\n")

        module_registry[module] = {
            "tokens": mod_tokens,
            "desc": mod_desc,
            "path": f"./{module}/llms.txt"
        }

        l4_name = f"{module}-complete-reference.md"
        l3_name = f"{module}-skeleton.md"

        if os.path.isfile(os.path.join(out_mod_dir, l4_name)):
            global_files.append({
                "rel_path": f"{module}/{l4_name}",
                "tokens": mod_tokens,
                "desc": f"Complete monolithic reference for {module}"
            })
        if os.path.isfile(os.path.join(out_mod_dir, l3_name)):
            global_files.append({
                "rel_path": f"{module}/{l3_name}",
                "tokens": int(mod_tokens * 0.1),
                "desc": f"Structural skeleton/map for {module}"
            })

    print(f"[06] Indexed {len(global_files)} files totaling ~{global_tokens} tokens.")

    with open(os.path.join(OUTDIR, "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# openwrt-docs4ai - LLM Routing Index\n")
        f.write("> For a flat file listing, see [llms-full.txt](./llms-full.txt)\n\n")
        f.write(f"> **Version:** {version_str}\n")
        f.write(f"> **Total Context Available:** ~{global_tokens} tokens\n\n")

        for cat_name, mod_list in CATEGORIES.items():
            found = [m for m in mod_list if m in module_registry]
            if found:
                f.write(f"## {cat_name}\n")
                for m in found:
                    reg = module_registry[m]
                    f.write(f"- [{m}]({reg['path']}): {reg['desc']} (~{reg['tokens']} tokens)\n")
                f.write("\n")

        uncat = [m for m in module_registry.keys() if not any(m in cat_list for cat_list in CATEGORIES.values())]
        if uncat:
            f.write("## Other Components\n")
            for m in sorted(uncat):
                reg = module_registry[m]
                f.write(f"- [{m}]({reg['path']}): {reg['desc']} (~{reg['tokens']} tokens)\n")
            f.write("\n")

        f.write("## Complete Aggregation\n")
        f.write("If your context window permits, you may fetch the flat URL index:\n")
        f.write("- [llms-full.txt](./llms-full.txt)\n")

    with open(os.path.join(OUTDIR, "llms-full.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# openwrt-docs4ai - Complete Flat Catalog\n")
        f.write(f"> **Total Context:** ~{global_tokens} tokens\n\n")

        for rec in sorted(global_files, key=lambda x: x["rel_path"]):
            f.write(f"- [{rec['rel_path']}](./{rec['rel_path']}) ({rec['tokens']} tokens) - {rec['desc']}\n")

    print("[06] Complete: Generated llms.txt, llms-full.txt, and module-level indexes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
