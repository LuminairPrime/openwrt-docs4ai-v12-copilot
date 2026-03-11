import os

# Base Directories
WORKDIR = os.environ.get("WORKDIR", "tmp")
OUTDIR = os.environ.get("OUTDIR", "openwrt-condensed-docs")

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
L1_RAW_WORKDIR = os.path.join(WORKDIR, "L1-raw")
L2_SEMANTIC_WORKDIR = os.path.join(WORKDIR, "L2-semantic")
REPO_MANIFEST_PATH = os.path.join(WORKDIR, "repo-manifest.json")
CROSS_LINK_REGISTRY = os.path.join(WORKDIR, "cross-link-registry.json")

# AI Summary Data Store
# Defaults to data/base/ and data/override/ relative to the repository root.
# Can be overridden by environment variables for non-standard layouts.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_DATA_BASE_DIR = os.environ.get(
    "AI_DATA_BASE_DIR",
    os.path.join(_REPO_ROOT, "data", "base"),
)
AI_DATA_OVERRIDE_DIR = os.environ.get(
    "AI_DATA_OVERRIDE_DIR",
    os.path.join(_REPO_ROOT, "data", "override"),
)


def ensure_dirs():
    os.makedirs(WORKDIR, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(L1_RAW_WORKDIR, exist_ok=True)
    os.makedirs(L2_SEMANTIC_WORKDIR, exist_ok=True)
