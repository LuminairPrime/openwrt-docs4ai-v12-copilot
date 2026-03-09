# Suspected Bugs and Structural Risks — openwrt-docs4ai Pipeline

**Status:** Investigation list for developer triage. All items are suspected defects identified through static code reading. Each should be confirmed before patching. Some may be intentional, mitigated by unseen code (the `lib/config.py` and `lib/extractor.py` modules were not provided for review), or inaccurate due to inherent limitations of manual review.

**Scope:** Scripts `01` through `08`, workflow YAML `00`, and their interactions. Shared library code in `lib/` was not available; bugs mitigated there would be false positives here.

### Triage Guidance

1. **Priority order:** Fix Critical first — BUG-001 blocks the entire pipeline. Then fix High (false-success, data-loss, and state-split bugs), then Medium (quality, robustness), then Low (cleanup).
2. **Recommended workflow:** Reproduce with minimal fixtures, add regression tests, patch, then rerun the full GitHub Actions pipeline with both default inputs and skip-flag variants.

---

## 🔴 Critical Severity

**BUG-001 — `01-clone-repos.py` is structurally mangled and cannot execute**

- **Location:** `openwrt-docs4ai-01-clone-repos.py`
- **Confidence:** Confirmed
- **Description:** The file has suffered a copy-paste or merge error. `run()` contains `get_commit()` logic referencing an undefined `repo_dir`. `set_env()` contains clone logic referencing undefined `dest`, `url`, `label`, and `sparse_paths`. Module-level code calls `clone_repo(...)` which is never defined as a function.
- **Failure scenario:** Phase 1 crashes immediately with `NameError`, blocking the entire pipeline.
- **Status:** Already Fixed / False Positive (Current version has correct structure)
- **Suggested fix:** Rebuild the file with properly separated functions: `run(cmd)`, `get_commit(repo_dir)`, `set_env(name, value)`, and `clone_repo(url, dest, label, sparse_paths=None)`, each with its own correct body.

---

**BUG-002 — `06b-generate-agents-md.py` has a syntax error and an undefined variable**

- **Location:** `openwrt-docs4ai-06b-generate-agents-md.py`
- **Confidence:** Confirmed
- **Description:** A stray `"""` appears immediately after the `agents_content` string assignment, opening an unterminated triple-quoted string that swallows the remaining code. Separately, the script writes `readme_content` to `README.md`, but `readme_content` is never defined.
- **Failure scenario:** Python raises `SyntaxError` at parse time. If the stray quote is removed, it then raises `NameError: name 'readme_content' is not defined`.
- **Status:** Already Fixed / False Positive
- **Suggested fix:** Remove the stray triple-quote, define `readme_content` as an explicit string, and add a smoke test asserting both output files are written and non-empty.

---

**BUG-003 — `04-generate-ai-summaries.py` uses `targets` before initialization**

- **Location:** `openwrt-docs4ai-04-generate-ai-summaries.py`
- **Confidence:** Confirmed
- **Description:** The module-scan loop calls `targets.append(...)`, but `targets = []` never appears before the loop.
- **Failure scenario:** Script crashes with `NameError: name 'targets' is not defined` before any AI summary work begins.
- **Status:** FIXED (targets = [] added)
- **Suggested fix:** Add `targets = []` immediately before the `for module in ["ucode", "luci", "procd", "uci"]:` loop.

---

**BUG-004 — `07-generate-index-html.py` builds HTML but never writes the file**

- **Location:** `openwrt-docs4ai-07-generate-index-html.py`
- **Confidence:** Confirmed
- **Description:** The script constructs `html_content` as a complete HTML string, then ends. No `open()` / `write()` call exists.
- **Failure scenario:** Script exits 0 (false success). `08-validate.py` later hard-fails because `index.html` is listed in `CORE_FILES` and is missing.
- **Status:** Already Fixed / False Positive
- **Suggested fix:** Add `with open(os.path.join(OUTDIR, "index.html"), "w", encoding="utf-8", newline="\n") as f: f.write(html_content)` and a completion log line.

