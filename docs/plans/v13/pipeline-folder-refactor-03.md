# Plan 006-v3: Pipeline Workspace Rationalization — Consolidated Implementation Spec

**Status:** Implementation-ready draft
**Date:** 2026-03-28
**Supersedes:** pipeline-folder-refactor-00.md, pipeline-folder-refactor-01.md,
pipeline-folder-refactor-02-review-addendum.md
**Scope:** Directory structure, CI workflow, stage 03/05a/07/08 path updates,
symlink bug fix, test alignment, run-state schema, documentation

---

## Goal

Unify all pipeline writes under a single, uniquely-named run directory. Every
pipeline execution — local or CI — produces exactly one root folder whose
internal structure is explicit and unambiguous. No writes land outside this
folder. No directory names are hardcoded in pipeline logic. Tests can locate
output without manual env-var setup.

---

## Non-Goals

- Do NOT rename `release-tree/` or `support-tree/` (published contract names).
- Do NOT change `sync_tree.py` CLI interface.
- Do NOT change `data/base/`, `data/override/` (persistent AI store).
- Do NOT change `release-inputs/` or `content/cookbook-source/` (repo inputs).
- Do NOT redirect stage stdout logging to files (smoke log at `tmp/logs/` stays
  as-is; stage-level file logs are a separate future feature).
- Do NOT reorganize `input/` internals (flat layout stays; high-churn, low-value
  for this refactor).
- Do NOT move the dated distribution ZIP into the output tree (it is currently
  built in `$RUNNER_TEMP` in CI and uploaded directly; this is fine).
- Do NOT add a source-repo root `llms.txt` (explicitly out of scope per
  CLAUDE.md).
- Do NOT create new documentation files; update existing ones only.

---

## Decision Log

Decisions that changed or were settled in this document vs. prior plans:

| Issue | Prior position | Decision here | Rationale |
|-------|---------------|---------------|-----------|
| Run ID uniqueness | Timestamp-only (plan 01, same-second collision OK) | Timestamp + 4-char random hex suffix | Eliminates collision; trivially cheap |
| Output zones | `input/` + flat `output/` (plan 01) | `input/` + three-zone `output/` | Makes public vs. internal vs. pipeline-working explicit |
| L1-raw / L2-semantic in OUTDIR | Kept in publish tree (plan 01) | Moved to `intermediates/` zone | They are pipeline working copies, not publish content; stage 05a/07/08 updated accordingly |
| Test discovery | Env-var only + "staging" fallback (plan 01) / five-tier chain (plan 02) | Two-tier only: env var → `tmp/current-run.json` → clear error | Five-tier chains rot; two-tier is debuggable and has no hidden fallbacks |
| `run.json` schema | Not specified (plan 01) / full path enumeration (plan 02) | Minimal, versioned; only `pipeline_run_dir` as relative path | Paths derivable from contract; including all paths creates drift when contract changes |
| `out/diagnostics/` contents | L1-raw + L2-semantic (plan 02) | Reserved placeholder; nothing writes there yet | Not creating empty semantics before a consumer exists |
| `out/artifacts/` for zip | Separate zone (plan 02) | Not in scope; zip stays in `$RUNNER_TEMP` | Zip is CI-artifact-upload only; no consumer reads from a local artifacts dir |
| input/ reorganization | `repos/`, `cache/`, `manifests/` subdirs (plan 02) | Keep flat | All scripts reference flat paths; reorganizing is high churn for no operational benefit |
| PUBLISH_PREFIX in stage 07 | `"./openwrt-condensed-docs"` | `"."` | Truthful; display path matches href |
| Stage 03 `promote_to_staging()` destination | OUTDIR (plans 00/01/02) | `INTERMEDIATES_DIR` for L1/L2; `OUTDIR` for registry/manifest | Separates pipeline working copies from published content |

---

## Terminology

| Term | Meaning |
|------|---------|
| `PIPELINE_RUN_DIR` | Root of one complete pipeline execution. Everything the pipeline writes lives here. |
| `WORKDIR` | `{PIPELINE_RUN_DIR}/input/` — authoritative source downloads and intermediates |
| `OUTPUT_ROOT` | `{PIPELINE_RUN_DIR}/output/` — parent of all output zones |
| `OUTDIR` | `{OUTPUT_ROOT}/content/` — all content deployed externally |
| `INTERMEDIATES_DIR` | `{OUTPUT_ROOT}/intermediates/` — promoted L1/L2 copies used by downstream stages; not deployed |
| `DIAGNOSTICS_DIR` | `{OUTPUT_ROOT}/diagnostics/` — reserved for future logs, temp, and scratch; nothing writes here yet |
| `RUN_STATE_PATH` | `{PIPELINE_RUN_DIR}/run.json` — run metadata file |
| `CURRENT_RUN_POINTER` | `tmp/current-run.json` — mutable pointer to the most-recent local run |

---

## Target Directory Layout

### Primary Layout (three-zone output) — this plan implements this

