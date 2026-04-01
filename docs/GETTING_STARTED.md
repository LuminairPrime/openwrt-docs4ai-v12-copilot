# Getting Started

## Purpose

This is the shortest path for maintainers who need to set up the repository, run the supported local validation flow, and find the right active docs.

## Prerequisites

```powershell
pip install -r .github/scripts/requirements.txt
npm install -g jsdoc-to-markdown
winget install --id JohnMacFarlane.Pandoc
```

Use the workspace interpreter directly when needed:

```powershell
.venv\Scripts\python.exe
```

Do not assume the system `python` on `PATH` is the repo interpreter.

## First Validation Commands

Run the smallest proof first, then expand:

```powershell
python tools/testing/run_default_validation.py
python tools/testing/run_source_validation.py
python tools/testing/run_targeted_pytest.py
python tools/testing/run_targeted_smoke.py
```

Preferred one-command local proof:

```powershell
python tools/testing/run_default_validation.py
```

## AI Summary Workflow

Real AI-summary work is scratch-first and AI-store-first.

```powershell
python tools/manage_ai_store.py --option review
python tools/manage_ai_store.py --option promote
python tools/manage_ai_store.py --option full --keep-scratch
```

Use [guides/runbook-ai-summary-operations.md](guides/runbook-ai-summary-operations.md) for the full workflow and rollback guidance.

## When You Need Remote Proof

1. Push the branch or target commit.
2. Pin the exact commit SHA.
3. Wait for the matching hosted workflow run.
4. Read `lint-review/summary.json` and then the summary artifacts before raw logs.

Useful commands:

```powershell
git rev-parse HEAD
gh run list --workflow "openwrt-docs4ai-pipeline" --limit 20 --json databaseId,headSha,status,conclusion,url
gh run watch <run_id> --exit-status --interval 15
gh run download <run_id> -n lint-review -D tmp/ci/lint-review
gh run download <run_id> -n pipeline-summary -D tmp/ci/pipeline-summary
gh run download <run_id> -n extract-summary -D tmp/ci/extract-summary
```

## What To Read Next

- [ARCHITECTURE.md](ARCHITECTURE.md) for repository zones, the layer model, and the current doc taxonomy.
- [specs/pipeline-stage-catalog.md](specs/pipeline-stage-catalog.md) before changing stage order or rerun guidance.
- [specs/schema-definitions.md](specs/schema-definitions.md) before changing data fields, frontmatter, or output layout.
- [specs/release-tree-contract.md](specs/release-tree-contract.md) before changing the published corpus structure.
- [specs/cookbook-authoring-spec.md](specs/cookbook-authoring-spec.md) before changing authored cookbook content rules.