---

## 🟠 High Severity

**BUG-005 — Split-brain L2 state causes AI summaries to be silently lost**

- **Location:** `03-normalize-semantic.py` → `04-generate-ai-summaries.py` → `05-assemble-references.py`
- **Confidence:** Confirmed
- **Description:** Script `03` copies L2 files from `WORKDIR` into `OUTDIR/L2-semantic/` via `promote_to_staging()`. Script `04` then writes AI summaries into files under `config.L2_SEMANTIC_WORKDIR` — which still points at the `WORKDIR` staging area. Script `05` reads from `OUTDIR/L2-semantic/`, which contains the pre-AI versions.
- **Failure scenario:** AI summaries are generated and written successfully but are never seen by assembly, indexing, or validation. LLM quota is consumed for zero benefit.
- **Status:** FIXED (Changed l2_dir to OUTDIR/L2-semantic)
- **Suggested fix:** Either move `promote_to_staging()` to run after `04`, or have `04` operate on `OUTDIR/L2-semantic/` directly.

---

**BUG-007 — AI summary cache has 100% miss rate due to missing `content_hash`**

- **Location:** `04-generate-ai-summaries.py`, all `02*` extractors
- **Confidence:** Confirmed
- **Description:** Script `04` reads `content_hash` from `.meta.json` files to key its cache lookups. No extractor script writes a `content_hash` field. The value always defaults to `"unknown"`, and the cache logic explicitly skips `"unknown"` hashes.
- **Failure scenario:** Every file hits the LLM API on every run, wasting quota and time.
- **Suggested fix:** Have `04` compute `hashlib.sha256(content.encode()).hexdigest()` at runtime from the file contents rather than relying on non-existent L1 metadata.

---

**BUG-008 — Validator does not verify index completeness**

- **Location:** `06a-generate-llms-txt.py`, `08-validate.py`
- **Confidence:** Confirmed
- **Description:** Script `06a` silently skips L2 files with malformed frontmatter (logs a warning, continues). Script `08` checks that top-level core files exist but never verifies that every valid L2 document is represented in `llms.txt` or `llms-full.txt`.
- **Failure scenario:** A corrupted L2 file disappears from navigation. CI passes. Documentation is silently incomplete.
- **Suggested fix:** Add a reconciliation check in `08` comparing valid L2 file count against entry count in `llms-full.txt`.

---

**BUG-009 — `05-assemble-references.py` can succeed with zero outputs**

- **Location:** `openwrt-docs4ai-05-assemble-references.py`
- **Confidence:** Confirmed
- **Description:** The script tracks `outputs_generated` but never gates on it. If all L2 directories are empty or all files fail to parse, the script prints a completion message and exits 0.
- **Failure scenario:** L3/L4 assembly produces nothing. Pipeline continues. No artifacts for downstream indexing or deployment.
- **Suggested fix:** Add `if outputs_generated == 0: print("[05] FAIL: Zero outputs"); sys.exit(1)` at the end.

---

**BUG-010 — Commit metadata is lost across GitHub Actions jobs**

- **Location:** `00-pipeline.yml`, `01-clone-repos.py`, `03-normalize-semantic.py`
- **Confidence:** Confirmed
- **Description:** Script `01` writes commit hashes to `GITHUB_ENV`, but `GITHUB_ENV` values are scoped to the current job. The `process` job runs on a separate runner where these variables do not exist.
- **Failure scenario:** `os.environ.get("OPENWRT_COMMIT")` returns `None` in the `process` job. All L2 files receive `version: "unknown"`, breaking telemetry and changelogs.
- **Suggested fix:** Write commit hashes to a JSON file included in the L0 artifact, or use job `outputs:` and `needs.initialize.outputs.*` in the workflow.

---

**BUG-011 — Slug collisions silently overwrite output files**

