# Plan 006 Addendum: Explicit Run Directory Contract

**Status:** Proposed
**Date:** 2026-03-28
**Applies to:** `pipeline-folder-refactor-00.md`, `pipeline-folder-refactor-01.md`

---

## Review Summary

`pipeline-folder-refactor-01.md` is stronger than `pipeline-folder-refactor-00.md` on implementation discipline. It correctly tightens the no-import-time-side-effects rule, removes the unnecessary local promotion idea, keeps the stage 07 and stage 08 cleanup concrete, and makes the symlink fix/test work item explicit.

However, plan 01 still stops short of the user's stated architectural goal: one clearly named pipeline run root with an explicit, low-ambiguity folder contract. It also rejects automatic test discovery in a way that conflicts with the requested workflow.

This addendum records the corrections that should be made before implementation starts.

---

## Keep From Plan 01

- Keep the decision to remove `PUBLISH_DIR` and stop promoting `$OUTDIR` to a second workspace location.
- Keep the decision to avoid creating directories at import time.
- Keep the stage 07 display-prefix cleanup.
- Keep the stage 08 validation cleanup.
- Keep the symlink-deletion fix and regression test.
- Keep the documentation-update phase.

## Replace From Plan 01

- Replace the ambiguous two-node layout (`input/` plus a broad `output/`) with a more explicit run-tree contract.
- Replace the "do not add auto-discovery" test position.
- Replace the acceptance of same-second local directory collisions.
- Replace the duplicated `L1-raw` and `L2-semantic` placement under both authoritative and publish roots with explicit naming for inspection copies.

---

## Required Architectural Corrections

### 1. Make the run root first-class

The plan should name the per-run root explicitly and treat it as the top-level pipeline working folder.

Recommended term:

- `PIPELINE_RUN_DIR` = the single writable root for one local or CI run

Keep compatibility names for existing code:

- `WORKDIR` = authoritative working input tree under `PIPELINE_RUN_DIR`
- `OUTDIR` = publishable output root under `PIPELINE_RUN_DIR`

This is more logical than making `WORKDIR` itself equal to `input/` while leaving the actual run root unnamed.

### 2. Use a unique run id, not timestamp-only

Plan 01 accepts collisions when two local runs start in the same second. That is not acceptable if the goal is "fresh run folder with no ambiguity."

Required format:

```text
pipeline-YYYYMMDD-HHMMSSz-<shortid>
```

Examples:

```text
pipeline-20260328-142455z-7f3c
pipeline-20260328-142455z-a19d
```

The suffix can be a short random hex string, PID-plus-counter, or UUID fragment. The critical point is: two local runs must not collide.

### 3. Separate publishable output from inspection, logs, temp, and packaged deliverables

The current plan still leaves too much implicit under `output/`. If the project goal is a rational and explicit pipeline filesystem, the tree should spell out what is publishable versus what is only diagnostic or temporary.

### 4. Add a machine-readable current-run pointer

Tests should not require manual `OUTDIR` export for the default local path. The pipeline should write a small JSON pointer so helpers can resolve the active run deterministically.

Windows makes symlink-based "latest" pointers less attractive. A JSON pointer is simpler and more robust.

---

## Recommended Explicit Directory Contract

This should replace the current target-layout section in plan 01.

```text
tmp/
  current-run.json                      # mutable pointer to the most recent local run
  pipeline-ci/                          # fixed CI run root on clean runners
    run.json
    input/                              # authoritative working tree (WORKDIR)
      repos/
        repo-ucode/
        repo-luci/
        repo-openwrt/
      cache/
      L1-raw/
      L2-semantic/
      manifests/
        repo-manifest.json
        cross-link-registry.json
    output/
      publish/                          # publishable/generated root (OUTDIR)
        release-tree/
        support-tree/
        llms.txt
        llms-full.txt
        AGENTS.md
        README.md
        index.html
        repo-manifest.json
        cross-link-registry.json
        {module}/
          llms.txt
        CHANGES.md
        changelog.json
        signature-inventory.json
      inspection/                       # non-publish inspection copies only
        L1-raw/
        L2-semantic/
      deliverables/
        zip/
      logs/
        pipeline.log
        stage-01-clone-repos.log
        stage-02a-scrape-wiki.log
        stage-03-normalize-semantic.log
        stage-05a-assemble-references.log
        stage-08-validate-output.log
      temp/
    run.json
  pipeline-YYYYMMDD-HHMMSSz-<shortid>/
    input/
      repos/
      cache/
      L1-raw/
      L2-semantic/
      manifests/
    output/
      publish/
      inspection/
      deliverables/
        zip/
      logs/
      temp/
    run.json
```

### Why this structure is better

- `input/` is authoritative working state.
- `output/publish/` is the only root that should be treated as publishable/generated output.
- `output/inspection/` makes copied diagnostics explicit instead of pretending they are part of the publish tree.
- `output/deliverables/zip/` gives packaged artifacts a clear place.
- `output/logs/` and `output/temp/` are explicit and cannot be mistaken for publishable content.
- `run.json` and `tmp/current-run.json` make run discovery deterministic.

