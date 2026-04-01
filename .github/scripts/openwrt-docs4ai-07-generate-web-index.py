"""Generate a filesystem-derived web index for the published tree.

Purpose: Generates the web landing page (index.html).
Phase: Presentation
Layers: L3
Inputs: OUTDIR/
Outputs: OUTDIR/index.html
Environment Variables: OUTDIR
Dependencies: lib.config
Notes: Builds a human-readable browse page directly from the staged filesystem.
"""

from __future__ import annotations

import datetime
import html
import os
import shutil
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

OUTDIR = Path(config.OUTDIR)
OUTPUT_PATH = OUTDIR / "index.html"
RELEASE_TREE_DIR = Path(config.RELEASE_TREE_DIR)
SUPPORT_TREE_DIR = Path(config.SUPPORT_TREE_DIR)
RELEASE_INCLUDE_DIR = Path(config.RELEASE_INCLUDE_DIR)
TS = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
PUBLISH_PREFIX = "."  # Display-path prefix for the staged root index.html
ROOT_SECTION = "__root__"
RELEASE_TREE_ROOT_SECTION = "__root__"
RELEASE_TREE_ROOT_FILES = [
    "index.html",
    "README.md",
    "llms.txt",
    "llms-full.txt",
    "AGENTS.md",
]
TOP_LEVEL_ORDER = [
    ROOT_SECTION,
    "luci",
    "luci-examples",
    "openwrt-core",
    "openwrt-hotplug",
    "procd",
    "uci",
    "ucode",
    "wiki",
]
SECTION_DESCRIPTIONS = {
    ROOT_SECTION: (
        "Top-level catalogs, routing files, telemetry, and release metadata for the published OpenWrt corpus."
    ),
    "luci": (
        "LuCI JavaScript references, skeletons, and complete-reference guides for the main web interface codebase."
    ),
    "luci-examples": (
        "LuCI example applications and companion references that show "
        "concrete UI, RPC, and Docker integration patterns."
    ),
    "openwrt-core": (
        "Core OpenWrt reference material covering build, package, and platform-facing implementation surfaces."
    ),
    "openwrt-hotplug": (
        "Hotplug event documentation and publishable references for OpenWrt event-driven shell workflows."
    ),
    "procd": (
        "procd service-management references, API maps, and generated context files for process supervision surfaces."
    ),
    "uci": (
        "UCI schema references, navigational indexes, and generated "
        "material for configuration-driven OpenWrt subsystems."
    ),
    "ucode": (
        "ucode API references, type surfaces, and generated navigation files for scripting and rpcd integration work."
    ),
    "wiki": ("OpenWrt wiki-derived references and navigational outputs preserved in the published product tree."),
}


def section_sort_key(name: str) -> tuple[int, str]:
    """Sort known sections first and append unknown folders alphabetically."""
    try:
        return TOP_LEVEL_ORDER.index(name), name
    except ValueError:
        return len(TOP_LEVEL_ORDER), name


def iter_section_files(root: Path, section: str) -> list[str]:
    """Return publishable file paths for one top-level section."""
    if section == ROOT_SECTION:
        root_files = {path.name for path in root.iterdir() if path.is_file()}
        root_files.add(OUTPUT_PATH.name)
        return sorted(root_files, key=root_file_sort_key)

    section_dir = root / section
    if not section_dir.is_dir():
        return []

    return sorted(
        (path.relative_to(root).as_posix() for path in section_dir.rglob("*") if path.is_file()),
        key=section_file_sort_key,
    )


def root_file_sort_key(name: str) -> tuple[int, str]:
    """Keep root landing files in a human-first order."""
    preferred = [
        "index.html",
        "README.md",
        "llms.txt",
        "llms-full.txt",
        "AGENTS.md",
        "CHANGES.md",
        "changelog.json",
        "cross-link-registry.json",
        "repo-manifest.json",
        "signature-inventory.json",
    ]
    try:
        return preferred.index(name), name
    except ValueError:
        return len(preferred), name


