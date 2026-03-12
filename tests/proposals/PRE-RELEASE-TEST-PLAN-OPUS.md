# Pre-Release Test Plan — openwrt-docs4ai v12

**Project:** LuminairPrime/openwrt-docs4ai-v12-copilot  
**Pipeline:** `openwrt-docs4ai-00-pipeline.yml`  
**Prepared:** 2026-03-11  
**Status:** Beta → Release Candidate  
**Python:** 3.12 (CI), 3.11+ (local)  
**Runner:** ubuntu-24.04

---

## How To Use This Document

Each test tier is ordered by priority. Within each tier, tests are numbered and include:

- **What** is being tested
- **Why** it matters for release
- **Exact commands** to run
- **Expected results** (pass criteria)
- **Status column** for the tester to fill in

Mark each test: ✅ PASS | ❌ FAIL | ⏭️ SKIPPED (with reason)

---

## Prerequisites

Before running any tests, ensure you have the following installed and accessible:

```powershell
# 1. Python 3.11+ with pip
python --version   # Expected: Python 3.11.x or 3.12.x

# 2. Clone the repo and cd into it
# (assumed: you are already in the repo root)

# 3. Create a virtual environment (if not already done)
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows PowerShell
# or: source .venv/bin/activate  # Linux/macOS

# 4. Install pipeline dependencies
pip install -r .github/scripts/requirements.txt

# 5. Install test/analysis dependencies
pip install pytest pytest-cov ruff pyright pip-audit bandit vulture radon

# 6. Verify tools are on PATH
pytest --version
ruff --version
pyright --version
pip-audit --version
bandit --version
vulture --version
radon --version
```

> **Note:** Some Tier 2 and Tier 3 tests require `node` and/or `ucode` on PATH. These are optional and tests will note when they are skipped due to missing binaries.

---

## Test Result Summary

| Tier | Section | Tests | Pass | Fail | Skip |
|------|---------|-------|------|------|------|
| 1 | Existing Unit Tests | | | | |
| 1 | Smoke Test (Fixture) | | | | |
| 1 | Static Analysis (Ruff) | | | | |
| 2 | Type Checking (Pyright) | | | | |
| 2 | Dependency Audit | | | | |
| 2 | Security Scan (Bandit) | | | | |
| 2 | Test Coverage | | | | |
| 3 | Dead Code Detection | | | | |
| 3 | Complexity Analysis | | | | |
| 3 | Full CI Pipeline Verification | | | | |
| 3 | Published Output Validation | | | | |

---

## Tier 1 — Must Pass Before Release

These tests represent the minimum quality bar. Any failure here is a **release blocker**.

---

### T1.1 — Existing Unit Tests (pytest)

**What:** Run the maintained pytest suite covering wiki scraper logic, pipeline hardening, normalization, validation, cross-link resolution, and workflow structure.

**Why:** These tests validate the correctness of every pipeline stage's core logic. A regression here means the pipeline will produce incorrect output.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot
python tests/run_pytest.py -v --tb=short 2>&1 | Tee-Object -FilePath tests\test-results-unit.txt
```

**Expected results:**
- Exit code: `0`
- All tests: `PASSED`
- No warnings from pytest itself (deprecation warnings from dependencies are acceptable)
- Zero `FAILED` or `ERROR` entries

**Pass criteria:** 100% of tests pass. Zero tolerance for failures.

| Status | Notes |
|--------|-------|
| | |

---

### T1.2 — Smoke Test (Fixture-Backed, Offline)

**What:** Run the full post-extract pipeline locally using synthetic fixture data. This exercises scripts 03→08 sequentially in an isolated temp directory.

**Why:** Validates that all pipeline stages execute without errors when given well-formed input, and that the output contract (required files, cross-links, deprecation warnings, monoliths, IDE schemas) is met.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot
python tests/smoke/smoke_01_full_local_pipeline.py --keep-temp 2>&1 | Tee-Object -FilePath tests\test-results-smoke.txt
```

**Expected results:**
- Final line: `Overall: PASS`
- All individual stages: `PASS`
- Fixture assertions: `PASS`
- Output directory (printed to console) should contain:
  - `llms.txt`, `llms-full.txt`, `AGENTS.md`, `README.md`, `index.html`
  - `ucode/ucode-complete-reference.md`, `ucode/ucode-skeleton.md`, `ucode/ucode.d.ts`
  - `CHANGES.md`, `changelog.json`, `signature-inventory.json`
  - Cross-link injections in `L2-semantic/procd/` referencing UCI
  - Deprecation `[!WARNING]` injections in `L2-semantic/wiki/`

