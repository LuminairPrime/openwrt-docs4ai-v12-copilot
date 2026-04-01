"""
Purpose: Copy and wrap curated LuCI application examples from the LuCI repo to L1 format.
Phase: Extraction
Layers: L0 -> L1
Inputs: tmp/repo-luci/applications/
Outputs: tmp/L1-raw/luci-examples/*.md and .meta.json
Environment Variables: WORKDIR, SKIP_BUILDROOT
Dependencies: lib.config, lib.extractor
Notes: Wraps .uc and .js files from 4 curated apps in Markdown blocks.
"""

import os
import sys
import re
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config, extractor
from lib.source_provenance import make_git_source_url, REPO_BASE_LUCI

sys.stdout.reconfigure(line_buffering=True)

LUCI_COMMIT = os.environ.get("LUCI_COMMIT", "unknown")
# Removed SKIP_BUILDROOT gate (BUG-020)

SRC = os.path.join(config.WORKDIR, "repo-luci", "applications")
TS = datetime.datetime.now(datetime.UTC).isoformat()
LUCI_URL = "https://github.com/openwrt/luci/tree/master/applications"

# App metadata: name -> description
APPS = {
    "luci-app-example": "Hello world / baseline — minimum viable app; ucode<->JS bridge, ACL, UCI form, rpcd scaffolding",
    "luci-app-commands": "HTTP API / controller — custom endpoints in ucode/controller/, URL parsing, secure popen execution",
    "luci-app-ddns": "Standard config app — service state (init_enabled), rpcd microbus, deep UCI read/write",
    "luci-app-dockerman": "Advanced / streaming — UNIX socket communication, HTTP streaming, large JSON, multi-file ucode",
}

if not os.path.isdir(SRC):
    print("[02e] FAIL: repo-luci not found")
    sys.exit(1)


def main():
    outputs_generated = 0
    read_failures = 0

    for app, desc in APPS.items():
        app_dir = os.path.join(SRC, app)
        if not os.path.isdir(app_dir):
            print(f"[02e] WARN: {app} not found at {app_dir} — skipping")
            continue

        print(f"[02e] Extracting {app}...")

        uc_count = 0
        js_count = 0
        app_read_failures = 0

        for root, _, files in os.walk(app_dir):
            for fname in sorted(files):
                if not (fname.endswith(".uc") or fname.endswith(".js")):
                    continue

                src_file = os.path.join(root, fname)
                rel = os.path.relpath(src_file, app_dir).replace("\\", "/")
                try:
                    with open(src_file, encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except Exception as exc:
                    read_failures += 1
                    app_read_failures += 1
                    print(f"[02e] WARN: Could not read {app}/{rel}: {exc}")
                    continue

                slug = f"{app}-{rel.replace('/', '-')}"
                slug = re.sub(r"[^a-zA-Z0-9-]", "-", slug).lower()

                is_uc = fname.endswith(".uc")
                lang = "ucode" if is_uc else "javascript"

                if is_uc:
                    uc_count += 1
                else:
                    js_count += 1

                final_content = extractor.wrap_code_block(fname, content, lang)

                metadata = {
                    "extractor": "02e-scrape-example-packages.py",
                    "origin_type": "example_app",
                    "module": "luci-examples",
                    "slug": slug,
                    "source_url": make_git_source_url(REPO_BASE_LUCI, LUCI_COMMIT, f"applications/{app}/{rel}"),
                    "source_locator": f"applications/{app}/{rel}",
                    "source_commit": LUCI_COMMIT,
                    "language": lang,
                    "fetch_status": "success",
                    "extraction_timestamp": TS,
                }

                extractor.write_l1_markdown("luci-examples", "example_app", slug, final_content, metadata)
                outputs_generated += 1

        print(f"[02e] OK: {app} ({uc_count} .uc, {js_count} .js, {app_read_failures} read failures)")

    print(f"[02e] Complete: {outputs_generated} total extracted.")
    if read_failures:
        print(f"[02e] WARN: Encountered {read_failures} curated file read failure(s).")
    if outputs_generated == 0:
        print("[02e] FAIL: Zero output files generated. Exiting with error.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
