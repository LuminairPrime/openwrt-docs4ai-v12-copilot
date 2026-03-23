"""
Purpose: Scrape the openwrt procd shell API documentation from procd.sh comments.
Phase: Extraction
Layers: L0 -> L1
Inputs: tmp/repo-openwrt/package/system/procd/files/procd.sh
Outputs: tmp/L1-raw/procd/header_api-procd-api.md and .meta.json
Environment Variables: WORKDIR
Dependencies: lib.config, lib.extractor
Notes: Extracts the header block comments from the procd setup script.
"""

import os
import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, extractor
from lib.source_provenance import make_git_source_url, REPO_BASE_OPENWRT

sys.stdout.reconfigure(line_buffering=True)

OPENWRT_COMMIT = os.environ.get("OPENWRT_COMMIT", "unknown")

print("[02f] Scrape procd init.d API documentation")

procd_sh_path = os.path.join(config.WORKDIR, "repo-openwrt", "package", "system", "procd", "files", "procd.sh")

if not os.path.isfile(procd_sh_path):
    print(f"[02f] SKIP: procd.sh not found at {procd_sh_path}")
    sys.exit(0)

try:
    with open(procd_sh_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
except Exception as e:
    print(f"[02f] FAIL: Could not read {procd_sh_path}: {e}")
    sys.exit(1)

# FIX BUG-024: Scan entire file for comment blocks (not just header)
doc_lines = []
for line in lines:
    if line.strip().startswith("#"):
        # Keep it if it looks like documentation (more than 3 chars)
        cleaned = line.strip().lstrip("# ").strip()
        if cleaned:
            doc_lines.append(cleaned)
    elif doc_lines and not line.strip():
        # Keep empty lines between comment blocks
        doc_lines.append("")

markdown_content = "\n".join(doc_lines).strip()
if not markdown_content:
    print("[02f] FAIL: Could not extract documentation from procd.sh")
    sys.exit(1)

ts = datetime.datetime.now(datetime.UTC).isoformat()
slug = "procd-api"

final_content = "# procd init.d API Reference\n\n> **Extracted from:** `procd.sh` block comments\n\n"
final_content += extractor.wrap_code_block("procd.sh", markdown_content, "bash")

metadata = {
    "extractor": "02f-scrape-procd-api.py",
    "origin_type": "header_api",
    "module": "procd",
    "slug": slug,
    "source_url": make_git_source_url(REPO_BASE_OPENWRT, OPENWRT_COMMIT, "package/system/procd/files/procd.sh"),
    "source_locator": "package/system/procd/files/procd.sh",
    "source_commit": OPENWRT_COMMIT,
    "language": "bash",
    "fetch_status": "success",
    "extraction_timestamp": ts
}

extractor.write_l1_markdown("procd", "header_api", slug, final_content, metadata)

print(f"[02f] OK: Wrote {slug} ({len(doc_lines)} lines)")
print("[02f] Complete.")
