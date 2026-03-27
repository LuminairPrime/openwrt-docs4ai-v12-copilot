# 02c / 05a Consolidated Fix and Hardening Plan

**Date:** 2026-03-26
**Branch target:** current working branch
**Applies to:** `openwrt-docs4ai-00-pipeline.yml`, `05a-assemble-references.py`, adjacent test and spec files

---

## Summary

This is a single-PR implementation memo covering two independent but thematically linked problems:

1. **02c / extract matrix** — `pandoc` and `jsdoc-to-markdown` are installed unconditionally for all seven matrix legs, adding ~5 minutes of unnecessary wait time to six of them.
2. **05a / link rewrite** — Three regex-based transform helpers accept `..` as a valid module name, causing `../../module/file.md`-style cookbook links to be rewritten into invalid paths that fail the `08` broken-link validator.

Both bugs share the same underlying cause: a contract that lives implicitly in shell steps or regex character classes rather than in a named, enforceable rule. The fix for each is small and surgical. The hardening work (tests, spec updates) is cheap and should go in the same PR to prevent regression.

**This plan is designed for a single atomic implementation pass.** Steps 1–5 are the required production fixes. Steps 6–8 are the test and documentation hardening that make the fixes verifiable and permanent. Optional work is marked explicitly and can be deferred.

---

## Current Evidence

### 02c — CI timing and dependency waste

In `openwrt-docs4ai-00-pipeline.yml`, the `extract` matrix job (Phase 2b) has a single shared "Install dependencies" step:

```yaml
# lines ~351-353 in the current workflow
- name: Install dependencies
  run: |
    pip install -r .github/scripts/requirements.txt
    sudo apt-get update -qq && sudo apt-get install -y -qq pandoc
    npm install -g jsdoc-to-markdown
```

This step runs identically for all seven matrix entries: `02b`, `02c`, `02d`, `02e`, `02f`, `02g`, `02h`.

- `pandoc` is not used by any of the `02b`–`02h` scripts. The only consumer of `pandoc` is `02a-scrape-wiki.py`, which runs in its own isolated `extract_wiki` job. The `apt-get update` alone takes several minutes of mirror sync time per matrix leg.
- `jsdoc-to-markdown` (npm) is used exclusively by `02c-scrape-jsdoc.py`. The npm global install runs across all seven parallel jobs, installing 80+ packages each time.

The timing marker `EXTRACT_STARTED_EPOCH` is set in the step immediately after dependency install, so the current contract duration metric does not include install overhead. This means pipeline summaries underreport actual elapsed time for non-`02c` legs.

### 05a — Link rewrite regex accepts `..` as a module name

In `openwrt-docs4ai-05a-assemble-references.py`, three functions share a regex that is intended to match cross-module relative links:

```python
# rewrite_relative_links — line 56
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+/.*?\.md)\)'

# rewrite_release_relative_links — line 71
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)'

# rewrite_release_chunked_links — line 86
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)'
```

The capture group `[^/)]+` is intended to match a module name like `luci-examples` or `procd`. But `[^/)]+` accepts any character except `/` and `)`, which means `..` (two dots) is a valid match.

When a cookbook source file contains `[text](../../luci-examples/file.md)`:
1. `\.\.\/` matches the **first** `../`
2. `[^/)]+` matches `..` (the second `..` before the second `/`)
3. `/([^)]*?\.md)` captures `luci-examples/file.md`

The rewrite substitution then produces paths like `../../../chunked-reference/luci-examples/file.md`, which is invalid and immediately caught by `08` as a broken relative link.

The cookbook authoring spec explicitly defines `../../<module>/chunked-reference/<topic>.md` as the correct authored format for cross-module links from cookbook pages. These links are already correct for the release-tree location and must not be rewritten at all. The fix is to ensure the regex cannot match them by restricting the module name to alphanumeric characters and hyphens.

---

## Root Causes

### 02c

Dependency installation is encoded as flat shell commands in a shared workflow step rather than as per-extractor metadata. There is no machine-readable record of which tools each extractor requires, so there is nothing for the workflow or tests to validate against. The cost is hidden behind a start-time marker that executes after the install.

### 05a

The correct module name format (alphanumeric + hyphens, no dots) is an implicit assumption of the regex rather than an explicit constraint. This allows any `../` in a link to be consumed, making the regex sensitive to authored link depth in a way that no authoring rule currently enforces or any test currently checks.

