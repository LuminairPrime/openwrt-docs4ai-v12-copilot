"""
openwrt-docs4ai-01-clone-repos.py

Purpose  : Clone upstream source repositories needed by the scraper scripts.
Env Vars : WORKDIR (default: ./tmp) — where to clone repos
           SKIP_BUILDROOT ("true" to skip the large openwrt/openwrt clone)
Outputs  : $WORKDIR/repo-ucode/    (jow-/ucode, depth=1)
           $WORKDIR/repo-luci/     (openwrt/luci, depth=1)
           $WORKDIR/repo-openwrt/  (openwrt/openwrt, sparse checkout, depth=1)
           Sets UCODE_COMMIT, LUCI_COMMIT, OPENWRT_COMMIT env vars for CI
Deps     : git (system binary)
Notes    : Clones are shallow (--depth=1) to minimize bandwidth.
           The openwrt repo uses sparse checkout to fetch only package/ and include/.
"""

import os
import sys
import subprocess
import shutil
import datetime
import json

sys.stdout.reconfigure(line_buffering=True)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import repo_manifest

WORKDIR = os.environ.get("WORKDIR", os.path.join(os.getcwd(), "tmp"))
SKIP_BUILDROOT = os.environ.get("SKIP_BUILDROOT", "false").lower() == "true"
GITHUB_ENV = os.environ.get("GITHUB_ENV")
MANIFEST_PATH = os.path.join(WORKDIR, "repo-manifest.json")

os.makedirs(WORKDIR, exist_ok=True)

def run(cmd, **kwargs):
    """Run a command and exit on failure."""
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"[01] FAIL: command returned {result.returncode}: {' '.join(cmd)}")
        sys.exit(1)
    return result

def get_commit(repo_dir):
    """Get the short commit hash of a cloned repo."""
    result = subprocess.run(
        ["git", "-C", repo_dir, "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            f"git rev-parse failed for {repo_dir} with exit {result.returncode}: {stderr or 'no stderr'}"
        )

    try:
        return repo_manifest.validate_commit_hash(result.stdout, label=f"commit for {repo_dir}")
    except repo_manifest.ManifestError as exc:
        raise RuntimeError(str(exc)) from exc

def set_env(name, value):
    """Write an env var to GITHUB_ENV for subsequent CI steps."""
    if GITHUB_ENV:
        with open(GITHUB_ENV, "a") as f:
            f.write(f"{name}={value}\n")
    os.environ[name] = value

def clone_repo(url, dest, label, sparse_paths=None):
    """Clone a git repo into WORKDIR. Supports sparse checkout."""
    dest_path = os.path.join(WORKDIR, dest)

    # Clean up if leftover from a previous run
    if os.path.isdir(dest_path):
        print(f"[01] Removing existing {dest}/")
        shutil.rmtree(dest_path, ignore_errors=True)

    print(f"[01] Cloning {label}...")

    if sparse_paths:
        run(["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", url, dest_path])
        run(["git", "-C", dest_path, "sparse-checkout", "set"] + sparse_paths)
    else:
        run(["git", "clone", "--depth=1", url, dest_path])

    commit = get_commit(dest_path)
    print(f"[01] OK: {label} @ {commit}")
    return commit


# --- Main ---

def main():
    print("[01] Phase 1: Clone upstream repositories")

    try:
        ucode_commit = clone_repo(
            "https://github.com/jow-/ucode.git",
            "repo-ucode", "ucode"
        )
        set_env("UCODE_COMMIT", ucode_commit)

        luci_commit = clone_repo(
            "https://github.com/openwrt/luci.git",
            "repo-luci", "LuCI"
        )
        set_env("LUCI_COMMIT", luci_commit)

        openwrt_commit = "skipped"
        if not SKIP_BUILDROOT:
            openwrt_commit = clone_repo(
                "https://github.com/openwrt/openwrt.git",
                "repo-openwrt", "OpenWrt buildroot (sparse)",
                sparse_paths=[
                    "package/network", "package/kernel", "package/utils",
                    "package/system", "package/libs", "package/firmware",
                    "package/boot", "package/multimedia", "include", "scripts"
                ]
            )
            set_env("OPENWRT_COMMIT", openwrt_commit)

        manifest = {
            "ucode": ucode_commit,
            "luci": luci_commit,
            "openwrt": openwrt_commit,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"[01] OK: Manifest written to {MANIFEST_PATH}")
        print("[01] Phase 1 complete.")
        return 0
    except Exception as exc:
        print(f"[01] FAIL: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
