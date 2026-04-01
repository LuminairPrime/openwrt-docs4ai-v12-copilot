import importlib.util
import os
import re
import json
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / ".github" / "scripts"
SMOKE_SUPPORT_PATH = PROJECT_ROOT / "tests" / "support" / "smoke_pipeline_support.py"
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "openwrt-docs4ai-00-pipeline.yml"


def _resolve_workspace_path(raw_path: str | None, fallback: Path) -> Path:
    if raw_path:
        candidate = Path(raw_path)
        return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
    return fallback


def _load_pipeline_run_dir() -> Path | None:
    state_path = PROJECT_ROOT / "tmp" / "pipeline-run-state.json"
    if not state_path.is_file():
        return None
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    raw_path = payload.get("pipeline_run_dir")
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    candidate = Path(raw_path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


PIPELINE_RUN_DIR = _load_pipeline_run_dir()
STAGED_DIR = _resolve_workspace_path(
    os.environ.get("STAGED_DIR") or os.environ.get("OUTDIR"),
    (PIPELINE_RUN_DIR / "staged") if PIPELINE_RUN_DIR else (PROJECT_ROOT / "staging"),
)
PROCESSED_DIR = _resolve_workspace_path(
    os.environ.get("PROCESSED_DIR"),
    (PIPELINE_RUN_DIR / "processed") if PIPELINE_RUN_DIR else (PROJECT_ROOT / "processed"),
)
OUTDIR = STAGED_DIR
WIKI_L2_DIR = PROCESSED_DIR / "L2-semantic" / "wiki"

WIKI_ARTIFACT_PATTERNS = {
    "wrap": re.compile(r"(?:\\<|&lt;|<)\s*/?wrap\b", re.IGNORECASE),
    "color": re.compile(r"(?:\\<|&lt;|<)\s*/?color\b", re.IGNORECASE),
    "html_table": re.compile(r"<table|<tr\b|<td\b|<th\b", re.IGNORECASE),
    "sortable": re.compile(r"(?:\\?<\s*/?sortable\b[^>]*\\?>|&lt;\/?sortable\b[^&]*&gt;)", re.IGNORECASE),
    "footnote_aside": re.compile(r"<aside\b[^>]*\bfootnotes\b", re.IGNORECASE),
}


def load_module_from_path(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_script_module(module_name, script_name):
    return load_module_from_path(module_name, SCRIPTS_DIR / script_name)


def load_smoke_support_module(module_name):
    return load_module_from_path(module_name, SMOKE_SUPPORT_PATH)


def load_workflow_text():
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def load_workflow_yaml():
    return yaml.safe_load(load_workflow_text())


def summarize_wiki_l2_corpus(corpus_dir):
    files = sorted(corpus_dir.glob("*.md"))
    summary = {"files": len(files), "duplicate_lead_heading_files": 0}
    for key in WIKI_ARTIFACT_PATTERNS:
        summary[f"{key}_files"] = 0
        summary[f"{key}_occurrences"] = 0

    for markdown_file in files:
        content = markdown_file.read_text(encoding="utf-8")
        for key, pattern in WIKI_ARTIFACT_PATTERNS.items():
            matches = pattern.findall(content)
            if matches:
                summary[f"{key}_files"] += 1
                summary[f"{key}_occurrences"] += len(matches)
        if has_duplicate_lead_heading(content):
            summary["duplicate_lead_heading_files"] += 1

    return summary


def has_duplicate_lead_heading(content):
    top_heading = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            top_heading = stripped[2:].strip().casefold()
            continue
        if stripped.startswith("## "):
            return stripped[3:].strip().casefold() == top_heading
        return False
    return False


def classify_wiki_l2_sanity(summary):
    if summary["files"] < 80:
        return "abnormal"
    if summary["duplicate_lead_heading_files"] > 0:
        return "abnormal"
    for key in WIKI_ARTIFACT_PATTERNS:
        if summary[f"{key}_files"]:
            return "abnormal"
    return "clean"


def get_workflow_job_block(workflow_text, job_name):
    match = re.search(
        rf"^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow_text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"Missing workflow job block: {job_name}"
    return match.group(1)


def collect_workflow_script_invocations(workflow_text):
    explicit_scripts = set(re.findall(r"openwrt-docs4ai-\d{2}[a-z]?-[\w-]+\.py", workflow_text))
    matrix_scripts = {f"openwrt-docs4ai-{name}" for name in re.findall(r'"(02[a-z]-[\w-]+\.py)"', workflow_text)}
    return explicit_scripts | matrix_scripts