**Pass criteria:** `Overall: PASS`. Zero `FAIL` or `TIMEOUT` stages.

| Status | Notes |
|--------|-------|
| | |

---

### T1.3 — Static Analysis: Ruff Lint

**What:** Run the Ruff linter across all Python source files (pipeline scripts + library modules + tests). Ruff checks for ~800 lint rules including pyflakes, pycodestyle, isort, and many pylint equivalents.

**Why:** Catches unused imports, undefined names, unreachable code, style violations, and common bugs. For a release, you want zero lint errors in production code.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# Lint the production pipeline scripts and library
ruff check .github/scripts/ lib/ --output-format=grouped 2>&1 | Tee-Object -FilePath tests\test-results-ruff-scripts.txt

# Lint the test code (separately, to distinguish test vs. production issues)
ruff check tests/ --output-format=grouped 2>&1 | Tee-Object -FilePath tests\test-results-ruff-tests.txt
```

**Expected results:**
- Exit code: `0` (no errors)
- If errors are found, the output will list file, line, rule code, and description
- Common findings to watch for:
  - `F401` — Unused import
  - `F811` — Redefinition of unused name
  - `F841` — Local variable assigned but never used
  - `E501` — Line too long (>88 chars by default)
  - `E722` — Bare `except:` clause

**Pass criteria for release:**
- **Production code** (`.github/scripts/`, `lib/`): Zero errors. Any findings must be fixed or explicitly suppressed with `# noqa: XXXX` with justification.
- **Test code** (`tests/`): Zero errors preferred; up to 5 minor style findings (E501) acceptable if documented.

| Status | Area | Notes |
|--------|------|-------|
| | scripts + lib | |
| | tests | |

---

### T1.4 — Static Analysis: Ruff Format Check

**What:** Verify that all Python files conform to a consistent code style (Black-compatible formatting).

**Why:** Consistent formatting reduces merge conflicts and cognitive load. A format check is non-destructive — it only reports, it doesn't change files.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# Check only (no changes)
ruff format --check .github/scripts/ lib/ tests/ 2>&1 | Tee-Object -FilePath tests\test-results-ruff-format.txt
```

**Expected results:**
- Exit code: `0` means all files are already formatted
- Exit code: `1` means some files would be reformatted

**If files need formatting, apply the fixes:**
```powershell
# Auto-format (modifies files in place)
ruff format .github/scripts/ lib/ tests/
```

**Pass criteria:** Exit code `0` after any fixes are applied. Commit the formatted files before release.

| Status | Notes |
|--------|-------|
| | |

---

## Tier 2 — Should Pass Before Release

These tests check for deeper quality issues. Failures should be addressed before release unless there is documented justification for deferral.

---

### T2.1 — Type Checking: Pyright (Strict Mode)

**What:** Run Pyright static type checker against the Python codebase. The project already has a `pyrightconfig.strict.json` that currently covers only 3 files. This test expands coverage.

**Why:** Type errors are a major source of runtime crashes in Python, especially for a pipeline that processes diverse data shapes (JSON manifests, YAML frontmatter, HTML scrapes).

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# A. Run against the existing strict config (MUST pass)
pyright --project pyrightconfig.strict.json 2>&1 | Tee-Object -FilePath tests\test-results-pyright-strict.txt

# B. Run in basic mode against ALL scripts (informational)
pyright .github/scripts/ lib/ --pythonversion 3.12 2>&1 | Tee-Object -FilePath tests\test-results-pyright-all.txt
```

**Expected results:**
- **A (strict config):** Exit code `0`, zero errors. This covers `lib/ai_store.py`, `lib/config.py`, and `openwrt-docs4ai-04-generate-ai-summaries.py`.
- **B (all scripts):** Will likely have findings. Document the count and severity.

**Pass criteria:**
- **A:** Zero errors (release blocker if failing)
- **B:** Document total errors. Target: reduce to <20 before release. Type errors in the `reportMissing*` categories are lowest priority; `reportGeneralTypeIssues` are highest.

**Post-release roadmap:** Incrementally add files to `pyrightconfig.strict.json` as they pass strict mode.

| Status | Scope | Error Count | Notes |
|--------|-------|-------------|-------|
| | strict (3 files) | | |
| | basic (all files) | | |