---

## Implementation Steps

These steps are ordered by risk (lowest first) with no inter-step dependencies except where noted. Steps 1–5 produce a correct, shippable diff. Steps 6–8 make it durable.

---

### Step 1 — Fix the 05a regex in all three helpers

**File:** `.github/scripts/openwrt-docs4ai-05a-assemble-references.py`

**Change 1a — `rewrite_relative_links` (line 56):**

```python
# Before
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+/.*?\.md)\)'

# After
r'\[(.*?)\]\(\.\./((?!L2-semantic)[a-zA-Z0-9-]+/.*?\.md)\)'
```

**Change 1b — `rewrite_release_relative_links` (line 71):**

```python
# Before
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)'

# After
r'\[(.*?)\]\(\.\./((?!L2-semantic)[a-zA-Z0-9-]+)/([^)]*?\.md)\)'
```

**Change 1c — `rewrite_release_chunked_links` (line 86):**

```python
# Before
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)'

# After
r'\[(.*?)\]\(\.\./((?!L2-semantic)[a-zA-Z0-9-]+)/([^)]*?\.md)\)'
```

**What this does:** `[a-zA-Z0-9-]+` cannot match `..` because `.` is not in the allowed set. A link starting with `../../` will fail the module-name capture, leave the `re.sub` call with zero matches, and pass the content through unchanged. This is the correct behavior: `../../module/chunked-reference/file.md` links in cookbook pages are already correct for their release-tree location and must not be touched.

**Risk:** Minimal. The change is purely restrictive — it removes a class of false matches. Any previously correct `../module/file.md` pattern continues to work because valid module names (`luci-examples`, `procd`, `uci`, etc.) are all alphanumeric plus hyphens.

---

### Step 2 — Remove unconditional `pandoc` from the `extract` matrix job

**File:** `.github/workflows/openwrt-docs4ai-00-pipeline.yml`

Find the "Install dependencies" step inside the `extract` job (Phase 2b, around line 351):

```yaml
# Before
- name: Install dependencies
  run: |
    pip install -r .github/scripts/requirements.txt
    sudo apt-get update -qq && sudo apt-get install -y -qq pandoc
    npm install -g jsdoc-to-markdown
```

```yaml
# After
- name: Install dependencies
  run: pip install -r .github/scripts/requirements.txt
- name: Install jsdoc-to-markdown (02c only)
  if: matrix.script == '02c-scrape-jsdoc.py'
  run: npm install -g jsdoc-to-markdown
```

**What this does:**
- Removes the `apt-get update + apt install pandoc` line entirely. `pandoc` is unused in this job.
- Moves the `npm install` behind an `if` condition so it only runs in the `02c` matrix leg.
- The six non-`02c` legs drop ~5 minutes of blocked mirror sync and npm install time. The `02c` leg is unchanged in behavior, only the step is now named and conditional.

**Risk:** Low. The only behavioral change is the absence of two tools that were never used by six of seven scripts. The `02c` leg retains full npm support. No Python dependencies change.

**Note on timing:** The existing `EXTRACT_STARTED_EPOCH` timer starts after the installation steps, so it does not need to move. Installation time is not included in the current contract metrics and removing the install removes the hidden overhead. If precise split timing (install vs. extract) is desired later, that is a separate optional improvement.

---

### Step 3 — Add unit tests for the three link rewrite helpers

**File:** `tests/pytest/pytest_00_pipeline_units_test.py`

Add a test class (or standalone test functions) that directly exercises the three helper functions from `05a`:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import importlib.util

# Load 05a without executing module-level side effects
spec = importlib.util.spec_from_file_location(
    "assemble",
    os.path.join(os.path.dirname(__file__), '../../.github/scripts/openwrt-docs4ai-05a-assemble-references.py'),
)


