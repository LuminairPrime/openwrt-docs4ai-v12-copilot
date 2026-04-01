# Ruff & Testing Upgrade Plan — v03

**Document Status:** Implementation-ready.
**Date:** 2026-04-01
**Supersedes:** `ruff-testing-upgrade-plan-{00,01,02}.md` (earlier drafts with varying project awareness; retained for history).

**Target Environment:** Windows development workstations / GitHub Actions CI (ubuntu-latest)
**Core Technologies:** Python 3.12, Ruff, Pyright, Pytest, pre-commit, GitHub Actions

---

## 1. Problem Statement

An agent introduced non-conforming syntax (bad tabs) that broke the primary data pipeline mid-execution. The defect was undetected because **no mechanism enforces code quality before commit or before CI pipeline execution.** The project's test infrastructure (`tests/check_linting.py`, `tests/run_pytest.py`, smoke suites) is well-built but advisory-only — nothing runs it automatically.

### Specific Gaps

| Gap | Impact |
|-----|--------|
| **No CI validation gate.** The 1360-line data pipeline workflow (`openwrt-docs4ai-00-pipeline.yml`) runs multi-minute clone/extraction jobs before any code quality check. Bad code wastes compute and breaks downstream stages. | High — directly caused the motivating incident. |
| **No Ruff configuration file.** `check_linting.py` calls `ruff check .github/scripts lib tests`, but no `ruff.toml` or `pyproject.toml` defines rules, exclusions, or target version. Behavior depends entirely on Ruff's defaults, which drift across releases. | Medium — silent behavior changes on tool update. |
| **No `ruff format` enforcement.** Only `ruff check` (linting) is wired into `check_linting.py`. Formatting is unenforced — whitespace/indentation errors (like the bad tabs incident) pass undetected. | High — directly enabled the motivating incident. |
| **No pre-commit hooks.** Agents and developers can commit code that fails Ruff, Pyright, or syntax checks with no local warning. | Medium — CI gate catches it, but wastes a round-trip. |
| **Python version mismatch.** `pyrightconfig.strict.json` targets `"pythonVersion": "3.11"`. CI uses Python 3.12. CLAUDE.md references 3.12. Pyright can report false positives or miss 3.12-specific type issues. | Low-medium — silent type-checking inaccuracy. |

### What Already Works

The project is not starting from zero. These tools are already operational and well-integrated:

- **`tests/check_linting.py`** — orchestrates Ruff check + Pyright strict + Actionlint, writes `summary.json` for forensic analysis
- **`tests/run_pytest.py`** — focused pytest suites under `tests/pytest/`
- **`tests/run_smoke.py`** — full-pipeline structural validation
- **`tests/run_smoke_and_pytest.py`** / `run_smoke_and_pytest_parallel.py` — combined runners
- **`pyrightconfig.strict.json`** — strict type checking on a curated file subset (8 files)
- **`pytest_06_warning_regression_test.py`** — enforces `@main` pinning policy on GitHub Actions refs

This plan adds the missing enforcement layer without replacing anything that works.

---

## 2. Architecture: Two-Phase Rollout

Previous plan drafts described a 7-phase sequence. In practice, there are only two meaningful phases, ordered by which failure mode they block:

### Phase A — CI Validation Gate (blocks regressions from reaching production)

This is the single highest-value change. An agent committed bad tabs. The agent does not run pre-commit hooks. Only a CI gate would have caught it. **Start here.**

Creates a new lightweight GitHub Actions workflow (`ci-validation.yml`) that runs on every push and PR to `main`. Two jobs:

1. **Lint job** — `ruff format --check`, `ruff check --output-format=github`, `pyright --project pyrightconfig.strict.json`. Completes in under 60 seconds.
2. **Test job** (depends on lint) — `python tests/run_pytest.py`. Runs only if lint passes. Fail-fast principle: don't spend compute on tests when formatting is broken.

The data pipeline workflow (`openwrt-docs4ai-00-pipeline.yml`) is untouched. The CI validation gate is a separate, independent check.

### Phase B — Local Ergonomics (prevents bad commits from ever being pushed)

Adds `ruff.toml`, fixes the pyrightconfig version, creates `.pre-commit-config.yaml`, baselines the codebase with a formatting commit, and updates check_linting.py to include format enforcement.

This phase makes development faster but is not the primary safety mechanism. The CI gate from Phase A catches anything that slips through.