---

### T2.2 — Dependency Audit

**What:** Check all Python dependencies for known security vulnerabilities (CVEs) and verify they are pinned to specific versions.

**Why:** Unpinned dependencies (`requests` instead of `requests==2.31.0`) mean CI builds are non-reproducible and could break at any time. Security vulnerabilities in deps could be exploited.

**Commands:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# A. Check for known vulnerabilities
pip-audit -r .github/scripts/requirements.txt 2>&1 | Tee-Object -FilePath tests\test-results-pip-audit.txt

# B. Generate a pinned requirements file (for comparison/adoption)
pip freeze > tests\test-results-pip-freeze.txt

# C. Check current requirements.txt for pinning
Get-Content .github/scripts/requirements.txt
```

**Current state of `requirements.txt`:**
```
requests
tiktoken
pyyaml
lxml
beautifulsoup4
html5lib
markdownify
```

> ⚠️ **None of these are version-pinned.** This is a pre-release finding.

**Expected results:**
- **A:** Zero vulnerabilities found
- **B:** Shows exact versions currently installed
- **C:** Confirms no pinning (known issue)

**Pass criteria:**
- Zero known CVEs in current dependency versions
- **Recommended fix:** Create a pinned `requirements.txt` using `pip freeze` output filtered to direct deps plus their transitive deps, or use `pip-compile` (from `pip-tools`) for deterministic lock files:

```powershell
pip install pip-tools
pip-compile .github/scripts/requirements.txt --output-file .github/scripts/requirements.lock
```

| Status | Vulnerabilities | Pinned? | Notes |
|--------|----------------|---------|-------|
| | | | |

---

### T2.3 — Security Scan: Bandit

**What:** Scan all Python source code for common security issues: hardcoded passwords, use of `eval()`, insecure temp files, subprocess shell injection, etc.

**Why:** The pipeline clones git repos, makes HTTP requests, runs `subprocess.run()`, and handles file paths. Any of these could be a vector if mishandled.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

bandit -r .github/scripts/ lib/ -f txt -ll 2>&1 | Tee-Object -FilePath tests\test-results-bandit.txt
```

**Flag explanations:**
- `-r` — Recursive scan
- `-f txt` — Text output format
- `-ll` — Only show medium and high severity issues

**Expected results:**
- Exit code: `0` means no medium/high findings
- Common false positives in this project:
  - `B603` (subprocess without shell=True) — this is actually the *safe* pattern; Bandit sometimes flags it
  - `B310` (urllib request) — safe if URL is controlled
- Real issues to watch for:
  - `B101` — Use of `assert` in production code (asserts are stripped with `-O`)
  - `B108` — Hardcoded temp directory
  - `B602` — `subprocess` with `shell=True` (should not exist)

**Pass criteria:**
- Zero HIGH severity findings
- Zero MEDIUM findings that are not documented false positives
- Record any LOW findings for post-release cleanup

| Status | High | Medium | Low | Notes |
|--------|------|--------|-----|-------|
| | | | | |

---

### T2.4 — Test Coverage Analysis

**What:** Measure how much of the pipeline's Python code is exercised by the existing unit tests.

**Why:** Low coverage means untested code paths that could have hidden bugs. For release, you need to know which scripts have zero test coverage.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