class TestRewriteRelativeLinks:
    """rewrite_relative_links must not corrupt double-dot authored links."""

    def test_single_level_cross_module_link_is_rewritten(self):
        from assemble_05a import rewrite_relative_links  # adjust import to match actual load strategy
        result = rewrite_relative_links("cookbook", "[see](../luci-examples/topic.md)")
        assert "L2-semantic" in result

    def test_double_dot_link_is_passed_through_unchanged(self):
        from assemble_05a import rewrite_relative_links
        link = "[see](../../luci-examples/chunked-reference/topic.md)"
        result = rewrite_relative_links("cookbook", link)
        assert result == link, f"Expected unchanged, got: {result}"

    def test_dot_dot_is_not_treated_as_module_name(self):
        from assemble_05a import rewrite_relative_links
        result = rewrite_relative_links("cookbook", "[see](../../luci-examples/file.md)")
        assert "L2-semantic/../" not in result
        assert "../../../" not in result


class TestRewriteReleaseRelativeLinks:
    """rewrite_release_relative_links must not corrupt double-dot authored links."""

    def test_single_level_link_is_rewritten(self):
        from assemble_05a import rewrite_release_relative_links
        result = rewrite_release_relative_links("[see](../luci-examples/topic.md)")
        assert "chunked-reference" in result

    def test_double_dot_link_is_passed_through_unchanged(self):
        from assemble_05a import rewrite_release_relative_links
        link = "[see](../../luci-examples/chunked-reference/topic.md)"
        result = rewrite_release_relative_links(link)
        assert result == link

    def test_dot_dot_is_not_injected_into_rewritten_path(self):
        from assemble_05a import rewrite_release_relative_links
        result = rewrite_release_relative_links("[see](../../luci-examples/file.md)")
        assert "/../" not in result
        assert "../../../" not in result


class TestRewriteReleaseChunkedLinks:
    """rewrite_release_chunked_links must not corrupt double-dot authored links."""

    def test_single_level_link_is_rewritten(self):
        from assemble_05a import rewrite_release_chunked_links
        result = rewrite_release_chunked_links("[see](../luci-examples/topic.md)")
        assert "chunked-reference" in result

    def test_double_dot_link_is_passed_through_unchanged(self):
        from assemble_05a import rewrite_release_chunked_links
        link = "[see](../../luci-examples/chunked-reference/topic.md)"
        result = rewrite_release_chunked_links(link)
        assert result == link

    def test_dot_dot_is_not_injected_into_rewritten_path(self):
        from assemble_05a import rewrite_release_chunked_links
        result = rewrite_release_chunked_links("[see](../../luci-examples/file.md)")
        assert "/../" not in result
```

**Implementation note on imports:** `05a` uses a `sys.path.insert` for `lib/` and has module-level side effects (OUTDIR check). Use `importlib.util` with a mock environment or extract the three helper functions into a small helper module that can be imported cleanly. The simplest no-refactor path is to set `OUTDIR` to a temp dir in a `conftest.py` fixture before importing, or to invoke the functions via a thin subprocess wrapper. Check how `pytest_09_release_tree_contract_test.py` imports `08-validate-output.py` for the established pattern in this project.

---

### Step 4 — Add regression tests for the broken link shapes in `pytest_09`

**File:** `tests/pytest/pytest_09_release_tree_contract_test.py`

Add a test that plants a cookbook release-tree file containing a `../../luci-examples/chunked-reference/topic.md` link, runs the `08` broken-link checker against a fixture tree that contains the corresponding file, and asserts zero failures:

```python
def test_cookbook_double_dot_cross_module_link_passes_validation(tmp_path):
    """
    A cookbook chunked page with a ../../module/chunked-reference/topic.md link
    must not be reported as a broken link when the target exists.
    This is the exact shape that triggered the 05a regex bug.
    """
    release_tree = tmp_path / "release-tree"
    cookbook_chunked = release_tree / "cookbook" / validate.config.MODULE_CHUNKED_REF_DIRNAME
    luci_chunked = release_tree / "luci-examples" / validate.config.MODULE_CHUNKED_REF_DIRNAME
    cookbook_chunked.mkdir(parents=True)
    luci_chunked.mkdir(parents=True)

    # The broken output that 05a used to produce
    broken_link = "../../luci-examples/chunked-reference/topic.md"
    cookbook_chunked.joinpath("my-guide.md").write_text(
        f"# My Guide\n\nSee [{broken_link}]({broken_link}).\n",
        encoding="utf-8",
    )
    luci_chunked.joinpath("topic.md").write_text("# topic\n", encoding="utf-8")

    hard_failures, _ = validate.check_release_tree_links(release_tree)
    assert hard_failures == [], f"Expected no broken links, got: {hard_failures}"