```
tmp/
  current-run.json                  # mutable pointer to most-recent local run
  logs/                             # smoke test logs (pre-existing, unchanged)
    smoke-01-full-local-pipeline-log.txt

  pipeline-2026-03-28-142537-UTC-7f3c/   # one fresh directory per run
    run.json                             # run state file
    input/                               # WORKDIR
      repo-ucode/
      repo-luci/
      repo-openwrt/
      repo-manifest.json
      cross-link-registry.json
      .cache/                            # wiki page cache
      L1-raw/                            # extracted by 02x scripts
        wiki/
        ucode/
        luci/
        ...
      L2-semantic/                       # normalized by stage 03
        wiki/
        ucode/
        luci/
        ...
    output/                              # OUTPUT_ROOT
      content/                           # OUTDIR — all externally deployed content
        release-tree/
          {module}/
            llms.txt
            map.md
            bundled-reference.md
            chunked-reference/
            types/
          llms.txt
          llms-full.txt
          AGENTS.md
          README.md
          index.html
        support-tree/
        llms.txt
        llms-full.txt
        AGENTS.md
        README.md
        index.html
        repo-manifest.json
        cross-link-registry.json
        CHANGES.md
        changelog.json
        signature-inventory.json
        {module}/
          llms.txt
      intermediates/                     # INTERMEDIATES_DIR — stage-to-stage working files
        L1-raw/                          # promoted by stage 03, read by stages 07/08
        L2-semantic/                     # promoted by stage 03, read by stages 04/05a
      diagnostics/                       # DIAGNOSTICS_DIR — reserved; nothing writes here yet
    run.json
```

### Comparison Layout (two-zone output) — simpler but does not separate pipeline working files

```
tmp/
  pipeline-2026-03-28-142537-UTC-7f3c/
    run.json
    input/                               # same as primary
      ...
    output/
      deliverables/                      # OUTDIR — everything that leaves (including L1-raw / L2-semantic)
        release-tree/
        support-tree/
        L1-raw/
        L2-semantic/
        llms.txt
        ...
      diagnostics/                       # DIAGNOSTICS_DIR — reserved
```

