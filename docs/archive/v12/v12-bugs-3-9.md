***

# Suspected Bugs and Structural Risks — openwrt-docs4ai Pipeline Audit

This document merges all identified issues across the `openwrt-docs4ai` pipeline into a single developer-oriented triage plan. It evaluates stage-to-stage contract mismatches, stale-data flows, validator blind spots, and code-level syntax faults.

### Triage Guidance

1.  **Priority order:** Fix parse-time and startup crashes first (Critical), then false-success, split-brain state, and artifact-loss bugs (High), then integrity, caching, and quality drift issues (Medium/Low).
2.  **Recommended workflow:** Reproduce with minimal fixtures, add regression tests, patch, then rerun the full GitHub Actions pipeline with both default inputs and skip-flag variants.

---

## 🔴 Critical Severity

**BUG-001 — `01-clone-repos.py` is structurally mangled and cannot execute**
*   **Location:** `openwrt-docs4ai-01-clone-repos.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The file appears to have suffered a copy-paste error. `run()` contains `get_commit()` logic using an undefined `repo_dir`. `set_env()` contains clone logic using undefined variables (`dest`, `url`). The module-level code calls `clone_repo(...)` which is never defined.
*   **Failure scenario:** Phase 1 fails immediately with `NameError: name 'clone_repo' is not defined`, blocking the entire pipeline.
*   **Suggested fix:** Rebuild the file into clearly separated helpers: `run(cmd)`, `get_commit(repo_dir)`, `clone_repo(url, dest, label, sparse_paths=None)`, and `set_env(name, value)`.

**BUG-002 — `06b-generate-agents-md.py` contains a parse-time break and undefined output content**
*   **Location:** `openwrt-docs4ai-06b-generate-agents-md.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The script shows an unclosed triple-quoted string (`"""`) immediately preceding the file-writing block. Furthermore, it attempts to write `README.md` from a `readme_content` variable that is never defined.
*   **Failure scenario:** The script fails at parse time with `SyntaxError: EOF while scanning triple-quoted string literal`, or at runtime with `NameError`.
*   **Suggested fix:** Remove the stray triple quote, define `readme_content` explicitly as a string, and add a simple smoke test asserting both files are written.

**BUG-003 — `04-generate-ai-summaries.py` uses `targets` list before initialization**
*   **Location:** `openwrt-docs4ai-04-generate-ai-summaries.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The script appends to `targets` inside the module scan loop (`targets.append(...)`), but no `targets =[]` initialization exists before the loop.
*   **Failure scenario:** The script crashes with `NameError` before any AI summary generation begins.
*   **Suggested fix:** Initialize `targets = []` immediately before the `for module in["ucode", "luci", "procd", "uci"]:` loop.

**BUG-004 — `07-generate-index-html.py` generates HTML content but never writes the file**
*   **Location:** `openwrt-docs4ai-07-generate-index-html.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The script successfully constructs the `html_content` string but visibly ends without invoking a file write operation.
*   **Failure scenario:** The script exits `0` (false success), but `08-validate.py` will later crash the pipeline because `index.html` is listed in `CORE_FILES` and will be missing.
*   **Suggested fix:** Add standard file writing logic at the end: `with open(os.path.join(OUTDIR, "index.html"), "w") as f: f.write(html_content)`.

---

## 🟠 High Severity

**BUG-005 — Split-brain L2 state drops AI summaries from final assembly**
*   **Location:** `03-normalize-semantic.py`, `04-generate-ai-summaries.py`, `05-assemble-references.py`
*   **Confidence:** Confirmed
*   **Symptoms:** `03-normalize` promotes L1 and L2 files into `OUTDIR/L2-semantic`. Later, `04-generate-ai` edits files in `config.L2_SEMANTIC_WORKDIR` (which points to the `tmp/` staging area). Finally, `05-assemble` and `06a-index` read from `OUTDIR/L2-semantic`. 
*   **Failure scenario:** Downstream artifacts are built from stale, pre-AI files. The AI summaries are successfully generated in `tmp/` but completely ignored by the final outputs, wasting LLM quota and silently degrading docs.
*   **Suggested fix:** Move the `promote_to_staging` function call in `03` to a separate `04b-promote.py` script, or have `04` operate directly on the `OUTDIR` files.

