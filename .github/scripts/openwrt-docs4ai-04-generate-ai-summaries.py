"""
Purpose: Apply AI summaries to L2 documentation from the structured data store
         and optionally generate new summaries via GitHub Models API.
Phase: AI Enrichment (Optional)
Layers: L2 -> L2 (In-place frontmatter mutation)
Inputs:  - OUTDIR/L2-semantic/                          (required L2 source)
         - data/base/{module}/{slug}.json               (base data store)
         - data/override/{module}/{slug}.json           (override data store)
         - ai-summaries-cache.json                      (legacy; migrated on run)
Outputs: - OUTDIR/L2-semantic/{module}/*.md             (mutated: ai fields added)
         - data/base/{module}/{slug}.json               (new entries when WRITE_AI)
Environment Variables:
  SKIP_AI          Skip entire step cleanly. Default: false.
  WRITE_AI         Call API for files missing summaries. Default: true.
  MAX_AI_FILES     Cap on API calls per run. Default: 40.
  GITHUB_TOKEN     GitHub Models API bearer token.
  LOCAL_DEV_TOKEN  Local development token (fallback when GITHUB_TOKEN absent).
    AI_CACHE_PATH    Optional override for legacy ai-summaries-cache.json path.
  AI_DATA_BASE_DIR    Override default data/base/ location.
  AI_DATA_OVERRIDE_DIR Override default data/override/ location.
  AI_VALIDATE_PAYLOAD  Validate AI payloads before injection. Default: true.
                       Set to false only when debugging malformed API responses locally.
Dependencies: requests, pyyaml, lib.config, lib.ai_store

=========================== MANUAL AI GENERATION PROMPT ===========================
Use this block to generate a data/base/{module}/{slug}.json file manually.
Paste an L2 file below the divider line, run the prompt in any capable LLM
(GitHub Copilot Chat, Claude, ChatGPT, etc.), then copy the JSON output into
data/base/{module}/{slug}.json.

## Task: openwrt-docs4ai AI Summary Generation

Generate a structured AI summary record for an OpenWrt documentation file.

### Output format
Return ONLY a valid JSON object with exactly these fields:
{
  "slug":              "<L2 filename without .md extension>",
  "module":            "<parent folder: ucode|luci|procd|uci|wiki|...>",
  "title":             "<value of the 'title' YAML field in the file>",
  "content_hash":      null,
    "ai_summary":        "<3-5 sentences. Sentence 1 is comprehensive; remaining sentences provide details/clarifications and name exact functions.>",
  "ai_when_to_use":    "<1-2 sentences: when is this the right tool in OpenWrt?>",
  "ai_related_topics": ["<exact symbol name found in the text>", "..."],
  "generated_at":      "<ISO 8601 timestamp>",
  "model":             "manual",
  "pipeline_version":  "v12"
}

### Rules
- ai_summary sentence 1 must be a comprehensive one-sentence overview of the entire page.
- ai_summary sentences 2+ must add details/clarifications and name exact symbols present in the body.
- Prefer 3-5 sentences unless the source page is extremely short.
- ai_related_topics must contain 4-10 exact symbol names present in the content.
- content_hash must be null (marks this as human-authored, never auto-invalidated).
- Do NOT include any text outside the JSON object.
- Do NOT hallucinate symbols not present in the provided content.

[PASTE L2 FILE CONTENT BELOW THIS LINE]
====================================================================================
"""

import hashlib
import json
import os
import re
import sys
import time
from typing import Any, Literal, TypedDict, cast

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config, ai_store

cast(Any, sys.stdout).reconfigure(line_buffering=True)

OUTDIR = config.OUTDIR
SKIP_AI = os.environ.get("SKIP_AI", "false").lower() == "true"
WRITE_AI = os.environ.get("WRITE_AI", "true").lower() == "true"
MAX_FILES = int(os.environ.get("MAX_AI_FILES", "40"))
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("LOCAL_DEV_TOKEN")
VALIDATE_PAYLOAD = os.environ.get("AI_VALIDATE_PAYLOAD", "true").lower() != "false"

