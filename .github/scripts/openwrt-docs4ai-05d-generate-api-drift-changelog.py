"""
Purpose: Generates telemetry tracking API drift (changelog.json).
Phase: Telemetry
Layers: L5
Inputs: OUTDIR/ (Current Run), baseline/signature-inventory.json (Baseline)
Outputs: OUTDIR/changelog.json, OUTDIR/CHANGES.md, OUTDIR/signature-inventory.json
Environment Variables: OUTDIR
Dependencies: lib.config
Notes: Fails safely if baseline is missing. Saves current signatures for next run.
"""

import os
import json
import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

OUTDIR = config.OUTDIR
REGISTRY_PATH = os.path.join(OUTDIR, "cross-link-registry.json")


def resolve_baseline_dir():
    explicit = os.environ.get("BASELINE_DIR")
    if explicit:
        return os.path.abspath(explicit)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "baseline"))


def load_registry(registry_path=REGISTRY_PATH):
    if not os.path.isfile(registry_path):
        raise RuntimeError(f"cross-link-registry.json not found at {registry_path}")

    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_current_inventory(registry):
    return {sym: meta.get("signature") for sym, meta in registry.get("symbols", {}).items()}


def build_current_modules(registry):
    return sorted({meta["module"] for meta in registry.get("symbols", {}).values() if meta.get("module")})


def load_baseline_inventory(baseline_path):
    if not os.path.isfile(baseline_path):
        return {}, None

    with open(baseline_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    signatures = payload.get("signatures", {})
    raw_modules = payload.get("modules")
    if isinstance(raw_modules, list):
        modules = sorted({module for module in raw_modules if isinstance(module, str) and module})
    else:
        modules = None

    return signatures, modules


def compute_signature_drift(current_inventory, baseline_inventory):
    added = []
    removed = []
    changed = []

    for sym, sig in current_inventory.items():
        if sym not in baseline_inventory:
            added.append({"symbol": sym, "signature": sig})
        elif baseline_inventory[sym] != sig:
            changed.append({
                "symbol": sym,
                "old": baseline_inventory[sym],
                "new": sig
            })

    for sym in baseline_inventory:
        if sym not in current_inventory:
            removed.append({"symbol": sym, "signature": baseline_inventory[sym]})

    return added, removed, changed


def compute_module_drift(current_modules, baseline_modules):
    if baseline_modules is None:
        return [], []
    current_set = set(current_modules)
    baseline_set = set(baseline_modules)
    return sorted(current_set - baseline_set), sorted(baseline_set - current_set)


def build_changes_markdown(added, removed, changed, added_mods, removed_mods):
    lines = [
        "# openwrt-docs4ai API Displacement Log",
        f"**Run Date:** {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Summary",
        f"- **Added:** {len(added)}",
        f"- **Removed:** {len(removed)}",
        f"- **Changed:** {len(changed)}",
        ""
    ]

    if added_mods:
        lines.append("## New Modules")
        for module in added_mods:
            lines.append(f"- `[NEW] {module}`")
        lines.append("")

    if removed_mods:
        lines.append("## Removed Modules")
        for module in removed_mods:
            lines.append(f"- `[DEL] {module}`")
        lines.append("")

    if added:
        lines.append("## Added Symbols")
        for item in sorted(added, key=lambda x: x["symbol"]):
            lines.append(f"- `{item['symbol']}` : `{item['signature']}`")
        lines.append("")

    if removed:
        lines.append("## Removed Symbols")
        for item in sorted(removed, key=lambda x: x["symbol"]):
            lines.append(f"- `{item['symbol']}`")
        lines.append("")

    if changed:
        lines.append("## Modified Signatures")
        for item in sorted(changed, key=lambda x: x["symbol"]):
            lines.append(f"- `{item['symbol']}`")
            lines.append(f"  - **Was:** `{item['old']}`")
            lines.append(f"  - **Now:** `{item['new']}`")
        lines.append("")

    return lines


def main():
    print("[05d] Generating L5 Changelog and Telemetry")
    baseline_dir = resolve_baseline_dir()
    baseline_path = os.path.join(baseline_dir, "signature-inventory.json")

    try:
        registry = load_registry(REGISTRY_PATH)
    except Exception as exc:
        print(f"[05d] FAIL: {exc}")
        return 1

    current_inventory = build_current_inventory(registry)
    current_modules = build_current_modules(registry)

    try:
        baseline_inventory, baseline_modules = load_baseline_inventory(baseline_path)
    except Exception as exc:
        print(f"[05d] WARN: Could not parse baseline inventory: {exc}")
        baseline_inventory, baseline_modules = {}, None

    if baseline_inventory:
        print(f"[05d] Loaded baseline with {len(baseline_inventory)} signatures from {baseline_path}.")
    else:
        print("[05d] INFO: No baseline inventory found. This is likely the first run.")

    if baseline_modules is None and os.path.isfile(baseline_path):
        print("[05d] INFO: Baseline lacks module metadata; suppressing module drift sections.")

    added, removed, changed = compute_signature_drift(current_inventory, baseline_inventory)
    added_mods, removed_mods = compute_module_drift(current_modules, baseline_modules)

    changelog = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed)
        },
        "details": {
            "added": added,
            "removed": removed,
            "changed": changed
        }
    }

    with open(os.path.join(OUTDIR, "changelog.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(changelog, f, indent=2)

    changes_md = build_changes_markdown(added, removed, changed, added_mods, removed_mods)
    with open(os.path.join(OUTDIR, "CHANGES.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(changes_md))

    inventory_payload = {
        "generated": datetime.datetime.now(datetime.UTC).isoformat(),
        "signatures": current_inventory
    }
    with open(os.path.join(OUTDIR, "signature-inventory.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(inventory_payload, f, indent=2)

    print(f"[05d] OK: changelog.json, CHANGES.md, signature-inventory.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
