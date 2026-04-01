import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, ".github", "scripts")
SCRIPT_NAME_RE = re.compile(r"^openwrt-docs4ai-(?P<stage_id>\d{2}[a-z]?)-.+\.py$")
STAGE_FAMILY_RE = re.compile(r"^\d{2}$")

POST_EXTRACT_PIPELINE = [
    "openwrt-docs4ai-03-normalize-semantic.py",
    "openwrt-docs4ai-04-generate-ai-summaries.py",
    "openwrt-docs4ai-05a-assemble-references.py",
    "openwrt-docs4ai-05b-generate-agents-and-readme.py",
    "openwrt-docs4ai-05c-generate-ucode-ide-schemas.py",
    "openwrt-docs4ai-05d-generate-api-drift-changelog.py",
    "openwrt-docs4ai-05e-generate-luci-dts.py",
    "openwrt-docs4ai-06-generate-llm-routing-indexes.py",
    "openwrt-docs4ai-07-generate-web-index.py",
    "openwrt-docs4ai-08-validate-output.py",
    "openwrt-docs4ai-09-build-packages.py",
]

FULL_PIPELINE = [
    "openwrt-docs4ai-01-clone-repos.py",
    "openwrt-docs4ai-02a-scrape-wiki.py",
    "openwrt-docs4ai-02b-scrape-ucode.py",
    "openwrt-docs4ai-02c-scrape-jsdoc.py",
    "openwrt-docs4ai-02d-scrape-core-packages.py",
    "openwrt-docs4ai-02e-scrape-example-packages.py",
    "openwrt-docs4ai-02f-scrape-procd-api.py",
    "openwrt-docs4ai-02g-scrape-uci-schemas.py",
    "openwrt-docs4ai-02h-scrape-hotplug-events.py",
    "openwrt-docs4ai-02i-ingest-cookbook.py",
    *POST_EXTRACT_PIPELINE,
]


def get_stage_id(script_name):
    match = SCRIPT_NAME_RE.match(script_name)
    if not match:
        raise ValueError(f"Unsupported pipeline script name: {script_name}")
    return match.group("stage_id")


def select_pipeline_scripts(pipeline, only=None):
    scripts = list(pipeline)
    if only is None:
        return scripts

    selector = only.strip().lower()
    if not selector:
        raise ValueError("Stage selector cannot be empty.")

    exact_stage_matches = [script for script in scripts if get_stage_id(script).lower() == selector]
    if exact_stage_matches:
        return exact_stage_matches

    if STAGE_FAMILY_RE.fullmatch(selector):
        family_matches = [script for script in scripts if get_stage_id(script).lower().startswith(selector)]
        if family_matches:
            return family_matches

    full_name_matches = [script for script in scripts if script.lower() == selector]
    if full_name_matches:
        return full_name_matches

    available = ", ".join(get_stage_id(script) for script in scripts)
    raise ValueError(f"No scripts match selector '{only}'. Available stage ids in this run: {available}")


FIXTURE_DOCS = [
    {
        "module": "uci",
        "origin_type": "c_source",
        "slug": "api-config",
        "content": "# UCI API\n\n## uci.get(package, section, option)\nReturns a config value.\n\n## uci.set(package, section, option, value)\nSets a config value.\n",
        "metadata": {
            "extractor": "fixture",
            "language": "c",
            "description": "Configuration access APIs",
            "upstream_path": "package/system/uci.c",
            "source_commit": "abc1234",
        },
    },
    {
        "module": "procd",
        "origin_type": "c_source",
        "slug": "init-service",
        "content": "# Procd Init\n\n## procd.add_service(name)\nAdds a service and later consults uci.get() for configuration.\n",
        "metadata": {
            "extractor": "fixture",
            "language": "c",
            "description": "Init and service lifecycle helpers",
            "upstream_path": "procd/init.c",
            "source_commit": "abc1234",
        },
    },
    {
        "module": "ucode",
        "origin_type": "c_source",
        "slug": "api-fs",
        "content": "# ucode fs module\n\n## fs.open(path, [mode])\nOpens a file.\n\n## fs.close(fd)\nCloses a file descriptor.\n\n## fs.oldThing()\n**Deprecated** Use fs.open() instead.\n",
        "metadata": {
            "extractor": "fixture",
            "language": "c",
            "description": "File system module for ucode",
            "upstream_path": "lib/fs.c",
            "source_commit": "abc1234",
        },
    },
    {
        "module": "ucode",
        "origin_type": "c_source",
        "slug": "api-uloop",
        "content": "# ucode uloop module\n\n## uloop.timer(timeout)\nCreates an event-loop timer.\n\nSee also fs.open().\n",
        "metadata": {
            "extractor": "fixture",
            "language": "c",
            "description": "Event loop timers and callbacks",
            "upstream_path": "lib/uloop.c",
            "source_commit": "abc1234",
        },
    },
    {
        "module": "wiki",
        "origin_type": "wiki_page",
        "slug": "service-events",
        "content": "# Service Events\n\nLegacy scripts still mention fs.oldThing() in examples. Modern scripts should call uloop.timer(timeout) instead.\n",
        "metadata": {
            "extractor": "fixture",
            "description": "Operational notes for service events",
            "original_url": "https://openwrt.org/docs/example/service-events",
        },
    },
]


