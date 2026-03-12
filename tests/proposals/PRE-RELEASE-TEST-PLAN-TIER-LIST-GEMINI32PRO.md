# openwrt-docs4ai Pre-Release Test & Code Analysis Plan

This document outlines a comprehensive, tiered test plan and code review strategy to execute immediately prior to releasing the `openwrt-docs4ai` project. It functions as an exhaustive checklist to ensure maximum pipeline stability, security, and correctness before deployment.

## Code Review & Analysis Primer

Before detailing the tiers, here is an overview of the analysis landscape applied to this plan:

- **Static Analysis**: Analyzing code without executing it (Linting, formatting, type checking).
- **Dynamic Analysis**: Executing code to verify behavior (Unit tests, integration tests, smoke tests).
- **Security Analysis**: Scanning for vulnerabilities in custom code (SAST) and dependencies (SCA).
- **Manual/Peer Review**: Human-driven logic, architecture, and intent verification.

### Environment Preparation
Testers must ensure they are operating in the project's virtual environment prior to execution:
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
```
---

## 🏆 Tier S: The "Must Pass" Release Blockers
*Do not proceed with the release if any of these checks fail. These ensure baseline functionality and syntactic correctness.*

### 1. Automated Functional Testing (Pytest)
Executes all defined unit, integration, and smoke tests to ensure the documentation pipeline resolves links, outputs correctly, and handles API anomalies.
- **Tool**: `pytest`
- **Installation**: `pip install pytest`
- **Command**:
  ```bash
  # Run all tests, limit to 1 failure before stopping to prevent log spam, and show verbose output
  python -m pytest -v --maxfail=1 tests/
  ```
- **Execution Rule**: Must return exit code `0`. 
- **Tester Action on Failure**: Read the traceback provided by pytest to identify the failing assertion. Fix the offending code in `lib/` and re-run.

### 2. Strict Type Checking (Mypy)
Catches type-related logic errors in Python before they manifest as runtime exceptions during long documentation generation runs.
- **Tool**: `mypy`
- **Installation**: `pip install mypy`
- **Command**:
  ```bash
  # Enforce rigorous type checking across the library
  python -m mypy --strict lib/
  ```
- **Execution Rule**: Must return exit code `0`. 
- **Tester Action on Failure**: Follow Mypy's guidance to add missing type hints or fix incorrect types. Do not use `# type: ignore` unless strictly necessary and documented.

### 3. Fast Linter & Formatter (Ruff)
Replaces older tools like Flake8, Black, and isort. Ensures code style consistency and catches common code smells.
- **Tool**: `ruff`
- **Installation**: `pip install ruff`
- **Command (Check First)**:
  ```bash
  # Discover linting errors without auto-fixing
  python -m ruff check lib/ tests/
  ```
- **Command (Format Preview)**:
  ```bash
  # See what files would be rewritten by the formatter
  python -m ruff format --check lib/ tests/
  ```
- **Execution Rule**: Both commands must return exit code `0`. 
- **Tester Action on Failure**: If check fails, manually address linting issues or run `ruff check --fix`. If format fails, run `ruff format lib/ tests/` to auto-format the codebase.

---

## 🥇 Tier A: Security & Regression Catchers
*These prevent security regressions and ensure your test suite is actually touching the critical paths.*

### 1. Software Composition Analysis (Dependencies)
Ensures no third-party packages in your `requirements.txt` or `.venv` have known Common Vulnerabilities and Exposures (CVEs).
- **Tool**: `pip-audit`
- **Installation**: `pip install pip-audit`
- **Command**:
  ```bash
  # Scan the current environment for known vulnerabilities
  python -m pip_audit
  ```
- **Execution Rule**: Must return exit code `0`. 
- **Tester Action on Failure**: Update flagged packages in `requirements.txt` to their latest secure versions and run `pip install -r requirements.txt --upgrade`.

