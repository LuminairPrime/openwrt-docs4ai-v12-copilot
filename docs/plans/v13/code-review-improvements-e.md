# Code Review Improvements E: Consolidated Execution Prompt

Supersedes C and D. Grounded in the actual repository state after the `02c-05a-refactor-sonnet.md` refactor was executed.

## Prompt

You are the implementation agent for `openwrt-docs4ai-pipeline`. Execute the fixes below in a single focused pass. This is an execution brief, not a planning exercise.

---

## Situation

The refactor plan (`02c-05a-refactor-sonnet.md`) was executed. It changed the 05a link rewrite regex from `[^/)]+` to `[a-zA-Z0-9-]+` for the module name capture group, and updated the cookbook authoring spec to say authors write `../../<module>/chunked-reference/<topic>.md` (which 05a passes through unchanged). It also added a conditional npm install step gated on `02b` and `02c`.

### Problem 1: Spec/source mismatch - cookbook files do not match the spec

The spec now says cross-module links use `../../<module>/chunked-reference/<topic>.md`. But the actual cookbook source files still use the old format without `chunked-reference/`:

```
content/cookbook-source/luci-form-with-uci.md:313
  [luci-app-example form.js](../../luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md)

content/cookbook-source/uci-read-write-from-ucode.md:243
  [ucode UCI module reference](../../ucode/c_source-api-module-uci.md)

content/cookbook-source/procd-service-lifecycle.md:200
  [procd API Reference](../../procd/header_api-procd-api.md)

content/cookbook-source/minimal-openwrt-package-makefile.md:252
  [Wiki: Creating packages](../../wiki/wiki_page-guide-developer-packages.md)
```

These links travel through the pipeline as-is. At `release-tree/cookbook/chunked-reference/my-guide.md`, a link `../../ucode/c_source-api-module-uci.md` resolves to `release-tree/ucode/c_source-api-module-uci.md`, which does not exist. The file lives at `release-tree/ucode/chunked-reference/c_source-api-module-uci.md`. Stage `08` correctly rejects these as broken links.

### Problem 2: 02b npm gating is wrong

The workflow currently installs `jsdoc-to-markdown` for both `02b` and `02c`:

```yaml
- name: Install jsdoc-to-markdown (02b/02c only)
  if: matrix.script == '02c-scrape-jsdoc.py' || matrix.script == '02b-scrape-ucode.py'
  run: npm install -g jsdoc-to-markdown
```

`02b-scrape-ucode.py` parses C header files. It does not use `jsdoc-to-markdown`. Only `02c` needs it.

### Problem 3: Unpinned npm dependency

`jsdoc-to-markdown` is installed without a version pin. A breaking upstream release will instantly break `main`.

### Problem 4: script-dependency-map.md is wrong for 02b

The dependency map says `02b` needs `jsdoc-to-markdown (npm global)`:

```
| `02b-scrape-ucode.py` | L1 extraction | ... | `jsdoc-to-markdown` (npm global) | none |
```

This is incorrect. `02b` has no external tool dependencies.

### Problem 5: Weak test assertions hide the bug

The existing tests in `TestRewriteReleaseChunkedLinks` check that `../../module/file.md` does not produce `../../../` in the output:

```python
def test_dot_dot_is_not_injected_into_rewritten_path(self):
    assemble = load_script_module("assemble_05a_9", "openwrt-docs4ai-05a-assemble-references.py")
    result = assemble.rewrite_release_chunked_links("[see](../../luci-examples/file.md)")
    assert "../../../" not in result
```

This test passes because the link goes through unchanged because the regex cannot match `../../`, not because it was correctly rewritten. The test should assert that the output contains `chunked-reference/` for links that need it, or if the fix is to update the cookbook files, should assert that `../../module/file.md` without `chunked-reference/` passes through unchanged. After Step 1, pass-through is the correct contract.

---

## Decision: Fix cookbook files, not the regex

There are two valid approaches:

