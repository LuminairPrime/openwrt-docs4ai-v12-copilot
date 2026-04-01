"""
Purpose: Generates TypeScript declaration files (.d.ts) for the LuCI JavaScript framework.
Phase: Indexing
Layers: L3
Inputs: WORKDIR/repo-luci/modules/luci-base/htdocs/luci-static/resources/*.js
Outputs: OUTDIR/luci/luci-env.d.ts, OUTDIR/release-tree/luci/types/luci-env.d.ts
Environment Variables: WORKDIR, OUTDIR
Dependencies: lib.config

Notes:
  Approach 2 chosen — L2 markdown for form/rpc/uci was too sparse to extract reliable type
  information. Specifically:
    - form.md contained only global helpers (isEqual, isContained), not class methods.
    - uci.md contained only the isEmpty helper, not LuCI.uci.load/get/set.
    - rpc.md, view.md, and network.md were absent from the L2 corpus entirely.
  JS source files are therefore parsed directly from the cloned repo at WORKDIR/repo-luci/.

  Scope is intentionally limited to the essential API namespaces per spec guard rail:
    LuCI.form  — Map, JSONMap, AbstractSection, TypedSection, TableSection, NamedSection,
                 AbstractValue, Value, DynamicList, ListValue, Flag, MultiValue, TextValue,
                 Button, HiddenValue
    LuCI.rpc   — declare, addInterceptor, removeInterceptor, getSessionID
    LuCI.uci   — load, unload, add, remove, sections, get, set, unset, save, apply
    LuCI.view  — lifecycle override points (load, render, handleSave, handleSaveApply,
                 handleReset, addFooter)
    LuCI.dom   — elem, parse, matches, parent, append, content, attr, data, bindClassInstance
    LuCI.request — get, post, cancel, batchedGet, batchedPost
    LuCI.network — (stub — network.js API surface is large; only class-level declaration)

  Auto-discovery of the full LuCI API surface is explicitly out of scope.
  If the cloned repo is not present, the script emits a stub .d.ts and exits without error.
"""

import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from lib import config  # noqa: E402

sys.stdout.reconfigure(line_buffering=True)

WORKDIR = config.WORKDIR
OUTDIR = config.OUTDIR
RELEASE_TREE_DIR = config.RELEASE_TREE_DIR

LUCI_REPO_PATH = os.path.join(WORKDIR, "repo-luci")
LUCI_JS_BASE = os.path.join(LUCI_REPO_PATH, "modules", "luci-base", "htdocs", "luci-static", "resources")

JS_FILES = {
    "form": os.path.join(LUCI_JS_BASE, "form.js"),
    "rpc": os.path.join(LUCI_JS_BASE, "rpc.js"),
    "uci": os.path.join(LUCI_JS_BASE, "uci.js"),
    "luci": os.path.join(LUCI_JS_BASE, "luci.js"),  # contains view + dom + request
    "network": os.path.join(LUCI_JS_BASE, "network.js"),
}

print("[05e] Generating luci-env.d.ts IDE type declarations")


# ---------------------------------------------------------------------------
# JSDoc parsing helpers
# ---------------------------------------------------------------------------

_JSDOC_RE = re.compile(r"/\*\*(.*?)\*/", re.DOTALL)

_PARAM_RE = re.compile(r"@param\s+\{([^}]+)\}\s+\[?([a-zA-Z0-9_$]+)\]?", re.MULTILINE)

_RETURNS_RE = re.compile(r"@returns?\s+\{([^}]+)\}", re.MULTILINE)

_CLASS_RE = re.compile(r"@class\s+(\S+)", re.MULTILINE)

_MEMBEROF_RE = re.compile(r"@memberof\s+([^\s*]+)", re.MULTILINE)


# Simpler type conversions used repeatedly
_JS_TYPE_MAP = {
    "string": "string",
    "number": "number",
    "boolean": "boolean",
    "null": "null",
    "undefined": "undefined",
    "void": "void",
    "*": "any",
    "any": "any",
    "object": "object",
    "Object": "Record<string, unknown>",
    "function": "(...args: any[]) => any",
    "Function": "(...args: any[]) => any",
    "Node": "Node",
    "HTMLElement": "HTMLElement",
    "Event": "Event",
    "Error": "Error",
    "Promise": "Promise<unknown>",
    "Array": "unknown[]",
}


