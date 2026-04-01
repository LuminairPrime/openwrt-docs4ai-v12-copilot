"""Shared helpers for reading L2 semantic markdown documents."""

import hashlib
import os
import re
from dataclasses import dataclass
from typing import Any, cast


_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)", re.DOTALL)


@dataclass(frozen=True)
class L2Document:
    """Minimal L2 metadata used by AI store validation and audit logic."""

    module: str
    slug: str
    title: str
    path: str
    body_hash: str


def body_hash(body_text: str) -> str:
    """Return the canonical 12-character L2 body hash."""
    return hashlib.sha256(body_text.encode("utf-8")).hexdigest()[:12]


def split_frontmatter(content: str) -> tuple[str | None, str | None]:
    """Split markdown into frontmatter and body when YAML is present."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2)


def load_l2_documents(
    l2_root: str,
) -> tuple[dict[tuple[str, str], L2Document], list[str]]:
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

            frontmatter_text, body = split_frontmatter(content)
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

            frontmatter = cast(dict[str, object], frontmatter_any)
            frontmatter_title = frontmatter.get("title", "")
            title = str(frontmatter_title).strip() or slug
            documents[(module, slug)] = L2Document(
                module=module,
                slug=slug,
                title=title,
                path=path,
                body_hash=body_hash(body),
            )

    return documents, issues
