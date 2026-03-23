"""
Purpose: Scrape OpenWrt wiki pages to pure markdown format (L1 target).
Phase: Extraction
Layers: L0 -> L1
Inputs: https://openwrt.org/docs/
Outputs: tmp/L1-raw/wiki/*.md and tmp/L1-raw/wiki/*.meta.json
Environment Variables: WORKDIR, SKIP_WIKI, WIKI_MAX_PAGES
Dependencies: requests, pandoc (system binary), lib.config, lib.extractor
Notes: Enforces 1.5s pacing, prefers conditional GETs over extra HEAD probes,
and can reuse cached wiki outputs when upstream or pandoc misbehaves.
"""

import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from email.utils import format_datetime, parsedate_to_datetime
from urllib.parse import unquote, urlparse

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add project root to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, extractor, source_exclusions

sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    print("[02a] FAIL: 'requests' package not installed")
    sys.exit(1)


BASE_URL = "https://openwrt.org"
DELAY = 1.5
MIN_MARKDOWN_LENGTH = 200
RAW_FETCH_TIMEOUT = 20
INDEX_FETCH_TIMEOUT = 30
PANDOC_TIMEOUT = 30
USER_AGENT = (
    "openwrt-docs4ai-v12-copilot/1.0 "
    "(+https://github.com/LuminairPrime/openwrt-docs4ai-v12-copilot)"
)
BASE_HOST = (urlparse(BASE_URL).hostname or "").lower()

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

HTML_ERROR_SIGNATURES = [
    "404 not found",
    "cloudflare",
    "access denied",
    "just a moment...",
    "checking your browser",
    "service temporarily unavailable",
    "rate limit exceeded",
    "captcha",
    "this topic does not exist",
    "testing to determine if you are a bot",
]


