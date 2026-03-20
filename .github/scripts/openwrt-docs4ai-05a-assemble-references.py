"""
Purpose: Assemble L4 references and L3 skeletons from L2 semantics.
Phase: Assembly
Layers: L2 -> L3/L4
Inputs: OUTDIR/L2-semantic/
Outputs: OUTDIR/{module}/{module}-complete-reference.md,
         OUTDIR/{module}/{module}-complete-reference.part-*.md,
         OUTDIR/{module}/{module}-skeleton.md
Environment Variables: OUTDIR
Dependencies: pyyaml, lib.config
Notes: Strips internal L2 YAML, injects L4 wrapper YAML, and shards oversized
       complete references while preserving the stable index filename.
"""

from __future__ import annotations

import datetime
import glob
import os
import re
import shutil
import sys
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

try:
    import yaml
except ImportError:
    print("[05a] FAIL: 'pyyaml' package not installed")
    sys.exit(1)

OUTDIR = config.OUTDIR
L2_DIR = os.path.join(OUTDIR, "L2-semantic")
MAX_MONOLITH_TOKENS = 100_000
RELEASE_TREE_DIR = config.RELEASE_TREE_DIR
RELEASE_PART_PREFIX = config.MODULE_BUNDLED_REF_FILENAME.removesuffix(".md") + ".part-"


def legacy_part_filename(module: str, part_number: int) -> str:
    """Return the internal sharded part filename for one module."""
    return f"{module}-complete-reference.part-{part_number:02d}.md"


def release_part_filename(part_number: int) -> str:
    """Return the release-tree sharded part filename."""
    return f"{RELEASE_PART_PREFIX}{part_number:02d}.md"


def rewrite_relative_links(module: str, body_text: str) -> str:
    """Rewrite L2-relative markdown links so they remain valid from L4 files."""
    body_with_fixed_links = re.sub(
        r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+/.*?\.md)\)',
        r'[\1](../L2-semantic/\2)',
        body_text,
    )
    body_with_fixed_links = re.sub(
        r'\[(.*?)\]\(\./(.*?\.md)\)',
        f'[\\1](../L2-semantic/{module}/\\2)',
        body_with_fixed_links,
    )
    return body_with_fixed_links


def rewrite_release_relative_links(body_text: str) -> str:
    """Rewrite L2-relative markdown links for release-tree bundled outputs."""
    body_with_fixed_links = re.sub(
        r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)',
        rf'[\1](../\2/{config.MODULE_CHUNKED_REF_DIRNAME}/\3)',
        body_text,
    )
    body_with_fixed_links = re.sub(
        r'\[(.*?)\]\(\./(.*?\.md)\)',
        rf'[\1](./{config.MODULE_CHUNKED_REF_DIRNAME}/\2)',
        body_with_fixed_links,
    )
    return body_with_fixed_links


def rewrite_release_chunked_links(content: str) -> str:
    """Rewrite cross-module L2 links for copied chunked-reference pages."""
    return re.sub(
        r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)',
        rf'[\1](../../\2/{config.MODULE_CHUNKED_REF_DIRNAME}/\3)',
        content,
    )


def append_skeleton_lines(
    skeleton_lines: list[str],
    frontmatter: dict[str, Any],
    body_text: str,
) -> None:
    """Append summary, headings, and short signatures for the module skeleton."""
    if frontmatter.get("ai_summary"):
        skeleton_lines.append(f"> **Summary:** {frontmatter['ai_summary']}")
    if frontmatter.get("ai_when_to_use"):
        skeleton_lines.append(f"> **Use Case:** {frontmatter['ai_when_to_use']}")

    for line in body_text.splitlines():
        if line.startswith("#"):
            skeleton_lines.append(line)
        elif re.match(r'^[-*]\s+[`*_a-zA-Z0-9]', line):
            if "(" in line and ")" in line and len(line) < 150:
                signature = re.split(r'[:|—\-]\s', line, maxsplit=1)[0].strip()
                skeleton_lines.append(signature)

    skeleton_lines.append("")


