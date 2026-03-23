# V13 Enhancement Plan — Opus 2

**Recorded:** 2026-03-20
**Status:** Ready for implementation — choose one option per decision point
**Supersedes:** `enhancement-plan-opusmax.md` (corrects the pipeline integration
design; the tier list, content specifications, and guardrails remain valid and
are incorporated by reference)

---

## 0. What this document changes

The previous plan (`enhancement-plan-opusmax.md`) recommended placing cookbook
source content in `release-inputs/release-include/cookbook/` and generating it
via a `04b` stage. That recommendation was wrong. This document explains why
and presents correct alternatives.

The tier list, cookbook topic specifications, content authoring guidelines, and
most guardrails from the previous plan are unchanged. This document focuses
exclusively on the pipeline integration and source-file location decisions.

---

## 1. Critical pipeline constraint discovered

Three downstream stages discover modules by scanning `OUTDIR/L2-semantic/`:

| Stage | Discovery mechanism | Code |
| --- | --- | --- |
| `05a` (assemble references) | `os.listdir(L2_DIR)` | Lists directories in `L2-semantic/`, iterates over each as a module |
| `06` (routing indexes) | `os.listdir(L2_DIR)` | Same scan, generates `llms.txt` per module and root routing indexes |
| `08` (validation) | `expected_module_names()` → `os.listdir(L2-semantic/)` | Derives the expected module set from L2, then hard-fails if the release-tree module set doesn't match |

**Stage 08 specifically hard-fails if the release-tree contains a module
that doesn't exist in L2-semantic:**

```python
# 08-validate-output.py, line 322-334
expected_modules = expected_module_names(outdir)     # from L2-semantic/
modules = expected_release_module_names(release_tree_dir)  # from release-tree/
if expected_modules and modules != expected_modules:
    hard_fail(f"release-tree module set mismatch (...)")
```

This means:
- **Any approach that bypasses L2-semantic requires modifying stages 05a, 06,
  AND 08** — three separate scripts that all independently assume the L2
  directory is the source of truth for the module list.
- **Any approach that produces L2-semantic output for cookbook automatically
  makes all three stages work with zero modifications.**

The `release-inputs/release-include/` overlay is applied in stage 07, AFTER
stages 05a and 06 have already run, and the overlay contents are invisible to
the L2-semantic module scan. This is why the previous plan's recommendation
was structurally broken.

---

## 2. Pipeline integration options

### Option A: L1 Extractor (RECOMMENDED)

**Create `02i-extract-cookbook.py` that writes L1 output like every other
extractor.** The cookbook content flows through L1 → L2 → L3/L4 identically
to every other module.

```
content/cookbook/*.md  →  02i writes L1-raw/cookbook/  →  03 normalizes to L2-semantic/cookbook/
→  05a assembles bundled-reference  →  06 generates routing  →  07 HTML index  →  08 validates
```

**What `02i` does:**
1. Reads hand-authored Markdown files from a repo source directory.
2. For each file, calls `extractor.write_l1_markdown("cookbook", "cookbook",
   slug, content, metadata)` — the same shared helper every other extractor
   uses (see `lib/extractor.py`).
3. This produces `L1-raw/cookbook/{origin_type}-{slug}.md` + `.meta.json`
   sidecar for each topic.

**What happens automatically downstream with NO code changes:**
- **Stage 03** reads `L1-raw/cookbook/`, adds YAML frontmatter (title, module,
  origin_type, token_count, version), runs cleanup (harmless no-ops on
  already-clean content), writes to `L2-semantic/cookbook/`.
- **Stage 05a** discovers `cookbook` in `L2-semantic/`, assembles
  `bundled-reference.md`, `map.md`, copies `chunked-reference/` pages —
  exactly as it does for every other module.
