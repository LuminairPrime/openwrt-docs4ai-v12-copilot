"""
Purpose: Extract package documentation from the OpenWrt buildroot source tree.
Phase: Extraction
Layers: L0 -> L1
Inputs: tmp/repo-openwrt/package/ and include/
Outputs: tmp/L1-raw/openwrt-core/*.md and .meta.json
Environment Variables: WORKDIR, SKIP_BUILDROOT
Dependencies: lib.config, lib.extractor
Notes: Parses PKG_* variables from Makefiles and extracts READMEs.
"""

import os
import re
import glob
import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config, extractor
from lib.source_provenance import make_git_source_url, REPO_BASE_OPENWRT

sys.stdout.reconfigure(line_buffering=True)

OPENWRT_COMMIT = os.environ.get("OPENWRT_COMMIT", "unknown")
SKIP_BUILDROOT = os.environ.get("SKIP_BUILDROOT", "false").lower() == "true"

if SKIP_BUILDROOT:
    print("[02d] SKIP: Package metadata extraction (SKIP_BUILDROOT=true)")
    sys.exit(0)

print("[02d] Extract OpenWrt core package documentation")

REPO = os.path.join(config.WORKDIR, "repo-openwrt")
TS = datetime.datetime.now(datetime.UTC).isoformat()
REPO_URL = "https://github.com/openwrt/openwrt"

if not os.path.isdir(REPO):
    print("[02d] FAIL: Buildroot repo not found")
    sys.exit(1)