### 2. Static Application Security Testing (Bandit)
Scans Python code for common security issues (e.g., hardcoded passwords, insecure `subprocess` calls common in script pipelines).
- **Tool**: `bandit`
- **Installation**: `pip install bandit`
- **Command**:
  ```bash
  # Scan recursively, showing only MEDIUM and HIGH severity/confidence issues
  python -m bandit -r lib/ --severity-level MEDIUM --confidence-level MEDIUM
  ```
- **Execution Rule**: Must return exit code `0`. 
- **Tester Action on Failure**: Assess if the warning is a false positive (e.g., a safe `subprocess` call). If safe, add a `# nosec` comment with a justification. Otherwise, fix the insecure logic.

### 3. Test Coverage Validation (Coverage.py)
Ensures unit tests are actually exercising the underlying pipeline logic.
- **Tool**: `pytest-cov`
- **Installation**: `pip install pytest-cov`
- **Command**:
  ```bash
  # Run tests with coverage tracking and display missing line numbers
  python -m pytest --cov=lib/ --cov-report=term-missing tests/
  ```
- **Execution Rule**: Output at the bottom of the table must show `TOTAL` coverage >85%.
- **Tester Action on Failure**: Look at the "Missing" column. Write additional tests in `tests/` targeting the uncovered lines.

---

## 🥈 Tier B: Advanced Quality Assurance
*Run these to validate the data artifacts generated by the pipeline, not just the code.*

### 1. Artifact Schema Validation
Since this project produces `L1-raw` and `L2-semantic` data for LLMs, the output must be mechanically verifiable.
- **Action**: Check that every generated semantic markdown file contains YAML frontmatter.
- **Command (Linux / Git Bash / macOS)**:
  ```bash
  find openwrt-condensed-docs/L2-semantic -type f -name "*.md" | xargs grep -m 1 "^---$"
  ```
- **Command (Windows PowerShell)**:
  ```powershell
  Get-ChildItem -Path openwrt-condensed-docs/L2-semantic -Recurse -Filter *.md | Select-String -Pattern "^---$" -List
  ```
- **Execution Rule**: Must successfully find schema markers on 100% of generated documents.

### 2. Broken Link & Cross-Reference Check
Validates that generated documentation doesn't have dead links.
- **Tool**: `markdown-link-check` (Node.js)
- **Installation requirement**: Requires Node.js and `npm` installed.
- **Command**:
  ```bash
  # Use npx to download and run the tool dynamically against a directory
  npx --yes markdown-link-check -p openwrt-condensed-docs
  ```
- **Execution Rule**: Must return exit code `0` with zero dead links. 

### 3. Human PR / Peer Review (The "Logic" Check)
- **Tool**: GitHub Pull Requests.
- **Action**: A second engineer reviews the diff focused strictly on algorithmic intent. Automation catches missing brackets; humans catch misunderstood requirements.

---

## 🥉 Tier C: Ongoing / Post-Release Maintenance
*Not release blockers, but configure them in CI/CD pipeline immediately after beta.*

### 1. Automated Dependency Updates
- **Tool**: Dependabot or Renovate.
- **Action**: Enable in GitHub repository settings. Keeps pipeline dependencies fresh automatically so security rot does not occur.

### 2. Code Complexity Analysis
- **Tool**: `radon` (Cyclomatic Complexity Tracker)
- **Installation**: `pip install radon`
- **Command**: 
  ```bash
  # Calculate complexity score (-s) and average it (-a)
  python -m radon cc -s -a lib/
  ```
- **Action**: Triggers warnings if a specific pipeline module's complexity grades C or lower. Refactor overly complex functions into smaller units.

## Release Sign-Off Checklist
*Before merging to Main, ensure all the following are complete:*

- [ ] `pytest` passed (Tier S)
- [ ] `mypy` strict passed (Tier S)
- [ ] `ruff` check and format passed (Tier S)
- [ ] `pip-audit` passed (Tier A)
- [ ] `bandit` passed (Tier A)
- [ ] `pytest-cov` meets >85% threshold (Tier A)
- [ ] Frontmatter schema validated (Tier B)
- [ ] `markdown-link-check` passed (Tier B)
- [ ] Human Code Review Approved (Tier B)