def load_l2_sections(
    module: str,
    md_files: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Load validated L2 sections and skeleton lines for one module."""
    sections: list[dict[str, Any]] = []
    skeleton_lines: list[str] = []

    for fpath in md_files:
        try:
            with open(fpath, encoding="utf-8") as handle:
                content = handle.read().strip()
        except Exception as exc:
            print(f"[05a] WARN: Could not read {fpath}: {exc}")
            continue

        fm_match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?(.*)', content, re.DOTALL)
        if not fm_match:
            print(f"[05a] WARN: Invalid L2 schema in {fpath}")
            continue

        fm_text = fm_match.group(1)
        body_text = fm_match.group(2).strip()

        try:
            frontmatter = yaml.safe_load(fm_text) or {}
        except Exception as exc:
            print(f"[05a] WARN: YAML parse error in {fpath}: {exc}")
            continue

        token_count = int(frontmatter.get("token_count", 0) or 0)
        sections.append(
            {
                "path": fpath,
                "token_count": token_count,
                "body_text": rewrite_relative_links(module, body_text),
                "release_body_text": rewrite_release_relative_links(body_text),
            }
        )
        append_skeleton_lines(skeleton_lines, frontmatter, body_text)

    return sections, skeleton_lines


def build_reference_layout(
    module: str,
    sections: list[dict[str, Any]],
    token_limit: int = MAX_MONOLITH_TOKENS,
) -> dict[str, Any]:
    """Plan whether a module emits one reference file or a sharded set."""
    total_tokens = sum(int(section["token_count"]) for section in sections)
    layout: dict[str, Any] = {
        "module": module,
        "total_token_count": total_tokens,
        "section_count": len(sections),
        "sharded": total_tokens > token_limit,
        "parts": [],
    }
    if not layout["sharded"]:
        return layout

    chunk_sections: list[dict[str, Any]] = []
    chunk_tokens = 0
    chunks: list[dict[str, Any]] = []

    for section in sections:
        section_tokens = int(section["token_count"])
        if chunk_sections and chunk_tokens + section_tokens > token_limit:
            chunks.append({"sections": chunk_sections, "token_count": chunk_tokens})
            chunk_sections = []
            chunk_tokens = 0

        chunk_sections.append(section)
        chunk_tokens += section_tokens

    if chunk_sections:
        chunks.append({"sections": chunk_sections, "token_count": chunk_tokens})

    part_count = len(chunks)
    layout["parts"] = [
        {
            "part_number": index,
            "part_count": part_count,
            "section_count": len(chunk["sections"]),
            "token_count": int(chunk["token_count"]),
            "sections": chunk["sections"],
        }
        for index, chunk in enumerate(chunks, start=1)
    ]
    return layout


def join_reference_sections(
    sections: list[dict[str, Any]],
    body_key: str = "body_text",
) -> str:
    """Join section bodies into one deterministic L4 markdown payload."""
    joined = "\n\n---\n\n".join(str(section[body_key]) for section in sections)
    return joined.rstrip() + "\n"


def write_yaml_frontmatter(handle, payload: dict[str, Any]) -> None:
    """Write one top-level YAML block for a generated markdown file."""
    handle.write("---\n")
    handle.write(yaml.safe_dump(payload, sort_keys=False))
    handle.write("---\n\n")


def write_complete_reference(
    path: str,
    module: str,
    total_tokens: int,
    section_count: int,
    generated_at: str,
    body_text: str,
) -> None:
    """Write the stable single-file complete reference for one module."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        write_yaml_frontmatter(
            handle,
            {
                "module": module,
                "total_token_count": total_tokens,
                "section_count": section_count,
                "is_monolithic": True,
                "generated": generated_at,
            },
        )
        handle.write(f"# {module} Complete Reference\n\n")
        handle.write(f"> **Contains:** {section_count} documents concatenated\n")
        handle.write(f"> **Tokens:** ~{total_tokens} (cl100k_base)\n\n---\n\n")
        handle.write(body_text)


