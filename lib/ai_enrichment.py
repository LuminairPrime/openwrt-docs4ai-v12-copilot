"""Shared AI enrichment runner used by the numbered stage and local tooling."""

import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Literal, TypedDict, cast

from lib import ai_store
from lib.ai_corpus import body_hash, split_frontmatter
from lib.ai_store_checks import (
    audit_store,
    print_audit_report,
    print_validation_report,
    validate_store,
)


API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL = "gpt-4o-mini"


class SummaryPayload(TypedDict):
    """Validated AI payload that can be injected into L2 frontmatter."""

    summary: str
    when_to_use: str
    related_topics: list[str]


SYSTEM_PROMPT = (
    "You are a technical documentation assistant for OpenWrt — a Linux-based "
    "operating system for embedded network devices. You write clear, accurate, "
    "developer-focused descriptions.\n\n"
    "Given an API/module doc as context, produce a JSON object with exactly:\n"
    '  "summary":       "<3-5 sentences. Sentence 1 is comprehensive. '
    "Sentences 2-5 add concrete details and clarifications with exact "
    'functions.>"\n'
    '  "when_to_use":   "<1-2 sentences: specific OpenWrt use case.>"\n'
    '  "related_topics": ["<exact symbol name found in text>", ...]\n\n'
    "Follow spelling/naming in the text exactly. Do not invent symbols."
)

_UNSAFE_PAYLOAD_RE = re.compile(
    r"<script\b|javascript:|data:text/html|[\x00-\x08\x0b\x0c\x0e-\x1f]",
    re.IGNORECASE,
)


def _coerce_related_topics(value: Any) -> list[str]:
    """Normalize related topics into a clean list of strings."""
    if not isinstance(value, list):
        return []

    out: list[str] = []
    for item in cast(list[Any], value):
        topic = str(item).strip()
        if topic:
            out.append(topic)
    return out


def _validate_payload(
    payload: SummaryPayload,
    label: str,
    prefix: str,
) -> bool:
    """Apply a light safety and sanity check before injecting AI payloads."""
    summary = payload.get("summary", "").strip()
    when_to_use = payload.get("when_to_use", "").strip()
    related_topics = _coerce_related_topics(payload.get("related_topics", []))

    if not summary or not when_to_use:
        print(f"{prefix} WARN: Rejecting empty AI payload for {label}")
        return False

    if len(summary) < 20:
        print(f"{prefix} WARN: Rejecting too-short summary for {label} (len={len(summary)})")
        return False

    for field_name, field_value in (("summary", summary), ("when_to_use", when_to_use)):
        if _UNSAFE_PAYLOAD_RE.search(field_value):
            print(f"{prefix} WARN: Unsafe content in {field_name} for {label}; skipping injection")
            return False

    if not related_topics:
        print(f"{prefix} WARN: Rejecting payload without related_topics for {label}")
        return False

    return True


def _load_legacy_cache(
    legacy_cache_path: str,
    prefix: str,
) -> dict[str, dict[str, Any]]:
    """Load the legacy hash-keyed cache when present and well formed."""
    if not os.path.isfile(legacy_cache_path):
        return {}

    try:
        with open(legacy_cache_path, "r", encoding="utf-8") as handle:
            loaded: Any = json.load(handle)
    except Exception as exc:
        print(f"{prefix} WARN: Could not read legacy cache: {exc}")
        return {}

    if not isinstance(loaded, dict):
        return {}

    normalized: dict[str, dict[str, Any]] = {}
    for key_any, value_any in cast(dict[Any, Any], loaded).items():
        if isinstance(key_any, str) and isinstance(value_any, dict):
            normalized[key_any] = cast(dict[str, Any], value_any)
    return normalized