- **Location:** `02c-scrape-jsdoc.py`, `02g-scrape-uci-schemas.py`
- **Confidence:** Likely
- **Description:** Script `02c` derives slugs from bare filenames (`api-{mod}` where `mod` is the basename without extension). If multiple JS files in different subdirectories share a name (e.g., `main.js`), later writes overwrite earlier ones. Script `02g` uses `schema-{schema_name}` where `schema_name` is the config filename; multiple packages ship files named `network`.
- **Failure scenario:** Documentation is silently lost. File count looks correct but coverage is reduced.
- **Status:** FIXED (Included pkg_name/path in slug)
- **Suggested fix:** Build slugs from relative paths (e.g., `api-luci-base-main`) instead of basenames alone, and log a warning if a slug collision is detected.

---

**BUG-012 — Wiki page caching is ineffective in CI**

- **Location:** `02a-scrape-wiki.py`, `00-pipeline.yml`
- **Confidence:** Confirmed
- **Description:** The workflow caches `.cache/wiki-lastmod.json` (metadata about page modification dates) but does **not** cache the L1 markdown output files. Script `02a` checks `if cache.get(url) == last_mod_str and os.path.exists(fpath)` — but on a fresh CI runner, `fpath` never exists.
- **Failure scenario:** Every wiki page is re-downloaded and re-converted on every run regardless of the metadata cache. This wastes minutes of runtime and risks Cloudflare rate-limiting.
- **Status:** FIXED (Added L1-raw/wiki to workflow cache)
- **Suggested fix:** Cache the `WORKDIR/L1-raw/wiki/` directory alongside `.cache/` in the workflow YAML, or remove the `os.path.exists(fpath)` guard.

---

**BUG-013 — Makefile description extractor misses standard OpenWrt format**

- **Location:** `02d-scrape-core-packages.py`
- **Confidence:** Confirmed
- **Description:** The script searches for `PKG_DESCRIPTION` as a Makefile variable and `DESCRIPTION\s*:?=` inside `define Package/` blocks. Standard OpenWrt packages use `define Package/foo/description` blocks containing plain text (no assignment operator). The regex does not match this format.
- **Failure scenario:** Package descriptions are extracted from very few (possibly zero) packages. Only packages with a README fallback get any description.
- **Status:** FIXED (Added support for /description blocks)
- **Suggested fix:** Add a regex targeting `define Package/[^/]+/description\s*\n(.*?)^endef` with `re.MULTILINE | re.DOTALL` to capture the plain-text block.

---

**BUG-014 — `llms.txt` and `llms-full.txt` generate broken links to individual files**

- **Location:** `06a-generate-llms-txt.py`
- **Confidence:** Confirmed
- **Description:** Module-level `llms.txt` files write links as `./filename.md`. The root `llms-full.txt` writes links as `./{module}/filename.md`. But the actual markdown files live in `OUTDIR/L2-semantic/{module}/`. These relative paths do not resolve to the correct location from either the module output directory or the root.
- **Failure scenario:** Every individual-file link in the navigation indexes is a 404.
- **Suggested fix:** Adjust relative paths to point to `../L2-semantic/{module}/filename.md` from module directories, and `./L2-semantic/{module}/filename.md` from root.

---

**BUG-015 — L4 monoliths contain broken cross-references that bypass validation**

- **Location:** `05-assemble-references.py`, `08-validate.py`
- **Confidence:** Confirmed
- **Description:** Script `05` concatenates L2 files that contain relative cross-links (e.g., `../luci/api.md`). These links were valid from `L2-semantic/wiki/`, but the L4 monolith lives in `OUTDIR/{module}/`, where the relative paths break. Script `08` only validates links inside `L2-semantic/` files, not L4 monoliths.
- **Failure scenario:** L4 reference files are full of broken internal links. CI passes.
- **Status:** FIXED (Corrected with ../L2-semantic/ prefix)
- **Suggested fix:** Rewrite relative links during assembly in `05` to reflect the new file location, and extend `08` link validation to cover all generated `.md` files.

---

**BUG-016 — Generated `.d.ts` contains invalid TypeScript syntax**

