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
import datetime
import sys
import shutil
from collections import Counter
from html import unescape

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from lib import config, repo_manifest

try:
    from bs4 import BeautifulSoup, Comment, NavigableString, Tag
    from markdownify import markdownify as markdownify_html
except ImportError:
    BeautifulSoup = None
    Comment = None
    NavigableString = None
    Tag = None
    markdownify_html = None

sys.stdout.reconfigure(line_buffering=True)

WORKDIR = config.WORKDIR
L1_DIR = config.L1_RAW_WORKDIR
L2_DIR = config.L2_SEMANTIC_WORKDIR

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
WIKI_SORTABLE_TAG_RE = re.compile(r'(?:\\?<\/?sortable\b[^>]*\\?>|&lt;\/?sortable\b[^&]*&gt;)', re.IGNORECASE)
WIKI_HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.MULTILINE)
HTML_COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)
TABLE_BLOCK_RE = re.compile(r'<table\b.*?</table>', re.IGNORECASE | re.DOTALL)
FOOTNOTE_REF_RE = re.compile(
    r'<a\b[^>]*href="#fn(?P<id>[^"]+)"[^>]*>\s*<sup>\s*(?P<label>.*?)\s*</sup>\s*</a>',
    re.IGNORECASE | re.DOTALL,
)
FOOTNOTE_ASIDE_RE = re.compile(
    r'<aside\b[^>]*class="[^"]*\bfootnotes\b[^"]*"[^>]*>.*?</aside>',
    re.IGNORECASE | re.DOTALL,
)
INLINE_HTML_FRAGMENT_RE = re.compile(
    r'<(?P<tag>a|code|strong|b|em|i|u|sup|sub|span|div)\b[^>]*>.*?</(?P=tag)>|<br\s*/?>|<img\b[^>]*>',
    re.IGNORECASE | re.DOTALL,
)
CODE_FENCE_BLOCK_RE = re.compile(r'(```.*?```|~~~.*?~~~)', re.DOTALL)

_HTML_NORMALIZER_WARNING_EMITTED = False


def html_normalizer_available():
    global _HTML_NORMALIZER_WARNING_EMITTED
    if BeautifulSoup is not None and markdownify_html is not None:
        return True

    if not _HTML_NORMALIZER_WARNING_EMITTED:
        print("[03] WARN: beautifulsoup4/html5lib/markdownify missing, falling back to legacy wiki cleanup")
        _HTML_NORMALIZER_WARNING_EMITTED = True
    return False


def parse_html_fragment(fragment):
    if not html_normalizer_available():
        return None

    for parser in ("html5lib", "html.parser"):
        try:
            return BeautifulSoup(fragment, parser)
        except Exception:
            continue
    return None


def is_code_symbol(name):
    if name.lower() in COMMON_WORDS:
        return False
    if len(name) < 4:
        return False
    if re.match(r'^[a-z][a-zA-Z0-9]+$', name) and any(char.isupper() for char in name):
        return True
    if ("." in name or "_" in name) and len(name) >= 5:
        return True
    if re.match(r'^[A-Z]{3,10}$', name):
        return True
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

    def flush_current_row():
        nonlocal current_row, previous_row
        if not current_row:
            return
        row_block = "\n".join(current_row)
        if row_block != previous_row:
            output.extend(current_row)
            previous_row = row_block
        current_row = []

    for line in content.splitlines():
        stripped = line.lstrip()
        if not current_row:
            if stripped.startswith("<tr"):
                current_row = [line]
                if "</tr>" in stripped:
                    flush_current_row()
            else:
                output.append(line)
            continue

        current_row.append(line)
        if "</tr>" not in stripped:
            continue

        flush_current_row()

    if current_row:
        output.extend(current_row)

    return "\n".join(output)