def log(level, message):
    print(f"[02a] {level}: {message}")


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/plain, text/html;q=0.9, */*;q=0.1",
    })

    retries = Retry(
        total=1,
        connect=1,
        read=1,
        status=1,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_cache_dir():
    return os.path.join(config.WORKDIR, ".cache")


def get_cache_file():
    return os.path.join(get_cache_dir(), "wiki-lastmod.json")


def sleep_with_rate_limit(reason):
    # The callsite keeps a reason argument so tests can stub this function without
    # changing the scraper flow, even though the production path just sleeps.
    _ = reason
    time.sleep(DELAY)


def path_to_filename(url_path):
    parts = url_path.strip("/").split("/")
    if parts and parts[0] == "docs":
        parts = parts[1:]
    if parts and parts[-1] == "start":
        parts = parts[:-1]
    slug = "-".join(part for part in parts if part)
    slug = re.sub(r"[^a-z0-9-]", "-", slug.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug if slug else "misc"


def output_paths(slug):
    out_dir = os.path.join(config.L1_RAW_WORKDIR, "wiki")
    base_name = f"wiki_page-{slug}"
    return (
        out_dir,
        os.path.join(out_dir, f"{base_name}.md"),
        os.path.join(out_dir, f"{base_name}.meta.json"),
    )


def parse_last_modified(header_value):
    if not header_value:
        return None
    try:
        parsed = parsedate_to_datetime(header_value)
    except Exception:
        return None

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(datetime.UTC).replace(tzinfo=None)
    return parsed


def normalize_cache_entry(url, value):
    if isinstance(value, str):
        return {
            "path": url.replace(BASE_URL, ""),
            "last_modified": value or "unknown",
            "last_modified_http": None,
            "raw_hash": None,
            "content_hash": None,
            "skip_reason": None,
        }

    if not isinstance(value, dict):
        return None

    last_modified_http = value.get("last_modified_http")
    last_modified = value.get("last_modified") or "unknown"
    if last_modified == "unknown" and last_modified_http:
        parsed = parse_last_modified(last_modified_http)
        if parsed is not None:
            last_modified = parsed.isoformat()

    return {
        "path": value.get("path") or url.replace(BASE_URL, ""),
        "last_modified": last_modified,
        "last_modified_http": last_modified_http,
        "raw_hash": value.get("raw_hash"),
        "content_hash": value.get("content_hash"),
        "skip_reason": value.get("skip_reason"),
    }


def load_cache(cache_file=None):
    cache_file = cache_file or get_cache_file()
    if not os.path.isfile(cache_file):
        return {}

    try:
        with open(cache_file, "r", encoding="utf-8") as handle:
            raw_cache = json.load(handle)
    except (json.JSONDecodeError, ValueError):
        log("WARN", f"Ignoring invalid wiki cache file: {cache_file}")
        return {}
    except Exception as exc:
        log("WARN", f"Unable to read wiki cache file {cache_file}: {exc}")
        return {}

    if not isinstance(raw_cache, dict):
        return {}

    normalized = {}
    for url, value in raw_cache.items():
        entry = normalize_cache_entry(url, value)
        if entry is not None:
            normalized[url] = entry
    return normalized


def save_cache(cache, cache_file=None):
    cache_file = cache_file or get_cache_file()
    cache_dir = os.path.dirname(cache_file)
    os.makedirs(cache_dir, exist_ok=True)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=cache_dir,
            prefix="wiki-lastmod-",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = handle.name
            json.dump(cache, handle, indent=2, sort_keys=True)
        os.replace(temp_path, cache_file)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def is_expected_openwrt_url(url):
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and (parsed.hostname or "").lower() == BASE_HOST


def normalize_wiki_href(href):
    if href.startswith("/docs/"):
        return unquote(href)
    if not href.startswith(("http://", "https://")):
        return None
    if not is_expected_openwrt_url(href):
        return None

    path = unquote(urlparse(href).path or "")
    return path if path.startswith("/docs/") else None


def get_existing_output_info(slug):
    _, md_path, meta_path = output_paths(slug)
    if not (os.path.isfile(md_path) and os.path.isfile(meta_path)):
        return None

    try:
        with open(meta_path, "r", encoding="utf-8") as handle:
            meta = json.load(handle)
        with open(md_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except Exception:
        return None

    computed_content_hash = content_hash_prefix(content)
    stored_content_hash = meta.get("content_hash") or computed_content_hash

    return {
        "md_path": md_path,
        "meta_path": meta_path,
        "content_hash": stored_content_hash,
        "computed_content_hash": computed_content_hash,
        "is_consistent": stored_content_hash == computed_content_hash,
    }


def remove_output(slug):
    _, md_path, meta_path = output_paths(slug)
    removed = False
    for path in (md_path, meta_path):
        if os.path.exists(path):
            os.remove(path)
            removed = True
    return removed


def compute_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_hash_prefix(text):
    return compute_hash(text)[:8]


def format_if_modified_since(cache_entry):
    if not cache_entry:
        return None

    header_value = cache_entry.get("last_modified_http")
    if header_value:
        return header_value

    last_modified = cache_entry.get("last_modified")
    if not last_modified or last_modified == "unknown":
        return None

    try:
        parsed = datetime.datetime.fromisoformat(last_modified)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.UTC)
    else:
        parsed = parsed.astimezone(datetime.UTC)
    return format_datetime(parsed, usegmt=True)


def is_html_error_page(text):
    lowered = text.lower()
    has_structural_html = "<!doctype" in lowered or "<html" in lowered
    has_error_signature = any(signature in lowered for signature in HTML_ERROR_SIGNATURES)
    return has_structural_html and has_error_signature


def fetch_namespace_index(session, prefix, idx_param):
    index_url = f"{BASE_URL}{prefix}start?do=index&idx={idx_param}"
    log("INFO", f"Fetching namespace index: {prefix}")
    sleep_with_rate_limit(f"namespace-index {prefix}")
    response = session.get(index_url, timeout=INDEX_FETCH_TIMEOUT)
    response.raise_for_status()
    return response.text


def discover_pages(session):
    discovered_pages = set(MANDATORY_PAGES)
    allow_cleanup = True

    for prefix, idx_param in NAMESPACES:
        try:
            html = fetch_namespace_index(session, prefix, idx_param)
        except Exception as exc:
            log("WARN", f"Could not fetch index for {prefix}: {exc}")
            allow_cleanup = False
            continue

        # Bot and error pages can still contain in-namespace links; never treat
        # them as trustworthy discovery input or as a safe basis for cleanup.
        if is_html_error_page(html):
            log("WARN", f"Namespace index for {prefix} appears to be a bot or error page.")
            allow_cleanup = False
            continue

        before = len(discovered_pages)
        for match in re.finditer(r'href=["\']([^"\'#?]+)["\']', html):
            href = match.group(1)
            path = normalize_wiki_href(href)
            if not path:
                continue

            if not path.startswith(prefix):
                continue
            if path.rstrip("/").endswith("/start"):
                continue
            if any(pattern in path for pattern in SKIP_PATTERNS):
                continue
            if re.match(r'^/[a-z]{2}(-[a-z]+)?/', path, re.IGNORECASE):
                continue
            if "/_export/" in path or "/_detail/" in path or "/_media/" in path:
                continue
            discovered_pages.add(path)

        added = len(discovered_pages) - before
        log("INFO", f"Discovered {added} pages from {prefix} ({len(discovered_pages)} total).")

    return discovered_pages, allow_cleanup


def fetch_raw_page(session, url, cache_entry=None):
    headers = {}
    if_modified_since = format_if_modified_since(cache_entry)
    if if_modified_since:
        headers["If-Modified-Since"] = if_modified_since

    raw_url = f"{url}?do=export_raw"
    response = session.get(raw_url, timeout=RAW_FETCH_TIMEOUT, headers=headers, allow_redirects=True)
    if response.status_code == 304:
        return {
            "status": "not_modified",
            "last_modified": cache_entry.get("last_modified") if cache_entry else "unknown",
            "last_modified_http": cache_entry.get("last_modified_http") if cache_entry else None,
        }

    response.raise_for_status()
    final_url = getattr(response, "url", None) or raw_url
    if not is_expected_openwrt_url(final_url):
        raise RuntimeError(f"Unexpected redirect target for wiki fetch: {final_url}")
    parsed_last_modified = parse_last_modified(response.headers.get("Last-Modified"))
    return {
        "status": "ok",
        "raw_content": response.text,
        "last_modified": parsed_last_modified.isoformat() if parsed_last_modified else "unknown",
        "last_modified_http": response.headers.get("Last-Modified"),
    }


def extract_title_from_dokuwiki(raw_content, path):
    for line in raw_content.splitlines():
        match = re.match(r'^\s*(={2,6})\s*(.*?)\s*\1\s*$', line)
        if match:
            title = match.group(2).strip()
            title = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', title)
            title = re.sub(r'\[\[([^\]]+)\]\]', r'\1', title)
            title = re.sub(r'[*/_`]+', '', title)
            return title.strip() or path.split("/")[-1]
    return path.split("/")[-1]


def build_fallback_markdown(path, raw_content):
    title = extract_title_from_dokuwiki(raw_content, path)
    body = raw_content
    body = re.sub(r'<(code|file)(?:\s+[^>]*)?>', '```', body, flags=re.IGNORECASE)
    body = re.sub(r'</(code|file)>', '```', body, flags=re.IGNORECASE)

    converted_lines = []
    title_removed = False
    for line in body.splitlines():
        match = re.match(r'^\s*(={2,6})\s*(.*?)\s*\1\s*$', line)
        if match:
            level = max(1, min(6, 7 - len(match.group(1))))
            heading_text = match.group(2).strip()
            heading_text = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', heading_text)
            heading_text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', heading_text)
            heading_text = re.sub(r'[*/_`]+', '', heading_text).strip()
            if not title_removed and heading_text == title:
                title_removed = True
                continue
            converted_lines.append(f"{'#' * level} {heading_text}".rstrip())
            continue
        converted_lines.append(line.rstrip())

    body = "\n".join(converted_lines).strip()
    body = re.sub(r'\n{3,}', '\n\n', body)
    return title, f"# {title}\n\n{body}".strip() + "\n"


