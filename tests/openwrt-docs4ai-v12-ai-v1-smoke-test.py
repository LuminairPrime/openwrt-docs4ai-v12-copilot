"""
openwrt-docs4ai-v12-ai-v1-smoke-test.py

Purpose  : Validate AI-V1 data store schema, prompt contract, and ai_store helpers.
Inputs   : data/base/**/*.json, script 04 prompt block, data/base/README prompt block.
Outputs  : Prints pass/fail checks to stdout and exits non-zero on failure.
Notes    : Does not require network access or API tokens.
"""

from __future__ import annotations

import json
import os
import tempfile
import sys
from typing import Any

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from lib import ai_store

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


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def validate_base_store_schema() -> tuple[int, dict[str, int]]:
    base_root = os.path.join(PROJECT_ROOT, "data", "base")
    _assert(os.path.isdir(base_root), f"Missing data/base directory: {base_root}")

    total = 0
    counts: dict[str, int] = {}

    for module in sorted(os.listdir(base_root)):
        module_dir = os.path.join(base_root, module)
        if not os.path.isdir(module_dir):
            continue

        module_count = 0
        for fname in sorted(os.listdir(module_dir)):
            if not fname.endswith(".json"):
                continue

            total += 1
            module_count += 1
            slug = fname[:-5]
            path = os.path.join(module_dir, fname)

            with open(path, "r", encoding="utf-8") as handle:
                data: Any = json.load(handle)

            _assert(isinstance(data, dict), f"Record is not a JSON object: {path}")

            for field in REQUIRED_FIELDS:
                _assert(field in data, f"Missing required field '{field}' in {path}")

            _assert(data["slug"] == slug, f"Slug mismatch in {path}")
            _assert(data["module"] == module, f"Module mismatch in {path}")
            _assert(data["pipeline_version"] == "v12", f"pipeline_version must be v12 in {path}")

            _assert(isinstance(data["ai_summary"], str) and data["ai_summary"].strip(), f"ai_summary empty in {path}")
            _assert(isinstance(data["ai_when_to_use"], str) and data["ai_when_to_use"].strip(), f"ai_when_to_use empty in {path}")

            related = data["ai_related_topics"]
            _assert(isinstance(related, list) and len(related) >= 1, f"ai_related_topics invalid in {path}")
            _assert(all(isinstance(item, str) and item.strip() for item in related), f"ai_related_topics has invalid entries in {path}")

            content_hash = data["content_hash"]
            valid_hash = content_hash is None or (
                isinstance(content_hash, str)
                and len(content_hash) == 12
                and all(ch in "0123456789abcdef" for ch in content_hash)
            )
            _assert(valid_hash, f"content_hash must be null or 12-char lowercase hex in {path}")

        if module_count > 0:
            counts[module] = module_count

    _assert(total > 0, "No JSON records found under data/base")
    return total, counts


def validate_prompt_contract() -> None:
    script_04 = _read_text(
        os.path.join(PROJECT_ROOT, ".github", "scripts", "openwrt-docs4ai-04-generate-ai-summaries.py")
    )
    base_readme = _read_text(os.path.join(PROJECT_ROOT, "data", "base", "README.md"))

    expected_fragments = (
        "Sentence 1",
        "comprehensive",
        "remaining sentences",
    )

    for fragment in expected_fragments:
        _assert(fragment in script_04, f"Prompt contract fragment missing in script 04: {fragment}")
        _assert(fragment in base_readme, f"Prompt contract fragment missing in data/base/README.md: {fragment}")


def validate_ai_store_roundtrip() -> None:
    old_base = ai_store.AI_DATA_BASE_DIR
    old_override = ai_store.AI_DATA_OVERRIDE_DIR

    with tempfile.TemporaryDirectory(prefix="ai-v1-store-test-") as tmp_dir:
        ai_store.AI_DATA_BASE_DIR = os.path.join(tmp_dir, "base")
        ai_store.AI_DATA_OVERRIDE_DIR = os.path.join(tmp_dir, "override")

        try:
            seed = {
                "slug": "sample-doc",
                "module": "ucode",
                "title": "Sample Title",
                "content_hash": "0123456789ab",
                "ai_summary": "Describe the module in one sentence.",
                "ai_when_to_use": "Use when validating store helpers.",
                "ai_related_topics": ["sample.func"],
                "model": "manual",
                "pipeline_version": "v12",
            }

            ai_store.save_summary("ucode", "sample-doc", seed)
            status_ok, record_ok = ai_store.load_summary("ucode", "sample-doc", current_hash="0123456789ab")
            _assert(status_ok == "ok" and record_ok is not None, "Expected ok status on hash match")
            _assert(
                isinstance(record_ok.get("generated_at"), str)
                and str(record_ok.get("generated_at")).strip(),
                "Expected save_summary to add generated_at when missing",
            )

            status_stale, record_stale = ai_store.load_summary("ucode", "sample-doc", current_hash="ffffffffffff")
            _assert(status_stale == "stale" and record_stale is not None, "Expected stale status on hash mismatch")

            created = ai_store.create_override_from_base("ucode", "sample-doc")
            _assert(created, "Expected override creation to succeed")

            status_override, record_override = ai_store.load_summary("ucode", "sample-doc", current_hash="ffffffffffff")
            _assert(status_override == "ok" and record_override is not None, "Override with null hash should be always valid")
            _assert(record_override.get("content_hash") is None, "Override should force content_hash to null")
            _assert(record_override.get("model") == "manual-override", "Override should mark model as manual-override")
        finally:
            ai_store.AI_DATA_BASE_DIR = old_base
            ai_store.AI_DATA_OVERRIDE_DIR = old_override


def main() -> int:
    total, counts = validate_base_store_schema()
    validate_prompt_contract()
    validate_ai_store_roundtrip()

    print("AI-V1 smoke test passed")
    print(f"Total base records: {total}")
    for module, count in sorted(counts.items()):
        print(f"  {module}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