def write_sharded_reference_index(
    path: str,
    module: str,
    total_tokens: int,
    section_count: int,
    generated_at: str,
    parts: list[dict[str, Any]],
) -> None:
    """Write the stable complete-reference index for an oversized module."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        write_yaml_frontmatter(
            handle,
            {
                "module": module,
                "total_token_count": total_tokens,
                "section_count": section_count,
                "is_monolithic": False,
                "is_sharded_index": True,
                "part_count": len(parts),
                "generated": generated_at,
            },
        )
        handle.write(f"# {module} Complete Reference\n\n")
        handle.write(
            f"> **Contains:** {section_count} documents across {len(parts)} sharded parts\n"
        )
        handle.write(f"> **Tokens:** ~{total_tokens} (cl100k_base)\n")
        handle.write(
            f"> **Sharding Rule:** The module exceeded the {MAX_MONOLITH_TOKENS} token budget, so use one of the smaller parts below for deep context.\n\n"
        )
        handle.write("## Reference Parts\n\n")
        for part in parts:
            filename = legacy_part_filename(module, int(part["part_number"]))
            handle.write(
                "- [{filename}](./{filename}): Part {part_number} of {part_count} "
                "(~{token_count} tokens, {section_count} documents)\n".format(
                    filename=filename,
                    part_number=part["part_number"],
                    part_count=part["part_count"],
                    token_count=part["token_count"],
                    section_count=part["section_count"],
                )
            )
        handle.write("\n")


def write_sharded_reference_part(
    path: str,
    module: str,
    generated_at: str,
    part: dict[str, Any],
) -> None:
    """Write one sharded complete-reference part for an oversized module."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        write_yaml_frontmatter(
            handle,
            {
                "module": module,
                "total_token_count": part["token_count"],
                "section_count": part["section_count"],
                "is_monolithic": False,
                "is_sharded_part": True,
                "part_number": part["part_number"],
                "part_count": part["part_count"],
                "generated": generated_at,
            },
        )
        handle.write(
            f"# {module} Complete Reference (Part {part['part_number']} of {part['part_count']})\n\n"
        )
        handle.write(f"> **Contains:** {part['section_count']} documents\n")
        handle.write(f"> **Tokens:** ~{part['token_count']} (cl100k_base)\n")
        handle.write(
            f"> **Index:** [./{module}-complete-reference.md](./{module}-complete-reference.md)\n\n---\n\n"
        )
        handle.write(join_reference_sections(part["sections"]))


def write_release_complete_reference(
    path: str,
    module: str,
    total_tokens: int,
    section_count: int,
    generated_at: str,
    sections: list[dict[str, Any]],
) -> None:
    """Write the release-tree bundled reference for one module."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        write_yaml_frontmatter(
            handle,
            {
                "module": module,
                "total_token_count": total_tokens,
                "section_count": section_count,
                "is_monolithic": True,
                "generated": generated_at,
            },
        )
        handle.write(f"# {module} Bundled Reference\n\n")
        handle.write(f"> **Contains:** {section_count} documents concatenated\n")
        handle.write(f"> **Tokens:** ~{total_tokens} (cl100k_base)\n\n---\n\n")
        handle.write(join_reference_sections(sections, body_key="release_body_text"))


def write_release_sharded_reference_index(
    path: str,
    module: str,
    total_tokens: int,
    section_count: int,
    generated_at: str,
    parts: list[dict[str, Any]],
) -> None:
    """Write the release-tree bundled-reference index for an oversized module."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        write_yaml_frontmatter(
            handle,
            {
                "module": module,
                "total_token_count": total_tokens,
                "section_count": section_count,
                "is_monolithic": False,
                "is_sharded_index": True,
                "part_count": len(parts),
                "generated": generated_at,
            },
        )
        handle.write(f"# {module} Bundled Reference\n\n")
        handle.write(
            f"> **Contains:** {section_count} documents across {len(parts)} sharded parts\n"
        )
        handle.write(f"> **Tokens:** ~{total_tokens} (cl100k_base)\n")
        handle.write(
            f"> **Sharding Rule:** The module exceeded the {MAX_MONOLITH_TOKENS} token budget, so use one of the smaller parts below for deep context.\n\n"
        )
        handle.write("## Reference Parts\n\n")
        for part in parts:
            filename = release_part_filename(int(part["part_number"]))
            handle.write(
                "- [{filename}](./{filename}): Part {part_number} of {part_count} "
                "(~{token_count} tokens, {section_count} documents)\n".format(
                    filename=filename,
                    part_number=part["part_number"],
                    part_count=part["part_count"],
                    token_count=part["token_count"],
                    section_count=part["section_count"],
                )
            )
        handle.write("\n")