def section_file_sort_key(rel_path: str) -> tuple[tuple[int, str], str]:
    """Sort files by immediate area and then by human-first file role."""
    parts = rel_path.split("/")
    filename = parts[-1]
    module_name = parts[0]

    try:
        module_rank = TOP_LEVEL_ORDER.index(module_name)
    except ValueError:
        module_rank = len(TOP_LEVEL_ORDER)

    preferred = [
        "llms.txt",
        f"{module_name}-skeleton.md",
        f"{module_name}-complete-reference.md",
        "README.md",
    ]
    if filename.endswith(".d.ts"):
        return ((module_rank, module_name), f"{len(preferred)}:{filename}"), rel_path
    try:
        return ((module_rank, module_name), f"{preferred.index(filename)}:{filename}"), rel_path
    except ValueError:
        return ((module_rank, module_name), f"{len(preferred) + 1}:{filename}"), rel_path


def collect_sections(root: Path) -> list[tuple[str, list[str]]]:
    """Collect top-level publish sections and their recursive file lists."""
    sections: list[tuple[str, list[str]]] = []

    root_files = iter_section_files(root, ROOT_SECTION)
    if root_files:
        sections.append((ROOT_SECTION, root_files))

    top_level_dirs = sorted(
        (path.name for path in root.iterdir() if path.is_dir()),
        key=section_sort_key,
    )
    if root == OUTDIR:
        excluded_dirs = {
            os.path.basename(config.RELEASE_TREE_DIR),
            os.path.basename(config.SUPPORT_TREE_DIR),
        }
        top_level_dirs = [name for name in top_level_dirs if name not in excluded_dirs]
    for section in top_level_dirs:
        files = iter_section_files(root, section)
        if files:
            sections.append((section, files))

    return sections


def describe_section(section: str, file_count: int) -> str:
    """Return a stable human-readable description for a publish section."""
    base = SECTION_DESCRIPTIONS.get(
        section,
        f"Published files grouped under the {section} top-level product area.",
    )
    noun = "file" if file_count == 1 else "files"
    return f"{base} This section currently lists {file_count} published {noun}."


def section_heading(section: str) -> str:
    """Return the visible heading label for a section."""
    return "Root Files" if section == ROOT_SECTION else section


def section_slug(section: str) -> str:
    """Return an anchor-safe slug for a section heading."""
    return "root-files" if section == ROOT_SECTION else section


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
    if filename.startswith(config.MODULE_BUNDLED_REF_FILENAME.removesuffix(".md") + ".part-"):
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
        (path.relative_to(root).as_posix() for path in section_dir.rglob("*") if path.is_file()),
        key=release_section_file_sort_key,
    )


def collect_release_sections(root: Path) -> list[tuple[str, list[str]]]:
    """Collect the direct-root release-tree sections and their file lists."""
    sections: list[tuple[str, list[str]]] = []

    root_files = iter_release_section_files(root, RELEASE_TREE_ROOT_SECTION)
    if root_files:
        sections.append((RELEASE_TREE_ROOT_SECTION, root_files))

    top_level_dirs = sorted(
        (path.name for path in root.iterdir() if path.is_dir()),
        key=section_sort_key,
    )
    for section in top_level_dirs:
        files = iter_release_section_files(root, section)
        if files:
            sections.append((section, files))

    return sections


def describe_release_section(section: str, file_count: int) -> str:
    """Return a stable human-readable description for one release-tree section."""
    if section == RELEASE_TREE_ROOT_SECTION:
        base = "Top-level routing files, catalogs, and landing pages for the published release tree."
    else:
        base = (
            f"Release-ready routing files, bundled references, "
            f"chunked-reference pages, and generated type surfaces for {section}."
        )
    noun = "file" if file_count == 1 else "files"
    return f"{base} This section currently lists {file_count} published {noun}."


def release_section_heading(section: str) -> str:
    return "Root Files" if section == RELEASE_TREE_ROOT_SECTION else section


