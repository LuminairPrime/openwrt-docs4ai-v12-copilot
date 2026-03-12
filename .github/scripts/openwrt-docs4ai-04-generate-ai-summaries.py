"""
Purpose: Apply AI summaries to L2 documentation from the structured data store
                 and optionally generate new summaries via GitHub Models API.
Phase: AI Enrichment (Optional)
Layers: L2 -> L2 (In-place frontmatter mutation)
Inputs:  - OUTDIR/L2-semantic/                          (required L2 source)
                 - data/base/{module}/{slug}.json               (base data store)
                 - data/override/{module}/{slug}.json           (override data store)
                 - ai-summaries-cache.json                      (legacy; migrated on run)
Outputs: - OUTDIR/L2-semantic/{module}/*.md             (mutated: ai fields added)
                 - data/base/{module}/{slug}.json               (new entries when WRITE_AI)
Environment Variables:
    SKIP_AI          Skip entire step cleanly. Default: true for direct local
                                     execution; the hosted workflow sets it explicitly.
    WRITE_AI         Call API for files missing summaries. Default: true.
    MAX_AI_FILES     Cap on API calls per run. Default: 40.
    GITHUB_TOKEN     GitHub Models API bearer token.
    LOCAL_DEV_TOKEN  Local development token (fallback when GITHUB_TOKEN absent).
    AI_CACHE_PATH    Optional override for legacy ai-summaries-cache.json path.
    AI_DATA_BASE_DIR Override default data/base/ location.
    AI_DATA_OVERRIDE_DIR Override default data/override/ location.
    AI_VALIDATE_PAYLOAD  Validate AI payloads before injection. Default: true.
                                             Set to false only when debugging malformed API
                                             responses locally.
Dependencies: requests, pyyaml, lib.config, lib.ai_store

=========================== MANUAL AI GENERATION PROMPT ===========================
Use this block to generate a data/base/{module}/{slug}.json file manually.
Paste an L2 file below the divider line, run the prompt in any capable LLM
(GitHub Copilot Chat, Claude, ChatGPT, etc.), then copy the JSON output into
data/base/{module}/{slug}.json.

## Task: openwrt-docs4ai AI Summary Generation

Generate a structured AI summary record for an OpenWrt documentation file.

### Output format
Return ONLY a valid JSON object with exactly these fields:
{
  "slug":              "<L2 filename without .md extension>",
  "module":            "<parent folder: ucode|luci|procd|uci|wiki|...>",
  "title":             "<value of the 'title' YAML field in the file>",
  "content_hash":      null,
    "ai_summary":        "<3-5 sentences. Sentence 1 is comprehensive; remaining sentences provide details/clarifications and name exact functions.>",
  "ai_when_to_use":    "<1-2 sentences: when is this the right tool in OpenWrt?>",
  "ai_related_topics": ["<exact symbol name found in the text>", "..."],
  "generated_at":      "<ISO 8601 timestamp>",
  "model":             "manual",
  "pipeline_version":  "v12"
}

### Rules
- ai_summary sentence 1 must be a comprehensive one-sentence overview of the entire page.
- ai_summary sentences 2+ must add details/clarifications and name exact symbols present in the body.
- Prefer 3-5 sentences unless the source page is extremely short.
- ai_related_topics must contain 4-10 exact symbol names present in the content.
- content_hash must be null (marks this as human-authored, never auto-invalidated).
- Do NOT include any text outside the JSON object.
- Do NOT hallucinate symbols not present in the provided content.

[PASTE L2 FILE CONTENT BELOW THIS LINE]
====================================================================================
"""

import os
import sys
from typing import Any, cast

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import ai_enrichment, config

cast(Any, sys.stdout).reconfigure(line_buffering=True)

OUTDIR = config.OUTDIR
SKIP_AI = os.environ.get("SKIP_AI", "true").lower() == "true"
WRITE_AI = os.environ.get("WRITE_AI", "true").lower() == "true"
MAX_FILES = int(os.environ.get("MAX_AI_FILES", "40"))
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("LOCAL_DEV_TOKEN")
VALIDATE_PAYLOAD = os.environ.get("AI_VALIDATE_PAYLOAD", "true").lower() != "false"

# Legacy flat cache — migrated opportunistically on first run that encounters it
_LEGACY_CACHE_PATH = os.path.abspath(
    os.environ.get(
        "AI_CACHE_PATH",
        os.path.join(os.path.dirname(__file__), "..", "..", "ai-summaries-cache.json"),
    )
)

def main() -> int:
    """Run the stage-04 AI enrichment step against the configured output tree."""
    return ai_enrichment.run_ai_enrichment(
        outdir=OUTDIR,
        base_dir=os.environ.get("AI_DATA_BASE_DIR", config.AI_DATA_BASE_DIR),
        override_dir=os.environ.get(
            "AI_DATA_OVERRIDE_DIR",
            config.AI_DATA_OVERRIDE_DIR,
        ),
        legacy_cache_path=_LEGACY_CACHE_PATH,
        skip_ai=SKIP_AI,
        write_ai=WRITE_AI,
        max_files=MAX_FILES,
        token=TOKEN,
        validate_payload=VALIDATE_PAYLOAD,
        report_prefix="[04]",
    )


if __name__ == "__main__":
    raise SystemExit(main())