def normalize_markdown_content(path, markdown):
    cleaned = re.sub(r'\n{3,}', '\n\n', markdown).strip()
    title_match = re.search(r'^#+\s+(.+)$', cleaned, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.split('/')[-1]
    cleaned = re.sub(r'^#+\s+.+\n\n?', '', cleaned, count=1)
    final_content = f"# {title}\n\n{cleaned}".strip() + "\n"
    return title, final_content


def convert_with_pandoc(raw_content, path):
    try:
        result = subprocess.run(
            ["pandoc", "-f", "dokuwiki", "-t", "gfm", "--wrap=none"],
            input=raw_content,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=PANDOC_TIMEOUT,
        )
    except Exception as exc:
        return None, f"pandoc exception for {path}: {exc}"

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        detail = f"Exit {result.returncode}"
        if stderr:
            detail = f"{detail}: {stderr.splitlines()[0][:180]}"
        return None, detail

    return result.stdout or "", None


def convert_raw_to_markdown(path, raw_content):
    markdown, error = convert_with_pandoc(raw_content, path)
    if markdown is not None:
        title, final_content = normalize_markdown_content(path, markdown)
        if len(final_content) >= MIN_MARKDOWN_LENGTH:
            return {
                "title": title,
                "content": final_content,
                "mode": "pandoc",
                "error": None,
            }

    fallback_title, fallback_content = build_fallback_markdown(path, raw_content)
    if len(fallback_content) >= MIN_MARKDOWN_LENGTH:
        return {
            "title": fallback_title,
            "content": fallback_content,
            "mode": "fallback-raw",
            "error": error,
        }

    if markdown is not None:
        title, final_content = normalize_markdown_content(path, markdown)
        return {
            "title": title,
            "content": final_content,
            "mode": "pandoc",
            "error": error,
        }

    return {
        "title": fallback_title,
        "content": fallback_content,
        "mode": "fallback-raw",
        "error": error,
    }


def write_page_output(slug, url, path, converted, last_modified, last_modified_http, raw_hash):
    metadata = {
        "extractor": "02a-scrape-wiki.py",
        "origin_type": "wiki_page",
        "module": "wiki",
        "slug": slug,
        "source_url": url,
        "language": "text",
        "fetch_status": "success",
        "conversion_mode": converted["mode"],
        "last_modified": last_modified,
        "last_modified_http": last_modified_http,
        "raw_hash": raw_hash,
        "source_path": path,
        "extraction_timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }
    extractor.write_l1_markdown("wiki", "wiki_page", slug, converted["content"], metadata)
    return content_hash_prefix(converted["content"])


def build_stats():
    return {
        "saved": 0,
        "skipped_old": 0,
        "skipped_unchanged": 0,
        "skipped_short": 0,
        "skipped_excluded": 0,
        "reused_cached": 0,
        "failed": 0,
    }


def get_cutoff_date():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(days=730)


def update_cache_entry(cache, url, path, last_modified, last_modified_http, raw_hash, content_hash, skip_reason=None):
    cache[url] = {
        "path": path,
        "last_modified": last_modified,
        "last_modified_http": last_modified_http,
        "raw_hash": raw_hash,
        "content_hash": content_hash,
        "skip_reason": skip_reason,
    }


def process_page(session, path, cache, stats, cutoff):
    url = f"{BASE_URL}{path}"
    slug = path_to_filename(path)
    reason = source_exclusions.get_exclusion_reason("wiki", slug)
    if reason is not None:
        stats["skipped_excluded"] += 1
        log("INFO", f"Excluding wiki page {slug}: {reason}")
        return "skipped_excluded"
    cache_entry = cache.get(url)
    existing_output = get_existing_output_info(slug)
    if existing_output and not existing_output["is_consistent"]:
        log("WARN", f"Discarding inconsistent cached wiki output for {slug}; metadata hash does not match markdown content.")
        remove_output(slug)
        existing_output = None

    sleep_with_rate_limit(f"raw-export {path}")
    try:
        fetch_result = fetch_raw_page(session, url, cache_entry)
    except Exception as exc:
        if existing_output:
            stats["reused_cached"] += 1
            log("WARN", f"Reusing cached wiki page {slug} after fetch failure: {exc}")
            return "reused_cached"
        stats["failed"] += 1
        log("FAIL", f"{path} ({exc})")
        return "failed"

    if fetch_result["status"] == "not_modified":
        if existing_output:
            stats["skipped_unchanged"] += 1
            log("INFO", f"Cache hit for {slug}: upstream returned 304 Not Modified.")
            return "skipped_unchanged"

        log("WARN", f"Received 304 for {slug} but cached files were missing. Refetching without validators.")
        try:
            fetch_result = fetch_raw_page(session, url, None)
        except Exception as exc:
            stats["failed"] += 1
            log("FAIL", f"{path} ({exc})")
            return "failed"

    raw_content = fetch_result["raw_content"]
    if is_html_error_page(raw_content):
        if existing_output:
            stats["reused_cached"] += 1
            log("WARN", f"Reusing cached wiki page {slug} after HTML error page detection.")
            return "reused_cached"
        stats["failed"] += 1
        log("WARN", f"HTML error signature or ghost page detected for {path}. Skipping.")
        return "failed"

    raw_hash = compute_hash(raw_content)
    last_modified = fetch_result["last_modified"]
    effective_last_modified = last_modified
    if effective_last_modified == "unknown" and cache_entry:
        effective_last_modified = cache_entry.get("last_modified", "unknown")
    effective_last_modified_http = fetch_result["last_modified_http"]
    if effective_last_modified_http is None and cache_entry:
        effective_last_modified_http = cache_entry.get("last_modified_http")

    parsed_last_modified = None
    if effective_last_modified != "unknown":
        try:
            parsed_last_modified = datetime.datetime.fromisoformat(effective_last_modified)
        except ValueError:
            parsed_last_modified = None

    if parsed_last_modified is not None and parsed_last_modified < cutoff and path not in MANDATORY_PAGES:
        if remove_output(slug):
            log("INFO", f"Removed cached output for old wiki page {slug}.")
        update_cache_entry(
            cache,
            url,
            path,
            effective_last_modified,
            effective_last_modified_http,
            raw_hash,
            existing_output["computed_content_hash"] if existing_output else None,
        )
        stats["skipped_old"] += 1
        return "skipped_old"

    if cache_entry and cache_entry.get("raw_hash") == raw_hash and cache_entry.get("skip_reason") == "short":
        update_cache_entry(
            cache,
            url,
            path,
            effective_last_modified,
            effective_last_modified_http,
            raw_hash,
            None,
            skip_reason="short",
        )
        stats["skipped_short"] += 1
        log("INFO", f"Cache hit for {slug}: raw wiki source still resolves to a short page.")
        return "skipped_short"

    if cache_entry and cache_entry.get("raw_hash") == raw_hash and existing_output:
        update_cache_entry(
            cache,
            url,
            path,
            effective_last_modified,
            effective_last_modified_http,
            raw_hash,
            existing_output["computed_content_hash"],
        )
        stats["skipped_unchanged"] += 1
        log("INFO", f"Cache hit for {slug}: raw wiki source hash unchanged.")
        return "skipped_unchanged"

    last_modified = effective_last_modified
    converted = convert_raw_to_markdown(path, raw_content)
    if converted["error"] and converted["mode"] == "fallback-raw":
        log("WARN", f"Pandoc failed for {path}; using raw wiki fallback. {converted['error']}")

    if len(converted["content"]) < MIN_MARKDOWN_LENGTH:
        if existing_output:
            stats["reused_cached"] += 1
            log("WARN", f"Reusing cached wiki page {slug} after short conversion result ({len(converted['content'])} chars).")
            return "reused_cached"
        update_cache_entry(
            cache,
            url,
            path,
            last_modified,
            effective_last_modified_http,
            raw_hash,
            None,
            skip_reason="short",
        )
        stats["skipped_short"] += 1
        log("INFO", f"Skipping short wiki page {slug} ({len(converted['content'])} chars).")
        return "skipped_short"

    content_hash = write_page_output(
        slug,
        url,
        path,
        converted,
        last_modified,
        effective_last_modified_http,
        raw_hash,
    )
    update_cache_entry(
        cache,
        url,
        path,
        last_modified,
        effective_last_modified_http,
        raw_hash,
        content_hash,
        skip_reason=None,
    )

    stats["saved"] += 1
    log("OK", f"{slug} [{last_modified}] -- {converted['title'][:55]}")
    return "saved"


def cleanup_orphaned_outputs(discovered_paths, cache, hit_cap):
    if hit_cap:
        return 0

    out_dir = os.path.join(config.L1_RAW_WORKDIR, "wiki")
    discovered_urls = {f"{BASE_URL}{path}" for path in discovered_paths}
    if not os.path.isdir(out_dir):
        stale_urls = [url for url in list(cache) if url not in discovered_urls]
        for url in stale_urls:
            del cache[url]
        return 0

    discovered_slugs = {path_to_filename(path) for path in discovered_paths}
    removed = 0

    for name in os.listdir(out_dir):
        if not name.startswith("wiki_page-"):
            continue
        if name.endswith(".meta.json"):
            slug = name[len("wiki_page-"):-len(".meta.json")]
        elif name.endswith(".md"):
            slug = name[len("wiki_page-"):-len(".md")]
        else:
            continue

        if slug in discovered_slugs:
            continue
        if remove_output(slug):
            removed += 1

    stale_urls = [url for url in list(cache) if url not in discovered_urls]
    for url in stale_urls:
        del cache[url]
    return removed


def main():
    if config.SKIP_WIKI:
        print("[02a] SKIP: Wiki scraping disabled (SKIP_WIKI=true)")
        return 0

    print("[02a] Scrape OpenWrt wiki (crawl namespace indexes, last 2 years)")
    config.ensure_dirs()
    os.makedirs(get_cache_dir(), exist_ok=True)
    session = create_session()
    cache = load_cache()
    cutoff = get_cutoff_date()

    try:
        discovered_pages, allow_cleanup = discover_pages(session)
        if not discovered_pages:
            log("WARN", "No wiki pages discovered.")
            return 1

        stats = build_stats()
        hit_cap = False

        for page_path in sorted(discovered_pages):
            if stats["saved"] >= config.WIKI_MAX_PAGES:
                hit_cap = True
                log("WARN", f"Reached WIKI_MAX_PAGES={config.WIKI_MAX_PAGES} cap. Stopping.")
                break
            process_page(session, page_path, cache, stats, cutoff)

        if allow_cleanup:
            removed = cleanup_orphaned_outputs(discovered_pages, cache, hit_cap)
            if removed:
                log("INFO", f"Removed {removed} stale cached wiki outputs not present in current discovery set.")
        else:
            log("INFO", "Skipping stale-cache cleanup because namespace discovery was incomplete.")

        save_cache(cache)
        print(
            f"[02a] Complete: {stats['saved']} fetched, {stats['skipped_unchanged']} unchanged, "
            f"{stats['skipped_old']} too old, {stats['skipped_short']} too short, "
            f"{stats['skipped_excluded']} excluded, "
            f"{stats['reused_cached']} reused-cache, {stats['failed']} failed."
        )
        if stats["saved"] == 0 and stats["skipped_unchanged"] == 0 and stats["reused_cached"] == 0:
            print("[02a] FAIL: Zero output files generated. Exiting with error.")
            return 1
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