def legacy_clean_wiki_semantic_content(title, content):
    cleaned = WIKI_WRAP_TAG_RE.sub('', content)
    cleaned = WIKI_COLOR_TAG_RE.sub('', cleaned)
    cleaned = strip_duplicate_lead_heading(title, cleaned)
    cleaned = collapse_duplicate_html_table_rows(cleaned)
    cleaned = re.sub(r'(?m)[ \t]+$', '', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip() + "\n"


def transform_outside_code_fences(content, transformer):
    pieces = []
    last_index = 0
    for match in CODE_FENCE_BLOCK_RE.finditer(content):
        pieces.append(transformer(content[last_index:match.start()]))
        pieces.append(match.group(0))
        last_index = match.end()
    pieces.append(transformer(content[last_index:]))
    return "".join(pieces)


def collapse_inline_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


def normalize_markdown_text(text, multiline=True):
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    normalized = re.sub(r'(?m)[ \t]+$', '', normalized)
    normalized = re.sub(r'\n{3,}', '\n\n', normalized)
    if multiline:
        return normalized.strip()
    normalized = re.sub(r'\s*\n\s*', '; ', normalized)
    normalized = re.sub(r'\s{2,}', ' ', normalized)
    return normalized.strip(' ;')


def normalize_footnote_label(raw_label):
    label = re.sub(r'[^A-Za-z0-9_-]+', '', (raw_label or '').strip())
    return label or "note"


def is_decorative_icon_image(tag):
    signature = " ".join(filter(None, [tag.get("src", ""), tag.get("alt", "")])).lower()
    return "/meta/icons/" in signature or "dialog-information" in signature or "outdated" in signature


def detect_callout_kind(signature):
    signature = signature.lower()
    if any(token in signature for token in ["outdated", "historic", "deprecated", "warning", "caution"]):
        return "WARNING"
    if any(token in signature for token in ["tip", "help"]):
        return "TIP"
    return "NOTE"


def render_image_markdown(tag, strip_icon_images=False):
    if is_decorative_icon_image(tag):
        return "" if strip_icon_images or is_decorative_icon_image(tag) else ""

    alt = collapse_inline_whitespace(unescape(tag.get("alt", "")))
    src = tag.get("src", "").strip()
    if not src:
        return alt
    return f"![{alt or os.path.basename(src)}]({src})"


def render_unknown_html_node(node, preserve_linebreaks=True):
    if markdownify_html is None:
        return normalize_markdown_text(node.get_text("\n" if preserve_linebreaks else " ", strip=False), multiline=preserve_linebreaks)
    rendered = markdownify_html(str(node), heading_style="ATX", bullets="-")
    return normalize_markdown_text(rendered, multiline=preserve_linebreaks)


def render_list(tag, strip_icon_images=False):
    ordered = tag.name.lower() == "ol"
    lines = []
    for index, item in enumerate(tag.find_all("li", recursive=False), start=1):
        prefix = f"{index}. " if ordered else "- "
        body = normalize_markdown_text(render_html_nodes(item.contents, preserve_linebreaks=True, strip_icon_images=strip_icon_images), multiline=True)
        if not body:
            continue
        body_lines = body.splitlines()
        lines.append(prefix + body_lines[0])
        for line in body_lines[1:]:
            lines.append((" " * len(prefix) + line) if line else "")
    if not lines:
        return ""
    return "\n".join(lines) + "\n\n"


def render_html_nodes(nodes, preserve_linebreaks=True, strip_icon_images=False):
    parts = []
    for node in nodes:
        if Comment is not None and isinstance(node, Comment):
            continue
        if NavigableString is not None and isinstance(node, NavigableString):
            parts.append(unescape(str(node)))
            continue
        if Tag is None or not isinstance(node, Tag):
            continue

        name = (node.name or "").lower()
        if name in {"span", "div", "thead", "tbody", "tfoot", "th", "td"}:
            parts.append(render_html_nodes(node.contents, preserve_linebreaks=preserve_linebreaks, strip_icon_images=strip_icon_images))
            continue
        if name == "a":
            label = normalize_markdown_text(
                render_html_nodes(node.contents, preserve_linebreaks=False, strip_icon_images=strip_icon_images),
                multiline=False,
            ) or node.get("href", "").strip()
            href = node.get("href", "").strip()
            parts.append(f"[{label}]({href})" if href else label)
            continue
        if name == "code":
            code_text = collapse_inline_whitespace(
                render_html_nodes(node.contents, preserve_linebreaks=False, strip_icon_images=strip_icon_images)
            )
            parts.append(f"`{code_text}`" if code_text else "")
            continue
        if name in {"strong", "b"}:
            strong_text = normalize_markdown_text(
                render_html_nodes(node.contents, preserve_linebreaks=False, strip_icon_images=strip_icon_images),
                multiline=False,
            )
            parts.append(f"**{strong_text}**" if strong_text else "")
            continue
        if name in {"em", "i"}:
            emphasis_text = normalize_markdown_text(
                render_html_nodes(node.contents, preserve_linebreaks=False, strip_icon_images=strip_icon_images),
                multiline=False,
            )
            parts.append(f"*{emphasis_text}*" if emphasis_text else "")
            continue
        if name == "u":
            underline_text = normalize_markdown_text(
                render_html_nodes(node.contents, preserve_linebreaks=False, strip_icon_images=strip_icon_images),
                multiline=False,
            )
            parts.append(f"**{underline_text}**" if underline_text else "")
            continue
        if name in {"sup", "sub"}:
            parts.append(
                normalize_markdown_text(
                    render_html_nodes(node.contents, preserve_linebreaks=False, strip_icon_images=strip_icon_images),
                    multiline=False,
                )
            )
            continue
        if name == "br":
            parts.append("\n" if preserve_linebreaks else "; ")
            continue
        if name == "p":
            paragraph = normalize_markdown_text(
                render_html_nodes(node.contents, preserve_linebreaks=True, strip_icon_images=strip_icon_images),
                multiline=True,
            )
            if paragraph:
                parts.append(paragraph + "\n\n")
            continue
        if name in {"ul", "ol"}:
            parts.append(render_list(node, strip_icon_images=strip_icon_images))
            continue
        if name == "li":
            item_text = normalize_markdown_text(
                render_html_nodes(node.contents, preserve_linebreaks=True, strip_icon_images=strip_icon_images),
                multiline=True,
            )
            if item_text:
                parts.append(f"- {item_text}\n")
            continue
        if name == "img":
            parts.append(render_image_markdown(node, strip_icon_images=strip_icon_images))
            continue
        if name == "table":
            table_markdown = render_html_table(str(node))
            if table_markdown == str(node):
                parts.append(normalize_markdown_text(node.get_text("\n", strip=True), multiline=preserve_linebreaks))
            else:
                parts.append(table_markdown)
            continue
        if name == "aside" and "footnotes" in " ".join(node.get("class", [])):
            continue

        parts.append(render_unknown_html_node(node, preserve_linebreaks=preserve_linebreaks))

    return "".join(parts)


def render_html_fragment(fragment_html, preserve_linebreaks=True, strip_icon_images=False):
    soup = parse_html_fragment(fragment_html)
    if soup is None:
        return normalize_markdown_text(unescape(fragment_html), multiline=preserve_linebreaks)
    root = soup.body if getattr(soup, "body", None) else soup
    rendered = render_html_nodes(root.contents, preserve_linebreaks=preserve_linebreaks, strip_icon_images=strip_icon_images)
    return normalize_markdown_text(rendered, multiline=preserve_linebreaks)


def flatten_table_cell_text(text):
    flattened = normalize_markdown_text(text, multiline=False)
    return flattened.replace("|", r"\|") or " "


def blank_table_cell():
    return {
        "markdown": "",
        "flat_text": " ",
        "has_icon": False,
        "icon_hint": None,
    }


def parse_html_table(table_html):
    soup = parse_html_fragment(table_html)
    if soup is None:
        return None

    table = soup.find("table")
    if table is None:
        return None

    rows = []
    has_header = False
    has_rowspan = False

    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if not cells:
            cells = tr.find_all(["th", "td"])
        if not cells:
            continue

        row = []
        for cell in cells:
            try:
                colspan = max(int(cell.get("colspan", 1)), 1)
            except ValueError:
                colspan = 1
            try:
                rowspan = max(int(cell.get("rowspan", 1)), 1)
            except ValueError:
                rowspan = 1

            has_header = has_header or cell.name == "th"
            has_rowspan = has_rowspan or rowspan > 1

            icon_signature = []
            for image in cell.find_all("img"):
                icon_signature.extend([image.get("alt", ""), image.get("src", "")])

            markdown = render_html_fragment(
                "".join(str(part) for part in cell.contents),
                preserve_linebreaks=True,
                strip_icon_images=False,
            )
            cell_info = {
                "markdown": markdown,
                "flat_text": flatten_table_cell_text(markdown),
                "has_icon": bool(cell.find("img")),
                "icon_hint": detect_callout_kind(" ".join(filter(None, icon_signature + [cell.get_text(" ", strip=True)]))),
            }
            row.append(cell_info)
            for _ in range(colspan - 1):
                row.append(dict(cell_info))
        rows.append(row)

    column_count = max((len(row) for row in rows), default=0)
    return {
        "rows": rows,
        "has_header": has_header,
        "has_rowspan": has_rowspan,
        "column_count": column_count,
    }


def pad_table_rows(rows, column_count):
    padded_rows = []
    for row in rows:
        padded_rows.append(row + [blank_table_cell() for _ in range(column_count - len(row))])
    return padded_rows


def is_callout_table(table_data):
    rows = table_data["rows"]
    column_count = table_data["column_count"]
    if not rows or table_data["has_header"] or len(rows) > 3:
        return False
    if column_count == 1 and len(rows) <= 2:
        return True
    if column_count != 2:
        return False
    first_column = [row[0] for row in rows if row]
    return any(cell["has_icon"] or cell["icon_hint"] for cell in first_column)


def classify_html_table(table_data):
    rows = table_data["rows"]
    if not rows or table_data["has_rowspan"]:
        return "preserve"
    if is_callout_table(table_data):
        return "callout"
    if table_data["column_count"] <= 4 and not (not table_data["has_header"] and len(rows) == 1):
        return "markdown"
    return "tsv"


def render_callout_table(table_data):
    rows = table_data["rows"]
    kinds = [row[0]["icon_hint"] for row in rows if row and row[0].get("icon_hint")]
    callout_kind = Counter(kinds).most_common(1)[0][0] if kinds else "NOTE"
    body_blocks = []
    for row in rows:
        if not row:
            continue
        target_cell = row[-1]
        block = normalize_markdown_text(target_cell["markdown"], multiline=True)
        if block:
            body_blocks.append(block)
    if not body_blocks:
        return ""

    lines = [f"> [!{callout_kind}]"]
    for block_index, block in enumerate(body_blocks):
        if block_index:
            lines.append(">")
        for line in block.splitlines():
            lines.append(f"> {line}" if line else ">")
    return "\n".join(lines)


def render_markdown_table(table_data):
    padded_rows = pad_table_rows(table_data["rows"], table_data["column_count"])
    if not padded_rows:
        return ""

    if table_data["has_header"]:
        header_cells = [cell["flat_text"] for cell in padded_rows[0]]
        data_rows = padded_rows[1:]
    else:
        header_cells = [f"Column {index}" for index in range(1, table_data["column_count"] + 1)]
        data_rows = padded_rows

    if not data_rows:
        return ""

    lines = [
        "| " + " | ".join(header_cells) + " |",
        "| " + " | ".join(["---"] * len(header_cells)) + " |",
    ]
    for row in data_rows:
        lines.append("| " + " | ".join(cell["flat_text"] for cell in row) + " |")
    return "\n".join(lines)


def render_tsv_table(table_data):
    padded_rows = pad_table_rows(table_data["rows"], table_data["column_count"])
    if not padded_rows:
        return ""

    lines = []
    for row in padded_rows:
        line = "\t".join(cell["flat_text"].replace("\t", "    ") for cell in row)
        lines.append(line.rstrip())
    return "```tsv\n" + "\n".join(lines).rstrip() + "\n```"


def render_html_table(table_html):
    table_data = parse_html_table(table_html)
    if table_data is None:
        return table_html

    kind = classify_html_table(table_data)
    if kind == "callout":
        rendered = render_callout_table(table_data)
    elif kind == "markdown":
        rendered = render_markdown_table(table_data)
    elif kind == "tsv":
        rendered = render_tsv_table(table_data)
    else:
        rendered = ""

    return rendered.strip() if rendered else table_html


def convert_footnotes_to_markdown(content):
    converted = FOOTNOTE_REF_RE.sub(
        lambda match: f"[^{normalize_footnote_label(match.group('label') or match.group('id'))}]",
        content,
    )

    def replace_aside(match):
        soup = parse_html_fragment(match.group(0))
        if soup is None:
            return match.group(0)
        aside = soup.find("aside")
        if aside is None:
            return match.group(0)

        definitions = []
        for item in aside.find_all("li"):
            note_id = normalize_footnote_label(item.get("id", "").replace("fn", "", 1))
            for backlink in item.find_all("a"):
                href = backlink.get("href", "")
                if href.startswith("#fnref"):
                    backlink.decompose()
            body = render_html_nodes(item.contents, preserve_linebreaks=True, strip_icon_images=True)
            body = normalize_markdown_text(body, multiline=True)
            if not body:
                continue
            body_lines = body.splitlines()
            definition = [f"[^{note_id}]: {body_lines[0]}"]
            for line in body_lines[1:]:
                definition.append(f"    {line}" if line else "")
            definitions.append("\n".join(definition))

        if not definitions:
            return ""
        return "\n\n" + "\n".join(definitions) + "\n\n"

    return FOOTNOTE_ASIDE_RE.sub(replace_aside, converted)


def normalize_html_tables(content):
    def replace_tables(segment):
        output = []
        last_index = 0
        for match in TABLE_BLOCK_RE.finditer(segment):
            output.append(segment[last_index:match.start()])
            rendered = render_html_table(match.group(0))
            output.append(match.group(0) if rendered == match.group(0) else f"\n\n{rendered}\n\n")
            last_index = match.end()
        output.append(segment[last_index:])
        return "".join(output)

    return transform_outside_code_fences(content, replace_tables)


def normalize_inline_html_residue(content):
    def replace_inline(segment):
        previous = None
        current = segment
        for _ in range(3):
            if current == previous:
                break
            previous = current
            current = INLINE_HTML_FRAGMENT_RE.sub(
                lambda match: render_html_fragment(match.group(0), preserve_linebreaks=True, strip_icon_images=False),
                current,
            )
        current = re.sub(r'</?(?:span|div)\b[^>]*>', '', current, flags=re.IGNORECASE)
        current = re.sub(r'</?(?:u|sup|sub)\b[^>]*>', '', current, flags=re.IGNORECASE)
        current = re.sub(r'<br\s*/?>', '\n', current, flags=re.IGNORECASE)
        return current

    return transform_outside_code_fences(content, replace_inline)


def normalize_wiki_semantic_content_v2(title, content):
    normalized = WIKI_SORTABLE_TAG_RE.sub('', content)
    normalized = HTML_COMMENT_RE.sub('', normalized)
    normalized = convert_footnotes_to_markdown(normalized)
    normalized = normalize_html_tables(normalized)
    normalized = normalize_inline_html_residue(normalized)
    normalized = strip_duplicate_lead_heading(title, normalized)
    normalized = re.sub(r'(?m)[ \t]+$', '', normalized)
    normalized = re.sub(r'\n{3,}', '\n\n', normalized)
    return normalized.strip() + "\n"


def clean_wiki_semantic_content(title, content):
    cleaned = legacy_clean_wiki_semantic_content(title, content)
    if not html_normalizer_available():
        return cleaned
    return normalize_wiki_semantic_content_v2(title, cleaned)


def resolve_pipeline_commits():
    env_snapshot = {key: os.environ.get(key) for key in repo_manifest.COMMIT_ENV_TO_MANIFEST_KEY}
    missing = [key for key, value in env_snapshot.items() if not value]
    commits, manifest_path = repo_manifest.resolve_commit_environment(
        env=env_snapshot,
        extra_manifest_paths=[config.REPO_MANIFEST_PATH, os.path.join(config.OUTDIR, "repo-manifest.json")],
    )

    if missing and manifest_path:
        print(f"[03] INFO: Loaded missing commit versions from {manifest_path}")

    return {
        "openwrt-core": commits["OPENWRT_COMMIT"],
        "openwrt-hotplug": commits["OPENWRT_COMMIT"],
        "procd": commits["OPENWRT_COMMIT"],
        "uci": commits["OPENWRT_COMMIT"],
        "wiki": "N/A",
        "luci": commits["LUCI_COMMIT"],
        "luci-examples": commits["LUCI_COMMIT"],
        "ucode": commits["UCODE_COMMIT"],
    }

def pass_1_normalize_all(ts_now):
    print("[03] Pass 1: YAML Schema Injection & Link Registry Build")
    cross_link_registry = {"pipeline_date": ts_now, "symbols": {}}
    l2_files = []

    for root, _, files in os.walk(L1_DIR):
        for f in files:
            if not f.endswith(".md"):
                continue
            md_path = os.path.join(root, f)
            meta_path = os.path.splitext(md_path)[0] + ".meta.json"
            
            with open(md_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            if not os.path.isfile(meta_path):
                print(f"[03] FAIL: Missing meta file: {meta_path}")
                sys.exit(1)
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
                "token_count": count_tokens(content),
                "source_file": l1_rel, "last_pipeline_run": ts_now
            }
            # Carry source_commit from L1 sidecar (git-backed modules only; wiki/cookbook omit it)
            if meta.get("source_commit"):
                y_meta["source_commit"] = meta["source_commit"]
            # Carry optional provenance and routing fields from L1 sidecar
            for k in ["source_url", "source_locator", "language", "description",
                      "routing_summary", "routing_keywords", "routing_priority",
                      "era_status", "audience_hint",
                      "when_to_use", "related_modules", "verification_basis",
                      "reviewed_by", "last_reviewed"]:
                if meta.get(k):
                    y_meta[k] = meta[k]

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
                if not is_code_symbol(symbol):
                    continue
                
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
        with open(info["path"], "r", encoding="utf-8") as f:
            content = f.read()
        
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
            if target.endswith(info["root_rel"]):
                continue
            for m in pat.finditer(content):
                if not any(i in prot for i in range(m.start(), m.end())):
                    if not any(s <= m.start() < e for s, e, _ in spans):
                        spans.append((m.start(), m.end(), f"[{m.group(0)}]({target})"))
        
        if spans:
            spans.sort(key=lambda x: x[0])
            new_c, last = [], 0
            for s, e, rep in spans:
                new_c.append(content[last:s])
                new_c.append(rep)
                last = e
            new_c.append(content[last:])
            with open(info["path"], "w", encoding="utf-8", newline="\n") as f:
                f.write("".join(new_c))

def pass_3_deprecation_warnings(l2_files, registry):
    print("[03] Pass 3: Injecting Deprecation Warnings")
    deprecated_symbols = {s: m for s, m in registry["symbols"].items() if m.get("deprecated")}
    if not deprecated_symbols:
        return

    for info in l2_files:
        if info["module"] != "wiki":
            continue  # Warnings priority for wiki usage
        
        with open(info["path"], "r", encoding="utf-8") as f:
            content = f.read()
        
        warnings = []
        for sym, meta in deprecated_symbols.items():
            # If the file contains a link to this deprecated symbol
            link_pat = rf'\[.*?\]\(\.\.\/{re.escape(meta["relative_target"].lstrip("./"))}\)'
            if re.search(link_pat, content):
                warnings.append(f"- `{sym}` (see [{sym}]({meta['relative_target']}))")
        
        if warnings:
            callout = "\n> [!WARNING]\n"
            callout += "> This page references deprecated symbols from the official API documentation:\n"
            for w in warnings:
                callout += f"> {w}\n"
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
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(d[1], dst)
    for f in [registry_path, os.path.join(WORKDIR, "repo-manifest.json")]:
        if os.path.isfile(f):
            shutil.copy2(f, os.path.join(dst_root, os.path.basename(f)))

if __name__ == "__main__":
    if not os.path.isdir(L1_DIR):
        print(f"[03] FAIL: L1 input directory not found: {L1_DIR}")
        sys.exit(1)
    
    TS = datetime.datetime.now(datetime.UTC).isoformat()
    l2_list, reg, r_path = pass_1_normalize_all(TS)
    pass_2_link_all(l2_list, reg)
    pass_3_deprecation_warnings(l2_list, reg)
    promote_to_staging(r_path)
    print("[03] Complete.")
