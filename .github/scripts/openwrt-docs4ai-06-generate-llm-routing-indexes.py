"""
Purpose: Generates the L3 navigational maps (llms.txt and llms-full.txt).
Phase: Aggregation / Indexing
Layers: L4 -> L3
Inputs: OUTDIR/
Outputs: OUTDIR/llms.txt, OUTDIR/llms-full.txt, OUTDIR/{module}/llms.txt
Environment Variables: OUTDIR, OPENWRT_COMMIT, LUCI_COMMIT, WORKDIR
Dependencies: pyyaml, lib.config, lib.repo_manifest
Notes: Root llms.txt remains a decision tree, while llms-full.txt and module
       llms.txt implement the stricter generated-corpus routing contract.
"""

import glob
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config, repo_manifest

sys.stdout.reconfigure(line_buffering=True)

try:
    import yaml
except ImportError:
    print("[06] FAIL: 'pyyaml' package not installed")
    sys.exit(1)

try:
    import tiktoken
except ImportError:
    tiktoken = None

OUTDIR = config.OUTDIR
L2_DIR = os.path.join(OUTDIR, "L2-semantic")
RELEASE_TREE_DIR = config.RELEASE_TREE_DIR
RELEASE_PART_PREFIX = config.MODULE_BUNDLED_REF_FILENAME.removesuffix(".md") + ".part-"
DESCRIPTION_FALLBACK = "Description unavailable."
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

MODULE_CATEGORIES = {
    "procd": "Core Daemons",
    "uci": "Core Daemons",
    "openwrt-hotplug": "Core Daemons",
    "ucode": "Scripting & Logic",
    "luci": "Scripting & Logic",
    "openwrt-core": "Ecosystem",
    "luci-examples": "Ecosystem",
    "wiki": "Manuals",
}
CATEGORY_ORDER = [
    "Core Daemons",
    "Scripting & Logic",
    "Ecosystem",
    "Manuals",
]

ENCODER = None
if tiktoken is not None:
    try:
        ENCODER = tiktoken.get_encoding("cl100k_base")
    except Exception:
        ENCODER = None


