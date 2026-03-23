"""
Purpose: Ingest hand-authored cookbook content into L1-raw.
Phase: Collection
Layers: content/cookbook-source/ -> L1-raw/cookbook/
Inputs: content/cookbook-source/*.md (YAML frontmatter required)
Outputs: L1-raw/cookbook/*.md, L1-raw/cookbook/*.meta.json
Dependencies: lib.config, pyyaml
Notes: Derives topic_slug from filename. Fails fast if required authored
       metadata fields are missing. Does not write source_commit or source_url
       — cookbook content has no upstream git source.
"""

import json
import os
import sys

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

COOKBOOK_SOURCE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "content", "cookbook-source"
)

REQUIRED_AUTHORED_FIELDS = [
    "title",
    "description",
    "module",
    "origin_type",
    "when_to_use",
    "related_modules",
    "era_status",
    "verification_basis",
    "reviewed_by",
    "last_reviewed",
]

print("[02i] Ingest hand-authored cookbook content")

source_dir = os.path.abspath(COOKBOOK_SOURCE_DIR)
if not os.path.isdir(source_dir):
    print(f"[02i] FAIL: cookbook source directory not found: {source_dir}")
    sys.exit(1)

out_dir = os.path.join(config.WORKDIR, "L1-raw", "cookbook")
os.makedirs(out_dir, exist_ok=True)

source_files = sorted(
    f for f in os.listdir(source_dir) if f.endswith(".md")
)

# Skip non-cookbook helper files (era evidence tracker, etc.)
SKIP_FILES = {"era-guide-evidence-needed.md"}
source_files = [f for f in source_files if f not in SKIP_FILES]

if not source_files:
    print("[02i] FAIL: No cookbook source files found in content/cookbook-source/")
    sys.exit(1)

processed = 0

for filename in source_files:
    filepath = os.path.join(source_dir, filename)
    with open(filepath, "r", encoding="utf-8") as fh:
        raw = fh.read()

    if not raw.startswith("---"):
        print(f"[02i] FAIL: missing YAML frontmatter in {filename}")
        sys.exit(1)

    parts = raw.split("---", 2)
    if len(parts) < 3:
        print(f"[02i] FAIL: malformed YAML frontmatter in {filename}")
        sys.exit(1)

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        print(f"[02i] FAIL: YAML parse error in {filename}: {exc}")
        sys.exit(1)

    missing = [f for f in REQUIRED_AUTHORED_FIELDS if not fm.get(f)]
    if missing:
        print(f"[02i] FAIL: {filename} missing required fields: {', '.join(missing)}")
        sys.exit(1)

    if fm.get("module") != "cookbook":
        print(f"[02i] FAIL: {filename} has module={fm.get('module')!r}, expected 'cookbook'")
        sys.exit(1)

    if fm.get("origin_type") != "authored":
        print(f"[02i] FAIL: {filename} has origin_type={fm.get('origin_type')!r}, expected 'authored'")
        sys.exit(1)

    topic_slug = filename[:-3]  # strip .md
    body = parts[2].lstrip("\n")

    # Write L1 markdown body (without frontmatter)
    out_md = os.path.join(out_dir, filename)
    with open(out_md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)

    # Build L1 sidecar — universal contract; no source_commit or source_url
    sidecar = {
        "module": "cookbook",
        "origin_type": "authored",
        "slug": topic_slug,
        "source_locator": f"content/cookbook-source/{filename}",
        "title": fm["title"],
        "description": fm["description"],
        "when_to_use": fm["when_to_use"],
        "related_modules": fm["related_modules"],
        "era_status": fm["era_status"],
        "verification_basis": fm["verification_basis"],
        "reviewed_by": fm["reviewed_by"],
        "last_reviewed": str(fm["last_reviewed"]),
    }

    out_meta = os.path.join(out_dir, f"{topic_slug}.meta.json")
    with open(out_meta, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sidecar, fh, indent=2)
        fh.write("\n")

    print(f"[02i] OK: {filename} -> L1-raw/cookbook/")
    processed += 1

print(f"[02i] Done: {processed} cookbook file(s) ingested")
