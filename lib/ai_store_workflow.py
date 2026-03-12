"""Scratch-first workflow helpers for AI summary store operations."""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from lib import config


OPTION_CHOICES = (
    "prepare",
    "generate",
    "validate",
    "audit",
    "review",
    "promote",
    "full",
    "cleanup",
)


@dataclass(frozen=True)
class OperationPaths:
    """Filesystem layout for permanent and scratch AI-store operations."""

    repo_root: Path
    source_outdir: Path
    permanent_l2_root: Path
    permanent_base_dir: Path
    permanent_override_dir: Path
    scratch_root: Path
    scratch_outdir: Path
    scratch_l2_root: Path
    scratch_ai_root: Path
    scratch_base_dir: Path
    scratch_override_dir: Path
    scratch_cache_path: Path
    legacy_cache_source: Path


def _resolve_repo_path(repo_root: Path, raw_path: str) -> Path:
    """Resolve one repo-relative path into an absolute filesystem location."""
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return repo_root / path


def build_operation_paths(scratch_root: str) -> OperationPaths:
    """Resolve permanent and scratch paths from repo config and CLI input."""
    repo_root = Path(__file__).resolve().parents[1]
    scratch_path = _resolve_repo_path(repo_root, scratch_root)
    source_outdir = _resolve_repo_path(repo_root, config.OUTDIR)

    return OperationPaths(
        repo_root=repo_root,
        source_outdir=source_outdir,
        permanent_l2_root=source_outdir / "L2-semantic",
        permanent_base_dir=_resolve_repo_path(repo_root, config.AI_DATA_BASE_DIR),
        permanent_override_dir=_resolve_repo_path(
            repo_root,
            config.AI_DATA_OVERRIDE_DIR,
        ),
        scratch_root=scratch_path,
        scratch_outdir=scratch_path / "out",
        scratch_l2_root=scratch_path / "out" / "L2-semantic",
        scratch_ai_root=scratch_path / "ai-data",
        scratch_base_dir=scratch_path / "ai-data" / "base",
        scratch_override_dir=scratch_path / "ai-data" / "override",
        scratch_cache_path=scratch_path / "ai-summaries-cache.json",
        legacy_cache_source=repo_root / "ai-summaries-cache.json",
    )


def expand_option_sequence(option: str) -> list[str]:
    """Expand compound CLI modes into the concrete action order."""
    if option == "review":
        return ["prepare", "generate", "validate", "audit"]
    if option == "full":
        return ["prepare", "generate", "validate", "audit", "promote"]
    return [option]


def ensure_directory_exists(path: Path, description: str) -> None:
    """Require one directory to exist before an operation proceeds."""
    if not path.is_dir():
        raise FileNotFoundError(f"Missing {description}: {path}")


def prepare_scratch(paths: OperationPaths) -> None:
    """Reset the scratch root and copy the current stores plus L2 corpus."""
    ensure_directory_exists(paths.permanent_base_dir, "base store")
    ensure_directory_exists(paths.permanent_override_dir, "override store")
    ensure_directory_exists(paths.permanent_l2_root, "L2 semantic corpus")

    if paths.scratch_root.exists():
        shutil.rmtree(paths.scratch_root)

    paths.scratch_root.mkdir(parents=True, exist_ok=True)

    shutil.copytree(paths.permanent_base_dir, paths.scratch_base_dir)
    shutil.copytree(paths.permanent_override_dir, paths.scratch_override_dir)
    shutil.copytree(paths.permanent_l2_root, paths.scratch_l2_root)

    if paths.legacy_cache_source.is_file():
        shutil.copy2(paths.legacy_cache_source, paths.scratch_cache_path)


def resolve_token_value(
    *,
    write_ai: bool,
    token_env: str | None,
    environ: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Resolve the token used for live AI generation when write_ai is enabled."""
    if not write_ai:
        return None, None

    env = os.environ if environ is None else environ
    candidates: Sequence[str]
    if token_env:
        candidates = (token_env,)
    else:
        candidates = ("LOCAL_DEV_TOKEN", "GITHUB_TOKEN")

    for name in candidates:
        value = str(env.get(name, "")).strip()
        if value:
            return value, name

    if token_env:
        raise RuntimeError(
            f"Live AI generation requested, but {token_env} is empty. "
            "Set that variable or rerun with --no-write-ai."
        )

    raise RuntimeError(
        "Live AI generation requested, but neither LOCAL_DEV_TOKEN nor "
        "GITHUB_TOKEN is set. Export one of them or rerun with --no-write-ai."
    )


def promote_base_records(source_root: Path, target_root: Path) -> int:
    """Copy scratch JSON records into the permanent base store without deletion."""
    ensure_directory_exists(source_root, "scratch base store")
    target_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    for source_path in sorted(source_root.rglob("*.json")):
        relative_path = source_path.relative_to(source_root)
        destination_path = target_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)
        copied += 1

    if copied == 0:
        raise RuntimeError(
            f"No JSON records found beneath scratch base store: {source_root}"
        )

    return copied


def cleanup_scratch(paths: OperationPaths) -> None:
    """Remove the scratch root if it exists."""
    if paths.scratch_root.exists():
        shutil.rmtree(paths.scratch_root)