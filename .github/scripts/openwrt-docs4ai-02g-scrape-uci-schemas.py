"""
Purpose: Scrape the openwrt UCI configuration schemas from package defaults.
Phase: Extraction
Layers: L0 -> L1
Inputs: tmp/repo-openwrt/package/**/etc/config/*
Outputs: tmp/L1-raw/uci/*.md and .meta.json
Environment Variables: WORKDIR
Dependencies: lib.config, lib.extractor
Notes: Parses default configuration files to serve as UCI schemas.
"""

import os
import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, extractor
from lib.source_provenance import make_git_source_url, REPO_BASE_OPENWRT

sys.stdout.reconfigure(line_buffering=True)

OPENWRT_COMMIT = os.environ.get("OPENWRT_COMMIT", "unknown")

print("[02g] Scrape UCI default configurations")

package_dir = os.path.join(config.WORKDIR, "repo-openwrt", "package")
if not os.path.isdir(package_dir):
    print(f"[02g] SKIP: repository not found at {package_dir}")
    sys.exit(0)

schema_files = []
for root, dirs, files in os.walk(package_dir):
    if "etc" in dirs:
        etc_config_dir = os.path.join(root, "etc", "config")
        if os.path.isdir(etc_config_dir):
            for f in os.listdir(etc_config_dir):
                full_path = os.path.join(etc_config_dir, f)
                if os.path.isfile(full_path):
                    schema_files.append((f, full_path))

if not schema_files:
    print("[02g] FAIL: No UCI schema files found")
    sys.exit(1)

ts = datetime.datetime.now(datetime.UTC).isoformat()
saved = 0

for schema_name, fpath in schema_files:
    try:
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        if "config " not in content:
            continue
            
        rel_path = os.path.relpath(fpath, os.path.join(config.WORKDIR, "repo-openwrt")).replace("\\", "/")
        
        # FIX BUG-011: Slug collision protection (UCI)
        # Identify package name from path
        pkg_parts = rel_path.split("/")
        pkg_name = pkg_parts[1] if len(pkg_parts) > 1 else "core"
        slug = f"schema-{pkg_name}-{schema_name}"
        
        final_content = f"# UCI Default Schema: {schema_name}\n\n"
        final_content += f"> **Source:** `{rel_path}`\n\n"
        final_content += extractor.wrap_code_block(schema_name, content.strip(), "uci")
        
        metadata = {
            "extractor": "02g-scrape-uci-schemas.py",
            "origin_type": "uci_schema",
            "module": "uci",
            "slug": slug,
            "source_url": make_git_source_url(REPO_BASE_OPENWRT, OPENWRT_COMMIT, rel_path),
            "source_locator": rel_path,
            "source_commit": OPENWRT_COMMIT,
            "language": "uci",
            "fetch_status": "success",
            "extraction_timestamp": ts
        }

        extractor.write_l1_markdown("uci", "uci_schema", slug, final_content, metadata)
        saved += 1
        
    except Exception as e:
        print(f"[02g] WARN: Could not process {fpath}: {e}")

print(f"[02g] Complete: Wrote {saved} UCI default schemas")
if saved == 0:
    print("[02g] FAIL: Zero output files generated. Exiting with error.")
    sys.exit(1)