def write_release_sharded_reference_part(
    path: str,
    module: str,
    generated_at: str,
    part: dict[str, Any],
) -> None:
    """Write one release-tree bundled-reference shard."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        write_yaml_frontmatter(
            handle,
            {
                "module": module,
                "total_token_count": part["token_count"],
                "section_count": part["section_count"],
                "is_monolithic": False,
                "is_sharded_part": True,
                "part_number": part["part_number"],
                "part_count": part["part_count"],
                "generated": generated_at,
            },
        )
        handle.write(
            f"# {module} Bundled Reference (Part {part['part_number']} of {part['part_count']})\n\n"
        )
        handle.write(f"> **Contains:** {part['section_count']} documents\n")
        handle.write(f"> **Tokens:** ~{part['token_count']} (cl100k_base)\n")
        handle.write(
            f"> **Index:** [./{config.MODULE_BUNDLED_REF_FILENAME}](./{config.MODULE_BUNDLED_REF_FILENAME})\n\n---\n\n"
        )
        handle.write(join_reference_sections(part["sections"], body_key="release_body_text"))


def write_release_map(
    path: str,
    module: str,
    generated_at: str,
    skeleton_lines: list[str],
) -> None:
    """Write the release-tree navigation map for one module."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# {module} Navigation Map\n\n")
        handle.write(f"> **Contains:** Headers and function signatures for {module}.\n")
        handle.write(f"> **Generated:** {generated_at}\n\n---\n\n")
        handle.write("\n".join(skeleton_lines).strip())
        handle.write("\n")


