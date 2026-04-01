# Ruff & Testing Upgrade Plan — v02

**Document Status:** Implementation-ready plan.
**Target Environment:** Windows Development Workstations / GitHub Actions CI
**Core Technologies:** Python 3.12, Ruff, Pyright, Pytest, pre-commit, GitHub Actions
**Motivating Incident:** An agent introduced non-conforming syntax (bad tabs) that broke the primary data pipeline mid-execution. The defect was undetected because no pre-validation gate exists between code modification and pipeline execution.

---

## 1. Problem Statement

The project has strong test infrastructure (`tests/check_linting.py`, `tests/run_smoke_and_pytest.py`, `tests/run_pytest.py`) and a validated Pyright strict subset (`pyrightconfig.strict.json`), but these tools are advisory-only. No mechanism enforces them before commit or before CI pipeline execution. The result:

- **No pre-commit gate.** Agents and developers can commit code that fails Ruff, Pyright, or syntax checks.
- **No CI validation gate.** The 1360-line data pipeline workflow (`openwrt-docs4ai-00-pipeline.yml`) runs multi-minute clone and extraction jobs before any code quality check. Bad code wastes compute.
- **No Ruff configuration file.** `check_linting.py` calls `ruff check .github/scripts lib tests`, but there is no `ruff.toml` or `pyproject.toml` to define rules, exclusions, or target version. The behavior depends entirely on Ruff defaults, which may drift.
- **Python version mismatch.** `pyrightconfig.strict.json` targets Python 3.11. CI and CLAUDE.md reference Python 3.12.
- **Unpinned GitHub Actions.** All 39 `uses:` references in the main workflow point to `@main`. This is an *intentional project policy* enforced by `pytest_06_warning_regression_test.py` (the project switched to `@main` to pick up Node 24 runtimes without waiting for stable tags). This plan does not change that policy but documents the tradeoff.

---

## 2. Architecture: The 3-Tier Gatekeeper System

Code quality is enforced at three escalating levels. Each tier uses the same configuration so violations found at any tier are reproducible.

| Tier | Mechanism | Scope | Failure Behavior |
|------|-----------|-------|-----------------|
| **Tier 1: IDE** | VSCode/Cursor Ruff + Pyright extensions, format-on-save | Single file, real-time | Visual warning only |
| **Tier 2: Local Git Hooks** | `pre-commit` framework running Ruff | Staged files at commit time | Commit blocked |
| **Tier 3: CI Pipeline** | Dedicated `ci-validation.yml` workflow | Full repo at PR/push time | PR merge blocked |

### Design Decisions

1. **`ruff.toml` over `pyproject.toml`.** The project uses standalone config files (`pyrightconfig.strict.json`). A `ruff.toml` is consistent with this pattern and avoids introducing a `pyproject.toml` for a single tool section. Ruff reads `ruff.toml` natively.

2. **Separate `ci-validation.yml` workflow.** Validation must not be injected into the 1360-line data pipeline. A dedicated workflow completes in under 60 seconds and provides an independent PR gate. The data pipeline retains its own triggers (schedule, push to main, manual dispatch).

3. **`ruff-pre-commit` hook for Tier 2, not `check_linting.py`.** The `ruff-pre-commit` hook is self-contained — it installs its own Ruff binary and doesn't depend on the developer's PATH or Python environment. Calling `python tests/check_linting.py` from pre-commit would require Ruff, Pyright, and actionlint all on PATH, which is fragile on Windows. The pre-commit hook handles the fast Ruff gate; `check_linting.py` remains the local full-validation runner invoked manually or from the combined runner scripts.

4. **Pinned pre-commit hooks, unpinned CI actions.** Pre-commit hooks are pinned to exact version tags (upstream can release new rules that break the local workflow). CI actions remain on `@main` per existing project policy — the test suite enforces this.

---

## 3. Implementation Plan

### Phase 1: Create Ruff Configuration

Create `ruff.toml` at the repository root:

```toml
line-length = 120
target-version = "py312"

exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "tmp",
    "data",
    "openwrt-condensed-docs-renamed",
    "static/release-inputs",
    "node_modules",
]

[lint]
select = ["F", "E", "W", "I", "UP", "B", "SIM"]
ignore = []

[format]
docstring-code-format = true
```

