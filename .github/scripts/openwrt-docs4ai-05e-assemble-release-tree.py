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

import glob
import os
import shutil
import sys

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


def module_legacy_paths(module: str) -> list[tuple[str, str]]:
    """Return module-local path rewrites for copied text content."""
    return [
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
    copy_support_tree()
    log("OK", f"assembled {len(modules)} modules into release-tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())