- **Location:** `06c-generate-ide-schemas.py`
- **Confidence:** Confirmed
- **Description:** Ucode docs use `[param]` to indicate optional parameters. The parser passes this through as `[param]: any`, which is illegal TypeScript (array destructuring syntax). Additionally, the parameterized function path omits the return type annotation, and global functions bypass parameter extraction entirely.
- **Failure scenario:** The generated `ucode.d.ts` file has syntax errors. TypeScript language servers report errors instead of providing autocomplete.
- **Status:** FIXED (Handled brackets and return types)
- **Suggested fix:** Strip brackets and append `?` for optional params (e.g., `param?: any`). Append `: {f['returns']}` to parameterized signatures. Apply parameter extraction to global functions.

---

**BUG-020 — `02e` is incorrectly gated by `SKIP_BUILDROOT`**

- **Location:** `openwrt-docs4ai-02e-scrape-example-packages.py`
- **Confidence:** Confirmed
- **Description:** The script exits early when `SKIP_BUILDROOT=true`, but it reads from `repo-luci/applications`, not the OpenWrt buildroot. `repo-luci` is always cloned regardless of the buildroot skip flag.
- **Failure scenario:** LuCI application examples are silently dropped from documentation whenever the buildroot clone is skipped, even though the data source is available.
- **Status:** FIXED (Removed gate)
- **Suggested fix:** Remove the `SKIP_BUILDROOT` gate and replace with a direct existence check on the `repo-luci/applications` directory.

---

## 🟡 Medium Severity

**BUG-006 — Matrix artifact upload may produce empty artifacts when skip flags fire**

- **Location:** `00-pipeline.yml`, extractors `02d`–`02h`
- **Confidence:** Likely
- **Description:** Extractors gated by `SKIP_BUILDROOT` exit 0 without creating `L1-raw/`. The `Upload L1 Artifacts` step attempts to upload this path. With `upload-artifact@v4` defaults, this produces a warning (not a fatal error), but the resulting artifact is empty. Downstream `merge-multiple: true` silently merges fewer files than expected.
- **Failure scenario:** Running with `skip_buildroot: true` causes some L1 artifact slots to be empty. The pipeline completes but documentation coverage is silently reduced beyond what was intended by the skip.
- **Suggested fix:** Add `if-no-files-found: ignore` to the upload step, and add a reconciliation log in `03` listing which L1 modules were actually received.

---

**BUG-017 — False-positive HTML leak detector in validator and wiki scraper**

- **Location:** `08-validate.py`, `02a-scrape-wiki.py`
- **Confidence:** High
- **Description:** Both scripts check for substrings like `"404 Not Found"`, `"Access Denied"`, and `"captcha"` in page content. Script `08` checks the first 500 bytes of every markdown file. Legitimate OpenWrt documentation about firewalls, reverse proxies, or error handling may contain these exact strings as instructional content.
- **Failure scenario:** A valid wiki page titled "Handling 404 Not Found errors" or documenting Cloudflare bypass is flagged as an HTML error leak and rejected.
- **Status:** FIXED (Require structural tags + signature)
- **Suggested fix:** Only trigger on structural HTML markers (`<!DOCTYPE`, `<html`) or require multiple markers to co-occur before flagging.

---

**BUG-019 — `SKIP_AI` defaults to `true` when env var is unset**

- **Location:** `04-generate-ai-summaries.py`
- **Confidence:** Confirmed (may be intentional)
- **Description:** `SKIP_AI = os.environ.get("SKIP_AI", "true").lower() == "true"`. This means local or ad-hoc runs produce no summaries unless the caller explicitly sets `SKIP_AI=false`.
- **Failure scenario:** Developers running locally are surprised that AI summaries are silently skipped. The workflow YAML passes `${{ inputs.skip_ai || 'false' }}`, so CI is unaffected.
- **Suggested fix:** If this is intentional (to avoid accidental API charges), document it prominently. If not, change the default to `"false"`.

---

**BUG-021 — `JSONDecodeError` risk on LLM response parsing**

