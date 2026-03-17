"""
Purpose: Assemble the V5a release-tree and support-tree from staged output.
Phase: Release Assembly
Layers: L3/L4 -> release-tree/support-tree
Inputs: OUTDIR/
Outputs: OUTDIR/release-tree/, OUTDIR/support-tree/
Environment Variables: OUTDIR, ENABLE_RELEASE_TREE
Dependencies: lib.config
Notes: Preserves the existing OUTDIR contract while producing the V5a layout
       behind a feature flag.
"""

from __future__ import annotations

import datetime
import glob
import html
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

OUTDIR = config.OUTDIR
RELEASE_TREE_DIR = config.RELEASE_TREE_DIR
SUPPORT_TREE_DIR = config.SUPPORT_TREE_DIR
MODULE_L2_ROOT = os.path.join(OUTDIR, "L2-semantic")
L1_RAW_ROOT = os.path.join(OUTDIR, "L1-raw")
PART_PREFIX = config.MODULE_BUNDLED_REF_FILENAME.removesuffix(".md") + ".part-"
ROOT_RELEASE_FILES = [
    "llms.txt",
    "llms-full.txt",
    "README.md",
    "AGENTS.md",
    "index.html",
]
RELEASE_TREE_ROOT_SECTION = "__root__"
RELEASE_TREE_ROOT_FILES = [
    "index.html",
    "README.md",
    "llms.txt",
    "llms-full.txt",
    "AGENTS.md",
]


def log(status: str, message: str) -> None:
    """Write one stage-prefixed log line."""
    print(f"[05e] {status}: {message}")


def reset_directory(path: str) -> None:
    """Recreate one generated output directory from scratch."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def copy_tree(src: str, dst: str) -> None:
    """Copy one directory tree with metadata preservation."""
    shutil.copytree(src, dst, copy_function=shutil.copy2, dirs_exist_ok=True)


def write_text(path: str, content: str) -> None:
    """Write UTF-8 text with normalized newlines."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def read_text(path: str) -> str:
    """Read one UTF-8 text file."""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def summarize_paths(paths: list[str], limit: int = 5) -> str:
    """Return a short preview for one list of copied overlay paths."""
    preview = paths[:limit]
    if len(paths) > limit:
        preview.append(f"... (+{len(paths) - limit} more)")
    return ", ".join(preview)


def module_legacy_paths(module: str) -> list[tuple[str, str]]:
    """Return module-local path rewrites for copied text content."""
    return [
        (f"{module}-skeleton.md", config.MODULE_MAP_FILENAME),
        (
            f"{module}-complete-reference.md",
            config.MODULE_BUNDLED_REF_FILENAME,
        ),
        (
            f"{module}-complete-reference.part-",
            PART_PREFIX,
        ),
        (
            f"{module}.d.ts",
            f"{config.MODULE_TYPES_DIRNAME}/{module}.d.ts",
        ),
        (f"./{module}-skeleton.md", f"./{config.MODULE_MAP_FILENAME}"),
        (
            f"./{module}-complete-reference.md",
            f"./{config.MODULE_BUNDLED_REF_FILENAME}",
        ),
        (
            f"./{module}-complete-reference.part-",
            f"./{PART_PREFIX}",
        ),
        (
            f"../L2-semantic/{module}/",
            f"./{config.MODULE_CHUNKED_REF_DIRNAME}/",
        ),
        (
            f"./{module}.d.ts",
            f"./{config.MODULE_TYPES_DIRNAME}/{module}.d.ts",
        ),
    ]


def bundled_reference_paths(current_module: str, modules: list[str]) -> list[tuple[str, str]]:
    """Return link rewrites for files stored at release-tree/{module}/."""
    replacements = module_legacy_paths(current_module)
    for module in modules:
        if module == current_module:
            target_prefix = f"./{config.MODULE_CHUNKED_REF_DIRNAME}/"
        else:
            target_prefix = f"../{module}/{config.MODULE_CHUNKED_REF_DIRNAME}/"
        replacements.append((f"../L2-semantic/{module}/", target_prefix))
    return replacements