**Option A** (recommended): Update the 4 cookbook source files to include `/chunked-reference/` in their links, matching the spec. The 05a regex already passes these through unchanged. This is 4 one-line edits and zero code changes.

**Option B**: Change 05a to detect `../../module/file.md` and insert `/chunked-reference/`. This requires regex changes, risks new edge cases, and contradicts the spec that was just deliberately written.

**Choose Option A** because:
- The spec was intentionally updated in the refactor to say "authors write the final form"
- The regex was intentionally tightened to reject `..` as a module name
- Adding insertion logic re-introduces the complexity the refactor was designed to remove
- 4 source file edits are simpler and more durable than regex surgery

---

## Invariants

- Do not change numbered script names, the layer model, or the release-tree public contract.
- Do not introduce lossy markdown re-rendering.
- Use minimal diffs. No unrelated refactors.

---

## Implementation Steps

### Step 1: Fix the 4 cookbook source files

Insert `/chunked-reference/` into the 4 cross-module links so they match the spec.

**File: `content/cookbook-source/luci-form-with-uci.md` line 313**

Before:
```markdown
- [luci-app-example form.js](../../luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md) — real-world reference implementation from LuCI upstream
```

After:
```markdown
- [luci-app-example form.js](../../luci-examples/chunked-reference/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md) — real-world reference implementation from LuCI upstream
```

**File: `content/cookbook-source/uci-read-write-from-ucode.md` line 243**

Before:
```markdown
- [ucode UCI module reference](../../ucode/c_source-api-module-uci.md) — full cursor API with all method signatures
```

After:
```markdown
- [ucode UCI module reference](../../ucode/chunked-reference/c_source-api-module-uci.md) — full cursor API with all method signatures
```

**File: `content/cookbook-source/procd-service-lifecycle.md` line 200**

Before:
```markdown
- [procd API Reference](../../procd/header_api-procd-api.md) — full parameter list for `procd_set_param`
```

After:
```markdown
- [procd API Reference](../../procd/chunked-reference/header_api-procd-api.md) — full parameter list for `procd_set_param`
```

**File: `content/cookbook-source/minimal-openwrt-package-makefile.md` line 252**

Before:
```markdown
- [Wiki: Creating packages](../../wiki/wiki_page-guide-developer-packages.md) — full reference for all Makefile variables
```

After:
```markdown
- [Wiki: Creating packages](../../wiki/chunked-reference/wiki_page-guide-developer-packages.md) — full reference for all Makefile variables
```

**Verification:** After this change, search `content/cookbook-source/` for `](../../`. Every cross-module cookbook link should contain `/chunked-reference/` in the path. If any do not, fix them too.

---

### Step 2: Fix the 02b npm gating in the workflow

**File: `.github/workflows/openwrt-docs4ai-00-pipeline.yml`**

Find:
```yaml
      - name: Install jsdoc-to-markdown (02b/02c only)
        if: matrix.script == '02c-scrape-jsdoc.py' || matrix.script == '02b-scrape-ucode.py'
        run: npm install -g jsdoc-to-markdown
```

Replace with:
```yaml
      - name: Install jsdoc-to-markdown (02c only)
        if: matrix.script == '02c-scrape-jsdoc.py'
        run: npm install -g jsdoc-to-markdown@9.1.1
```

This removes the wrong `02b` gating and pins the version. Verify the current stable version with `npm view jsdoc-to-markdown version` and use that exact version if it differs.

---

### Step 3: Fix the script-dependency-map.md

**File: `docs/specs/script-dependency-map.md`**

Change the `02b` row from:
```
| `02b-scrape-ucode.py` | L1 extraction | `WORKDIR/repo-ucode/` | `WORKDIR/L1-raw/ucode/` | `01` | `jsdoc-to-markdown` (npm global) | none |
```

To:
```
| `02b-scrape-ucode.py` | L1 extraction | `WORKDIR/repo-ucode/` | `WORKDIR/L1-raw/ucode/` | `01` | none | none |
```