# Legacy flat cache — migrated opportunistically on first run that encounters it
_LEGACY_CACHE_PATH = os.path.abspath(
    os.environ.get(
        "AI_CACHE_PATH",
        os.path.join(os.path.dirname(__file__), "..", "..", "ai-summaries-cache.json"),
    )
)

API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL = "gpt-4o-mini"


class SummaryPayload(TypedDict):
    summary: str
    when_to_use: str
    related_topics: list[str]

SYSTEM_PROMPT = (
    "You are a technical documentation assistant for OpenWrt — a Linux-based "
    "operating system for embedded network devices. You write clear, accurate, "
    "developer-focused descriptions.\n\n"
    "Given an API/module doc as context, produce a JSON object with exactly:\n"
    '  "summary":       "<3-5 sentences. Sentence 1 is comprehensive. Sentences 2-5 add concrete details and clarifications with exact functions.>"\n'
    '  "when_to_use":   "<1-2 sentences: specific OpenWrt use case.>"\n'
    '  "related_topics": ["<exact symbol name found in text>", ...]\n\n'
    "Follow spelling/naming in the text exactly. Do not invent symbols."
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _body_hash(body_text: str) -> str:
    return hashlib.sha256(body_text.encode("utf-8")).hexdigest()[:12]


def _split_frontmatter(content: str) -> tuple[str | None, str | None]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)", content, re.DOTALL)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2)


def _coerce_related_topics(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    out: list[str] = []
    for item in cast(list[Any], value):
        topic = str(item).strip()
        if topic:
            out.append(topic)
    return out


_UNSAFE_PAYLOAD_RE = re.compile(
    r"<script\b|javascript:|data:text/html|[\x00-\x08\x0b\x0c\x0e-\x1f]",
    re.IGNORECASE,
)


def _validate_payload(payload: SummaryPayload, label: str) -> bool:
    """Light safety/sanity check before injecting an AI payload into L2 frontmatter.

    Rejects payloads that are empty, suspiciously short, or contain characters or
    patterns that should never appear in documentation text (e.g. script injection,
    binary control characters). Does not reject for style or length opinions beyond
    a very low minimum bar.
    """
    summary = payload.get("summary", "").strip()
    when_to_use = payload.get("when_to_use", "").strip()

    if not summary or not when_to_use:
        print(f"[04] WARN: Rejecting empty AI payload for {label}")
        return False

    if len(summary) < 20:
        print(f"[04] WARN: Rejecting too-short summary for {label} (len={len(summary)})")
        return False

    for field_name, field_val in (("summary", summary), ("when_to_use", when_to_use)):
        if _UNSAFE_PAYLOAD_RE.search(field_val):
            print(f"[04] WARN: Unsafe content in {field_name} for {label}; skipping injection")
            return False

    return True


def _load_legacy_cache() -> dict[str, dict[str, Any]]:
    if not os.path.isfile(_LEGACY_CACHE_PATH):
        return {}
    try:
        with open(_LEGACY_CACHE_PATH, "r", encoding="utf-8") as fh:
            loaded: Any = json.load(fh)

        if not isinstance(loaded, dict):
            return {}

        normalized: dict[str, dict[str, Any]] = {}
        for key_any, val_any in cast(dict[Any, Any], loaded).items():
            if isinstance(key_any, str) and isinstance(val_any, dict):
                normalized[key_any] = cast(dict[str, Any], val_any)
        return normalized
    except Exception as exc:
        print(f"[04] WARN: Could not read legacy cache: {exc}")
        return {}


def _call_api(content: str, label: str) -> SummaryPayload | Literal["STOP"] | None:
    """Call GitHub Models API. Returns parsed dict, 'STOP', or None."""
    try:
        import requests as _req
    except ImportError:
        print("[04] FAIL: 'requests' package not installed")
        return None

    headers: dict[str, str] = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Summarize this OpenWrt API module:\n\n{content[:4000]}",
            },
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": 500,
    }

    for attempt in range(3):
        try:
            resp: Any = _req.post(API_URL, json=payload, headers=headers, timeout=60)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 30))
                print(f"[04] Rate-limited; waiting {wait}s...")
                time.sleep(wait)
                continue

            if resp.status_code in (401, 403) or any(
                kw in resp.text.lower() for kw in ("no quota", "limit reached")
            ):
                print(
                    f"[04] API quota/auth failure (HTTP {resp.status_code}); "
                    "halting API calls for this run."
                )
                return "STOP"

            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            # Strip markdown fences the model sometimes wraps its output in
            raw = re.sub(
                r"^```(?:json)?\n?|(?:^|\n)```$", "", raw.strip(), flags=re.MULTILINE
            )
            parsed_any: Any = json.loads(raw)
            if not isinstance(parsed_any, dict):
                print(f"[04] WARN: API returned non-object JSON for {label}")
                return None

            parsed = cast(dict[str, Any], parsed_any)
            summary = str(parsed.get("summary", "")).replace("\n", " ").strip()
            when_to_use = str(parsed.get("when_to_use", "")).replace("\n", " ").strip()
            related_topics = _coerce_related_topics(parsed.get("related_topics", []))

            return {
                "summary": summary,
                "when_to_use": when_to_use,
                "related_topics": related_topics,
            }

        except Exception as exc:
            print(f"[04] WARN: API error for {label} (attempt {attempt + 1}): {exc}")
            time.sleep(5)

    return None


