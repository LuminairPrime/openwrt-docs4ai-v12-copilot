from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import tools.manage_ai_store as manage_ai_store
from lib.ai_store_workflow import OperationPaths


def _make_operation_paths(tmp_path: Path) -> OperationPaths:
    repo_root = tmp_path / "repo"
    source_outdir = repo_root / "tmp" / "pipeline-test" / "staged"
    permanent_l2_root = repo_root / "tmp" / "pipeline-test" / "processed" / "L2-semantic"
    permanent_base_dir = repo_root / "static" / "data" / "base"
    permanent_override_dir = repo_root / "static" / "data" / "override"
    scratch_root = tmp_path / "scratch"
    scratch_outdir = scratch_root / "out"
    scratch_l2_root = scratch_outdir / "L2-semantic"
    scratch_ai_root = scratch_root / "ai-data"
    scratch_base_dir = scratch_ai_root / "base"
    scratch_override_dir = scratch_ai_root / "override"
    scratch_cache_path = scratch_root / "ai-summaries-cache.json"
    legacy_cache_source = repo_root / "ai-summaries-cache.json"

    return OperationPaths(
        repo_root=repo_root,
        source_outdir=source_outdir,
        permanent_l2_root=permanent_l2_root,
        permanent_base_dir=permanent_base_dir,
        permanent_override_dir=permanent_override_dir,
        scratch_root=scratch_root,
        scratch_outdir=scratch_outdir,
        scratch_l2_root=scratch_l2_root,
        scratch_ai_root=scratch_ai_root,
        scratch_base_dir=scratch_base_dir,
        scratch_override_dir=scratch_override_dir,
        scratch_cache_path=scratch_cache_path,
        legacy_cache_source=legacy_cache_source,
    )


def _mkdir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_main_review_runs_expected_actions_and_keeps_scratch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    paths = _make_operation_paths(tmp_path)
    actions: list[str] = []

    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "build_operation_paths",
        lambda scratch_root: paths,
    )

    def fake_execute_action(action: str, *, paths: OperationPaths, args: SimpleNamespace) -> None:
        actions.append(action)

    monkeypatch.setattr(manage_ai_store, "execute_action", fake_execute_action)
    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "cleanup_scratch",
        lambda paths: pytest.fail("cleanup_scratch should not run when --keep-scratch is set"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "manage_ai_store.py",
            "--option",
            "review",
            "--no-write-ai",
            "--keep-scratch",
        ],
    )

    assert manage_ai_store.main() == 0
    assert actions == ["prepare", "generate", "validate", "audit"]


def test_main_full_cleans_scratch_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    paths = _make_operation_paths(tmp_path)
    actions: list[str] = []
    cleanup_calls: list[Path] = []

    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "build_operation_paths",
        lambda scratch_root: paths,
    )

    def fake_execute_action(action: str, *, paths: OperationPaths, args: SimpleNamespace) -> None:
        actions.append(action)

    monkeypatch.setattr(manage_ai_store, "execute_action", fake_execute_action)
    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "cleanup_scratch",
        lambda paths: cleanup_calls.append(paths.scratch_root),
    )
    monkeypatch.setattr(sys, "argv", ["manage_ai_store.py", "--option", "full"])

    assert manage_ai_store.main() == 0
    assert actions == ["prepare", "generate", "validate", "audit", "promote"]
    assert cleanup_calls == [paths.scratch_root]


def test_main_returns_failure_when_generate_cannot_resolve_token(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    paths = _make_operation_paths(tmp_path)
    _mkdir(paths.scratch_base_dir)
    _mkdir(paths.scratch_override_dir)
    _mkdir(paths.scratch_l2_root)

    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "build_operation_paths",
        lambda scratch_root: paths,
    )
    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "resolve_token_value",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("missing token")),
    )
    monkeypatch.setattr(sys, "argv", ["manage_ai_store.py", "--option", "generate"])

    assert manage_ai_store.main() == 1
    output = capsys.readouterr().out
    assert "FAIL: missing token" in output


def test_run_generate_passes_token_and_cap_to_enrichment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    paths = _make_operation_paths(tmp_path)
    _mkdir(paths.scratch_base_dir)
    _mkdir(paths.scratch_override_dir)
    _mkdir(paths.scratch_l2_root)
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "resolve_token_value",
        lambda **kwargs: ("secret-token", "LOCAL_DEV_TOKEN"),
    )

    def fake_run_ai_enrichment(**kwargs: object) -> int:
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(
        manage_ai_store.ai_enrichment,
        "run_ai_enrichment",
        fake_run_ai_enrichment,
    )

    args = SimpleNamespace(write_ai=True, token_env=None, max_ai_files=7)
    manage_ai_store.run_generate(paths, args)

    assert captured["outdir"] == str(paths.scratch_outdir)
    assert captured["base_dir"] == str(paths.scratch_base_dir)
    assert captured["override_dir"] == str(paths.scratch_override_dir)
    assert captured["legacy_cache_path"] == str(paths.scratch_cache_path)
    assert captured["write_ai"] is True
    assert captured["max_files"] == 7
    assert captured["token"] == "secret-token"

    output = capsys.readouterr().out
    assert "Using token from LOCAL_DEV_TOKEN" in output


def test_run_generate_raises_when_enrichment_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    paths = _make_operation_paths(tmp_path)
    _mkdir(paths.scratch_base_dir)
    _mkdir(paths.scratch_override_dir)
    _mkdir(paths.scratch_l2_root)

    monkeypatch.setattr(
        manage_ai_store.ai_store_workflow,
        "resolve_token_value",
        lambda **kwargs: ("secret-token", "LOCAL_DEV_TOKEN"),
    )
    monkeypatch.setattr(
        manage_ai_store.ai_enrichment,
        "run_ai_enrichment",
        lambda **kwargs: 1,
    )

    args = SimpleNamespace(write_ai=True, token_env=None, max_ai_files=3)
    with pytest.raises(RuntimeError, match="AI generation failed"):
        manage_ai_store.run_generate(paths, args)


def test_run_promote_copies_reviewed_json_and_rechecks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    paths = _make_operation_paths(tmp_path)
    scratch_file = _mkdir(paths.scratch_base_dir / "ucode") / "sample-doc.json"
    scratch_file.write_text('{"slug": "sample-doc"}', encoding="utf-8")

    validate_calls: list[tuple[Path, Path, Path]] = []
    audit_calls: list[tuple[Path, Path, Path, bool]] = []

    monkeypatch.setattr(
        manage_ai_store,
        "run_validate_for_paths",
        lambda *, base_dir, override_dir, l2_root: validate_calls.append((base_dir, override_dir, l2_root)),
    )
    monkeypatch.setattr(
        manage_ai_store,
        "run_audit_for_paths",
        lambda *, base_dir, override_dir, l2_root, strict_audit: audit_calls.append(
            (base_dir, override_dir, l2_root, strict_audit)
        ),
    )

    manage_ai_store.run_promote(paths, strict_audit=True)

    promoted = paths.permanent_base_dir / "ucode" / "sample-doc.json"
    assert promoted.is_file()
    assert promoted.read_text(encoding="utf-8") == '{"slug": "sample-doc"}'
    assert validate_calls == [(paths.permanent_base_dir, paths.permanent_override_dir, paths.permanent_l2_root)]
    assert audit_calls == [
        (
            paths.permanent_base_dir,
            paths.permanent_override_dir,
            paths.permanent_l2_root,
            True,
        )
    ]