def chunked_reference_paths(current_module: str, modules: list[str]) -> list[tuple[str, str]]:
    """Return link rewrites for files stored at release-tree/{module}/chunked-reference/."""
    replacements = []
    for module in modules:
        if module == current_module:
            target_prefix = "./"
        else:
            target_prefix = f"../../{module}/{config.MODULE_CHUNKED_REF_DIRNAME}/"
        replacements.append((f"../{module}/", target_prefix))
        replacements.append((f"../L2-semantic/{module}/", target_prefix))
    return replacements


def root_legacy_paths(modules: list[str]) -> list[tuple[str, str]]:
    """Return root-level path rewrites for copied text content."""
    replacements = [
        ("./openwrt-condensed-docs/", "./"),
        ("openwrt-condensed-docs publish tree", "openwrt-docs4ai release tree"),
        (
            "including the intermediate L1 and L2\n            layers that are now part of the public mirror.",
            "including bundled references, chunked-reference pages,\n            and release-ready routing surfaces.",
        ),
        ("[module]/*-skeleton.md", "[module]/map.md"),
        (
            "[module]/*-complete-reference.md",
            "[module]/bundled-reference.md",
        ),
        ("[module]/*.d.ts", "[module]/types/*.d.ts"),
        (
            "Prefer `*-skeleton.md` files for orientation, then monolithic references, and only then individual L2 documents when deeper provenance is needed.",
            "Prefer `map.md` for orientation, then `bundled-reference.md`, and only then `chunked-reference/` topic documents when deeper provenance is needed.",
        ),
    ]
    for module in modules:
        replacements.extend(
            [
                (
                    f"{module}/{module}-skeleton.md",
                    f"{module}/{config.MODULE_MAP_FILENAME}",
                ),
                (
                    f"{module}/{module}-complete-reference.md",
                    f"{module}/{config.MODULE_BUNDLED_REF_FILENAME}",
                ),
                (
                    f"{module}/{module}-complete-reference.part-",
                    f"{module}/{PART_PREFIX}",
                ),
                (
                    f"L2-semantic/{module}/",
                    f"{module}/{config.MODULE_CHUNKED_REF_DIRNAME}/",
                ),
                (
                    f"{module}/{module}.d.ts",
                    f"{module}/{config.MODULE_TYPES_DIRNAME}/{module}.d.ts",
                ),
            ]
        )
    return replacements


def apply_replacements(content: str, replacements: list[tuple[str, str]]) -> str:
    """Apply a deterministic list of string replacements."""
    updated = content
    for old, new in replacements:
        updated = updated.replace(old, new)
    return updated


def rewrite_module_text(content: str, module: str) -> str:
    """Rewrite one module-local text file to the V5a layout."""
    return apply_replacements(content, module_legacy_paths(module))


def rewrite_bundled_reference_text(content: str, module: str, modules: list[str]) -> str:
    """Rewrite one bundled-reference or map text file to the V5a layout."""
    return apply_replacements(content, bundled_reference_paths(module, modules))


def rewrite_chunked_reference_text(content: str, module: str, modules: list[str]) -> str:
    """Rewrite one copied chunked-reference page to the V5a layout."""
    return apply_replacements(content, chunked_reference_paths(module, modules))


def rewrite_root_text(content: str, modules: list[str]) -> str:
    """Rewrite one root-level text file to the V5a layout."""
    return apply_replacements(content, root_legacy_paths(modules))


def release_root_file_sort_key(name: str) -> tuple[int, str]:
    """Keep release-tree root files in a human-first order."""
    try:
        return RELEASE_TREE_ROOT_FILES.index(name), name
    except ValueError:
        return len(RELEASE_TREE_ROOT_FILES), name