---

## 3. Design Decisions

### 3.1 `ruff.toml`, not `pyproject.toml`

The project uses standalone config files (`pyrightconfig.strict.json`). A `ruff.toml` is consistent with this pattern. There is no existing `pyproject.toml` and introducing one solely for a `[tool.ruff]` section is unnecessary complexity.

### 3.2 Separate `ci-validation.yml`, not injected into the data pipeline

The data pipeline is 1360 lines, runs multi-minute jobs, and has its own trigger matrix (schedule, push to main, manual dispatch). Injecting a lint gate into it creates coupling, complicates the workflow YAML, and delays the pipeline's primary function. A separate 50-line workflow provides an independent, fast PR gate.

### 3.3 `ruff-pre-commit` for Tier 2, not `check_linting.py`

The `ruff-pre-commit` hook is self-contained — it installs its own Ruff binary and doesn't depend on the developer's PATH or Python environment. Calling `python tests/check_linting.py` from pre-commit would require Ruff, Pyright, **and** actionlint all on PATH, which is fragile on Windows. The pre-commit hook handles the fast Ruff gate; `check_linting.py` remains the manual full-validation command.

### 3.4 `@main` action refs

The project intentionally uses `@main` for all GitHub Actions action refs. This is enforced by `pytest_06_warning_regression_test.py` — the test asserts `@main` presence and rejects pinned version tags. The new `ci-validation.yml` follows the same policy for consistency. This plan does not change the pinning policy.

### 3.5 Runtime vs. dev dependencies

`.github/scripts/requirements.txt` contains **runtime pipeline dependencies** (`requests`, `tiktoken`, `pyyaml`, `lxml`, `beautifulsoup4`, `html5lib`, `markdownify`). Ruff and Pyright are dev/lint tools. They are installed explicitly in the CI workflow via `pip install ruff pyright`, not added to the runtime requirements file. No `requirements-dev.txt` is created — the CI workflow is the canonical source for lint tool installation.

### 3.6 `check_linting.py` update scope

The existing `check_linting.py` runs `ruff check` but not `ruff format --check`. After this plan, it will run both. This means the local `python tests/check_linting.py` command catches both lint violations and formatting drift, matching what CI enforces.

### 3.7 Expanded Ruff rule set

The existing `check_linting.py` runs Ruff with default rules (equivalent to `F` and `E` subset). This plan enables an expanded set with rationale:

| Rule Set | Purpose | Why |
|----------|---------|-----|
| `F` (Pyflakes) | Undefined names, unused imports, syntax errors | Core safety net — catches the most damaging errors |
| `E` (pycodestyle errors) | Style errors (indentation, whitespace) | Would have caught the bad-tabs incident |
| `W` (pycodestyle warnings) | Style warnings | Low noise, high signal |
| `I` (isort) | Import ordering | Prevents merge conflicts from import reordering |
| `UP` (pyupgrade) | Python 2→3 migration leftovers, old-style type hints | Free modernization on every commit |
| `B` (flake8-bugbear) | Common logic errors (bare except, mutable default args) | Catches real bugs, not style nits |
| `SIM` (flake8-simplify) | Unnecessary complexity (nested ifs, redundant bool comparisons) | Keeps code readable |

Rules are defined in `ruff.toml` so all three tiers (IDE, pre-commit, CI) enforce the identical set.

---

## 4. Implementation: Phase A — CI Validation Gate

### Step A1: Create `ruff.toml`

Create at the repository root:

```toml
# Ruff configuration — shared by IDE, pre-commit hooks, and CI.
# Docs: https://docs.astral.sh/ruff/settings/

line-length = 120
target-version = "py312"

exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "tmp",
    "data",
    "static/data",
    "static/release-inputs",
    "node_modules",
]

[lint]
select = ["F", "E", "W", "I", "UP", "B", "SIM"]
ignore = []

[format]
docstring-code-format = true
```

**`line-length = 120`:** The existing codebase uses lines wider than 88. Setting 120 avoids mass reformatting while still enforcing a boundary.

**`target-version = "py312"`:** Matches CI Python version and CLAUDE.md.

**`exclude` is top-level** (not under `[lint]`): controls whether files are processed at all by both linting and formatting. Ruff never touches `tmp/`, generated data, or vendored content.

### Step A2: Align Pyright Python version

Edit `pyrightconfig.strict.json` — change one line:

