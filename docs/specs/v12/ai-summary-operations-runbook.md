# AI Summary Operations Runbook

## Purpose

This is the permanent operator workflow for real AI-summary work in v12.
The policy is:

- AI store only
- scratch-first only

`data/base/` and `data/override/` are the source of truth for AI summaries.
`openwrt-condensed-docs/` is downstream generated evidence, not the primary
edit surface.

## Authoritative References

- [ai-summary-feature-spec.md](./ai-summary-feature-spec.md)
- [data/base/README.md](../../../data/base/README.md)
- [data/override/README.md](../../../data/override/README.md)
- [openwrt-docs4ai-04-generate-ai-summaries.py](../../../.github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py)
- [openwrt-docs4ai-04a-audit-ai-store.py](../../../.github/scripts/openwrt-docs4ai-04a-audit-ai-store.py)
- [openwrt-docs4ai-04b-validate-ai-store.py](../../../.github/scripts/openwrt-docs4ai-04b-validate-ai-store.py)
- [openwrt-docs4ai-v12-ai-v1-smoke-test.py](../../../tests/openwrt-docs4ai-v12-ai-v1-smoke-test.py)

## Safety Rules

1. Never generate directly into the committed `data/base/` tree on the first
   pass.
2. Never treat `tests/* --run-ai` as proof of real AI generation. Those paths
   are cache-backed local smoke tests for placement behavior.
3. Always validate the scratch AI store before promotion.
4. Promote reviewed JSON records into `data/base/`; do not hand-edit generated
   files under `openwrt-condensed-docs/` as the primary AI workflow.
5. Use `data/override/` only for intentional human-pinned edits.

## Operation Modes

### Mode A: Prompt review only

Use the manual prompt from [data/base/README.md](../../../data/base/README.md)
or the prompt block in
[openwrt-docs4ai-04-generate-ai-summaries.py](../../../.github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py).
Save the result into a scratch `data/base/<module>/<slug>.json`, then run the
validator and audit tools before any promotion.

### Mode B: Current-chat manual generation

Use the same schema and prompt contract as Mode A. Manual records should set
`content_hash` to `null` and `model` to `manual`.

### Mode C: External AI/manual generation

External models may draft JSON, but they should never write directly into the
committed store. Paste their output into a scratch base-store file, then run the
same validation and audit steps as every other mode.

### Mode D: Live API generation into a scratch store

This is the standard whole-project workflow.

1. Create a scratch area.
2. Copy the current committed AI store into scratch so existing curated records
   remain available.
3. Copy the current `openwrt-condensed-docs/L2-semantic/` tree into a scratch
   `OUTDIR`.
4. Point `AI_DATA_BASE_DIR`, `AI_DATA_OVERRIDE_DIR`, and `AI_CACHE_PATH` at the
   scratch area.
5. Set `SKIP_AI=false` and run script `04`.
6. Validate and audit the scratch store.

PowerShell example:

```powershell
$root = Resolve-Path .
$scratch = Join-Path $root "tmp/ai-summary-run"

Remove-Item $scratch -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $scratch | Out-Null

Copy-Item (Join-Path $root "data/base") (Join-Path $scratch "ai-data/base") -Recurse
Copy-Item (Join-Path $root "data/override") (Join-Path $scratch "ai-data/override") -Recurse
Copy-Item (Join-Path $root "openwrt-condensed-docs/L2-semantic") (Join-Path $scratch "out/L2-semantic") -Recurse

$env:OUTDIR = Join-Path $scratch "out"
$env:AI_DATA_BASE_DIR = Join-Path $scratch "ai-data/base"
$env:AI_DATA_OVERRIDE_DIR = Join-Path $scratch "ai-data/override"
$env:AI_CACHE_PATH = Join-Path $scratch "ai-summaries-cache.json"
$env:SKIP_AI = "false"
$env:WRITE_AI = "true"
$env:MAX_AI_FILES = "300"
$env:LOCAL_DEV_TOKEN = "<token>"

python .github/scripts/openwrt-docs4ai-04-generate-ai-summaries.py
python .github/scripts/openwrt-docs4ai-04b-validate-ai-store.py --base-dir $env:AI_DATA_BASE_DIR --override-dir $env:AI_DATA_OVERRIDE_DIR --l2-root (Join-Path $env:OUTDIR "L2-semantic")
python .github/scripts/openwrt-docs4ai-04a-audit-ai-store.py --base-dir $env:AI_DATA_BASE_DIR --override-dir $env:AI_DATA_OVERRIDE_DIR --l2-root (Join-Path $env:OUTDIR "L2-semantic") --fail-on-missing --fail-on-stale --fail-on-orphan --fail-on-invalid
```

## Review And Validation

Use all three checks before promotion:

1. `python tests/openwrt-docs4ai-v12-ai-v1-smoke-test.py`
2. `python .github/scripts/openwrt-docs4ai-04b-validate-ai-store.py ...`
3. `python .github/scripts/openwrt-docs4ai-04a-audit-ai-store.py ...`

What each check proves:

- The AI smoke test verifies the stable schema contract and persistence helper
  behavior.
- `04b` validates JSON structure plus title and hash integrity against the
  current L2 corpus.
- `04a` proves coverage, staleness, orphan detection, and override precedence.

## Promotion To The Permanent Store

Only promote after the scratch store is clean.

PowerShell example:

```powershell
$root = Resolve-Path .
$scratchBase = Join-Path $root "tmp/ai-summary-run/ai-data/base"

robocopy $scratchBase (Join-Path $root "data/base") *.json /E /NJH /NJS /NP
if ($LASTEXITCODE -gt 3) {
  throw "robocopy failed with exit code $LASTEXITCODE"
}
```

This updates and adds records without using the published output tree as the
source of truth.

## Cleanup

After promotion, clear the scratch environment variables and optionally remove
the scratch folder:

```powershell
Remove-Item Env:OUTDIR -ErrorAction SilentlyContinue
Remove-Item Env:AI_DATA_BASE_DIR -ErrorAction SilentlyContinue
Remove-Item Env:AI_DATA_OVERRIDE_DIR -ErrorAction SilentlyContinue
Remove-Item Env:AI_CACHE_PATH -ErrorAction SilentlyContinue
Remove-Item Env:SKIP_AI -ErrorAction SilentlyContinue
Remove-Item Env:WRITE_AI -ErrorAction SilentlyContinue
Remove-Item Env:MAX_AI_FILES -ErrorAction SilentlyContinue
Remove-Item Env:LOCAL_DEV_TOKEN -ErrorAction SilentlyContinue

Remove-Item (Join-Path (Resolve-Path .) "tmp/ai-summary-run") -Recurse -Force
```

## Promotion To Published Outputs

The published corpus is promoted by the hosted workflow, not by direct manual
copy from the scratch area. After committing AI-store changes:

1. push the AI-store update
2. wait for the workflow run pinned to that commit SHA
3. inspect the `final-staging` artifact or the follow-up auto-update commit
4. spot-check representative L2 and routing outputs for the new AI fields

That keeps the AI store authoritative and the generated corpus reproducible.