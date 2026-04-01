# Project Implementation Document: Code Quality & CI/CD Pipeline Modernization

**Document Status:** Notional. An agent wrote some bad tabs in a recent development action which broke the pipeline run and tracking it down was difficult. We need to incorporate a pre-testing step that is always run during test runsw and reveals easy obvious stuff like formatting problems to the agent so the agent doesn't let stupid mistakes pass. 
**Target Environment:** Windows Development Workstations / GitHub Actions CI
**Core Technologies:** Python, Ruff, pre-commit, GitHub Actions

---

## 1. Executive Summary

### 1.1 Objective
To upgrade the existing Python code validation pipeline by replacing legacy, fragmented tooling (Flake8, Black, isort, Pylint) with a unified, high-performance toolchain. This plan implements **Ruff** (a Rust-based linter/formatter) and orchestrates it via a 3-Tier Gatekeeper architecture to enforce deterministic code quality, reduce CI compute costs, and eliminate syntax-related regressions.

### 1.2 Justification
* **Performance:** Ruff executes 10-100x faster than legacy Python linters, significantly reducing CI pipeline duration.
* **Toolchain Consolidation:** Ruff replaces dozens of disparate dependencies and plugins, simplifying environment management.
* **Deterministic Validation:** Replaces any reliance on non-deterministic methods (e.g., LLMs) for syntax or formatting enforcement, reserving AI resources for logical and architectural design.

---

## 2. Architecture: The 3-Tier Gatekeeper System

The pipeline enforces code quality at three escalating levels to minimize compute waste and prevent invalid code from polluting the Git history.

* **Tier 1: The IDE (Real-Time Prevention)**
    * **Mechanism:** Developer's IDE (e.g., VSCode, PyCharm) running the official Ruff extension.
    * **Action:** Formats code and highlights linting errors on save.
* **Tier 2: Local Git Hooks (Commit Prevention)**
    * **Mechanism:** `pre-commit` framework running locally on Windows workstations.
    * **Action:** Intercepts `git commit`. Executes Ruff. Aborts the commit if violations cannot be auto-fixed.
* **Tier 3: CI Pipeline (Merge Prevention)**
    * **Mechanism:** GitHub Actions workflow.
    * **Action:** Acts as the immutable source of truth. Runs as the "Fail-Fast" step prior to unit testing. Rejects Pull Requests containing malformed code.

---

## 3. Implementation Plan

### Phase 1: Codebase Baseline & Isolation
Applying strict linting to an existing project will generate thousands of violations. The codebase must be baselined in a single, isolated commit to prevent polluting the repository's authorship history.

**Execute the following in PowerShell at the repository root:**

```powershell
# 1. Install required tools within the active virtual environment
pip install ruff pre-commit

# 2. Execute a global auto-fix for safe violations (e.g., unused imports)
ruff check --fix .

# 3. Execute a global format to align all syntax
ruff format .

# 4. Commit the changes, isolating the formatting modifications
git add .
git commit -m "chore: baseline codebase with ruff formatting"

# 5. Capture the Git commit hash
$CommitHash = git rev-parse HEAD
```

**Critical Next Step:** To prevent this massive formatting commit from ruining `git blame` for the engineering team, create a `.git-blame-ignore-revs` file in the repository root and paste the `$CommitHash` into it. 

Configure local Git clients to use this file:
```powershell
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

### Phase 2: Configuration & Hook Binding
Define the ruleset centrally so Tier 1, 2, and 3 all enforce the exact same standards.

**1. Create `pyproject.toml` (Repository Root):**
```toml
[tool.ruff]
# Set the maximum line length
line-length = 88
# Assume Python 3.11 for target features
target-version = "py311"
# Exclude standard directories
exclude = [".git", ".venv", "env", "venv", "__pycache__", "build", "dist"]