python tests/run_pytest.py --cov=.github/scripts --cov=lib --cov-report=term-missing --cov-report=html:tests/coverage-report -v 2>&1 | Tee-Object -FilePath tests\test-results-coverage.txt
```

**Expected results:**
- The terminal output will show a table like:
  ```
  Name                                                      Stmts   Miss  Cover
  ---------------------------------------------------------------------------------
  .github/scripts/openwrt-docs4ai-02a-scrape-wiki.py          250     80    68%
  .github/scripts/openwrt-docs4ai-03-normalize-semantic.py     350    120    66%
  lib/config.py                                                 40      5    88%
  ...
  ```
- An HTML report will be generated at `tests/coverage-report/index.html` — open it in a browser for line-by-line coverage visualization.

**Pass criteria:**
- **Library modules** (`lib/`): ≥80% coverage
- **Pipeline scripts** (`.github/scripts/`): ≥50% average coverage
- **No script at 0%:** Every script should have at least one test exercising its imports and basic path

**Scripts likely to have low/no direct coverage** (by design, since they require network or CI context):
- `01-clone-repos.py` (requires git repos)
- `02b` through `02h` extractors (require cloned repos)
- `04-generate-ai-summaries.py` (requires API access)

| Status | Overall % | Lowest Script | Notes |
|--------|-----------|---------------|-------|
| | | | |

---

### T2.5 — Workflow YAML Validation

**What:** Validate the GitHub Actions workflow file for syntax correctness and common issues.

**Why:** A YAML syntax error in the workflow will break the entire CI pipeline. Even if it "works" today, certain edge cases (like YAML anchor reuse or special characters) can cause silent misparses.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# A. Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/openwrt-docs4ai-00-pipeline.yml', encoding='utf-8').read()); print('YAML syntax: OK')"

# B. Check for common issues
python -c "
import yaml
with open('.github/workflows/openwrt-docs4ai-00-pipeline.yml', encoding='utf-8') as f:
    wf = yaml.safe_load(f)
jobs = wf.get('jobs', {})
print(f'Jobs: {len(jobs)}')
for name, job in jobs.items():
    steps = job.get('steps', [])
    print(f'  {name}: {len(steps)} steps, runs-on={job.get(\"runs-on\", \"?\")}, needs={job.get(\"needs\", \"none\")}')
print('Workflow structure: OK')
"
```

**Expected results:**
- Both commands exit `0`
- Job graph should show correct dependency chain: `initialize` → `extract` (parallel matrix + `extract_wiki`) → `extract_summary` → `process` → `deploy` → `pipeline_summary`
- No orphaned jobs (every job except triggers should have `needs`)

**Pass criteria:** Valid YAML, correct job dependency chain, all jobs present.

| Status | Notes |
|--------|-------|
| | |

---

## Tier 3 — Recommended Before Release

These tests improve code quality and long-term maintainability. Document findings even if not fully resolved before release.

---

### T3.1 — Dead Code Detection: Vulture

**What:** Scan for unused functions, variables, classes, and imports that are dead code.

**Why:** After 30+ bug fixes, dead code accumulates. It increases cognitive load and can hide bugs.

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

vulture .github/scripts/ lib/ --min-confidence 80 2>&1 | Tee-Object -FilePath tests\test-results-vulture.txt
```

**Flag explanation:**
- `--min-confidence 80` — Only report findings Vulture is ≥80% confident are truly unused (reduces false positives from dynamic attribute access)

**Expected results:**
- List of potentially unused code with file, line, and confidence percentage
- Common false positives: functions called via `importlib`, functions exposed as module-level API but only called from workflow inline Python

**Pass criteria:**
- Document all findings
- Remove any genuinely dead code before release
- Add `# vulture: ignore` comments to legitimate false positives

| Status | Findings | Removed | False Positives | Notes |
|--------|----------|---------|-----------------|-------|
| | | | | |

---

### T3.2 — Complexity Analysis: Radon

**What:** Measure cyclomatic complexity (CC) and maintainability index (MI) of all Python functions.

**Why:** Functions with CC > 15 are difficult to test and maintain. A MI < 20 indicates code that is hard to understand.

**Commands:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# A. Cyclomatic complexity — show only C grade and worse (CC ≥ 11)
radon cc .github/scripts/ lib/ -s -n C 2>&1 | Tee-Object -FilePath tests\test-results-radon-cc.txt