```diff
-  "pythonVersion": "3.11"
+  "pythonVersion": "3.12"
```

The strict file subset and `typeCheckingMode` are unchanged. This eliminates the mismatch between Ruff's target, Pyright's target, and CI's runtime.

### Step A3: Create `ci-validation.yml`

Create `.github/workflows/ci-validation.yml`:

```yaml
name: CI Validation

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@main
      - uses: actions/setup-python@main
        with:
          python-version: "3.12"
          cache: pip

      - name: Install pipeline dependencies
        run: pip install -r .github/scripts/requirements.txt

      - name: Install lint tools
        run: pip install ruff pyright

      - name: Ruff format check
        run: ruff format --check .

      - name: Ruff lint
        run: ruff check --output-format=github .

      - name: Pyright strict subset
        run: pyright --project pyrightconfig.strict.json

  test:
    name: Pytest Suites
    runs-on: ubuntu-latest
    timeout-minutes: 15
    needs: lint
    steps:
      - uses: actions/checkout@main
      - uses: actions/setup-python@main
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r .github/scripts/requirements.txt pytest

      - name: Run focused pytest
        run: python tests/run_pytest.py

      - name: Upload test artifacts
        if: always()
        uses: actions/upload-artifact@main
        with:
          name: ci-validation-artifacts
          path: tmp/ci/
          retention-days: 7
```

**Key design choices:**

- **Separate lint and test jobs.** GitHub shows these as distinct PR checks. A developer can see immediately whether the failure is a lint issue or a test issue.
- **`needs: lint`** on the test job. Fail-fast: don't spend compute on tests when formatting is broken.
- **`--output-format=github`** on Ruff. Produces inline PR annotations on the exact lines with violations.
- **`@main` action refs.** Consistent with project policy enforced by `pytest_06_warning_regression_test.py`.
- **Pipeline deps installed before lint tools.** Pyright needs the same packages importable that the source code imports. Installing runtime deps first ensures import resolution works.
- **Test artifacts uploaded on failure.** The `tmp/ci/` bundle is uploaded for forensic analysis, matching the local runner pattern.
- **No actionlint step in CI.** Actionlint validates workflow YAML — it's most valuable locally to catch edits before push. Adding it to CI would require either installing a Go binary or a pip wrapper. The existing `check_linting.py` handles actionlint locally; CI focuses on the two tools that directly catch the motivating failure mode (bad code, not bad YAML).

### Step A4: Extend workflow contract test

Update `tests/pytest/pytest_06_warning_regression_test.py` to cover the new workflow. Add a new test function:

```python
def test_ci_validation_workflow_uses_main_refs() -> None:
    ci_val_path = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci-validation.yml"
    assert ci_val_path.exists(), "ci-validation.yml must exist"
    ci_val_text = ci_val_path.read_text(encoding="utf-8")

    expected_refs = [
        "actions/checkout@main",
        "actions/setup-python@main",
        "actions/upload-artifact@main",
    ]
    for ref in expected_refs:
        assert ref in ci_val_text, f"Expected {ref} in ci-validation.yml"

    # Verify fail-fast dependency: test job depends on lint job
    assert "needs: lint" in ci_val_text or "needs: [lint]" in ci_val_text
```

This ensures the new workflow stays consistent with the project's `@main` pinning policy and preserves the lint→test dependency.

### Step A5: Verify Phase A

Run in order (stop on first failure):

```powershell
# 1. Ruff config is valid
ruff check --config ruff.toml .
ruff format --check --config ruff.toml .

# 2. Pyright still passes on the strict subset
pyright --project pyrightconfig.strict.json

# 3. Existing tests still pass
python tests/run_pytest.py

# 4. New contract test passes
python -m pytest tests/pytest/pytest_06_warning_regression_test.py -q

# 5. Local lint runner still works
python tests/check_linting.py
```

At this point the CI gate is live. Every push and PR to `main` will be validated before the data pipeline runs. **Phase A alone blocks the motivating failure mode.** Phase B is an improvement, not a prerequisite.

---

## 5. Implementation: Phase B — Local Ergonomics

Phase B depends on Phase A being complete and green. These steps can be done in a single session.

### Step B1: Baseline format commit

Apply Ruff auto-fix and formatting to the entire codebase in a single isolated commit. This produces a large diff that is purely mechanical — no logic changes.