---

### Step 4: Strengthen the test assertions

**File: `tests/pytest/pytest_00_pipeline_units_test.py`**

The goal is to make the 05a link rewrite tests assert the correct positive behavior, not just the absence of malformed output.

**4a.** In `TestRewriteReleaseRelativeLinks`, update the existing `test_dot_dot_is_not_injected_into_rewritten_path` to assert the pass-through contract instead of only checking for malformed fragments:

The current regex cannot match `../../module/file.md` at all because `..` is not in `[a-zA-Z0-9-]`, so the link passes through unchanged. After Step 1, this is the correct behavior because authors include `/chunked-reference/` themselves. The test should assert the link is unchanged:

```python
def test_dot_dot_is_not_injected_into_rewritten_path(self):
    assemble = load_script_module("assemble_05a_6", "openwrt-docs4ai-05a-assemble-references.py")
    link = "[see](../../luci-examples/file.md)"
    result = assemble.rewrite_release_relative_links(link)
    assert result == link, f"Expected unchanged pass-through, got: {result}"
```

**4b.** In `TestRewriteReleaseChunkedLinks`, update the existing `test_dot_dot_is_not_injected_into_rewritten_path` the same way:

```python
def test_dot_dot_is_not_injected_into_rewritten_path(self):
    assemble = load_script_module("assemble_05a_9", "openwrt-docs4ai-05a-assemble-references.py")
    link = "[see](../../luci-examples/file.md)"
    result = assemble.rewrite_release_chunked_links(link)
    assert result == link, f"Expected unchanged pass-through, got: {result}"
```

**4c.** In `TestRewriteRelativeLinks`, update the existing `test_dot_dot_is_not_treated_as_module_name` to assert the pass-through contract instead of the current malformed-fragment checks:

```python
def test_dot_dot_is_not_treated_as_module_name(self):
    assemble = load_script_module("assemble_05a_3", "openwrt-docs4ai-05a-assemble-references.py")
    link = "[see](../../luci-examples/file.md)"
    result = assemble.rewrite_relative_links("cookbook", link)
    assert result == link, f"Expected unchanged pass-through, got: {result}"
```

**4d.** Add a new test class that exercises the real cookbook link patterns:

```python
class TestCookbookCrossModuleLinkContract:
    """The exact link shapes used in cookbook source files must be handled correctly."""

    def test_authored_chunked_reference_link_passes_through_rewrite_relative(self):
        assemble = load_script_module("assemble_05a_cb1", "openwrt-docs4ai-05a-assemble-references.py")
        link = "[ucode UCI](../../ucode/chunked-reference/c_source-api-module-uci.md)"
        result = assemble.rewrite_relative_links("cookbook", link)
        assert result == link

    def test_authored_chunked_reference_link_passes_through_release_relative(self):
        assemble = load_script_module("assemble_05a_cb2", "openwrt-docs4ai-05a-assemble-references.py")
        link = "[ucode UCI](../../ucode/chunked-reference/c_source-api-module-uci.md)"
        result = assemble.rewrite_release_relative_links(link)
        assert result == link

    def test_authored_chunked_reference_link_passes_through_release_chunked(self):
        assemble = load_script_module("assemble_05a_cb3", "openwrt-docs4ai-05a-assemble-references.py")
        link = "[ucode UCI](../../ucode/chunked-reference/c_source-api-module-uci.md)"
        result = assemble.rewrite_release_chunked_links(link)
        assert result == link
```

**4e.** Replace the existing workflow contract test `test_jsdoc_npm_install_is_conditional_on_02c_and_02b` with one that matches the corrected contract, and add a version-pinning assertion:

**File: `tests/pytest/pytest_01_workflow_contract_test.py`**