- **Location:** `04-generate-ai-summaries.py`
- **Confidence:** High
- **Description:** The script parses AI responses with `json.loads(data["choices"][0]["message"]["content"])`. LLMs frequently wrap JSON in markdown code fences (`` ```json ... ``` ``), which causes `json.loads` to fail.
- **Failure scenario:** Valid AI summaries are discarded because the raw response string isn't clean JSON.
- **Suggested fix:** Strip markdown code fences (` ```json` prefix and ` ``` ` suffix) from the response string before parsing.

---

**BUG-022 — Unsafe YAML injection when writing AI summaries to frontmatter**

- **Location:** `04-generate-ai-summaries.py`
- **Confidence:** High
- **Description:** AI summaries are injected into YAML frontmatter via string formatting with naive quote-escaping (`.replace('"', '\\"')`). YAML-significant characters such as colons, newlines, `#`, `{`, `}`, and unbalanced quotes in AI output can corrupt the frontmatter block.
- **Failure scenario:** A summary containing `key: value` or a literal newline breaks YAML parsing in `05` and `06a`, causing the file to be skipped or misread.
- **Suggested fix:** Load frontmatter with `yaml.safe_load()`, update the dict, and re-serialize with `yaml.safe_dump()`.

---

**BUG-023 — Validator syntax checking covers only a small subset of generated code**

- **Location:** `08-validate.py`
- **Confidence:** Confirmed
- **Description:** AST-based syntax checking only runs on `javascript` and `ucode` fenced code blocks inside `OUTDIR/L1-raw/luci-examples/*.md`. Code blocks in ucode JSDoc output (`02b`), LuCI JSDoc output (`02c`), and all L2/L3/L4 files are not checked.
- **Failure scenario:** Syntax errors in generated API documentation escape validation.
- **Suggested fix:** Extend the code-fence scanner to cover all `.md` files under `OUTDIR/` that contain `javascript` or `ucode` fenced blocks.

---

**BUG-024 — Shell API extractor captures only the file header, not function docs**

- **Location:** `02f-scrape-procd-api.py`
- **Confidence:** Confirmed
- **Description:** The script reads lines starting with `#`, skips blank lines with `continue`, and `break`s on the first non-comment, non-blank line. This captures the shebang/copyright/SPDX header at the top and stops before reaching any function-level documentation comments deeper in the file.
- **Failure scenario:** The procd API reference contains only the license header, missing all function documentation.
- **Status:** FIXED (Full file scan implemented)
- **Suggested fix:** Scan the entire file for comment blocks that immediately precede shell function declarations (`^[a-z_]+\s*\(\)`), or at minimum remove the `break` and collect all comment blocks.

---

**BUG-025 — Memory scaling risk in cross-link protection set**

- **Location:** `03-normalize-semantic.py`, `pass_2_link_all()`
- **Confidence:** Likely
- **Description:** The function builds a `set()` of every individual character index inside protected regions (code blocks, inline code, headings) via `prot.update(range(m.start(), m.end()))`. A single 50KB code block adds 50,000 integers to the set.
- **Failure scenario:** Files with large code blocks cause significant memory pressure, potentially triggering OOM on CI runners processing many files.
- **Suggested fix:** Store protected regions as a sorted list of `(start, end)` tuples and check membership with binary search or interval overlap testing.

---

**BUG-026 — Missing return type annotation in generated `.d.ts` for parameterized functions**

- **Location:** `06c-generate-ide-schemas.py`
- **Confidence:** Confirmed
- **Description:** When parameters are successfully parsed, the signature is built as `{name}({params})` without appending `: {returns}`. The return type is only included in the fallback `...args: any[]` path.
- **Failure scenario:** IDE autocomplete shows parameter names but no return type for most functions.
- **Suggested fix:** Change the parameterized path to `sig_ts = f"{f['name']}({', '.join(ts_params)}): {f['returns']}"`.

---

**BUG-027 — Subprocess failures in JSDoc generators are treated as clean skips**

