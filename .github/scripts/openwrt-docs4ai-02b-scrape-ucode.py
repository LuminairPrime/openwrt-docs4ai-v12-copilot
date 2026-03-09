"""
Purpose: Generate ucode language and module API documentation using jsdoc2md into L1.
Phase: Extraction
Layers: L0 -> L1
Inputs: tmp/repo-ucode/docs/ and tmp/repo-ucode/lib/
Outputs: tmp/L1-raw/ucode/*.md and .meta.json
Environment Variables: WORKDIR
Dependencies: jsdoc2md (npm global install), Node.js, lib.config, lib.extractor
Notes: Uses isolated temporary directories for each .c file to workaround jsdoc2md recursive bug.
"""

import os
import subprocess
import glob
import datetime
import sys
import re
import shutil
import tempfile
import html
import json

# Add project root to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, extractor

sys.stdout.reconfigure(line_buffering=True)

print("[02b] Generate ucode documentation (JSDoc)")

repo_ucode = os.path.join(config.WORKDIR, "repo-ucode")
if not os.path.exists(repo_ucode):
    print(f"[02b] SKIP: {repo_ucode} not found")
    sys.exit(0)

jsdoc2md = shutil.which("jsdoc2md") or shutil.which("jsdoc2md.cmd")
if not jsdoc2md:
    print("[02b] FAIL: jsdoc2md not found in PATH — skipping ucode JSDoc steps")
    # A complete failure to execute an extractor should exit non-zero if it's supposed to work
    sys.exit(1)

# Check for package.json before running npm install
if os.path.isfile(os.path.join(repo_ucode, "package.json")):
    subprocess.run(["npm", "install", "--silent"], cwd=repo_ucode,
                   shell=(os.name == "nt"), capture_output=True)

repo_url = "https://github.com/jow-/ucode"

saved = 0

# --- Process tutorials ---
print("[02b] Processing tutorials...")
for src in sorted(glob.glob(os.path.join(repo_ucode, "docs", "tutorial-*.md"))):
    base = os.path.basename(src)
    slug = re.sub(r'tutorial-[0-9]*-', 'ucode-tutorial-', base).replace(".md", "")

    with open(src, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    title = "Tutorial"
    for line in lines:
        if line.startswith("#"):
            title = line.strip("# \n")
            break

    rel_src = src.replace(repo_ucode + os.sep, "").replace("\\", "/")
    
    # Strip existing top heading so we enforce standard H1 later if we wanted, 
    # but the content itself is already prose. We'll reconstruct.
    md_body = "".join(lines[1:] if lines and lines[0].startswith("#") else lines)
    final_content = f"# {title}\n\n> **Live docs:** https://ucode.mein.io/{os.path.basename(src).replace('.md', '')}.html\n\n---\n\n{md_body}"

    metadata = {
        "extractor": "02b-scrape-ucode.py",
        "origin_type": "readme", # Using readme for markdown prose guide
        "module": "ucode",
        "slug": slug,
        "original_url": None,
        "language": "text",
        "upstream_path": rel_src,
        "fetch_status": "success",
        "extraction_timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    }

    extractor.write_l1_markdown("ucode", "readme", slug, final_content, metadata)
    saved += 1
    print(f"[02b] OK: {slug}")

# --- Process modules ---
print("[02b] Processing modules...")
srcs = sorted(glob.glob(os.path.join(repo_ucode, "lib", "*.js")) +
              glob.glob(os.path.join(repo_ucode, "lib", "*.c")))

plugin_path = os.path.abspath(os.path.join(repo_ucode, "jsdoc", "c-transpiler")).replace('\\', '/')

for src in srcs:
    mod = os.path.splitext(os.path.basename(src))[0]
    is_c = src.endswith(".c")

    with tempfile.TemporaryDirectory() as tempd:
        temp_c = os.path.join(tempd, os.path.basename(src))
        shutil.copy2(src, temp_c)
        
        ephemeral_conf = os.path.join(tempd, "jsdoc-ephemeral.json")
        with open(ephemeral_conf, "w", encoding="utf-8") as cw:
            if is_c:
                cw.write('{"source": {"includePattern": ".+\\\\.c(pp)?$"}, "plugins": ["' + plugin_path.replace("\\", "\\\\") + '"]}')
            else:
                cw.write('{}') # For standard JS files jsdoc2md

        cmd = [jsdoc2md, "--heading-depth", "2", "--global-index-format", "none",
               "--configure", "jsdoc-ephemeral.json", "--files", os.path.basename(temp_c)]

        res = subprocess.run(cmd, capture_output=True, text=True, cwd=tempd, encoding="utf-8")
        
    stdout = res.stdout or ""
    stderr = res.stderr or ""
    
    # FIX BUG-027: Check subprocess return code
    if res.returncode != 0:
        print(f"[02b] FAIL: jsdoc2md failed for {mod} (Exit {res.returncode})")
        with open(os.path.join(config.WORKDIR, "jsdoc-ucode.err"), "a", encoding="utf-8") as err_f:
            err_f.write(f"ERROR for {mod}:\n{stderr}\n")
        continue

    if stderr:
        with open(os.path.join(config.WORKDIR, "jsdoc-ucode.err"), "a", encoding="utf-8") as err_f:
            err_f.write(f"Stderr for {mod}:\n{stderr}\n")

    output = stdout.strip()
    word_count = len(output.split())
    if not output or word_count < 15:
        print(f"[02b] SKIP: {mod} (too short, {word_count} words)")
        continue

    # Post-process html out of markdown
    output = re.sub(r'<pre class="prettyprint[^"]*"><code>', '```c\n' if is_c else '```javascript\n', output)
    output = output.replace('</code></pre>', '\n```')
    output = re.sub(r'</?code>', '`', output)
    output = re.sub(r'</?p>', '', output)
    output = re.sub(r'</?(?:dl|dt|dd|ul|li|table|thead|tbody|tr|th|td|h[1-6])[^>]*>', '', output)
    output = html.unescape(output)
    output = re.sub(r'\n{3,}', '\n\n', output)

    slug = f"api-module-{mod}"
    title = f"ucode module: {mod}"
    final_content = f"# {title}\n\n> **Live docs:** https://ucode.mein.io/module-{mod}.html\n\n---\n\n{output}"

    rel_src_fwd = src.replace(repo_ucode + os.sep, "").replace("\\", "/")
    origin_type = "c_source" if is_c else "js_source"
    language = "c" if is_c else "javascript"

    metadata = {
        "extractor": "02b-scrape-ucode.py",
        "origin_type": origin_type,
        "module": "ucode",
        "slug": slug,
        "original_url": None,
        "language": language,
        "upstream_path": rel_src_fwd,
        "fetch_status": "success",
        "extraction_timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    }

    extractor.write_l1_markdown("ucode", origin_type, slug, final_content, metadata)
    saved += 1
    print(f"[02b] OK: {slug}")

if os.path.exists(os.path.join(config.WORKDIR, "jsdoc-ucode.err")):
    print("\n=== jsdoc warnings/errors (ucode) ===")
    with open(os.path.join(config.WORKDIR, "jsdoc-ucode.err"), "r", encoding="utf-8") as err_f:
        print(err_f.read())
    print("=== end jsdoc warnings ===")
    os.remove(os.path.join(config.WORKDIR, "jsdoc-ucode.err"))

print("[02b] Complete.")
if saved == 0:
    print("[02b] FAIL: Zero output files generated. Exiting with error.")
    sys.exit(1)