- **Stage 06** discovers `cookbook` in `L2-semantic/`, generates
  `cookbook/llms.txt` and includes cookbook in root `llms.txt` and
  `llms-full.txt`. Cookbook lands in the "Other Components" category
  (because `MODULE_CATEGORIES` in stage 06 doesn't list it yet) —
  one 2-line dictionary addition gives it a proper category.
- **Stage 08** sees `cookbook` in both L2-semantic and release-tree → passes
  the module-set-match validation automatically.

**Script changes required:**

| Script | Change | Scope |
| --- | --- | --- |
| NEW `02i-extract-cookbook.py` | ~60-line extractor | New file |
| `06` routing indexes | Add `"cookbook": "Guides"` to `MODULE_CATEGORIES` dict | 1 line |
| None of: 03, 05a, 05b, 07, 08 | Zero changes needed | — |

**Pros:**
- Zero modifications to stages 03, 05a, 07, 08.
- One-line addition to stage 06 (`MODULE_CATEGORIES`).
- Cookbook content gets full pipeline treatment: YAML frontmatter injection,
  cl100k_base token counting, cross-link processing, and validation.
- The extractor pattern is proven across 8 existing extractors (02a–02h).
- No stage renaming needed — `02i` is a clean sibling in the existing `02`
  family.
- Stage 04 (AI summaries) automatically sees cookbook in L2 and can optionally
  enrich it. Setting `SKIP_AI=true` (the default) skips it cleanly.

**Cons:**
- Hand-authored content goes through L1→L2 normalization, which includes
  wiki-specific cleanup logic. This is harmless (the cleanup regexes won't
  match clean Markdown) but conceptually unnecessary.
- Adds a dependency edge: `02i` must run before `03`. However, `02i` has no
  dependency on `01` (clone-repos) since it reads local files, so it can run
  in parallel with both `01` and `02a` in CI.

**Estimated effort:** Small. The extractor is trivial (~60 lines, following
the pattern of `02h` which is 92 lines for a similar "read files, write L1"
pattern). No modifications to any existing script except one dictionary entry.

---

### Option B: Direct L2 Injection via `04b`

**Create `04b-assemble-cookbook.py` that writes directly to `L2-semantic/cookbook/`,
bypassing L1.**

```
content/cookbook/*.md  →  04b writes L2-semantic/cookbook/ (with proper frontmatter)
→  05a assembles  →  06 routes  →  07 indexes  →  08 validates
```

**What `04b` does:**
1. Reads hand-authored Markdown files from a repo source directory.
2. Injects YAML frontmatter (title, module, origin_type, token_count, version)
   to match L2 schema requirements.
3. Writes directly to `OUTDIR/L2-semantic/cookbook/`.
4. Does NOT produce L1 output — the cookbook has no "raw" layer.

**Script changes required:**

| Script | Change | Scope |
| --- | --- | --- |
| NEW `04b-assemble-cookbook.py` | ~120-line L2 assembler | New file |
| `04-generate-ai-summaries.py` | **RENAME to `04a-generate-ai-summaries.py`** | Filename + all references |
| `06` routing indexes | Add `"cookbook": "Guides"` to `MODULE_CATEGORIES` | 1 line |
| Workflow YAML | Update `04` reference to `04a`, add `04b` step | Several lines |
| `docs/ARCHITECTURE.md` | Update stage table | Several lines |
| `docs/specs/v12/execution-map.md` | Update stage dependency map | Several lines |
| Tests referencing `04-generate` | Update to `04a-generate` | Several files |

**Pros:**
- The cookbook content doesn't go through L1 cleanup, which is more
  conceptually honest (there's no "raw" extraction step for hand-authored
  content).
- The `04b` script has full control over frontmatter generation.
- L2 output is the same as Option A — all downstream stages work.

**Cons:**
- **Requires the `04` → `04a` rename.** The naming constraint ("bare stage id
  cannot coexist with lettered siblings") forces renaming the existing
  `04-generate-ai-summaries.py` to `04a-generate-ai-summaries.py`. This
  cascades to: workflow YAML, ARCHITECTURE.md, execution-map.md, CLAUDE.md,
  any test files, and any other documents referencing the old name.
- The `04b` script must duplicate stage 03's frontmatter-injection and
  token-counting logic rather than reusing it via the L1→L2 pipeline.
- The cookbook has no L1 representation, which means `support-tree/raw/`
  (uploaded as CI artifact) won't include cookbook source files — a minor
  debuggability gap.
- More total lines of change across the repo due to the rename cascade.

**Estimated effort:** Medium. The script itself is moderate, but the `04` →
`04a` rename requires touching 5–10 files and all their tests.

---

### Option C: Early Overlay Application

**Move the `release-inputs/release-include/` overlay application from stage 07
to a new step between 05a and 06.** This makes the overlay-based approach from
the previous plan work correctly.

```
release-inputs/release-include/cookbook/  →  applied after 05a, before 06
→  06 generates routing (sees cookbook)  →  07 HTML index  →  08 validates
```

**Changes required:**

| Script | Change | Scope |
| --- | --- | --- |
| NEW content in `release-inputs/release-include/cookbook/` | All cookbook files pre-built: `llms.txt`, `map.md`, `bundled-reference.md`, `chunked-reference/*.md` | Content files |
| `07` | Extract `apply_release_include_overlay()` into a separate callable step, or split it into a pre-06 and post-06 phase | Moderate refactor of stage 07 |
| `06` | Must scan `release-tree/` for modules in addition to `L2-semantic/` | Module discovery change |
| `08` | Must accept modules that exist in release-tree but not in L2-semantic | Validation logic change |
| Workflow YAML | Add new step between 05d and 06 for overlay application | Several lines |

**Pros:**
- Cookbook source files live in `release-inputs/`, which is already a
  source-controlled input directory.
- No new top-level directories needed.
- No extractor script needed.

**Cons:**
- **Modifies the overlay contract.** The current behavior is: overlays are
  applied late (stage 07), after all generation. Moving them earlier changes
  the semantics — an overlay file could now be overwritten by a later
  generation step. This is a subtle behavioral change that could cause
  hard-to-debug issues for existing overlays.
- **Requires modifying three downstream scripts** (06, 07, 08) to handle
  modules that don't have L2 source. This is exactly the problem Option A
  avoids.
- The cookbook files in `release-inputs/` must include pre-built `llms.txt`,
  `map.md`, and `bundled-reference.md` — these are normally generated by the
  pipeline, but here they must be maintained by hand. Any time a topic is
  added, the routing and bundled reference files must be manually updated.
- Token counts in the hand-maintained `llms.txt` will drift from actual values
  unless a separate tool is run to recalculate them.
- Conflates "static overlays" (`.nojekyll`) with "primary content modules"
  in a single mechanism.

**Estimated effort:** Medium-high. Three script modifications, contract changes,
and ongoing maintenance burden for hand-built routing files.

---

### Option D: Full Pipeline Renumber

**Rename all scripts from the current 01–08 scheme to a grouped 1x/2x/3x/4x/5x
scheme.** This removes the "bare stage vs lettered siblings" constraint entirely
and creates natural insertion points for new content types.

```
Current → Proposed
01-clone-repos            → 10-clone-repos
02a-scrape-wiki           → 11a-scrape-wiki
02b through 02h           → 11b through 11h
(NEW) 02i-extract-cookbook → 11i-extract-cookbook
03-normalize-semantic     → 20-normalize-semantic
04-generate-ai-summaries  → 21-generate-ai-summaries
05a-assemble-references   → 30a-assemble-references
05b through 05d           → 30b through 30d
06-generate-llm-routing   → 31-generate-llm-routing
07-generate-web-index     → 32-generate-web-index
08-validate-output        → 40-validate-output
```

**Changes required:** Every script filename, every workflow YAML reference,
every test, every doc reference, every log prefix, CLAUDE.md, ARCHITECTURE.md,
execution-map.md, and any external documentation that mentions script names.

**Pros:**
- Clean conceptual groupings (1x=acquisition, 2x=processing, 3x=assembly,
  4x=validation).
- Room for growth within each group (10 slots per group).
- The `04`→`04a` rename tension disappears permanently.
- Clearer for new contributors to understand stage relationships.

**Cons:**
- **Massive churn.** Every single pipeline reference in the repo changes.
  Conservative estimate: 30–50 files need updates.
- **High regression risk.** Missing one reference in a test, workflow, or doc
  creates a silent failure or CI break.
- **The current naming works.** The 01–08 scheme is well-documented and all
  maintainers know it. The benefit is aesthetic, not functional.
- **Blocks other work.** A rename of this scope should be its own PR, not
  mixed with cookbook content additions.

**Estimated effort:** High. 1–2 days of mechanical renaming plus thorough
validation. Should not be combined with any other change.

**Recommendation:** Do not pursue for V13. The cookbook can be integrated
cleanly without a full renumber (Option A requires zero renames). Consider
for a future V14 if the stage count grows significantly.

---

## 3. Source content location options

Independent of the pipeline integration choice, the hand-authored cookbook
Markdown files need a home in the repo. These are the source files that the
extractor (or assembler) reads from.

### Option X: `content/cookbook/` (new top-level directory)

```text
content/
  cookbook/
    era-guide.md
    common-ai-mistakes.md
    architecture-overview.md
    embedded-constraints.md
    inter-component-communication-map.md
    luci-form-with-uci.md
    ...
```

**Pros:**
- Self-documenting name. "content" means "hand-authored content that feeds the
  pipeline."
- Clearly distinct from `templates/` (which holds pipeline templates),
  `release-inputs/` (which holds release overlays), and `docs/` (which holds
  maintainer documentation).
- Scales naturally: `content/cookbook/`, and later potentially
  `content/tutorials/`, `content/quickstart/`, etc.
- Parallel to the `data/` directory which holds AI store data — `data/` is
  machine-generated pipeline data, `content/` is human-authored pipeline data.

**Cons:**
- New top-level directory to document in ARCHITECTURE.md.
- One more entry in the Repository Zones table.

**What needs updating:**
- `docs/ARCHITECTURE.md` Repository Zones table: add `content/` row.
- `.gitignore`: verify no exclusion patterns would match.

### Option Y: `templates/cookbook/` (existing directory)

```text
templates/
  mermaid/              (existing)
  cookbook/
    era-guide.md
    common-ai-mistakes.md
    ...
```

**Pros:**
- `templates/` already exists and is documented as "static content templates
  consumed by the live pipeline."
- No new top-level directory.
- The cookbook source files are, in a sense, templates that get processed into
  pipeline output.

**Cons:**
- The `templates/` directory currently only holds Mermaid diagram templates.
  Adding Markdown content modules to it stretches the semantic meaning.
- ARCHITECTURE.md describes `templates/` as: "Only keep templates that are
  actually consumed by the live pipeline." The cookbook files fit this
  description, but a future maintainer might not expect to find primary
  content modules alongside diagram templates.
- If the project later adds other authored content modules (tutorials, guides),
  `templates/` becomes a grab-bag.

**What needs updating:**
- Nothing structural — directory exists.
- ARCHITECTURE.md could optionally be updated to clarify the broader use.

### Option Z: Inline in `.github/scripts/cookbook-source/`

```text
.github/
  scripts/
    cookbook-source/
      era-guide.md
      ...
    openwrt-docs4ai-02i-extract-cookbook.py
```

**Pros:**
- Source content lives next to the script that processes it.
- No new top-level directory.

**Cons:**
- `.github/scripts/` is documented as containing numbered pipeline Python
  scripts. Mixing Markdown content into it is a category violation.
- `.github/` is typically for CI/CD infrastructure, not content.
- Least intuitive location for a maintainer looking for cookbook source files.

**Recommendation:** Not recommended.

---

## 4. Recommended combination

**Option A (L1 extractor) + Option X (`content/cookbook/`)** is the
recommended combination.

**Rationale:**

| Criterion | Option A+X | Option B+X | Option C |
| --- | --- | --- | --- |
| Scripts requiring modification | 1 (one dict entry in 06) | 5+ (rename cascade) | 3 (06, 07, 08) |
| New scripts to create | 1 (~60 lines) | 1 (~120 lines) | 0 |
| Stages that work unchanged | 03, 05a, 05b, 05c, 05d, 07, 08 | 03, 05a, 05b, 05c, 05d, 07, 08 | Only 03, 05a-d |
| Stage rename required | No | Yes (`04` → `04a`) | No |
| L2-semantic module presence | Automatic | Automatic | Requires special handling |
| Token counting | Automatic (stage 03) | Manual (in 04b) | Manual (hand-maintained) |
| Cross-link processing | Automatic (stage 03) | Manual (in 04b) | None |
| Validation pass | Automatic | Automatic | Requires 08 modification |
| Overlay contract change | None | None | Yes (behavioral change) |
| CI parallelism | 02i runs parallel to 01 and 02a | 04b runs after 03 | N/A |

Option A is strictly superior on script-change count, requires no renames,
preserves all existing contracts, and makes every downstream stage work
automatically through the proven L1→L2 pipeline path.

---

## 5. Detailed implementation plan (Option A + Option X)

This section replaces the "Phase 1 files" section of the previous plan.

### 5.1 New files to create

**`content/cookbook/` directory with topic source files:**

Each file is a pure Markdown file (no YAML frontmatter — stage 03 adds that).
Files should be named with descriptive slugs matching the topic names from
`enhancement-plan-opusmax.md` §1.4:

```text
content/cookbook/
  era-guide.md
  common-ai-mistakes.md
  architecture-overview.md
  embedded-constraints.md
  inter-component-communication-map.md
  luci-form-with-uci.md
  luci-rpcd-ubus-flow.md
  ucode-rpcd-service-pattern.md
  procd-service-lifecycle.md
  minimal-openwrt-package-makefile.md
  uci-read-write-from-ucode.md
  uci-read-write-from-shell.md
  hotplug-handler-pattern.md
  wifi-radio-configuration.md
  luci-status-page-with-polling.md
  ubus-service-registration.md
  full-stack-vpn-toggle.md
```

Content format: pure Markdown starting with an H1 heading. Stage 03 will
add YAML frontmatter automatically. Do NOT add YAML frontmatter to these files.

**`.github/scripts/openwrt-docs4ai-02i-extract-cookbook.py`:**

```python
"""
Purpose: Extract hand-authored cookbook content into L1.
Phase: Extraction
Layers: content/ -> L1
Inputs: content/cookbook/*.md
Outputs: tmp/L1-raw/cookbook/*.md and .meta.json
Environment Variables: WORKDIR
Dependencies: lib.config, lib.extractor
Notes: Reads from repo-local content directory. No upstream clone dependency.
"""

import os
import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, extractor

sys.stdout.reconfigure(line_buffering=True)

print("[02i] Extract cookbook content")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
COOKBOOK_SOURCE_DIR = os.path.join(REPO_ROOT, "content", "cookbook")

if not os.path.isdir(COOKBOOK_SOURCE_DIR):
    print(f"[02i] SKIP: cookbook source directory not found at {COOKBOOK_SOURCE_DIR}")
    sys.exit(0)

ts = datetime.datetime.now(datetime.UTC).isoformat()
saved = 0

for fname in sorted(os.listdir(COOKBOOK_SOURCE_DIR)):
    if not fname.endswith(".md"):
        continue

    fpath = os.path.join(COOKBOOK_SOURCE_DIR, fname)
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        print(f"[02i] WARN: Could not read {fpath}: {e}")
        continue

    if not content:
        print(f"[02i] WARN: Empty file {fname}, skipping")
        continue

    slug = fname.removesuffix(".md")
    metadata = {
        "extractor": "02i-extract-cookbook.py",
        "origin_type": "cookbook",
        "module": "cookbook",
        "slug": slug,
        "original_url": None,
        "language": "markdown",
        "upstream_path": f"content/cookbook/{fname}",
        "fetch_status": "success",
        "extraction_timestamp": ts,
    }

    extractor.write_l1_markdown("cookbook", "cookbook", slug, content, metadata)
    saved += 1

if saved == 0:
    print("[02i] FAIL: Zero cookbook files extracted")
    sys.exit(1)

print(f"[02i] OK: extracted {saved} cookbook topics")
```

### 5.2 Existing files to modify

**`.github/scripts/openwrt-docs4ai-06-generate-llm-routing-indexes.py`:**

Add `"cookbook"` to the `MODULE_CATEGORIES` dictionary:

```python
MODULE_CATEGORIES = {
    "procd": "Core Daemons",
    "uci": "Core Daemons",
    "openwrt-hotplug": "Core Daemons",
    "ucode": "Scripting & Logic",
    "luci": "Scripting & Logic",
    "cookbook": "Guides",                # ← add this line
    "luci-examples": "Ecosystem",
    "openwrt-core": "Ecosystem",
    "wiki": "Manuals",
}
```

If a `CATEGORY_ORDER` list exists, add `"Guides"` to it in a sensible position
(before "Ecosystem", after "Scripting & Logic").

**`.github/workflows/openwrt-docs4ai-pipeline.yml`:**

Add `02i` to the extraction phase. Since `02i` has no dependency on `01`
(clone-repos), it can run:
- In the same matrix as `02b`–`02h` (simplest, even though it doesn't need
  the clone artifacts), OR
- In parallel with `02a` (wiki scraper) as an independent job, OR
- As a step in the `process` job before stage `03` runs.

The simplest approach: add it as a step in the `process` job, before the
`03-normalize-semantic` step. This is safe because `02i` only reads from
`content/cookbook/` (always available) and writes to `WORKDIR/L1-raw/cookbook/`.

**`docs/ARCHITECTURE.md`:**

Add to the Repository Zones table:

```markdown
| `content/` | Hand-authored content that feeds the pipeline | Source for synthetic modules like cookbook. Not generated, not scratch. |
```

Add `02i` to the Execution Contract or the stage listing:

```markdown
2b. `02i` extracts hand-authored cookbook content into L1 from `content/cookbook/`. No upstream clone dependency.
```

**`docs/specs/v12/execution-map.md`:**

Add `02i` to the Ordered Script Flow after `02h`:

```markdown
3b. `02i-extract-cookbook.py` (local content, no clone dependency)
```

### 5.3 Files that need NO modification

| Script | Why no change needed |
| --- | --- |
| `03-normalize-semantic.py` | Scans all of L1-raw/, picks up cookbook automatically |
| `04-generate-ai-summaries.py` | Scans L2-semantic/, will see cookbook. With SKIP_AI=true, no-op. |
| `05a-assemble-references.py` | Scans L2-semantic/, assembles cookbook like any module |
| `05b-generate-agents-and-readme.py` | Generates root AGENTS.md from all release-tree modules |
| `05c-generate-ucode-ide-schemas.py` | Only processes ucode module, unaffected |
| `05d-generate-api-drift-changelog.py` | Processes signature inventory, unaffected |
| `07-generate-web-index.py` | Scans release-tree/, includes cookbook in HTML index |
| `08-validate-output.py` | Derives expected modules from L2-semantic, cookbook is there |

### 5.4 Verification

After implementation, run:

```powershell
python tests/run_smoke_and_pytest.py
python tests/check_linting.py
```

Then verify manually:
1. `tmp/L1-raw/cookbook/` contains `.md` + `.meta.json` files for each topic.
2. `openwrt-condensed-docs/L2-semantic/cookbook/` contains frontmatter-enriched
   Markdown files.
3. `openwrt-condensed-docs/release-tree/cookbook/` contains `llms.txt`,
   `map.md`, `bundled-reference.md`, and `chunked-reference/`.
4. `openwrt-condensed-docs/release-tree/llms.txt` includes a cookbook entry.
5. `openwrt-condensed-docs/release-tree/index.html` includes cookbook links.
6. Module count in AGENTS.md is 9 (was 8).

---

## 6. Phases 2–5 from previous plan

The Phase 2 (era guide + communication maps), Phase 3 (expanded .d.ts),
Phase 4 (llms-mini.txt, per-module AGENTS.md), and Phase 5 (XML export,
Makefile templates) specifications from `enhancement-plan-opusmax.md` remain
valid and are incorporated by reference.

Key adjustments for consistency with Option A:

- **Phase 3 (type surfaces):** New `.d.ts` files for the cookbook module go in
  `content/cookbook/types/` as source, and `02i` copies them to
  `L1-raw/cookbook/types/`. Alternatively, the `05c` script extension can
  generate them directly into the release-tree `cookbook/types/` directory
  (following the existing `ucode.d.ts` pattern which is generated by `05c`,
  not extracted).

- **Phase 4 (per-module AGENTS.md):** The `05b` extension generates these into
  the release-tree. No change needed — cookbook is a normal module by this point.

- **Phase 4 (llms-mini.txt):** The `06` extension generates this into the
  release-tree root. Cookbook will be listed automatically since it's a
  recognized module.

- **Phase 5 (XML export):** If implemented as `05e`, it scans L2-semantic or
  release-tree for modules. Cookbook is present in both, so it works
  automatically.

---

## 7. Updated guardrails for implementing agents

These replace guardrail #6 from the previous plan and add new ones:

1. **Cookbook source content goes in `content/cookbook/`, not in
   `release-inputs/`, `openwrt-condensed-docs/`, or `templates/`.** (Assuming
   Option X is chosen for source location.)

2. **Cookbook source files must be pure Markdown starting with an H1 heading.**
   Do NOT add YAML frontmatter — stage 03 injects it automatically. If you
   add frontmatter, stage 03 will detect and skip it, or double-inject.

3. **Do NOT modify stages 03, 05a, 07, or 08 for cookbook support.** The
   L1 extractor approach makes all of these work automatically. If you find
   yourself editing these scripts to handle cookbook, you're on the wrong path.

4. **The only required modification to an existing script is one dictionary
   entry in stage 06** (`MODULE_CATEGORIES`). If you find yourself making
   more extensive changes to existing scripts, stop and verify your approach.

5. **The `02i` extractor has no dependency on `01` (clone-repos).** It reads
   from `content/cookbook/` which is always available in the repo. Do not gate
   it on the `initialize` job in CI.

6. **Do NOT rename `04-generate-ai-summaries.py`.** The L1 extractor approach
   (Option A) avoids the `04` → `04a` rename entirely. If you're adding a
   `04b` script, you've chosen Option B, not Option A.

7. All other guardrails from `enhancement-plan-opusmax.md` §5 remain in
   effect (don't reorganize modules, follow existing script patterns, use
   relative Markdown links, Windows path compat, etc.).

---

## 8. Decision summary

The owner must choose:

| Decision | Recommended | Alternatives |
| --- | --- | --- |
| Pipeline integration | **Option A** (L1 extractor, `02i`) | Option B (L2 injection, `04b`), Option C (early overlay), Option D (full renumber) |
| Source location | **Option X** (`content/cookbook/`) | Option Y (`templates/cookbook/`), Option Z (`.github/scripts/cookbook-source/`) |

The recommended combination (A+X) requires:
- 1 new script (~60 lines)
- 1 new directory (`content/cookbook/`) with 14–17 Markdown files
- 1 line added to an existing script
- 2 documentation files updated
- 1 workflow YAML update

No existing scripts renamed. No existing contracts changed. No validation
logic modified.
