import datetime
import json
import os
import secrets
from typing import cast


_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_RUN_STATE = os.path.join("tmp", "pipeline-run-state.json")


def _resolve_repo_path(raw_path: str) -> str:
    if os.path.isabs(raw_path):
        return raw_path
    return os.path.join(_REPO_ROOT, raw_path)


def _normalize_repo_relative(raw_path: str) -> str:
    absolute_path = os.path.abspath(_resolve_repo_path(raw_path))
    repo_root = os.path.abspath(_REPO_ROOT)

    try:
        if os.path.commonpath([repo_root, absolute_path]) == repo_root:
            return os.path.relpath(absolute_path, repo_root).replace("\\", "/")
    except ValueError:
        pass

    return os.path.normpath(raw_path).replace("\\", "/")


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json_atomic(path: str, payload: dict[str, object]) -> None:
    absolute_path = _resolve_repo_path(path)
    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    temp_path = f"{absolute_path}.tmp"

    with open(temp_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    os.replace(temp_path, absolute_path)


def _read_json(path: str) -> dict[str, object] | None:
    absolute_path = _resolve_repo_path(path)
    if not os.path.isfile(absolute_path):
        return None

    try:
        with open(absolute_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None

    raw_payload = cast(dict[object, object], payload)
    normalized_payload: dict[str, object] = {}
    for key, value in raw_payload.items():
        if not isinstance(key, str):
            return None
        normalized_payload[key] = value

    return normalized_payload


def _read_state_file(path: str) -> str | None:
    payload = _read_json(path)
    if payload is None:
        return None

    pipeline_run_dir = payload.get("pipeline_run_dir")
    if not isinstance(pipeline_run_dir, str) or not pipeline_run_dir.strip():
        return None

    return os.path.normpath(pipeline_run_dir)


def _generate_and_save_new_run_dir() -> str:
    run_id = datetime.datetime.now(datetime.UTC).strftime("pipeline-%Y%m%d-%H%MUTC-") + secrets.token_hex(2)
    run_dir = os.path.join("tmp", run_id)
    _write_json_atomic(
        PIPELINE_RUN_STATE,
        {"pipeline_run_dir": _normalize_repo_relative(run_dir)},
    )
    return run_dir


def _resolve_pipeline_run_dir() -> str:
    env_run_dir = os.environ.get("PIPELINE_RUN_DIR")
    if env_run_dir:
        return os.path.normpath(env_run_dir)

    state_run_dir = _read_state_file(PIPELINE_RUN_STATE)
    if state_run_dir:
        return state_run_dir

    return _generate_and_save_new_run_dir()


PIPELINE_RUN_DIR = _resolve_pipeline_run_dir()
DOWNLOADS_DIR = os.path.normpath(
    os.environ.get("DOWNLOADS_DIR") or os.environ.get("WORKDIR") or os.path.join(PIPELINE_RUN_DIR, "downloads")
)
PROCESSED_DIR = os.path.normpath(os.environ.get("PROCESSED_DIR") or os.path.join(PIPELINE_RUN_DIR, "processed"))
STAGED_DIR = os.path.normpath(
    os.environ.get("STAGED_DIR") or os.environ.get("OUTDIR") or os.path.join(PIPELINE_RUN_DIR, "staged")
)
WORKDIR = DOWNLOADS_DIR
OUTDIR = STAGED_DIR
PACKAGES_DIR = os.path.join(STAGED_DIR, "packages")
RUN_RECORD_PATH = os.path.join(PIPELINE_RUN_DIR, "pipeline-run-record.json")

# Execution Flags & Quotas
SKIP_WIKI = os.environ.get("SKIP_WIKI", "false").lower() == "true"
SKIP_AI = os.environ.get("SKIP_AI", "true").lower() == "true"
WIKI_MAX_PAGES = int(os.environ.get("WIKI_MAX_PAGES", "300"))
MAX_AI_FILES = int(os.environ.get("MAX_AI_FILES", "40"))
LLM_BUDGET_LIMIT = float(os.environ.get("LLM_BUDGET_LIMIT", "5.00").replace("$", ""))
VALIDATE_MODE = os.environ.get("VALIDATE_MODE", "hard")
MERMAID_INJECT = os.environ.get("MERMAID_INJECT", "true").lower() == "true"

# Token & Baseline Configs
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
LOCAL_DEV_TOKEN = os.environ.get("LOCAL_DEV_TOKEN", "")
TOKENIZER = os.environ.get("TOKENIZER", "cl100k_base")
DTS_GENERATE = os.environ.get("DTS_GENERATE", "true").lower() == "true"
BASELINE_SOURCE = os.environ.get("BASELINE_SOURCE", "github-release")

# Computed Paths
L1_RAW_WORKDIR = os.path.join(PROCESSED_DIR, "L1-raw")
L2_SEMANTIC_WORKDIR = os.path.join(PROCESSED_DIR, "L2-semantic")
REPO_MANIFEST_PATH = os.path.join(PROCESSED_DIR, "manifests", "repo-manifest.json")
CROSS_LINK_REGISTRY = os.path.join(PROCESSED_DIR, "manifests", "cross-link-registry.json")

# V5a Release Tree Configuration
RELEASE_TREE_DIR = os.path.join(STAGED_DIR, "release-tree")
SUPPORT_TREE_DIR = os.path.join(STAGED_DIR, "support-tree")

# V5a Public Output Name Constants
MODULE_MAP_FILENAME = "map.md"
MODULE_BUNDLED_REF_FILENAME = "bundled-reference.md"
MODULE_CHUNKED_REF_DIRNAME = "chunked-reference"
MODULE_TYPES_DIRNAME = "types"

# V5a Release Include Paths (relative to repo root)
RELEASE_INCLUDE_DIR = os.path.join(_REPO_ROOT, "static", "release-inputs", "release-include")
PAGES_INCLUDE_DIR = os.path.join(_REPO_ROOT, "static", "release-inputs", "pages-include")

# AI Summary Data Store
# Defaults to static/data/base/ and static/data/override/ relative to the repository root.
# Can be overridden by environment variables for non-standard layouts.
AI_DATA_BASE_DIR = os.environ.get(
    "AI_DATA_BASE_DIR",
    os.path.join(_REPO_ROOT, "static", "data", "base"),
)
AI_DATA_OVERRIDE_DIR = os.environ.get(
    "AI_DATA_OVERRIDE_DIR",
    os.path.join(_REPO_ROOT, "static", "data", "override"),
)


def _run_record_payload(status: str) -> dict[str, object]:
    existing_payload = _read_json(RUN_RECORD_PATH) or {}
    created_utc = existing_payload.get("created_utc")

    return {
        "schema_version": 1,
        "run_id": os.path.basename(os.path.normpath(PIPELINE_RUN_DIR)),
        "created_utc": created_utc if isinstance(created_utc, str) and created_utc else _utc_now_iso(),
        "status": status,
        "pipeline_run_dir": _normalize_repo_relative(PIPELINE_RUN_DIR),
    }


def _write_run_record(status: str) -> None:
    _write_json_atomic(RUN_RECORD_PATH, _run_record_payload(status))


def ensure_dirs() -> None:
    run_dir = _resolve_repo_path(PIPELINE_RUN_DIR)
    run_record_path = _resolve_repo_path(RUN_RECORD_PATH)
    run_dir_exists = os.path.isdir(run_dir)

    directories = [
        _resolve_repo_path(os.path.join("tmp", "logs")),
        run_dir,
        _resolve_repo_path(DOWNLOADS_DIR),
        _resolve_repo_path(os.path.join(DOWNLOADS_DIR, "repos")),
        _resolve_repo_path(os.path.join(DOWNLOADS_DIR, "wiki", "raw")),
        _resolve_repo_path(PROCESSED_DIR),
        _resolve_repo_path(L1_RAW_WORKDIR),
        _resolve_repo_path(L2_SEMANTIC_WORKDIR),
        _resolve_repo_path(os.path.join(PROCESSED_DIR, "manifests")),
        _resolve_repo_path(STAGED_DIR),
        _resolve_repo_path(RELEASE_TREE_DIR),
        _resolve_repo_path(SUPPORT_TREE_DIR),
        _resolve_repo_path(PACKAGES_DIR),
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    if not run_dir_exists or not os.path.isfile(run_record_path):
        _write_run_record("running")


def mark_run_complete() -> None:
    _write_run_record("complete")


def mark_run_failed() -> None:
    _write_run_record("failed")
