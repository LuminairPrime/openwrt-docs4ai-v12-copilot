"""
openwrt-docs4ai-v10-smoke-test.py

A local runner to test the exact python scripts modified in v10 before allowing them to deploy to GitHub Actions. This runs the logic sequentially and outputs to a safe sandbox directory.
"""

import os
import subprocess
import shutil
import sys

WORKDIR = os.path.abspath("tmp")
OUTDIR = os.path.abspath(os.path.join("tmp", "v10-smoke-test-out"))

# Set environment variables for the subprocesses
os.environ["WORKDIR"] = WORKDIR
os.environ["OUTDIR"] = OUTDIR
os.environ["WIKI_MAX_PAGES"] = "10" # Cap wiki scraping for the smoke test to save time
os.environ["SKIP_AI"] = "true" # Do not run AI summarization locally to save LLM quota
os.environ["SKIP_BUILDROOT"] = "true" # Don't re-parse the 1.5GB openwrt repo C packages just for a smoke test

print("="*60)
print(f"Starting v10 Local Smoke Test")
print(f"OUTDIR : {OUTDIR}")
print(f"WORKDIR: {WORKDIR}")
print("="*60)

# Clean out old smoke test artifacts
if os.path.exists(OUTDIR):
    shutil.rmtree(OUTDIR, ignore_errors=True)
os.makedirs(OUTDIR, exist_ok=True)

# Clean out old git repos that block cloning on Windows
for repo in ["repo-openwrt", "repo-luci", "repo-ucode"]:
    rpath = os.path.join(WORKDIR, repo)
    if os.path.exists(rpath):
        import stat
        # Windows sometimes holds readonly flags on .git objects causing rmtree to fail
        def remove_readonly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(rpath, onerror=remove_readonly)
        
scripts_to_test = [
    ".github/scripts/openwrt-docs4ai-01-clone-repos.py",
    ".github/scripts/openwrt-docs4ai-02b-scrape-ucode.py",
    ".github/scripts/openwrt-docs4ai-02c-scrape-jsdoc.py",
    ".github/scripts/openwrt-docs4ai-02f-scrape-procd-api.py",
    ".github/scripts/openwrt-docs4ai-02h-scrape-hotplug-events.py",
    # Skip wiki completely or run it? Let's run it capped to see frontmatter output:
    ".github/scripts/openwrt-docs4ai-02a-scrape-wiki.py",
    ".github/scripts/openwrt-docs4ai-03-normalize-semantic.py",
    ".github/scripts/openwrt-docs4ai-05a-assemble-references.py",
    ".github/scripts/openwrt-docs4ai-05b-generate-agents-and-readme.py",
    ".github/scripts/openwrt-docs4ai-05c-generate-ucode-ide-schemas.py",
    ".github/scripts/openwrt-docs4ai-05d-generate-api-drift-changelog.py",
    ".github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py",
    ".github/scripts/openwrt-docs4ai-07-generate-web-index.py",
    ".github/scripts/openwrt-docs4ai-08-validate-output.py"
]

for script in scripts_to_test:
    print(f"\n---> Running {script}")
    if not os.path.exists(script):
        print(f"CRITICAL: Script not found: {script}")
        sys.exit(1)
        
    result = subprocess.run([sys.executable, script], env=os.environ, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ FATAL: {script} exited with error code {result.returncode}")
        sys.exit(1)

print("\n" + "="*60)
print("✅ Local Smoke Test Completed Successfully!")
print(f"Check {OUTDIR} for the generated output, *-skeleton.md files, and YAML frontmatter validation.")
