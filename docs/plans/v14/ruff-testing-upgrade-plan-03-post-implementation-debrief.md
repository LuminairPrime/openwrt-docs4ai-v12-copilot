# Ruff & Testing Upgrade v03 Post-Implementation Debrief

Date: 2026-04-01
Status: implemented
Audience: the maintainer, future AI agents, and any future contributor who needs to understand how validation now works in this repository.

## Executive Summary

The quality-upgrade rollout is now implemented in the repository.

The key outcome is simple:

- source validation is now authoritative and automatic
- formatting drift is now checked explicitly with Ruff
- type-checking is aligned to Python 3.12
- direct pushes to `main` now hit a cheap validation gate before the expensive pipeline work begins
- local and remote validation now share one primary source-validation surface: `tests/check_linting.py`
- `summary.json` is now the first diagnostic artifact to inspect when source validation fails

This is not a broad maturity-program rollout. Deferred choices remain deferred.

This implementation intentionally did **not** add:

- a separate `ci-validation.yml` workflow
- mandatory pre-commit hooks
- broader Ruff rule expansion beyond the conservative first pass
- a tests-folder rearchitecture
- CI smoke-test expansion

## What Was Implemented

The implementation landed in five practical slices.

### 1. Conservative Ruff configuration

A new repo-level Ruff config now exists in [ruff.toml](../../../ruff.toml).

The first-pass policy is intentionally conservative:

- `target-version = "py312"`
- `line-length = 120`
- lint rules are limited to a narrow baseline instead of a broad style/bugbear sweep
- `tmp/`, `.venv/`, `.git/`, and `.specstory/` are excluded

This means the implementation solved the real incident class first: formatting drift and basic source hygiene. It did **not** bundle a second policy program on top of that.

### 2. Pyright alignment

[pyrightconfig.strict.json](../../../pyrightconfig.strict.json) now targets Python 3.12 instead of 3.11, which matches the current project and CI reality.

### 3. Local lint runner upgrade

[tests/check_linting.py](../../../tests/check_linting.py) is now the authoritative local source-validation runner.

It now performs four checks in order:

1. `ruff format --check`
2. `ruff check`
3. `pyright --project pyrightconfig.strict.json`
4. `actionlint .github/workflows/openwrt-docs4ai-00-pipeline.yml`

It also now supports a strict mode:

- normal mode: missing tools downgrade to local skips where appropriate
- `--strict` mode: missing tools are treated as failures

That strict mode is what CI now uses.

### 4. Top-of-pipeline validation gate

The main hosted workflow, [openwrt-docs4ai-00-pipeline.yml](../../../.github/workflows/openwrt-docs4ai-00-pipeline.yml), now begins with a new root job:

- `validate_source`

That job:

- checks out the repo
- sets up Python 3.12
- sets up Go for actionlint installation
- installs the validation tools
- runs `python tests/check_linting.py --strict --result-root tmp/ci/lint-review/current`
- uploads a `lint-review` artifact
- writes a step summary derived from the emitted `summary.json`

Downstream expensive jobs now wait until that gate passes.

### 5. Contract tests and docs

The workflow contract tests were updated so the new gate is not just present, but expected.

The maintainer-facing docs were also updated so future work starts from the implemented reality instead of the old plan.

Files updated for this:

- [CLAUDE.md](../../../CLAUDE.md)
- [DEVELOPMENT.md](../../../DEVELOPMENT.md)
- [tests/README.md](../../../tests/README.md)
- [tools/testing/README.md](../../../tools/testing/README.md)
- [GETTING_STARTED.md](../../GETTING_STARTED.md)

## Debrief: How The Implementation Went

The rollout went the right way because it followed the actual control path instead of the earlier abstract plan.

### What went well

- The implementation started from the existing authoritative runner, not from a new parallel validation surface.
- The new format enforcement immediately proved useful by catching repo-wide formatting drift even though Ruff lint, Pyright, and actionlint were already clean.
- The workflow contract tests were updated before the workflow graph change, which kept the pipeline wiring change grounded and falsifiable.
- The decision to use a top-of-pipeline validation job was correct for this repository’s direct-push workflow.
- The artifact-first debugging model is now much cleaner because `lint-review/summary.json` exists both locally and remotely.

### What was learned during implementation