def _convert_type(js_type: str) -> str:
    """
    Convert a JSDoc type annotation to a TypeScript type string.

    Handles:
    - Simple types: string, number, boolean, null, *, void
    - Union types: string|string[], null|string|string[]
    - Generic types: Promise<T>, Array<T>, Object<K, V>
    - LuCI-specific: LuCI.uci.SectionObject, LuCI.form.AbstractSection
    """
    raw = js_type.strip()

    if raw in _JS_TYPE_MAP:
        return _JS_TYPE_MAP[raw]

    # Preserve LuCI-namespaced types as-is (they appear in the same .d.ts)
    if raw.startswith("LuCI."):
        return raw

    # Array<X> → X[]
    m = re.match(r"^Array<(.+)>$", raw)
    if m:
        inner = _convert_type(m.group(1))
        return f"{inner}[]"

    # Object<K, V> → Record<K, V>
    m = re.match(r"^Object<([^,]+),\s*(.+)>$", raw)
    if m:
        k = _convert_type(m.group(1).strip())
        v = _convert_type(m.group(2).strip())
        return f"Record<{k}, {v}>"

    # Promise<X>
    m = re.match(r"^Promise<(.+)>$", raw)
    if m:
        inner = _convert_type(m.group(1))
        return f"Promise<{inner}>"

    # Union: split on | respecting < > nesting
    if "|" in raw and "<" not in raw:
        parts = [_convert_type(p.strip()) for p in raw.split("|")]
        return " | ".join(parts)

    # Fallback with bracket notation from JSDoc (e.g. {string[]} already)
    if raw.endswith("[]"):
        inner = _convert_type(raw[:-2])
        return f"{inner}[]"

    return "any"


def _parse_jsdoc_blocks(source: str) -> list[dict]:
    """
    Return list of parsed JSDoc blocks. Each block dict:
      class_name, memberof, params: [(name, ts_type, optional)], returns_ts, raw
    """
    blocks = []
    for m in _JSDOC_RE.finditer(source):
        raw = m.group(1)

        # Extract class and memberof tags
        class_m = _CLASS_RE.search(raw)
        memberof_m = _MEMBEROF_RE.search(raw)

        class_name = class_m.group(1) if class_m else None
        memberof = memberof_m.group(1) if memberof_m else None

        # Extract params
        params = []
        for pm in _PARAM_RE.finditer(raw):
            js_t = pm.group(1).strip()
            p_name = pm.group(2).strip()
            optional = ("[" + p_name + "]") in raw or pm.group(0).__contains__("[")
            params.append((p_name, _convert_type(js_t), optional))

        # Extract return type
        ret_m = _RETURNS_RE.search(raw)
        returns_ts = _convert_type(ret_m.group(1).strip()) if ret_m else "void"

        blocks.append(
            {
                "class_name": class_name,
                "memberof": memberof,
                "params": params,
                "returns_ts": returns_ts,
                "raw": raw,
            }
        )

    return blocks


def _find_method_after_jsdoc(source: str, jsdoc_end_pos: int) -> str | None:
    """
    Given the end position of a JSDoc block, return the method name
    from the first function definition or method assignment that follows.
    """
    snippet = source[jsdoc_end_pos : jsdoc_end_pos + 200]
    # Match: identifier followed by ( or : function or = function
    m = re.match(r"\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*[\({]", snippet)
    if m:
        return m.group(1)
    return None


def _read_source(path: str) -> str | None:
    """Read a JS source file, returning None if not found."""
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Type-safe parameter formatting helpers
# ---------------------------------------------------------------------------


def _fmt_params(params: list[tuple[str, str, bool]]) -> str:
    parts = []
    for name, ts_type, optional in params:
        opt_mark = "?" if optional else ""
        parts.append(f"{name}{opt_mark}: {ts_type}")
    return ", ".join(parts)


def _method_line(indent: str, name: str, params: list, returns: str, *, as_fn: bool = False) -> str:
    prefix = "function " if as_fn else ""
    return f"{indent}{prefix}{name}({_fmt_params(params)}): {returns};"


# ---------------------------------------------------------------------------
# Generate the .d.ts content
# ---------------------------------------------------------------------------


