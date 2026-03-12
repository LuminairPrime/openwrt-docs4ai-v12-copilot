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
- [manage_ai_store.py](../../../tools/manage_ai_store.py)
- [smoke_02_ai_store_contract.py](../../../tests/smoke/smoke_02_ai_store_contract.py)

## Safety Rules

1. Never generate directly into the committed `data/base/` tree on the first
   pass.
2. Never treat `tests/* --run-ai` as proof of real AI generation. Those paths
   are cache-backed local smoke tests for placement behavior.
3. Always validate the scratch AI store before promotion.
4. Promote reviewed JSON records into `data/base/`; do not hand-edit generated
   files under `openwrt-condensed-docs/` as the primary AI workflow.
5. Use `data/override/` only for intentional human-pinned edits.

## Preferred Helper

The maintained operator entry point is:

```powershell
python tools/manage_ai_store.py --option review
```

The helper scopes scratch paths, store paths, and token selection inside one
local CLI. It does not create new numbered pipeline stages.

| `--option` value | Sequence | Use when |
| --- | --- | --- |
| `prepare` | copy committed store + L2 into scratch | you want to inspect or edit scratch inputs before generation |
| `generate` | run script `04` against existing scratch data | scratch is already prepared and you only want a live/apply pass |
| `validate` | run library-backed validation against existing scratch data | you only want schema and title/hash checks |
| `audit` | run library-backed audit against existing scratch data | you only want coverage, staleness, and hygiene checks |
| `review` | `prepare` → `generate` → `validate` → `audit` | standard scratch-first whole-project review flow |
| `promote` | copy scratch JSON into `data/base/`, then rerun validation and audit on the permanent store | scratch is already clean and reviewed |
| `full` | `review` → `promote` | you want one command for the full local store workflow |
| `cleanup` | remove scratch root | you are finished with scratch data |

Recommended examples:

```powershell
# Standard scratch-first review run.
python tools/manage_ai_store.py --option review --max-ai-files 300

# Promote a reviewed scratch run into data/base/ and re-check the permanent store.
python tools/manage_ai_store.py --option promote

# Combined local path while keeping scratch files for inspection.
python tools/manage_ai_store.py --option full --keep-scratch --max-ai-files 300
```

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

Use the helper first:

```powershell
python tools/manage_ai_store.py --option review --max-ai-files 300
```

The helper performs the same scratch-first sequence documented below: copies the
committed store and L2 corpus into scratch, runs script `04`, then runs the
same shared validation and audit logic against the scratch store.

Manual PowerShell fallback:

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
python tools/manage_ai_store.py --option validate --scratch-root tmp/ai-summary-run
python tools/manage_ai_store.py --option audit --scratch-root tmp/ai-summary-run
```

## Review And Validation

Use all three checks before promotion:

1. `python tests/smoke/smoke_02_ai_store_contract.py`
2. `python tools/manage_ai_store.py --option validate ...`
3. `python tools/manage_ai_store.py --option audit ...`

What each check proves:

- The AI smoke test verifies the stable schema contract and persistence helper
  behavior.
- `validate` checks JSON structure plus title and hash integrity against the
  current L2 corpus.
- `audit` proves coverage, staleness, orphan detection, and override precedence.

## Promotion To The Permanent Store

Only promote after the scratch store is clean.

Preferred helper path:

```powershell
python tools/manage_ai_store.py --option promote
```

`--option promote` copies reviewed scratch JSON into `data/base/`, then reruns
validation and audit against the permanent store before returning success.

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

Preferred helper path:

```powershell
python tools/manage_ai_store.py --option cleanup
```

The helper does not mutate the parent shell environment, so explicit env-var
cleanup is only needed when you use the manual environment-variable workflow.

Manual environment cleanup fallback:

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