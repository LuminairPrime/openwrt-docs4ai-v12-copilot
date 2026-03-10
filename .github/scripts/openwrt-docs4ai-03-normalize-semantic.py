"""
Purpose: Parallel L2 Semantic Normalization & Staging Promotion.
Phase: Process
Layers: L1 -> L2 (Normalization) -> Staging (Promotion)
Inputs: tmp/L1-raw/
Outputs: staging/L1-raw/, staging/L2-semantic/, staging/cross-link-registry.json
Environment Variables: WORKDIR, OUTDIR, OPENWRT_COMMIT, LUCI_COMMIT, UCODE_COMMIT
Dependencies: tiktoken, lib.config, shutil
Notes: Pass 1/2 handles normalization. Final block promotes intermediates to staging.
"""

import os
import re
import json
import yaml
import glob
import datetime
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config

sys.stdout.reconfigure(line_buffering=True)

try:
    import tiktoken
    encoder = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text):
        return len(encoder.encode(text))
except ImportError:
    print("[03] WARN: tiktoken missing, falling back to word count * 1.35")
    def count_tokens(text):
        return int(len(text.split()) * 1.35)

# --- Heuristics & Config ---
COMMON_WORDS = {
    "name", "type", "value", "event", "data", "code", "info", "list",
    "item", "node", "text", "form", "page", "time", "date", "user",
    "host", "port", "path", "file", "mode", "status", "error", "result",
    "state", "flags", "index", "count", "length", "size", "version",
    "base", "init", "load", "open", "read", "write", "close", "send",
    "recv", "bind", "call", "stop", "start", "reset", "clear", "check",
    "parse", "fetch", "apply", "remove", "create", "update", "delete",
    "source", "target", "output", "input", "params", "options", "config",
    "return", "object", "string", "number", "boolean", "array", "table",
    "class", "method", "property", "function", "callback", "promise",
    "procd"
}

# procd is NOT common (BUG-041)
COMMON_WORDS.discard("procd")

WIKI_WRAP_TAG_RE = re.compile(r'\\?<\/?WRAP\b[^>]*\\?>', re.IGNORECASE)
WIKI_COLOR_TAG_RE = re.compile(r'(?:\\?<\/?color\b[^>]*\\?>|&lt;\/?color\b[^&]*&gt;)', re.IGNORECASE)
WIKI_HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.MULTILINE)

def is_code_symbol(name):
    if name.lower() in COMMON_WORDS: return False
    if len(name) < 4: return False
    # CamelCase (starts with lower, contains upper)
    if re.match(r'^[a-z][a-zA-Z0-9]+$', name) and any(c.isupper() for c in name): return True
    # Namespaced or Snake_case
    if ("." in name or "_" in name) and len(name) >= 5: return True
    # Const/Enum
    if re.match(r'^[A-Z]{3,10}$', name): return True
    return False


def normalize_heading_text(text):
    return re.sub(r'\s+', ' ', text.strip()).casefold()


def strip_duplicate_lead_heading(title, content):
    lines = content.splitlines()
    if not lines:
        return content

    title_key = normalize_heading_text(title)
    first_heading_index = None
    for index, line in enumerate(lines):
        if line.startswith("# "):
            first_heading_index = index
            break
        if line.strip():
            break

    if first_heading_index is None:
        return content

    probe = first_heading_index + 1
    while probe < len(lines) and not lines[probe].strip():
        probe += 1

    if probe >= len(lines):
        return content

    match = WIKI_HEADING_RE.match(lines[probe].strip())
    if not match:
        return content

    if normalize_heading_text(match.group(2)) != title_key:
        return content

    del lines[probe]
    if probe < len(lines) and not lines[probe].strip() and probe - 1 >= 0 and not lines[probe - 1].strip():
        del lines[probe]
    return "\n".join(lines)


def collapse_duplicate_html_table_rows(content):
    output = []
    current_row = []
    previous_row = None

    for line in content.splitlines():
        stripped = line.lstrip()
        if not current_row:
            if stripped.startswith("<tr"):
                current_row = [line]
            else:
                output.append(line)
            continue

        current_row.append(line)
        if "</tr>" not in stripped:
            continue

        row_block = "\n".join(current_row)
        if row_block != previous_row:
            output.extend(current_row)
            previous_row = row_block
        current_row = []

    if current_row:
        output.extend(current_row)

    return "\n".join(output)