```powershell
# Auto-fix safe violations (unused imports, old-style syntax)
ruff check --fix .

# Format all code
ruff format .

# Verify nothing broke
python tests/run_pytest.py
python tests/check_linting.py

# Commit
git add .
git commit -m "chore: baseline codebase with ruff formatting and auto-fix"
```

**Critical: run tests BEFORE committing.** If `ruff check --fix` removes an import that Pyright's strict subset considers necessary, or if formatting changes break a string comparison in a test, fix it manually before committing.

**Risk mitigation:** If the baseline diff is large and hard to review, split into two commits:
1. `ruff check --fix .` — logic-adjacent changes (removing unused imports, upgrading syntax)
2. `ruff format .` — whitespace-only changes

Both go into `.git-blame-ignore-revs`.

### Step B2: Create `.git-blame-ignore-revs`

After the baseline commit(s), record the hash(es) so `git blame` stays useful:

```powershell
$hash = git rev-parse HEAD
"# Ruff baseline formatting commit`n$hash" | Out-File -Encoding utf8 .git-blame-ignore-revs
git add .git-blame-ignore-revs
git commit -m "chore: add baseline formatting commit to blame-ignore-revs"

# Configure local Git to use the file
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

GitHub automatically reads `.git-blame-ignore-revs` from the repository root for the web blame view. No additional configuration needed.

### Step B3: Update `check_linting.py` to include `ruff format --check`

The existing `check_linting.py` runs three checks: `ruff check`, `pyright`, `actionlint`. After this step, it runs four checks by adding `ruff format --check` as check index 0 (before `ruff check`).

In `tests/check_linting.py`, update the `checks` list:

```python
checks = [
    (0, "ruff-format", _resolve_tool_command("ruff", "ruff"), ["format", "--check", ".github/scripts", "lib", "tests", "tools"]),
    (1, "ruff", _resolve_tool_command("ruff", "ruff"), ["check", ".github/scripts", "lib", "tests", "tools"]),
    (2, "pyright", _resolve_tool_command("pyright", "pyright"), ["--project", "pyrightconfig.strict.json"]),
    (3, "actionlint", _resolve_tool_command("actionlint"), [".github/workflows/openwrt-docs4ai-00-pipeline.yml"]),
]
```

**Why add `tools` to the target paths:** The `tools/` directory contains maintainer scripts (`manage_ai_store.py`, `sync_tree.py`) that are authored Python but were not covered by the existing `ruff check` invocation. Match the scope of what CI validates.

**Why also pass targets to `ruff format --check`:** Without explicit targets, `ruff format --check .` would check the entire repo including directories that should be excluded. While `ruff.toml` has an `exclude` list, being explicit in the command matches the existing `ruff check` invocation pattern and prevents surprises.

### Step B4: Create `.pre-commit-config.yaml`

Create at the repository root:

```yaml
default_stages: [pre-commit]

repos:
  # File hygiene — catches trailing whitespace, bad YAML, merge conflict markers
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict

  # Ruff linter and formatter — self-contained, no PATH dependency
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Pinned revs:** Both repos are pinned to exact stable release tags. Run `pre-commit autoupdate` quarterly or after major Ruff releases. The CI gate (`ci-validation.yml`) is the immutable safety net; if a pre-commit update introduces a new rule violation, the developer can bypass locally with `git commit --no-verify` while fixing, and CI will still catch the actual violation.

**Why `ruff-pre-commit` and not calling `check_linting.py`:** The `ruff-pre-commit` hook downloads its own Ruff binary per platform. It works on Windows, macOS, and Linux without requiring Ruff, Pyright, or actionlint on PATH. This is critical for agent environments and fresh developer setups where PATH is unpredictable.

Install the hooks:

```powershell
pip install pre-commit
pre-commit install
```

**Windows note:** If PowerShell execution policies block hook scripts, run:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Step B5: Verify Phase B

```powershell
# 1. Pre-commit runs cleanly on all files
pre-commit run --all-files

# 2. check_linting.py passes with the new format check
python tests/check_linting.py

# 3. Full local validation
python tests/run_smoke_and_pytest.py