def extract_makefile_meta(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception:
        return {}
    fields = {}
    for key in ["PKG_NAME", "PKG_VERSION", "PKG_SOURCE_URL", "PKG_MAINTAINER", "PKG_LICENSE"]:
        m = re.search(rf"^{key}\s*[?:+]?=\s*(.+?)(?=\n[A-Z_]|\Z)", text, re.MULTILINE | re.DOTALL)
        if m:
            val = re.sub(r"\s+", " ", m.group(1).replace("\\\n", " ")).strip()
            if val and not val.startswith("$("):
                fields[key] = val[:200]

    m = re.search(r"^PKG_DESCRIPTION\s*[?:+]?=\s*(.+?)(?=\n[A-Z]|\Z)", text, re.MULTILINE | re.DOTALL)
    if m:
        fields["DESCRIPTION"] = re.sub(r"\s+", " ", m.group(1).replace("\\\n", " ")).strip()[:500]

    block_m = re.search(r"define Package/[^\n]+\n(.*?)^endef", text, re.MULTILINE | re.DOTALL)
    if block_m:
        block = block_m.group(1)
        d = re.search(r"DESCRIPTION\s*:?=\s*(.+?)(?=\n\s*[A-Z]|\Z)", block, re.DOTALL)
        if d:
            desc = re.sub(r"\s+", " ", d.group(1).replace("\\\n", " ")).strip()
            if desc:
                fields.setdefault("DESCRIPTION", desc[:500])

    # FIX BUG-013: Support for 'define Package/foo/description' blocks
    desc_block_m = re.search(r"define Package/[^/]+/description\s*\n(.*?)^endef", text, re.MULTILINE | re.DOTALL)
    if desc_block_m:
        desc = re.sub(r"\s+", " ", desc_block_m.group(1).replace("\\\n", " ")).strip()
        if desc:
            fields.setdefault("DESCRIPTION", desc[:1000])  # Descriptions can be longer

    return fields


def extract_readme(pkg_dir):
    for name in ["README.md", "README", "README.txt"]:
        p = os.path.join(pkg_dir, name)
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                if len(content) > 50:
                    return content
            except Exception:
                pass
    return None


total_pkgs = 0
outputs_generated = 0

for cat_path in sorted(glob.glob(os.path.join(REPO, "package", "*"))):
    if not os.path.isdir(cat_path):
        continue
    category = os.path.basename(cat_path)
    entries = []

    for pkg_path in sorted(glob.glob(os.path.join(cat_path, "*"))):
        if not os.path.isdir(pkg_path):
            continue
        pkg_name = os.path.basename(pkg_path)
        meta = extract_makefile_meta(os.path.join(pkg_path, "Makefile"))
        readme = extract_readme(pkg_path)
        if not meta and not readme:
            continue
        entries.append({"name": pkg_name, "meta": meta, "readme": readme})

    if not entries:
        continue

    total_pkgs += len(entries)
    cat_src_url = f"{REPO_URL}/tree/master/package/{category}"
    slug = f"category-{category}"

    content_lines = []
    content_lines.append(f"# OpenWrt Buildroot: {category} packages\n")
    content_lines.append(f"> **Source:** {cat_src_url}\n---\n")

    for e in entries:
        m = e["meta"]
        content_lines.append(f"## {e['name']}\n")
        if m.get("DESCRIPTION"):
            content_lines.append(f"{m['DESCRIPTION']}\n")
        rows = []
        if m.get("PKG_VERSION"):
            rows.append(f"| Version | {m['PKG_VERSION']} |")
        if m.get("PKG_LICENSE"):
            rows.append(f"| License | {m['PKG_LICENSE']} |")
        if m.get("PKG_MAINTAINER"):
            rows.append(f"| Maintainer | {m['PKG_MAINTAINER']} |")
        if m.get("PKG_SOURCE_URL"):
            rows.append(f"| Source URL | {m['PKG_SOURCE_URL'][:120]} |")
        if rows:
            content_lines.append("| Field | Value |\n|---|---|\n" + "\n".join(rows) + "\n")
        if e["readme"]:
            content = e["readme"]
            truncated = len(content) > 2000
            content_lines.append("**README:**\n")
            content_lines.append(extractor.wrap_code_block("README", content[:2000], "markdown"))
            if truncated:
                pkg_url = f"{REPO_URL}/tree/master/package/{category}/{e['name']}"
                content_lines.append(f"\n> *(README truncated — [view full file]({pkg_url}))*\n")
        pkg_url = f"{REPO_URL}/tree/master/package/{category}/{e['name']}"
        content_lines.append(f"\n> Source: {pkg_url}\n---\n")

    metadata = {
        "extractor": "02d-scrape-core-packages.py",
        "origin_type": "makefile_meta",
        "module": "openwrt-core",
        "slug": slug,
        "source_url": make_git_source_url(REPO_BASE_OPENWRT, OPENWRT_COMMIT, f"package/{category}"),
        "source_locator": f"package/{category}",
        "source_commit": OPENWRT_COMMIT,
        "language": "makefile",
        "fetch_status": "success",
        "extraction_timestamp": TS,
    }

    extractor.write_l1_markdown("openwrt-core", "makefile_meta", slug, "\n".join(content_lines), metadata)
    outputs_generated += 1
    print(f"[02d] OK: {category} ({len(entries)} packages)")

# --- Process build system include files ---
mk_entries = []
for mk_file in sorted(glob.glob(os.path.join(REPO, "include", "*.mk"))):
    try:
        with open(mk_file, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception:
        continue
    fname_mk = os.path.basename(mk_file)
    comments = []
    for line in text.splitlines()[:100]:
        if line.startswith("#"):
            cleaned = line.lstrip("# ").strip()
            if cleaned:
                comments.append(cleaned)
        elif comments:
            break
    if len(comments) >= 2:
        mk_entries.append((fname_mk, "\n".join(comments)))

if mk_entries:
    slug = "include-mk"
    content_lines = []
    content_lines.append("# OpenWrt Buildroot: Build System Include Files\n")
    content_lines.append(f"> **Source:** {REPO_URL}/tree/master/include\n")
    content_lines.append("Core build system Makefile fragments.\n\n---\n")
    for fname_mk, doc in mk_entries:
        content_lines.append(f"## {fname_mk}\n")
        content_lines.append(extractor.wrap_code_block("Documentation", doc, "text"))
        content_lines.append(f"\n> Source: {REPO_URL}/blob/master/include/{fname_mk}\n---\n")

    metadata = {
        "extractor": "02d-scrape-core-packages.py",
        "origin_type": "makefile_meta",
        "module": "openwrt-core",
        "slug": slug,
        "source_url": make_git_source_url(REPO_BASE_OPENWRT, OPENWRT_COMMIT, "include/"),
        "source_locator": "include/",
        "source_commit": OPENWRT_COMMIT,
        "language": "makefile",
    }
    extractor.write_l1_markdown("openwrt-core", "makefile_meta", slug, "\n".join(content_lines), metadata)
    outputs_generated += 1
    print(f"[02d] OK: include-mk ({len(mk_entries)} documented)")

print(f"[02d] Complete: {total_pkgs} packages across {outputs_generated} outputs.")
if outputs_generated == 0:
    print("[02d] FAIL: Zero output files generated. Exiting with error.")
    sys.exit(1)
