# Project Implementation Document: Comprehensive Testing & Linting Architecture Upgrade

**Target Environment:** Windows Development Workstations / GitHub Actions CI
**Core Technologies:** Python, Ruff, Pyright, Pytest, pre-commit, GitHub Actions

---

## 1. Executive Summary

### 1.1 Objective
To upgrade and formalize the existing Python testing and code validation architecture. Recently, an agent introduced non-conforming syntax (e.g., bad tabs) which slipped through undetected until the primary data pipeline broke mid-execution. To prevent this, we are upgrading to a strict **3-Tier Gatekeeper System** powered by Ruff, Pyright, Pytest, and our existing local test runners. 

### 1.2 Justification
*   **Fail Fast:** The main data extraction pipeline (`openwrt-docs4ai-00-pipeline.yml`) runs heavy jobs without pre-validation. We need a fast CI gatekeeper to block invalid logic/syntax *before* taking compute time.
*   **Standardization Without Conflict:** Using Ruff prevents "formatting wars" between different AI agents or developers.
*   **Durable Artifacts:** Existing test tracking is well-built but loosely coupled. This plan tightly integrates it into a mandatory workflow.

### 1.3 Tooling Consensus & Toolchain Tiers
The public consensus in the Python ecosystem has solidified rapidly on adopting single-binary, compiled tools ("Rewrite it in Rust for speed"). Developers are aggressively replacing the old Python-based ecosystem. Below is the definitive tier list driving this architectural decision:

*   **S-Tier (The New Gods):** 
    *   **Ruff:** (Rust) Replaces Flake8, Black, isort, pyupgrade, and dozens of plugins. It executes 10-100x faster than all of them combined. Major repositories (FastAPI, HuggingFace, Pydantic, CPython) depend on it.
    *   **uv:** (Rust) Replaces `pip`, `pip-tools`, and `virtualenv`, resolving environments in milliseconds. A perfect companion to Ruff for ultra-fast CI/CD pipelines.