def write_skeleton(
    path: str,
    module: str,
    generated_at: str,
    skeleton_lines: list[str],
) -> None:
    """Write the compact skeleton map for one module."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# {module} (Skeleton Semantic Map)\n\n")
        handle.write(f"> **Contains:** Headers and function signatures for {module}.\n")
        handle.write(f"> **Generated:** {generated_at}\n\n---\n\n")
        handle.write("\n".join(skeleton_lines).strip())
        handle.write("\n")


def copy_release_chunked_pages(md_files: list[str], out_mod_dir: str) -> None:
    """Copy L2 semantic pages into the release-tree chunked-reference folder."""
    chunked_dir = os.path.join(out_mod_dir, config.MODULE_CHUNKED_REF_DIRNAME)
    os.makedirs(chunked_dir, exist_ok=True)

    for fpath in md_files:
        with open(fpath, "r", encoding="utf-8") as handle:
            content = handle.read().strip()
        out_path = os.path.join(chunked_dir, os.path.basename(fpath))
        with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rewrite_release_chunked_links(content).rstrip() + "\n")

def main() -> int:
    """Assemble publishable L4 references and L3 skeletons from staged L2 files."""
    if not os.path.isdir(L2_DIR):
        print(f"[05a] FAIL: L2 semantic directory not found: {L2_DIR}")
        return 1

    modules = [d for d in os.listdir(L2_DIR) if os.path.isdir(os.path.join(L2_DIR, d))]
    if not modules:
        print("[05a] FAIL: No modules found in L2 semantic directory.")
        return 1

    if os.path.isdir(RELEASE_TREE_DIR):
        shutil.rmtree(RELEASE_TREE_DIR)
    os.makedirs(RELEASE_TREE_DIR, exist_ok=True)

    generated_at = datetime.datetime.now(datetime.UTC).isoformat()
    warn_count = 0
    outputs_generated = 0

    print("[05a] Assemble L4 monolithic files and L3 skeletons")

    for module in sorted(modules):
        mod_dir = os.path.join(L2_DIR, module)
        md_files = sorted(glob.glob(os.path.join(mod_dir, "*.md")))
        if not md_files:
            continue

        print(f"[05a] Processing module: {module} ({len(md_files)} files)")

        sections, skeleton_lines = load_l2_sections(module, md_files)
        layout = build_reference_layout(module, sections)

        out_mod_dir = os.path.join(OUTDIR, module)
        os.makedirs(out_mod_dir, exist_ok=True)

        l4_path = os.path.join(out_mod_dir, f"{module}-complete-reference.md")
        l3_skeleton_path = os.path.join(out_mod_dir, f"{module}-skeleton.md")

        if layout["sharded"]:
            write_sharded_reference_index(
                l4_path,
                module,
                int(layout["total_token_count"]),
                int(layout["section_count"]),
                generated_at,
                layout["parts"],
            )
            outputs_generated += 1

            for part in layout["parts"]:
                write_sharded_reference_part(
                    os.path.join(
                        out_mod_dir,
                        legacy_part_filename(module, int(part["part_number"])),
                    ),
                    module,
                    generated_at,
                    part,
                )
                outputs_generated += 1
                if int(part["token_count"]) > MAX_MONOLITH_TOKENS:
                    print(
                        "[05a] WARN: {module} reference part {part_number} exceeds "
                        "{limit} tokens ({token_count})".format(
                            module=module,
                            part_number=part["part_number"],
                            limit=MAX_MONOLITH_TOKENS,
                            token_count=part["token_count"],
                        )
                    )
                    warn_count += 1
        else:
            write_complete_reference(
                l4_path,
                module,
                int(layout["total_token_count"]),
                int(layout["section_count"]),
                generated_at,
                join_reference_sections(sections),
            )
            outputs_generated += 1

        write_skeleton(l3_skeleton_path, module, generated_at, skeleton_lines)
        outputs_generated += 1

        release_mod_dir = os.path.join(RELEASE_TREE_DIR, module)
        os.makedirs(release_mod_dir, exist_ok=True)

        release_reference_path = os.path.join(
            release_mod_dir,
            config.MODULE_BUNDLED_REF_FILENAME,
        )
        release_map_path = os.path.join(
            release_mod_dir,
            config.MODULE_MAP_FILENAME,
        )

        if layout["sharded"]:
            write_release_sharded_reference_index(
                release_reference_path,
                module,
                int(layout["total_token_count"]),
                int(layout["section_count"]),
                generated_at,
                layout["parts"],
            )

            for part in layout["parts"]:
                write_release_sharded_reference_part(
                    os.path.join(
                        release_mod_dir,
                        release_part_filename(int(part["part_number"])),
                    ),
                    module,
                    generated_at,
                    part,
                )
        else:
            write_release_complete_reference(
                release_reference_path,
                module,
                int(layout["total_token_count"]),
                int(layout["section_count"]),
                generated_at,
                sections,
            )

        write_release_map(release_map_path, module, generated_at, skeleton_lines)
        copy_release_chunked_pages(md_files, release_mod_dir)

        if layout["sharded"]:
            print(
                "[05a] OK: {module} L4 index + {part_count} parts ({token_count} tokens) and L3 skeleton".format(
                    module=module,
                    part_count=len(layout["parts"]),
                    token_count=layout["total_token_count"],
                )
            )
        else:
            print(
                f"[05a] OK: {module} L4 ({layout['total_token_count']} tokens) and L3 skeleton"
            )

    print(f"[05a] Complete: {outputs_generated} artifacts generated.")
    if outputs_generated == 0:
        print("[05a] FAIL: Zero outputs generated.")
        return 1

    if warn_count > 0:
        print(f"[05a] Process finished with {warn_count} size warnings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