def release_section_file_sort_key(rel_path: str) -> tuple[int, str]:
    """Sort release-tree module files by router, map, bundled docs, and details."""
    parts = rel_path.split("/")
    filename = parts[-1]

    if filename == "llms.txt":
        return 0, filename
    if filename == config.MODULE_MAP_FILENAME:
        return 1, filename
    if filename == config.MODULE_BUNDLED_REF_FILENAME:
        return 2, filename
    if filename.startswith(PART_PREFIX):
        return 3, filename
    if len(parts) > 1 and parts[1] == config.MODULE_TYPES_DIRNAME and filename.endswith(".d.ts"):
        return 4, rel_path
    if len(parts) > 1 and parts[1] == config.MODULE_CHUNKED_REF_DIRNAME:
        return 5, rel_path
    return 6, rel_path


def iter_release_section_files(root: Path, section: str) -> list[str]:
    """Return publishable file paths for one release-tree top-level section."""
    if section == RELEASE_TREE_ROOT_SECTION:
        root_files = {path.name for path in root.iterdir() if path.is_file()}
        root_files.add("index.html")
        return sorted(root_files, key=release_root_file_sort_key)

    section_dir = root / section
    if not section_dir.is_dir():
        return []

    return sorted(
        (
            path.relative_to(root).as_posix()
            for path in section_dir.rglob("*")
            if path.is_file()
        ),
        key=release_section_file_sort_key,
    )


def collect_release_sections(root: Path, modules: list[str]) -> list[tuple[str, list[str]]]:
    """Collect release-tree sections using module order from the staged output."""
    sections: list[tuple[str, list[str]]] = []

    root_files = iter_release_section_files(root, RELEASE_TREE_ROOT_SECTION)
    if root_files:
        sections.append((RELEASE_TREE_ROOT_SECTION, root_files))

    known_modules = set(modules)
    for module in modules:
        files = iter_release_section_files(root, module)
        if files:
            sections.append((module, files))

    extra_sections = sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name not in known_modules
    )
    for section in extra_sections:
        files = iter_release_section_files(root, section)
        if files:
            sections.append((section, files))

    return sections


def describe_release_section(section: str, file_count: int) -> str:
    """Return a human-readable description for one release-tree section."""
    if section == RELEASE_TREE_ROOT_SECTION:
        base = (
            "Top-level routing files, catalogs, and landing pages for the "
            "published release tree."
        )
    else:
        base = (
            f"Release-ready routing files, bundled references, "
            f"chunked-reference pages, and generated type surfaces for {section}."
        )

    noun = "file" if file_count == 1 else "files"
    return f"{base} This section currently lists {file_count} published {noun}."


def release_section_heading(section: str) -> str:
    """Return the visible heading label for one release-tree section."""
    return "Root Files" if section == RELEASE_TREE_ROOT_SECTION else section


def release_section_slug(section: str) -> str:
    """Return an anchor-safe slug for one release-tree section."""
    return "root-files" if section == RELEASE_TREE_ROOT_SECTION else section


def render_release_section_nav(sections: list[tuple[str, list[str]]]) -> str:
    """Render a simple jump list for the release-tree landing page."""
    items = []
    for section, files in sections:
        items.append(
            "<li><a href=\"#{slug}\">{label}</a> <span>({count})</span></li>".format(
                slug=html.escape(release_section_slug(section)),
                label=html.escape(release_section_heading(section)),
                count=len(files),
            )
        )
    return "".join(items)


def render_release_section(section: str, files: list[str]) -> str:
    """Render one top-level release-tree section as HTML."""
    items = []
    for rel_path in files:
        items.append(
            "<li><a href=\"{href}\">{label}</a></li>".format(
                href=quote(rel_path),
                label=html.escape(f"./{rel_path}"),
            )
        )

    return "".join(
        [
            f"<section id=\"{html.escape(release_section_slug(section))}\">",
            f"<h2>{html.escape(release_section_heading(section))}</h2>",
            f"<p>{html.escape(describe_release_section(section, len(files)))}</p>",
            "<ul class=\"path-list\">",
            "".join(items),
            "</ul>",
            "</section>",
        ]
    )