# B. Maintainability Index — show all files ranked
radon mi .github/scripts/ lib/ -s 2>&1 | Tee-Object -FilePath tests\test-results-radon-mi.txt
```

**Complexity grades:**
| Grade | CC Range | Meaning |
|-------|----------|---------|
| A | 1–5 | Simple, low risk |
| B | 6–10 | Moderate, manageable |
| C | 11–15 | Complex, needs attention |
| D | 16–20 | Very complex, refactor candidate |
| E | 21–30 | Alarming complexity |
| F | 31+ | Unmaintainable |

**Expected high-complexity candidates** (based on file sizes):
- `openwrt-docs4ai-03-normalize-semantic.py` (33KB, largest script — likely has complex HTML table conversion)
- `openwrt-docs4ai-02a-scrape-wiki.py` (26KB — wiki discovery, caching, pandoc fallback)
- `openwrt-docs4ai-04-generate-ai-summaries.py` (20KB — AI store, API retry logic)

**Pass criteria:**
- No functions at grade **E** or **F**
- Document all grade **C** and **D** functions
- Target: refactor any grade **D** functions post-release

| Status | Grade D+ Count | Worst Function | Notes |
|--------|----------------|----------------|-------|
| | | | |

---

### T3.3 — Full CI Pipeline Verification (GitHub Actions)

**What:** Verify the actual GHA pipeline runs green end-to-end with zero warnings from your own code.

**Why:** The ultimate integration test. Local tests can't replicate the exact CI environment (ubuntu-24.04, parallel matrix jobs, artifact upload/download).

**How to run:**

1. Push a branch or trigger the workflow manually (`workflow_dispatch` if enabled)
2. Wait for the run to complete
3. Download or inspect the run logs

**What to check:**

| Check | Location | Expected |
|-------|----------|----------|
| All jobs green | Actions tab | ✅ All jobs pass |
| Zero `##[error]` lines | Every job log | Zero |
| `##[warning]` lines | Every job log | Only the known Node.js 20 deprecation (see `log-warning-analysis-opus.md`) |
| Script 05a size warnings | process job log | ≤2 (wiki, luci-examples) — known and documented |
| Script 08 soft warnings | process job log | ≤1 (luci-app-dockerman uCode false positive) |
| Extract summary | extract_summary job | `contract_failures: 0` |
| Process summary | process job | `contract_ok: true`, `missing_required_files: none` |
| Pages deployment | deploy job | `Reported success!` |

**Pass criteria:** Pipeline green, zero errors, only documented/expected warnings.

| Status | Run ID | Duration | Notes |
|--------|--------|----------|-------|
| | | | |

---

### T3.4 — Published Output Integrity

**What:** Validate the final published output against the quality contract after a live pipeline run.

**Why:** Even if the pipeline runs green, the output could have subtle issues (truncated files, missing cross-links, broken llms.txt entries).

**How to run (after T3.3 completes):**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# Pull the latest committed output
git pull origin main

# A. Run the validation script locally against the committed output
$env:OUTDIR = "openwrt-condensed-docs"
$env:VALIDATE_MODE = "hard"
python .github/scripts/openwrt-docs4ai-08-validate-output.py 2>&1 | Tee-Object -FilePath tests\test-results-output-validation.txt
```

**Expected results:**
```
[08] Validation Results
[08]   Files Checked: ~325
[08]   Hard Failures: 0
[08]   Soft Warnings: ≤1
[08] Validation pass complete.
```

**Additional manual checks:**

```powershell
# B. Verify file counts are reasonable
(Get-ChildItem -Recurse openwrt-condensed-docs -Filter "*.md").Count  # Expected: ~320-340
(Get-ChildItem -Recurse openwrt-condensed-docs -Filter "*.json").Count  # Expected: ~15+

# C. Verify no zero-byte files
Get-ChildItem -Recurse openwrt-condensed-docs | Where-Object { $_.Length -eq 0 }  # Expected: empty/none

# D. Verify llms.txt is populated
(Get-Content openwrt-condensed-docs\llms.txt | Measure-Object -Line).Lines  # Expected: 50+

# E. Verify GitHub Pages site is live
# Open in browser: https://luminairprime.github.io/openwrt-docs4ai-v12-copilot/
# Expected: styled landing page with module links
```

**Pass criteria:** Zero hard failures, all manual checks pass.

| Status | Files Checked | Hard Failures | Notes |
|--------|---------------|---------------|-------|
| | | | |

---

### T3.5 — Line Ending Consistency

**What:** Verify all committed files use consistent line endings (LF, not CRLF).

**Why:** Mixed line endings cause diff noise, can break shell scripts in CI (ubuntu), and have historically caused bugs in this project (per conversation history).

**Command:**

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# Check .gitattributes exists and enforces LF
Get-Content .gitattributes

# Find any files with CRLF line endings in the scripts directory
python -c "
from pathlib import Path
crlf_files = []
for p in list(Path('.github/scripts').glob('*.py')) + list(Path('lib').glob('*.py')) + list(Path('tests').glob('*.py')):
    content = p.read_bytes()
    if b'\r\n' in content:
        crlf_files.append(str(p))
if crlf_files:
    print(f'CRLF found in {len(crlf_files)} files:')
    for f in crlf_files:
        print(f'  {f}')
else:
    print('All Python files use LF line endings: OK')
"
```

**Expected results:**
- `.gitattributes` should contain `* text=auto` or `*.py text eol=lf`
- All Python files should use LF line endings

**Pass criteria:** All Python files use LF. `.gitattributes` enforces `text=auto` at minimum.

| Status | CRLF Files | Notes |
|--------|-----------|-------|
| | | |

