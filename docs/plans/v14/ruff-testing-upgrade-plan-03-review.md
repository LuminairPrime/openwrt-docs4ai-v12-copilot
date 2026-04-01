# Ruff & Testing Upgrade Plans Review

Date: 2026-04-01
Scope: adversarial review of v03, delta scan of v00-v02, and right-sizing assessment for a solo Windows-based pipeline project.

## Repo-grounded starting point

These observations are from the current repo state, not from the plans:

- `tests/check_linting.py` currently runs Ruff check, Pyright, and actionlint only. It does not run `ruff format --check`, and it only lint-targets `.github/scripts`, `lib`, and `tests`.
- `pyrightconfig.strict.json` still targets Python 3.11 even though CI and project docs target Python 3.12.
- `tests/README.md` still describes `tests/check_linting.py` as a Ruff, Pyright, and actionlint runner only.
- `.github/workflows/openwrt-docs4ai-00-pipeline.yml` runs on push to `main`, schedule, and manual dispatch, and uses the repo's intentional `@main` action-ref policy.
- There is currently no `ruff.toml`, no `.pre-commit-config.yaml`, and no dedicated validation workflow.

## Adversarial Review Of v03

### Overall assessment

v03 is the strongest draft by a wide margin. It is the first plan that is actually grounded in this repository's real conventions instead of generic Python-project boilerplate. That said, it still overstates how safely it can be rolled out and it hides one major architectural weakness:

- The biggest hidden flaw is that a separate `ci-validation.yml` does not actually prevent the main pipeline from running on a direct push to `main`. The current data pipeline still triggers on push. If the lone developer pushes broken code directly to `main`, both workflows will run, and compute waste still happens.
- The biggest rollout flaw is that Phase A is presented as independent from Phase B, but Phase A also introduces a stricter Ruff ruleset. If the repository is not already compliant with `UP`, `B`, and `SIM`, the new validation gate can go red before the baseline cleanup lands.
- The biggest strength is that v03 finally separates real protection from ergonomics: CI first, local hooks second.

### 1. Problem Statement

What v03 gets right:

- The motivating incident is concrete and correctly tied to a missing enforcement layer.
- It identifies the real repo gaps instead of inventing fake ones.
- It correctly treats the existing test tools as useful but advisory-only.

Adversarial criticism:

- The statement implies the plan will stop bad code before CI pipeline execution. That is only true for pull requests with enforced branch protection. It is not true for direct pushes to `main`, which this repository already uses.
- The severity framing is mostly right, but it understates that the current failure mode is not just "bad code wastes compute". It also wastes operator attention because the primary pipeline is the wrong place to discover formatting errors.
- The problem statement should explicitly say whether the expected workflow is PR-based or direct-push-based. That choice determines whether a separate validation workflow is sufficient.

### 2. Architecture: Two-Phase Rollout

What v03 gets right:

- Separating "real safety" from "local convenience" is the correct mental model.
- Starting with CI is the right instinct for an AI-assisted codebase, because agents often bypass or ignore local hook machinery.

Adversarial criticism:

- The phases are not truly independent. Phase A introduces stricter Ruff rules, so it can require the Phase B baseline before it can pass cleanly.
- If the real project workflow is direct pushes to `main`, then a separate CI validation workflow is not enough. The simplest hard gate for that workflow is a cheap lint step at the top of the existing data pipeline or a `workflow_run` dependency from the pipeline onto validation.
- The plan should be explicit that Phase A is only a true gate if branch protection exists and the developer actually merges through PRs.

### 3. Design Decisions

#### 3.1 `ruff.toml`, not `pyproject.toml`

What v03 gets right:

- This matches the project's existing pattern of standalone tool config files.
- It avoids introducing a project-wide config file only to hold one tool section.

Adversarial criticism:

- This is correct, but the plan treats it as a major decision when it is really just a compatibility choice. The important decision is the ruleset and rollout strategy, not the file container.
- The exclusion list should be verified against the real tree. For example, the repo guidance talks about `static/data/base/`; the plan uses `static/data`. That is probably fine, but it should be called out as intentional broad exclusion.

#### 3.2 Separate `ci-validation.yml`, not injected into the data pipeline

What v03 gets right:

- It keeps the huge production workflow cleaner.
- It makes PR feedback faster and easier to understand.
- It reduces coupling in workflow YAML.

Adversarial criticism:

- Clean separation is not the same as actual enforcement. On direct pushes to `main`, this design still allows the heavy pipeline to start before validation has blocked anything.
- For a modest solo-maintained project, the extra workflow may add status noise without providing stronger protection than a top-of-pipeline lint job.
- If the plan keeps a separate validation workflow, it should also define how it becomes authoritative: branch protection, no direct pushes, or pipeline trigger changes.