**Why the primary layout is better:**
`L1-raw` and `L2-semantic` are pipeline working files — intermediate products
used by stages 04/05a/07/08. They are build artifacts, not published content.
Mixing them into `content/` makes `content/` harder to reason about and complicates
stage 07's web index (which should only reflect the public deliverable tree).
Separating them into `intermediates/` mirrors standard build-system practice
(e.g., Maven's `build/classes/` vs `build/dist/`).

---

## Configuration Variable Map

All variables live in `lib/config.py`. Changes show old → new default when
env vars are absent.

| Variable | Old default | New default | Notes |
|----------|-------------|-------------|-------|
| `PIPELINE_RUN_DIR` | n/a | `tmp/pipeline-YYYY-MM-DD-HHMMSS-UTC-XXXX` | New; first-class run root |
| `WORKDIR` | `tmp` | `{PIPELINE_RUN_DIR}/input` | Same logical purpose, new path |
| `OUTPUT_ROOT` | n/a | `{PIPELINE_RUN_DIR}/output` | New; derive other output vars from this |
| `OUTDIR` | `staging` | `{PIPELINE_RUN_DIR}/output/content` | Same logical purpose, new path |
| `INTERMEDIATES_DIR` | n/a | `{OUTPUT_ROOT}/intermediates` | New; replaces OUTDIR/L1-raw, OUTDIR/L2-semantic |
| `DIAGNOSTICS_DIR` | n/a | `{OUTPUT_ROOT}/diagnostics` | New; reserved placeholder |
| `RUN_STATE_PATH` | n/a | `{PIPELINE_RUN_DIR}/run.json` | New |
| `CURRENT_RUN_POINTER` | n/a | `tmp/current-run.json` | New; constant path, not per-run |
| `L1_RAW_WORKDIR` | `tmp/L1-raw` | `{WORKDIR}/L1-raw` | Formula unchanged; value changes |
| `L2_SEMANTIC_WORKDIR` | `tmp/L2-semantic` | `{WORKDIR}/L2-semantic` | Formula unchanged; value changes |
| `REPO_MANIFEST_PATH` | `tmp/repo-manifest.json` | `{WORKDIR}/repo-manifest.json` | Formula unchanged; value changes |
| `CROSS_LINK_REGISTRY` | `tmp/cross-link-registry.json` | `{WORKDIR}/cross-link-registry.json` | Formula unchanged; value changes |
| `RELEASE_TREE_DIR` | `staging/release-tree` | `{OUTDIR}/release-tree` | Formula unchanged; value changes |
| `SUPPORT_TREE_DIR` | `staging/support-tree` | `{OUTDIR}/support-tree` | Formula unchanged; value changes |

---

## Run State Schema

### `{PIPELINE_RUN_DIR}/run.json`

Written by `ensure_dirs()` when a new pipeline run directory is created (not at
import time — only when `ensure_dirs()` is explicitly called). Updated by stage
08 on successful completion.

```json
{
  "schema_version": 1,
  "run_id": "pipeline-2026-03-28-142537-UTC-7f3c",
  "created_utc": "2026-03-28T14:25:37Z",
  "status": "running",
  "pipeline_run_dir": "tmp/pipeline-2026-03-28-142537-UTC-7f3c"
}
```

Field notes:
- `schema_version`: increment if the schema changes; consumers check this first.
- `run_id`: matches the directory name.
- `created_utc`: ISO 8601 UTC timestamp set when `ensure_dirs()` runs.
- `status`: `"running"` on create; `"completed"` written by stage 08 on success;
  `"failed"` written by stage 08 on validation failure. If absent or `"running"`,
  the test discovery chain treats this run as incomplete.
- `pipeline_run_dir`: relative path from the repo root. All other paths are
  derivable from this using the documented contract. Do NOT add per-path fields —
  if the contract changes, update it here, not in every run file.

### `tmp/current-run.json`

Written (or overwritten) by `ensure_dirs()` for every new local run. Not written
when `PIPELINE_RUN_DIR` is set via env (CI manages its own state).

```json
{
  "schema_version": 1,
  "run_id": "pipeline-2026-03-28-142537-UTC-7f3c",
  "pipeline_run_dir": "tmp/pipeline-2026-03-28-142537-UTC-7f3c"
}
```

---

## Test Discovery Contract

Two tiers only. No hidden fallbacks beyond tier 2.

**For `tests/support/pytest_pipeline_support.py`:**

```python
def _resolve_outdir() -> Path:
    """Resolve the OUTDIR for pytest test runs. Two tiers only."""
    # Tier 1: explicit env var (used by CI and deliberate local overrides)
    if os.environ.get("OUTDIR"):
        return PROJECT_ROOT / os.environ["OUTDIR"]

    # Tier 2: current-run pointer written by the pipeline's ensure_dirs()
    pointer_path = PROJECT_ROOT / "tmp" / "current-run.json"
    if pointer_path.exists():
        try:
            data = json.loads(pointer_path.read_text(encoding="utf-8"))
            run_dir = PROJECT_ROOT / data["pipeline_run_dir"]
            outdir = run_dir / "output" / "content"
            if outdir.is_dir():
                return outdir
        except (KeyError, ValueError, OSError):
            pass  # fall through to error

    raise RuntimeError(
        "Cannot locate pipeline output. Either:\n"
        "  (a) set OUTDIR env var, or\n"
        "  (b) run the pipeline first (creates tmp/current-run.json automatically).\n"
        "Do NOT add more fallback tiers here — two is the maximum."
    )

OUTDIR = _resolve_outdir()
```

**Why two tiers only:** Complex discovery chains (4-5 tiers) rot silently. Each
additional tier is an untested code path that developers forget about. When a
tier fails, the fallback fires correctly once and then becomes invisible. Users
have no idea which tier resolved their path, making failures confusing. Two tiers
is the observable maximum: one explicit, one documented. The error message tells
users exactly how to fix it.

**For CI:** `OUTDIR` env var is always set. Tier 1 always applies.

**For local runs after running the pipeline:** `tmp/current-run.json` is written
by `ensure_dirs()`. Tier 2 applies without any manual env-var setup.

**For local runs without a prior pipeline execution:** The error message fires.
This is correct — there is nothing to test.

---

## Phase 1: `lib/config.py` — Core Path Refactor

**Read this file in full before editing.** The file is short (~70 lines). The
implementing agent must not rearrange existing entries or change variable names
beyond what is listed here.

### 1a. Add imports

At the top of the file, add:

```python
import datetime
import json
import secrets
```

### 1b. Add `_generate_run_id()`

Add immediately after the import block:

```python
def _generate_run_id() -> str:
    """Generate a unique pipeline run identifier.

    Format:  pipeline-YYYY-MM-DD-HHMMSS-UTC-XXXX
    Example: pipeline-2026-03-28-142537-UTC-7f3c

    The timestamp is UTC. The 4-character hex suffix prevents collisions
    between two runs started in the same second.
    """
    ts = datetime.datetime.now(datetime.timezone.utc)
    ts_str = ts.strftime("%Y-%m-%d-%H%M%S")
    suffix = secrets.token_hex(2)  # 4-char hex, e.g. "7f3c"
    return f"pipeline-{ts_str}-UTC-{suffix}"
```

### 1c. Replace WORKDIR/OUTDIR defaults

Replace:

```python
WORKDIR = os.environ.get("WORKDIR", "tmp")
OUTDIR = os.environ.get("OUTDIR", "staging")
```

With:

```python
def _resolve_run_paths():
    """Resolve pipeline run paths from env vars or a fresh timestamped run dir.

    Priority:
    1. PIPELINE_RUN_DIR env var  → derive WORKDIR, OUTPUT_ROOT, OUTDIR, INTERMEDIATES, DIAGNOSTICS
    2. WORKDIR + OUTDIR env vars → use them directly; derive OUTPUT_ROOT as OUTDIR parent
    3. Neither set               → compute a fresh unique PIPELINE_RUN_DIR

    No directories are created here. Only path strings are computed.
    ensure_dirs() creates them when a pipeline script calls it.
    """
    pipeline_run_dir_env = os.environ.get("PIPELINE_RUN_DIR")
    workdir_env = os.environ.get("WORKDIR")
    outdir_env = os.environ.get("OUTDIR")

    if pipeline_run_dir_env:
        run_dir = pipeline_run_dir_env
    elif workdir_env and outdir_env:
        # Backward compat: both set explicitly without PIPELINE_RUN_DIR.
        # Derive run dir as the common grandparent if layout matches; otherwise None.
        run_dir = None
    else:
        run_id = _generate_run_id()
        run_dir = os.path.join("tmp", run_id)

    if run_dir:
        resolved_run_dir = run_dir
        resolved_workdir = workdir_env or os.path.join(run_dir, "input")
        resolved_output_root = os.path.join(run_dir, "output")
        resolved_outdir = outdir_env or os.path.join(run_dir, "output", "content")
        resolved_intermediates = os.path.join(run_dir, "output", "intermediates")
        resolved_diagnostics = os.path.join(run_dir, "output", "diagnostics")
    else:
        # Backward compat path: WORKDIR + OUTDIR set, no PIPELINE_RUN_DIR.
        resolved_run_dir = None
        resolved_workdir = workdir_env
        resolved_output_root = os.path.dirname(outdir_env)
        resolved_outdir = outdir_env
        resolved_intermediates = os.path.join(resolved_output_root, "intermediates")
        resolved_diagnostics = os.path.join(resolved_output_root, "diagnostics")

    return (
        resolved_run_dir,
        resolved_workdir,
        resolved_output_root,
        resolved_outdir,
        resolved_intermediates,
        resolved_diagnostics,
    )

(
    PIPELINE_RUN_DIR,
    WORKDIR,
    OUTPUT_ROOT,
    OUTDIR,
    INTERMEDIATES_DIR,
    DIAGNOSTICS_DIR,
) = _resolve_run_paths()

CURRENT_RUN_POINTER = os.path.join("tmp", "current-run.json")
RUN_STATE_PATH = os.path.join(PIPELINE_RUN_DIR, "run.json") if PIPELINE_RUN_DIR else None
```

### 1d. Keep computed paths unchanged

These derive from WORKDIR and OUTDIR. They automatically point to the right
places after 1c. Do NOT change them:

```python
L1_RAW_WORKDIR = os.path.join(WORKDIR, "L1-raw")
L2_SEMANTIC_WORKDIR = os.path.join(WORKDIR, "L2-semantic")
REPO_MANIFEST_PATH = os.path.join(WORKDIR, "repo-manifest.json")
CROSS_LINK_REGISTRY = os.path.join(WORKDIR, "cross-link-registry.json")
RELEASE_TREE_DIR = os.path.join(OUTDIR, "release-tree")
SUPPORT_TREE_DIR = os.path.join(OUTDIR, "support-tree")
```

### 1e. Update `ensure_dirs()`

Replace the current `ensure_dirs()` with:

```python
def ensure_dirs() -> None:
    """Create all required pipeline directories and write run-state files."""
    # Input zone
    os.makedirs(WORKDIR, exist_ok=True)
    os.makedirs(L1_RAW_WORKDIR, exist_ok=True)
    os.makedirs(L2_SEMANTIC_WORKDIR, exist_ok=True)

    # Output zones
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(INTERMEDIATES_DIR, exist_ok=True)
    os.makedirs(DIAGNOSTICS_DIR, exist_ok=True)

    # Run state — only when PIPELINE_RUN_DIR is known
    if PIPELINE_RUN_DIR and RUN_STATE_PATH:
        _write_run_state("running")
        _update_current_run_pointer()


def _write_run_state(status: str) -> None:
    """Write or update the run.json state file."""
    if not RUN_STATE_PATH:
        return
    run_id = os.path.basename(PIPELINE_RUN_DIR) if PIPELINE_RUN_DIR else "unknown"
    created_utc = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    # Preserve created_utc if the file already exists
    if os.path.exists(RUN_STATE_PATH):
        try:
            existing = json.loads(Path(RUN_STATE_PATH).read_text(encoding="utf-8"))
            created_utc = existing.get("created_utc", created_utc)
        except (ValueError, OSError):
            pass
    state = {
        "schema_version": 1,
        "run_id": run_id,
        "created_utc": created_utc,
        "status": status,
        "pipeline_run_dir": PIPELINE_RUN_DIR.replace("\\", "/") if PIPELINE_RUN_DIR else None,
    }
    Path(RUN_STATE_PATH).write_text(
        json.dumps(state, indent=2) + "\n",
        encoding="utf-8",
    )


def _update_current_run_pointer() -> None:
    """Overwrite tmp/current-run.json to point at this run."""
    if not PIPELINE_RUN_DIR:
        return
    run_id = os.path.basename(PIPELINE_RUN_DIR)
    pointer = {
        "schema_version": 1,
        "run_id": run_id,
        "pipeline_run_dir": PIPELINE_RUN_DIR.replace("\\", "/"),
    }
    os.makedirs("tmp", exist_ok=True)
    Path(CURRENT_RUN_POINTER).write_text(
        json.dumps(pointer, indent=2) + "\n",
        encoding="utf-8",
    )


def mark_run_complete() -> None:
    """Called by stage 08 on successful validation. Updates run.json status."""
    _write_run_state("completed")


def mark_run_failed() -> None:
    """Called by stage 08 on validation failure. Updates run.json status."""
    _write_run_state("failed")
```

**Add `from pathlib import Path` to the import block if not already present.**

### 1f. Fix script 01 WORKDIR divergence

**File:** `.github/scripts/openwrt-docs4ai-01-clone-repos.py`

This script has its own WORKDIR resolution that ignores `config.py`:

```python
# CURRENT (line ~28)
WORKDIR = os.environ.get("WORKDIR", os.path.join(os.getcwd(), "tmp"))
```

Replace with:

```python
from lib import config
WORKDIR = config.WORKDIR
```

Remove any standalone `os.makedirs(WORKDIR, exist_ok=True)` call that follows
(line ~34). Ensure `config.ensure_dirs()` is called at the top of `main()`.

---

## Phase 2: Stage 03 — Promote to `INTERMEDIATES_DIR` Not `OUTDIR`

**File:** `.github/scripts/openwrt-docs4ai-03-normalize-semantic.py`

Find the `promote_to_staging()` function (around line 899). It currently copies
L1-raw and L2-semantic to `config.OUTDIR`. Change it to copy them to
`config.INTERMEDIATES_DIR` instead. Registry and manifest files still go to
`config.OUTDIR` (they are published content).

Replace the body:

```python
def promote_to_staging(registry_path: str) -> None:
    print("[03] Promoting to staging OUTDIR")
    dst_root = config.OUTDIR
    os.makedirs(dst_root, exist_ok=True)
    for d in [("L1-raw", L1_DIR), ("L2-semantic", L2_DIR)]:
        dst = os.path.join(dst_root, d[0])
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(d[1], dst)
    for f in [registry_path, os.path.join(WORKDIR, "repo-manifest.json")]:
        if os.path.isfile(f):
            shutil.copy2(f, os.path.join(dst_root, os.path.basename(f)))
```

With:

```python
def promote_to_staging(registry_path: str) -> None:
    print("[03] Promoting L1/L2 intermediates and content files")

    # L1-raw and L2-semantic go to INTERMEDIATES_DIR — used by downstream stages
    # but not deployed externally.
    intermediates_root = config.INTERMEDIATES_DIR
    os.makedirs(intermediates_root, exist_ok=True)
    for d in [("L1-raw", L1_DIR), ("L2-semantic", L2_DIR)]:
        dst = os.path.join(intermediates_root, d[0])
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(d[1], dst)

    # Registry and manifest go to OUTDIR (content/) — they are deployed externally.
    content_root = config.OUTDIR
    os.makedirs(content_root, exist_ok=True)
    for f in [registry_path, os.path.join(WORKDIR, "repo-manifest.json")]:
        if os.path.isfile(f):
            shutil.copy2(f, os.path.join(content_root, os.path.basename(f)))
```

Also update `fail_if_partial_staging_promotion()` (around line 928) which reads
`config.OUTDIR` to find L1-raw/L2-semantic. Change those references to
`config.INTERMEDIATES_DIR`:

```python
# CURRENT (line 929)
existing_root = os.path.join(config.OUTDIR, label)

# CHANGE TO:
existing_root = os.path.join(config.INTERMEDIATES_DIR, label)
```

---

## Phase 3: Stage 05a — Read L2-semantic from `INTERMEDIATES_DIR`

**File:** `.github/scripts/openwrt-docs4ai-05a-assemble-references.py`

Line 38 currently:

```python
L2_DIR = os.path.join(OUTDIR, "L2-semantic")
```

Change to:

```python
L2_DIR = os.path.join(config.INTERMEDIATES_DIR, "L2-semantic")
```

**Update the module docstring** (lines 5-9) to reflect the corrected input
path:

```python
"""
Inputs: INTERMEDIATES_DIR/L2-semantic/
Outputs: OUTDIR/{module}/{module}-complete-reference.md, ...
"""
```

---

## Phase 4: Stage 07 — Display Prefix and L1-raw Source

**File:** `.github/scripts/openwrt-docs4ai-07-generate-web-index.py`

### 4a. Remove the hardcoded display prefix

Replace line 35:

```python
PUBLISH_PREFIX = "./openwrt-condensed-docs"
```

With:

```python
PUBLISH_PREFIX = "."
```

`render_section()` uses `f"{PUBLISH_PREFIX}/{rel_path}"` which becomes
`"./{rel_path}"` — truthful and matches the actual href.

### 4b. Update L1-raw source

Stage 07 reads `outdir / "L1-raw"` (line 582) to build the L1-raw section in
the web index. L1-raw is now in `INTERMEDIATES_DIR`, not `OUTDIR`. Two options:

**Option B1 (recommended):** Remove the L1-raw section from the web index.
The public `index.html` is in `content/` and should reflect the public
deliverable, not internal intermediate files. Find the `raw_root = outdir /
"L1-raw"` line and the surrounding section-building logic. Remove the block that
generates the L1-raw section. The index.html will be cleaner.

**Option B2:** Pass `config.INTERMEDIATES_DIR` to the web index generator as an
additional parameter and build an "Intermediates" section separately.

Use Option B1 unless there is a specific reason to keep L1-raw browseable in the
index. Add a code comment: `# L1-raw is in INTERMEDIATES_DIR and is not part of
the published content tree.`

### 4c. Update HTML title and heading

Change `"openwrt-condensed-docs staging tree"` to `"openwrt-docs4ai pipeline output"`
in both the `<title>` tag and the `<h1>` tag inside `build_html()`.

### 4d. Update description paragraph

Change the paragraph referencing `PUBLISH_PREFIX` to:

> This page is a filesystem-derived browse index for the pipeline output tree.
> Each link points to a file in the content output directory. Each section maps
> to one top-level area of the generated tree.

### 4e. Update pipeline version string

In the HTML footer meta div, change `Pipeline version: v12` to
`Pipeline version: v13`.

---

## Phase 5: Stage 08 — Validation Path Updates

**File:** `.github/scripts/openwrt-docs4ai-08-validate-output.py`

### 5a. Remove hardcoded string checks from root index.html validation

In `validate_index_html_contract()` (lines 169-175), remove:

```python
if "./openwrt-condensed-docs/" not in content:
    hard_fail("index.html missing the mirrored display-path prefix")
```

The existing `actual_links` vs `expected_links` comparison already validates
link correctness. The hardcoded string check is dead.

### 5b. Remove hardcoded absence check from release-tree index.html validation

In `validate_release_index_html_contract()` (lines 200-205), remove:

```python
if "./openwrt-condensed-docs/" in content:
    hard_fail("release-tree index.html leaks the legacy display-path prefix")
```

Stage 07 no longer emits this string. The absence check is vacuous.

### 5c. Update L1-raw validation to use INTERMEDIATES_DIR

Stage 08 validates L1-raw at lines 474 and 895. Currently:

```python
staged_raw_dir = os.path.join(outdir, "L1-raw")          # line 474
l1_glob = os.path.join(outdir, "L1-raw", source)          # line 895
```

Change both to read from `config.INTERMEDIATES_DIR`:

```python
staged_raw_dir = os.path.join(config.INTERMEDIATES_DIR, "L1-raw")
l1_glob = os.path.join(config.INTERMEDIATES_DIR, "L1-raw", source)
```

### 5d. Keep legacy-guard checks (no changes)

These checks correctly prevent old names from appearing in the published tree:

- Line 370: `"openwrt-condensed-docs"` in the set of forbidden dirs inside
  release-tree. **Keep.**
- Line 403: `"openwrt-condensed-docs" in content` check on release-tree root
  files. **Keep.**

### 5e. Call `mark_run_complete()` on success

At the end of the main validation function, before exiting with code 0, add:

```python
from lib import config as pipeline_config
pipeline_config.mark_run_complete()
```

And in the failure path:

```python
pipeline_config.mark_run_failed()
```

This updates `run.json` status to `"completed"` or `"failed"`, which the test
discovery chain checks before trusting a run.

---

## Phase 6: CI Workflow Update

**File:** `.github/workflows/openwrt-docs4ai-00-pipeline.yml`

### 6a. Change the top-level `env:` block

Replace:

```yaml
env:
  PUBLISH_DIR: openwrt-condensed-docs
  WORKDIR: ${{ github.workspace }}/tmp
  OUTDIR: ${{ github.workspace }}/staging
  DIST_PAGES_REPO: openwrt-docs4ai/openwrt-docs4ai.github.io
  DIST_RELEASE_REPO: openwrt-docs4ai/corpus
  DIST_TARGET_BRANCH: main
  DIST_ZIP_ROOT_DIR: openwrt-docs4ai
```

With:

```yaml
env:
  PIPELINE_RUN_DIR: ${{ github.workspace }}/tmp/pipeline-ci
  WORKDIR: ${{ github.workspace }}/tmp/pipeline-ci/input
  OUTPUT_ROOT: ${{ github.workspace }}/tmp/pipeline-ci/output
  OUTDIR: ${{ github.workspace }}/tmp/pipeline-ci/output/content
  INTERMEDIATES_DIR: ${{ github.workspace }}/tmp/pipeline-ci/output/intermediates
  DIAGNOSTICS_DIR: ${{ github.workspace }}/tmp/pipeline-ci/output/diagnostics
  DIST_PAGES_REPO: openwrt-docs4ai/openwrt-docs4ai.github.io
  DIST_RELEASE_REPO: openwrt-docs4ai/corpus
  DIST_TARGET_BRANCH: main
  DIST_ZIP_ROOT_DIR: openwrt-docs4ai
```

Notes:
- All six path vars are set explicitly. Redundant with what config.py derives,
  but explicit is better than implicit in CI. There is no ambiguity about where
  each directory lives.
- Remove `PUBLISH_DIR: openwrt-condensed-docs` entirely — it no longer has a
  meaning or purpose.

### 6b. Fix the "Prepare Baseline" step

The current step reads from `$PUBLISH_DIR/signature-inventory.json`. Replace with:

```yaml
- name: Prepare Baseline
  run: |
    mkdir -p baseline
    echo "No baseline inventory available; drift changelog will report a clean start."
```

If baseline persistence across CI runs is desired later, add it via GHA artifact
caching. Do NOT add that complexity in this refactor.

### 6c. Remove the "Promote staging to workspace" step

Delete the entire step:

```yaml
- name: Promote staging to workspace
  run: |
    echo "Promoting staging to $PUBLISH_DIR"
    python tools/sync_tree.py promote-generated --src "$OUTDIR" --dest "$GITHUB_WORKSPACE/$PUBLISH_DIR"
```

The downstream deploy steps already read from `$OUTDIR` directly. This step is
vestigial.

### 6d. Fix the "Publish GitHub Pages branch mirror" step

Change:

```bash
publish_root="$GITHUB_WORKSPACE/$PUBLISH_DIR"
```

To:

```bash
publish_root="$OUTDIR"
```

The rest of the step uses `$publish_root` and does not need changes.

### 6e. Update artifact upload to include the full output zone

The "Upload Final Staging" artifact step currently uploads from `$OUTDIR`. Change
it to upload from `$OUTPUT_ROOT`:

```yaml
path: ${{ env.OUTPUT_ROOT }}
```

The "Deploy Download Staging" step must correspondingly download to
`$OUTPUT_ROOT` instead of `$OUTDIR`:

```yaml
path: ${{ env.OUTPUT_ROOT }}
```

**Why:** The deploy job runs in a separate VM. It needs both `content/` and
`intermediates/` (stage 08 validates against `INTERMEDIATES_DIR`). Uploading
and downloading `OUTPUT_ROOT` gives the deploy job the full output zone.

### 6f. Verify deploy steps are unaffected

The following steps already correctly use `$OUTDIR/release-tree` and need NO
changes. Verify only; do not edit:

- "Validate external distribution staging" — `release_tree="$OUTDIR/release-tree"`
- "Build dated distribution ZIP" — `release_tree="$OUTDIR/release-tree"` (zip
  written to `$RUNNER_TEMP`, not OUTDIR; no change needed)
- "Publish corpus distribution repository" — `release_tree="$OUTDIR/release-tree"`
- "Publish external Pages distribution repository" — `release_tree="$OUTDIR/release-tree"`

### 6g. Verify `mkdir -p` calls in initialize/extract jobs

The `initialize` job has `mkdir -p "$WORKDIR"`. With `WORKDIR` now pointing to
`input/`, this creates the correct input directory. Extract jobs write to
`$WORKDIR/L1-raw/` et al. — correct, since `WORKDIR = .../input`. No changes.

---

## Phase 7: Fix Symlink Deletion Bug — `lib/output_sync.py`

This phase is independent of the path refactor. It can be merged separately.

### 7a. Add `_safe_remove_entry()` helper

Add near line 245, before `_sync_recursive`:

```python
def _safe_remove_entry(path: Path) -> None:
    """Remove a filesystem entry, handling symlinks correctly.

    Symlinks are unlinked directly. shutil.rmtree is never called on a symlink
    because it follows the link and deletes the target's contents.
    """
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
```

### 7b. Use it in the node-type conflict branch (lines 282-285)

Replace:

```python
if dst_entry.is_symlink() or not dst_is_dir:
    dst_entry.unlink()
else:
    shutil.rmtree(dst_entry)
```

With:

```python
_safe_remove_entry(dst_entry)
```

### 7c. Use it in the delete-extraneous branch (lines 300-303)

Replace:

```python
if dst_entry.is_dir():
    shutil.rmtree(dst_entry)
else:
    dst_entry.unlink()
```

With:

```python
_safe_remove_entry(dst_entry)
```

### 7d. Add regression test

In `tests/pytest/pytest_08_output_sync_test.py`, add:

```python
import pytest
from pathlib import Path

def test_sync_tree_removes_extraneous_symlink_to_directory(tmp_path):
    """Extraneous symlink-to-dir in destination must be unlinked, not rmtree'd."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    target_dir = tmp_path / "real_target"

    src.mkdir()
    dst.mkdir()
    target_dir.mkdir()
    (target_dir / "important.txt").write_text("keep me", encoding="utf-8")
    (src / "file.txt").write_text("source file", encoding="utf-8")

    try:
        symlink_path = dst / "stale_link"
        symlink_path.symlink_to(target_dir)
    except OSError:
        pytest.skip("Symlink creation requires Developer Mode on Windows")

    sync_tree(src, dst, delete_extraneous=True)

    assert not symlink_path.is_symlink(), "Symlink must have been removed"
    assert target_dir.is_dir(), "Target directory must be unharmed"
    assert (target_dir / "important.txt").read_text(encoding="utf-8") == "keep me"
    assert (dst / "file.txt").read_text(encoding="utf-8") == "source file"
```

---

## Phase 8: Fix Tests

### 8a. Update `pytest_pipeline_support.py`

Replace:

```python
OUTDIR = PROJECT_ROOT / os.environ.get("OUTDIR", "staging")
```

With the two-tier resolver defined in the **Test Discovery Contract** section
above. Also add `import json` to the imports.

**Important:** `WIKI_L2_DIR` is derived from `OUTDIR` and must remain correct
after the OUTDIR change. Verify that `OUTDIR / "L2-semantic" / "wiki"` is still
appropriate, OR update it if L2-semantic has moved to INTERMEDIATES_DIR. Given
that L2-semantic moves to `intermediates/`, update:

```python
# CURRENT
WIKI_L2_DIR = OUTDIR / "L2-semantic" / "wiki"

# NEW — L2-semantic is now in INTERMEDIATES_DIR
def _resolve_intermediates_dir() -> Path:
    if os.environ.get("INTERMEDIATES_DIR"):
        return PROJECT_ROOT / os.environ["INTERMEDIATES_DIR"]
    # Derive from resolved OUTDIR (which is output/content/).
    # INTERMEDIATES_DIR is output/intermediates/, a sibling of content/.
    return OUTDIR.parent.parent / "output" / "intermediates"

INTERMEDIATES_DIR = _resolve_intermediates_dir()
WIKI_L2_DIR = INTERMEDIATES_DIR / "L2-semantic" / "wiki"
```

### 8b. Update `smoke_01_full_local_pipeline.py`

Change lines 86-87:

```python
work_dir = os.path.join(temp_dir, "work")
out_dir = os.path.join(temp_dir, "openwrt-condensed-docs")
```

To:

```python
work_dir = os.path.join(temp_dir, "input")
out_dir = os.path.join(temp_dir, "output", "content")
```

Also update `build_env()` call (a few lines later) to pass in
`intermediates_dir = os.path.join(temp_dir, "output", "intermediates")`. Check
`smoke_pipeline_support.build_env()` signature — if it does not accept
`intermediates_dir`, add it and set `INTERMEDIATES_DIR` in the env dict:

```python
env["INTERMEDIATES_DIR"] = intermediates_dir
```

### 8c. Verify `smoke_00_post_extract_pipeline.py`

Uses `workdir = temp_dir` and `outdir = os.path.join(temp_dir, "out")`. This
test is a lighter weight post-extract smoke. Leave naming as-is but ensure
`build_env()` sets `INTERMEDIATES_DIR` to a valid scratch directory even if the
value is unused:

```python
env.setdefault("INTERMEDIATES_DIR", os.path.join(os.path.dirname(outdir), "intermediates"))
```

---

## Phase 9: Update `.gitignore`

Replace any current entries for `staging/` and `openwrt-condensed-docs/` with:

```gitignore
# Pipeline run directories (all timestamped local runs + fixed CI dir)
tmp/

# Legacy and backup output roots (safety net)
staging/
openwrt-condensed-docs*/
```

`tmp/` already covers both the timestamped local run dirs and `tmp/pipeline-ci/`.

---

## Phase 10: Update Documentation

### 10a. `CLAUDE.md`

Update the "Architecture: Layer Model" table entry for WORKDIR and OUTDIR:

| Layer | Location | Notes |
|-------|----------|-------|
| WORKDIR default | `tmp/pipeline-YYYY-MM-DD-HHMMSS-UTC-XXXX/input/` | Auto-created per local run when no env vars set |
| OUTDIR default | `tmp/pipeline-YYYY-MM-DD-HHMMSS-UTC-XXXX/output/content/` | Sibling to intermediates/ and diagnostics/ |

Remove the sentence "There is no tracked publish root in the source repository."
Replace with:

> All pipeline working state lives under `tmp/` (gitignored). Each local run
> creates a fresh uniquely-named directory automatically. CI uses the fixed
> path `tmp/pipeline-ci/`. The run layout is:
> `{run-dir}/input/` (WORKDIR), `{run-dir}/output/content/` (OUTDIR),
> `{run-dir}/output/intermediates/` (stage-to-stage working copies).

Update the "Local Validation Commands" section to note that tests automatically
resolve the output location via `tmp/current-run.json` — no manual `OUTDIR`
export needed after a local pipeline run.

### 10b. `docs/ARCHITECTURE.md`

Update the "Repository Zones" or directory layout table. Replace `staging/` row
with:

| Zone | Path | Description |
|------|------|-------------|
| Pipeline runs | `tmp/pipeline-*/` | One directory per execution; gitignored |
| Run input | `tmp/pipeline-*/input/` | WORKDIR: clones, L1-raw, L2-semantic (authoritative) |
| Run content output | `tmp/pipeline-*/output/content/` | OUTDIR: all externally deployed content |
| Run intermediates | `tmp/pipeline-*/output/intermediates/` | Stage-to-stage working copies; not deployed |
| Run diagnostics | `tmp/pipeline-*/output/diagnostics/` | Reserved for future logs and temp |
| Current-run pointer | `tmp/current-run.json` | Points to most-recent local run |

### 10c. `DEVELOPMENT.md`

Update "Output Architecture" or equivalent:
- Document the three-zone output layout.
- Document that `tmp/current-run.json` is written automatically and how tests
  use it.
- Note that `tmp/` accumulates run directories; users manage size themselves.
- Remove references to `staging/` as the default output location.

---

## Phase Ordering and Dependencies

```
Phase 1 (config.py)
  --- All later phases depend on this; do it first ---

Phase 2 (stage 03)     depends on: INTERMEDIATES_DIR from Phase 1
Phase 3 (stage 05a)    depends on: INTERMEDIATES_DIR from Phase 1
Phase 4 (stage 07)     depends on: OUTDIR from Phase 1; L1-raw move from Phase 2
Phase 5 (stage 08)     depends on: INTERMEDIATES_DIR from Phase 1; L1-raw move from Phase 2
Phase 6 (CI workflow)  depends on: path changes from Phase 1; promote removal from Phase 2
Phase 8 (tests)        depends on: OUTDIR/INTERMEDIATES_DIR from Phase 1
Phase 7 (symlink fix)  independent — can be done in any order
Phase 9 (.gitignore)   independent
Phase 10 (docs)        do last
```

---

## Verification Checklist

Run these in order after all phases are complete:

```powershell
# 1. Lint (fast; catches syntax, type, and workflow errors)
python tests/check_linting.py

# 2. Focused pytest (config helpers, output_sync, contract tests)
python tests/run_pytest.py

# 3. Full smoke test (runs pipeline in fresh temp dir; validates new layout)
python tests/run_smoke.py

# 4. Legacy name sweep — must return ZERO matches in active code
# Allowed: .gitignore patterns, stage 08 legacy-guard sets, docs/archive/*, docs/plans/*
grep -rn "openwrt-condensed-docs" --include="*.py" --include="*.yml" .github/ lib/ tests/ tools/
grep -rn '"staging"' --include="*.py" lib/ .github/scripts/

# 5. Confirm run directory is created and current-run.json is written
python .github/scripts/openwrt-docs4ai-03-normalize-semantic.py --allow-partial
cat tmp/current-run.json
```

Expected state:
- `tmp/current-run.json` exists and points to a valid `tmp/pipeline-*/` directory
- `run.json` inside that directory has `"status": "running"` or `"completed"`
- `tmp/pipeline-*/output/content/` exists with pipeline output
- `tmp/pipeline-*/output/intermediates/L1-raw/` and `L2-semantic/` exist
- `tmp/pipeline-*/output/diagnostics/` exists (empty)
- `staging/` does not exist unless the user explicitly set `OUTDIR=staging`

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Stage 05a reads from wrong L2-semantic location | Medium | Phase 3 explicitly updates `L2_DIR`; linting and smoke test catch broken reads |
| Stage 07 L1-raw section breaks after removal | Low | Removing a section from web index is safe; stage 08 no longer validates it in OUTDIR |
| Stage 08 validates wrong L1-raw path | Medium | Phase 5c updates both lines explicitly; smoke test runs stage 08 and validates |
| CI artifact upload excludes intermediates | Medium | Phase 6e changes upload/download to use `$OUTPUT_ROOT` not `$OUTDIR` |
| pytest_pipeline_support resolves wrong OUTDIR | Medium | Two-tier resolver is explicit; error message fires if both tiers fail |
| `_write_run_state()` fails on CI (no PIPELINE_RUN_DIR) | Low | Guard: `if PIPELINE_RUN_DIR and RUN_STATE_PATH` before writing |
| Timestamp collision between two ad-hoc local runs | Very low | 4-char hex suffix makes P(collision) ≈ 1/65536 per second |
| `current-run.json` stale after a failed run | Low | Test discovery checks `run.json` status; if `"running"` or `"failed"`, a clear log message is appropriate but tests can still use the dir for inspecting failures |
| smoke_01 `build_env()` missing INTERMEDIATES_DIR | Medium | Phase 8b explicitly adds it; stage 03 would fail immediately and loudly if missing |

---

## What NOT to Change

Listed explicitly to prevent scope creep:

- Do NOT rename `release-tree/` or `support-tree/` inside OUTDIR.
- Do NOT change `sync_tree.py` CLI (the `promote-generated` subcommand can
  remain unused but should not be deleted — it may be used manually).
- Do NOT change `data/base/`, `data/override/`, `release-inputs/`,
  `templates/`, or `content/cookbook-source/`.
- Do NOT move the dated distribution ZIP from `$RUNNER_TEMP` into the output
  tree.
- Do NOT add stage-level file logging (stdout logging stays as-is).
- Do NOT add a source-repo root `llms.txt`.
- Do NOT reorganize `input/` internals (`repo-*/`, flat layout stays).
- Do NOT change the `tmp/logs/` location for smoke test output; that is a test
  runner concern, not a pipeline stage concern.
