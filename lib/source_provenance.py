"""
source_provenance.py — V13 provenance helpers for L1 ingest scripts.

Provides deterministic URL construction and a set of known git-backed
origin_type values. All 02* scripts that write .meta.json sidecars should
import from this module instead of hard-coding URL patterns.

Usage (git-backed extractor):
    from lib.source_provenance import make_git_source_url, GIT_BACKED_ORIGIN_TYPES

    source_url = make_git_source_url(REPO_BASE, commit_sha, upstream_path)

Usage (wiki extractor):
    # source_url is already the full wiki page URL — use it as-is.
    # No helper needed; just rename the field from original_url to source_url.
"""

# ---------------------------------------------------------------------------
# Repo base URLs (no trailing slash)
# ---------------------------------------------------------------------------

REPO_BASE_OPENWRT = "https://github.com/openwrt/openwrt"
REPO_BASE_LUCI = "https://github.com/openwrt/luci"
REPO_BASE_UCODE = "https://github.com/nicowillis/ucode"

# ---------------------------------------------------------------------------
# Git-backed origin types (require source_commit in L2)
# ---------------------------------------------------------------------------

GIT_BACKED_ORIGIN_TYPES: frozenset[str] = frozenset(
    {
        "readme",
        "c_source",
        "js_source",
        "makefile_meta",
        "example_app",
        "header_api",
        "uci_schema",
        "hotplug_event",
    }
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_git_source_url(repo_base: str, commit: str, upstream_path: str) -> str:
    """
    Build a dereferenceable GitHub blob URL from repo base, commit SHA,
    and the relative file path within the repository.

    Args:
        repo_base:      Base repository URL without trailing slash,
                        e.g. REPO_BASE_OPENWRT.
        commit:         Full or abbreviated commit SHA, e.g. "abc1234".
                        If empty or "unknown", the URL is still returned but
                        will point to HEAD via the literal string "unknown",
                        which is acceptable for debugging.
        upstream_path:  Relative path within the repo, e.g.
                        "package/system/procd/files/procd.sh".
                        Leading slashes are stripped.

    Returns:
        A string of the form:
            {repo_base}/blob/{commit}/{upstream_path}
    """
    clean_path = upstream_path.lstrip("/")
    return f"{repo_base}/blob/{commit}/{clean_path}"
