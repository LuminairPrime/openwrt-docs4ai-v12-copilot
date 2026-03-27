# Project Code Review & Improvement Roadmap

Based on extensive interaction with the `openwrt-docs4ai-pipeline` architecture, test suite, and CI workflows, here is a categorized list of identified technical debt and recommended improvements, culminating in two comprehensive proposals to resolve the current pipeline-blocking `05a` link mapping failure.

---

## 1. CI/CD Architecture & Extractor Matrix

**The Problem:** 
The pipeline relies on a hardcoded JSON array in `openwrt-docs4ai-00-pipeline.yml` for the `extract` matrix. Dependencies like `jsdoc-to-markdown` or `pandoc` are gated by clunky `if: matrix.script == '02...'` conditionals. As new extractors are added, this becomes a maintenance hazard (which caused the recent `02b` CI failure).

**Improvements:**
*   **Centralized Extractor Manifest:** Create an `extractors.yaml` file that acts as the single source of truth. The GitHub Action setup job reads this file to dynamically generate the matrix, automatically injecting required dependencies (npm, apt), environment flags (`SKIP_BUILDROOT`), and execution paths.
*   **Composite Actions:** The upload/download artifact boilerplate is repeated heavily across L0, L1, and L2 boundaries. Moving this into a `.github/actions/sync-l1-artifacts/action.yml` composite action would strip hundreds of lines of YAML from the main workflow.
*   **Strict Mode Fast-Failing:** The `extract` matrix currently uses `continue-on-error: true`, meaning a catastrophic extractor failure forces the pipeline to burn CI minutes running downstream steps on empty data before finally erroring out. Implement a "strict mode" boolean that hard-fails the matrix immediately.
*   **Unpinned/Uncached NPM Dependencies:** The pipeline currently runs `npm install -g jsdoc-to-markdown` fetching `latest` blindly over the network. A broken upstream package will instantly break `main`. We must pin the version (e.g., `jsdoc-to-markdown@9.0.0`) and use `actions/setup-node` to cache the global modules.

## 2. Testing & Validation Robustness

**The Problem:** 
The pytest suite relies on brittle string-matching, misses negative test cases, and couples integration assertions to fragile directory discovery loops.

**Improvements:**
*   **Naive Substring Assumptions (`pytest_01_workflow_contract_test.py`):** Our workflow tests manually assert `assert "02c-scrape-jsdoc.py" in condition`. This substring logic is easily fooled if a developer writes negative conditions (e.g. `!=`). We must test evaluated YAML ASTs rather than raw strings.
*   **False-Positive Integration Tests (`pytest_09_release_tree_contract_test.py`):** The integration tests scan the compiled release tree iterating over `Path.rglob("*.md")`. If the pipeline fatally fails upstream and creates zero L4 output files, the iterators never run and the tests pass unconditionally. Implement strict structural minimum assertions (e.g., `assert req_files > 0`) before test loops.
*   **Pytest Fixture Virtualization & HTTP Mocking:** Mock the `WORKDIR` using pytest `tmp_path` fixtures rather than creating real `./tmp/ci/` paths. Additionally, use `responses` or `vcrpy` to record/replay the HTTP requests in `02a-scrape-wiki.py` to massively speed up tests and prevent external rate limits.

---

## 3. The Central Crisis: Cross-Module Relative Linking

**The Problem:**
The most critical failure currently blocking the pipeline is inside `05a-assemble-references.py`. The script attempts to rewrite markdown links authored in `content/cookbook-source/` (like `[text](../../module/file.md)`) so they correctly point to the compiled `release-tree/cookbook/chunked-reference/` depth.

When we tightened the `05a` regex to `((?!L2-semantic)[a-zA-Z0-9-]+)` to prevent recursive module loops, we strictly blocked the character `.` from matching as a module name. As a side-effect, the script now completely **ignores** all `../../` traversing links. Because `05a` bypasses them, they are deposited directly into the final `release-tree` un-rewritten, causing immediate `08-validate-output` hard failures when the links inevitably misroute out-of-bounds in the published static site.

To solve this permanently, we must abandon regex entirely. Below are two comprehensive architectural proposals for fixing this.

---

### Remediation Plan A: L2 Flat Linking (Semantic Normalization)
**Core Concept:** Authors should never need to perform "mental geometry" mapping `../../` paths to a hypothetical future `release-tree` output. All relative links should be mathematically flattened strictly into a single domain depth (e.g., `../module/file.md`).

**Implementation Steps:**
1. **Redefine Authoring Spec:** Update `cookbook-authoring-spec.md`. Authors write links exactly as if all modules sit side-by-side in a flat folder: `[See LuCI](../luci/file.md)`. 
2. **Semantic Normalizer (`03`):** Update `03-normalize-semantic.py` (not the L1 ingestion scripts, as L1 MUST remain raw). During the transition from `L1-raw/cookbook/` to `L2-semantic/cookbook/`, `03` intercepts the markdown and ensures all cross-module relative links adhere to the flat `../module/file.md` standard.
3. **Smart Serialization (`05a`):** With the L2 data completely flat, `05a-assemble-references.py` becomes drastically simpler. Since `05a` knows EXACTLY where it is placing a file, it simply calculates the algebraic filesystem path delta. 
   * If writing to `release-tree/module/bundled-reference.md`, the output depth is `1`. A link `../luci/foo.md` stays `../luci/foo.md`.
   * If writing to `release-tree/module/chunked-reference/file.md`, the output depth is `2`. A link `../luci/foo.md` is mathematically adjusted to `../../luci/chunked-reference/foo.md` via `os.path.relpath`.

**Pros:** Radically simplifies authoring rules. Flattens data complexity at the L2 layer where it belongs.
**Cons:** Requires migrating existing cookbook files and retraining authors who are used to `../../`.

---

### Remediation Plan B: Robust AST Byte-Offset Replacement (05a Assembly)
**Core Concept:** Leave the authoring behavior exactly as it is today (`../../module/file.md`). Instead of relying on brittle Python regex strings, upgrade `05a-assemble-references.py` to utilize a native Abstract Syntax Tree (AST) parser to locate links, but specifically use **byte-offset string slicing** to modify them.

**Implementation Steps:**
1. **Dependencies:** Introduce `markdown-it-py` to the pipeline's Python environment.
2. **AST Parsing Engine (`05a`):** Do NOT parse and re-serialize the entire AST (e.g. `md.render()`). Converting ASTs *back* into raw Markdown is notoriously lossy and often destroys author formatting (e.g., altering list indents, stripping raw HTML).
3. **Byte-Offset Slicing:** Use the AST specifically in read-only mode to find `link_open` tokens. Extract the exact start and end byte/character offsets of the `href` attribute from the token's source mapping.
4. **Geometry Resolver:** Extract the authored `../../module/file.md` string from that offset. Leverage `pathlib.PurePosixPath` to map it into an absolute representation `root/module/file`, append the `/chunked-reference/` boundary natively, and translate it backward via `os.path.relpath()` to the exact target artifact.
5. **Implantation:** Slice the original raw markdown string using the exact token offsets and inject the new URL. The remainder of the markdown file remains untouched, preserving 100% fidelity.

**Pros:** Future-proof. Inherently ignores HTML anchors, codeblock noise, and string literals. Zero risk of formatting destruction because it doesn't re-render the document.
**Cons:** Requires precise offset map manipulation.