**Rationale for rule selection:**

| Rule Set | Purpose |
|----------|---------|
| `F` (Pyflakes) | Undefined names, unused imports, syntax errors |
| `E` (pycodestyle errors) | Style errors |
| `W` (pycodestyle warnings) | Style warnings |
| `I` (isort) | Import ordering |
| `UP` (pyupgrade) | Python 2 → 3 migration leftovers, old-style type hints |
| `B` (flake8-bugbear) | Common logic errors (bare except, mutable default args, loop variable leaks) |
| `SIM` (flake8-simplify) | Unnecessary complexity (nested ifs, redundant bool comparisons) |

**Rationale for exclusions:**

- `tmp/` — Ephemeral pipeline output, never committed.
- `openwrt-condensed-docs-renamed/` — Generated content, not authored code.
- `data/` — Pipeline data artifacts.
- `static/release-inputs/` — External input files.
- `node_modules/` — npm dependencies.

**Rationale for `line-length = 120`:** The existing codebase uses lines wider than 88. Setting 120 avoids thousands of E501 reformatting on an existing project while still enforcing a boundary.

**Rationale for `target-version = "py312"`:** Matches the CI Python version and CLAUDE.md. Update `pyrightconfig.strict.json` to align (see Phase 1b).

**`exclude` is top-level, not under `[lint]`.** Ruff's `exclude` controls whether files are processed at all (both linting and formatting). Placing it under `[lint]` would leave `ruff format` processing excluded directories.

### Phase 1b: Align Pyright Python Version

Update `pyrightconfig.strict.json` to set `"pythonVersion": "3.12"`. This removes the mismatch between Ruff and Pyright. The strict file subset and `typeCheckingMode` remain unchanged.

### Phase 2: Baseline Commit

Apply Ruff auto-fix and formatting to the entire codebase in a single isolated commit:

```powershell
# Install ruff (will be added to .github/scripts/requirements.txt in Phase 5)
pip install ruff

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

**After committing, record the hash in `.git-blame-ignore-revs`:**

```powershell
$CommitHash = git rev-parse HEAD
echo $CommitHash >> .git-blame-ignore-revs
git add .git-blame-ignore-revs
git commit -m "chore: add baseline formatting commit to blame-ignore-revs"
```

**Configure local Git to use the file:**

```powershell
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

**Critical:** Run `python tests/run_pytest.py` and `python tests/check_linting.py` after formatting but **before** committing. If Ruff's auto-fix introduces a Pyright failure in the strict subset, fix it manually before committing.

**Risk mitigation:** If the baseline commit produces a large diff that is hard to review, split it into two commits: one for `ruff check --fix` (logic-adjacent changes like removing unused imports) and one for `ruff format` (whitespace-only changes). Both go into `.git-blame-ignore-revs`.

### Phase 3: Pre-Commit Hooks

Create `.pre-commit-config.yaml` at the repository root:

```yaml
default_stages: [commit]

repos:
  # File hygiene — catches trailing whitespace, missing EOF newlines, merge conflict markers
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict

  # Ruff linter and formatter — pinned to stable release
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.7
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Install:**

```powershell
pip install pre-commit
pre-commit install
```

**Version update cadence:** Run `pre-commit autoupdate` quarterly or after major Ruff releases. Pin to exact tags; never use `@latest`.

**Windows considerations:** `pre-commit` can be slow on first run on Windows (it creates isolated environments per hook). Subsequent runs use cached environments. If PowerShell execution policies block hook scripts, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

### Phase 4: CI Validation Workflow

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

      - name: Install dependencies
        run: |
          pip install -r .github/scripts/requirements.txt
          pip install ruff pyright

      - name: Ruff format check
        run: ruff format --check .

      - name: Ruff lint
        run: ruff check --output-format=github .

      - name: Pyright strict
        run: pyright --project pyrightconfig.strict.json

      - name: Actionlint
        run: |
          pip install actionlint
          actionlint .github/workflows/openwrt-docs4ai-00-pipeline.yml

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

1. **Lint job runs before test job (`needs: lint`).** Fails fast on syntax/format before spending compute on tests. This is the core fail-fast principle.

2. **`--output-format=github` on Ruff.** Produces inline PR annotations on the exact lines with violations, drastically improving developer experience.

3. **Separate lint and test jobs.** GitHub Actions shows these as distinct checks. A developer can see immediately whether the failure is a lint issue or a test issue.

4. **`@main` action refs.** Consistent with existing project policy. The new `ci-validation.yml` workflow uses the same refs as the main data pipeline so `pytest_06_warning_regression_test.py` can be extended to cover it.

5. **Test artifacts uploaded on failure.** The `tmp/ci/` bundle is uploaded for forensic analysis, matching the local runner pattern.

6. **Actionlint checked.** The existing `check_linting.py` validates workflow YAML. This CI step ensures workflow syntax stays valid.

### Phase 4b: Extend Workflow Contract Test

Add `ci-validation.yml` to the workflow contract test coverage in `pytest_06_warning_regression_test.py`. The test should verify that the new workflow:

- Uses `@main` for all action refs (consistent with project policy).
- Does not contain any pinned version tags like `@v4` or `@v5`.
- Runs lint before test (`needs: lint` dependency exists).

### Phase 5: Dependency Updates

**`.github/scripts/requirements.txt`** — add `ruff` and `pyright`:

```
requests
tiktoken
pyyaml
lxml
beautifulsoup4
html5lib
markdownify
ruff
pyright
```

These are development dependencies. They don't need pinning to exact versions — Ruff's `ruff.toml` and Pyright's `pyrightconfig.strict.json` control behavior; the installed versions just need to be recent enough to support the config.

### Phase 6: GitHub Actions Pinning — Policy Assessment

The current project intentionally uses `@main` for all action refs. This is enforced by `pytest_06_warning_regression_test.py` at `tests/pytest/pytest_06_warning_regression_test.py:11-46`. The test explicitly:

- Asserts that `@main` refs are present for `checkout`, `setup-python`, `cache`, `upload-artifact`, `download-artifact`, and `create-github-app-token`.
- Asserts that pinned versions (`@v4`, `@v5`, `@v6`, etc.) are **not** present.

**This plan does not change this policy.** The reasons:

1. The project made a deliberate tradeoff: faster access to Node 24 runtime updates at the cost of supply-chain exposure to HEAD-of-default-branch changes.
2. `actions/create-github-app-token` has no stable release — only `@main` or `v3.0.0-beta.5`. Pinning it requires using a beta tag, which is worse than `@main`.
3. Changing the policy requires updating the test, the workflow, and the new `ci-validation.yml` — a coordinated change that should be a separate decision.

**What this plan does instead:**

- The new `ci-validation.yml` uses `@main` for consistency.
- If the team decides to pin in the future, the mechanical change is straightforward: update the workflow, update the test's `expected_refs` and `removed_pinned_versions` lists, and optionally add Dependabot or Renovate to keep SHA pins current.
- The `@main` risk is mitigated by the fact that GitHub Actions runs in ephemeral containers with read-only permissions on the repo.

### Phase 7: Documentation Updates

**`CLAUDE.md`** — add to the Prerequisites section:

```
pip install pre-commit
pre-commit install
```

Add to the Key Conventions section:

- **Pre-commit hooks:** Ruff linter/formatter and file hygiene hooks run on every `git commit`. Bypass with `git commit --no-verify` only for emergencies.
- **CI validation gate:** `ci-validation.yml` runs lint + pytest on every push/PR to main. The data pipeline (`openwrt-docs4ai-00-pipeline.yml`) is a separate workflow for scheduled/triggered runs.

**`DEVELOPMENT.md`** — update Prerequisites table with `pre-commit`, `ruff`, and `pyright`. Update Recommended Local Commands to include `pre-commit run --all-files`.

**`tests/README.md`** — add `ruff.toml` to the config references and note that `check_linting.py` uses the centralized `ruff.toml` configuration via the `ruff` command.

---

## 4. Verification Checklist

After implementing all phases, verify in order:

```powershell
# 1. Ruff config is valid and finds no errors
ruff check .
ruff format --check .

# 2. Pyright still passes on the strict subset
pyright --project pyrightconfig.strict.json

