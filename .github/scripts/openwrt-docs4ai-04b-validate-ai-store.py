"""
Purpose: Validate AI summary JSON records and their L2 referential integrity.
Phase: AI Maintenance (Read-only)
Layers: AI data store + optional L2 cross-check -> stdout
Inputs:  - data/base/{module}/{slug}.json     (base data store)
         - data/override/{module}/{slug}.json (override data store)
         - OUTDIR/L2-semantic/                (optional integrity source)
Outputs: - Validation report to stdout only
Environment Variables:
  OUTDIR               Default L2 root via OUTDIR/L2-semantic.
  AI_DATA_BASE_DIR     Override default data/base/ location.
  AI_DATA_OVERRIDE_DIR Override default data/override/ location.
Dependencies: pyyaml, lib.config, lib.ai_store
Notes: Read-only helper. Does not mutate L2 files or the AI store.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)

from lib import ai_store, config

_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)", re.DOTALL)
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
class L2Document:
    """Minimal L2 metadata needed for store integrity checks."""

    module: str
    slug: str
    title: str
    body_hash: str
    path: str


def _body_hash(body_text: str) -> str:
    """Return the canonical 12-character L2 body hash."""
    return hashlib.sha256(body_text.encode("utf-8")).hexdigest()[:12]


def _split_frontmatter(content: str) -> tuple[str | None, str | None]:
    """Split markdown into frontmatter and body when YAML is present."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2)


def _is_iso_timestamp(value: Any) -> bool:
    """Return True when a value parses as ISO 8601 text."""
    if not isinstance(value, str) or not value.strip():
        return False

    normalized = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def _load_l2_documents(l2_root: str) -> tuple[dict[tuple[str, str], L2Document], list[str]]:
    """Load the current L2 corpus into a keyed lookup table."""
    documents: dict[tuple[str, str], L2Document] = {}
    issues: list[str] = []

    if not os.path.isdir(l2_root):
        return documents, [f"Missing L2 root: {l2_root}"]

    try:
        import yaml as _yaml
    except ImportError:
        return documents, ["Missing dependency: pyyaml"]

    for module in sorted(os.listdir(l2_root)):
        module_dir = os.path.join(l2_root, module)
        if not os.path.isdir(module_dir):
            continue

        for filename in sorted(os.listdir(module_dir)):
            if not filename.endswith(".md"):
                continue

            slug = filename[:-3]
            path = os.path.join(module_dir, filename)

            try:
                with open(path, "r", encoding="utf-8") as handle:
                    content = handle.read()
            except Exception as exc:
                issues.append(f"Unreadable L2 file {module}/{slug}: {exc}")
                continue

            frontmatter_text, body = _split_frontmatter(content)
            if frontmatter_text is None or body is None:
                issues.append(f"Missing or invalid YAML frontmatter in {module}/{slug}")
                continue

            try:
                frontmatter_any: Any = _yaml.safe_load(frontmatter_text)
            except Exception as exc:
                issues.append(f"Invalid YAML frontmatter in {module}/{slug}: {exc}")
                continue

            if not isinstance(frontmatter_any, dict):
                issues.append(f"Frontmatter is not a mapping in {module}/{slug}")
                continue

            title = str(frontmatter_any.get("title", "")).strip()
            if not title:
                issues.append(f"Missing title in L2 frontmatter for {module}/{slug}")
                continue

            documents[(module, slug)] = L2Document(
                module=module,
                slug=slug,
                title=title,
                body_hash=_body_hash(body),
                path=path,
            )

    return documents, issues


def _iter_store_files(store_root: str) -> list[tuple[str, str, str]]:
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


