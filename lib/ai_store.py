"""
AI summary data store for openwrt-docs4ai.

Manages reading and writing of AI-generated summaries from the structured
data store under data/base/ and data/override/.

Resolution order:
  data/override/{module}/{slug}.json  (highest priority)
  data/base/{module}/{slug}.json      (pipeline-generated or seeded)
  None                                (no record found)

content_hash semantics:
  null / None   Human-authored entry. Always treated as valid regardless of
                L2 body changes. Content hash comparison is skipped.
  "<hex12>"     Pipeline-generated entry. Compared against the current L2 body
                hash when current_hash is supplied at lookup time. A mismatch
                returns "stale" so the caller can decide whether to regenerate.

File format (JSON, one file per L2 document):
  {
    "slug":              "<L2 filename without .md>",
    "module":            "<parent module name>",
    "title":             "<value of L2 title frontmatter field>",
    "content_hash":      "<sha256[:12] of L2 body, or null for human-authored>",
    "ai_summary":        "<2-4 sentence description starting with a verb>",
    "ai_when_to_use":    "<1-2 sentence OpenWrt-specific use case>",
    "ai_related_topics": ["<exact symbol name>", ...],
    "generated_at":      "<ISO 8601 timestamp>",
    "model":             "<model name or 'manual'/'seeded'>",
    "pipeline_version":  "v12",
    "saved_at":          "<ISO 8601 timestamp written at save time>"
  }
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Literal, Mapping, TypedDict, cast

from lib import config

AI_DATA_BASE_DIR = config.AI_DATA_BASE_DIR
AI_DATA_OVERRIDE_DIR = config.AI_DATA_OVERRIDE_DIR

PIPELINE_VERSION = "v12"


class SummaryRecord(TypedDict, total=False):
    slug: str
    module: str
    title: str
    content_hash: str | None
    ai_summary: str
    ai_when_to_use: str
    ai_related_topics: list[str]
    generated_at: str
    model: str
    pipeline_version: str
    saved_at: str


def _json_path(store_dir: str, module: str, slug: str) -> str:
    """Return the expected filesystem path for a summary JSON file."""
    return os.path.join(store_dir, module, f"{slug}.json")


def _load_record(path: str) -> SummaryRecord | None:
    """Load a JSON record from disk when it is valid dict-like JSON."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data: Any = json.load(fh)
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    return cast(SummaryRecord, data)


def load_summary(
    module: str,
    slug: str,
    current_hash: str | None = None,
) -> tuple[Literal["ok", "stale"] | None, SummaryRecord | None]:
    """
    Resolve and load an AI summary record.

    Returns (status, data):
      ("ok",    dict)   Valid record; safe to apply to L2 frontmatter.
      ("stale", dict)   Record exists but its content_hash does not match
                        current_hash; the L2 body has changed since the
                        summary was generated. Caller decides what to do.
      (None,    None)   No record found in either store.

    When current_hash is None, hash comparison is skipped for non-null stored
    hashes (the caller does not want staleness detection for this call).
    A null stored content_hash always returns "ok" (human-authored is always
    trusted).
    """
    for store_dir in (AI_DATA_OVERRIDE_DIR, AI_DATA_BASE_DIR):
        path = _json_path(store_dir, module, slug)
        if not os.path.isfile(path):
            continue
        data = _load_record(path)
        if data is None:
            continue

        stored_hash = data.get("content_hash")

        # null content_hash = human-authored; always valid
        if stored_hash is not None and current_hash is not None:
            if stored_hash != current_hash:
                return "stale", data

        return "ok", data

    return None, None


def save_summary(
    module: str,
    slug: str,
    summary_data: Mapping[str, Any],
    to_override: bool = False,
) -> None:
    """
    Persist an AI summary record to the data store.

    summary_data must contain:
      slug, module, title, content_hash (or null),
      ai_summary, ai_when_to_use, ai_related_topics,
      model, pipeline_version

    Writes to data/override/ when to_override=True, else data/base/.
    Always writes saved_at timestamp and ensures pipeline_version is set.
    """
    store_dir = AI_DATA_OVERRIDE_DIR if to_override else AI_DATA_BASE_DIR
    path = _json_path(store_dir, module, slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    record: dict[str, Any] = dict(summary_data)
    record.setdefault("pipeline_version", PIPELINE_VERSION)
    record["saved_at"] = datetime.now(timezone.utc).isoformat()

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def create_override_from_base(module: str, slug: str) -> bool:
    """
    Copy a base record to the override store for manual editing.

    If the base record does not exist, returns False.
    If an override record already exists, returns False (refuse to clobber).
    On success, sets content_hash to null (human-authored) and returns True.

    Usage pattern:
      1. Call create_override_from_base(module, slug)
      2. Edit data/override/{module}/{slug}.json manually
      3. The override is picked up automatically on the next pipeline run.
    """
    base_path = _json_path(AI_DATA_BASE_DIR, module, slug)
    override_path = _json_path(AI_DATA_OVERRIDE_DIR, module, slug)

    if not os.path.isfile(base_path):
        return False
    if os.path.isfile(override_path):
        return False

    data = _load_record(base_path)
    if data is None:
        return False

    # Mark as human-authored (null hash = always valid)
    data["content_hash"] = None
    data["model"] = "manual-override"
    save_summary(module, slug, data, to_override=True)
    return True


def list_all(
    store: Literal["base", "override"] = "base",
) -> list[tuple[str, str, SummaryRecord]]:
    """
    Enumerate all summary records in a store.

    Returns list of (module, slug, data) tuples sorted by module then slug.
    store must be "base" or "override".
    """
    store_dir = AI_DATA_BASE_DIR if store == "base" else AI_DATA_OVERRIDE_DIR
    results: list[tuple[str, str, SummaryRecord]] = []

    if not os.path.isdir(store_dir):
        return results

    for module in sorted(os.listdir(store_dir)):
        mod_dir = os.path.join(store_dir, module)
        if not os.path.isdir(mod_dir):
            continue
        for fname in sorted(os.listdir(mod_dir)):
            if not fname.endswith(".json"):
                continue
            slug = fname[:-5]
            fpath = os.path.join(mod_dir, fname)
            data = _load_record(fpath)
            if data is None:
                continue
            results.append((module, slug, data))

    return results


def stats() -> tuple[int, int]:
    """Return (base_count, override_count) count of stored records."""
    return len(list_all("base")), len(list_all("override"))
