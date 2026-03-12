"""Validation and audit helpers for the AI summary data store."""

import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, DefaultDict, Mapping

from lib.ai_corpus import L2Document, load_l2_documents


_HASH_RE = re.compile(r"^[0-9a-f]{12}$")

REQUIRED_FIELDS = (
    "slug",
    "module",
    "title",
    "content_hash",
    "ai_summary",
    "ai_when_to_use",
    "ai_related_topics",
    "generated_at",
    "model",
    "pipeline_version",
)


@dataclass(frozen=True)
class StoreValidationResult:
    """Structured result for schema and referential AI store validation."""

    checked_records: int
    errors: list[str]
    warnings: list[str]
    l2_document_count: int


def load_json_record(path: str) -> dict[str, Any] | None:
    """Load a dict-like JSON record from disk when possible."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data: Any = json.load(handle)
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    return data


def is_iso_timestamp(value: Any) -> bool:
    """Return True when a value parses as ISO 8601 text."""
    if not isinstance(value, str) or not value.strip():
        return False

    normalized = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def iter_store_files(store_root: str) -> list[tuple[str, str, str]]:
    """Return all JSON records in a store root."""
    files: list[tuple[str, str, str]] = []

    if not os.path.isdir(store_root):
        return files

    for module in sorted(os.listdir(store_root)):
        module_dir = os.path.join(store_root, module)
        if not os.path.isdir(module_dir):
            continue
        for filename in sorted(os.listdir(module_dir)):
            if not filename.endswith(".json"):
                continue
            slug = filename[:-5]
            files.append((module, slug, os.path.join(module_dir, filename)))

    return files


def _append_detail(
    details: DefaultDict[str, list[str]],
    category: str,
    item: str,
) -> None:
    """Append one human-readable detail line to a grouped category."""
    details[category].append(item)


def _classify_record(record: dict[str, Any], body_hash: str) -> str:
    """Return the active record status for a matching L2 document."""
    stored_hash = record.get("content_hash")
    if stored_hash is None:
        return "pinned"
    if stored_hash == body_hash:
        return "current"
    return "stale"


def _report_issue(
    *,
    message: str,
    errors: list[str],
    warnings: list[str],
    as_warning: bool,
) -> None:
    """Append one validation issue to the correct severity list."""
    if as_warning:
        warnings.append(message)
        return
    errors.append(message)


def _validate_record(
    *,
    store_name: str,
    module: str,
    slug: str,
    path: str,
    record: dict[str, Any],
    l2_documents: dict[tuple[str, str], L2Document] | None,
    errors: list[str],
    warnings: list[str],
    allow_orphans: bool,
    allow_title_mismatch: bool,
    allow_hash_mismatch: bool,
) -> None:
    """Validate one AI summary record against schema and optional L2 data."""
    missing_fields = [field for field in REQUIRED_FIELDS if field not in record]
    if missing_fields:
        errors.append(
            f"{store_name} {module}/{slug}: missing required fields {missing_fields}"
        )
        return

    if record.get("slug") != slug:
        errors.append(f"{store_name} {module}/{slug}: slug does not match path")
    if record.get("module") != module:
        errors.append(f"{store_name} {module}/{slug}: module does not match path")

    title = record.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append(f"{store_name} {module}/{slug}: title must be a non-empty string")

    content_hash = record.get("content_hash")
    if content_hash is not None and (
        not isinstance(content_hash, str)
        or not _HASH_RE.fullmatch(content_hash)
    ):
        errors.append(
            f"{store_name} {module}/{slug}: content_hash must be null or "
            "12-char lowercase hex"
        )

    if store_name == "override" and content_hash is not None:
        errors.append(
            f"override {module}/{slug}: content_hash must be null for "
            "human-pinned overrides"
        )

    summary = record.get("ai_summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append(f"{store_name} {module}/{slug}: ai_summary must be non-empty text")

    when_to_use = record.get("ai_when_to_use")
    if not isinstance(when_to_use, str) or not when_to_use.strip():
        errors.append(
            f"{store_name} {module}/{slug}: ai_when_to_use must be non-empty text"
        )

    related_topics = record.get("ai_related_topics")
    if not isinstance(related_topics, list) or not related_topics:
        errors.append(
            f"{store_name} {module}/{slug}: ai_related_topics must be a "
            "non-empty list"
        )
    elif not all(isinstance(item, str) and item.strip() for item in related_topics):
        errors.append(
            f"{store_name} {module}/{slug}: ai_related_topics entries must be "
            "non-empty strings"
        )

    if not is_iso_timestamp(record.get("generated_at")):
        errors.append(
            f"{store_name} {module}/{slug}: generated_at must be ISO 8601 text"
        )

    saved_at = record.get("saved_at")
    if saved_at is not None and not is_iso_timestamp(saved_at):
        errors.append(
            f"{store_name} {module}/{slug}: saved_at must be ISO 8601 text"
        )

    model = record.get("model")
    if not isinstance(model, str) or not model.strip():
        errors.append(f"{store_name} {module}/{slug}: model must be non-empty text")

    if record.get("pipeline_version") != "v12":
        errors.append(f"{store_name} {module}/{slug}: pipeline_version must be v12")

    if l2_documents is None:
        return

    document = l2_documents.get((module, slug))
    if document is None:
        _report_issue(
            message=(
                f"{store_name} {module}/{slug}: no matching L2 document found "
                f"for {path}"
            ),
            errors=errors,
            warnings=warnings,
            as_warning=allow_orphans,
        )
        return

    if isinstance(title, str) and title.strip() and title.strip() != document.title:
        _report_issue(
            message=(
                f"{store_name} {module}/{slug}: title does not match L2 "
                "frontmatter"
            ),
            errors=errors,
            warnings=warnings,
            as_warning=allow_title_mismatch,
        )

    if isinstance(content_hash, str) and content_hash != document.body_hash:
        _report_issue(
            message=(
                f"{store_name} {module}/{slug}: content_hash does not match "
                "current L2 body"
            ),
            errors=errors,
            warnings=warnings,
            as_warning=allow_hash_mismatch,
        )


def validate_store(
    *,
    store: str,
    base_dir: str,
    override_dir: str,
    l2_root: str,
    skip_l2_checks: bool = False,
    allow_orphans: bool = False,
    allow_title_mismatch: bool = False,
    allow_hash_mismatch: bool = False,
) -> StoreValidationResult:
    """Validate selected AI store records against schema and optional L2 data."""
    l2_documents: dict[tuple[str, str], L2Document] | None = None
    if not skip_l2_checks:
        l2_documents, issues = load_l2_documents(l2_root)
        if issues:
            return StoreValidationResult(
                checked_records=0,
                errors=issues,
                warnings=[],
                l2_document_count=0,
            )

    selected_stores: list[tuple[str, str]] = []
    if store in {"base", "both"}:
        selected_stores.append(("base", base_dir))
    if store in {"override", "both"}:
        selected_stores.append(("override", override_dir))

    checked_records = 0
    errors: list[str] = []
    warnings: list[str] = []

    for store_name, store_root in selected_stores:
        for module, slug, path in iter_store_files(store_root):
            checked_records += 1
            record = load_json_record(path)
            if record is None:
                errors.append(f"{store_name} {module}/{slug}: invalid JSON at {path}")
                continue

            _validate_record(
                store_name=store_name,
                module=module,
                slug=slug,
                path=path,
                record=record,
                l2_documents=l2_documents,
                errors=errors,
                warnings=warnings,
                allow_orphans=allow_orphans,
                allow_title_mismatch=allow_title_mismatch,
                allow_hash_mismatch=allow_hash_mismatch,
            )

    return StoreValidationResult(
        checked_records=checked_records,
        errors=errors,
        warnings=warnings,
        l2_document_count=len(l2_documents or {}),
    )


def audit_store(
    *,
    l2_root: str,
    base_dir: str,
    override_dir: str,
) -> tuple[Counter[str], DefaultDict[str, list[str]], list[str]]:
    """Audit store coverage, staleness, and orphaned records."""
    counts: Counter[str] = Counter()
    details: DefaultDict[str, list[str]] = defaultdict(list)
    l2_documents, issues = load_l2_documents(l2_root)

    if issues:
        return counts, details, issues

    l2_keys = set(l2_documents)
    counts["l2_documents"] = len(l2_documents)

    for document in l2_documents.values():
        override_path = os.path.join(override_dir, document.module, f"{document.slug}.json")
        base_path = os.path.join(base_dir, document.module, f"{document.slug}.json")

        if os.path.isfile(override_path):
            record = load_json_record(override_path)
            if record is None:
                counts["invalid_override"] += 1
                _append_detail(
                    details,
                    "invalid",
                    f"override {document.module}/{document.slug} ({override_path})",
                )
                continue

            status = _classify_record(record, document.body_hash)
            counts[f"override_{status}"] += 1
            _append_detail(
                details,
                status,
                f"override {document.module}/{document.slug} — {document.title}",
            )
            continue

        if os.path.isfile(base_path):
            record = load_json_record(base_path)
            if record is None:
                counts["invalid_base"] += 1
                _append_detail(
                    details,
                    "invalid",
                    f"base {document.module}/{document.slug} ({base_path})",
                )
                continue

            status = _classify_record(record, document.body_hash)
            counts[f"base_{status}"] += 1
            _append_detail(
                details,
                status,
                f"base {document.module}/{document.slug} — {document.title}",
            )
            continue

        counts["missing"] += 1
        _append_detail(
            details,
            "missing",
            f"{document.module}/{document.slug} — {document.title}",
        )

    for store_name, store_root in (("base", base_dir), ("override", override_dir)):
        for module, slug, path in iter_store_files(store_root):
            if (module, slug) in l2_keys:
                continue
            counts[f"orphan_{store_name}"] += 1
            _append_detail(details, "orphan", f"{store_name} {module}/{slug} ({path})")

    return counts, details, issues


def summarize_audit_counts(counts: Mapping[str, int]) -> dict[str, int]:
    """Collapse raw audit counters into user-facing coverage totals."""
    return {
        "current": counts.get("base_current", 0) + counts.get("override_current", 0),
        "pinned": counts.get("base_pinned", 0) + counts.get("override_pinned", 0),
        "stale": counts.get("base_stale", 0) + counts.get("override_stale", 0),
        "missing": counts.get("missing", 0),
        "orphan": counts.get("orphan_base", 0) + counts.get("orphan_override", 0),
        "invalid": counts.get("invalid_base", 0) + counts.get("invalid_override", 0),
    }


def default_audit_categories(counts: Mapping[str, int]) -> list[str]:
    """Return the non-empty detail categories worth printing by default."""
    totals = summarize_audit_counts(counts)
    return [
        category
        for category in ("missing", "stale", "orphan", "invalid")
        if totals[category] > 0
    ]


def print_validation_report(
    prefix: str,
    result: StoreValidationResult,
    *,
    max_errors: int = 200,
    max_warnings: int = 50,
) -> None:
    """Render a bounded validation report to stdout."""
    error_limit = max(0, max_errors)
    warning_limit = max(0, max_warnings)

    for error in result.errors[:error_limit]:
        print(f"{prefix} FAIL: {error}")

    remaining_errors = len(result.errors) - error_limit
    if remaining_errors > 0:
        print(f"{prefix} FAIL: ... {remaining_errors} more errors")

    for warning in result.warnings[:warning_limit]:
        print(f"{prefix} WARN: {warning}")

    remaining_warnings = len(result.warnings) - warning_limit
    if remaining_warnings > 0:
        print(f"{prefix} WARN: ... {remaining_warnings} more warnings")

    status = "FAILED" if result.errors else "OK"
    print(f"{prefix} Checked {result.checked_records} records: {status}")
    if result.l2_document_count:
        print(
            f"{prefix} L2 documents available for cross-check: "
            f"{result.l2_document_count}"
        )
    else:
        print(f"{prefix} L2 cross-checks were skipped")


def print_audit_report(
    prefix: str,
    counts: Mapping[str, int],
    details: Mapping[str, list[str]],
    *,
    detail_limit: int = 20,
    categories: list[str] | None = None,
) -> None:
    """Render an audit summary and bounded detail sections to stdout."""
    totals = summarize_audit_counts(counts)

    print(f"{prefix} L2 documents: {counts.get('l2_documents', 0)}")
    print(
        f"{prefix} Active coverage: current={totals['current']}, "
        f"pinned={totals['pinned']}, stale={totals['stale']}, "
        f"missing={totals['missing']}"
    )
    print(
        f"{prefix} Active sources: base_current={counts.get('base_current', 0)}, "
        f"base_pinned={counts.get('base_pinned', 0)}, "
        f"base_stale={counts.get('base_stale', 0)}, "
        f"override_current={counts.get('override_current', 0)}, "
        f"override_pinned={counts.get('override_pinned', 0)}, "
        f"override_stale={counts.get('override_stale', 0)}"
    )
    print(
        f"{prefix} Store hygiene: orphan_base={counts.get('orphan_base', 0)}, "
        f"orphan_override={counts.get('orphan_override', 0)}, "
        f"invalid_base={counts.get('invalid_base', 0)}, "
        f"invalid_override={counts.get('invalid_override', 0)}"
    )

    selected_categories = categories or default_audit_categories(counts)
    limit = max(0, detail_limit)
    for category in selected_categories:
        entries = list(details.get(category, []))
        if not entries:
            continue

        print(f"{prefix} {category} detail ({len(entries)}):")
        for item in entries[:limit]:
            print(f"  - {item}")

        remaining = len(entries) - limit
        if remaining > 0:
            print(f"  ... {remaining} more")


def audit_failure_labels(
    counts: Mapping[str, int],
    *,
    fail_on_missing: bool,
    fail_on_stale: bool,
    fail_on_orphan: bool,
    fail_on_invalid: bool,
) -> list[str]:
    """Return failure labels for the requested non-zero audit categories."""
    totals = summarize_audit_counts(counts)
    failures: list[str] = []

    if fail_on_missing and totals["missing"]:
        failures.append(f"missing={totals['missing']}")
    if fail_on_stale and totals["stale"]:
        failures.append(f"stale={totals['stale']}")
    if fail_on_orphan and totals["orphan"]:
        failures.append(f"orphan={totals['orphan']}")
    if fail_on_invalid and totals["invalid"]:
        failures.append(f"invalid={totals['invalid']}")

    return failures