*   **A-Tier (The Enforcers):** 
    *   **pre-commit:** The undisputed king of local Git hook management, necessary to trigger Ruff locally to prevent developers from pushing garbage.
    *   **Pyright:** The current preferred static type checker by Microsoft, which is faster and more accurate than MyPy, providing identical checks locally (via VSCode's Pylance) and in CI.
*   **B-Tier & C-Tier (Legacy / Deprecated):** Black (subsumed by Ruff), Pylint (slow, but kept sometimes for deep cross-file analysis), Flake8 / isort (dead tools walking, superseded by Ruff), MyPy (slow, increasingly outpaced by Pyright).
*   **F-Tier (The Anti-Pattern):** Using LLMs for syntax/format linting is non-deterministic, slow, and expensive. Deterministic linters like Ruff handle syntax instantly; LLMs should be reserved for logical synthesis.

---

## 2. Deep Dive: Testing Mechanics & Documentation

The repository maintains an advanced suite of tests in the `tests/` directory.

### 2.1 The Test Suites (What & Why)

1.  **Pytest Suite (`tests/pytest/`)**: 
    *   *What:* Isolated unit tests and small integration tests.
    *   *Why:* To verify granular python logic, helper functions, and extraction mechanisms (e.g. `pytest_04_wiki_scraper_test.py`) without requiring internet access or long-running repository clones.
2.  **Smoke Suite (`tests/smoke/`)**: 
    *   *What:* Full-pipeline structural validations that run serially.
    *   *Why:* To exercise the massive data extraction and synthesis workflow locally. The smoke scripts route output to temporary environments (`tmp/`) to ensure no side effects mutate the root repo.
3.  **Static Analysis & Linting (`tests/check_linting.py`)**: 
    *   *What:* A wrapper orchestrating Ruff, Pyright, and Actionlint.
    *   *Why:* To enforce deterministic static typing and syntactic formatting instantaneously. AI agents should *never* be used to grade syntax; `check_linting.py` handles this deterministically.

### 2.2 Test Invocations (How & Where)

Developers or agents invoke tests using the provided root-level runners. These runners are built to generate robust output bundles for easy forensic analysis.

*   `python tests/run_pytest.py` $\rightarrow$ Outputs logs and results to `tmp/ci/pytest/<timestamp>/`
*   `python tests/run_smoke.py` $\rightarrow$ Outputs logs to `tmp/ci/smoke/<timestamp>/`
*   `python tests/run_smoke_and_pytest.py` $\rightarrow$ Sequential, outputs to `tmp/ci/local-validation/<timestamp>/`
*   `python tests/run_smoke_and_pytest_parallel.py` $\rightarrow$ Parallel lanes, outputs to `tmp/ci/local-validation-parallel/<timestamp>/`
*   `python tests/check_linting.py` $\rightarrow$ Outputs to `tmp/ci/lint-review/<timestamp>/summary.json`

**Documentation Strategy:** Every execution leaves a `summary.json`. This acts as an API for AI agents. If a pipeline breaks, the agent should immediately read the newest `summary.json` for deterministic exit codes, rather than scraping standard out.

---

## 3. Architecture: The 3-Tier Gatekeeper System

The upgrade plan enforces code quality at three escalating levels.

### Tier 1: The IDE (Real-Time Prevention)
*   **Mechanism:** Developer's IDE (e.g., VSCode, Cursor) running the official Ruff and Pyright extensions.
*   **Action:** Formats code and highlights linting and typing errors on save.

### Tier 2: Local Git Hooks (Commit Prevention)
*   **Mechanism:** `pre-commit` framework running locally on Windows workstations.
*   **Action:** Intercepts `git commit`. Executes Ruff auto-formatting (`ruff check --fix` & `ruff format`) and runs `tests/check_linting.py`. Aborts the commit if violations cannot be resolved automatically.

### Tier 3: CI Pipeline (Merge Prevention)
*   **Mechanism:** A new GitHub Actions workflow dedicated exclusively to Validation (`ci-validation.yml`).
*   **Action:** Acts as the immutable source of truth. Runs immediately on Pull Requests and Pushes. Executes `run_pytest.py` and `check_linting.py`.

---

## 4. Implementation Plan

### Phase 1: Establish Strict Configuration
Define the ruleset centrally so Tier 1, 2, and 3 all enforce the exact same standards. Create a `pyproject.toml` in the repository root:

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
exclude = [".git", ".venv", "tmp", "data"]

[tool.ruff.lint]
select = ["F", "E", "W", "I"]
```

### Phase 2: Codebase Baseline & Auto-Fix
Apply strict linting to isolate syntax updates from logic updates:

```powershell
# Execute global auto-fix and format
python -m ruff check --fix .
python -m ruff format .

# Commit modifications
git add .
git commit -m "chore: baseline codebase with ruff formatting"
```
*Note:* The `$CommitHash` must be added to `.git-blame-ignore-revs` so that `git blame` functionality is not destroyed for the engineering team.

### Phase 3: Bind Local Git Hooks
Implement a `.pre-commit-config.yaml` to run `check_linting.py` prior to any commit.

```yaml
default_stages: [commit]
repos:
  - repo: local
    hooks:
      - id: check-linting
        name: Run check_linting.py
        entry: python tests/check_linting.py
        language: system
        pass_filenames: false
```
*Execution:* `pre-commit install`

### Phase 4: CI/CD Pipeline Integration (The new CI Workflow)
Create `.github/workflows/ci-validation.yml`. 
This is critical for establishing the fail-fast principle. Instead of contaminating `openwrt-docs4ai-00-pipeline.yml`, this separate test workflow acts as a Pull Request gate.

```yaml
name: CI Validation

on:
  pull_request:
    branches: [ "main" ]
  push:
    branches: [ "main" ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main
      - uses: actions/setup-python@main
        with:
          python-version: "3.12"
          cache: 'pip'
      
      - name: Install Linting & App Dependencies
        run: pip install -r .github/scripts/requirements.txt ruff pytest

      - name: Tier 3 Gate - Run check_linting.py
        run: python tests/check_linting.py
      
      - name: Tier 3 Gate - Run PyTest
        run: python tests/run_pytest.py
```

---

## 5. Summary & Guidelines

*   **DON'T** merge code that fails `tests/check_linting.py`.
*   **DO** examine `tmp/ci/<runner>/<timestamp>/summary.json` if a local run fails to quickly identify the breaking component programmatically.
*   **DON'T** use LLMs to check code semantics; lean entirely on the deterministic feedback of Pyright and Ruff provided through our test runners.

---

## 6. Expert Resources & Reference Architectures

### Documentation Sources
*   **Astral's Official Ruff Integrations Guide:** [docs.astral.sh/ruff/integrations/](https://docs.astral.sh/ruff/integrations/)
    * *Why:* Contains exact CLI flags for CI/CD environments and instructions for IDE bindings (VSCode, PyCharm, Vim) ensuring parity between local and CI execution.
*   **Pre-commit Official Documentation:** [pre-commit.com](https://pre-commit.com/#intro)
    * *Why:* Details the Git hook architecture, safe bypasses, and auto-updating logic.
*   **Ignoring Bulk Formatting Commits in Git:** [GitHub Docs on blame.ignoreRevsFile](https://docs.github.com/en/repositories/working-with-files/using-files/viewing-a-file#ignore-commits-in-the-blame-view)
    * *Why:* Explains `.git-blame-ignore-revs` so massive one-time formatting commits do not destroy the historical authorship context of the entire codebase.

### Real-World Reference Architectures (GitHub Repositories)
Study these repositories to see this exact gatekeeping strategy implemented by top-tier projects:
1.  **`python/cpython`** (The Core Python Repository): The official Python language repository uses `pre-commit` and `ruff` (via `.pre-commit-config.yaml`) to enforce code quality. 
2.  **`tiangolo/full-stack-fastapi-template`**: Maintained by the creator of FastAPI. The current industry gold standard for modern Python web backends. Bakes Ruff, `pre-commit`, and GitHub Actions into the core scaffolding.
3.  **`Ranteck/PyStrict-strict-python`**: A boilerplate template combining Ruff, `pre-commit`, and `uv` to achieve "TypeScript strict-mode" levels of safety and fail-fast validation in Python environments.