```

Also add a complementary negative test confirming that an actually broken path (wrong module name or missing file) does produce a failure, to verify the validator is exercised:

```python
def test_cookbook_broken_cross_module_link_fails_validation(tmp_path):
    release_tree = tmp_path / "release-tree"
    cookbook_chunked = release_tree / "cookbook" / validate.config.MODULE_CHUNKED_REF_DIRNAME
    cookbook_chunked.mkdir(parents=True)

    cookbook_chunked.joinpath("my-guide.md").write_text(
        "# My Guide\n\nSee [topic](../../luci-examples/chunked-reference/nonexistent.md).\n",
        encoding="utf-8",
    )
    # target file deliberately absent

    hard_failures, _ = validate.check_release_tree_links(release_tree)
    assert any("my-guide.md" in f for f in hard_failures)
```

---

### Step 5 — Add workflow contract tests for the conditional npm install

**File:** `tests/pytest/pytest_01_workflow_contract_test.py`

Add two tests alongside the existing `test_extract_matrix_fail_fast_is_disabled`:

```python
def test_pandoc_not_installed_in_extract_matrix(workflow_text):
    """
    pandoc is only needed by 02a (extract_wiki job). The extract matrix must not
    install it — doing so wastes ~5 minutes per matrix leg via apt-get mirror sync.
    """
    import yaml
    wf = yaml.safe_load(workflow_text)
    extract_steps = wf.get("jobs", {}).get("extract", {}).get("steps", [])
    for step in extract_steps:
        run_text = step.get("run", "")
        assert "apt-get install" not in run_text or "pandoc" not in run_text, (
            f"extract matrix step '{step.get('name')}' installs pandoc unconditionally; "
            "pandoc is only needed in the extract_wiki job."
        )


def test_jsdoc_npm_install_is_conditional_on_02c(workflow_text):
    """
    jsdoc-to-markdown is only needed by 02c-scrape-jsdoc.py.
    Its npm install step must be gated behind an if: condition referencing that script.
    """
    import yaml
    wf = yaml.safe_load(workflow_text)
    extract_steps = wf.get("jobs", {}).get("extract", {}).get("steps", [])
    npm_steps = [s for s in extract_steps if "jsdoc-to-markdown" in s.get("run", "")]
    assert npm_steps, "No npm install step for jsdoc-to-markdown found in extract job"
    for step in npm_steps:
        condition = step.get("if", "")
        assert "02c-scrape-jsdoc.py" in condition, (
            f"jsdoc-to-markdown install step is not gated on matrix.script == '02c-scrape-jsdoc.py'. "
            f"Got: if: {condition!r}"
        )
```

---

### Step 6 — Update `script-dependency-map.md` with external tool dependencies

**File:** `docs/specs/script-dependency-map.md`

The current table header is:
```
| Script | Phase | Reads | Writes | Depends on | AI data |
```

The `02c` row currently reads:
```
| `02c-scrape-jsdoc.py` | L1 extraction | `WORKDIR/repo-luci/` | `WORKDIR/L1-raw/luci/` | `01` | none |
```

Add an `External tools` column after `Depends on`:

```
| Script | Phase | Reads | Writes | Depends on | External tools | AI data |
```

Update the `02c` row:
```
| `02c-scrape-jsdoc.py` | L1 extraction | `WORKDIR/repo-luci/` | `WORKDIR/L1-raw/luci/` | `01` | `jsdoc-to-markdown` (npm global) | none |
```

Update all other `02b`–`02h` rows to reflect `none` in that column. Update `02a` to note `pandoc` (apt/system). This makes tool dependencies machine-scannable and prevents the hidden-contract pattern from recurring.

---

### Step 7 — Clarify the cookbook authoring spec on regex scope (optional but cheap)

**File:** `docs/specs/cookbook-authoring-spec.md`

The Cross-Link Contract section already documents `../../<module>/chunked-reference/<topic>.md` as the correct format. Add one sentence under that bullet to state that these links are written for the release-tree position and are intentionally not rewritten by the assembly stage:

```markdown
- a reference page in another module uses `../../<module>/chunked-reference/<topic>.md`
  — these are authored for the `release-tree/cookbook/chunked-reference/` position and
  must not use a single `../` prefix. The assembly stage (`05a`) will pass them through
  unchanged. Do not use `../module/file.md` from cookbook chunked pages.