#### 3.3 `ruff-pre-commit` for Tier 2, not `check_linting.py`

What v03 gets right:

- This is the correct local-hook choice for Windows portability.
- It avoids PATH and toolchain fragility around Pyright and actionlint.

Adversarial criticism:

- The plan is right to do this, but it should be more blunt: local hooks are convenience only. They are not a trustworthy guardrail for AI agent edits.
- If the lone developer finds hooks annoying and frequently bypasses them, the project should not pretend Tier 2 is meaningful. In that environment, Tier 1 and Tier 3 do the real work.

#### 3.4 `@main` action refs

What v03 gets right:

- It accurately reflects repository policy.
- It does not try to smuggle in a security-policy change under the banner of linting work.

Adversarial criticism:

- This quality plan knowingly inherits volatility from upstream GitHub Actions HEAD. That is defensible only because the repository already chose that tradeoff.
- The plan should say more clearly: this work improves Python code quality, but it does nothing to improve action-supply-chain stability.

#### 3.5 Runtime vs dev dependencies

What v03 gets right:

- This is one of the strongest corrections versus older drafts. It keeps dev tools out of runtime requirements.
- Installing Ruff and Pyright explicitly in CI is cleaner than polluting runtime dependency manifests.

Adversarial criticism:

- The plan still needs a canonical local bootstrap story. If CI is the only place that explicitly installs Ruff and Pyright, local setup can drift unless the docs are sharp and short.
- A lone developer may value one repeatable local bootstrap command over ideological purity about dev dependency files.

#### 3.6 `check_linting.py` update scope

What v03 gets right:

- Adding `ruff format --check` to the local lint runner is directly responsive to the motivating incident.
- The rationale for keeping a manual full-suite runner is good.

Adversarial criticism:

- Adding `tools/` broadens policy scope, not just parity. That may be a good idea, but it is still a scope increase hidden inside a tooling cleanup.
- The plan still leaves `check_linting.py` validating only the main pipeline workflow via actionlint. The new `ci-validation.yml` workflow is not covered there.

#### 3.7 Expanded Ruff rule set

What v03 gets right:

- `UP`, `B`, and `SIM` are good long-term rules for this codebase.
- The rationale table is well argued and not cargo-culted.

Adversarial criticism:

- This is too much for the first gate if the main goal is "catch obvious formatting and syntax mistakes early".
- The incident only proves the need for `ruff format --check` plus a stable baseline of `F/E/W/I`. The plan is using the same rollout to also tighten broader style and bug-detection policy.
- That makes the implementation riskier than necessary. The clean rollout would be: first add format check plus current lint behavior, then expand rules after the baseline is known-good.

### 4. Implementation: Phase A — CI Validation Gate

#### Step A1: Create `ruff.toml`

What v03 gets right:

- `line-length = 120` is realistic for this repo.
- `target-version = "py312"` matches actual project reality.
- The exclusions are directionally correct.

Adversarial criticism:

- The selected ruleset likely makes this more than a "config file creation" step. It is functionally a policy change.
- The plan assumes the repository can immediately pass `ruff check --config ruff.toml .`. That assumption should be proved before this is presented as a Phase A activity.

#### Step A2: Align Pyright Python version

What v03 gets right:

- This is obvious, cheap, and correct.

Adversarial criticism:

- None at the conceptual level. This should happen no matter what else is adopted.

#### Step A3: Create `ci-validation.yml`

What v03 gets right:

- Split lint and test jobs with `needs: lint` is the best CI structure in any of the drafts.
- `ruff check --output-format=github` is the right developer experience choice.
- Installing runtime deps before Pyright is sensible when the typed modules import those packages.

Adversarial criticism:

- The promised timings are optimistic. With fresh dependency installs on GitHub-hosted runners, sub-60-second lint feedback is plausible but not guaranteed.
- Triggering only on pull requests and pushes to `main` means feature-branch pushes still get no validation signal unless the developer opens a PR.
- The workflow does not validate itself. Because actionlint is intentionally omitted from CI, a broken `ci-validation.yml` can fail in a low-signal way.
- The plan explicitly says a red validation workflow on the same commit is "immediate signal" even though the heavy pipeline will still run on push to `main`. That is signal, not prevention.

#### Step A4: Extend workflow contract test

What v03 gets right:

- Extending the existing contract-test pattern is the right repo-native move.

Adversarial criticism:

- This is text matching, not YAML validation.
- It checks policy shape, not syntax correctness.
- It should not be the only protection around the new workflow file.

#### Step A5: Verify Phase A

What v03 gets right:

- It uses small proof-first commands.
- It reuses existing local runners.

Adversarial criticism:

- This verification order can fail for avoidable reasons if the broader Ruff rules are not yet baselined.
- `python tests/check_linting.py` in Phase A does not verify the newly proposed format enforcement because the `check_linting.py` changes do not land until Phase B.
- The phase is called implementation-ready, but the verification story still assumes current cleanliness it has not yet established.

### 5. Implementation: Phase B — Local Ergonomics

#### Step B1: Baseline format commit

What v03 gets right:

- Isolating the bulk rewrite is correct.
- Mentioning `git blame` hygiene is correct.
- Warning that tests must run before commit is correct.

Adversarial criticism:

- `ruff check --fix` with the proposed rule set is not purely mechanical. It can change imports, syntax forms, and simplifications in ways that are adjacent to logic.
- If the repository is only infrequently touched, a full-repo autofix may be more churn than value.
- A safer rollout would be format-only first, then a smaller second pass for clearly safe lint fixes.

#### Step B2: Create `.git-blame-ignore-revs`

What v03 gets right:

- This is the right follow-through to a baseline rewrite.

Adversarial criticism:

- The instructions assume a single baseline hash, then later also mention splitting the baseline into multiple commits. The file example should show the multi-hash case explicitly.

#### Step B3: Update `check_linting.py`

What v03 gets right:

- This is probably the single highest-value local change after the Pyright version fix.
- Bringing `ruff format --check` into the existing runner matches how this repo already works.

Adversarial criticism:

- It still actionlints only the main pipeline workflow, not the new validation workflow.
- It silently broadens the lint surface to `tools/`. That is good if intentional, but it is not just a mechanical parity change.

#### Step B4: Create `.pre-commit-config.yaml`

What v03 gets right:

- Pinned hook revisions are correct.
- The chosen hooks are pragmatic and low-noise.

Adversarial criticism:

- For a lone developer who works infrequently and uses AI tools, mandatory installed hooks can create more friction than value.
- This should probably be framed as recommended local ergonomics, not mandatory project policy.

#### Step B5: Verify Phase B

What v03 gets right:

- It re-runs the meaningful local surfaces.

Adversarial criticism:

- `python tests/run_smoke_and_pytest.py` is probably too heavy for a tooling-only change in a modest project.
- For this repo size and usage pattern, `run_pytest.py` plus `check_linting.py` is usually enough after lint-tooling edits unless the baseline rewrite was very broad.

### 6. Relationship Between Tools After Implementation

What v03 gets right:

- The three-tier explanation is clear.
- It preserves the current role of `check_linting.py` as a manual full-validation entry point.

Adversarial criticism:

- The IDE tier is weaker than the document implies in an AI-assisted workflow. Agents do not reliably inherit extension behavior or format-on-save settings.
- The local hook tier is also weaker than presented because it is trivially bypassed.
- There is still divergence between CI and `check_linting.py`: local runs would include actionlint, CI would not.

### 7. Documentation Updates

What v03 gets right:

- It is consistent about updating the maintainer docs.

Adversarial criticism:

- For a modest solo project, this may be too much documentation churn for too little operational value.
- The highest-value docs are probably `CLAUDE.md` and `tests/README.md`. Updating `DEVELOPMENT.md` is nice, but not essential unless that file is actively used as the real maintainer entry point.

### 8. Deferred Items

What v03 gets right:

- This section is excellent. It clearly defines what the plan will not attempt.
- Deferring smoke tests in CI is the right call.
- Deferring coverage work is reasonable.

Adversarial criticism:

- Deferring actionlint in CI is more debatable than the plan suggests. Validating the validation workflow is cheap insurance.
- The plan correctly defers Pyright strict expansion, but it should still leave one sentence of forward guidance so the strict subset does not stagnate.

### 9. Rollback Plan

What v03 gets right:

- This is practical and grounded.

Adversarial criticism:

- It is missing a social/operational rollback: if the new validation workflow creates duplicate-noise fatigue on every push, the fastest rollback may be disabling its push trigger before changing anything else.
- The note about `summary.json` consumers assumes there are position-indexing consumers. That may be true, but the plan does not identify one.

### 10. File Inventory

What v03 gets right:

- This is complete and operationally useful.

Adversarial criticism:

- The inventory makes the baseline rewrite sound like a bounded change even though it can touch a large portion of the Python tree.
- For a solo developer, it would be helpful to call out which files are "surgical" versus which step is the intentionally large churn event.