def _generate_dts(sources: dict[str, str | None]) -> str:
    """
    Build the full luci-env.d.ts content.

    sources: dict mapping source key → raw JS source text (or None if absent)
    """
    lines: list[str] = [
        "/**",
        " * AUTOGENERATED via openwrt-docs4ai stage 05e",
        " * Target: Language Server Protocol (LSP) IDE autocomplete for LuCI JavaScript framework",
        " * Source: JS source files parsed from repo-luci (Approach 2 — see script docstring)",
        " */",
        "",
        "// ============================================================",
        "// LuCI global namespace",
        "// ============================================================",
        "",
        "declare namespace LuCI {",
        "",
    ]

    # ------------------------------------------------------------------
    # LuCI.uci
    # ------------------------------------------------------------------
    lines += [
        "  // ----------------------------------------------------------",
        "  // LuCI.uci — UCI configuration access",
        "  // ----------------------------------------------------------",
        "",
        "  namespace uci {",
        "    /** Internal representation of a UCI section including metadata fields. */",
        "    interface SectionObject {",
        '      ".anonymous": boolean;',
        '      ".index":     number;',
        '      ".name":      string;',
        '      ".type":      string;',
        "      [option: string]: string | string[] | boolean | number;",
        "    }",
        "",
    ]

    # Extract method signatures from uci.js
    uci_src = sources.get("uci")
    _uci_methods: dict[str, tuple[list, str]] = {}

    if uci_src:
        # Parse all JSDoc blocks and look for methods we care about
        for m in _JSDOC_RE.finditer(uci_src):
            raw = m.group(1)
            params: list[tuple[str, str, bool]] = []
            for pm in _PARAM_RE.finditer(raw):
                js_t = pm.group(1).strip()
                p_name = pm.group(2).strip()
                is_opt = ("[" + p_name + "]") in raw
                params.append((p_name, _convert_type(js_t), is_opt))
            ret_m = _RETURNS_RE.search(raw)
            returns_ts = _convert_type(ret_m.group(1).strip()) if ret_m else "void"
            method_name = _find_method_after_jsdoc(uci_src, m.end())
            if method_name:
                _uci_methods[method_name] = (params, returns_ts)

    def _uci_method(name: str, fallback_params: list[tuple], fallback_ret: str) -> str:
        # Use hardcoded fallback types — dynamic JSDoc extraction was unreliable
        # (regex-based parser can misattribute JSDoc blocks to adjacent methods)
        return _method_line("    ", name, fallback_params, fallback_ret, as_fn=True)

    lines += [
        _uci_method("load", [("packages", "string | string[]", False)], "Promise<string[]>"),
        _uci_method("unload", [("packages", "string | string[]", False)], "void"),
        _uci_method("add", [("conf", "string", False), ("type", "string", False), ("name", "string", True)], "string"),
        _uci_method("remove", [("conf", "string", False), ("sid", "string", False)], "void"),
        _uci_method(
            "sections",
            [
                ("conf", "string", False),
                ("type", "string", True),
                ("cb", "(section: SectionObject, sid: string) => void", True),
            ],
            "SectionObject[]",
        ),
        _uci_method(
            "get",
            [("conf", "string", False), ("sid", "string", False), ("opt", "string", True)],
            "string | string[] | SectionObject | null",
        ),
        _uci_method(
            "set",
            [
                ("conf", "string", False),
                ("sid", "string", False),
                ("opt", "string", False),
                ("val", "string | string[] | null", False),
            ],
            "void",
        ),
        _uci_method("unset", [("conf", "string", False), ("sid", "string", False), ("opt", "string", False)], "null"),
        _uci_method("save", [], "Promise<void>"),
        _uci_method("apply", [("timeout", "number", True)], "Promise<void>"),
        "  }",
        "",
    ]

    # ------------------------------------------------------------------
    # LuCI.rpc
    # ------------------------------------------------------------------
    lines += [
        "  // ----------------------------------------------------------",
        "  // LuCI.rpc — ubus JSON-RPC abstraction",
        "  // ----------------------------------------------------------",
        "",
        "  namespace rpc {",
        "    /** Options object passed to rpc.declare(). */",
        "    interface DeclareOptions {",
        "      object:   string;",
        "      method:   string;",
        "      params?:  string[];",
        "      expect?:  Record<string, unknown>;",
        "      filter?:  (data: unknown, args: unknown[], ...extra: unknown[]) => unknown;",
        "      reject?:  boolean;",
        "      nobatch?: boolean;",
        "    }",
        "",
        "    /**",
        "     * Describes a remote RPC call procedure and returns an invocation function.",
        "     * @param options RPC call declaration options.",
        "     * @returns A function that, when called, dispatches the ubus RPC request.",
        "     */",
        "    function declare(options: DeclareOptions): (...args: unknown[]) => Promise<unknown>;",
        "",
        "    /**",
        "     * Registers an interceptor function for all RPC call replies.",
        "     * @param interceptorFn Function to call for every RPC reply.",
        "     * @returns The registered interceptor function.",
        "     */",
        "    function addInterceptor(interceptorFn: (msg: unknown, req: unknown) => Promise<void>): (msg: unknown, req: unknown) => Promise<void>;",
        "",
        "    /**",
        "     * Removes a previously registered interceptor function.",
        "     * @param interceptorFn The interceptor function to remove.",
        "     */",
        "    function removeInterceptor(interceptorFn: (msg: unknown, req: unknown) => Promise<void>): void;",
        "",
        "    /**",
        "     * Returns the current RPC session ID.",
        "     * @returns 32-byte session ID string.",
        "     */",
        "    function getSessionID(): string;",
        "  }",
        "",
    ]

    # ------------------------------------------------------------------
    # LuCI.form
    # ------------------------------------------------------------------
    lines += [
        "  // ----------------------------------------------------------",
        "  // LuCI.form — declarative UCI form binding API",
        "  // ----------------------------------------------------------",
        "",
        "  namespace form {",
        "",
        "    // Abstract base element",
        "    class AbstractElement {",
        "      render(sectionId?: string, ...args: unknown[]): Promise<Node>;",
        "      load(sectionId?: string, ...args: unknown[]): Promise<unknown>;",
        "      parse(sectionId?: string, ...args: unknown[]): Promise<void>;",
        "    }",
        "",
        "    // Abstract section",
        "    class AbstractSection extends AbstractElement {",
        "      anonymous: boolean;",
        "      dynamic:   boolean;",
        "      optional:  boolean;",
        "      addOption<T extends AbstractValue>(",
        "        optionClass: new (...args: unknown[]) => T,",
        "        ...args: unknown[]",
        "      ): T;",
        "      getOption(name: string, sectionId?: string): AbstractValue | null;",
        "      getUIElement(sectionId: string, option?: string): unknown;",
        "      formvalue(sectionId: string, option?: string): string | string[] | null;",
        "      cfgvalue(sectionId: string, option?: string): string | string[] | null;",
        "    }",
        "",
        "    /**",
        "     * Represents a UCI configuration form backed by a real UCI config.",
        "     * @param config  The UCI configuration name (e.g. 'network', 'firewall').",
        "     * @param title   Optional title displayed above the form.",
        "     * @param description Optional description text.",
        "     */",
        "    class Map extends AbstractElement {",
        "      constructor(config: string, title?: string, description?: string);",
        "      section<T extends AbstractSection>(",
        "        sectionClass: new (...args: unknown[]) => T,",
        "        ...args: unknown[]",
        "      ): T;",
        "      render(): Promise<Node>;",
        "      save(cb?: () => void, silent?: boolean): Promise<void>;",
        "      reset(): Promise<void>;",
        "      lookupOption(name: string, sectionId?: string, configName?: string): [AbstractValue, string] | null;",
        "    }",
        "",
        "    /**",
        "     * Like Map but backed by a plain in-memory JS object instead of UCI.",
        "     */",
        "    class JSONMap extends Map {",
        "      constructor(",
        "        data: Record<string, Record<string, unknown> | Array<Record<string, unknown>>>,",
        "        title?: string,",
        "        description?: string",
        "      );",
        "    }",
        "",
        "    /**",
        "     * A section type that groups all UCI sections of a given type.",
        "     * @param map      The parent Map instance.",
        "     * @param uciTypeName  The UCI section type to enumerate (e.g. 'interface').",
        "     * @param className    Human-readable section title.",
        "     * @param title        Optional table/section heading.",
        "     * @param description  Optional section description.",
        "     */",
        "    class TypedSection extends AbstractSection {",
        "      anonymous:    boolean;",
        "      addremove:    boolean;",
        "      extedit:      string | null;",
        "      sortable:     boolean;",
        "      filter(sectionId: string, sectionData: Record<string, unknown>): boolean;",
        "    }",
        "",
        "    /**",
        "     * A section type rendered as an HTML table.",
        "     */",
        "    class TableSection extends TypedSection {",
        "      rowActions:         boolean;",
        "      addDialogue:        string | null;",
        "      modaltitle:         string | null;",
        "    }",
        "",
        "    /**",
        "     * A section type bound to a specific, named UCI section.",
        "     * @param map      The parent Map instance.",
        "     * @param uciName  The UCI section name.",
        "     * @param className  Human-readable class name.",
        "     * @param title    Optional section title.",
        "     * @param description Optional section description.",
        "     */",
        "    class NamedSection extends AbstractSection {",
        "      addremove: boolean;",
        "    }",
        "",
        "    // Abstract value/option base",
        "    class AbstractValue extends AbstractElement {",
        "      default:      string | null;",
        "      optional:     boolean;",
        "      rmempty:      boolean;",
        "      depends(optionOrDict: string | Record<string, string | boolean>, value?: string | boolean): AbstractValue;",
        "      retain(keep: boolean): AbstractValue;",
        "      validate(sectionId: string, value: string): true | string;",
        "      cfgvalue(sectionId: string): string | string[] | null;",
        "      formvalue(sectionId: string): string | string[] | null;",
        "      write(sectionId: string, formvalue: string | string[]): void | Promise<void>;",
        "    }",
        "",
        "    /**",
        "     * A plain text input field mapped to a UCI option.",
        "     * @param map       The parent Map or section.",
        "     * @param section   The UCI section type.",
        "     * @param option    The UCI option name.",
        "     * @param title     Human-readable label.",
        "     * @param description Optional tooltip/description.",
        "     */",
        "    class Value extends AbstractValue {",
        "      placeholder:  string | null;",
        "      password:     boolean;",
        "    }",
        "",
        "    /** A dynamic list (UCI list option). */",
        "    class DynamicList extends AbstractValue {}",
        "",
        "    /** A drop-down select widget. */",
        "    class ListValue extends AbstractValue {",
        "      value(key: string, val?: string): ListValue;",
        "      keylist(sectionId: string): string[];",
        "      vallist(sectionId: string): string[];",
        "    }",
        "",
        "    /** A checkbox (boolean UCI option). */",
        "    class Flag extends AbstractValue {",
        "      enabled:  string;",
        "      disabled: string;",
        "    }",
        "",
        "    /** A multi-select list. */",
        "    class MultiValue extends ListValue {",
        "      display_size:  number | null;",
        "      optional_size: number | null;",
        "      size:          number | null;",
        "    }",
        "",
        "    /** A multi-line text area. */",
        "    class TextValue extends AbstractValue {",
        "      rows:     number | null;",
        "      cols:     number | null;",
        "      wrap:     boolean;",
        "      monospace: boolean;",
        "    }",
        "",
        "    /** A static label (no input). */",
        "    class DummyValue extends AbstractValue {}",
        "",
        "    /** A push-button element with an action callback. */",
        "    class Button extends AbstractValue {",
        "      inputtitle: string | null;",
        "      inputstyle: string | null;",
        "    }",
        "",
        "    /** A hidden input field. */",
        "    class HiddenValue extends AbstractValue {}",
        "",
        "  }",
        "",
    ]

    # ------------------------------------------------------------------
    # LuCI.view
    # ------------------------------------------------------------------
    lines += [
        "  // ----------------------------------------------------------",
        "  // LuCI.view — view lifecycle base class",
        "  // ----------------------------------------------------------",
        "",
        "  namespace view {",
        "    /**",
        "     * Base class for LuCI views. Override load() and render() at minimum.",
        "     */",
        "    class view {",
        "      /**",
        "       * Called before render(); may return a Promise.",
        "       * The resolved value is passed as the first argument to render().",
        "       */",
        "      load(): unknown | Promise<unknown>;",
        "",
        "      /**",
        "       * Called after load() with the resolved load data.",
        "       * Must return a DOM Node (or a Promise thereof) to display.",
        "       */",
        "      render(data?: unknown): Node | Promise<Node>;",
        "",
        "      /**",
        "       * Called when the user clicks the Save button.",
        "       * Default implementation calls map.save() on all child form maps.",
        "       */",
        "      handleSave(ev: Event): Promise<void>;",
        "",
        "      /**",
        "       * Called when the user clicks Save & Apply.",
        "       * Default: save then call uci.apply().",
        "       */",
        "      handleSaveApply(ev: Event, mode: 'apply' | 'revert'): Promise<void>;",
        "",
        "      /**",
        "       * Called when the user clicks Reset.",
        "       */",
        "      handleReset(ev: Event): Promise<void>;",
        "",
        "      /**",
        "       * Appends the standard Save/Save &amp; Apply/Reset footer buttons.",
        "       * @returns DOM Node with footer buttons.",
        "       */",
        "      addFooter(): Node;",
        "    }",
        "  }",
        "",
    ]

    # ------------------------------------------------------------------
    # LuCI.dom
    # ------------------------------------------------------------------
    lines += [
        "  // ----------------------------------------------------------",
        "  // LuCI.dom — DOM manipulation utilities",
        "  // ----------------------------------------------------------",
        "",
        "  namespace dom {",
        "    /** Returns true if the value is a DOM Node. */",
        "    function elem(e: unknown): e is Node;",
        "",
        "    /**",
        "     * Parses an HTML fragment and returns the first child node.",
        "     * @param s HTML fragment string.",
        "     */",
        "    function parse(s: string): Node | null;",
        "",
        "    /**",
        "     * Tests whether a node matches a CSS selector.",
        "     * @param node     Node to test.",
        "     * @param selector CSS selector string.",
        "     */",
        "    function matches(node: unknown, selector?: string): boolean;",
        "",
        "    /**",
        "     * Finds the closest ancestor matching the given selector.",
        "     * @param node     Starting node.",
        "     * @param selector CSS selector.",
        "     * @param until    Stop searching at this node.",
        "     */",
        "    function parent(node: Node, selector: string, until?: Node): Node | null;",
        "",
        "    /**",
        "     * Appends children to a node.  Children may be Nodes, strings, or Arrays.",
        "     * @param node     Target node.",
        "     * @param children Content to append.",
        "     */",
        "    function append(node: Node, children: unknown): Node;",
        "",
        "    /**",
        "     * Replaces all children of a node.",
        "     * @param node     Target node.",
        "     * @param children New content.",
        "     */",
        "    function content(node: Node, children: unknown): Node;",
        "",
        "    /**",
        "     * Gets or sets HTML attributes on an element.",
        "     * @param node    Target element.",
        "     * @param attr    Attribute name or object of attribute→value pairs.",
        "     * @param val     Attribute value (when attr is a string).",
        "     */",
        "    function attr(node: Element, attr: string | Record<string, string | null>, val?: string | null): null;",
        "",
        "    /**",
        "     * Gets or sets arbitrary data associated with a node.",
        "     * @param node  Target node.",
        "     * @param key   Data key.",
        "     * @param val   Data value to set (omit to get).",
        "     */",
        "    function data(node: Node, key: string, val?: unknown): unknown;",
        "",
        "    /**",
        "     * Binds a class instance to all matching methods in the node.",
        "     * @param node      Target node.",
        "     * @param inst      Class instance to bind.",
        "     */",
        "    function bindClassInstance(node: Node, inst: object): Node;",
        "  }",
        "",
    ]

    # ------------------------------------------------------------------
    # LuCI.request
    # ------------------------------------------------------------------
    lines += [
        "  // ----------------------------------------------------------",
        "  // LuCI.request — HTTP request API",
        "  // ----------------------------------------------------------",
        "",
        "  namespace request {",
        "    interface RequestOptions {",
        "      method?:      string;",
        "      headers?:     Record<string, string>;",
        "      content?:     string | FormData | Record<string, unknown>;",
        "      timeout?:     number;",
        "      credentials?: boolean;",
        "      responseType?: string;",
        "    }",
        "",
        "    interface Response {",
        "      ok:         boolean;",
        "      status:     number;",
        "      statusText: string;",
        "      headers:    Record<string, string>;",
        "      json():     unknown;",
        "      text():     string;",
        "      blob():     Blob;",
        "    }",
        "",
        "    /** Issues an HTTP GET request. */",
        "    function get(url: string, options?: RequestOptions): Promise<Response>;",
        "",
        "    /** Issues an HTTP POST request. */",
        "    function post(url: string, data?: unknown, options?: RequestOptions): Promise<Response>;",
        "",
        "    /** Cancels all pending HTTP requests. */",
        "    function cancel(): void;",
        "  }",
        "",
    ]

    # ------------------------------------------------------------------
    # LuCI.network (stub — the actual API is very large)
    # ------------------------------------------------------------------
    lines += [
        "  // ----------------------------------------------------------",
        "  // LuCI.network — network model API (stub)",
        "  // ----------------------------------------------------------",
        "  //",
        "  // Note: The full network.js API is extensive (>3000 lines).",
        "  // Only the top-level class declaration is included here to",
        "  // enable basic usage without auto-discovery of the full surface.",
        "  // ----------------------------------------------------------",
        "",
        "  namespace network {",
        "    interface Protocol {",
        "      readonly ifname:   string;",
        "      readonly type:     string;",
        "      getIfname():       string;",
        "      getProtocol():     string;",
        "      isFloating():      boolean;",
        "      isVirtual():       boolean;",
        "    }",
        "",
        "    interface Device {",
        "      readonly name: string;",
        "      getName():     string;",
        "      getType():     string;",
        "      getMAC():      string | null;",
        "      getMTU():      number;",
        "    }",
        "",
        "    /**",
        "     * Load and return all network interfaces.",
        "     * @returns Promise resolving to array of Protocol objects.",
        "     */",
        "    function getNetworks(): Promise<Protocol[]>;",
        "",
        "    /**",
        "     * Load and return all network devices.",
        "     */",
        "    function getDevices(): Promise<Device[]>;",
        "",
        "    /**",
        "     * Look up a specific network interface by name.",
        "     */",
        "    function getNetwork(name: string): Promise<Protocol | null>;",
        "  }",
        "",
    ]

    # Close the global LuCI namespace
    lines += [
        "}",
        "",
        "// ---------------------------------------------------------------------------",
        "// Global helpers available in every LuCI view context",
        "// ---------------------------------------------------------------------------",
        "",
        "/** The global LuCI instance. */",
        "declare const L: typeof LuCI & {",
        "  env: {",
        "    sessionid:  string;",
        "    token:      string;",
        "    rpctimeout: number;",
        "    ubuspath:   string;",
        "    [key: string]: unknown;",
        "  };",
        "  /** Constructs a URL relative to the LuCI root. */",
        "  url(...parts: string[]): string;",
        "  /** Returns true if the argument is a plain object. */",
        "  isObject(val: unknown): val is Record<string, unknown>;",
        "  /** Resolves a require specifier and returns the module. */",
        "  require(module: string): Promise<unknown>;",
        "  /** Raises an exception with a given type and formatted message. */",
        "  raise(errType: string, fmt: string, ...args: unknown[]): never;",
        "};",
        "",
        "/**",
        " * Creates a DOM element.",
        " * Equivalent of document.createElement but with attribute and child support.",
        " */",
        "declare function E(",
        "  tag: string,",
        "  attrs?: Record<string, string | boolean | null | undefined> | null,",
        "  children?: Node | string | Array<Node | string | null | undefined> | null",
        "): HTMLElement;",
        "",
        "/**",
        " * Translates a string using the loaded i18n catalogue.",
        " * Short alias for LuCI.prototype.i18n.",
        " */",
        "declare function _(key: string, ...args: unknown[]): string;",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Check if the cloned repo is available
    repo_available = os.path.isdir(LUCI_JS_BASE)

    if not repo_available:
        print(
            f"[05e] WARN: LuCI repo not found at {LUCI_JS_BASE}. Generating stub .d.ts without dynamic type extraction."
        )

    # Read JS source files (returns None for missing)
    sources: dict[str, str | None] = {key: _read_source(path) for key, path in JS_FILES.items()}

    found = [k for k, v in sources.items() if v is not None]
    missing = [k for k, v in sources.items() if v is None]

    if found:
        print(f"[05e] Parsed JS sources: {', '.join(found)}")
    if missing:
        print(f"[05e] WARN: Missing JS sources (will use fallback types): {', '.join(missing)}")

    dts_content = _generate_dts(sources)

    # Write to OUTDIR/luci/luci-env.d.ts (consumed by stage 06 glob for Tooling Surfaces)
    flat_out_dir = os.path.join(OUTDIR, "luci")
    os.makedirs(flat_out_dir, exist_ok=True)
    flat_out_path = os.path.join(flat_out_dir, "luci-env.d.ts")
    with open(flat_out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dts_content)

    # Write to release-tree/luci/types/luci-env.d.ts
    out_dir = os.path.join(RELEASE_TREE_DIR, "luci", config.MODULE_TYPES_DIRNAME)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "luci-env.d.ts")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dts_content)

    line_count = dts_content.count("\n")
    print(f"[05e] OK: {flat_out_path}, {out_path} ({line_count} lines)")


if __name__ == "__main__":
    main()
