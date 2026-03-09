"""
Purpose: Strict CI/CD gatekeeper validating all documentation layers.
Phase: Validation
Layers: L1, L2, L3, L4, L5
Inputs: OUTDIR/
Outputs: Validation report to stdout
Environment Variables: OUTDIR, VALIDATE_MODE (hard/soft)
Dependencies: lib.config, pyyaml
Notes: Implements hard fails for 0-byte files, broken links, malformed YAML, and 404 HTML.
       Soft warnings for AST issues and token overflows.
"""

import os
import re
import yaml
import glob
import sys
import subprocess
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

OUTDIR = os.environ.get("OUTDIR", config.OUTDIR)
VALIDATE_MODE = os.environ.get("VALIDATE_MODE", "hard").lower()
if "--warn-only" in sys.argv:
    VALIDATE_MODE = "soft"

print(f"[08] Security & Quality Validation ({OUTDIR}) [Mode: {VALIDATE_MODE}]")

hard_failures = []
soft_warnings = []

RELATIVE_MD_LINK_RE = re.compile(
    r'\[[^\]\n]+\]\(((?!https?:\/\/|mailto:|[a-z0-9]+:)[^)\s]+?\.md(?:#[^)\s]+)?)\)',
    re.IGNORECASE,
)

def hard_fail(msg):
    hard_failures.append(msg)
    print(f"[08] FAIL: {msg}")

def soft_warn(msg):
    soft_warnings.append(msg)
    print(f"[08] WARN: {msg}")

# ============================================================
# Check 1: Structural Integrity (L3 Entry Points)
# ============================================================
CORE_FILES = ["llms.txt", "llms-full.txt", "AGENTS.md", "README.md", "index.html"]
for f in CORE_FILES:
    if not os.path.isfile(os.path.join(OUTDIR, f)):
        hard_fail(f"Missing core L3 file: {f}")

# Registry Schema Validation
import json
registry_path = os.path.join(OUTDIR, "cross-link-registry.json")
if os.path.isfile(registry_path):
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            reg = json.load(f)
        if "symbols" not in reg or "pipeline_date" not in reg:
            hard_fail("cross-link-registry.json missing core fields ('symbols', 'pipeline_date')")
    except Exception as e:
        hard_fail(f"Could not parse cross-link-registry.json: {e}")

# ============================================================
# Check 2: Content Validation (0-byte, HTML Leaks, UTF-8, Size)
# ============================================================
HTML_ERROR_MARKERS = [
    "<!DOCTYPE", "<html", "404 Not Found", "Access Denied", "captcha",
    "cloudflare", "captcha-delivery", "Just a moment...", "Checking your browser",
    "Rate limit exceeded", "Service Temporarily Unavailable"
]
MAX_FILE_SIZE_MB = 2.0

all_md = glob.glob(os.path.join(OUTDIR, "**", "*.md"), recursive=True)
checked_count = 0

for fpath in all_md:
    rel = os.path.relpath(fpath, OUTDIR)
    checked_count += 1
    
    # Check 0-byte & Size ceiling
    f_size = os.path.getsize(fpath)
    if f_size == 0:
        hard_fail(f"0-byte file detected: {rel}")
        continue
    
    size_mb = f_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        hard_fail(f"Oversized file ({size_mb:.1f}MB): {rel}")
        continue

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        hard_fail(f"Non-UTF-8 content: {rel}")
        continue

    # FIX BUG-017: Check for HTML leak with structural requirement
    has_structural = "<!DOCTYPE" in content or "<html" in content
    if has_structural:
        for marker in HTML_ERROR_MARKERS:
            if marker in content[:500]:
                hard_fail(f"HTML error/leak detected ({marker}): {rel}")
                break

    # L2 YAML Validation
    if "L2-semantic" in rel:
        if not content.startswith("---"):
            hard_fail(f"Missing YAML frontmatter in L2: {rel}")
        else:
            try:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_data = yaml.safe_load(parts[1])
                    required = ["title", "module", "origin_type", "token_count", "version"]
                    for field in required:
                        if field not in yaml_data:
                            hard_fail(f"L2 YAML missing required field '{field}': {rel}")
            except Exception as e:
                hard_fail(f"Malformed YAML in L2: {rel} ({e})")