# ── Early exit ────────────────────────────────────────────────────────────────

if SKIP_AI:
    print("[04] SKIP: AI summarization disabled (SKIP_AI=true)")
    sys.exit(0)

print("[04] AI summary enrichment starting")
if not WRITE_AI:
    print("[04] INFO: WRITE_AI=false — applying stored summaries only, no API calls")

# ── Legacy cache migration (opportunistic) ────────────────────────────────────

legacy_cache = _load_legacy_cache()
if legacy_cache:
    print(
        f"[04] Legacy cache loaded: {len(legacy_cache)} hash-keyed entries "
        "available for migration"
    )

# ── Discover L2 targets ───────────────────────────────────────────────────────

l2_dir = os.path.join(OUTDIR, "L2-semantic")
if not os.path.isdir(l2_dir):
    print(f"[04] FAIL: L2 directory not found: {l2_dir}")
    sys.exit(1)

all_targets: list[tuple[str, str, str]] = []
for module in sorted(os.listdir(l2_dir)):
    mod_dir = os.path.join(l2_dir, module)
    if not os.path.isdir(mod_dir):
        continue
    for fname in sorted(os.listdir(mod_dir)):
        if fname.endswith(".md"):
            all_targets.append((module, fname[:-3], os.path.join(mod_dir, fname)))

print(f"[04] Found {len(all_targets)} L2 documents")

# ── Counters ──────────────────────────────────────────────────────────────────

applied = 0
skipped_already = 0
skipped_short = 0
migrated_from_legacy = 0
generated_via_api = 0
stale_applied = 0
api_stopped = False
api_calls_made = 0

# ── Process ───────────────────────────────────────────────────────────────────

try:
    import yaml as _yaml
except ImportError:
    print("[04] FAIL: 'pyyaml' package not installed")
    sys.exit(1)

