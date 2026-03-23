# AI Deliverable Enhancement Plan

**Recorded:** 2026-03-20
**Updated:** 2026-03-20 (required expansion pass)
**Status:** Planning baseline
**Scope:** Evaluate and sequence output enhancements that make the published
OpenWrt corpus more useful for AI agents writing OpenWrt code.
**Relationship:** Complements
[the V13 discovery upgrade plan](discovery-upgrade-plan-2026-03-15.md) and
stays within the current
[release-tree contract](../../specs/v12/release-tree-contract.md) unless
explicitly noted.

---

## 1. Executive Recommendation

The project should now run a two-track strategy:

1. **Deliverable track (what agents read):** add high-signal cookbook content,
   inter-component communication maps, and low-context routing surfaces.
2. **Validation track (what keeps outputs truthful):** add type contracts,
   AST-aware parsing and chunking, and a fast compile-check loop.

The new requirement from this update is explicit: this plan is no longer only
about publishing more text; it is also about enforcing a verifiable feedback
loop so generated guidance stays compilable and era-correct.

---

## 2. Scope Boundary

The product goal remains the same: improve the **published OpenWrt AI
deliverable**. Internal tooling changes are included only when they increase
output quality, correctness, or machine-interpretability of that deliverable.

This boundary keeps the work focused:

- in scope: artifacts shipped in `release-tree/` and upstream generation logic
  that materially improves those artifacts
- in scope: validator and sandbox tooling required to prove that examples and
  templates are correct before publication
- out of scope: broad platform rearchitecture unrelated to output quality

---

## 3. Coverage Verdict For Required Ideas

This section answers "does the plan factor these ideas in?" with explicit
status.

| Required idea | Previous status | New status |
| --- | --- | --- |
| XML output format | Optional, deferred | Included as a required but staged output after content and validation phases |
| New example code files from proven code | Included | Remains mandatory first deliverable phase |
| Use tests to build examples | Mostly rejected | Kept constrained: use **upstream/OpenWrt-facing example sources**, not repo pipeline tests |
| Tree-sitter | Previously low priority | Elevated to required enabler for AST-aware chunking and linting |
| Repomix | Low value duplicate | Still not a required implementation path for this repo |
| `llms-mini` | Optional | Elevated to required low-context surface after cookbook lands |
| Inter-component communication map | Included | Remains mandatory and expanded |
| `.d.ts` type enforcement surfaces | Partial (`ucode.d.ts` only) | Required expansion to broader OpenWrt AI typing surfaces |
| Dockerized compile sandbox | Not explicit | Added as required validation phase |
| Auto-eval compile loop | Not explicit | Added as required validation phase |
| MCP server hardening (`makefile`, `ucode`, `ubus`) | Not explicit | Added as required validation phase |

---

## 4. Updated Tier List

| Idea | Tier | Deliverable value | Repo-specific judgment |
| --- | --- | --- | --- |
| Curated OpenWrt cookbook examples | S | Highest | Most direct fix for agent failure modes in LuCI, ucode, procd, and packaging workflows. |
| Inter-component communication maps | S | Highest | Addresses the biggest composition gap: cross-daemon call flow, not just isolated APIs. |
| Expanded `.d.ts` typing surfaces for agent context | S | Highest | Existing [openwrt-docs4ai-05c-generate-ucode-ide-schemas.py](../../../.github/scripts/openwrt-docs4ai-05c-generate-ucode-ide-schemas.py) proves the pattern; extending this materially reduces hallucinated API calls. |
| Dockerized buildroot compile sandbox + auto-eval loop | A | Very high | Critical quality gate for generated examples and templates; enforces "docs that compile." |
| MCP hardening with validation tools | A | High | Converts retrieval-only behavior into actionable code validation feedback for agents. |
| Tree-sitter and AST-aware chunking | A | High | Expensive, but now required as an enabler for robust chunking, linting, and syntax-aware extraction. |
| `llms-mini` surface | A | High | Necessary for low-context agents once cookbook and type surfaces exist. |
| XML export | B | Moderate | Useful as alternate ingestion format, but secondary to content quality and validation loops. |
| Test-mining for examples (repo tests) | C | Low | Repo tests are pipeline-contract tests, not OpenWrt programming examples. |
| Repomix adoption | C | Low | Largely duplicates existing domain-specific bundling and routing already in this pipeline. |

### 4.1 Key Adjustment In This Update

Tree-sitter, typing, and validation tooling are now treated as **required
quality enablers**, not as optional internal niceties.

---

## 5. Structural Recommendation

Keep the module-centric release-tree architecture and add one new synthetic
module for cross-cutting coding guidance:

- `cookbook`

Why this remains the best base:

- It aligns with the current release-tree schema without immediate root-file
  expansion.
- It automatically participates in stage `05a` -> `06` -> `07` -> `08`.
- It keeps high-value coding guidance separately fetchable for constrained
  agent contexts.

The cookbook should combine:

1. task-oriented examples
2. communication maps
3. strict typing helper surfaces for AI tools

---

## 6. Required Implementation Plan

## 6.1 Phase 1: Ship cookbook module (mandatory)

Add a synthetic content generator before stage `05a` and publish a first set of
task-oriented pages.

Required first topics:

1. `luci-form-with-uci.md`
2. `luci-rpcd-ubus-flow.md`
3. `ucode-rpcd-service-pattern.md`
4. `procd-service-lifecycle.md`
5. `minimal-openwrt-package-makefile.md`
6. `uci-read-write-from-shell.md`
7. `hotplug-handler-pattern.md`
8. `inter-component-communication-map.md`

Required acceptance criteria:

- `cookbook/llms.txt`
- `cookbook/map.md`
- `cookbook/bundled-reference.md` (and sharded parts if needed)
- `cookbook/chunked-reference/*.md`
- automatic inclusion in root routing indexes