# ============================================================
# Check 3: Link Integrity (L2 Relative Links)
# ============================================================
for fpath in all_md:
    if "L2-semantic" not in fpath:
        continue
    
    rel_dir = os.path.dirname(fpath)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    for match in RELATIVE_MD_LINK_RE.finditer(content):
        link = match.group(1)
        target_file = link.split("#", 1)[0]
        target_path = os.path.normpath(os.path.join(rel_dir, target_file))
        if not os.path.isfile(target_path):
            hard_fail(f"Broken relative link in {os.path.relpath(fpath, OUTDIR)}: {link}")

# ============================================================
# Check 3.5: Index Reconciliation (BUG-008)
# ============================================================
full_txt_path = os.path.join(OUTDIR, "llms-full.txt")
if os.path.isfile(full_txt_path):
    with open(full_txt_path, "r", encoding="utf-8") as f:
        full_index = f.read()
    
    for fpath in all_md:
        if "L2-semantic" not in fpath: continue
        fname = os.path.basename(fpath)
        if fname not in full_index:
            soft_warn(f"L2 file missing from llms-full.txt index: {fname}")

# ============================================================
# Check 4: AST Validation (Soft)
# ============================================================
JS_BINARY = shutil.which("node")
UCODE_BINARY = shutil.which("ucode")

def check_ast(code, lang, rel_path):
    if lang == "javascript" and JS_BINARY:
        with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        res = subprocess.run([JS_BINARY, "--check", tmp_path], capture_output=True, text=True)
        os.unlink(tmp_path)
        if res.returncode != 0:
            soft_warn(f"JS Syntax Error in {rel_path}: {res.stderr.strip()}")
    elif lang == "ucode" and UCODE_BINARY:
        with tempfile.NamedTemporaryFile(suffix=".uc", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        res = subprocess.run([UCODE_BINARY, "-c", tmp_path], capture_output=True, text=True)
        os.unlink(tmp_path)
        if res.returncode != 0:
            soft_warn(f"uCode Syntax Error in {rel_path}: {res.stderr.strip()}")

# Check only canonical L2 files for syntax errors (Soft).
# L1 raw captures and assembled L3/L4 outputs duplicate the same code blocks,
# which inflates warning volume without adding meaningful signal.
if JS_BINARY or UCODE_BINARY:
    for fpath in all_md:
        if "L2-semantic" not in fpath:
            continue
        rel = os.path.relpath(fpath, OUTDIR)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract code blocks
        blocks = re.findall(r'```(javascript|ucode|js|uc)\n(.*?)\n```', content, re.DOTALL)
        for lang, code in blocks:
            # Normalize lang names
            l = "javascript" if lang in ["js", "javascript"] else "ucode"
            check_ast(code, l, rel)

# ============================================================
# Summary
# ============================================================
print(f"\n[08] ----------------------------------------------")
print(f"[08] Validation Results")
print(f"[08]   Files Checked: {checked_count}")
print(f"[08]   Hard Failures: {len(hard_failures)}")
print(f"[08]   Soft Warnings: {len(soft_warnings)}")
print(f"[08] ----------------------------------------------")

if hard_failures:
    print("\n[08] BLOCKING FAILURES:")
    for f in hard_failures:
        print(f"  X {f}")
    
    if VALIDATE_MODE == "hard":
        sys.exit(1)
    else:
        print("[08] INFO: Continuing despite failures due to VALIDATE_MODE=soft")

if soft_warnings:
    print("\n[08] NON-BLOCKING WARNINGS:")
    for w in soft_warnings:
        print(f"  ! {w}")

print("\n[08] Validation pass complete.")
sys.exit(0)
