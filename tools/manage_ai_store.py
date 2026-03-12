"""
Purpose: Orchestrate scratch-first AI summary store operations from one CLI.
Phase: AI Maintenance / Operations
Layers: data/base + data/override + L2 -> scratch store -> optional promotion
Inputs:  - data/base/                         (authoritative base store)
         - data/override/                     (authoritative override store)
         - OUTDIR/L2-semantic/                (current L2 source corpus)
         - LOCAL_DEV_TOKEN / GITHUB_TOKEN     (optional live API token)
Outputs: - scratch area under tmp/ai-summary-run/
         - optional promoted JSON updates in data/base/
Environment Variables:
  OUTDIR               Source L2 root parent for scratch preparation.
  AI_DATA_BASE_DIR     Permanent base store root.
  AI_DATA_OVERRIDE_DIR Permanent override store root.
  LOCAL_DEV_TOKEN      Preferred local token for live AI generation.
  GITHUB_TOKEN         Fallback token for live AI generation.
Dependencies: lib.ai_enrichment, lib.ai_store_checks, lib.ai_store_workflow
Notes: Local support CLI only. Numbered pipeline stages remain under
       .github/scripts/.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import ai_enrichment, ai_store_checks, ai_store_workflow


PREFIX = "[manage-ai-store]"


def run_generate(
    paths: ai_store_workflow.OperationPaths,
    args: argparse.Namespace,
) -> None:
    """Run stage 04 against the prepared scratch store and scratch L2 corpus."""
    ai_store_workflow.ensure_directory_exists(
        paths.scratch_base_dir,
        "scratch base store",
    )
    ai_store_workflow.ensure_directory_exists(
        paths.scratch_override_dir,
        "scratch override store",
    )
    ai_store_workflow.ensure_directory_exists(
        paths.scratch_l2_root,
        "scratch L2 semantic corpus",
    )

    token_value, token_source = ai_store_workflow.resolve_token_value(
        write_ai=args.write_ai,
        token_env=args.token_env,
        environ=os.environ,
    )
    if token_value and token_source:
        print(f"{PREFIX} Using token from {token_source}")

    exit_code = ai_enrichment.run_ai_enrichment(
        outdir=str(paths.scratch_outdir),
        base_dir=str(paths.scratch_base_dir),
        override_dir=str(paths.scratch_override_dir),
        legacy_cache_path=str(paths.scratch_cache_path),
        skip_ai=False,
        write_ai=args.write_ai,
        max_files=args.max_ai_files,
        token=token_value,
        validate_payload=True,
        report_prefix=PREFIX,
    )
    if exit_code != 0:
        raise RuntimeError("AI generation failed")


def run_validate_for_paths(
    *,
    base_dir: Path,
    override_dir: Path,
    l2_root: Path,
) -> None:
    """Validate one AI store root against one specific L2 corpus."""
    ai_store_workflow.ensure_directory_exists(base_dir, "base store")
    ai_store_workflow.ensure_directory_exists(override_dir, "override store")
    ai_store_workflow.ensure_directory_exists(l2_root, "L2 semantic corpus")

    result = ai_store_checks.validate_store(
        store="both",
        base_dir=str(base_dir),
        override_dir=str(override_dir),
        l2_root=str(l2_root),
    )
    ai_store_checks.print_validation_report(PREFIX, result)
    if result.errors:
        raise RuntimeError("AI store validation failed")


def run_audit_for_paths(
    *,
    base_dir: Path,
    override_dir: Path,
    l2_root: Path,
    strict_audit: bool,
) -> None:
    """Audit one AI store root against one specific L2 corpus."""
    ai_store_workflow.ensure_directory_exists(base_dir, "base store")
    ai_store_workflow.ensure_directory_exists(override_dir, "override store")
    ai_store_workflow.ensure_directory_exists(l2_root, "L2 semantic corpus")

    counts, details, issues = ai_store_checks.audit_store(
        l2_root=str(l2_root),
        base_dir=str(base_dir),
        override_dir=str(override_dir),
    )
    if issues:
        for issue in issues:
            print(f"{PREFIX} FAIL: {issue}")
        raise RuntimeError("AI store audit failed")

    ai_store_checks.print_audit_report(PREFIX, counts, details)

    failures = ai_store_checks.audit_failure_labels(
        counts,
        fail_on_missing=strict_audit,
        fail_on_stale=strict_audit,
        fail_on_orphan=strict_audit,
        fail_on_invalid=strict_audit,
    )
    if failures:
        raise RuntimeError(f"AI store audit failed: {', '.join(failures)}")


def run_validate(paths: ai_store_workflow.OperationPaths) -> None:
    """Validate the current scratch store against the current scratch L2 corpus."""
    run_validate_for_paths(
        base_dir=paths.scratch_base_dir,
        override_dir=paths.scratch_override_dir,
        l2_root=paths.scratch_l2_root,
    )


def run_audit(
    paths: ai_store_workflow.OperationPaths,
    *,
    strict_audit: bool,
) -> None:
    """Audit the current scratch store against the current scratch L2 corpus."""
    run_audit_for_paths(
        base_dir=paths.scratch_base_dir,
        override_dir=paths.scratch_override_dir,
        l2_root=paths.scratch_l2_root,
        strict_audit=strict_audit,
    )


def run_promote(
    paths: ai_store_workflow.OperationPaths,
    *,
    strict_audit: bool,
) -> None:
    """Promote reviewed scratch JSON into the permanent base store and re-check."""
    copied = ai_store_workflow.promote_base_records(
        paths.scratch_base_dir,
        paths.permanent_base_dir,
    )
    print(
        f"{PREFIX} Promoted {copied} JSON records into "
        f"{paths.permanent_base_dir}"
    )

    run_validate_for_paths(
        base_dir=paths.permanent_base_dir,
        override_dir=paths.permanent_override_dir,
        l2_root=paths.permanent_l2_root,
    )
    run_audit_for_paths(
        base_dir=paths.permanent_base_dir,
        override_dir=paths.permanent_override_dir,
        l2_root=paths.permanent_l2_root,
        strict_audit=strict_audit,
    )


def execute_action(
    action: str,
    *,
    paths: ai_store_workflow.OperationPaths,
    args: argparse.Namespace,
) -> None:
    """Dispatch one concrete action from the selected option sequence."""
    if action == "prepare":
        ai_store_workflow.prepare_scratch(paths)
        print(f"{PREFIX} Prepared scratch root: {paths.scratch_root}")
        print(f"{PREFIX} Scratch L2 source: {paths.scratch_l2_root}")
        print(f"{PREFIX} Scratch base store: {paths.scratch_base_dir}")
        print(f"{PREFIX} Scratch override store: {paths.scratch_override_dir}")
        return

    if action == "generate":
        run_generate(paths, args)
        return

    if action == "validate":
        run_validate(paths)
        return

    if action == "audit":
        run_audit(paths, strict_audit=args.strict_audit)
        return

    if action == "promote":
        run_promote(paths, strict_audit=args.strict_audit)
        return

    if action == "cleanup":
        ai_store_workflow.cleanup_scratch(paths)
        print(f"{PREFIX} Removed scratch root: {paths.scratch_root}")
        return

    raise ValueError(f"Unsupported action: {action}")


def build_argument_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser for AI store operations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--option",
        choices=ai_store_workflow.OPTION_CHOICES,
        default="review",
        help="Operation mode to run (default: review)",
    )
    parser.add_argument(
        "--scratch-root",
        default="tmp/ai-summary-run",
        help=(
            "Scratch root used for copied L2 and AI-store data "
            "(default: tmp/ai-summary-run)"
        ),
    )
    parser.add_argument(
        "--max-ai-files",
        type=int,
        default=300,
        help="Maximum live API generations when stage 04 runs (default: 300)",
    )
    parser.add_argument(
        "--token-env",
        default=None,
        help="Specific environment variable to use for live AI generation",
    )
    parser.add_argument(
        "--write-ai",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Allow live API generation during the generate step (default: true)",
    )
    parser.add_argument(
        "--strict-audit",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Fail audit on missing, stale, orphan, or invalid records",
    )
    parser.add_argument(
        "--keep-scratch",
        action="store_true",
        help="Preserve scratch data after a successful full run",
    )
    return parser


def main() -> int:
    """Run the selected AI-store workflow."""
    parser = build_argument_parser()
    args = parser.parse_args()
    paths = ai_store_workflow.build_operation_paths(args.scratch_root)
    actions = ai_store_workflow.expand_option_sequence(args.option)

    print(f"{PREFIX} Option: {args.option}")
    print(f"{PREFIX} Scratch root: {paths.scratch_root}")
    print(f"{PREFIX} Source OUTDIR: {paths.source_outdir}")
    print(f"{PREFIX} Permanent base store: {paths.permanent_base_dir}")
    print(f"{PREFIX} Permanent override store: {paths.permanent_override_dir}")

    try:
        for action in actions:
            print(f"{PREFIX} Action: {action}")
            execute_action(action, paths=paths, args=args)
    except Exception as exc:
        print(f"{PREFIX} FAIL: {exc}")
        return 1

    if args.option == "full" and not args.keep_scratch:
        ai_store_workflow.cleanup_scratch(paths)
        print(f"{PREFIX} Removed scratch root: {paths.scratch_root}")

    print(f"{PREFIX} Complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())