- The repo was already lint-clean enough for a conservative Ruff rollout, but not format-clean.
- The formatting baseline was a real repo-wide event, not a cosmetic no-op.
- Contract tests catch workflow-shape regressions well, but they do not catch runtime errors inside inline Python heredocs in workflow YAML. That still needed explicit execution validation.
- The current validation architecture is now coherent, but the `tests/` tree still reflects historical growth rather than ideal taxonomy.

### What remains intentionally imperfect

- The first-pass Ruff ruleset is intentionally narrow.
- `tests/check_linting.py` still validates only the main workflow file, not every hypothetical future workflow.
- The `tests/` tree still mixes runnable validation surfaces, support code, and historical material.
- `.git-blame-ignore-revs` is scaffolded but still needs the actual formatting-baseline commit hash after commit time.

That is acceptable. The current state is better because it solves the original operational problem without widening scope into unrelated cleanup.

## Current Validation Model

This repository now has a clear validation model.

### Local validation

Local validation is the first stop.

Use the canonical wrappers under [tools/testing](../../../tools/testing):

- [tools/testing/run_default_validation.py](../../../tools/testing/run_default_validation.py)
- [tools/testing/run_source_validation.py](../../../tools/testing/run_source_validation.py)
- [tools/testing/run_targeted_pytest.py](../../../tools/testing/run_targeted_pytest.py)
- [tools/testing/run_targeted_smoke.py](../../../tools/testing/run_targeted_smoke.py)

These delegate to the maintained implementation-level runners under [tests](../../../tests) and write durable result bundles under `tmp/ci/`.

### Remote validation

Remote validation is confirmation, not the first debugger.

The hosted workflow now starts with `validate_source`, which is the authoritative source gate for direct pushes and manual dispatches.

If `validate_source` fails remotely:

1. download the `lint-review` artifact
2. inspect `summary.json`
3. only then move on to raw logs

### Source of truth for source validation

The source-validation source of truth is now:

- local operator command: `python tools/testing/run_source_validation.py`
- implementation source of truth: `python tests/check_linting.py --strict`
- hosted gate: `validate_source` in the main workflow

Those three are intentionally aligned.

## Empirical Timing Snapshot

The runner policy should follow measured cost, not intuition.

On 2026-04-01, every maintained executable surface was run individually from the workspace root using the repo virtual environment. All passed.

Measurement artifacts:

- per-file timings: `tmp/ci/manual-test-file-timings/20260401-093649/summary.json`
- runner timings: `tmp/ci/manual-runner-timings/20260401-093837/summary.json`

### Category totals

| Surface | Count | Total Seconds |
|---|---:|---:|
| `tests/check_linting.py --strict` | 1 | 4.999 |
| all maintained pytest files | 13 | 22.593 |
| all smoke files | 3 | 5.948 |
| all individually measured executable surfaces | 17 | 33.540 |

### Maintained runner timings

| Runner | Seconds |
|---|---:|
| `python tests/run_pytest.py` | 10.524 |
| `python tests/run_smoke.py` | 6.319 |
| `python tests/run_smoke_and_pytest.py` | 15.517 |
| `python tests/run_smoke_and_pytest_parallel.py` | 10.053 |

### Interpretation

The key conclusion is simple:

- these tests are not expensive enough to justify a complicated daily decision tree
- the default local policy should be to run almost everything
- focused commands still matter, but mainly for diagnosis and iteration, not for routine pre-push decisionmaking

## User Manual: Default First, Focused Second

This section is the practical operator guide.

### Default local proof for normal work

For normal changes, the default should be:

```powershell
python tools/testing/run_default_validation.py
```

Measured combined cost remains about 20.5 seconds because the wrapper delegates
to the same underlying maintained runners.

That is cheap enough that it should be the normal maintainer and agent path for most changes.

### Focused proof only when you are isolating a problem

Use the narrower commands only when you are intentionally debugging one slice.

#### Source gate only

```powershell
python tools/testing/run_source_validation.py
```

Use this when you are working only on:

- formatting and lint config
- Pyright scope or typing changes
- workflow YAML or validation-gate behavior

#### Focused pytest only

```powershell
python tools/testing/run_targeted_pytest.py
```

Or narrower still:

```powershell
python tools/testing/run_targeted_pytest.py tests/pytest/pytest_01_workflow_contract_test.py -q
```

Use this when you are iterating on one focused suite and want quick failure isolation.

#### Smoke only

```powershell
python tools/testing/run_targeted_smoke.py
```

Use this when you are isolating smoke-only behavior and do not need the focused pytest layer in that iteration loop.