- **Location:** `02b-scrape-ucode.py`, `02c-scrape-jsdoc.py`
- **Confidence:** High
- **Description:** Both scripts run `jsdoc2md` via `subprocess.run()` and capture stdout/stderr, but neither checks `res.returncode`. A tool crash that produces no stdout is indistinguishable from "no documentation found" — both result in a "SKIP" log.
- **Failure scenario:** A broken npm dependency or jsdoc2md crash silently produces zero documentation. The script exits 0 if at least one other file succeeded.
- **Status:** FIXED (Check res.returncode added)
- **Suggested fix:** Check `res.returncode != 0` and either log an explicit error or increment a failure counter that gates exit status.

---

**BUG-028 — Baseline path in changelog generator is CWD-dependent**

- **Location:** `06d-generate-changelog.py`
- **Confidence:** Medium
- **Description:** `BASELINE_DIR = os.path.join(os.getcwd(), "baseline")`. The script works in CI (where CWD is the repo root) but breaks if invoked from a subdirectory during local development.
- **Failure scenario:** Changelog reports all symbols as "added" because baseline lookup silently fails.
- **Suggested fix:** Resolve relative to `os.path.dirname(os.path.abspath(__file__))` or accept the path via an environment variable.

---

**BUG-029 — Duplicate initialization block in AI summary script**

- **Location:** `04-generate-ai-summaries.py`
- **Confidence:** Confirmed
- **Description:** Lines ~20–35 duplicate the imports, `sys.path.insert`, `OUTDIR`, `SKIP_AI`, and `MAX_FILES` assignments from lines ~1–19. This also creates a second `SKIP_AI` check and `sys.exit(0)` call, and a second `import requests` inside a try/except.
- **Failure scenario:** No runtime error, but maintenance risk: fixes applied to one block may not be applied to the other. The duplicate `SKIP_AI` gate is dead code since the first one already exited.
- **Suggested fix:** Delete the duplicate block entirely.

---

**BUG-030 — Unescaped HTML interpolation in generated `index.html`**

- **Location:** `07-generate-index-html.py`
- **Confidence:** Likely
- **Description:** Module names and descriptions from `llms.txt` are interpolated directly into HTML `<li>` elements without escaping. If any description contains `<`, `>`, `&`, or `"`, the HTML structure breaks.
- **Failure scenario:** A module description containing `<script>` or angle brackets corrupts the landing page layout.
- **Status:** FIXED (html.escape applied)
- **Suggested fix:** Apply `html.escape()` to all text fields before interpolation. The `html` module is already imported in several other scripts.

---

**BUG-038 — (NEW) Code-fence protection regex matches wrong delimiters**

- **Location:** `03-normalize-semantic.py`, `pass_2_link_all()`
- **Confidence:** Confirmed
- **Description:** The protected-region regex includes the pattern `~~~.*?---` which attempts to match tilde-fenced code blocks. However, tilde blocks close with `~~~`, not `---`. The `---` is a YAML frontmatter delimiter. This pattern can incorrectly match from a tilde fence opening all the way to a YAML frontmatter boundary, protecting far too much content (or too little, if no `---` follows).
- **Failure scenario:** Cross-links are either incorrectly injected inside tilde-fenced code blocks, or incorrectly suppressed across large regions of body text.
- **Suggested fix:** Change `~~~.*?---` to `~~~.*?~~~` in the regex pattern.

---

**BUG-039 — (NEW) Double delay per wiki page doubles scrape time**

- **Location:** `02a-scrape-wiki.py`
- **Confidence:** Confirmed
- **Description:** The page-processing loop calls `time.sleep(DELAY)` before `fetch_page_lastmod()` and again before the raw content fetch. With `DELAY = 1.5`, each page incurs 3 seconds of sleep even though only one external request per step needs throttling.
- **Failure scenario:** A 200-page wiki scrape takes ~10 minutes of pure sleep time instead of ~5 minutes.
- **Suggested fix:** Remove the first `time.sleep(DELAY)` before the HEAD request, or reduce it. The delay before the content GET is sufficient for politeness.

---

**BUG-040 — (NEW) Pandoc return code is not checked**