**BUG-006 — Matrix jobs fail artifact upload when skip paths produce no L1-raw output**
*   **Location:** `openwrt-docs4ai-00-pipeline.yml` & `02f, 02g, 02h`
*   **Confidence:** Confirmed
*   **Symptoms:** Extractors return `sys.exit(0)` when their required repositories are skipped. However, the workflow unconditionally uploads `${{ env.WORKDIR }}/L1-raw/` as an artifact.
*   **Failure scenario:** Running with `skip_buildroot: true` causes the extractor scripts to exit cleanly, but the artifact upload step throws a fatal error because the directory doesn't exist, breaking the pipeline matrix.
*   **Suggested fix:** Add `if-no-files-found: ignore` to the `Upload L1 Artifacts` step.

**BUG-007 — 100% AI cache miss rate due to missing metadata contracts**
*   **Location:** `04-generate-ai-summaries.py` & All `02*` extractors
*   **Confidence:** Confirmed
*   **Symptoms:** Script `04` attempts to use `content_hash` from the L1 `.meta.json` files to look up cached AI summaries. However, none of the extraction scripts actually generate or write a `content_hash` key.
*   **Failure scenario:** `content_hash` defaults to `"unknown"` every time. The cache logic is bypassed entirely, hitting the LLM API for every file on every run.
*   **Suggested fix:** Have `04-generate-ai` calculate the SHA256 hash of the target markdown file's contents at runtime, rather than relying on non-existent L1 metadata.

**BUG-008 — System-level false success on incomplete indexing**
*   **Location:** `06a-generate-llms-txt.py` & `08-validate.py`
*   **Confidence:** Confirmed
*   **Symptoms:** `06a` skips malformed or unreadable L2 files with a warning. `08-validate` checks that top-level core files exist, but does not verify that every valid L2 document is actually represented in `llms.txt`.
*   **Failure scenario:** If an extraction or L2 schema gets corrupted, documents vanish from the navigational map but pass CI, resulting in incomplete documentation.
*   **Suggested fix:** Add a reconciliation check in `08` that compares the total count of valid L2 files against the entry counts in `llms.txt`.

**BUG-009 — `05-assemble-references.py` succeeds with zero useful outputs**
*   **Location:** `05-assemble-references.py`
*   **Confidence:** High
*   **Symptoms:** The script tracks `outputs_generated` and logs warnings for unreadable files, but the visible ending only prints completion counts. There is no hard failure if `outputs_generated == 0`.
*   **Failure scenario:** If upstream L2 directories are empty or corrupted, L3/L4 assembly silently produces nothing, and the pipeline continues.
*   **Suggested fix:** Assert `outputs_generated > 0` at the end of the script and `sys.exit(1)` if false.

**BUG-010 — Commit/version metadata is lost across jobs**
*   **Location:** `00-pipeline.yml` & `03-normalize-semantic.py`
*   **Confidence:** Confirmed
*   **Symptoms:** `initialize` attempts to export variables like `OPENWRT_COMMIT` to `GITHUB_ENV`. However, `GITHUB_ENV` values do not persist across different GitHub Actions jobs.
*   **Failure scenario:** When `03-normalize` runs in the downstream `process` job, `os.environ.get("OPENWRT_COMMIT")` returns `None`. All L2 files receive `version: "unknown"`, breaking telemetry.
*   **Suggested fix:** Map the commit hashes to job `outputs:` in the `initialize` job, and inject them into the `env:` block of the `process` job using `${{ needs.initialize.outputs.openwrt_commit }}`.

**BUG-011 — Slug collisions silently overwrite output**
*   **Location:** `02c-scrape-jsdoc.py` & `02g-scrape-uci-schemas.py`
*   **Confidence:** Likely
*   **Symptoms:** `02c` creates slugs based purely on basenames (`mod = os.path.splitext(filename)`). `02g` uses UCI config names. Many packages ship files with identical names (e.g., `network`, `main.js`).
*   **Failure scenario:** Later-written files silently overwrite earlier ones with the same slug. Generation "works", but massive coverage is lost.
*   **Suggested fix:** Build slugs from normalized relative paths (e.g., `api-luci-base-main`) instead of basenames.

**BUG-012 — Total failure of Wiki caching in CI environments**
*   **Location:** `02a-scrape-wiki.py` & `00-pipeline.yml`
*   **Confidence:** Confirmed
*   **Symptoms:** The action caches `.cache/wiki-lastmod.json`, but does *not* cache the actual markdown files inside `L1-raw/`. `02a` logic reads: `if cache hits AND os.path.exists(fpath): continue`. Because CI runners spin up fresh, `fpath` never exists.
*   **Failure scenario:** 100% cache miss rate. The script re-downloads and re-parses every wiki page on every run, wasting time and risking Cloudflare IP bans.
*   **Suggested fix:** Cache the `WORKDIR/L1-raw/wiki` directory alongside the `.cache` metadata file in the YAML.