#### Parallel combined runner

```powershell
python tests/run_smoke_and_pytest_parallel.py
```

This is a supported implementation detail, not the primary human-facing default.

Use it only when you specifically want the split-lane behavior. It should not be the default documented path because additional runner choices increase the chance that future agents pick the wrong one.

## Dos And Don’ts

### Do

- do default to `python tools/testing/run_default_validation.py` for most real work
- do use the narrower commands only when you are intentionally isolating a failure
- do inspect `tmp/ci/.../summary.json` before scrolling through terminal output when a maintained runner fails
- do inspect the `lint-review` artifact first when `validate_source` fails remotely
- do treat `validate_source` as the authoritative remote source gate
- do keep the public runner guidance small enough that future AI agents can follow it without choosing from too many permutations
- do keep the deferred items deferred unless a new plan explicitly widens scope

### Don’t

- don’t skip local validation and rely on GitHub Actions as your first debugger
- don’t present every supported command as if it were equally recommended for daily use
- don’t expand the documented runner menu unless the extra choice clearly earns its keep
- don’t inspect raw CI logs before reading the structured artifacts
- don’t widen the Ruff policy casually just because the first rollout passed
- don’t mix a `tests/` tree cleanup into unrelated source-validation fixes unless you deliberately open a new cleanup tranche

## Which Tests Should A User Or Agent Run, And Why?

This is the simplified routing guidance.

### Normal case

Run:

```powershell
python tools/testing/run_default_validation.py
```

Why:

- this is still cheap enough to run routinely
- it minimizes decision overhead for humans and agents
- it covers the source gate plus the maintained combined local runner

### Lint and workflow-gate diagnosis only

Run:

```powershell
python tools/testing/run_source_validation.py
```

Why:

- this isolates the source-validation layer
- this is the right first slice when the failure is clearly in formatting, typing, or workflow validation

### Single focused pytest diagnosis

Run:

```powershell
python tools/testing/run_targeted_pytest.py tests/pytest/<target_file>.py -q
```

Why:

- this is for active debugging of one maintained focused suite
- it is not the recommended default for routine validation anymore

### Smoke-only diagnosis

Run:

```powershell
python tools/testing/run_targeted_smoke.py
```

Why:

- this isolates smoke behavior when you already know the focused pytest layer is not the question

### If you need hosted confirmation

Push or dispatch the workflow, then:

1. pin the run to the exact commit SHA
2. wait on that exact run
3. inspect `lint-review`
4. inspect `pipeline-summary` and `extract-summary`
5. only then inspect raw logs

## Are There Multiple Redundant Ways To Execute Validation?

Yes, but the important distinction is between **supported choice** and **accidental redundancy**.

### The supported entry points

There are several supported entry points by design:

- `tests/check_linting.py`
- `tests/run_pytest.py`
- `tests/run_smoke.py`
- `tests/run_smoke_and_pytest.py`
- `tests/run_smoke_and_pytest_parallel.py`
- the hosted `validate_source` job
- the hosted main pipeline run

### Why this is not pure duplication

They answer different questions:

- `check_linting.py`: is the source tree hygienic and workflow-safe?
- `run_pytest.py`: do the maintained focused suites pass?
- `run_smoke.py`: does the local pipeline behavior hold?
- `run_smoke_and_pytest.py`: does the maintained sequential local validation path pass end to end?
- `run_smoke_and_pytest_parallel.py`: can the supported split-lane local validation run safely?
- `validate_source`: can the source tree pass the authoritative remote gate?
- full hosted workflow: does the real remote pipeline complete?

So there are multiple ways in, but they are not interchangeable.

### Where redundancy really exists

The current mild redundancy is mostly human-facing:

- a user can enter validation via separate commands or the combined sequential runner
- a user can run `check_linting.py` in normal or strict mode
- smoke can be entered directly or as part of the combined runner

That is acceptable internally, but it should not drive the public operator guidance.

The better rule is:

- keep the implementation surface flexible enough for maintenance work
- keep the documented default surface very small

In practice, that means most humans and agents should see only:

- `tools/testing/run_default_validation.py`
- `tools/testing/run_source_validation.py`

Everything else is a diagnostic or maintainer-oriented branch.

## Local Pipeline vs Remote Pipeline

### Local pipeline

Local execution uses the maintained Python runners under `tests/`.

These runners:

- use the repo interpreter
- write bundles under `tmp/ci/`
- preserve small, durable JSON summaries
- are intended to be cheap, readable, and repeatable

Local execution is where debugging should normally begin.

### Remote pipeline

Remote execution uses the hosted GitHub Actions workflow.

The current remote structure is:

1. `validate_source`
2. `initialize`, `extract_wiki`, and `extract_cookbook` after the gate
3. clone-gated extraction matrix through `extract`
4. `extract_summary`
5. `process`
6. `deploy`
7. `pipeline_summary`

Remote execution is not a replacement for local proof. It is confirmation that the hosted environment still behaves correctly.

## Dependency Model: What Must Run Before What?

There are two dependency models to understand.

### 1. Source-validation dependency model

The new top-level source gate is upstream of the heavy workflow.

That means:

- if `validate_source` fails, expensive pipeline work should not start
- this is the main operational improvement of the rollout

### 2. Local runner dependency model

The local runners are intentionally layered.

- `run_pytest.py` is independent and cheap
- `run_smoke.py` runs its selected smoke stages serially
- `run_smoke_and_pytest.py` is explicitly ordered: pytest first, then smoke
- `run_smoke_and_pytest_parallel.py` only supports one pytest lane plus one smoke lane

Inside the smoke lane, order still matters.

Do not assume you can arbitrarily reorder smoke stages and get the same meaning.

## Result Bundles And Artifact Triage

The JSON summaries are now part of the operational contract.

### Local bundle roots

- `tmp/ci/pytest/<timestamp>/`
- `tmp/ci/smoke/<timestamp>/`
- `tmp/ci/local-validation/<timestamp>/`
- `tmp/ci/local-validation-parallel/<timestamp>/`
- `tmp/ci/lint-review/<timestamp>/`

### Remote source-validation bundle root

- `tmp/ci/lint-review/current/` inside the hosted workflow artifact

### First artifact to inspect

If source validation fails, inspect:

- `summary.json`

before raw stdout/stderr logs.

This is true both locally and remotely.

## Future Operating Guidance

This is how the repository should be operated going forward.

### Normal workflow for the maintainer

For small source-only changes:

```powershell
python tools/testing/run_source_validation.py
python tools/testing/run_targeted_pytest.py
```

For non-trivial changes:

```powershell
python tools/testing/run_default_validation.py
```

Then push.

### Normal workflow for future agents

Agents should:

1. prefer the smallest proof first
2. use maintained runners instead of ad hoc terminal chains
3. inspect `summary.json` before scraping console output
4. treat the hosted workflow as confirmation after local proof, not as the first debugger

### What should happen next, but not yet

These are sensible next-phase ideas, but they remain out of scope for this rollout:

- a second Ruff-policy expansion
- richer `summary.json` metadata if future AI triage needs more context
- optional pre-commit ergonomics
- broader workflow lint coverage if more workflows are added
- cleanup of the `tests/` folder structure

## Fleshed-Out Future Refactor For The Tests Folder

Only the `tools/testing/` operator surface from this section is now implemented.
The rest is still future-facing and does **not** mean the remaining refactor should happen immediately.

### Current situation

The current [tests](../../../tests) tree is functional, but it mixes multiple concerns in one surface:

- runnable entrypoints
- runnable suites
- orchestration support code
- committed artifacts
- historical planning material

Current top-level shape:

- `tests/pytest/`
- `tests/smoke/`
- `tests/support/`
- `tests/sample-inputs/`
- `tests/artifacts/`
- `tests/proposals/`
- root-level runner scripts

### Why a future refactor is justified

The current tree works, but it is harder to scan than it should be.

The biggest structural issues are:

1. `pytest/` is tool-named rather than intent-named.
2. numeric filenames encode order and identity at the same time.
3. root-level operational runner CLIs live beside test code.
4. non-executable material lives inside the active test surface.

### Recommended future target shape

If the repo opens a deliberate cleanup tranche later, the target should be closer to this:

```text
tests/
  contracts/
  integration/
  unit/
  smoke/
  fixtures/
  support/
tools/
  testing/
docs/
  testing/
  archive/testing/
```

Important clarification:

- this is **not** a proposal to move the canonical project test suite into `tools/`
- the canonical suites should stay under `tests/`
- `tools/testing/` would exist only for operator-facing runner and orchestration CLIs
- if `tools/testing/` ever grows into a real subsystem, its own tests could live adjacent to it under something like `tools/testing/tests/`

That is the distinction that matters.