- **Location:** `02a-scrape-wiki.py`
- **Confidence:** Confirmed
- **Description:** The `subprocess.run()` call to pandoc captures stdout but does not check `result.returncode`. If pandoc fails (e.g., unsupported input, internal error), `result.stdout` may be empty or contain an error message that passes the `len(md) < 200` filter.
- **Failure scenario:** A pandoc conversion failure produces truncated or garbled markdown that is written to L1 as valid output.
- **Suggested fix:** Check `result.returncode != 0` and log/skip the page on failure.

---

**BUG-041 — (NEW) `procd` is in COMMON_WORDS, blocking cross-link generation**

- **Location:** `03-normalize-semantic.py`
- **Confidence:** Confirmed
- **Description:** The `COMMON_WORDS` set includes `"procd"`. The `is_code_symbol()` function returns `False` for any symbol in this set. This prevents the procd API from being registered in the cross-link registry.
- **Failure scenario:** No cross-links are generated for `procd` symbols. Wiki pages referencing procd functions are not linked to the procd API documentation.
- **Suggested fix:** Remove `"procd"` from `COMMON_WORDS`. It is a proper module name, not a generic word.

---

**BUG-042 — (NEW) Bare `except` in wiki cache loader swallows all exceptions**

- **Location:** `02a-scrape-wiki.py`, `load_cache()`
- **Confidence:** Confirmed
- **Description:** `load_cache()` uses a bare `except:` clause that catches everything including `KeyboardInterrupt` and `SystemExit`.
- **Failure scenario:** A corrupted cache file silently returns `{}` even if the real error is a permissions issue or disk failure. Ctrl+C during cache loading is swallowed.
- **Status:** FIXED (Except clause narrowed)
- **Suggested fix:** Change to `except (json.JSONDecodeError, ValueError):` or at minimum `except Exception:`.

---

**BUG-043 — (NEW) Subprocess calls across multiple scripts have no timeout**

- **Location:** `02b-scrape-ucode.py`, `02c-scrape-jsdoc.py`, `01-clone-repos.py`
- **Confidence:** Confirmed
- **Description:** The `subprocess.run()` calls for `jsdoc2md`, `npm install`, and `git clone/sparse-checkout` do not specify a `timeout` parameter. Script `02a` sets `timeout=30` for pandoc, demonstrating the pattern is known.
- **Failure scenario:** A hung external tool (npm registry timeout, git fetch stall) blocks the CI job until the runner's global timeout kills it, wasting runner minutes with no diagnostic output.
- **Suggested fix:** Add `timeout=120` (or appropriate per-tool value) to all `subprocess.run()` calls.

---

**BUG-044 — (NEW) `LLM_BUDGET_LIMIT` is logged but never enforced**

- **Location:** `04-generate-ai-summaries.py`
- **Confidence:** Confirmed
- **Description:** The script logs `config.LLM_BUDGET_LIMIT` in its progress message but never tracks token usage or cost against it. There is no mechanism to stop API calls when the budget is exceeded.
- **Failure scenario:** A large run with many uncached files exceeds the intended budget with no automatic cutoff.
- **Suggested fix:** Either implement cost tracking and enforcement, or remove the budget reference from the log message to avoid implying it is enforced.

---

## 🟢 Low Severity

**BUG-031 — Monolithic and skeleton files are not indexed in `llms.txt`**

- **Location:** `06a-generate-llms-txt.py`
- **Confidence:** Confirmed
- **Description:** Script `06a` indexes only L2 files. The `*-complete-reference.md` and `*-skeleton.md` files generated by `05` are not listed. `AGENTS.md` tells AI agents to use these files, but they cannot discover them through the index.
- **Suggested fix:** Add an explicit pass in `06a` that indexes L3/L4 artifacts from each module's output directory.

---

**BUG-032 — Short wiki pages are silently dropped without tracking**

- **Location:** `02a-scrape-wiki.py`
- **Confidence:** Confirmed
- **Description:** Pages whose converted markdown is under 200 characters are skipped via `continue` without incrementing any counter or logging.
- **Suggested fix:** Increment a `skipped_short` counter, log the page path, and include it in the final summary.

---

**BUG-033 — Redundant `GITHUB_ENV` mapping in workflow**