[tool.ruff.lint]
# Enable standard rules: Pyflakes (F), pycodestyle (E, W), isort (I)
select = ["F", "E", "W", "I"]
# Explicitly ignore rules that conflict with legacy architecture (adjust as needed)
ignore = [] 

[tool.ruff.format]
# Enable auto-formatting of code examples in docstrings
docstring-code-format = true
```

**2. Create `.pre-commit-config.yaml` (Repository Root):**
```yaml
# Enforce fail-fast execution
default_stages: [commit]

repos:
  # Standard file hygiene hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict

  # Ruff Integration
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0  # MUST be pinned to a specific version for stability
    hooks:
      # Run the linter and auto-fix what is safely fixable
      - id: ruff
        args: [ --fix ]
      # Run the formatter
      - id: ruff-format
```

**3. Bind the Hooks:**
Deploy the configuration to the local hidden `.git/hooks` directory.
```powershell
pre-commit install
```

### Phase 3: CI/CD Pipeline Integration
Inject the gatekeeper into the existing GitHub Actions pipeline. This must execute *before* the test matrix.

**Modify `.github/workflows/ci.yml`:**
```yaml
name: Continuous Integration

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main", "develop" ]

jobs:
  validate-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: 'pip'

      # ==========================================
      # TIER 3: THE FAIL-FAST LINTING GATEKEEPER
      # ==========================================
      - name: Install Linting Dependencies
        run: pip install ruff

      - name: Enforce Formatting
        # --check verifies formatting without altering files
        run: ruff format --check .

      - name: Enforce Linting Rules
        # --output-format=github creates inline PR annotations for failures
        run: ruff check --output-format=github .
      # ==========================================

      # Proceed to unit tests ONLY if linting passes
      - name: Install Application Dependencies
        run: pip install -r requirements.txt pytest
        
      - name: Run PyTest Matrix
        run: pytest tests/
```

---

## 4. Implementation Guidelines: DOs and DON'Ts

### DO
* **DO pin tool versions:** Always pin the `rev:` in `.pre-commit-config.yaml`. Unpinned linters will break the CI pipeline unexpectedly when new rules are released upstream. Use `pre-commit autoupdate` on a scheduled maintenance cycle.
* **DO utilize `.git-blame-ignore-revs`:** This is mandatory for existing projects. Failing to implement this will destroy the ability to trace the historical context of code lines.
* **DO implement `--output-format=github`:** This parameter in the CI workflow drastically improves the developer experience by placing linting errors directly on the exact lines in the GitHub Pull Request "Files Changed" tab.
* **DO mandate IDE extensions:** Require all developers to install the Ruff extension for VSCode/PyCharm and enable "Format on Save."

### DON'T
* **DON'T utilize LLMs/AI for syntax validation:** Never construct evaluation scripts or CI hooks that use LLMs to detect syntax or formatting issues. They are non-deterministic, slow, and expensive. Use compiled deterministic binaries (Ruff).
* **DON'T run heavy tests before linting:** Never place `pytest` or database spin-ups before Ruff in the GitHub Actions YAML. Linting is a microsecond operation; tests take minutes. Fail fast to conserve CI compute minutes.
* **DON'T forcefully replace Pylint immediately if relying on deep type inference:** Ruff is exceptionally fast because it generally analyzes one file at a time. If the legacy project relies on Pylint for complex cross-file architectural analysis, retain Pylint in CI as a secondary check until the codebase is refactored.
* **DON'T panic on legacy rule conflicts:** If Ruff flags thousands of errors on a specific rule (e.g., `E501` Line Length) that cannot be auto-fixed, add that rule to the `ignore = []` array in `pyproject.toml` temporarily. Fix architectural debt iteratively, not instantaneously.

---

## 5. Reference Architectures
For production-grade examples of this exact pipeline architecture, refer to the following open-source repositories:
* **`python/cpython`**: The core Python language repository.
* **`tiangolo/full-stack-fastapi-template`**: The industry standard for modern Python web backends.

http://googleusercontent.com/interactive_content_block/0