"""
Purpose: Scrape OpenWrt wiki pages to pure markdown format (L1 target).
Phase: Extraction
Layers: L0 -> L1
Inputs: https://openwrt.org/docs/
Outputs: tmp/L1-raw/wiki/*.md and tmp/L1-raw/wiki/*.meta.json
Environment Variables: WORKDIR, SKIP_WIKI, WIKI_MAX_PAGES
Dependencies: requests, pandoc (system binary), lib.config, lib.extractor
Notes: Enforces 1.5s delay to prevent bot rate-limits. Uses cache logic.
"""

import os
import re
import time
import datetime
import subprocess
import sys
import json

# Add project root to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, extractor

sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    print("[02a] FAIL: 'requests' package not installed")
    sys.exit(1)

if config.SKIP_WIKI:
    print("[02a] SKIP: Wiki scraping disabled (SKIP_WIKI=true)")
    sys.exit(0)

print("[02a] Scrape OpenWrt wiki (crawl namespace indexes, last 2 years)")

DELAY = 1.5
CUTOFF = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(days=730)

# Namespaces to crawl.
NAMESPACES = [
    ("/docs/techref/", "docs%3Atechref"),
    ("/docs/guide-developer/", "docs%3Aguide-developer"),
    ("/docs/guide-user/base-system/uci/", "docs%3Aguide-user%3Abase-system%3Auci"),
]

# Explicit pages that MUST be scraped regardless of age or index presence.
MANDATORY_PAGES = [
    "/docs/techref/ubus",
]

SKIP_PATTERNS = [
    "/toh/", "/inbox/", "/meta/", "/playground/", "changelog", "release_notes"
]

session = requests.Session()

CACHE_DIR = os.path.join(config.WORKDIR, ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "wiki-lastmod.json")

def load_cache():
    if not os.path.isfile(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}
    except Exception:
        return {}

    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f)

def path_to_filename(url_path):
    parts = url_path.strip("/").split("/")
    if parts and parts[0] == "docs":
        parts = parts[1:]
    if parts and parts[-1] == "start":
        parts = parts[:-1]
    slug = "-".join(p for p in parts if p)
    slug = re.sub(r"[^a-z0-9-]", "-", slug.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug if slug else "misc"

def fetch_page_lastmod(url):
    try:
        r = session.head(url, timeout=15, allow_redirects=True)
        lm = r.headers.get("Last-Modified")
        if lm:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(lm)
                return datetime.datetime(dt.year, dt.month, dt.day)
            except Exception:
                pass
    except Exception:
        pass
    return None

cache = load_cache()
discovered_pages = set(MANDATORY_PAGES)

for prefix, idx_param in NAMESPACES:
    index_url = f"https://openwrt.org{prefix}start?do=index&idx={idx_param}"
    print(f"[02a] Fetching namespace index: {prefix}")
    time.sleep(DELAY)
    try:
        resp = session.get(index_url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[02a] WARN: Could not fetch index for {prefix}: {e}")
        continue

    html = resp.text
    for m in re.finditer(r'href="([^"#?]*)"', html):
        href = m.group(1)
        path = None
        if href.startswith("https://openwrt.org"):
            path = href.replace("https://openwrt.org", "")
        elif href.startswith("/docs/"):
            path = href
        else:
            continue

        if not path.startswith(prefix): continue
        if path.rstrip("/").endswith("/start"): continue
        if any(pat in path for pat in SKIP_PATTERNS): continue
        if re.match(r'^/[a-z]{2}(-[a-z]+)?/', path): continue
        if "/_export/" in path or "/_detail/" in path or "/_media/" in path: continue
        discovered_pages.add(path)

if not discovered_pages:
    print("[02a] WARN: No wiki pages discovered.")
    sys.exit(1)

saved = 0
skipped_old = 0
skipped_unchanged = 0
skipped_short = 0 # FIX BUG-032
failed = 0

for path in sorted(discovered_pages):
    if saved >= config.WIKI_MAX_PAGES:
        print(f"[02a] WARN: Reached WIKI_MAX_PAGES={config.WIKI_MAX_PAGES} cap. Stopping.")
        break

    url = f"https://openwrt.org{path}"
    slug = path_to_filename(path)

    # time.sleep(DELAY) # BUG-039: Removed first delay
    last_mod = fetch_page_lastmod(url)

    if last_mod and last_mod < CUTOFF and path not in MANDATORY_PAGES:
        skipped_old += 1
        continue

    last_mod_str = last_mod.isoformat() if last_mod else "unknown"
    if cache.get(url) == last_mod_str and last_mod_str != "unknown":
        fpath = os.path.join(config.L1_RAW_WORKDIR, "wiki", f"wiki_page-{slug}.md")
        if os.path.exists(fpath):
            skipped_unchanged += 1
            continue

    time.sleep(DELAY)
    raw_url = f"{url}?do=export_raw"
    try:
        r = session.get(raw_url, timeout=20)
        r.raise_for_status()
        raw_content = r.text
    except Exception as e:
        print(f"[02a] FAIL: {path} ({e})")
        failed += 1
        continue

    # FIX BUG-017: Hardened HTML leak detection
    # Must have structural tags (<!DOCTYPE or <html) AND an error signature
    has_structural = "<!DOCTYPE" in raw_content or "<html" in raw_content
    html_error_signatures = [
        "404 Not Found", "Cloudflare", "Access Denied", 
        "Just a moment...", "Checking your browser", "Service Temporarily Unavailable",
        "Rate limit exceeded", "captcha", "This topic does not exist"
    ]
    has_signature = any(sig in raw_content for sig in html_error_signatures)
    
    if (has_structural and has_signature) or not raw_content.strip():
        print(f"[02a] WARN: HTML error signature or ghost page detected for {path}. Skipping.")
        failed += 1
        continue

    try:
        result = subprocess.run(
            ["pandoc", "-f", "dokuwiki", "-t", "gfm", "--wrap=none"],
            input=raw_content, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30
        )
        md = result.stdout or ""
        # FIX BUG-040: Check pandoc return code
        if result.returncode != 0:
            print(f"[02a] FAIL: pandoc failed for {path} (Exit {result.returncode})")
            failed += 1
            continue
    except Exception as e:
        print(f"[02a] FAIL: pandoc error for {path} ({e})")
        failed += 1
        continue

    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    if len(md) < 200:
        skipped_short += 1 # FIX BUG-032
        continue

    title_m = re.search(r"^#+ (.+)$", md, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else path.split("/")[-1]

    md = re.sub(r"^#+ .+\n\n?", "", md, count=1)
    
    final_content = f"# {title}\n\n{md}"

    metadata = {
        "extractor": "02a-scrape-wiki.py",
        "origin_type": "wiki_page",
        "module": "wiki",
        "slug": slug,
        "original_url": url,
        "language": "text",
        "fetch_status": "success",
        "extraction_timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    }

    extractor.write_l1_markdown("wiki", "wiki_page", slug, final_content, metadata)
    cache[url] = last_mod_str
    
    saved += 1
    print(f"[02a] OK: {slug} [{last_mod_str}] -- {title[:55]}")

save_cache(cache)
print(f"[02a] Complete: {saved} fetched, {skipped_unchanged} unchanged, {skipped_old} too old, {skipped_short} too short, {failed} failed.")
if saved == 0 and skipped_unchanged == 0:
    print("[02a] FAIL: Zero output files generated. Exiting with error.")
    sys.exit(1)
