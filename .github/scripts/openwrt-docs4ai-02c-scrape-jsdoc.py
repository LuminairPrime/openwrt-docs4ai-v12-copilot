"""
Purpose: Generate LuCI JavaScript API documentation using jsdoc2md into L1.
Phase: Extraction
Layers: L0 -> L1
Inputs: tmp/repo-luci/modules/luci-base/htdocs/luci-static/resources/
Outputs: tmp/L1-raw/luci/*.md and .meta.json
Environment Variables: WORKDIR
Dependencies: jsdoc2md (npm global install), Node.js, lib.config, lib.extractor
Notes: Processes all .js files. Falls back to whole-directory mode if needed.
"""

import os
import subprocess
import glob
import datetime
import sys
import re
import shutil
import html
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, extractor

sys.stdout.reconfigure(line_buffering=True)
JSDOC_TIMEOUT = int(os.environ.get("JSDOC_TIMEOUT", "120"))


def clean_jsdoc_output(output):
    output = re.sub(r'<pre class="prettyprint[^"]*"><code>', '```javascript\n', output)
    output = output.replace('</code></pre>', '\n```')
    output = re.sub(r'</?code>', '`', output)
    output = re.sub(r'</?p>', '', output)
    output = re.sub(r'</?(?:dl|dt|dd|ul|li|table|thead|tbody|tr|th|td|h[1-6]|a(?:\s+[^>]*)?|/a)[^>]*>', '', output)
    output = html.unescape(output)
    output = re.sub(r'\n{3,}', '\n\n', output)
    return output


def run_jsdoc_command(cmd, cwd, timeout=JSDOC_TIMEOUT):
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        encoding="utf-8",
        timeout=timeout,
    )


def fallback_has_usable_output(result):
    return result.returncode == 0 and bool((result.stdout or "").strip())


def append_error_log(message):
    with open(os.path.join(config.WORKDIR, "jsdoc-luci.err"), "a", encoding="utf-8") as err_f:
        err_f.write(message)


def main():
    print("[02c] Generate LuCI JS API documentation (JSDoc)")

    repo_luci = os.path.join(config.WORKDIR, "repo-luci")
    if not os.path.exists(repo_luci):
        print(f"[02c] SKIP: {repo_luci} not found")
        return 0

    jsdoc2md = shutil.which("jsdoc2md") or shutil.which("jsdoc2md.cmd")
    if not jsdoc2md:
        print("[02c] FAIL: jsdoc2md not found in PATH — skipping LuCI JSDoc steps")
        return 1

    live_base = "https://openwrt.github.io/luci/jsapi"
    print("[02c] Processing LuCI JS API source files...")
    target_dir = os.path.join(repo_luci, "modules", "luci-base", "htdocs", "luci-static", "resources")

    file_count = 0
    skip_count = 0
    failed_count = 0

    luci_srcs = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".js"):
                luci_srcs.append(os.path.join(root, file))
    luci_srcs.sort()

    for src in luci_srcs:
        filename = os.path.basename(src)
        mod = os.path.splitext(filename)[0]
        relpath = os.path.relpath(src, repo_luci).replace("\\", "/")

        cmd = [jsdoc2md, "--heading-depth", "2", "--global-index-format", "none", "--files", relpath]
        try:
            res = run_jsdoc_command(cmd, repo_luci)
        except subprocess.TimeoutExpired:
            print(f"[02c] FAIL: jsdoc2md timed out for {mod} after {JSDOC_TIMEOUT}s")
            failed_count += 1
            append_error_log(f"TIMEOUT for {mod}: jsdoc2md exceeded {JSDOC_TIMEOUT}s\n")
            continue

        stdout = res.stdout or ""
        stderr = res.stderr or ""

        if res.returncode != 0:
            print(f"[02c] FAIL: jsdoc2md failed for {mod} (Exit {res.returncode})")
            failed_count += 1
            append_error_log(f"ERROR for {mod}:\n{stderr}\n")
            continue

        if stderr:
            append_error_log(f"Stderr for {mod}:\n{stderr}\n")

        output = stdout.strip()
        word_count = len(output.split())

        if not output or word_count < 15:
            print(f"[02c] SKIP: {mod} (too short, {word_count} words)")
            skip_count += 1
            continue

        output = clean_jsdoc_output(output)
        live_url = f"{live_base}/LuCI.html" if mod == "luci" else f"{live_base}/LuCI.{mod}.html"
        sub_path = relpath.replace("modules/luci-base/htdocs/luci-static/resources/", "").replace(".js", "").replace("/", "-")
        slug = f"api-{sub_path}"
        title = f"LuCI API: {mod}"
        final_content = f"# {title}\n\n> **Live docs:** {live_url}\n\n---\n\n{output}"

        metadata = {
            "extractor": "02c-scrape-jsdoc.py",
            "origin_type": "js_source",
            "module": "luci",
            "slug": slug,
            "original_url": None,
            "language": "javascript",
            "upstream_path": relpath,
            "fetch_status": "success",
            "extraction_timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }

        extractor.write_l1_markdown("luci", "js_source", slug, final_content, metadata)
        member_count = output.count("##")
        file_count += 1
        print(f"[02c] OK: {slug} ({member_count} members)")

    if file_count == 0 and len(luci_srcs) > 0:
        print("[02c] WARN: 0 files generated individually. Running whole-directory fallback.")
        target_rel = os.path.relpath(target_dir, repo_luci).replace("\\", "/")
        cmd = [jsdoc2md, "--heading-depth", "2", "--global-index-format", "none", "--files", f"{target_rel}/**/*.js"]
        try:
            res = run_jsdoc_command(cmd, repo_luci)
        except subprocess.TimeoutExpired:
            print(f"[02c] FAIL: whole-directory fallback timed out after {JSDOC_TIMEOUT}s")
            append_error_log(f"TIMEOUT for api-all: jsdoc2md exceeded {JSDOC_TIMEOUT}s\n")
            res = None

        if res is not None:
            if res.stderr:
                append_error_log(f"Stderr for api-all:\n{res.stderr}\n")

            if fallback_has_usable_output(res):
                output = clean_jsdoc_output((res.stdout or "").strip())
                final_content = f"# LuCI API: All\n\n{output}"
                metadata = {
                    "extractor": "02c-scrape-jsdoc.py",
                    "origin_type": "js_source",
                    "module": "luci",
                    "slug": "api-all",
                    "original_url": None,
                    "language": "javascript",
                    "upstream_path": target_rel,
                    "fetch_status": "success",
                    "extraction_timestamp": datetime.datetime.now(datetime.UTC).isoformat()
                }
                extractor.write_l1_markdown("luci", "js_source", "api-all", final_content, metadata)
                file_count += 1
                print("[02c] OK: api-all.md")
            else:
                failed_count += 1
                print("[02c] FAIL: whole-directory fallback did not return usable output")

    err_path = os.path.join(config.WORKDIR, "jsdoc-luci.err")
    if os.path.exists(err_path):
        print("\n=== jsdoc warnings/errors (LuCI) ===")
        with open(err_path, "r", encoding="utf-8") as err_f:
            print(err_f.read())
        print("=== end jsdoc warnings ===")
        os.remove(err_path)

    print(f"[02c] Complete: {file_count} files generated, {skip_count} skipped, {failed_count} failed.")
    if file_count == 0:
        print("[02c] FAIL: Zero output files generated. Exiting with error.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