def _repair_base_record_metadata(
    module: str,
    slug: str,
    title: str,
    current_body_hash: str,
    prefix: str,
) -> bool:
    """Repair base-record metadata drift without touching overrides."""
    override_path = os.path.join(ai_store.AI_DATA_OVERRIDE_DIR, module, f"{slug}.json")
    base_path = os.path.join(ai_store.AI_DATA_BASE_DIR, module, f"{slug}.json")

    if os.path.isfile(override_path) or not os.path.isfile(base_path):
        return False

    status, record = ai_store.load_summary(module, slug, current_hash=current_body_hash)
    if status != "ok" or record is None:
        return False

    generated_at = record.get("generated_at")
    stored_title = str(record.get("title", "")).strip()
    has_generated_at = isinstance(generated_at, str) and generated_at.strip()

    if stored_title == title and has_generated_at:
        return False

    repaired = dict(record)
    repaired["slug"] = slug
    repaired["module"] = module
    repaired["title"] = title
    if repaired.get("content_hash") is not None:
        repaired["content_hash"] = current_body_hash
    if not has_generated_at:
        repaired["generated_at"] = datetime.now(timezone.utc).isoformat()

    ai_store.save_summary(module, slug, repaired)
    print(f"{prefix} INFO: Repaired base metadata for {module}/{slug}")
    return True


def _call_api(
    content: str,
    label: str,
    token: str,
    prefix: str,
) -> SummaryPayload | Literal["STOP"] | None:
    """Call the GitHub Models API and return one parsed summary payload."""
    try:
        import requests as _requests
    except ImportError:
        print(f"{prefix} FAIL: 'requests' package not installed")
        return None

    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
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
            response: Any = _requests.post(
                API_URL,
                json=payload,
                headers=headers,
                timeout=60,
            )

            if response.status_code == 429:
                wait_seconds = int(response.headers.get("Retry-After", 30))
                print(f"{prefix} Rate-limited; waiting {wait_seconds}s...")
                time.sleep(wait_seconds)
                continue

            if response.status_code in (401, 403) or any(
                keyword in response.text.lower() for keyword in ("no quota", "limit reached")
            ):
                print(f"{prefix} API quota/auth failure (HTTP {response.status_code}); halting API calls for this run.")
                return "STOP"

            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"]
            raw = re.sub(
                r"^```(?:json)?\n?|(?:^|\n)```$",
                "",
                raw.strip(),
                flags=re.MULTILINE,
            )
            parsed_any: Any = json.loads(raw)
            if not isinstance(parsed_any, dict):
                print(f"{prefix} WARN: API returned non-object JSON for {label}")
                return None

            parsed = cast(dict[str, Any], parsed_any)
            return {
                "summary": str(parsed.get("summary", "")).replace("\n", " ").strip(),
                "when_to_use": str(parsed.get("when_to_use", "")).replace("\n", " ").strip(),
                "related_topics": _coerce_related_topics(parsed.get("related_topics", [])),
            }
        except Exception as exc:
            print(f"{prefix} WARN: API error for {label} (attempt {attempt + 1}): {exc}")
            time.sleep(5)

    return None


def _discover_targets(
    l2_dir: str,
    prefix: str,
) -> tuple[list[tuple[str, str, str]], float]:
    """Discover all markdown files beneath the staged L2 root."""
    all_targets: list[tuple[str, str, str]] = []
    discover_start = time.perf_counter()

    for module in sorted(os.listdir(l2_dir)):
        module_dir = os.path.join(l2_dir, module)
        if not os.path.isdir(module_dir):
            continue
        for filename in sorted(os.listdir(module_dir)):
            if filename.endswith(".md"):
                all_targets.append((module, filename[:-3], os.path.join(module_dir, filename)))

    discover_seconds = time.perf_counter() - discover_start
    print(f"{prefix} Found {len(all_targets)} L2 documents")
    print(f"{prefix} TIMER: phase=discover_targets seconds={discover_seconds:.3f}")
    return all_targets, discover_seconds


def _run_preflight(
    *,
    l2_dir: str,
    base_dir: str,
    override_dir: str,
    prefix: str,
) -> bool:
    """Validate committed or scratch AI store state before enrichment runs."""
    validation = validate_store(
        store="both",
        base_dir=base_dir,
        override_dir=override_dir,
        l2_root=l2_dir,
        allow_orphans=True,
        allow_title_mismatch=True,
        allow_hash_mismatch=True,
    )
    print_validation_report(prefix, validation)
    if validation.errors:
        return False

    counts, details, issues = audit_store(
        l2_root=l2_dir,
        base_dir=base_dir,
        override_dir=override_dir,
    )
    if issues:
        for issue in issues:
            print(f"{prefix} FAIL: {issue}")
        return False

    print_audit_report(prefix, counts, details, detail_limit=10)
    return True