def build_release_tree_index_html(root: Path, modules: list[str]) -> str:
    """Build a filesystem-derived index.html for the assembled release-tree."""
    generated_at = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    sections = collect_release_sections(root, modules)
    publish_file_count = sum(len(files) for _section, files in sections)
    rendered_sections = "".join(
        render_release_section(section, files) for section, files in sections
    )
    section_nav = render_release_section_nav(sections)

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>openwrt-docs4ai release tree</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #fbfbf7;
      --ink: #1f2328;
      --muted: #5a6472;
      --line: #d7d9d0;
      --panel: #f1f0e8;
      --link: #0f5c47;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Georgia, \"Times New Roman\", serif;
      line-height: 1.6;
    }}

    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 2rem 1.25rem 3rem;
    }}

    h1 {{
      margin: 0 0 0.75rem;
      padding-bottom: 0.75rem;
      border-bottom: 2px solid var(--line);
      font-size: clamp(2rem, 4vw, 3rem);
    }}

    h2 {{
      margin: 2rem 0 0.5rem;
      font-size: 1.5rem;
    }}

    p {{
      margin: 0 0 1rem;
      color: var(--muted);
      max-width: 72ch;
    }}

    section {{
      margin-top: 2rem;
      padding-top: 0.5rem;
      border-top: 1px solid var(--line);
    }}

    .path-list {{
      margin: 0;
      padding-left: 1.25rem;
    }}

    .path-list li {{
      margin: 0.25rem 0;
    }}

        .section-nav {{
            margin: 1.25rem 0 0;
            padding: 1rem 1.25rem;
            background: var(--panel);
            border: 1px solid var(--line);
        }}

        .section-nav h2 {{
            margin-top: 0;
            font-size: 1.1rem;
        }}

        .section-nav ul {{
            margin: 0;
            padding-left: 1.25rem;
            columns: 2 18rem;
            column-gap: 2rem;
        }}

        .section-nav li {{
            margin: 0.2rem 0;
        }}

        .section-nav span {{
            color: var(--muted);
            font-size: 0.95rem;
        }}

    .path-list a {{
      color: var(--link);
      font-family: \"Cascadia Code\", Consolas, \"Courier New\", monospace;
      text-decoration-thickness: 1px;
      overflow-wrap: anywhere;
    }}

    .meta {{
      margin-top: 2.5rem;
      padding-top: 1rem;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.95rem;
    }}
  </style>
</head>
<body>
  <main>
    <h1>openwrt-docs4ai release tree</h1>
    <p>
      This page is a filesystem-derived browse index for the published
      openwrt-docs4ai release tree. The link text mirrors the packaged
      layout inside this directory and each section maps to one
      top-level area of the public release surface.
    </p>
        <p>
            The current publish snapshot contains {publish_file_count} files across
            {len(sections)} top-level sections, including module routers,
            maps, bundled references, chunked-reference pages, and generated
            type surfaces where available.
        </p>
        <nav class=\"section-nav\" aria-label=\"Section navigation\">
            <h2>Jump to section</h2>
            <ul>
                {section_nav}
            </ul>
        </nav>
    {rendered_sections}
    <div class=\"meta\">
      Generated: {generated_at}<br>
      Pipeline version: v12
    </div>
  </main>