- **Location:** `00-pipeline.yml`, `initialize` job
- **Confidence:** Confirmed
- **Description:** The Clone Repositories step maps `GITHUB_ENV: ${{ github.env }}` in its `env:` block. GitHub Actions already provides `GITHUB_ENV` natively to all steps. The explicit mapping is redundant and could confuse maintainers.
- **Suggested fix:** Remove the explicit `GITHUB_ENV` mapping from the step's `env:` block.

---

**BUG-034 — Primary cache keys include `run_id`, guaranteeing primary misses**

- **Location:** `00-pipeline.yml`
- **Confidence:** Confirmed
- **Description:** Wiki and AI cache keys use `${{ github.run_id }}` in the primary key, making it unique per run. Caching only works via the `restore-keys` prefix fallback, which is less efficient and accumulates stale cache entries.
- **Suggested fix:** Use a content-hash or date-based primary key (e.g., `wiki-cache-${{ runner.os }}-${{ hashFiles('...') }}`) with a stable restore-key prefix.

---

**BUG-035 — `repo-manifest.json` is expected but never generated**

- **Location:** `00-pipeline.yml`, `01-clone-repos.py`, `03-normalize-semantic.py`
- **Confidence:** Confirmed
- **Description:** The workflow artifact upload includes `repo-manifest.json`. Script `03` attempts to copy it during staging promotion. But `01` never creates this file.
- **Suggested fix:** Add manifest generation to `01` (a JSON file recording repo URLs, commits, and clone timestamps), or remove the references.

---

**BUG-036 — Dead `failed_count` variable in LuCI JSDoc scraper**

- **Location:** `02c-scrape-jsdoc.py`
- **Confidence:** Confirmed
- **Description:** `failed_count` is initialized to `0` but is never incremented or reported. Failures are not tracked.
- **Status:** FIXED (Increment added)
- **Suggested fix:** Increment `failed_count` when `jsdoc2md` fails or produces empty output, and include it in the completion summary.

---

**BUG-037 — Version banner in `llms.txt` omits ucode commit**

- **Location:** `06a-generate-llms-txt.py`
- **Confidence:** Confirmed
- **Description:** The `versions` list includes `openwrt/openwrt` and `openwrt/luci` commits but does not include `UCODE_COMMIT`.
- **Suggested fix:** Add `f"jow-/ucode@{os.environ.get('UCODE_COMMIT', 'unknown')}"` to the versions list.

---

### Withdrawn

**~~BUG-018~~ — HTML landing page regex coupling (FALSE POSITIVE)**

- **Original claim:** The regex in `07` fails to match the output format of `06a`.
- **Reason for withdrawal:** The root `llms.txt` uses the format `- [name](path): description (~N tokens)`, and the regex `r'- \[(.*?)\]\((.*?)\): (.*)'` matches this correctly. The user's description confused the root `llms.txt` format with the `llms-full.txt` format. The HTML generator works as written (though it still has BUG-004 and BUG-030).

---

### Verification Suggestions

1. **Parse smoke test:** `python -m py_compile .github/scripts/openwrt-docs4ai-01-clone-repos.py` will confirm BUG-001. Same for `06b` (BUG-002).
2. **Split-brain proof (BUG-005):** Run `03`, manually edit an L2 file in `WORKDIR`, run `05`, and confirm the edit is absent from the L4 monolith.
3. **HTML leak false positive (BUG-017):** Create a file whose first line is `# Configuring 404 Not Found pages`, run `08-validate.py`, and observe the hard failure.
4. **Slug collision (BUG-011):** Feed two dummy files named `subdir1/main.js` and `subdir2/main.js` through `02c`'s slug logic and confirm both produce `api-main`.
5. **Cache miss rate (BUG-007):** Run `04` twice on the same input and observe that every file triggers an API call on the second run.
6. **Workflow skip-flag test (BUG-006, BUG-020):** Dispatch with `skip_buildroot: true` and verify that LuCI examples (`02e`) are incorrectly skipped and that matrix artifact counts match expectations.