Replace the existing test with:
```python
def test_jsdoc_npm_install_is_gated_to_02c_only():
    workflow = load_workflow_yaml()
    extract_steps = workflow["jobs"]["extract"]["steps"]
    npm_steps = [s for s in extract_steps if "jsdoc-to-markdown" in s.get("run", "")]
    assert npm_steps, "No jsdoc-to-markdown install step found in extract job"
    for step in npm_steps:
        condition = step.get("if", "")
        assert "02c-scrape-jsdoc.py" in condition, (
            f"jsdoc-to-markdown install not gated to 02c. Got: if: {condition!r}"
        )
        assert "02b-scrape-ucode.py" not in condition, (
            f"jsdoc-to-markdown install should not be gated on 02b. Got: if: {condition!r}"
        )
```

Then add:
```python
def test_jsdoc_npm_install_is_version_pinned():
    workflow = load_workflow_yaml()
    extract_steps = workflow["jobs"]["extract"]["steps"]
    npm_steps = [s for s in extract_steps if "jsdoc-to-markdown" in s.get("run", "")]
    assert npm_steps, "No jsdoc-to-markdown install step found in extract job"
    for step in npm_steps:
        run_text = step["run"]
        assert "@" in run_text, (
            f"jsdoc-to-markdown is not version-pinned. Got: {run_text!r}"
        )
```

---

### Step 5: Verify

Run in this order. Stop at the first failure and fix before continuing.

```powershell
# 1. Confirm no cookbook source files have ../../ without chunked-reference
python -c "
import re, pathlib
for f in pathlib.Path('content/cookbook-source').glob('*.md'):
    for i, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        m = re.search(r'\]\(\.\./\.\./([^)]+)\)', line)
        if m and 'chunked-reference/' not in m.group(1):
            print(f'FAIL: {f.name}:{i} - {m.group(0)}')
"

# 2. Workflow YAML is valid
python -c "import yaml; yaml.safe_load(open('.github/workflows/openwrt-docs4ai-00-pipeline.yml', encoding='utf-8'))"

# 3. Tests pass
python tests/run_pytest.py

# 4. Linting passes
python tests/check_linting.py
```

---

## Explicit Non-Goals

Do not implement any of these in this pass:

- Extracting link rewrite helpers into a separate `lib/` module
- Adding an `extractors.yaml` manifest
- Converting artifact boilerplate into composite actions
- Adding strict-mode fast-fail to the extract matrix
- Adding HTTP mocking for wiki tests
- Changing the 05a regex logic because the current regex is correct for the authoring contract
- Redesigning the layer model or renaming scripts
- Adding a source-repo root `llms.txt`

---

## Acceptance Criteria

All of these must be true:

1. Every cookbook cross-module link under `content/cookbook-source/` that starts with `](../../` includes `/chunked-reference/`.
2. The workflow installs `jsdoc-to-markdown` only for `02c`, with a pinned version.
3. `script-dependency-map.md` shows `none` for `02b` external tools.
4. All existing and new tests pass via `python tests/run_pytest.py`.
5. `python tests/check_linting.py` passes clean.
6. No unrelated file churn.

---

## Files Touched (expected)

| File | Change |
|------|--------|
| `content/cookbook-source/luci-form-with-uci.md` | Insert `/chunked-reference/` in 1 link |
| `content/cookbook-source/uci-read-write-from-ucode.md` | Insert `/chunked-reference/` in 1 link |
| `content/cookbook-source/procd-service-lifecycle.md` | Insert `/chunked-reference/` in 1 link |
| `content/cookbook-source/minimal-openwrt-package-makefile.md` | Insert `/chunked-reference/` in 1 link |
| `.github/workflows/openwrt-docs4ai-00-pipeline.yml` | Remove `02b` condition, pin version |
| `docs/specs/script-dependency-map.md` | Fix `02b` external tools to `none` |
| `tests/pytest/pytest_00_pipeline_units_test.py` | Strengthen 3 assertions, add 1 test class |
| `tests/pytest/pytest_01_workflow_contract_test.py` | Replace 1 test, add 1 test |