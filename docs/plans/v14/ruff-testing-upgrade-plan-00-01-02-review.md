Now I have all three plan files in full. Here's the comprehensive analysis.

---

## Comparative Analysis of the Three Quality Upgrade Plans

### Plan v00 — Grade: **C-** (Generic boilerplate, project-unaware)

**What it gets right:**
- The 3-Tier Gatekeeper concept (IDE → pre-commit → CI) is sound and appears in all three plans
- DOs/DON'Ts section has universally good advice: pin tool versions, use `.git-blame-ignore-revs`, `--output-format=github` for PR annotations, never use LLMs for syntax checking
- References cpython and FastAPI as exemplars — both are valid

**What it gets wrong:**
- Claims to replace "legacy, fragmented tooling (Flake8, Black, isort, Pylint)" — none of which exist in this project. The project already uses Ruff (just `ruff check`, no `ruff format`)
- **Python 3.11** — wrong. CI runs 3.12
- **Line length 88** — PEP 8 default but narrow for this codebase
- **`pyproject.toml`** — the project uses standalone config files (pyrightconfig.strict.json), not a centralized pyproject.toml
- **`@v4`/`@v5` action refs** — directly violates the project's intentional `@main` pinning policy, which is enforced by `pytest_06_warning_regression_test.py`. Applying this plan as-is would break the existing contract test
- References a `ci.yml` workflow that doesn't exist
- No awareness of check_linting.py, the existing test runners, or the pyrightconfig version mismatch

**Verdict:** This is a generic "modernize your Python linting" document pasted from a template. It would actively break things if applied without heavy adaptation.

---

### Plan v01 — Grade: **B** (Project-aware, some design misjudgments)

**What it gets right:**
- Correctly identifies check_linting.py and all test runners with their exact output paths
- Tooling tier list (S/A/B/C/F) is an excellent framing device — clearly explains why Ruff won and why LLMs are F-tier for syntax
- **Python 3.12** and **line-length 120** — both correct for this project
- Creates a separate `ci-validation.yml` instead of contaminating the data pipeline workflow — architecturally clean
- Uses **`@main` action refs** — consistent with project policy
- Documents the test invocation patterns and summary.json forensics approach

**What it gets wrong:**
- **`pyproject.toml`** — still the wrong config pattern for this project
- **Pre-commit uses a LOCAL hook calling `python tests/check_linting.py`** — this is a creative reuse of existing tooling, but v02 correctly identifies the problem: check_linting.py has fragile Windows PATH dependencies for pyright and actionlint that may not resolve correctly in a pre-commit hook subprocess environment
- **Ruff rules limited to `F, E, W, I`** — misses easy wins like `UP` (pyupgrade), `B` (flake8-bugbear), `SIM` (simplify)
- **Never mentions the pyrightconfig Python version mismatch** (3.11 in config vs 3.12 in CI)
- CI workflow runs check_linting.py and run_pytest.py in a single job — no separation between fast lint gate and slower test execution

**Verdict:** Shows real project understanding. The test documentation section is valuable standalone. Falls short on configuration details and misses the pyrightconfig mismatch.

---

### Plan v02 — Grade: **A-** (Implementation-ready, deeply project-aware)

**What it gets right:**
- **Identifies all real gaps**: no pre-commit, no CI validation, no ruff config file, Python version mismatch, unpinned actions (correctly documented as intentional policy)
- **`ruff.toml`** as a standalone file — matches the project's config pattern. This is the only plan to get this right
- **Expanded rule set** (`F, E, W, I, UP, B, SIM`) with per-category rationale — catches real bugs (bugbear), modernizes syntax (pyupgrade), simplifies code (simplify)
- **Phase 1b fixes pyrightconfig from 3.11 → 3.12** — the only plan to address this mismatch
- **Separate lint and test CI jobs** with `needs: lint` dependency — proper fail-fast architecture. GitHub shows these as distinct checks in the PR
- **Phase 4b extends `pytest_06_warning_regression_test.py`** for the new workflow — the only plan that considers compatibility with existing test contracts
- **Phase 6 policy assessment** of `@main` pinning — thoroughly documents the tradeoff without fighting it
- **Explicit deferred items list** — smoke tests in CI, coverage, SHA pinning, Pyright expansion. Knowing what you're NOT doing is as important as knowing what you are
- **Rollback plan per phase** — practical recovery for each possible failure mode
- **File inventory and timeline** — operationally complete

**What could be stronger:**
- **Adds ruff/pyright to requirements.txt** — that file is the production runtime deps file. Phase 5 proposes mixing dev tools into it, contradicting the CI workflow which correctly installs them via `pip install ruff pyright` separately. Should use a separate `requirements-dev.txt` or just keep the explicit `pip install` in CI
- **Defers Pyright strict expansion entirely** — reasonable for scope, but a phased expansion path would be valuable even if not executed now
- **Pre-commit uses `ruff-pre-commit` with no version pin in the example** — the `rev:` field is empty in the Phase 3 YAML. v00's advice about pinning tool versions is correct here