**BUG-013 — OpenWrt Makefile Extractor expects impossible syntax**
*   **Location:** `02d-scrape-core-packages.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The script looks for package descriptions using `r'DESCRIPTION\s*:?=\s*(.+?)(?=\n\s*[A-Z]|\Z)'`. OpenWrt Makefiles *do not use* `DESCRIPTION :=` variables; they use a `define Package/foo/description \n ... \n endef` block format.
*   **Failure scenario:** Exactly 0 custom package descriptions are extracted, resulting in a massive loss of OpenWrt context.
*   **Suggested fix:** Rewrite the regex to target the standard OpenWrt `define Package/.../description` multiline block.

**BUG-014 — `llms.txt` generates broken relative links for every single file**
*   **Location:** `06a-generate-llms-txt.py`
*   **Confidence:** Confirmed
*   **Symptoms:** `06a` writes relative links pointing to `./filename.md` in the module directories. However, the actual markdown files reside in `OUTDIR/L2-semantic/<module>/`.
*   **Failure scenario:** Every single file link in `llms.txt` is broken (404). If an LLM tries to fetch a file, it will fail.
*   **Suggested fix:** Change link generation to point to `../L2-semantic/{module}/{os.path.basename(rec['rel_path'])}`.

**BUG-015 — Broken link validation bypassed for L4 monoliths**
*   **Location:** `08-validate.py` & `05-assemble-references.py`
*   **Confidence:** Confirmed
*   **Symptoms:** `05` concatenates L2 files containing relative links (e.g., `../luci/api.md`). Placed in `OUTDIR/<module>/`, those links break because the folder depth changed. `08-validate` explicitly skips link validation for files outside `L2-semantic`.
*   **Failure scenario:** The L4 monoliths are full of broken cross-references, but CI passes cleanly.
*   **Suggested fix:** Rewrite relative links inside `05` during assembly, and remove the validator bypass in `08`.

**BUG-016 — Invalid TS syntax breaks IDE schemas**
*   **Location:** `06c-generate-ide-schemas.py`
*   **Confidence:** Confirmed
*   **Symptoms:** Ucode docs indicate optional arguments with brackets (`foo(a, [b])`). Script `06c` parses this and writes `[b]: any`. Furthermore, global functions bypass parameter extraction entirely, resulting in `declare function foo(...args: any[]): any;`.
*   **Failure scenario:** `[b]: any` is illegal TypeScript. It breaks generated IDE schemas, causing autocomplete plugins to crash. Global functions offer zero parameter hints.
*   **Suggested fix:** Strip brackets and append `?` (e.g., `b?: any`). Apply the parameter extraction logic to global functions.

---

## 🟡 Medium Severity

**BUG-017 — False-positive HTML leak detector deletes legitimate networking docs**
*   **Location:** `08-validate.py` & `02a-scrape-wiki.py`
*   **Confidence:** High
*   **Symptoms:** `08` and `02a` hard-fail/skip if strings like `"404 Not Found"`, `"Access Denied"`, or even the substring `"html"` appear in the first 500 bytes.
*   **Failure scenario:** Legitimate OpenWrt documentation teaching users how to configure a reverse proxy (mentioning 404s) or firewall ACLs (mentioning Access Denied) will be flagged as an HTML error page leak and deleted.
*   **Suggested fix:** Only trigger if the document actually contains HTML framing tags (e.g., `<!DOCTYPE`, `<html`).

**BUG-018 — HTML landing page regex coupling destroys index**
*   **Location:** `07-generate-index-html.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The HTML generator parses `llms.txt` using `r'- \[(.*?)\]\((.*?)\): (.*)'`. However, `06a` writes lines formatted as `- [name](link) (X tokens) - desc`.
*   **Failure scenario:** The regex silently fails on every line. `index.html` generates successfully but renders completely empty bulleted lists under every section.
*   **Suggested fix:** Update the regex in `07` to match the actual output of `06a`, or generate the HTML directly from the dictionary in `06a` to avoid text scraping entirely.