### Proposed category meanings

#### `tests/unit/`

Fast, pure logic tests.

Use for:

- helper modules
- pure transformation logic
- local utility behavior

#### `tests/contracts/`

Contract and policy tests.

Use for:

- workflow-shape assertions
- release-tree contract checks
- warning-regression tests
- contract behavior that future agents must not accidentally break

This repo has many contract-style tests, so this folder would likely become the most important one.

#### `tests/integration/`

Fixture-backed integration tests.

Use for:

- partial pipeline slices
- test cases that exercise multiple components together
- pipeline interactions that are narrower than smoke, but broader than unit tests

#### `tests/smoke/`

Keep this concept.

The smoke lane is already a good abstraction and should stay explicit.

#### `tests/fixtures/`

This would be a clearer evolution of `sample-inputs/`.

Use for:

- committed repro fixtures
- minimal input trees
- deterministic support files for integration and smoke tests

#### `tests/support/`

Keep this concept too.

The current support layer is valid. The repo is orchestration-heavy, and centralizing runner logic is the right design.

#### `tools/testing/`

If a cleanup tranche happens, the runner CLIs should likely move here:

- `run_pytest.py`
- `run_smoke.py`
- `run_smoke_and_pytest.py`
- `run_smoke_and_pytest_parallel.py`
- possibly `check_linting.py`

Why:

- these are operational entrypoints, not test modules
- they behave more like maintainer tools than suites
- their value would be clearer policy, clearer documentation, and less decision sprawl for humans and agents, not raw runtime savings

This should be read narrowly.

It means:

- move the driver commands here
- keep smoke, contract, integration, and fixture content under `tests/`
- do **not** create a second general-purpose project test tree under `tools/`

### What noteworthy projects actually do

Looking at mature GitHub projects, the common pattern is separation of **test content** from **test drivers**.

Examples:

- Node.js keeps the main suites under `test/`, but uses a large runner/orchestrator in `tools/test.py`.
- Kubernetes keeps executable test content under `test/`, but uses `hack/verify-*.sh`, `hack/test-go.sh`, and related maintainer scripts outside the test tree.
- CPython keeps the standard-library suite under `Lib/test`, while `Tools/README` explicitly documents helper scripts including `Tools/scripts/run_tests.py`.
- Django is the main counterexample here: it keeps `tests/runtests.py` inside `tests/`, which works because that runner is tightly coupled to the suite and to contributor workflow.
- pandas keeps its main library tests in `pandas/tests`, but also has `scripts/tests` specifically for testing the `scripts/` subsystem itself.

The important conclusion is that mature repos do both patterns, but with a boundary:

- project tests stay in the canonical test tree
- orchestration and maintainer automation often lives in `tools/`, `scripts/`, or `hack/`
- tests for the tooling itself can be colocated with that tooling

That is the best-practice version of the idea, and it is narrower than "move tests into tools."

#### `docs/testing/` and `docs/archive/testing/`

Move historical proposals and planning notes out of the active test surface.

That includes material like:

- `tests/proposals/`
- historical test plans
- committed investigation notes that are not part of executable validation

### Naming changes worth making in a future cleanup

The current numbering scheme is useful but overloaded.

For a future cleanup, prefer names that encode intent first.

Examples:

- `pytest_01_workflow_contract_test.py` -> `workflow_contract_test.py`
- `pytest_06_warning_regression_test.py` -> `workflow_warning_regression_test.py`
- `pytest_09_release_tree_contract_test.py` -> `release_tree_contract_test.py`

If order matters, encode order in the runner or in a curated test list, not in every filename.

### How would users and agents know what to run after a refactor?

The answer should become even clearer after cleanup:

- `unit/` means cheapest proof
- `contracts/` means policy and repo-shape proof
- `integration/` means wider fixture-backed proof
- `smoke/` means end-to-end local proof
- `tools/testing/` means operator entrypoints, not a second home for the project test suite

That would make the test surface easier to navigate for both humans and agents.

## Final State Assessment

The implementation succeeded.

It did not solve every quality problem in the repository. It solved the right one first.

The repository is now in a better operational state because:

- formatting drift is checked explicitly
- source validation is authoritative in the hosted workflow
- local and remote source validation share one main control surface
- artifact-first debugging is clearer
- the docs now describe the implemented reality

The future should build on this in small deliberate tranches, not by reopening the entire testing architecture all at once.

That is the correct outcome for this project profile.