def clean_wiki_semantic_content(title, content):
    cleaned = WIKI_WRAP_TAG_RE.sub('', content)
    cleaned = WIKI_COLOR_TAG_RE.sub('', cleaned)
    cleaned = strip_duplicate_lead_heading(title, cleaned)
    cleaned = collapse_duplicate_html_table_rows(cleaned)
    cleaned = re.sub(r'(?m)[ \t]+$', '', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip() + "\n"

def pass_1_normalize_all(ts_now):
    print("[03] Pass 1: YAML Schema Injection & Link Registry Build")
    cross_link_registry = {"pipeline_date": ts_now, "symbols": {}}
    l2_files = []
    
    # Commit map for versioning from environment
    COMMITS = {
        "openwrt-core": os.environ.get("OPENWRT_COMMIT", "unknown"),
        "openwrt-hotplug": os.environ.get("OPENWRT_COMMIT", "unknown"),
        "procd": os.environ.get("OPENWRT_COMMIT", "unknown"),
        "uci": os.environ.get("OPENWRT_COMMIT", "unknown"),
        "wiki": "N/A",
        "luci": os.environ.get("LUCI_COMMIT", "unknown"),
        "luci-examples": os.environ.get("LUCI_COMMIT", "unknown"),
        "ucode": os.environ.get("UCODE_COMMIT", "unknown"),
    }

    for root, _, files in os.walk(L1_DIR):
        for f in files:
            if not f.endswith(".md"): continue
            md_path = os.path.join(root, f)
            meta_path = os.path.splitext(md_path)[0] + ".meta.json"
            
            with open(md_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            if not os.path.isfile(meta_path):
                print(f"[03] FAIL: Missing meta file: {meta_path}"); sys.exit(1)
            with open(meta_path, "r", encoding="utf-8") as file:
                meta = json.load(file)

            module, o_type = meta.get("module", "unknown"), meta.get("origin_type", "unknown")
            slug = meta.get("slug", os.path.splitext(f)[0])
            
            title_m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else slug

            if module == "wiki":
                content = clean_wiki_semantic_content(title, content)

            # Mermaid Injection (Specific to procd)
            if module == "procd" and "init" in title.lower():
                mermaid_tmpl = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "mermaid", "procd-init-sequence.md")
                if os.path.isfile(mermaid_tmpl):
                    with open(mermaid_tmpl, "r", encoding="utf-8") as tmpl_f:
                        content = content.replace("---\n\n", "---\n\n" + tmpl_f.read().strip() + "\n\n", 1)

            l1_rel = os.path.relpath(md_path, WORKDIR).replace("\\", "/")
            y_meta = {
                "title": title, "module": module, "origin_type": o_type,
                "token_count": count_tokens(content), "version": COMMITS.get(module, "unknown"),
                "source_file": l1_rel, "last_pipeline_run": ts_now
            }
            for k in ["upstream_path", "language", "description"]:
                if meta.get(k): y_meta[k] = meta[k]

            full_l2 = "---\n" + yaml.dump(y_meta, sort_keys=False) + "---\n" + content
            out_file = os.path.join(L2_DIR, module, f)
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, "w", encoding="utf-8", newline="\n") as out:
                out.write(full_l2)
            
            l2_files.append({"path": out_file, "module": module, "root_rel": f"{module}/{f}", "l1_rel": l1_rel})
            
            # Symbol Indexing
            for m in re.finditer(r'^#{2,4}\s+[`"]?([A-Za-z][A-Za-z0-9_.]+(?:\(.*\))?)[`"]?', content, re.MULTILINE):
                raw_node = m.group(1)
                symbol = re.split(r'\(', raw_node)[0].strip()
                if not is_code_symbol(symbol): continue
                
                # Check for deprecation only inside the current section.
                is_dep = False
                section_tail = content[m.end():]
                next_heading = re.search(r'^#{2,4}\s+', section_tail, re.MULTILINE)
                dep_window = section_tail[:next_heading.start()] if next_heading else section_tail[:1000]
                if re.search(r'\*\*[Dd]eprecated\*\*', dep_window):
                    is_dep = True

                sig = raw_node if "(" in raw_node else f"{symbol}()"
                payload = {
                    "signature": sig, "file": l1_rel,
                    "module": module,
                    "relative_target": f"../{module}/{f}", 
                    "returns": "any", "parameters": [],
                    "deprecated": is_dep
                }
                
                if symbol not in cross_link_registry["symbols"]:
                    cross_link_registry["symbols"][symbol] = payload
                elif any(x in l1_rel for x in ["ucode", "luci"]): # API docs (L2/L3) win conflicts
                    cross_link_registry["symbols"][symbol] = payload

    reg_path = os.path.join(WORKDIR, "cross-link-registry.json")
    with open(reg_path, "w", encoding="utf-8") as rf:
        json.dump(cross_link_registry, rf, indent=2)
    return l2_files, cross_link_registry, reg_path