## 6.2 Phase 2: Inter-component maps (mandatory)

Publish communication chains as explicit, navigable documentation pages.

Required first flows:

1. LuCI JS view -> rpcd -> ubus -> UCI
2. LuCI JS view -> rpcd file/exec surface -> system mutation
3. procd init script -> service registration -> lifecycle hooks
4. hotplug event -> script handler -> config/service change
5. network config edit -> UCI -> netifd -> hotplug effects

These must be human-readable and agent-usable. Pure raw graph dumps are not
sufficient for first release.

## 6.3 Phase 3: Type enforcement surfaces (mandatory)

Expand from current single-surface `ucode.d.ts` generation to broader typed
contracts used as LLM context anchors.

Mandatory outputs:

- `cookbook/types/ucode-env.d.ts`
- `cookbook/types/luci-env.d.ts`

Mandatory behavior:

- generate from canonical extracted signatures wherever possible
- annotate unknown or ambiguous signatures explicitly
- include these files in routing surfaces and flat catalogs

Implementation path:

- extend or siblingize
  [openwrt-docs4ai-05c-generate-ucode-ide-schemas.py](../../../.github/scripts/openwrt-docs4ai-05c-generate-ucode-ide-schemas.py)
  rather than introducing ad hoc one-off generators.

## 6.4 Phase 4: Tree-sitter + AST-aware chunking (mandatory)

Tree-sitter is now a required enabler for chunk integrity and syntax-aware
agent surfaces.

Required outputs and behavior:

- initial `tree-sitter-ucode` grammar project (or compatible grammar adapter)
- AST-aware chunking rules to prevent semantic breakage

Minimum chunking guardrails:

- never split inside `define Package/*` blocks in Makefiles
- keep `start_service()` and `service_triggers()` together in init examples
- keep UCI schema sections grouped with related ubus/rpc usage examples

Note: this phase may start with best-effort coverage and improve iteratively,
but it is required in the roadmap.

## 6.5 Phase 5: AI validation pipeline (mandatory)

Introduce a compile-check loop so generated examples are continuously tested.

Required components:

1. Dockerized OpenWrt SDK/buildroot environment for fast package compile checks
2. auto-eval script that:
   - generates candidate examples/templates
   - runs build checks (`make package/<name>/compile V=s` or scoped checks)
   - captures failures
   - produces repair prompts and regression reports

Required stance:

- validation failures block promotion of affected generated guidance
- compile and lint evidence becomes part of release confidence, not optional

## 6.6 Phase 6: MCP server hardening (mandatory)

Upgrade retrieval-oriented MCP behavior into validation-capable tool surfaces.

Required MCP tools:

- `validate_openwrt_makefile`
  - checks for `include $(TOPDIR)/rules.mk`
  - checks `$(eval $(call BuildPackage,...))` placement at file end
  - warns on `PKG_MD5SUM` and prefers `PKG_HASH`
- `lint_ucode`
  - runs syntax validation via `ucode -c` where available
- `query_ubus_schema`
  - prefers live `ubus -v list` data when target runtime is available
  - falls back to corpus-derived schema snapshots when runtime is unavailable

## 6.7 Phase 7: Low-context and XML export surfaces (mandatory, staged)

After phases 1-6 land:

1. publish `llms-mini.txt` for constrained contexts
2. publish scoped XML packs (module-level first)

If root-level files are introduced, update:

- [release-tree-contract.md](../../specs/v12/release-tree-contract.md)
- [schema-definitions.md](../../specs/v12/schema-definitions.md)
- stage `07` index generation
- stage `08` validation rules

---

## 7. Directory Additions (Repo-Adapted)

The following structure maps the requested additions into this repository's
existing conventions.

```text
tools/
  type-definitions/
    generate_ucode_env_dts.py
    generate_luci_env_dts.py
  ai-validation/
    docker/
      Dockerfile.buildroot
      docker-compose.yml
    scripts/
      test_llm_generation.py
      ucode_linter.py
  mcp/
    openwrt_docs_mcp.py
    tools/
      makefile_analyzer.py
      ucode_validator.py
      ubus_introspector.py

docs/specs/v13/
  ai-validation-contract.md
  typing-surfaces-contract.md

release-tree (generated):
  cookbook/
    types/
      ucode-env.d.ts
      luci-env.d.ts
```

Notes:

- This plan keeps generated deliverables under module-local `types/` paths.
- It avoids introducing a separate top-level `openwrt-ai-docs/` tree that would
  conflict with current repo contracts.

---

## 8. Stage and Contract Constraints

Required constraints from current pipeline behavior:

- New routed artifacts must be generated before stage `06`.
- Do not plan routed outputs as a late `05e` compatibility pass.
- Stage `08` validation must be expanded whenever new deliverable classes are
  added.

This protects internal consistency between generated files, routing indexes, and
publish-time validation.

---

## 9. Immediate Execution Steps

The immediate order is now:

1. Freeze cookbook, typing, and validation directory scaffolding in this plan.
2. Implement typed contract generation (`ucode-env.d.ts`, `luci-env.d.ts`).
3. Bring up Dockerized OpenWrt SDK validation sandbox.
4. Add first compile-loop evaluator for package-template guidance.
5. Add MCP validation tools (`makefile`, `ucode`, `ubus`) with fallback modes.

These steps are required to move from static context provision to reliable,
agentic, compile-validated guidance.

---

## 10. Explicit Non-Adoptions

The following remain non-required for this repo even after the expansion:

- Repomix as a replacement for the pipeline's native packing/routing model
- mining this repo's pipeline tests as primary OpenWrt coding examples

These can still be explored experimentally, but they are not in the required
implementation baseline.