def _load_json(path: str) -> dict[str, Any] | None:
    """Load a dict-like JSON record from disk when possible."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data: Any = json.load(handle)
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    return data


def _validate_record(
    store_name: str,
    module: str,
    slug: str,
    path: str,
    record: dict[str, Any],
    l2_documents: dict[tuple[str, str], L2Document] | None,
    errors: list[str],
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
        not isinstance(content_hash, str) or not _HASH_RE.fullmatch(content_hash)
    ):
        errors.append(
            f"{store_name} {module}/{slug}: content_hash must be null or 12-char lowercase hex"
        )

    if store_name == "override" and content_hash is not None:
        errors.append(
            f"override {module}/{slug}: content_hash must be null for human-pinned overrides"
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
            f"{store_name} {module}/{slug}: ai_related_topics must be a non-empty list"
        )
    elif not all(isinstance(item, str) and item.strip() for item in related_topics):
        errors.append(
            f"{store_name} {module}/{slug}: ai_related_topics entries must be non-empty strings"
        )

    if not _is_iso_timestamp(record.get("generated_at")):
        errors.append(f"{store_name} {module}/{slug}: generated_at must be ISO 8601 text")

    saved_at = record.get("saved_at")
    if saved_at is not None and not _is_iso_timestamp(saved_at):
        errors.append(f"{store_name} {module}/{slug}: saved_at must be ISO 8601 text")

    model = record.get("model")
    if not isinstance(model, str) or not model.strip():
        errors.append(f"{store_name} {module}/{slug}: model must be non-empty text")

    if record.get("pipeline_version") != "v12":
        errors.append(f"{store_name} {module}/{slug}: pipeline_version must be v12")

    if l2_documents is None:
        return

    document = l2_documents.get((module, slug))
    if document is None:
        errors.append(
            f"{store_name} {module}/{slug}: no matching L2 document found for {path}"
        )
        return

    if isinstance(title, str) and title.strip() and title.strip() != document.title:
        errors.append(
            f"{store_name} {module}/{slug}: title does not match L2 frontmatter"
        )

    if isinstance(content_hash, str) and content_hash != document.body_hash:
        errors.append(
            f"{store_name} {module}/{slug}: content_hash does not match current L2 body"
        )


def main() -> int:
    """Run the CLI validator and return an exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store",
        choices=["base", "override", "both"],
        default="both",
        help="Store selection to validate (default: both)",
    )
    parser.add_argument(
        "--base-dir",
        default=ai_store.AI_DATA_BASE_DIR,
        help="Base AI store root (default: AI_DATA_BASE_DIR)",
    )
    parser.add_argument(
        "--override-dir",
        default=ai_store.AI_DATA_OVERRIDE_DIR,
        help="Override AI store root (default: AI_DATA_OVERRIDE_DIR)",
    )
    parser.add_argument(
        "--l2-root",
        default=os.path.join(config.OUTDIR, "L2-semantic"),
        help="L2 root for cross-checks (default: OUTDIR/L2-semantic)",
    )
    parser.add_argument(
        "--skip-l2-checks",
        action="store_true",
        help="Validate JSON schema only and skip L2 title/hash checks",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=200,
        help="Maximum errors to print before truncating output (default: 200)",
    )
    args = parser.parse_args()

    l2_documents: dict[tuple[str, str], L2Document] | None = None
    if not args.skip_l2_checks:
        l2_documents, issues = _load_l2_documents(args.l2_root)
        if issues:
            for issue in issues:
                print(f"[04b] FAIL: {issue}")
            return 1

    selected_stores: list[tuple[str, str]] = []
    if args.store in {"base", "both"}:
        selected_stores.append(("base", args.base_dir))
    if args.store in {"override", "both"}:
        selected_stores.append(("override", args.override_dir))

    checked_records = 0
    errors: list[str] = []

    for store_name, store_root in selected_stores:
        for module, slug, path in _iter_store_files(store_root):
            checked_records += 1
            record = _load_json(path)
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
            )

    if checked_records == 0:
        print("[04b] FAIL: no JSON records were found in the selected store(s)")
        return 1

    if errors:
        for error in errors[: max(0, args.max_errors)]:
            print(f"[04b] FAIL: {error}")

        remaining = len(errors) - max(0, args.max_errors)
        if remaining > 0:
            print(f"[04b] FAIL: ... {remaining} more errors")

        print(f"[04b] Checked {checked_records} records: FAILED")
        return 1

    print(f"[04b] Checked {checked_records} records: OK")
    if args.skip_l2_checks:
        print("[04b] L2 cross-checks were skipped")
    else:
        print(f"[04b] L2 documents available for cross-check: {len(l2_documents or {})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())