def run_ai_enrichment(
    *,
    outdir: str,
    base_dir: str,
    override_dir: str,
    legacy_cache_path: str,
    skip_ai: bool,
    write_ai: bool,
    max_files: int,
    token: str | None,
    validate_payload: bool,
    report_prefix: str = "[04]",
) -> int:
    """Run AI summary application and optional generation for one staged corpus."""
    if skip_ai:
        print(f"{report_prefix} SKIP: AI summarization disabled (SKIP_AI=true)")
        return 0

    l2_dir = os.path.join(outdir, "L2-semantic")
    if not os.path.isdir(l2_dir):
        print(f"{report_prefix} FAIL: L2 directory not found: {l2_dir}")
        return 1

    try:
        import yaml as _yaml
    except ImportError:
        print(f"{report_prefix} FAIL: 'pyyaml' package not installed")
        return 1

    token_value = str(token or "").strip() or None

    print(f"{report_prefix} AI summary enrichment starting")
    stage_start_epoch = int(time.time())
    stage_timer_start = time.perf_counter()
    if not write_ai:
        print(f"{report_prefix} INFO: WRITE_AI=false — applying stored summaries only, no API calls")
    elif not token_value:
        print(f"{report_prefix} INFO: WRITE_AI=true but no token is configured — applying stored summaries only")

    if not _run_preflight(
        l2_dir=l2_dir,
        base_dir=base_dir,
        override_dir=override_dir,
        prefix=report_prefix,
    ):
        return 1

    legacy_cache = _load_legacy_cache(legacy_cache_path, report_prefix)
    if legacy_cache:
        print(f"{report_prefix} Legacy cache loaded: {len(legacy_cache)} hash-keyed entries available for migration")

    all_targets, discover_targets_seconds = _discover_targets(l2_dir, report_prefix)

    applied = 0
    skipped_already = 0
    skipped_short = 0
    migrated_from_legacy = 0
    generated_via_api = 0
    stale_applied = 0
    api_stopped = False
    api_calls_made = 0
    store_lookup_seconds = 0.0
    legacy_migration_seconds = 0.0
    api_generation_seconds = 0.0
    injection_seconds = 0.0

    with ai_store.temporary_store_roots(base_dir, override_dir):
        for module, slug, path in all_targets:
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    full_content = handle.read()
            except Exception as exc:
                print(f"{report_prefix} WARN: Cannot read {path}: {exc}")
                continue

            frontmatter_text, body = split_frontmatter(full_content)
            if frontmatter_text is None or body is None:
                print(f"{report_prefix} WARN: Skipping {slug} — no valid L2 frontmatter")
                continue

            try:
                frontmatter_any: Any = _yaml.safe_load(frontmatter_text)
            except Exception as exc:
                print(f"{report_prefix} WARN: Skipping {slug} — invalid YAML frontmatter: {exc}")
                continue

            frontmatter: dict[str, Any] = {}
            if isinstance(frontmatter_any, dict):
                for key_any, value_any in cast(dict[Any, Any], frontmatter_any).items():
                    if isinstance(key_any, str):
                        frontmatter[key_any] = value_any

            title = str(frontmatter.get("title", "")).strip() or slug
            current_body_hash = body_hash(body)

            if write_ai:
                _repair_base_record_metadata(
                    module,
                    slug,
                    title,
                    current_body_hash,
                    report_prefix,
                )

            if "ai_summary:" in frontmatter_text:
                skipped_already += 1
                continue

            if len(body.split()) < 15:
                skipped_short += 1
                continue

            result: SummaryPayload | None = None

            store_lookup_start = time.perf_counter()
            status, record = ai_store.load_summary(
                module,
                slug,
                current_hash=current_body_hash,
            )

            if status == "ok" and record:
                result = {
                    "summary": str(record.get("ai_summary", "")),
                    "when_to_use": str(record.get("ai_when_to_use", "")),
                    "related_topics": _coerce_related_topics(record.get("ai_related_topics", [])),
                }
            elif status == "stale" and record:
                stored_hash = record.get("content_hash", "?")
                print(f"{report_prefix} STALE: {module}/{slug} (stored={stored_hash} current={current_body_hash})")
                if not write_ai or not token_value:
                    result = {
                        "summary": str(record.get("ai_summary", "")),
                        "when_to_use": str(record.get("ai_when_to_use", "")),
                        "related_topics": _coerce_related_topics(record.get("ai_related_topics", [])),
                    }
                    stale_applied += 1
            store_lookup_seconds += time.perf_counter() - store_lookup_start

            legacy_migration_start = time.perf_counter()
            if result is None and current_body_hash in legacy_cache:
                legacy_entry = legacy_cache[current_body_hash]
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
                        "title": title,
                        "content_hash": current_body_hash,
                        "ai_summary": result["summary"],
                        "ai_when_to_use": result["when_to_use"],
                        "ai_related_topics": result["related_topics"],
                        "generated_at": legacy_entry.get(
                            "generated_at",
                            datetime.now(timezone.utc).isoformat(),
                        ),
                        "model": "migrated-from-legacy-cache",
                        "pipeline_version": "v12",
                    },
                )
                migrated_from_legacy += 1
            legacy_migration_seconds += time.perf_counter() - legacy_migration_start

            api_generation_start = time.perf_counter()
            if result is None and write_ai and token_value and not api_stopped:
                if api_calls_made >= max_files:
                    if api_calls_made == max_files:
                        print(
                            f"{report_prefix} API cap reached ({max_files}); remaining files left unenriched this run"
                        )
                    api_stopped = True
                else:
                    api_result = _call_api(
                        full_content,
                        f"{module}/{slug}",
                        token_value,
                        report_prefix,
                    )
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
                                "title": title,
                                "content_hash": current_body_hash,
                                "ai_summary": result["summary"],
                                "ai_when_to_use": result["when_to_use"],
                                "ai_related_topics": result["related_topics"],
                                "generated_at": datetime.now(timezone.utc).isoformat(),
                                "model": MODEL,
                                "pipeline_version": "v12",
                            },
                        )
                        generated_via_api += 1
                        api_calls_made += 1
                        time.sleep(0.5)
                    else:
                        print(f"{report_prefix} WARN: No summary generated for {module}/{slug}")
            api_generation_seconds += time.perf_counter() - api_generation_start

            injection_start = time.perf_counter()
            if (
                result
                and validate_payload
                and not _validate_payload(
                    result,
                    f"{module}/{slug}",
                    report_prefix,
                )
            ):
                result = None

            if result:
                try:
                    frontmatter["ai_summary"] = result["summary"]
                    frontmatter["ai_when_to_use"] = result["when_to_use"]
                    frontmatter["ai_related_topics"] = result["related_topics"]

                    new_frontmatter = _yaml.safe_dump(
                        frontmatter,
                        sort_keys=False,
                        width=1000,
                        allow_unicode=True,
                    )
                    new_content = f"---\n{new_frontmatter}---\n{body}"

                    with open(path, "w", encoding="utf-8", newline="\n") as handle:
                        handle.write(new_content)
                    applied += 1
                except Exception as exc:
                    print(f"{report_prefix} ERR: YAML injection failed for {module}/{slug}: {exc}")
            injection_seconds += time.perf_counter() - injection_start

        base_count, override_count = ai_store.stats()

    print(
        f"{report_prefix} Complete: {applied} enriched "
        f"({generated_via_api} API-generated, "
        f"{migrated_from_legacy} migrated from legacy cache, "
        f"{stale_applied} applied stale), {skipped_already} already had "
        f"summaries, {skipped_short} too short."
    )
    print(f"{report_prefix} Data store: {base_count} base records, {override_count} override records.")

    stage_end_epoch = int(time.time())
    total_seconds = time.perf_counter() - stage_timer_start
    print(
        f"{report_prefix} TIMER: stage_start_epoch={stage_start_epoch} "
        f"stage_end_epoch={stage_end_epoch} total_seconds={total_seconds:.3f} "
        f"discover_targets_seconds={discover_targets_seconds:.3f} "
        f"store_lookup_seconds={store_lookup_seconds:.3f} "
        f"legacy_migration_seconds={legacy_migration_seconds:.3f} "
        f"api_generation_seconds={api_generation_seconds:.3f} "
        f"injection_seconds={injection_seconds:.3f} targets={len(all_targets)} "
        f"api_calls={api_calls_made}"
    )
    if api_stopped and generated_via_api == 0:
        print(f"{report_prefix} INFO: API calls were halted (quota/auth/cap); remaining files left unenriched.")

    return 0