### 11. Execution Checklist

What v03 gets right:

- This is a genuinely usable implementation checklist.

Adversarial criticism:

- The phase boundaries are still slightly too coarse because the expanded rule set and baseline rewrite can force iteration inside Phase A.
- The checklist should probably include one explicit decision gate: "If direct pushes to main remain normal, either add a cheap lint pre-step to the existing pipeline or change the branching workflow." Right now that core architectural choice is still implied rather than decided.

## Good Ideas In Older Drafts That v03 Still Does Not Capture

These are the older-draft ideas that are still worth carrying forward because they are not fully present in v03:

- Treat `summary.json` bundles as the first-class machine-readable artifact for agents after a failed local run. v01 explains this well: agents should inspect the newest bundle under `tmp/ci/...` instead of scraping console output. v03 mentions artifact upload, but it does not explicitly operationalize `summary.json` as the primary debugging surface.
- Validate the new workflow file itself, not just the existing main pipeline workflow. Older drafts were stronger on explicitly actionlinting the new validation workflow or at least verifying it separately. v03 extends a text-based contract test but still leaves `ci-validation.yml` outside the local actionlint target.
- Make the IDE tier actionable, not just conceptual. Older drafts were more explicit about recommending Ruff plus Pyright extensions and format-on-save. v03 has the architecture table, but not the short concrete setup note that makes Tier 1 real for a human maintainer.

## Are These Plans Out Of Scope For A Modest Solo Pipeline Project?

### Short answer

Yes, parts of them are out of scope. Not the core quality goal, but the full architecture.

### What is in scope

These items are absolutely in scope, even for a modest pipeline project run infrequently by one developer on Windows with AI IDE tools:

- Add `ruff format --check` somewhere authoritative.
- Fix `pyrightconfig.strict.json` from Python 3.11 to 3.12.
- Add a real Ruff config file so tool behavior stops drifting.
- Keep `python tests/check_linting.py` as a first-class local command.

These are cheap, concrete, and directly connected to the motivating failure.

### What is borderline

These items are useful, but only if they match how the developer actually works:

- A separate `ci-validation.yml` workflow is worth it if work flows through pull requests and branch protection. If the developer mostly pushes directly to `main`, a separate workflow is weaker than it looks.
- Pre-commit hooks are useful if the developer wants that friction. They are optional ergonomics, not core safety, in a one-developer AI-assisted project.
- A full baseline auto-fix sweep is worth doing once if the repository is actively maintained. If the repository changes rarely, a smaller "only touch what you edit" policy may be more practical.

### What is probably out of scope or overbuilt

For this specific project profile, these parts feel heavier than necessary:

- Treating the repo like a multi-developer platform with strong assumptions about PR gating, hook adoption, and three-tier enforcement culture.
- A broad initial Ruff ruleset expansion (`UP`, `B`, `SIM`) bundled into the same rollout as the incident-driven formatting fix.
- Running the full smoke-plus-pytest combined validation after every tooling adjustment.
- Large documentation updates across multiple maintainer files if only one person really uses the repo.

### The right-sized version for this project

If I were right-sizing this for one infrequent solo maintainer using AI IDE tools on Windows, I would simplify the target state to this:

1. Create `ruff.toml` with a conservative first-pass ruleset: start with `F`, `E`, `W`, `I`, plus formatting.
2. Update `pyrightconfig.strict.json` to Python 3.12 immediately.
3. Update `tests/check_linting.py` to add `ruff format --check`.
4. Decide between these two enforcement models based on actual workflow:
   - If the maintainer uses pull requests: create `ci-validation.yml`.
   - If the maintainer mostly pushes directly to `main`: put a cheap lint-and-type gate at the top of the existing pipeline workflow instead of relying on a separate validation workflow.
5. Make pre-commit optional. Document it, but do not treat it as the main safety mechanism.
6. Defer broader Ruff rule tightening until after the simple format/syntax gate has already paid off.

That version is modest, cheap, and directly aligned with the actual failure that triggered these plans.

### Bottom line

- v00 is mostly out of scope because it is generic boilerplate and would fight the repo.
- v01 has useful project awareness but still carries too much framework energy for a solo-maintained pipeline.
- v02 and v03 are mostly in scope, but only after trimming the rollout so the first change is "catch broken formatting and type drift" rather than "adopt a full maturity model."

The project does need a quality upgrade. It probably does not need the full ceremony of a three-tier platform-quality program unless the working style also changes to PR-first, branch-protected development.