---

## Post-Test Artifacts Checklist

After running all tests, the `tests/` directory should contain these result files:

| File | From Test | Purpose |
|------|-----------|---------|
| `test-results-unit.txt` | T1.1 | pytest unit test output |
| `test-results-smoke.txt` | T1.2 | Smoke test output |
| `test-results-ruff-scripts.txt` | T1.3 | Ruff lint (production code) |
| `test-results-ruff-tests.txt` | T1.3 | Ruff lint (test code) |
| `test-results-ruff-format.txt` | T1.4 | Ruff format check |
| `test-results-pyright-strict.txt` | T2.1 | Pyright strict (3 files) |
| `test-results-pyright-all.txt` | T2.1 | Pyright basic (all files) |
| `test-results-pip-audit.txt` | T2.2 | Dependency vulnerability scan |
| `test-results-pip-freeze.txt` | T2.2 | Pinned dependency snapshot |
| `test-results-bandit.txt` | T2.3 | Security scan |
| `test-results-coverage.txt` | T2.4 | Test coverage report |
| `coverage-report/` | T2.4 | HTML coverage detail |
| `test-results-vulture.txt` | T3.1 | Dead code detection |
| `test-results-radon-cc.txt` | T3.2 | Cyclomatic complexity |
| `test-results-radon-mi.txt` | T3.2 | Maintainability index |
| `test-results-output-validation.txt` | T3.4 | Published output validation |

> **Tip:** Add `test-results-*` and `coverage-report/` to `.gitignore` to avoid committing transient test artifacts.

---

## Release Criteria Decision Matrix

| Condition | Release? |
|-----------|----------|
| Any Tier 1 test fails | ❌ NO — must fix first |
| Tier 1 passes, one Tier 2 test fails | ⚠️ CONDITIONAL — document the gap, set a fix deadline within 1 sprint |
| Tier 1+2 pass, Tier 3 has findings | ✅ YES — file issues for Tier 3 findings as post-release cleanup |
| All tiers pass | ✅ YES — ship it |

---

## Quick-Run Script

For convenience, you can run all local tests (Tier 1 + most of Tier 2) in a single session:

```powershell
cd C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-v12-copilot

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

Write-Host "`n========== T1.1: Unit Tests ==========" -ForegroundColor Cyan
python tests/run_pytest.py -v --tb=short 2>&1 | Tee-Object -FilePath tests\test-results-unit.txt

Write-Host "`n========== T1.2: Smoke Test ==========" -ForegroundColor Cyan
python tests/smoke/smoke_01_full_local_pipeline.py 2>&1 | Tee-Object -FilePath tests\test-results-smoke.txt

Write-Host "`n========== T1.3: Ruff Lint ==========" -ForegroundColor Cyan
ruff check .github/scripts/ lib/ --output-format=grouped 2>&1 | Tee-Object -FilePath tests\test-results-ruff-scripts.txt

Write-Host "`n========== T1.4: Ruff Format ==========" -ForegroundColor Cyan
ruff format --check .github/scripts/ lib/ tests/ 2>&1 | Tee-Object -FilePath tests\test-results-ruff-format.txt

Write-Host "`n========== T2.1: Pyright Strict ==========" -ForegroundColor Cyan
pyright --project pyrightconfig.strict.json 2>&1 | Tee-Object -FilePath tests\test-results-pyright-strict.txt

Write-Host "`n========== T2.2: Dependency Audit ==========" -ForegroundColor Cyan
pip-audit -r .github/scripts/requirements.txt 2>&1 | Tee-Object -FilePath tests\test-results-pip-audit.txt

Write-Host "`n========== T2.3: Bandit Security ==========" -ForegroundColor Cyan
bandit -r .github/scripts/ lib/ -f txt -ll 2>&1 | Tee-Object -FilePath tests\test-results-bandit.txt

Write-Host "`n========== T2.4: Test Coverage ==========" -ForegroundColor Cyan
python tests/run_pytest.py --cov=.github/scripts --cov=lib --cov-report=term-missing -v 2>&1 | Tee-Object -FilePath tests\test-results-coverage.txt

Write-Host "`n========== Complete ==========" -ForegroundColor Green
Write-Host "Test result files saved to tests\ directory"
```

Save this as `tests/run-all-local-tests.ps1` and run it with:
```powershell
powershell -ExecutionPolicy Bypass -File tests/run-all-local-tests.ps1
```