```

This closes the implicit gap between "what the spec says" and "what the regex does".

---

### Step 8 — Verify timing marker is positioned correctly after Step 2

After removing the `pandoc` and unconditional npm steps, confirm that `Mark extractor start` appears as the first step that runs after Python dependency install, and that the extract contract step uses `EXTRACT_STARTED_EPOCH` correctly. The current positioning (timer starts after install) means install time was never counted in contract metrics — this is acceptable. No change needed here unless split timing is specifically wanted (see Deferred section).

---

## Deferred / Optional Work

The following are valid improvements but are not required in this PR and carry more complexity or risk than the items above:

| Item | Why deferred |
|------|-------------|
| Move `EXTRACT_STARTED_EPOCH` before Python pip install for true wall-time measurement | Low-value change to metrics that no consumer currently depends on; risk of confusing existing baseline comparisons |
| Add `needs_jsdoc_to_markdown: true` matrix metadata flag | Useful if a third npm-dependent extractor is added, but over-engineered for a single consumer |
| Extract regex into a shared `link_rewrite.py` lib module | Correct structural improvement, but requires changes to `08` import paths and test infrastructure; net-positive only in a subsequent refactor PR |
| Normalize cookbook `../../` links to `../` at `02i` or `03` stage | Would allow simpler regexes but conflicts with the authoring spec's explicit statement that links are authored for the release-tree position; requires spec decision first |
| Machine-readable extractor tool manifest consumed by workflow, docs, and tests | Best long-term solution; requires designing the manifest schema and plumbing it through three systems; not justified for two current tool dependencies |

---

## Not Recommended

- Renaming pipeline stages or script filenames.
- Redesigning the layer model.
- Adding external URL checking or network-dependent validation.
- Rewriting all cookbook authored content (the regex fix makes the existing content correct without edits).
- Changing the `08` broken-link validator's resolution logic (it is correct; the bug is in `05a`'s transform, not `08`'s check).

---

## Implementation Targets by Step

| Step | Files touched |
|------|--------------|
| 1 | `.github/scripts/openwrt-docs4ai-05a-assemble-references.py` (3 regex lines) |
| 2 | `.github/workflows/openwrt-docs4ai-00-pipeline.yml` (1 step split into 2) |
| 3 | `tests/pytest/pytest_00_pipeline_units_test.py` (new test class) |
| 4 | `tests/pytest/pytest_09_release_tree_contract_test.py` (2 new tests) |
| 5 | `tests/pytest/pytest_01_workflow_contract_test.py` (2 new tests) |
| 6 | `docs/specs/script-dependency-map.md` (table column + 8 row updates) |
| 7 | `docs/specs/cookbook-authoring-spec.md` (1 sentence added) |

---

## Verification Checklist

**Before opening PR:**

- [ ] Run `python tests/run_pytest.py` locally — all existing tests pass.
- [ ] Run `python tests/check_linting.py` — Ruff and Pyright clean.
- [ ] Inspect the three changed regex lines manually with a test input of `../../luci-examples/chunked-reference/topic.md` to confirm no match.
- [ ] Confirm the workflow YAML is valid: `python -c "import yaml; yaml.safe_load(open('.github/workflows/openwrt-docs4ai-00-pipeline.yml'))"`.

**After CI run:**

- [ ] `extract` matrix legs `02b`, `02d`, `02e`, `02f`, `02g`, `02h` complete in under 60 seconds (previously ~5 minutes).
- [ ] `[08]` validation passes with zero broken-link failures for cookbook module.
- [ ] New tests in `pytest_00`, `pytest_01`, `pytest_09` pass.
- [ ] Pipeline summary artifact reflects correct duration for all matrix legs.

---

## Adoption Ordering

Steps 1 and 2 are independent and can be implemented in either order or in parallel. Steps 3–5 (tests) can be written before or after the production changes — writing them first (TDD order) is preferred to confirm they fail against the current code, then pass after the fix. Steps 6–7 (docs) can be committed last in the same PR.

There are no cross-step dependencies except that Step 4 tests the output of Step 1's fix at the integration level, so Step 1 must be applied before those tests are expected to pass.