def release_section_slug(section: str) -> str:
    return "root-files" if section == RELEASE_TREE_ROOT_SECTION else section


def render_release_section_nav(sections: list[tuple[str, list[str]]]) -> str:
    items = []
    for section, files in sections:
        items.append(
            '<li><a href="#{slug}">{label}</a> <span>({count})</span></li>'.format(
                slug=html.escape(release_section_slug(section)),
                label=html.escape(release_section_heading(section)),
                count=len(files),
            )
        )
    return "".join(items)


def render_release_section(section: str, files: Iterable[str]) -> str:
    file_list = list(files)
    items = []
    for rel_path in file_list:
        items.append(
            '<li><a href="{href}">{label}</a></li>'.format(
                href=quote(rel_path),
                label=html.escape(f"./{rel_path}"),
            )
        )

    return "".join(
        [
            f'<section id="{html.escape(release_section_slug(section))}">',
            f"<h2>{html.escape(release_section_heading(section))}</h2>",
            f"<p>{html.escape(describe_release_section(section, len(file_list)))}</p>",
            '<ul class="path-list">',
            "".join(items),
            "</ul>",
            "</section>",
        ]
    )


def build_release_tree_html(root: Path) -> str:
    """Build the direct-root release-tree landing page."""
    sections = collect_release_sections(root)
    publish_file_count = sum(len(files) for _section, files in sections)
    rendered_sections = "".join(render_release_section(section, files) for section, files in sections)
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
            Generated: {TS}<br>
            Pipeline version: v12
        </div>
    </main>