def pass_2_link_all(l2_files, registry):
    print("[03] Pass 2: Injecting Cross-Links")
    sorted_syms = sorted(registry["symbols"].items(), key=lambda x: -len(x[0]))
    patterns = [(s, m["relative_target"], re.compile(rf'\b{re.escape(s)}\b(?:\(\))?')) for s, m in sorted_syms]

    for info in l2_files:
        with open(info["path"], "r", encoding="utf-8") as f: content = f.read()
        
        # Protection: Skip frontmatter, fenced code blocks, existing links, inline code, and headers.
        prot = set()
        fm_match = re.match(r'^---\r?\n.*?\r?\n---\r?\n?', content, re.DOTALL)
        if fm_match:
            prot.update(range(fm_match.start(), fm_match.end()))
        for m in re.finditer(r'```.*?```|~~~.*?~~~', content, re.DOTALL):
            prot.update(range(m.start(), m.end()))
        for m in re.finditer(r'^\s*#+ .+$', content, re.MULTILINE):
            prot.update(range(m.start(), m.end()))
        for m in re.finditer(r'<[^>\n]+>', content):
            prot.update(range(m.start(), m.end()))
        for m in re.finditer(r'^\s*[*-]\s+\[.*\]\(#.*\).*$' , content, re.MULTILINE):
            prot.update(range(m.start(), m.end()))
        for m in re.finditer(r'`[^`\n]+`|\[[^\]]+\]\([^)]+\)', content):
            prot.update(range(m.start(), m.end()))
            
        spans = []
        for sym, target, pat in patterns:
            if target.endswith(info["root_rel"]): continue
            for m in pat.finditer(content):
                if not any(i in prot for i in range(m.start(), m.end())):
                    if not any(s <= m.start() < e for s, e, _ in spans):
                        spans.append((m.start(), m.end(), f"[{m.group(0)}]({target})"))
        
        if spans:
            spans.sort(key=lambda x: x[0])
            new_c, last = [], 0
            for s, e, rep in spans:
                new_c.append(content[last:s]); new_c.append(rep); last = e
            new_c.append(content[last:])
            with open(info["path"], "w", encoding="utf-8", newline="\n") as f:
                f.write("".join(new_c))

def pass_3_deprecation_warnings(l2_files, registry):
    print("[03] Pass 3: Injecting Deprecation Warnings")
    deprecated_symbols = {s: m for s, m in registry["symbols"].items() if m.get("deprecated")}
    if not deprecated_symbols: return

    for info in l2_files:
        if info["module"] != "wiki": continue # Warnings priority for wiki usage
        
        with open(info["path"], "r", encoding="utf-8") as f: content = f.read()
        
        warnings = []
        for sym, meta in deprecated_symbols.items():
            # If the file contains a link to this deprecated symbol
            link_pat = rf'\[.*?\]\(\.\.\/{re.escape(meta["relative_target"].lstrip("./"))}\)'
            if re.search(link_pat, content):
                warnings.append(f"- `{sym}` (see [{sym}]({meta['relative_target']}))")
        
        if warnings:
            callout = "\n> [!WARNING]\n"
            callout += "> This page references deprecated symbols from the official API documentation:\n"
            for w in warnings: callout += f"> {w}\n"
            callout += "\n"
            
            # Inject after frontmatter
            if content.startswith("---"):
                end_fm = content.find("---\n", 3)
                if end_fm != -1:
                    content = content[:end_fm+4] + callout + content[end_fm+4:]
            else:
                content = callout + content
                
            with open(info["path"], "w", encoding="utf-8", newline="\n") as f:
                f.write(content)

def promote_to_staging(registry_path):
    print("[03] Promoting to staging OUTDIR")
    dst_root = config.OUTDIR
    os.makedirs(dst_root, exist_ok=True)
    for d in [("L1-raw", L1_DIR), ("L2-semantic", L2_DIR)]:
        dst = os.path.join(dst_root, d[0])
        if os.path.exists(dst): shutil.rmtree(dst)
        shutil.copytree(d[1], dst)
    for f in [registry_path, os.path.join(WORKDIR, "repo-manifest.json")]:
        if os.path.isfile(f): shutil.copy2(f, os.path.join(dst_root, os.path.basename(f)))

if __name__ == "__main__":
    WORKDIR, L1_DIR, L2_DIR = config.WORKDIR, config.L1_RAW_WORKDIR, config.L2_SEMANTIC_WORKDIR
    if not os.path.isdir(L1_DIR):
        print(f"[03] FAIL: L1 input directory not found: {L1_DIR}"); sys.exit(1)
    
    TS = datetime.datetime.now(datetime.UTC).isoformat()
    l2_list, reg, r_path = pass_1_normalize_all(TS)
    pass_2_link_all(l2_list, reg)
    pass_3_deprecation_warnings(l2_list, reg)
    promote_to_staging(r_path)
    print("[03] Complete.")
