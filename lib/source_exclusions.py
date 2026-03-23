"""
source_exclusions.py — Source-intake exclusion policy loader for V13.

Provides should_exclude(source_type, identifier) to check whether a given
upstream source file should be skipped during L1 ingest. The exclusion list
is loaded from config/source-exclusions.yml at the project root.

Public API:
  should_exclude(source_type, identifier) -> bool
  get_exclusion_reason(source_type, identifier) -> str | None
  get_all_exclusions() -> list[dict]
"""

import os

import yaml

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_POLICY_PATH = os.path.join(_PROJECT_ROOT, "config", "source-exclusions.yml")

_policy: dict | None = None


def _load_policy() -> dict:
    global _policy
    if _policy is None:
        if not os.path.isfile(_POLICY_PATH):
            _policy = {"exclusions": []}
        else:
            with open(_POLICY_PATH, "r", encoding="utf-8") as fh:
                _policy = yaml.safe_load(fh) or {"exclusions": []}
    return _policy


def should_exclude(source_type: str, identifier: str) -> bool:
    """Return True if the given source/identifier combination is excluded by policy."""
    policy = _load_policy()
    for entry in policy.get("exclusions", []):
        if entry.get("source") == source_type and entry.get("identifier") == identifier:
            return True
    return False


def get_exclusion_reason(source_type: str, identifier: str) -> str | None:
    """Return the reason string for an excluded entry, or None if not excluded."""
    policy = _load_policy()
    for entry in policy.get("exclusions", []):
        if entry.get("source") == source_type and entry.get("identifier") == identifier:
            return entry.get("reason", "no reason recorded")
    return None


def get_all_exclusions() -> list:
    """Return a copy of all exclusion entries from the policy."""
    return list(_load_policy().get("exclusions", []))