**Verdict:** This is the only plan that could be executed as-written with minor corrections. It respects every project convention, identifies every real gap, and makes defensible tradeoff decisions.

---

## Comparative Summary Table

| Dimension | v00 | v01 | v02 |
|---|---|---|---|
| **Project awareness** | None | Medium-high | Very high |
| **Python version** | 3.11 (wrong) | 3.12 (correct) | 3.12 (correct) |
| **Config file choice** | pyproject.toml (wrong pattern) | pyproject.toml (wrong pattern) | ruff.toml (correct) |
| **Action refs** | @v4/@v5 (breaks policy) | @main (correct) | @main (correct) |
| **Line length** | 88 (narrow) | 120 (good) | 120 (good) |
| **Ruff rules** | F,E,W,I | F,E,W,I | F,E,W,I,UP,B,SIM |
| **Pyrightconfig fix** | No | No | Yes |
| **CI architecture** | Modifies non-existent ci.yml | Separate workflow, single job | Separate workflow, split lint/test jobs |
| **Pre-commit strategy** | ruff-pre-commit | LOCAL check_linting.py (fragile) | ruff-pre-commit (fast, portable) |
| **Test contract compat** | Would break pytest_06 | Compatible | Extends pytest_06 |
| **Deferred items documented** | No | No | Yes, explicit list |
| **Rollback plan** | No | No | Yes, per phase |

---

## My Recommended Architecture

If I were designing the quality upgrade for this project, I'd take v02 as the foundation and make these adjustments:

### 1. Two-phase rollout, not seven phases

**Phase A — CI gate (the real safety net).** This is the single highest-value change. Create `ci-validation.yml` with separate lint and test jobs, triggered on push and PR to main. This catches everything, regardless of whether a developer or agent has pre-commit installed. No local tooling changes required.

**Phase B — Local ergonomics.** Add `ruff.toml`, fix pyrightconfig version, create `.pre-commit-config.yaml`, baseline the codebase. This makes development faster but is not the primary safety mechanism.

Rationale: The motivating incident was an agent committing bad tabs that broke the pipeline. The agent doesn't run pre-commit hooks. Only a CI gate would have caught this. Start with the gate that actually blocks the failure mode.

### 2. Separate dev dependencies

Do NOT add ruff/pyright to requirements.txt. That file is runtime deps. Install lint tools explicitly in the CI workflow:

```yaml
- name: Install lint tools
  run: pip install ruff pyright
```

If a local `requirements-dev.txt` is desired, create one. But the CI workflow should be self-contained.

### 3. Pin ruff-pre-commit rev

v02's `.pre-commit-config.yaml` example leaves `rev:` unspecified. Pin it to the current stable release. Use `pre-commit autoupdate` on a maintenance cadence.

### 4. Pyright expansion roadmap (deferred but documented)

v02 correctly defers expanding the Pyright strict subset, but I'd add a one-line note: "When adding new lib/ modules, add them to pyrightconfig.strict.json includes. Existing untyped files are grandfathered until a typing sprint." This prevents the strict subset from falling further behind as the codebase grows.

### 5. Keep check_linting.py as the local full-suite tool

v02's instinct to NOT use check_linting.py in pre-commit is correct — it's fragile in hook environments. But check_linting.py remains the right tool for `python tests/check_linting.py` as a manual local validation command. The CI workflow should run ruff and pyright directly (not via check_linting.py) for reliability and better GitHub annotations.

---

## Concise Plan Summary: How This Project Should Catch Simple Mistakes Early

**The core problem:** An agent or developer can commit broken code and nothing stops it before the full 1360-line pipeline workflow runs and fails mid-execution.

**The fix, in priority order:**

1. **CI validation gate** (`ci-validation.yml`) — a separate workflow that runs on every push/PR to main. Two jobs: (a) lint job runs `ruff format --check`, `ruff check --output-format=github`, and `pyright`; (b) test job (depends on lint) runs `python tests/run_pytest.py`. This is the non-negotiable minimum. It would have caught the bad-tabs incident.

2. **Centralized ruff config** (`ruff.toml`) — line-length 120, target py312, rules `F, E, W, I, UP, B, SIM`, excludes tmp, data. All three tiers (IDE, hook, CI) read the same config. No format or lint ambiguity.

3. **Pyrightconfig version alignment** — change `pythonVersion` from `"3.11"` to `"3.12"` in pyrightconfig.strict.json. One-line fix, eliminates a class of false-positive/false-negative type errors.

4. **Format baseline commit** — run `ruff format .` and `ruff check --fix .` once, commit with `.git-blame-ignore-revs` entry. Everything is clean from this point forward.

5. **Pre-commit hooks** (optional but recommended) — `ruff-pre-commit` for fast local feedback. NOT check_linting.py. Developers and agents can bypass with `--no-verify` in emergencies, but the CI gate in item 1 catches anything that slips through.

Items 1-3 are the minimum viable quality gate. Items 4-5 improve the developer experience but are not the primary defense. The CI gate is what prevents regressions from reaching the pipeline.