for module, slug, fpath in all_targets:
    try:
        with open(fpath, encoding="utf-8") as fh:
            full_content = fh.read()
    except Exception as exc:
        print(f"[04] WARN: Cannot read {fpath}: {exc}")
        continue

    fm_text, body = _split_frontmatter(full_content)
    if fm_text is None or body is None:
        print(f"[04] WARN: Skipping {slug} — no valid L2 frontmatter")
        continue

    # Already enriched: skip
    if "ai_summary:" in fm_text:
        skipped_already += 1
        continue

    # Too short to summarize
    if len(body.split()) < 15:
        skipped_short += 1
        continue

    body_hash = _body_hash(body)
    result: SummaryPayload | None = None

    # 1. Structured data store (override takes precedence over base)
    status, record = ai_store.load_summary(module, slug, current_hash=body_hash)

    if status == "ok" and record:
        result = {
            "summary": str(record.get("ai_summary", "")),
            "when_to_use": str(record.get("ai_when_to_use", "")),
            "related_topics": _coerce_related_topics(record.get("ai_related_topics", [])),
        }
    elif status == "stale" and record:
        stored_hash = record.get("content_hash", "?")
        print(
            f"[04] STALE: {module}/{slug} "
            f"(stored={stored_hash} current={body_hash})"
        )
        # Use stale data rather than leaving the file unenriched, unless we
        # can regenerate it below.
        if not WRITE_AI or not TOKEN:
            result = {
                "summary": str(record.get("ai_summary", "")),
                "when_to_use": str(record.get("ai_when_to_use", "")),
                "related_topics": _coerce_related_topics(record.get("ai_related_topics", [])),
            }
            stale_applied += 1

    # 2. Legacy hash-keyed cache (migrate to structured store on hit)
    if result is None and body_hash in legacy_cache:
        legacy_entry = legacy_cache[body_hash]
        result = {
            "summary": str(legacy_entry.get("summary", "")),
            "when_to_use": str(legacy_entry.get("when_to_use", "")),
            "related_topics": _coerce_related_topics(legacy_entry.get("related_topics", [])),
        }
        ai_store.save_summary(
            module,
            slug,
            {
                "slug": slug,
                "module": module,
                "title": slug,
                "content_hash": body_hash,
                "ai_summary": result["summary"],
                "ai_when_to_use": result["when_to_use"],
                "ai_related_topics": result["related_topics"],
                "model": "migrated-from-legacy-cache",
                "pipeline_version": "v12",
            },
        )
        migrated_from_legacy += 1

    # 3. Generate via API
    if result is None and WRITE_AI and TOKEN and not api_stopped:
        if api_calls_made >= MAX_FILES:
            if api_calls_made == MAX_FILES:
                print(
                    f"[04] API cap reached ({MAX_FILES}); "
                    "remaining files left unenriched this run"
                )
            api_stopped = True
        else:
            api_result = _call_api(full_content, f"{module}/{slug}")
            if api_result == "STOP":
                api_stopped = True
            elif api_result:
                result = api_result
                ai_store.save_summary(
                    module,
                    slug,
                    {
                        "slug": slug,
                        "module": module,
                        "title": slug,
                        "content_hash": body_hash,
                        "ai_summary": result["summary"],
                        "ai_when_to_use": result["when_to_use"],
                        "ai_related_topics": result["related_topics"],
                        "model": MODEL,
                        "pipeline_version": "v12",
                    },
                )
                generated_via_api += 1
                api_calls_made += 1
                time.sleep(0.5)
            else:
                print(f"[04] WARN: No summary generated for {module}/{slug}")

    # 4. Validate and inject into L2 YAML frontmatter
    if result and VALIDATE_PAYLOAD and not _validate_payload(result, f"{module}/{slug}"):
        result = None

    if result:
        try:
            loaded_fm: Any = _yaml.safe_load(fm_text)
            fm_data: dict[str, Any] = {}
            if isinstance(loaded_fm, dict):
                for key_any, val_any in cast(dict[Any, Any], loaded_fm).items():
                    if isinstance(key_any, str):
                        fm_data[key_any] = val_any
            fm_data["ai_summary"] = result["summary"]
            fm_data["ai_when_to_use"] = result["when_to_use"]
            fm_data["ai_related_topics"] = result["related_topics"]

            new_fm = _yaml.safe_dump(
                fm_data, sort_keys=False, width=1000, allow_unicode=True
            )
            new_content = f"---\n{new_fm}---\n{body}"

            with open(fpath, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new_content)
            applied += 1
        except Exception as exc:
            print(f"[04] ERR: YAML injection failed for {module}/{slug}: {exc}")

# ── Summary ───────────────────────────────────────────────────────────────────

base_count, override_count = ai_store.stats()
print(
    f"[04] Complete: {applied} enriched "
    f"({generated_via_api} API-generated, "
    f"{migrated_from_legacy} migrated from legacy cache, "
    f"{stale_applied} applied stale), "
    f"{skipped_already} already had summaries, "
    f"{skipped_short} too short."
)
print(
    f"[04] Data store: {base_count} base records, "
    f"{override_count} override records."
)
if api_stopped and generated_via_api == 0:
    print(
        "[04] INFO: API calls were halted (quota/auth/cap); "
        "remaining files left unenriched."
    )