If the project prefers `logs/` and `temp/` as siblings of `output/` instead, that is also logical. The critical requirement is to choose one contract and state it explicitly. The key point is that they must NOT live inside the publish root.

---

## Config Contract Changes

Plan 01 should be amended to introduce these path concepts explicitly:

- `PIPELINE_RUN_DIR`
- `WORKDIR = PIPELINE_RUN_DIR / input`
- `OUTPUT_ROOT_DIR = PIPELINE_RUN_DIR / output`
- `OUTDIR = OUTPUT_ROOT_DIR / publish`
- `INSPECTION_DIR = OUTPUT_ROOT_DIR / inspection`
- `DELIVERABLES_DIR = OUTPUT_ROOT_DIR / deliverables`
- `DELIVERABLES_ZIP_DIR = DELIVERABLES_DIR / zip`
- `LOG_DIR = OUTPUT_ROOT_DIR / logs`
- `TEMP_DIR = OUTPUT_ROOT_DIR / temp`
- `RUN_STATE_PATH = PIPELINE_RUN_DIR / run.json`
- `CURRENT_RUN_POINTER = tmp / current-run.json`

### Required behavior

- When env vars are absent locally, compute a fresh unique `PIPELINE_RUN_DIR`.
- Do not create directories at import time.
- `ensure_dirs()` creates the full layout and writes `run.json`.
- Local runs update `tmp/current-run.json` to point at the chosen run.
- CI can keep using a fixed `tmp/pipeline-ci/` root because the runner is clean.

### Important compatibility note

Existing code can still read `config.WORKDIR` and `config.OUTDIR`. The change is architectural clarity, not needless interface churn.

---

## Test Discovery Contract

Plan 01 section 6c should be replaced.

Recommended resolution order for `tests/support/pytest_pipeline_support.py`:

1. If `OUTDIR` is set, use it.
2. Else if `PIPELINE_RUN_DIR` is set, use `PIPELINE_RUN_DIR/output/publish`.
3. Else if `tmp/current-run.json` exists and points to a valid run, use that.
4. Else choose the newest valid `tmp/pipeline-*/run.json`.
5. Else fall back to legacy `staging/` for backward compatibility.

This preserves explicit overrides while still making the common local workflow easy.

### Why this is better than env-only

- It matches the user's requested workflow.
- It avoids forcing developers to manually export `OUTDIR` after every local run.
- It is more robust than "newest directory only" because `run.json` can confirm the exact publish root.
- It remains debuggable because the pointer file is visible and inspectable.

Suggested `run.json` fields:

```json
{
  "schema_version": 1,
  "run_id": "pipeline-20260328-142455z-7f3c",
  "created_utc": "2026-03-28T14:24:55Z",
  "status": "running",
  "paths": {
    "run_dir": "tmp/pipeline-20260328-142455z-7f3c",
    "workdir": "tmp/pipeline-20260328-142455z-7f3c/input",
    "outdir": "tmp/pipeline-20260328-142455z-7f3c/output/publish",
    "inspection_dir": "tmp/pipeline-20260328-142455z-7f3c/output/inspection",
    "deliverables_dir": "tmp/pipeline-20260328-142455z-7f3c/output/deliverables",
    "logs_dir": "tmp/pipeline-20260328-142455z-7f3c/output/logs",
    "temp_dir": "tmp/pipeline-20260328-142455z-7f3c/output/temp"
  }
}
```

---

## Specific Deltas Against Plan 01

### Target Directory Layout

Replace the current `input/` and `output/` section with the explicit contract above.

### Phase 1

Keep the "no import-time directory creation" rule, but revise phase 1 so it computes a unique `PIPELINE_RUN_DIR` and derived child paths, not just `WORKDIR=input` and `OUTDIR=output`.

### Phase 2

CI should set either:

```yaml
PIPELINE_RUN_DIR: ${{ github.workspace }}/tmp/pipeline-ci
```

or continue setting `WORKDIR` and `OUTDIR` explicitly while still conforming to the new layout:

```yaml
WORKDIR: ${{ github.workspace }}/tmp/pipeline-ci/input
OUTDIR: ${{ github.workspace }}/tmp/pipeline-ci/output/publish
```

The plan should pick one of these patterns and standardize it everywhere.

### Phase 6

Do not keep the current "set an env var manually" position as the only default local path. Adopt the discovery chain above.

### Phase 8

Documentation updates must include the explicit run-tree diagram and the run-discovery contract, not only the new default `tmp/pipeline-*` language.

---

## Recommended Decision

Use plan 01 as the implementation base, but amend it with this addendum before any code changes begin.

In short:

- Keep plan 01's discipline.
- Reintroduce automatic test discovery.
- Add a first-class run root.
- Add a unique run id suffix.
- Replace the broad `output/` bucket with explicit publish, inspection, deliverables, logs, and temp subtrees.

That yields a plan that is both implementable and logically explicit.