# 4. Workflow contract test still passes
python -m pytest tests/pytest/pytest_06_warning_regression_test.py -q
```

---

## 6. Relationship Between Tools After Implementation

After both phases, the project has a three-tier enforcement architecture. Each tier uses the same `ruff.toml` configuration, so violations found anywhere are reproducible everywhere.

| Tier | Mechanism | Scope | Speed | Failure Behavior |
|------|-----------|-------|-------|-----------------|
| **Tier 1: IDE** | VSCode/Cursor Ruff + Pyright extensions, format-on-save enabled | Single file, real-time | Instant | Visual warning only |
| **Tier 2: Pre-commit hooks** | `pre-commit` framework running `ruff-pre-commit` hooks | Staged files at commit time | < 5 seconds | Commit blocked (bypass: `--no-verify`) |
| **Tier 3: CI Pipeline** | `ci-validation.yml` — `ruff format --check`, `ruff check`, `pyright`, then pytest | Full repo at push/PR time | < 90 seconds | PR merge blocked |

**`check_linting.py` role:** Remains the manual full-validation command. Runs Ruff check + Ruff format check + Pyright + Actionlint. Agents and developers invoke it via `python tests/check_linting.py` when they want comprehensive local validation. It is NOT wired into pre-commit (too many PATH dependencies) and NOT called from CI (CI runs the tools directly for better GitHub annotations and job separation).

**Data pipeline workflow role:** `openwrt-docs4ai-00-pipeline.yml` is unchanged. It continues to run on push-to-main, schedule, and manual dispatch. The new `ci-validation.yml` is a separate, independent workflow that provides the quality gate. Both trigger on push to `main`, but `ci-validation.yml` completes in under 90 seconds while the data pipeline runs for 15+ minutes. A formatting or lint failure in `ci-validation.yml` does not block the data pipeline (they are independent workflows), but seeing a red check on the same commit provides immediate signal.

---

## 7. Documentation Updates

### 7.1 CLAUDE.md

Add to **Prerequisites** section, after the existing `pip install` line:

```
pip install pre-commit
pre-commit install
```

Add to **Key Conventions** section:

```
- **Pre-commit hooks:** Ruff linter/formatter and file hygiene hooks run on every `git commit`. Bypass with `git commit --no-verify` only for emergencies.
- **CI validation gate:** `ci-validation.yml` runs lint + pytest on every push/PR to main. The data pipeline (`openwrt-docs4ai-00-pipeline.yml`) is a separate workflow with its own trigger schedule.
- **Ruff configuration:** `ruff.toml` at the repository root. All three tiers (IDE, pre-commit, CI) read the same config. Do not duplicate rule settings elsewhere.
```

### 7.2 DEVELOPMENT.md

Update prerequisites to include `pre-commit` and `ruff`. Add to the recommended local commands section:

```
pre-commit run --all-files      # Run all pre-commit hooks (format + lint)
```

### 7.3 tests/README.md

Add `ruff.toml` to the configuration references. Note that `check_linting.py` now includes a `ruff format --check` step in addition to the existing `ruff check`. Document the new `ci-validation.yml` workflow as the CI counterpart to `check_linting.py`.

---

## 8. Deferred Items (Not in Scope)

These are explicitly deferred, not forgotten:

| Item | Why deferred |
|------|-------------|
| **Smoke tests in CI.** The smoke suite (`smoke_00`, `smoke_01`, `smoke_02`) exercises the full pipeline and requires network access + upstream repo clones. Running them on every PR would be slow and flaky. They remain a local-first validation surface. | Separate decision with different cost/benefit profile. |
| **Test coverage reporting.** No `pytest-cov` integration. | Orthogonal to "catch syntax/format errors before pipeline execution." |
| **GitHub Actions SHA pinning.** The `@main` policy is intentional and test-enforced. | Changing it requires updating `pytest_06`, both workflows, and possibly adding Dependabot/Renovate. Separate decision. |
| **Expanding the Pyright strict subset.** Currently 8 files. | Driven by typing coverage goals, not by this incident. **Guidance for growth:** when adding new modules to `lib/`, add them to `pyrightconfig.strict.json` `include`. Existing untyped files are grandfathered until a dedicated typing sprint. |
| **`ruff format` in CI for the data pipeline workflow.** `ci-validation.yml` catches the code; `openwrt-docs4ai-00-pipeline.yml` doesn't need its own lint step. | Adding lint to the data pipeline would delay it without adding safety beyond what `ci-validation.yml` already provides. |
| **Actionlint in CI.** Actionlint validates workflow YAML. Installing it in CI requires a Go binary or a pip wrapper. | `check_linting.py` handles it locally. Low incident risk — bad YAML fails immediately with a clear GitHub error. |

---

## 9. Rollback Plan

| Failure | Recovery |
|---------|----------|
| **Ruff auto-fix introduced a bug in baseline commit** | `git revert <baseline-hash>`, fix the specific file manually, re-run `ruff format` on the fixed file only, commit. |
| **Pre-commit hooks block a legitimate commit** | `git commit --no-verify` to bypass. Fix the hook config or the file. The CI gate catches the actual violation regardless. Pre-commit is a convenience, not a security boundary. |
| **CI validation workflow is too strict on an existing pattern** | Add the problematic rule to `ruff.toml` `ignore = [...]`. Fix iteratively, not all at once. |
| **Pyright fails on strict subset after Python 3.12 upgrade** | Revert `pyrightconfig.strict.json` to `"pythonVersion": "3.11"`. Investigate the specific stub incompatibility before re-attempting. |
| **CI workflow itself has a syntax error** | GitHub rejects the YAML immediately with a clear error. Fix the YAML. The data pipeline workflow is unaffected (separate file). |
| **`check_linting.py` changes break the summary.json API** | The `summary.json` schema is additive — the new `ruff-format` check adds a new entry to the `results` array. Existing consumers that iterate the array are unaffected. Consumers that index by position need updating (change from 3 entries to 4). |

---

## 10. File Inventory

All files created or modified by this plan:

| File | Action | Phase |
|------|--------|-------|
| `ruff.toml` | **Create** | A1 |
| `pyrightconfig.strict.json` | **Modify** — `pythonVersion` 3.11 → 3.12 | A2 |
| `.github/workflows/ci-validation.yml` | **Create** | A3 |
| `tests/pytest/pytest_06_warning_regression_test.py` | **Modify** — add new test function | A4 |
| `.github/scripts` + `lib` + `tests` + `tools` (all `.py`) | **Modified by Ruff** — formatting + auto-fix | B1 |
| `.git-blame-ignore-revs` | **Create** | B2 |
| `tests/check_linting.py` | **Modify** — add `ruff format --check` step, add `tools` to target paths | B3 |
| `.pre-commit-config.yaml` | **Create** | B4 |
| `CLAUDE.md` | **Modify** — prerequisites + conventions | B (docs) |
| `DEVELOPMENT.md` | **Modify** — prerequisites + commands | B (docs) |
| `tests/README.md` | **Modify** — add ruff.toml reference | B (docs) |

---

## 11. Execution Checklist

Print this and check off each item during implementation:

### Phase A — CI Gate

- [ ] Create `ruff.toml` (Step A1)
- [ ] Update `pyrightconfig.strict.json` pythonVersion to 3.12 (Step A2)
- [ ] Create `.github/workflows/ci-validation.yml` (Step A3)
- [ ] Add `test_ci_validation_workflow_uses_main_refs` to `pytest_06` (Step A4)
- [ ] Run Phase A verification (Step A5)
- [ ] Commit Phase A: `feat: add CI validation gate with ruff, pyright, and pytest`
- [ ] Push and confirm CI validation workflow runs green

### Phase B — Local Ergonomics

- [ ] Run `ruff check --fix .` (Step B1)
- [ ] Run `ruff format .` (Step B1)
- [ ] Run `python tests/run_pytest.py` — verify green before committing (Step B1)
- [ ] Run `python tests/check_linting.py` — verify green before committing (Step B1)
- [ ] Commit baseline: `chore: baseline codebase with ruff formatting and auto-fix`
- [ ] Create `.git-blame-ignore-revs` with baseline hash (Step B2)
- [ ] Run `git config blame.ignoreRevsFile .git-blame-ignore-revs` (Step B2)
- [ ] Update `check_linting.py` — add `ruff format --check` and `tools` path (Step B3)
- [ ] Create `.pre-commit-config.yaml` (Step B4)
- [ ] Run `pip install pre-commit && pre-commit install` (Step B4)
- [ ] Run Phase B verification (Step B5)
- [ ] Commit Phase B: `chore: add pre-commit hooks, update check_linting, blame-ignore-revs`
- [ ] Update CLAUDE.md, DEVELOPMENT.md, tests/README.md
- [ ] Commit docs: `docs: document CI validation gate and pre-commit hooks`
- [ ] Push and confirm CI validation workflow runs green