**BUG-019 — `SKIP_AI` defaults to true locally**
*   **Location:** `04-generate-ai-summaries.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The logic sets `SKIP_AI = os.environ.get("SKIP_AI", "true").lower() == "true"`.
*   **Failure scenario:** Local or ad-hoc runs silently produce no summaries if the caller forgets to explicitly set `SKIP_AI=false`.
*   **Suggested fix:** Change the fallback default to `"false"`.

**BUG-020 — `02e` is incorrectly gated by `SKIP_BUILDROOT`**
*   **Location:** `openwrt-docs4ai-02e-scrape-example-packages.py`
*   **Confidence:** High
*   **Symptoms:** The script exits early when `SKIP_BUILDROOT=true`, but it actually parses LuCI examples from `repo-luci/applications`.
*   **Failure scenario:** LuCI examples are wrongly dropped from the documentation when users skip the heavy Buildroot extraction.
*   **Suggested fix:** Remove the `SKIP_BUILDROOT` gate from `02e` and replace it with a `repo-luci` directory existence check.

**BUG-021 — `JSONDecodeError` Risk on LLM Payload Parsing**
*   **Location:** `openwrt-docs4ai-04-generate-ai-summaries.py`
*   **Confidence:** High
*   **Symptoms:** Parses AI responses using `json.loads(data["choices"][0]["message"]["content"])`. LLMs frequently wrap JSON in Markdown formatting (e.g., ` ```json\n{...}\n``` `).
*   **Failure scenario:** `json.loads` throws a `JSONDecodeError`, crashing the script or skipping the file.
*   **Suggested fix:** Strip Markdown code blocks from the raw response string before parsing.

**BUG-022 — Unsafe YAML injection in AI summaries**
*   **Location:** `openwrt-docs4ai-04-generate-ai-summaries.py`
*   **Confidence:** High
*   **Symptoms:** The script manually appends `ai_summary` lines into frontmatter using string replacement, naively stripping quotes.
*   **Failure scenario:** Model output containing YAML-significant characters (colons, newlines, unescaped quotes) corrupts frontmatter, breaking downstream parsers.
*   **Suggested fix:** Load frontmatter via `yaml.safe_load()`, update the dictionary, and re-serialize with `yaml.safe_dump()`.

**BUG-023 — Validator syntax coverage is much narrower than generator surface**
*   **Location:** `08-validate.py`
*   **Confidence:** Confirmed
*   **Symptoms:** `08` only AST-checks fenced `javascript` and `ucode` blocks under `OUTDIR/L1-raw/luci-examples/*.md`.
*   **Failure scenario:** Syntax regressions in generated docs from other modules (like `ucode` JSDoc output), or in assembled L3/L4 outputs, completely escape the validation net.
*   **Suggested fix:** Expand AST checking to scan all generated `.md` files containing `javascript` or `ucode` code fences.

**BUG-024 — Shell extractor blinds itself after the copyright header**
*   **Location:** `02f-scrape-procd-api.py`
*   **Confidence:** Confirmed
*   **Symptoms:** The script reads lines starting with `#`. As soon as it hits an empty line: `elif not line.strip(): continue; else: break`.
*   **Failure scenario:** It stops parsing at the first line of executable code. It captures the SPDX/shebang header and immediately stops, completely missing all function-level comments further down.
*   **Suggested fix:** Scan the *entire* file, specifically targeting `#` comment blocks that immediately precede shell function declarations.

**BUG-025 — Memory scaling risk in semantic normalizer**
*   **Location:** `03-normalize-semantic.py`
*   **Confidence:** Likely
*   **Symptoms:** Builds a massive `set()` of every protected character index via `prot.update(range(m.start(), m.end()))` to avoid replacing links inside code blocks.
*   **Failure scenario:** Large code blocks create immense memory pressure, risking Out-Of-Memory (OOM) kills on CI runners.
*   **Suggested fix:** Store protected spans as `[(start, end)]` tuples and test membership via ranges.

**BUG-026 — Missing explicit return types in IDE generation**
*   **Location:** `06c-generate-ide-schemas.py`
*   **Confidence:** Confirmed
*   **Symptoms:** `sig_ts = f"{f['name']}({', '.join(ts_params)})"` fails to append `: {f['returns']}` for parameterized functions.
*   **Failure scenario:** The generated `.d.ts` loses useful return-type information.
*   **Suggested fix:** Append `: {f['returns']}` to the string format.

**BUG-027 — Subprocess failures in JSDoc generators treated as clean skips**
*   **Location:** `02b-scrape-ucode.py` & `02c-scrape-jsdoc.py`
*   **Confidence:** High
*   **Symptoms:** Both scripts run `jsdoc2md` and capture `stderr`, but neither enforces `returncode == 0`.
*   **Failure scenario:** If dependencies fail, the scripts see "0 words output", report a "SKIP", and exit `0`. Real tool crashes hide behind benign messages.
*   **Suggested fix:** Check `res.returncode` and trigger `sys.exit(1)` on non-zero exit.

**BUG-028 — Cwd-dependent baseline contract**
*   **Location:** `06d-generate-changelog.py`
*   **Confidence:** Medium
*   **Symptoms:** Sets `BASELINEDIR = os.path.join(os.getcwd(), "baseline")`.
*   **Failure scenario:** Changelog accuracy depends entirely on being launched from the exact expected working directory, breaking easily if invoked from subfolders.
*   **Suggested fix:** Resolve paths relative to `__file__` or use a strict `OUTDIR`/environment variable path.

**BUG-029 — Duplicate code block in AI script**
*   **Location:** `04-generate-ai-summaries.py`
*   **Confidence:** Confirmed
*   **Symptoms:** Lines 20-35 are an exact, copy-pasted duplicate of lines 1-19 (imports, `sys.path.insert`, env vars).
*   **Failure scenario:** Maintenance debt; fixes made to one block may not be applied to the other.
*   **Suggested fix:** Delete the redundant block.

**BUG-030 — XSS / Unescaped HTML injection**
*   **Location:** `07-generate-index-html.py`
*   **Confidence:** Likely
*   **Symptoms:** Module titles and descriptions are interpolated directly into HTML fragments.
*   **Failure scenario:** Malformed descriptions break the landing page or produce unintended markup.
*   **Suggested fix:** Apply `html.escape()` to text fields before interpolation.

---

## 🟢 Low Severity

**BUG-031 — The "Monolithic Files" exist but are completely hidden from the AI**
*   **Location:** `06a-generate-llms-txt.py`
*   **Symptoms:** `06a` indexes the raw L2 files, but completely ignores the `*-complete-reference.md` and `*-skeleton.md` files generated in `05`. `AGENTS.md` tells the AI to use files it cannot find.
*   **Suggested fix:** Update `06a` to explicitly index the L3/L4 files.

**BUG-032 — `02a` silently drops short Wiki pages**
*   **Location:** `02a-scrape-wiki.py`
*   **Symptoms:** Pages whose converted markdown is <200 chars are skipped via `continue` without incrementing `failed` or logging.
*   **Suggested fix:** Track explicit skips and whitelist legitimate short pages.

**BUG-033 — `GITHUB_ENV` export syntax overrides native behavior**
*   **Location:** `00-pipeline.yml` & `01-clone-repos.py`
*   **Symptoms:** The workflow maps `GITHUB_ENV: ${{ github.env }}`, overriding the native filepath injection behavior of Actions.

**BUG-034 — Cache keys are too run-specific**
*   **Location:** `00-pipeline.yml`
*   **Symptoms:** Wiki and AI cache keys include `${{ github.run_id }}`, making each run's primary key unique and ensuring a primary miss.
*   **Suggested fix:** Use content-hash or branch-derived keys with stable restore prefixes.

**BUG-035 — Missing `repo-manifest.json`**
*   **Location:** `00-pipeline.yml` & `01-clone-repos.py`
*   **Symptoms:** The workflow uploads `repo-manifest.json` as an artifact, but `01` never writes it.

**BUG-036 — Dead failure tracking in JS scraper**
*   **Location:** `02c-scrape-jsdoc.py`
*   **Symptoms:** `failed_count` is initialized but never incremented or reported.

**BUG-037 — Version banner omits ucode**
*   **Location:** `06a-generate-llms-txt.py`
*   **Symptoms:** The version banner includes OpenWrt and LuCI commits but forgets `UCODE_COMMIT`.

---

### Suggested Repros & Testing Workflow

1.  **Parse Smoke Tests:** Run `python -m py_compile .github/scripts/*.py` locally to immediately catch the syntax and mangling errors in `01` and `06b`.
2.  **L2 Stale State Validation:** Run `03`, artificially modify an L2 file using `04`'s logic, and run `05` to mathematically prove that the monoliths ignore the modification.
3.  **HTML Leak False Positives:** Create a markdown file named `test.md` whose first line is `# Setting up a 404 Not Found redirect`. Run `08-validate.py` over it and watch it hard-fail.
4.  **Matrix Upload Integrity:** Run a `workflow_dispatch` with `skip_buildroot: true` to trigger the `sys.exit(0)` missing artifact failure in the `extract` matrix.
5.  **Schema Collision Tests:** Feed two dummy files named `luci-base/main.js` and `luci-app/main.js` into `02c` and assert that two distinct L1 files are produced, rather than one overwriting the other.