import hashlib
import json
import os
import re
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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
    "openwrt-docs4ai-06-generate-llm-routing-indexes.py",
    "openwrt-docs4ai-07-generate-web-index.py",
    "openwrt-docs4ai-08-validate-output.py",
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


def build_env(workdir, outdir, run_ai=False, extra_env=None):
    env = os.environ.copy()
    env["WORKDIR"] = workdir
    env["OUTDIR"] = outdir
    env["SKIP_AI"] = "false" if run_ai else "true"
    env["AI_DATA_BASE_DIR"] = os.path.join(workdir, "ai-data", "base")
    env["AI_DATA_OVERRIDE_DIR"] = os.path.join(workdir, "ai-data", "override")
    env["VALIDATE_MODE"] = env.get("VALIDATE_MODE", "hard")

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


def seed_l1_fixtures(workdir):
    l1_root = os.path.join(workdir, "L1-raw")
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
    with open(os.path.join(workdir, "repo-manifest.json"), "w", encoding="utf-8", newline="\n") as handle:
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


def expected_outputs(outdir):
    return [
        os.path.join(outdir, "L1-raw", "ucode", "c_source-api-fs.md"),
        os.path.join(outdir, "L2-semantic", "wiki", "wiki_page-service-events.md"),
        os.path.join(outdir, "llms.txt"),
        os.path.join(outdir, "llms-full.txt"),
        os.path.join(outdir, "AGENTS.md"),
        os.path.join(outdir, "README.md"),
        os.path.join(outdir, "index.html"),
        os.path.join(outdir, "CHANGES.md"),
        os.path.join(outdir, "changelog.json"),
        os.path.join(outdir, "signature-inventory.json"),
        os.path.join(outdir, "ucode", "ucode-complete-reference.md"),
        os.path.join(outdir, "ucode", "ucode-skeleton.md"),
        os.path.join(outdir, "ucode", "ucode.d.ts"),
    ]


def assert_fixture_outputs(outdir, expect_ai=False):
    missing = [path for path in expected_outputs(outdir) if not os.path.exists(path)]
    if missing:
        joined = "\n".join(missing)
        raise AssertionError(f"Missing expected output files:\n{joined}")

    procd_l2 = read_text(os.path.join(outdir, "L2-semantic", "procd", "c_source-init-service.md"))
    if "../uci/c_source-api-config.md" not in procd_l2:
        raise AssertionError("Expected cross-link from procd fixture to the UCI fixture output")

    wiki_l2 = read_text(os.path.join(outdir, "L2-semantic", "wiki", "wiki_page-service-events.md"))
    if "[!WARNING]" not in wiki_l2:
        raise AssertionError("Expected deprecated-symbol warning to be injected into the wiki fixture output")

    monolith = read_text(os.path.join(outdir, "ucode", "ucode-complete-reference.md"))
    if "ucode fs module" not in monolith or "ucode uloop module" not in monolith:
        raise AssertionError("Expected the ucode monolith to contain both seeded ucode documents")

    dts = read_text(os.path.join(outdir, "ucode", "ucode.d.ts"))
    if 'declare module "fs"' not in dts or 'declare module "uloop"' not in dts:
        raise AssertionError("Expected ucode.d.ts to contain declarations for both seeded ucode modules")

    if expect_ai:
        ucode_l2 = read_text(os.path.join(outdir, "L2-semantic", "ucode", "c_source-api-fs.md"))
        if "ai_summary:" not in ucode_l2 or "ai_when_to_use:" not in ucode_l2:
            raise AssertionError("Expected cached AI metadata to be injected into the ucode fs fixture")

        skeleton = read_text(os.path.join(outdir, "ucode", "ucode-skeleton.md"))
        if "> **Summary:**" not in skeleton:
            raise AssertionError("Expected AI summary metadata to propagate into the generated skeleton")