def build_version_string(env=None):
    env_snapshot = env if env is not None else {
        key: os.environ.get(key) for key in repo_manifest.COMMIT_ENV_TO_MANIFEST_KEY
    }
    missing = [key for key, value in env_snapshot.items() if not value]
    commits, manifest_path = repo_manifest.resolve_commit_environment(
        env=env_snapshot,
        extra_manifest_paths=[
            config.REPO_MANIFEST_PATH,
            os.path.join(OUTDIR, "repo-manifest.json"),
        ],
    )

    versions = [
        f"openwrt/openwrt@{commits['OPENWRT_COMMIT']}",
        f"openwrt/luci@{commits['LUCI_COMMIT']}",
        f"jow-/ucode@{commits['UCODE_COMMIT']}",
    ]
    return ", ".join(versions), missing, manifest_path


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def strip_markdown_noise(text):
    cleaned = text or ""
    cleaned = re.sub(r"```.*?```", " ", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"^\s{0,3}#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*[-*+]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\d+\.\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = cleaned.replace("|", " ")
    return normalize_whitespace(cleaned)


def first_sentence(text):
    cleaned = strip_markdown_noise(text)
    if not cleaned:
        return ""

    sentence = SENTENCE_SPLIT_RE.split(cleaned, maxsplit=1)[0].strip()
    if not sentence:
        return ""
    if len(sentence) > 240:
        sentence = sentence[:237].rstrip() + "..."
    return sentence


def choose_short_description(frontmatter, body, fallback=DESCRIPTION_FALLBACK):
    for candidate in [
        frontmatter.get("ai_summary"),
        frontmatter.get("description"),
        body,
    ]:
        sentence = first_sentence(candidate)
        if sentence and sentence.casefold() != "no description":
            return sentence
    return fallback


def estimate_tokens(text):
    if ENCODER is not None:
        return len(ENCODER.encode(text))
    return max(1, round(len(text) / 4))


def load_markdown_file(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def extract_frontmatter_and_body(content, path):
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)", content, re.DOTALL)
    if not match:
        raise ValueError(f"Invalid L2 schema in {path}")
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def build_catalog_entry(label, rel_path, description, tokens, kind):
    return {
        "label": label,
        "rel_path": rel_path,
        "description": description,
        "tokens": int(tokens),
        "kind": kind,
    }


def build_generated_entry(rel_path, description, kind):
    full_path = os.path.join(OUTDIR, rel_path.replace("/", os.sep))
    content = load_markdown_file(full_path)
    return build_catalog_entry(
        label=os.path.basename(rel_path),
        rel_path=rel_path,
        description=description,
        tokens=estimate_tokens(content),
        kind=kind,
    )


def format_entry_line(label, link, description, tokens, kind=None):
    token_text = f"~{int(tokens)} tokens"
    if kind:
        token_text += f", {kind}"
    return f"- [{label}]({link}): {description} ({token_text})"


def render_section(title, entries):
    if not entries:
        return []

    lines = [f"## {title}", ""]
    for entry in entries:
        lines.append(
            format_entry_line(
                entry["label"],
                entry["link"],
                entry["description"],
                entry["tokens"],
                entry.get("kind"),
            )
        )
    lines.append("")
    return lines


def module_sort_key(module_name):
    return (MODULE_CATEGORIES.get(module_name, "Other Components"), module_name)


def apply_replacements(content, replacements):
    updated = content
    for old, new in replacements:
        updated = updated.replace(old, new)
    return updated


def rewrite_release_module_llms(content, module):
    return apply_replacements(
        content,
        [
            (f"{module}-skeleton.md", config.MODULE_MAP_FILENAME),
            (
                f"{module}-complete-reference.md",
                config.MODULE_BUNDLED_REF_FILENAME,
            ),
            (
                f"{module}-complete-reference.part-",
                RELEASE_PART_PREFIX,
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
                f"./{RELEASE_PART_PREFIX}",
            ),
            (
                f"../L2-semantic/{module}/",
                f"./{config.MODULE_CHUNKED_REF_DIRNAME}/",
            ),
            (
                f"./{module}.d.ts",
                f"./{config.MODULE_TYPES_DIRNAME}/{module}.d.ts",
            ),
        ],
    )


def rewrite_release_llms_full(content, modules):
    replacements = []
    for module in modules:
        replacements.extend(
            [
                (
                    f"./{module}/{module}-skeleton.md",
                    f"./{module}/{config.MODULE_MAP_FILENAME}",
                ),
                (
                    f"./{module}/{module}-complete-reference.md",
                    f"./{module}/{config.MODULE_BUNDLED_REF_FILENAME}",
                ),
                (
                    f"./{module}/{module}-complete-reference.part-",
                    f"./{module}/{RELEASE_PART_PREFIX}",
                ),
                (
                    f"./L2-semantic/{module}/",
                    f"./{module}/{config.MODULE_CHUNKED_REF_DIRNAME}/",
                ),
                (
                    f"./{module}/{module}.d.ts",
                    f"./{module}/{config.MODULE_TYPES_DIRNAME}/{module}.d.ts",
                ),
            ]
        )
    return apply_replacements(content, replacements)


def write_release_tree_routes(modules):
    os.makedirs(RELEASE_TREE_DIR, exist_ok=True)

    shutil.copy2(
        os.path.join(OUTDIR, "llms.txt"),
        os.path.join(RELEASE_TREE_DIR, "llms.txt"),
    )

    with open(os.path.join(OUTDIR, "llms-full.txt"), "r", encoding="utf-8") as handle:
        llms_full_content = handle.read()
    with open(
        os.path.join(RELEASE_TREE_DIR, "llms-full.txt"),
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        handle.write(rewrite_release_llms_full(llms_full_content, modules))

    for module in modules:
        src_path = os.path.join(OUTDIR, module, "llms.txt")
        if not os.path.isfile(src_path):
            continue
        dst_dir = os.path.join(RELEASE_TREE_DIR, module)
        os.makedirs(dst_dir, exist_ok=True)
        with open(src_path, "r", encoding="utf-8") as handle:
            module_content = handle.read()
        with open(
            os.path.join(dst_dir, "llms.txt"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(rewrite_release_module_llms(module_content, module))


def main():
    if not os.path.isdir(L2_DIR):
        print(f"[06] FAIL: L2 directory not found: {L2_DIR}")
        return 1

    version_str, missing, manifest_path = build_version_string()
    if missing and manifest_path:
        print(f"[06] INFO: Loaded missing commit versions from {manifest_path}")

    print("[06] Generating L3 Navigational Maps (llms.txt)")

    global_tokens = 0
    full_catalog = []
    module_registry = {}

    for module in sorted(os.listdir(L2_DIR), key=module_sort_key):
        mod_dir = os.path.join(L2_DIR, module)
        if not os.path.isdir(mod_dir):
            continue

        l2_entries = []
        module_tokens = 0

        for fpath in sorted(glob.glob(os.path.join(mod_dir, "*.md"))):
            try:
                content = load_markdown_file(fpath)
                frontmatter, body = extract_frontmatter_and_body(content, fpath)
            except Exception as exc:
                print(f"[06] WARN: Skipping {fpath}: {exc}")
                continue

            tokens = int(frontmatter.get("token_count", 0) or 0)
            description = choose_short_description(frontmatter, body)
            rel_path = f"L2-semantic/{module}/{os.path.basename(fpath)}"

            module_tokens += tokens
            global_tokens += tokens

            l2_entries.append(
                build_catalog_entry(
                    label=os.path.basename(fpath),
                    rel_path=rel_path,
                    description=description,
                    tokens=tokens,
                    kind="l2-source",
                )
            )

        if not l2_entries:
            continue

        out_mod_dir = os.path.join(OUTDIR, module)
        os.makedirs(out_mod_dir, exist_ok=True)

        recommended_entries = []
        tooling_entries = []

        skeleton_name = f"{module}-skeleton.md"
        skeleton_path = os.path.join(out_mod_dir, skeleton_name)
        if os.path.isfile(skeleton_path):
            recommended_entries.append(
                build_generated_entry(
                    f"{module}/{skeleton_name}",
                    f"Structural map for {module} that prioritizes quick orientation and symbol discovery.",
                    "l3-skeleton",
                )
            )

        monolith_name = f"{module}-complete-reference.md"
        monolith_path = os.path.join(out_mod_dir, monolith_name)
        monolith_part_paths = sorted(
            glob.glob(
                os.path.join(out_mod_dir, f"{module}-complete-reference.part-*.md")
            )
        )
        if os.path.isfile(monolith_path):
            monolith_description = (
                f"Sharded complete reference index for {module} with links to smaller part files."
                if monolith_part_paths
                else f"Complete monolithic reference for {module} when a larger context window is available."
            )
            recommended_entries.append(
                build_generated_entry(
                    f"{module}/{monolith_name}",
                    monolith_description,
                    "l4-monolith",
                )
            )

        for index, part_path in enumerate(monolith_part_paths, start=1):
            part_name = os.path.basename(part_path)
            recommended_entries.append(
                build_generated_entry(
                    f"{module}/{part_name}",
                    f"Part {index} of the sharded complete reference for {module} when the full module exceeds the token budget.",
                    "l4-monolith-part",
                )
            )

        for dts_path in sorted(glob.glob(os.path.join(out_mod_dir, "*.d.ts"))):
            dts_name = os.path.basename(dts_path)
            tooling_entries.append(
                build_generated_entry(
                    f"{module}/{dts_name}",
                    f"TypeScript declarations for IDE navigation and static analysis of {module}.",
                    "l3-ide-schema",
                )
            )

        source_section_entries = []
        for entry in l2_entries:
            source_section_entries.append(
                {
                    "label": entry["label"],
                    "link": f"../{entry['rel_path']}",
                    "description": entry["description"],
                    "tokens": entry["tokens"],
                    "kind": entry["kind"],
                }
            )
            full_catalog.append(entry)

        module_description = next(
            (entry["description"] for entry in l2_entries if entry["description"] != DESCRIPTION_FALLBACK),
            DESCRIPTION_FALLBACK,
        )

        module_lines = [
            f"# {module} module",
            f"> {module_description}",
            f"> **Total Context:** ~{module_tokens} tokens",
            "",
        ]

        module_lines.extend(
            render_section(
                "Recommended Entry Points",
                [
                    {
                        "label": entry["label"],
                        "link": f"./{os.path.basename(entry['rel_path'])}",
                        "description": entry["description"],
                        "tokens": entry["tokens"],
                        "kind": entry["kind"],
                    }
                    for entry in recommended_entries
                ],
            )
        )
        module_lines.extend(
            render_section(
                "Tooling Surfaces",
                [
                    {
                        "label": entry["label"],
                        "link": f"./{os.path.basename(entry['rel_path'])}",
                        "description": entry["description"],
                        "tokens": entry["tokens"],
                        "kind": entry["kind"],
                    }
                    for entry in tooling_entries
                ],
            )
        )
        module_lines.extend(render_section("Source Documents", source_section_entries))

        module_content = "\n".join(module_lines).rstrip() + "\n"
        module_index_path = os.path.join(out_mod_dir, "llms.txt")
        with open(module_index_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(module_content)

        module_index_entry = build_catalog_entry(
            label="llms.txt",
            rel_path=f"{module}/llms.txt",
            description=f"Module-specific routing guide for {module} with preferred entry points, tooling, and source documents.",
            tokens=estimate_tokens(module_content),
            kind="l3-module-index",
        )

        full_catalog.append(module_index_entry)
        full_catalog.extend(recommended_entries)
        full_catalog.extend(tooling_entries)

        module_registry[module] = {
            "tokens": module_tokens,
            "description": module_description,
            "path": f"./{module}/llms.txt",
        }

    if os.path.isfile(os.path.join(OUTDIR, "AGENTS.md")):
        full_catalog.append(
            build_generated_entry(
                "AGENTS.md",
                "AI agent usage rules for navigating the generated OpenWrt documentation corpus.",
                "l3-agent-guide",
            )
        )

    if os.path.isfile(os.path.join(OUTDIR, "README.md")):
        full_catalog.append(
            build_generated_entry(
                "README.md",
                "Generated corpus overview and quick-start guidance for published outputs.",
                "l3-generated-readme",
            )
        )

    print(f"[06] Indexed {len(full_catalog)} catalog entries across {len(module_registry)} modules totaling ~{global_tokens} underlying L2 tokens.")

    with open(os.path.join(OUTDIR, "llms.txt"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("# openwrt-docs4ai - LLM Routing Index\n")
        handle.write("> For a flat file listing, see [llms-full.txt](./llms-full.txt)\n\n")
        handle.write(f"> **Version:** {version_str}\n")
        handle.write(f"> **Total Context Available:** ~{global_tokens} tokens\n\n")

        for category in CATEGORY_ORDER:
            modules_in_category = [
                module
                for module in sorted(module_registry)
                if MODULE_CATEGORIES.get(module) == category
            ]
            if not modules_in_category:
                continue

            handle.write(f"## {category}\n")
            for module in modules_in_category:
                registry = module_registry[module]
                handle.write(
                    format_entry_line(
                        module,
                        registry["path"],
                        registry["description"],
                        registry["tokens"],
                    )
                    + "\n"
                )
            handle.write("\n")

        uncategorized_modules = [
            module for module in sorted(module_registry) if module not in MODULE_CATEGORIES
        ]
        if uncategorized_modules:
            handle.write("## Other Components\n")
            for module in uncategorized_modules:
                registry = module_registry[module]
                handle.write(
                    format_entry_line(
                        module,
                        registry["path"],
                        registry["description"],
                        registry["tokens"],
                    )
                    + "\n"
                )
            handle.write("\n")

        handle.write("## Complete Aggregation\n")
        handle.write("If your context window permits, you may fetch the flat URL index:\n")
        handle.write("- [llms-full.txt](./llms-full.txt): Exhaustive flat catalog of generated AI-facing documents. (~0 tokens)\n")

    with open(os.path.join(OUTDIR, "llms-full.txt"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("# openwrt-docs4ai - Complete Flat Catalog\n")
        handle.write("> Includes generated AI-facing helper surfaces and all published L2 source documents.\n")
        handle.write(f"> **Total Underlying L2 Context:** ~{global_tokens} tokens\n\n")

        seen_paths = set()
        for entry in sorted(full_catalog, key=lambda item: item["rel_path"]):
            if entry["rel_path"] in seen_paths:
                continue
            seen_paths.add(entry["rel_path"])
            handle.write(
                format_entry_line(
                    entry["label"],
                    f"./{entry['rel_path']}",
                    entry["description"],
                    entry["tokens"],
                    entry["kind"],
                )
                + "\n"
            )

    write_release_tree_routes(sorted(module_registry))

    print("[06] Complete: Generated llms.txt, llms-full.txt, and module-level indexes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())