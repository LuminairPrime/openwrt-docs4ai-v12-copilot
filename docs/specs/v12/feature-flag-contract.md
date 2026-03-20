# Retired ENABLE_RELEASE_TREE Feature Flag

## Purpose

This document records the rollout-only `ENABLE_RELEASE_TREE` environment variable that controlled the V5a migration. The flag has been removed from the live codepath in Phase 7 after successful local validation, CI proof, and external publication through the GitHub App distribution flow.

Use [release-tree-contract.md](release-tree-contract.md) for the active public contract. Use `docs/plans/v12/public-distribution-mirror-plan-2026-03-15-V5a.md` for the full rollout plan and implementation history.

## Historical Summary

| Property | Historical value |
| --- | --- |
| Name | `ENABLE_RELEASE_TREE` |
| Type | Environment variable |
| Values | `true` / `false` |
| Introduced | Phase 0 |
| Default changed to `true` | Phase 5 |
| Removed | Phase 7 |

## Historical Scope

Before removal, the flag controlled the late-stage publication path during the V5a rollout. Its scope included the release-tree-generating late stages and the transitional `05e` assembler that no longer exists in the live pipeline.

## Historical Outcome

- The live pipeline now always generates `release-tree/` and `support-tree/`.
- Validation now always requires the release-tree contract.
- Tests now treat release-tree output as the primary publish surface.
- External publication now deploys from the validated `release-tree/` subtree.

This file is retained only for rollout archaeology and should not be used as implementation guidance.
