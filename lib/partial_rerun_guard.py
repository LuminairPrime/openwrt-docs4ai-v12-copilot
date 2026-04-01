from __future__ import annotations

import os
from typing import Iterable


def collect_directory_modules(root: str) -> set[str]:
    """Return module directory names under one pipeline root."""
    if not os.path.isdir(root):
        return set()

    return {name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name))}


def find_missing_modules_for_partial_rerun(
    incoming_modules: Iterable[str],
    existing_root: str,
) -> list[str]:
    """Return existing modules that would be deleted by a strict-subset rerun."""
    existing_modules = collect_directory_modules(existing_root)
    if not existing_modules:
        return []

    incoming_set = {module for module in incoming_modules if module}
    if incoming_set < existing_modules:
        return sorted(existing_modules - incoming_set)

    return []