</body>
</html>
"""


def write_release_tree_index(modules: list[str]) -> None:
    """Generate a release-tree-native landing page from assembled output."""
    release_root = Path(RELEASE_TREE_DIR)
    write_text(
        str(release_root / "index.html"),
        build_release_tree_index_html(release_root, modules),
    )


def is_module_dir(path: str, name: str) -> bool:
    """Return True when one OUTDIR child is a module directory."""
    if not os.path.isdir(path):
        return False
    if name in {
        "L1-raw",
        "L2-semantic",
        os.path.basename(RELEASE_TREE_DIR),
        os.path.basename(SUPPORT_TREE_DIR),
    }:
        return False

    old_skeleton = os.path.join(path, f"{name}-skeleton.md")
    old_reference = os.path.join(path, f"{name}-complete-reference.md")
    new_map = os.path.join(path, config.MODULE_MAP_FILENAME)
    new_reference = os.path.join(path, config.MODULE_BUNDLED_REF_FILENAME)
    return (os.path.isfile(old_skeleton) and os.path.isfile(old_reference)) or (
        os.path.isfile(new_map) and os.path.isfile(new_reference)
    )


def collect_modules() -> list[str]:
    """Discover staged module directories inside OUTDIR."""
    modules = []
    for name in sorted(os.listdir(OUTDIR)):
        module_dir = os.path.join(OUTDIR, name)
        if is_module_dir(module_dir, name):
            modules.append(name)
    return modules


def copy_rewritten_text(src: str, dst: str, rewrite) -> None:
    """Copy one text file after applying a rewrite function."""
    write_text(dst, rewrite(read_text(src)))


def copy_optional_file(src: str, dst: str) -> bool:
    """Copy one optional file and report whether it existed."""
    if not os.path.isfile(src):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return True


def apply_release_include_overlay(
    release_tree_dir: str = RELEASE_TREE_DIR,
    include_dir: str = config.RELEASE_INCLUDE_DIR,
) -> list[str]:
    """Copy the common release include overlay on top of release-tree/."""
    if not os.path.isdir(include_dir):
        return []

    copied_paths: list[str] = []
    for root, dirs, files in os.walk(include_dir):
        dirs.sort()
        files.sort()
        for name in files:
            src_path = os.path.join(root, name)
            rel_path = os.path.relpath(src_path, include_dir)
            dst_path = os.path.join(release_tree_dir, rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            copied_paths.append(rel_path.replace("\\", "/"))
    return copied_paths


def copy_module_types(module: str, src_dir: str, dst_dir: str) -> None:
    """Copy module IDE helper files into the V5a types/ folder."""
    src_types_dir = os.path.join(src_dir, config.MODULE_TYPES_DIRNAME)
    dst_types_dir = os.path.join(dst_dir, config.MODULE_TYPES_DIRNAME)
    if os.path.isdir(src_types_dir):
        copy_tree(src_types_dir, dst_types_dir)
        return

    dts_paths = sorted(glob.glob(os.path.join(src_dir, "*.d.ts")))
    if not dts_paths:
        return

    os.makedirs(dst_types_dir, exist_ok=True)
    for dts_path in dts_paths:
        shutil.copy2(dts_path, os.path.join(dst_types_dir, os.path.basename(dts_path)))


def copy_module_chunked_reference(module: str, modules: list[str], dst_dir: str) -> None:
    """Copy L2 semantic pages into the module chunked-reference folder."""
    src_l2_dir = os.path.join(MODULE_L2_ROOT, module)
    if not os.path.isdir(src_l2_dir):
        log("WARN", f"skipping module with no L2 content: {module}")
        return

    dst_chunk_dir = os.path.join(dst_dir, config.MODULE_CHUNKED_REF_DIRNAME)
    copy_tree(src_l2_dir, dst_chunk_dir)

    for page_name in sorted(os.listdir(dst_chunk_dir)):
        if not page_name.endswith(".md"):
            continue
        page_path = os.path.join(dst_chunk_dir, page_name)
        write_text(
            page_path,
            rewrite_chunked_reference_text(read_text(page_path), module, modules),
        )


def copy_module_release_tree(module: str, modules: list[str]) -> None:
    """Copy one module into the V5a release-tree layout."""
    src_dir = os.path.join(OUTDIR, module)
    dst_dir = os.path.join(RELEASE_TREE_DIR, module)
    os.makedirs(dst_dir, exist_ok=True)

    old_reference_path = os.path.join(src_dir, f"{module}-complete-reference.md")
    if os.path.isfile(old_reference_path):
        copy_rewritten_text(
            old_reference_path,
            os.path.join(dst_dir, config.MODULE_BUNDLED_REF_FILENAME),
            lambda text: rewrite_bundled_reference_text(text, module, modules),
        )
    else:
        log("WARN", f"missing bundled reference source: {module}")

    old_part_glob = os.path.join(src_dir, f"{module}-complete-reference.part-*.md")
    for part_path in sorted(glob.glob(old_part_glob)):
        old_name = os.path.basename(part_path)
        new_name = old_name.replace(f"{module}-complete-reference.part-", PART_PREFIX)
        copy_rewritten_text(
            part_path,
            os.path.join(dst_dir, new_name),
            lambda text: rewrite_bundled_reference_text(text, module, modules),
        )

    old_map_path = os.path.join(src_dir, f"{module}-skeleton.md")
    if os.path.isfile(old_map_path):
        copy_rewritten_text(
            old_map_path,
            os.path.join(dst_dir, config.MODULE_MAP_FILENAME),
            lambda text: rewrite_bundled_reference_text(text, module, modules),
        )
    else:
        log("WARN", f"missing map source: {module}")

    copy_module_chunked_reference(module, modules, dst_dir)
    copy_module_types(module, src_dir, dst_dir)

    router_path = os.path.join(src_dir, "llms.txt")
    if os.path.isfile(router_path):
        copy_rewritten_text(
            router_path,
            os.path.join(dst_dir, "llms.txt"),
            lambda text: rewrite_module_text(text, module),
        )
    else:
        log("WARN", f"missing module router: {module}")


def copy_root_release_files(modules: list[str]) -> None:
    """Copy rewritten root routing and landing files into release-tree/."""
    for name in ROOT_RELEASE_FILES:
        if name == "index.html":
            continue
        src_path = os.path.join(OUTDIR, name)
        dst_path = os.path.join(RELEASE_TREE_DIR, name)
        if not os.path.isfile(src_path):
            log("WARN", f"missing root release file: {name}")
            continue
        copy_rewritten_text(
            src_path,
            dst_path,
            lambda text: rewrite_root_text(text, modules),
        )


def copy_support_tree() -> None:
    """Copy support-only artifacts into support-tree/."""
    raw_dst = os.path.join(SUPPORT_TREE_DIR, "raw")
    semantic_dst = os.path.join(SUPPORT_TREE_DIR, "semantic-pages")
    manifests_dst = os.path.join(SUPPORT_TREE_DIR, "manifests")
    telemetry_dst = os.path.join(SUPPORT_TREE_DIR, "telemetry")

    if os.path.isdir(L1_RAW_ROOT):
        copy_tree(L1_RAW_ROOT, raw_dst)
    if os.path.isdir(MODULE_L2_ROOT):
        copy_tree(MODULE_L2_ROOT, semantic_dst)

    for name in ["cross-link-registry.json", "repo-manifest.json"]:
        copied = copy_optional_file(
            os.path.join(OUTDIR, name),
            os.path.join(manifests_dst, name),
        )
        if not copied and name == "cross-link-registry.json":
            log("WARN", f"missing support manifest: {name}")

    for name in ["CHANGES.md", "changelog.json", "signature-inventory.json"]:
        copied = copy_optional_file(
            os.path.join(OUTDIR, name),
            os.path.join(telemetry_dst, name),
        )
        if not copied:
            log("WARN", f"missing support telemetry file: {name}")


def main() -> int:
    """Assemble release-tree/ and support-tree/ from the staged old contract."""
    if not config.ENABLE_RELEASE_TREE:
        log("SKIP", "release-tree assembly disabled")
        return 0

    if not os.path.isdir(OUTDIR):
        log("FAIL", f"OUTDIR not found: {OUTDIR}")
        return 1

    modules = collect_modules()
    if not modules:
        log("FAIL", f"no module directories found in {OUTDIR}")
        return 1

    reset_directory(RELEASE_TREE_DIR)
    reset_directory(SUPPORT_TREE_DIR)

    for module in modules:
        copy_module_release_tree(module, modules)

    copy_root_release_files(modules)
    write_release_tree_index(modules)
    overlay_paths = apply_release_include_overlay()
    if overlay_paths:
        log("OK", f"applied release-include overlay: {summarize_paths(overlay_paths)}")
    copy_support_tree()
    log("OK", f"assembled {len(modules)} modules into release-tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())