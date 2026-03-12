"""
Purpose: Audit AI summary coverage against the current L2 corpus.
Phase: AI Maintenance (Read-only)
Layers: L2 + AI data store -> stdout
Inputs:  - OUTDIR/L2-semantic/              (required L2 source)
         - data/base/{module}/{slug}.json   (base data store)
         - data/override/{module}/{slug}.json (override data store)
Outputs: - Summary report to stdout only
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
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, DefaultDict

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)

from lib import ai_store, config

_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)", re.DOTALL)


@dataclass(frozen=True)
class L2Document:
    """Minimal L2 metadata needed for AI store coverage checks."""

    module: str
    slug: str
    title: str
    path: str
    body_hash: str


def _body_hash(body_text: str) -> str:
    """Return the canonical 12-character L2 body hash."""
    return hashlib.sha256(body_text.encode("utf-8")).hexdigest()[:12]


def _split_frontmatter(content: str) -> tuple[str | None, str | None]:
    """Split markdown into frontmatter and body when YAML is present."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2)


def _load_json_record(path: str) -> dict[str, Any] | None:
    """Load a dict-like JSON record from disk when possible."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data: Any = json.load(handle)
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    return data


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

            title = str(frontmatter_any.get("title", "")).strip() or slug
            documents[(module, slug)] = L2Document(
                module=module,
                slug=slug,
                title=title,
                path=path,
                body_hash=_body_hash(body),
            )

    return documents, issues


def _classify_record(record: dict[str, Any], body_hash: str) -> str:
    """Return the active record status for a matching L2 document."""
    stored_hash = record.get("content_hash")
    if stored_hash is None:
        return "pinned"
    if stored_hash == body_hash:
        return "current"
    return "stale"


def _append_detail(
    details: DefaultDict[str, list[str]],
    category: str,
    item: str,
) -> None:
    """Append one human-readable detail line to a grouped category."""
    details[category].append(item)


def _walk_store_paths(store_root: str) -> list[tuple[str, str, str]]:
    """Return all JSON record paths beneath a store root."""
    paths: list[tuple[str, str, str]] = []

    if not os.path.isdir(store_root):
        return paths

    for module in sorted(os.listdir(store_root)):
        module_dir = os.path.join(store_root, module)
        if not os.path.isdir(module_dir):
            continue
        for filename in sorted(os.listdir(module_dir)):
            if not filename.endswith(".json"):
                continue
            slug = filename[:-5]
            paths.append((module, slug, os.path.join(module_dir, filename)))

    return paths


def audit_store(
    l2_root: str,
    base_dir: str,
    override_dir: str,
) -> tuple[Counter[str], DefaultDict[str, list[str]], list[str]]:
    """Audit store coverage, staleness, and orphaned records."""
    counts: Counter[str] = Counter()
    details: DefaultDict[str, list[str]] = defaultdict(list)
    l2_documents, issues = _load_l2_documents(l2_root)

    if issues:
        return counts, details, issues

    l2_keys = set(l2_documents)
    counts["l2_documents"] = len(l2_documents)

    for document in l2_documents.values():
        key = (document.module, document.slug)
        override_path = os.path.join(override_dir, document.module, f"{document.slug}.json")
        base_path = os.path.join(base_dir, document.module, f"{document.slug}.json")

        if os.path.isfile(override_path):
            record = _load_json_record(override_path)
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
            record = _load_json_record(base_path)
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
        for module, slug, path in _walk_store_paths(store_root):
            if (module, slug) in l2_keys:
                continue
            counts[f"orphan_{store_name}"] += 1
            _append_detail(
                details,
                "orphan",
                f"{store_name} {module}/{slug} ({path})",
            )

    return counts, details, issues


def _print_details(
    details: DefaultDict[str, list[str]],
    categories: list[str],
    detail_limit: int,
) -> None:
    """Print bounded detail sections for selected categories."""
    for category in categories:
        entries = details.get(category, [])
        if not entries:
            continue

        print(f"[04a] {category} detail ({len(entries)}):")
        for item in entries[:detail_limit]:
            print(f"  - {item}")

        remaining = len(entries) - detail_limit
        if remaining > 0:
            print(f"  ... {remaining} more")


def main() -> int:
    """Run the CLI audit and return an exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--l2-root",
        default=os.path.join(config.OUTDIR, "L2-semantic"),
        help="L2 root to audit (default: OUTDIR/L2-semantic)",
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
        "--show",
        action="append",
        choices=["missing", "stale", "orphan", "invalid", "current", "pinned", "all"],
        default=[],
        help="Detail categories to print (repeatable)",
    )
    parser.add_argument(
        "--detail-limit",
        type=int,
        default=20,
        help="Maximum detail lines per category (default: 20)",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit non-zero when missing records are found",
    )
    parser.add_argument(
        "--fail-on-stale",
        action="store_true",
        help="Exit non-zero when stale records are found",
    )
    parser.add_argument(
        "--fail-on-orphan",
        action="store_true",
        help="Exit non-zero when orphaned records are found",
    )
    parser.add_argument(
        "--fail-on-invalid",
        action="store_true",
        help="Exit non-zero when invalid JSON records are found",
    )
    args = parser.parse_args()

    counts, details, issues = audit_store(
        l2_root=args.l2_root,
        base_dir=args.base_dir,
        override_dir=args.override_dir,
    )

    if issues:
        for issue in issues:
            print(f"[04a] FAIL: {issue}")
        return 1

    current_total = counts["base_current"] + counts["override_current"]
    pinned_total = counts["base_pinned"] + counts["override_pinned"]
    stale_total = counts["base_stale"] + counts["override_stale"]
    orphan_total = counts["orphan_base"] + counts["orphan_override"]
    invalid_total = counts["invalid_base"] + counts["invalid_override"]

    print(f"[04a] L2 documents: {counts['l2_documents']}")
    print(
        "[04a] Active coverage: "
        f"current={current_total}, "
        f"pinned={pinned_total}, "
        f"stale={stale_total}, "
        f"missing={counts['missing']}"
    )
    print(
        "[04a] Active sources: "
        f"base_current={counts['base_current']}, "
        f"base_pinned={counts['base_pinned']}, "
        f"base_stale={counts['base_stale']}, "
        f"override_current={counts['override_current']}, "
        f"override_pinned={counts['override_pinned']}, "
        f"override_stale={counts['override_stale']}"
    )
    print(
        "[04a] Store hygiene: "
        f"orphan_base={counts['orphan_base']}, "
        f"orphan_override={counts['orphan_override']}, "
        f"invalid_base={counts['invalid_base']}, "
        f"invalid_override={counts['invalid_override']}"
    )

    categories = list(args.show)
    if "all" in categories:
        categories = ["missing", "stale", "orphan", "invalid", "current", "pinned"]
    elif not categories:
        categories = [
            category
            for category, value in (
                ("missing", counts["missing"]),
                ("stale", stale_total),
                ("orphan", orphan_total),
                ("invalid", invalid_total),
            )
            if value > 0
        ]

    _print_details(details, categories, max(0, args.detail_limit))

    failures: list[str] = []
    if args.fail_on_missing and counts["missing"]:
        failures.append(f"missing={counts['missing']}")
    if args.fail_on_stale and stale_total:
        failures.append(f"stale={stale_total}")
    if args.fail_on_orphan and orphan_total:
        failures.append(f"orphan={orphan_total}")
    if args.fail_on_invalid and invalid_total:
        failures.append(f"invalid={invalid_total}")

    if failures:
        print(f"[04a] FAIL: {', '.join(failures)}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())