# 3. Pre-commit hooks work
pre-commit run --all-files

# 4. Local test runners still pass
python tests/run_pytest.py
python tests/check_linting.py

# 5. Workflow contract test passes (confirms @main refs are intact)
python -m pytest tests/pytest/pytest_06_warning_regression_test.py -q

# 6. Full local validation (if time permits)
python tests/run_smoke_and_pytest.py

# 7. Verify the CI workflow YAML is valid
actionlint .github/workflows/ci-validation.yml
```

---

## 5. Rollback Plan

If the baseline commit causes issues:

1. **Ruff auto-fix introduced a bug:** `git revert <baseline-hash>` then fix the specific file manually. Re-run formatting on the fixed file only.
2. **Pre-commit hooks block legitimate commits:** `git commit --no-verify` to bypass, then fix the hook config. The hooks are a convenience layer, not a security boundary.
3. **CI validation workflow is too strict:** Adjust `ruff.toml` ignore list. Add rules to `ignore = []` temporarily. Fix iteratively.
4. **Pyright version mismatch after Python version update:** Revert `pyrightconfig.strict.json` to `"pythonVersion": "3.11"` if the strict subset has incompatibilities with 3.12 type stubs. Investigate the specific failures before re-attempting.

---

## 6. What This Plan Does NOT Cover

These are explicitly deferred, not forgotten:

- **Smoke tests in CI.** The smoke suite (`smoke_00`, `smoke_01`, `smoke_02`) exercises the full pipeline and requires network access and upstream repo clones. Running them on every PR would be slow and flaky. They remain a local-first validation surface and a scheduled CI concern. Adding a smoke gate to CI is a separate plan.
- **Test coverage reporting.** No `pytest-cov` integration or coverage threshold is proposed. Coverage is valuable but orthogonal to "catch syntax/format errors before pipeline execution."
- **GitHub Actions pinning to SHA.** See Phase 6 — this is an intentional project policy decision. SHA pinning with Dependabot/Renovate is a future enhancement if the team decides to change the `@main` policy.
- **Contract schema centralization.** The Codex review's recommendation #1 (centralize stage contracts in a typed manifest module) is a larger architectural effort. This plan addresses the narrower "don't commit broken code" problem.
- **Atomic L1 writes.** The Codex review's recommendation #2 (temp-write then promote both .md and .meta.json together) is a pipeline resilience improvement, not a testing/linting concern.
- **Expanding the Pyright strict subset.** The current subset in `pyrightconfig.strict.json` is unchanged. Expanding it is a separate effort driven by type-coverage goals.

---

## 7. File Inventory

All files created or modified by this plan:

| File | Action | Phase |
|------|--------|-------|
| `ruff.toml` | **Create** | 1 |
| `pyrightconfig.strict.json` | **Modify** — `pythonVersion` → `"3.12"` | 1b |
| `.git-blame-ignore-revs` | **Create** | 2 |
| `.pre-commit-config.yaml` | **Create** | 3 |
| `.github/workflows/ci-validation.yml` | **Create** | 4 |
| `tests/pytest/pytest_06_warning_regression_test.py` | **Modify** — extend for `ci-validation.yml` | 4b |
| `.github/scripts/requirements.txt` | **Modify** — add `ruff`, `pyright` | 5 |
| `CLAUDE.md` | **Modify** — prerequisites + conventions | 7 |
| `DEVELOPMENT.md` | **Modify** — prerequisites + commands | 7 |
| `tests/README.md` | **Modify** — add ruff.toml reference | 7 |

---

## 8. Timeline Estimate

| Phase | Effort | Risk |
|-------|--------|------|
| 1. Ruff config | 10 min | Low |
| 1b. Pyright version alignment | 2 min | Low |
| 2. Baseline commit | 15–30 min | Medium (auto-fix may need manual follow-up) |
| 3. Pre-commit hooks | 10 min | Low |
| 4. CI workflow | 15 min | Low |
| 4b. Extend contract test | 10 min | Low |
| 5. Dependency updates | 5 min | Low |
| 7. Documentation | 15 min | Low |
| **Verification** | 15 min | — |
| **Total** | **~2 hours** | |