</body>
</html>
"""


def reset_directory(path: Path) -> None:
    """Recreate one generated support directory from scratch."""
    if path.is_dir():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tree(src: Path, dst: Path) -> None:
    """Copy one directory tree while preserving metadata."""
    shutil.copytree(src, dst, copy_function=shutil.copy2, dirs_exist_ok=True)


def copy_optional_file(src: Path, dst: Path) -> bool:
    """Copy one optional file and report whether it existed."""
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def summarize_paths(paths: list[str], limit: int = 5) -> str:
    """Return a short preview for logged overlay paths."""
    preview = paths[:limit]
    if len(paths) > limit:
        preview.append(f"... (+{len(paths) - limit} more)")
    return ", ".join(preview)


def apply_release_include_overlay(
    release_tree_dir: Path | str = RELEASE_TREE_DIR,
    include_dir: Path | str = RELEASE_INCLUDE_DIR,
) -> list[str]:
    """Copy the common release include overlay on top of release-tree/."""
    release_root = Path(release_tree_dir)
    include_root = Path(include_dir)
    if not include_root.is_dir():
        return []

    copied_paths: list[str] = []
    for src_path in sorted(path for path in include_root.rglob("*") if path.is_file()):
        rel_path = src_path.relative_to(include_root).as_posix()
        dst_path = release_root / rel_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        copied_paths.append(rel_path)
    return copied_paths


def finalize_release_tree(
    release_tree_dir: Path | str = RELEASE_TREE_DIR,
    include_dir: Path | str = RELEASE_INCLUDE_DIR,
) -> list[str]:
    """Apply overlays, regenerate the release index, and preserve any custom index override."""
    release_root = Path(release_tree_dir)
    include_root = Path(include_dir)

    overlay_paths = apply_release_include_overlay(release_root, include_root)
    release_html = build_release_tree_html(release_root)
    index_path = release_root / "index.html"
    index_path.write_text(release_html, encoding="utf-8", newline="\n")

    # Allow an explicit overlay-provided index to replace the generated listing.
    copy_optional_file(include_root / "index.html", index_path)
    return overlay_paths


def copy_support_tree(
    outdir: Path = OUTDIR,
    support_tree_dir: Path = SUPPORT_TREE_DIR,
) -> None:
    """Materialize support-tree from the staged internal outputs."""
    reset_directory(support_tree_dir)

    manifests_source_dir = Path(config.PROCESSED_DIR) / "manifests"
    manifests_dir = support_tree_dir / "manifests"
    telemetry_dir = support_tree_dir / "telemetry"

    copy_optional_file(manifests_source_dir / "cross-link-registry.json", manifests_dir / "cross-link-registry.json")
    copy_optional_file(manifests_source_dir / "repo-manifest.json", manifests_dir / "repo-manifest.json")
    copy_optional_file(outdir / "CHANGES.md", telemetry_dir / "CHANGES.md")
    copy_optional_file(outdir / "changelog.json", telemetry_dir / "changelog.json")
    copy_optional_file(outdir / "signature-inventory.json", telemetry_dir / "signature-inventory.json")


def render_section_nav(sections: list[tuple[str, list[str]]]) -> str:
    """Render a simple jump list for the long single-page index."""
    items = []
    for section, files in sections:
        items.append(
            '<li><a href="#{slug}">{label}</a> <span>({count})</span></li>'.format(
                slug=html.escape(section_slug(section)),
                label=html.escape(section_heading(section)),
                count=len(files),
            )
        )
    return "".join(items)


def render_section(section: str, files: Iterable[str]) -> str:
    """Render one top-level section as HTML."""
    file_list = list(files)
    items = []
    for rel_path in file_list:
        display_path = f"{PUBLISH_PREFIX}/{rel_path}"
        href = quote(rel_path)
        items.append(
            '<li><a href="{href}">{label}</a></li>'.format(
                href=href,
                label=html.escape(display_path),
            )
        )

    return "".join(
        [
            f'<section id="{html.escape(section_slug(section))}">',
            f"<h2>{html.escape(section_heading(section))}</h2>",
            f"<p>{html.escape(describe_section(section, len(file_list)))}</p>",
            '<ul class="path-list">',
            "".join(items),
            "</ul>",
            "</section>",
        ]
    )


def build_html(root: Path) -> str:
    """Build the final index.html document from the staged filesystem."""
    sections = collect_sections(root)
    publish_file_count = sum(len(files) for _section, files in sections)
    rendered_sections = "".join(render_section(section, files) for section, files in sections)
    section_nav = render_section_nav(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>openwrt-docs4ai staged tree</title>
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
      font-family: Georgia, "Times New Roman", serif;
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
      font-family: "Cascadia Code", Consolas, "Courier New", monospace;
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
        <h1>openwrt-docs4ai staged tree</h1>
    <p>
            This page is a filesystem-derived browse index for the staged
            openwrt-docs4ai output tree. The link text mirrors the packaged layout
      under {html.escape(PUBLISH_PREFIX)} and each section maps to one
            top-level area of the internal staging folder.
    </p>
        <p>
                        The current staged snapshot contains {publish_file_count} files across
                        {len(sections)} top-level sections, including release-ready routing
                        surfaces, telemetry files, and internal staging artifacts.
        </p>
        <nav class="section-nav" aria-label="Section navigation">
            <h2>Jump to section</h2>
            <ul>
                {section_nav}
            </ul>
        </nav>
    {rendered_sections}
    <div class="meta">
      Generated: {TS}<br>
      Pipeline version: v12
    </div>
  </main>
</body>
</html>
"""


def main() -> int:
    """Generate index.html from the current staged output tree."""
    print("[07] Generating filesystem-derived index.html web landing page")

    if not OUTDIR.is_dir():
        print(f"[07] FAIL: OUTDIR not found at {OUTDIR}")
        return 1

    html_content = build_html(OUTDIR)
    OUTPUT_PATH.write_text(html_content, encoding="utf-8", newline="\n")

    if not RELEASE_TREE_DIR.is_dir():
        print(f"[07] FAIL: release-tree not found at {RELEASE_TREE_DIR}")
        return 1

    overlay_paths = finalize_release_tree()
    copy_support_tree()

    if overlay_paths:
        print(f"[07] OK: applied release-include overlay: {summarize_paths(overlay_paths)}")

    print("[07] OK: generated index.html and finalized release/support trees.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