def get_local_log_path(filename):
    log_dir = os.path.join(PROJECT_ROOT, "tmp", "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, filename)


def build_env(downloads_dir, staged_dir, run_ai=False, extra_env=None, processed_dir=None, pipeline_run_dir=None):
    env = os.environ.copy()
    if processed_dir is None:
        processed_dir = os.path.join(os.path.dirname(staged_dir), "processed")
    if pipeline_run_dir is None:
        pipeline_run_dir = os.path.dirname(downloads_dir)

    env["PIPELINE_RUN_DIR"] = pipeline_run_dir
    env["DOWNLOADS_DIR"] = downloads_dir
    env["WORKDIR"] = downloads_dir
    env["PROCESSED_DIR"] = processed_dir
    env["STAGED_DIR"] = staged_dir
    env["OUTDIR"] = staged_dir
    env["SKIP_AI"] = "false" if run_ai else "true"
    env["AI_DATA_BASE_DIR"] = os.path.join(pipeline_run_dir, "ai-data", "base")
    env["AI_DATA_OVERRIDE_DIR"] = os.path.join(pipeline_run_dir, "ai-data", "override")
    env["VALIDATE_MODE"] = env.get("VALIDATE_MODE", "hard")

    os.makedirs(downloads_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(staged_dir, exist_ok=True)
    os.makedirs(env["AI_DATA_BASE_DIR"], exist_ok=True)
    os.makedirs(env["AI_DATA_OVERRIDE_DIR"], exist_ok=True)

    if extra_env:
        env.update(extra_env)
    return env


def append_log(log_file, title, body):
    if not log_file:
        return
    with open(log_file, "a", encoding="utf-8") as handle:
        handle.write(f"\n--- {title} ---\n")
        handle.write(body)
        if not body.endswith("\n"):
            handle.write("\n")


def run_named_script(script_name, env, cwd, log_file=None, extra_args=None, timeout=300):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.isfile(script_path):
        raise FileNotFoundError(script_path)

    command = [sys.executable, script_path]
    if extra_args:
        command.extend(extra_args)

    result = subprocess.run(
        command,
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    body = f"COMMAND: {' '.join(command)}\n\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}\n"
    append_log(log_file, script_name, body)
    return result


def seed_l1_fixtures(downloads_dir, processed_dir):
    l1_root = os.path.join(processed_dir, "L1-raw")
    os.makedirs(l1_root, exist_ok=True)

    for doc in FIXTURE_DOCS:
        module_dir = os.path.join(l1_root, doc["module"])
        os.makedirs(module_dir, exist_ok=True)

        base_name = f"{doc['origin_type']}-{doc['slug']}"
        md_path = os.path.join(module_dir, f"{base_name}.md")
        meta_path = os.path.join(module_dir, f"{base_name}.meta.json")

        with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(doc["content"])

        metadata = dict(doc["metadata"])
        metadata.update(
            {
                "module": doc["module"],
                "origin_type": doc["origin_type"],
                "slug": doc["slug"],
                "content_hash": hashlib.sha256(doc["content"].encode("utf-8")).hexdigest()[:8],
            }
        )
        with open(meta_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(metadata, handle, indent=2)

    manifest = {
        "openwrt": "1111111",
        "luci": "2222222",
        "ucode": "3333333",
        "timestamp": "2026-03-09T00:00:00Z",
    }
    with open(os.path.join(downloads_dir, "repo-manifest.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2)


def seed_ai_cache(cache_path):
    ucode_fs = next(doc for doc in FIXTURE_DOCS if doc["module"] == "ucode" and doc["slug"] == "api-fs")
    cache_payload = {
        hashlib.sha256(ucode_fs["content"].encode("utf-8")).hexdigest()[:12]: {
            "summary": "Provide filesystem access primitives for ucode scripts, including file opening and cleanup helpers. Highlight the legacy fs.oldThing() entry only for backwards-compatible maintenance.",
            "when_to_use": "Use when an OpenWrt ucode workflow needs direct file I/O or when you are reviewing legacy scripts that still mention deprecated filesystem helpers.",
            "related_topics": ["fs.open", "fs.close", "fs.oldThing"],
        }
    }
    with open(cache_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(cache_payload, handle, indent=2)


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def publish_root(outdir):
    return os.path.join(outdir, "release-tree")


def support_root(outdir):
    return os.path.join(outdir, "support-tree")


def processed_root(outdir):
    return os.path.join(os.path.dirname(outdir), "processed")


def expected_outputs(outdir, processed_dir=None, expect_fixture_wiki=True):
    publish_dir = publish_root(outdir)
    support_dir = support_root(outdir)
    if processed_dir is None:
        processed_dir = processed_root(outdir)

    outputs = [
        os.path.join(
            processed_dir,
            "L1-raw",
            "ucode",
            "c_source-api-fs.md",
        ),
        os.path.join(publish_dir, "llms.txt"),
        os.path.join(publish_dir, "llms-full.txt"),
        os.path.join(publish_dir, "AGENTS.md"),
        os.path.join(publish_dir, "README.md"),
        os.path.join(publish_dir, "index.html"),
        os.path.join(support_dir, "manifests", "cross-link-registry.json"),
        os.path.join(support_dir, "manifests", "repo-manifest.json"),
        os.path.join(support_dir, "telemetry", "CHANGES.md"),
        os.path.join(support_dir, "telemetry", "changelog.json"),
        os.path.join(support_dir, "telemetry", "signature-inventory.json"),
        os.path.join(publish_dir, "procd", "llms.txt"),
        os.path.join(publish_dir, "uci", "llms.txt"),
        os.path.join(publish_dir, "ucode", "llms.txt"),
        os.path.join(publish_dir, "wiki", "llms.txt"),
        os.path.join(publish_dir, "ucode", "bundled-reference.md"),
        os.path.join(publish_dir, "ucode", "map.md"),
        os.path.join(publish_dir, "ucode", "types", "ucode.d.ts"),
    ]

    if expect_fixture_wiki:
        outputs.insert(
            1,
            os.path.join(
                processed_dir,
                "L2-semantic",
                "wiki",
                "wiki_page-service-events.md",
            ),
        )

    return outputs


def assert_fixture_outputs(outdir, processed_dir=None, expect_ai=False, expect_fixture_wiki=True):
    publish_dir = publish_root(outdir)
    if processed_dir is None:
        processed_dir = processed_root(outdir)
    semantic_root = os.path.join(processed_dir, "L2-semantic")

    missing = [
        path
        for path in expected_outputs(outdir, processed_dir, expect_fixture_wiki=expect_fixture_wiki)
        if not os.path.exists(path)
    ]
    if missing:
        joined = "\n".join(missing)
        raise AssertionError(f"Missing expected output files:\n{joined}")

    packages_dir = os.path.join(outdir, "packages")
    zip_files = (
        sorted(file_name for file_name in os.listdir(packages_dir) if file_name.endswith(".zip"))
        if os.path.isdir(packages_dir)
        else []
    )
    if len(zip_files) != 1:
        raise AssertionError(f"Expected exactly one package zip in {packages_dir}, found: {zip_files}")
    zip_path = os.path.join(packages_dir, zip_files[0])
    if os.path.getsize(zip_path) == 0:
        raise AssertionError(f"Expected non-empty package zip: {zip_path}")

    procd_l2 = read_text(os.path.join(semantic_root, "procd", "c_source-init-service.md"))
    if expect_fixture_wiki:
        if "../uci/c_source-api-config.md" not in procd_l2:
            raise AssertionError("Expected cross-link from procd fixture to the UCI fixture output")
    elif "[uci.get()](" not in procd_l2:
        raise AssertionError("Expected extractor-enabled smoke to preserve a resolvable uci.get() cross-link")

    if expect_fixture_wiki:
        wiki_l2 = read_text(os.path.join(semantic_root, "wiki", "wiki_page-service-events.md"))
        if "[!WARNING]" not in wiki_l2:
            raise AssertionError("Expected deprecated-symbol warning to be injected into the wiki fixture output")
    else:
        wiki_semantic_dir = Path(semantic_root) / "wiki"
        published_wiki_dir = Path(publish_dir) / "wiki" / "chunked-reference"
        semantic_wiki_names = {path.name for path in wiki_semantic_dir.glob("wiki_page-*.md")}
        published_wiki_names = {path.name for path in published_wiki_dir.glob("wiki_page-*.md")}

        if not semantic_wiki_names:
            raise AssertionError("Expected extractor-enabled smoke to generate semantic wiki outputs")
        if not published_wiki_names:
            raise AssertionError("Expected extractor-enabled smoke to publish wiki chunked-reference outputs")
        if not any(name.startswith("wiki_page-guide-developer-") for name in semantic_wiki_names):
            raise AssertionError("Expected extractor-enabled smoke to include guide-developer wiki outputs")
        if not any(name.startswith("wiki_page-techref-") for name in semantic_wiki_names):
            raise AssertionError("Expected extractor-enabled smoke to include techref wiki outputs")

    monolith = read_text(os.path.join(publish_dir, "ucode", "bundled-reference.md"))
    if "ucode fs module" not in monolith or "ucode uloop module" not in monolith:
        raise AssertionError("Expected the ucode monolith to contain both seeded ucode documents")

    dts_path = os.path.join(publish_dir, "ucode", "types", "ucode.d.ts")
    dts = read_text(dts_path)
    if 'declare module "fs"' not in dts or 'declare module "uloop"' not in dts:
        raise AssertionError("Expected ucode.d.ts to contain declarations for both seeded ucode modules")

    root_llms = read_text(os.path.join(publish_dir, "llms.txt"))
    for fragment in [
        "# openwrt-docs4ai - LLM Routing Index",
        "[llms-full.txt](./llms-full.txt)",
        "- [ucode](./ucode/llms.txt):",
        "- [wiki](./wiki/llms.txt):",
    ]:
        if fragment not in root_llms:
            raise AssertionError(f"Expected root llms.txt to contain: {fragment}")

    module_llms = read_text(os.path.join(publish_dir, "ucode", "llms.txt"))
    source_link = "./chunked-reference/c_source-api-fs.md"
    map_link = "./map.md"
    bundled_link = "./bundled-reference.md"
    types_link = "./types/ucode.d.ts"
    for fragment in [
        "# ucode module",
        "> **Total Context:**",
        "## Recommended Entry Points",
        "## Tooling Surfaces",
        "## Source Documents",
        map_link,
        bundled_link,
        types_link,
        source_link,
    ]:
        if fragment not in module_llms:
            raise AssertionError(f"Expected ucode/llms.txt to contain: {fragment}")

    full_catalog = read_text(os.path.join(publish_dir, "llms-full.txt"))
    full_catalog_dts = "./ucode/types/ucode.d.ts"
    full_catalog_source = "./ucode/chunked-reference/c_source-api-fs.md"
    for fragment in [
        "# openwrt-docs4ai - Complete Flat Catalog",
        "./AGENTS.md",
        "./README.md",
        "./ucode/llms.txt",
        full_catalog_dts,
        full_catalog_source,
    ]:
        if fragment not in full_catalog:
            raise AssertionError(f"Expected llms-full.txt to contain: {fragment}")
    if not expect_fixture_wiki and "./wiki/chunked-reference/" not in full_catalog:
        raise AssertionError("Expected llms-full.txt to catalog published wiki chunked-reference outputs")

    agents = read_text(os.path.join(publish_dir, "AGENTS.md"))
    agent_fragments = ["[module]/llms.txt", "chunked-reference/", "bundled-reference.md"]
    for fragment in agent_fragments:
        if fragment not in agents:
            raise AssertionError(f"Expected AGENTS.md to describe: {fragment}")

    generated_readme = read_text(os.path.join(publish_dir, "README.md"))
    readme_fragments = ["./llms.txt", "./AGENTS.md", "./ucode/map.md"]
    for fragment in readme_fragments:
        if fragment not in generated_readme:
            raise AssertionError(f"Expected generated README.md to route readers to: {fragment}")

    index_html = read_text(os.path.join(publish_dir, "index.html"))
    index_fragments = [
        "Jump to section",
        "./llms.txt",
        "./index.html",
        "openwrt-docs4ai release tree",
        "./ucode/map.md",
    ]
    if expect_fixture_wiki:
        index_fragments.append("./wiki/chunked-reference/wiki_page-service-events.md")
    else:
        index_fragments.append("./wiki/chunked-reference/")
    for fragment in index_fragments:
        if fragment not in index_html:
            raise AssertionError(f"Expected index.html to contain: {fragment}")

    if expect_ai:
        ucode_l2 = read_text(os.path.join(semantic_root, "ucode", "c_source-api-fs.md"))
        if "ai_summary:" not in ucode_l2 or "ai_when_to_use:" not in ucode_l2:
            raise AssertionError("Expected cached AI metadata to be injected into the ucode fs fixture")

        skeleton = read_text(os.path.join(publish_dir, "ucode", "map.md"))
        if "> **Summary:**" not in skeleton:
            raise AssertionError("Expected AI summary metadata to propagate into the generated skeleton")
