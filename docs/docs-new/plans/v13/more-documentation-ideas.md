read this list of ideas for enhancing the output of our project with new forms of documentation that different AI tools may use. some potentially good new ideas are using XML; building new example code files about specific programming functionality based on existing proven project code; using project tests to build good code examples because presumably the tests are well-written and rigorous; using "tree sitter" and "repomix"; using llms-mini; and generating a map of inter-component communication. write a tier list of the viable ideas and write a preliminary plan for implementation of your recommendations. note: while our project could benefit from some of these concepts internally for development, the goal of this plan is to improve the DELIVERABLE of the project (meaning the documentation for openwrt that helps ai agents program better for openwrt systems).







# Comprehensive Guide: Making AI Tools Master a Rare Programming Language

The answer you received is a strong foundation. What follows is a significantly expanded treatment — covering overlooked strategies, deeper implementation details, practical pitfalls, and the critical distinction between an AI that *references* your documentation and one that genuinely *reasons* in your language.

---

## Part 1: Reframing the Problem

Before choosing tools, understand that you're solving **three distinct problems**, not one:

### Problem 1: Syntax & Grammar Recognition
The AI needs to know what *valid code* looks like — tokenization, operator precedence, block delimiters, type syntax. Without this, the AI will constantly generate syntactically broken code, even if it "knows" the semantics.

### Problem 2: Semantic Understanding
The AI needs to know what constructs *mean* — what a `defer` keyword does, how ownership transfers, what the concurrency model guarantees. This is where your documentation payload lives.

### Problem 3: Idiomatic Pattern Generation
The AI needs to know what *good code* looks like — common patterns, standard library usage conventions, error handling idioms, project structure norms. Documentation alone rarely teaches this. You need **annotated examples**.

Most approaches in the original answer address Problem 2 only. A complete solution addresses all three.

---

## Part 2: Expanded Tier List with New Entries

### Tier S+: Annotated Example Corpus (Often Overlooked, Highest Impact)

**What it is:** A curated set of 50–200 code examples with inline comments explaining *why* each pattern is used, covering progressively complex scenarios.

**Why it outranks everything else:** LLMs learn patterns through demonstration more effectively than through specification. A formal grammar spec tells the AI that `fn` declares a function. Fifty examples of functions being declared, called, composed, and passed as arguments teach it to *write* functions fluently.

**Structure:**

```
examples/
├── 01_hello_world.rlang          # Minimal valid program
├── 02_variables_and_types.rlang  # Type declarations, inference, casting
├── 03_control_flow.rlang         # if/else, match, loops
├── 04_functions.rlang            # Declaration, closures, higher-order
├── 05_error_handling.rlang       # The idiomatic error pattern
├── 06_structs_and_traits.rlang   # Type composition
├── 07_concurrency.rlang          # Language-specific concurrency model
├── 08_ffi.rlang                  # Foreign function interface
├── 09_metaprogramming.rlang      # Macros, compile-time evaluation
├── 10_real_project/              # A small but complete project
│   ├── main.rlang
│   ├── config.rlang
│   ├── http_server.rlang
│   └── tests/
│       └── server_test.rlang
└── anti_patterns/
    ├── 01_common_mistakes.rlang  # What NOT to do, with corrections
    └── 02_gotchas.rlang          # Surprising behaviors
```

**Each file should follow this template:**

```
// EXAMPLE: Higher-order functions and closures
// CONTEXT: RareLang treats functions as first-class values.
// Closures capture variables by reference unless `copy` is specified.
// WHEN TO USE: Callback patterns, event handlers, collection transforms.

// Basic function declaration
fn add(a: Int, b: Int) -> Int {
    return a + b
}

// Function as parameter (note the `Fn` type constructor)
fn apply_twice(f: Fn(Int) -> Int, x: Int) -> Int {
    return f(f(x))
}

// Closure capturing outer variable
fn make_multiplier(factor: Int) -> Fn(Int) -> Int {
    // `factor` is captured by reference here
    return fn(x: Int) -> Int { x * factor }
}

// ANTI-PATTERN: Do NOT capture mutable state in concurrent closures.
// This compiles but causes a runtime data race:
// var counter = 0
// spawn { counter += 1 }  // ERROR-PRONE

// CORRECT: Use atomic operations or channels instead:
// let counter = Atomic(0)
// spawn { counter.increment() }
```

**Why this works:** When the AI encounters a user request like "write me an HTTP handler that transforms request bodies," it doesn't need to deduce behavior from a spec — it pattern-matches against your examples of closures + your example of the HTTP server + your error handling idiom, and composes them.

**Automation:** You can bootstrap this with a prompt:

```
Given the following language specification [attach spec], generate 
a progressive series of annotated code examples covering:
1. Every primitive type and operator
2. Every control flow construct
3. Every standard library module
4. Three complete mini-projects of increasing complexity

For each example:
- Include a header comment explaining WHAT, WHEN, and WHY
- Show the idiomatic way first, then show one common mistake with correction
- Use only features documented in the spec — never invent syntax
```

---

### Tier S: llms.txt (The Router) — Expanded

The original answer covers the basics. Here's what's missing:

**The full specification** (from `llmstxt.org`) actually defines four files:

| File | Purpose | Token Budget |
|------|---------|-------------|
| `llms.txt` | Concise overview + links to sections | < 2,000 tokens |
| `llms-full.txt` | Complete documentation in one file | Entire corpus |
| `llms-small.txt` | Ultra-compressed reference card | < 500 tokens |
| Per-page `*.md` | Individual topic files linked from `llms.txt` | Varies |

**The `llms-small.txt` is critically underused.** It should be a cheat sheet that fits in any context window:

```markdown
# RareLang Quick Reference

## Types
Int, Float, String, Bool, Byte, List<T>, Map<K,V>, Option<T>, Result<T,E>

## Variable Declaration
let x: Int = 5        // immutable
var y: Int = 5        // mutable
const Z: Int = 5      // compile-time constant

## Functions
fn name(param: Type) -> ReturnType { body }
fn name(param: Type) -> ReturnType = expression   // single-expression shorthand

## Control Flow
if cond { } else if cond { } else { }
match value { pattern => expr, _ => default }
for item in collection { }
while cond { }

## Error Handling
fn risky() -> Result<Int, Error> { ... }
let val = risky().unwrap()          // panics on error
let val = risky()?                  // propagates error
let val = risky().or_default(0)     // fallback

## Concurrency
spawn { async_work() }
let ch = Channel<Int>.new()
ch.send(42)
let val = ch.recv()

## Common Patterns
// Builder pattern: Config.new().set_port(8080).set_host("localhost").build()
// Resource cleanup: using resource = acquire() { ... }  // auto-cleanup
```

**Practical tip:** Many AI tools (Claude, ChatGPT) will use the `llms.txt` if it's served at your documentation website's root. But for local coding tools (Claude Code, Cursor, Cline), **the file needs to be in the project directory or explicitly referenced in the system prompt.**

---

### Tier A: Repomix — Expanded

**Critical details the original answer glosses over:**

**Configuration file (`repomix.config.json`):**

```json
{
  "output": {
    "filePath": "llms-full.txt",
    "style": "xml",
    "headerText": "This is the complete language specification and standard library reference for RareLang v2.4. When writing RareLang code, adhere strictly to the syntax and semantics described in this document. Do not invent functions or types not documented here.",
    "removeComments": false,
    "showLineNumbers": true,
    "topFilesLength": 20
  },
  "include": [
    "docs/**/*.md",
    "examples/**/*.rlang",
    "stdlib/**/*.rlang"
  ],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": [
      "**/*.pdf",
      "**/*.png",
      "**/node_modules/**",
      "**/CHANGELOG.md",
      "**/CONTRIBUTING.md"
    ]
  }
}
```

**The XML output structure** Repomix generates (understanding this helps you debug):

```xml
<repository>
  <repository_structure>
    docs/
      syntax.md
      types.md
      stdlib/
        io.md
        net.md
    examples/
      hello.rlang
  </repository_structure>

  <repository_files>
    <file path="docs/syntax.md">
      <content>
        # RareLang Syntax Reference
        ...
      </content>
    </file>
    <file path="examples/hello.rlang">
      <content>
        fn main() {
          print("Hello, world!")
        }
      </content>
    </file>
  </repository_files>
</repository>
```

**Why XML matters:** Benchmarks from Anthropic and community testing consistently show that LLMs parse hierarchical XML tags more reliably than deeply nested Markdown. The `<file path="...">` tags give the AI clear provenance — it knows *which document* a piece of information came from, reducing hallucination.

**Token budget reality check:**

| Documentation Size | Approximate Tokens | Fits In |
|---|---|---|
| 50 pages of docs | ~30k–50k tokens | Everything |
| 200 pages + stdlib | ~100k–200k tokens | Claude 3.5/Opus, Gemini 1.5 |
| 500+ pages | ~300k+ tokens | Only Gemini 2.5 Pro (1M context) |
| Complete language + ecosystem | 500k+ tokens | Must use RAG/MCP |

**If you're close to the limit**, prioritize inclusion order:
1. Syntax quick reference
2. Annotated examples
3. Type system documentation
4. Standard library reference
5. Error messages and their meanings
6. Advanced/niche features

---

### Tier A: Behavioral Priming Files — Massively Expanded

The original answer mentions `.cursorrules` and `.clinerules`. The landscape is broader and more nuanced:

| File | Tool | Location | Format |
|------|------|----------|--------|
| `.cursorrules` | Cursor (legacy) | Project root | Markdown |
| `.cursor/rules/*.mdc` | Cursor (current) | `.cursor/rules/` directory | MDC (Markdown with frontmatter) |
| `CLAUDE.md` | Claude Code | Project root (or `~/.claude/`) | Markdown |
| `.clinerules` | Cline | Project root | Markdown |
| `.github/copilot-instructions.md` | GitHub Copilot | `.github/` directory | Markdown |
| `.aider/conventions.md` | Aider | `.aider/` directory | Markdown |
| `.windsurfrules` | Windsurf | Project root | Markdown |
| `codex-instructions.md` or `AGENTS.md` | OpenAI Codex CLI | Project root | Markdown |

**Cursor's new MDC format** is particularly powerful because it supports conditional activation:

```markdown
---
description: RareLang syntax and idioms enforcement
globs: ["**/*.rlang", "**/*.rl"]
alwaysApply: false
---

# RareLang Development Rules

You are an expert RareLang developer. When working with .rlang files:

## Syntax Rules
1. All blocks use curly braces `{}`, never indentation-based
2. Semicolons are OPTIONAL and discouraged (the formatter removes them)
3. Type annotations are required for function parameters and return types
4. Type annotations are optional for local variables (inference is strong)

## Standard Library Usage
- For HTTP: use `std.net.http`, never suggest third-party libraries
- For JSON: use `std.encoding.json`, parsing returns `Result<Json, ParseError>`
- For file I/O: use `std.fs`, all operations are async by default

## Error Handling Convention
- ALWAYS use the `?` operator for error propagation in library code
- Use `match` on `Result` types in application entry points
- NEVER use `.unwrap()` except in tests and examples

## Memory Model
- RareLang uses automatic reference counting (ARC), not garbage collection
- Cyclic references must be broken with `weak` references
- The `using` block ensures deterministic cleanup

## What NOT To Do
- Do NOT generate Python-style list comprehensions (they don't exist)
- Do NOT assume null/nil exists (use `Option<T>` instead)
- Do NOT use inheritance (RareLang uses trait composition only)

## Documentation Reference
When uncertain about any syntax or standard library function, consult 
the language specification at `@docs/llms-full.txt` before generating code.
```

**`CLAUDE.md` for Claude Code** — this one is special because Claude Code reads it automatically and hierarchically:

```
project-root/
├── CLAUDE.md                    # Root-level instructions (always loaded)
├── docs/
│   └── CLAUDE.md                # Loaded when working in docs/
├── src/
│   ├── CLAUDE.md                # Loaded when working in src/
│   ├── parser/
│   │   └── CLAUDE.md            # Loaded when working in src/parser/
│   └── stdlib/
│       └── CLAUDE.md            # Loaded when working in src/stdlib/
└── tests/
    └── CLAUDE.md                # Loaded when working in tests/
```

Root `CLAUDE.md`:
```markdown
# Project: RareLang Compiler & Standard Library

This project is written in RareLang. The complete language specification 
is in `docs/llms-full.txt`. Read it before making changes.

## Build Commands
- Build: `rlang build`
- Test: `rlang test`  
- Test single: `rlang test tests/specific_test.rlang`
- Format: `rlang fmt`
- Lint: `rlang lint`

## Code Style
- 4-space indentation
- snake_case for functions and variables
- PascalCase for types and traits
- SCREAMING_CASE for constants
- Maximum line length: 100 characters

## Architecture
- `src/parser/` — Lexer and parser (produces AST)
- `src/typeck/` — Type checker  
- `src/codegen/` — Code generation (targets LLVM IR)
- `src/stdlib/` — Standard library implementations
- `tests/` — Integration tests
```

**Pro tip for Claude Code specifically:** You can also create a `~/.claude/CLAUDE.md` file for *global* instructions that apply to every project. This is where you'd put universal RareLang rules if you work on multiple RareLang projects.

---

### Tier A-: Tree-sitter Grammar (Syntax Recognition — Problem 1)

**This is entirely absent from the original answer and is critical.**

Tree-sitter is a parser generator that produces fast, incremental parsers. Many AI coding tools use Tree-sitter under the hood for syntax highlighting, code folding, and — crucially — **AST-aware code chunking for context windows**.

If your rare language has no Tree-sitter grammar:
- Repomix can't parse `.rlang` files into meaningful AST chunks
- AI tools will treat your code as plain text, losing structural understanding
- Features like "edit this function" become unreliable because the tool can't identify function boundaries

**Creating a Tree-sitter grammar:**

```javascript
// grammar.js for tree-sitter-rarelang
module.exports = grammar({
  name: 'rarelang',

  rules: {
    source_file: $ => repeat($._definition),

    _definition: $ => choice(
      $.function_definition,
      $.struct_definition,
      $.trait_definition,
      $.const_definition,
    ),

    function_definition: $ => seq(
      'fn',
      field('name', $.identifier),
      field('parameters', $.parameter_list),
      optional(seq('->', field('return_type', $._type))),
      field('body', $.block)
    ),

    parameter_list: $ => seq(
      '(',
      commaSep($.parameter),
      ')'
    ),

    parameter: $ => seq(
      field('name', $.identifier),
      ':',
      field('type', $._type)
    ),

    // ... continue for all syntax constructs
  }
});
```

**Effort:** High (days to weeks for a complete grammar). But the downstream benefits for *every* AI tool are enormous.

**Shortcut:** Ask an AI to draft the Tree-sitter grammar from your language spec, then iterate. This is one of the best uses of the documentation payload you're creating.

---

### Tier B+: Custom MCP Server (Dynamic Retrieval) — Expanded

The original answer correctly identifies MCP as high-friction but undersells a key use case: **when the AI needs to search your docs contextually rather than load them all upfront.**

**When MCP beats Repomix:**
- Documentation exceeds context window limits
- The language has 200+ standard library modules and the AI only needs 2–3 for any given task
- You want the AI to look up error messages dynamically
- You're building a persistent coding assistant that handles diverse tasks across the whole language

**Minimal MCP server for documentation (Python):**

```python
# rarelang_docs_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import os

app = Server("rarelang-docs")

# Load documentation index
DOCS_DIR = "./docs"
doc_index = {}
for root, dirs, files in os.walk(DOCS_DIR):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'r') as fh:
                content = fh.read()
            key = os.path.relpath(path, DOCS_DIR).replace('\\', '/').replace('.md', '')
            doc_index[key] = content

@app.tool()
async def search_docs(query: str) -> str:
    """Search RareLang documentation for a topic, function, or type name."""
    results = []
    query_lower = query.lower()
    for key, content in doc_index.items():
        if query_lower in content.lower():
            # Return first 2000 chars of matching docs
            snippet = content[:2000]
            results.append(f"## {key}\n{snippet}")
    if not results:
        return f"No documentation found for '{query}'. Available topics: {', '.join(doc_index.keys())}"
    return "\n\n---\n\n".join(results[:5])  # Top 5 matches

@app.tool()
async def get_doc_section(section: str) -> str:
    """Get a specific documentation section by path (e.g., 'stdlib/net', 'syntax/types')."""
    if section in doc_index:
        return doc_index[section]
    close_matches = [k for k in doc_index if section.lower() in k.lower()]
    if close_matches:
        return f"Section '{section}' not found. Did you mean: {', '.join(close_matches)}?"
    return f"Section '{section}' not found. Available: {', '.join(sorted(doc_index.keys()))}"

@app.tool()
async def lookup_error(error_code: str) -> str:
    """Look up a RareLang compiler error code (e.g., 'E0142') for explanation and fix."""
    errors_doc = doc_index.get('reference/errors', '')
    # Find the specific error
    lines = errors_doc.split('\n')
    capture = False
    result = []
    for line in lines:
        if error_code in line:
            capture = True
        elif capture and line.startswith('## '):
            break
        if capture:
            result.append(line)
    return '\n'.join(result) if result else f"Error code {error_code} not found in documentation."

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(app))
```

**Configuration for Claude Code (`~/.claude/claude_desktop_config.json`):**

```json
{
  "mcpServers": {
    "rarelang-docs": {
      "command": "python",
      "args": ["C:/path/to/rarelang_docs_server.py"],
      "env": {}
    }
  }
}
```

Now when Claude Code encounters a RareLang question, it can call `search_docs("async channel")` or `lookup_error("E0142")` as tools.

---

### Tier B: RAG Pipeline (For Massive Documentation)

**When you need it:** Your total documentation exceeds 500k tokens, or you have thousands of API reference pages.

**Simplest viable RAG setup:**

```python
# Using LlamaIndex (simplest RAG framework)
# pip install llama-index llama-index-embeddings-huggingface chromadb

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load docs
documents = SimpleDirectoryReader("./docs", recursive=True).load_data()

# Parse into semantic chunks (respects markdown headers)
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# Create searchable index
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
index = VectorStoreIndex(nodes, embed_model=embed_model)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("How do I create an async HTTP server in RareLang?")
print(response)
```

**RAG vs. full-context comparison:**

| Dimension | Full Context (Repomix) | RAG |
|---|---|---|
| Accuracy | Higher (AI sees everything) | Lower (retrieval may miss relevant chunks) |
| Token cost per query | High (entire doc loaded every time) | Low (only relevant chunks loaded) |
| Setup complexity | Minutes | Hours to days |
| Maintenance | Regenerate on doc change | Re-index on doc change |
| Best for | < 200k tokens of docs | > 500k tokens of docs |
| Failure mode | Context window exceeded | Wrong chunks retrieved → hallucination |

---

### Tier B-: TextMate / VS Code Grammar (Syntax Highlighting)

Less impactful for AI than Tree-sitter, but if your language already has a VS Code extension with a TextMate grammar (`.tmLanguage.json`), some AI tools can leverage it for basic syntax awareness.

---

### Tier C: Fine-tuning a Model

**When it makes sense:** Almost never for a single developer. Fine-tuning requires:
- Thousands of high-quality (prompt, completion) pairs
- Significant compute budget ($50–$500+ per training run)
- Ongoing maintenance as the language evolves

**When it *does* make sense:**
- You're the language creator and want to offer an AI assistant as a product
- You have a large corpus of existing RareLang code (open-source projects, etc.)
- Context-window approaches consistently fail because the language is too alien

**If you do pursue it**, the training data format matters:

```jsonl
{"messages": [{"role": "system", "content": "You are a RareLang expert."}, {"role": "user", "content": "Write a function that reads a file and returns its lines as a list of strings."}, {"role": "assistant", "content": "```rarelang\nfn read_lines(path: String) -> Result<List<String>, IoError> {\n    let file = std.fs.open(path)?\n    let content = file.read_to_string()?\n    return Ok(content.split(\"\\n\"))\n}\n```"}]}
{"messages": [{"role": "system", "content": "You are a RareLang expert."}, {"role": "user", "content": "What's wrong with this code?\n\nvar x = 5\nif x = 10 { print(x) }"}, {"role": "assistant", "content": "The issue is on line 2: `x = 10` is an assignment, not a comparison. RareLang uses `==` for equality comparison. The correct code is:\n\n```rarelang\nvar x = 5\nif x == 10 { print(x) }\n```\n\nRareLang's compiler would catch this with error E0087: 'assignment in condition expression'. Unlike C, RareLang does not allow assignments as expressions."}]}
```

---

## Part 3: Missing from the Original — Critical Additions

### Error Message Documentation

**This is almost always overlooked and dramatically improves AI performance.** If your language has a compiler, document every error message with:
- The error code/text
- What causes it
- A minimal reproduction
- The fix

```markdown
## E0042: Type mismatch in assignment

**Message:** `cannot assign value of type '{actual}' to variable of type '{expected}'`

**Cause:** Attempting to assign a value to a variable when the types don't match 
and no implicit conversion exists.

**Example:**
```rarelang
let x: Int = "hello"  // E0042: cannot assign value of type 'String' to variable of type 'Int'
```

**Fix:** Either change the variable type, convert the value, or use a compatible type:
```rarelang
let x: Int = "42".parse_int()?     // Explicit conversion
let x: String = "hello"             // Match the type
let x = "hello"                     // Let type inference handle it
```
```

When an AI sees an error message in terminal output, it can match it against this documentation and provide the correct fix instead of guessing.

### Build System & Toolchain Documentation

AI coding assistants don't just write code — they need to know how to:
- Initialize a project (`rlang init`)
- Add dependencies (`rlang add package_name`)
- Build (`rlang build`)
- Run tests (`rlang test`)
- Format code (`rlang fmt`)
- Understand the project manifest file (like `Cargo.toml` or `package.json`)

Include a dedicated section:

```markdown
## Project Structure

A standard RareLang project:
```
my_project/
├── project.toml          # Project manifest
├── src/
│   ├── main.rlang        # Entry point (for applications)
│   └── lib.rlang         # Entry point (for libraries)
├── tests/
│   └── test_main.rlang
└── vendor/               # Downloaded dependencies
```

## project.toml Format
```toml
[project]
name = "my_project"
version = "0.1.0"
entry = "src/main.rlang"

[dependencies]
http_framework = "2.1.0"
json_parser = { git = "https://github.com/example/json_parser" }

[dev-dependencies]
test_utils = "1.0.0"
```
```

---

## Part 4: The Integrated Workflow (Putting It All Together)

Here's the **recommended complete setup**, ordered by implementation priority:

### Phase 1: Foundation (Day 1)

1. **Create the annotated example corpus** (50+ examples)
2. **Write `llms-small.txt`** (the cheat sheet — under 500 tokens)
3. **Write `llms.txt`** (the router — under 2000 tokens)

### Phase 2: Context Payload (Day 2)

4. **Install and configure Repomix**
5. **Generate `llms-full.txt`** from your docs + examples
6. **Verify token count** — `repomix` reports this automatically
7. If under 200k tokens: you're done with the payload
8. If over 200k tokens: prioritize sections, create a trimmed version

### Phase 3: Tool Integration (Day 3)

9. **Create behavioral priming files** for every tool you use:
   - `CLAUDE.md` for Claude Code
   - `.cursor/rules/rarelang.mdc` for Cursor
   - `.github/copilot-instructions.md` for Copilot
   - Etc.

10. **Each priming file should reference the payload:**

```markdown
Before writing or modifying any .rlang file, load and internalize the 
language specification at `docs/llms-full.txt`.
```

### Phase 4: Validation (Day 4)

11. **Test with progressively harder prompts:**
    - "Write a hello world in RareLang" (should use correct syntax)
    - "Write an HTTP server that serves JSON" (should use correct stdlib)
    - "Refactor this code to handle errors properly" (should use language idioms)
    - "This code throws E0042 — fix it" (should know the error)

12. **Iterate on your documentation based on failures.** Every time the AI gets something wrong, add:
    - An example covering that case
    - A rule in the priming file
    - A clarification in the spec

### Phase 5: Automation (Week 2)

13. **Set up GitHub Actions** to regenerate `llms-full.txt` on documentation changes
14. **Optionally build an MCP server** if you find the context window is a bottleneck
15. **Optionally create a Tree-sitter grammar** if you want AST-aware tooling

---

## Part 5: Dependency Graph & Decision Matrix

```
                    ┌─────────────────────┐
                    │  Your Documentation  │
                    │  (Markdown/HTML/PDF) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Conversion to MD   │
                    │  (if not already)    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼─────────┐ ┌───▼───┐ ┌──────────▼──────────┐
    │  llms.txt (router) │ │ Quick │ │  Annotated Examples  │
    │  llms-small.txt    │ │  Ref  │ │  (50-200 files)      │
    └─────────┬─────────┘ └───┬───┘ └──────────┬──────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Repomix        │
                    │  (Pack everything)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   llms-full.txt     │
                    │   (XML payload)     │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
┌────────▼────────┐  ┌────────▼────────┐  ┌─────────▼────────┐
│   CLAUDE.md     │  │  .cursorrules   │  │  copilot-        │
│   (Claude Code) │  │  (Cursor)       │  │  instructions.md │
└─────────────────┘  └─────────────────┘  └──────────────────┘
```

### Mutual Exclusions & Compatibility:

| Approach A | Approach B | Relationship |
|---|---|---|
| Repomix (full context) | MCP Server | **Choose one.** Both simultaneously wastes tokens. Use Repomix if docs fit in context, MCP if they don't. |
| Repomix (full context) | RAG Pipeline | **Choose one.** Same rationale as above. |
| MCP Server | RAG Pipeline | **Complementary.** MCP is the interface; RAG can be the retrieval backend inside the MCP server. |
| llms.txt | Repomix | **Complementary.** llms.txt is the index; Repomix generates the payload. |
| Priming files | Everything else | **Always use alongside** any other approach. They're the behavioral guardrails. |
| Tree-sitter grammar | Everything else | **Independent.** Improves all other approaches but is not required by any. |
| Examples corpus | Everything else | **Always include.** Most impactful single investment. |

---

## Part 6: GitHub Projects & Tools Reference

| Tool | GitHub | Purpose | Stars |
|---|---|---|---|
| Repomix | `yamadashy/repomix` | Pack repos into AI-readable files | 10k+ |
| llms.txt Generator | `demodrive-ai/llms-txt-action` | Auto-generate llms.txt from docs sites | ~200 |
| llms-txt (spec) | `jxnl/llmstxt` | Python tools for llms.txt | ~300 |
| Tree-sitter | `tree-sitter/tree-sitter` | Parser generator framework | 18k+ |
| MCP SDK (Python) | `modelcontextprotocol/python-sdk` | Build MCP servers | 5k+ |
| MCP SDK (TypeScript) | `modelcontextprotocol/typescript-sdk` | Build MCP servers (TS) | 3k+ |
| Cursor Directory | `pontusab/cursor.directory` | Community .cursorrules collection | 3k+ |
| Awesome CursorRules | `PatrickJS/awesome-cursorrules` | Curated rules examples | 5k+ |
| LlamaIndex | `run-llama/llama_index` | RAG framework | 37k+ |
| Docling | `DS4SD/docling` | Convert PDF/DOCX docs to Markdown | 15k+ |

---

## Part 7: If Your Documentation Is in PDF/HTML/Non-Markdown

You need a conversion step first:

**PDF → Markdown:**
```bash
# Using Docling (IBM Research)
pip install docling
docling convert --from pdf --to md ./docs/spec.pdf --output ./docs/md/

# Or using Marker (higher quality for complex layouts)
pip install marker-pdf
marker_single ./docs/spec.pdf ./docs/md/
```

**HTML → Markdown:**
```bash
# Using Pandoc
pandoc -f html -t markdown ./docs/reference.html -o ./docs/reference.md

# Or using Trafilatura (better for web scraping)
pip install trafilatura
trafilatura -u https://rarelang.org/docs --output-format markdown > docs/reference.md
```

**After conversion**, audit the output. Automated conversion often mangles:
- Code blocks (losing language-specific syntax)
- Tables (especially complex ones)
- Cross-references and links
- Mathematical notation

---

## Part 8: The Meta-Prompt (Generate Everything with AI)

Use this prompt to bootstrap the entire documentation suite from your raw docs:

```
I have the complete documentation for a programming language called 
[RareLang]. I'm attaching the full specification below.

Please generate the following files:

1. **llms-small.txt**: A cheat sheet under 500 tokens covering all 
   syntax, types, operators, control flow, and the most important 
   10 standard library functions.

2. **llms.txt**: A routing document under 2000 tokens that describes 
   what each section of the documentation covers and when an AI should 
   consult it.

3. **CLAUDE.md**: A behavioral priming file for Claude Code that 
   includes build commands, code style rules, common mistakes to avoid, 
   and a reference to the full documentation.

4. **examples/**: A series of 20 annotated code examples progressing 
   from hello world to a complete mini-project. Each example should 
   include header comments explaining WHAT the example demonstrates, 
   WHEN you'd use this pattern, and any pitfalls to avoid.

5. **error_reference.md**: Documentation for the 20 most likely 
   compiler/runtime errors a new user would encounter, with examples 
   and fixes.

Rules:
- Use ONLY syntax and features documented in the attached specification.
- If something is ambiguous in the spec, flag it with [AMBIGUOUS] and 
  provide your best interpretation.
- Do NOT invent standard library functions.
- Include anti-patterns alongside correct patterns.

[ATTACH YOUR DOCUMENTATION HERE]
```

---

## Summary Recommendation

For a single developer wanting AI tools to master a rare language:

1. **Start with examples** (Tier S+) — highest ROI, lowest tooling dependency
2. **Pack everything with Repomix** (Tier A) — simple, works today
3. **Write priming files** (Tier A) — 30 minutes, permanent benefit
4. **Add `llms.txt`** (Tier S) — future-proofing, trivial effort
5. **Skip MCP/RAG/fine-tuning** unless your docs exceed 200k tokens
6. **Consider Tree-sitter** only if you'll be doing heavy development long-term

The combination of a well-structured example corpus + Repomix payload + behavioral priming file will get you 90% of the way to an AI that can competently write your rare language. The remaining 10% comes from iterative refinement as you discover the AI's failure modes and address them with additional examples and rules.






# The Annotated Example Corpus: Prior Art, Standards, and Auto-Generation

## Is It Novel?

No. The approach is a convergence of several well-established practices, each with its own lineage. What's somewhat newer is the specific framing of "curated examples as the primary AI context artifact," but even that has been formalized by multiple projects in the last 18 months. Here's the genealogy:

---

## Established Prior Art

### 1. The "By Example" Documentation Pattern

This predates AI tooling entirely and has been proven across dozens of languages:

| Project | Language | URL | Format |
|---|---|---|---|
| Go by Example | Go | gobyexample.com | Progressive annotated examples |
| Rust by Example | Rust | doc.rust-lang.org/rust-by-example | Progressive annotated examples |
| Haskell by Example | Haskell | lotz84.github.io/haskellbyexample | Progressive annotated examples |
| Zig by Example | Zig | zig.guide | Progressive annotated examples |
| Nim by Example | Nim | nim-by-example.github.io | Progressive annotated examples |
| Learn X in Y Minutes | ~200 languages | learnxinyminutes.com | Single-file cheat sheets |

**"Learn X in Y Minutes"** is particularly relevant — it's essentially `llms-small.txt` before that concept existed. Each file is a single heavily-commented source file that teaches an entire language through annotated code. These files are already being used as AI context by developers who paste them into prompts.

**Key insight:** These projects proved that progressive annotated examples are the most efficient format for both humans and machines to acquire a language. The AI documentation community didn't invent this — they inherited it.

### 2. Executable Documentation (Doctests)

Several languages have built the "examples as documentation" idea directly into their toolchains, with the critical addition that examples are **tested against the compiler**:

```rust
// Rust: doc comments with tested examples
/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// let result = my_crate::add(2, 3);
/// assert_eq!(result, 5);
/// ```
///
/// # Panics
///
/// Panics if the result overflows:
///
/// ```should_panic
/// my_crate::add(i64::MAX, 1);
/// ```
pub fn add(a: i64, b: i64) -> i64 {
    a.checked_add(b).expect("overflow")
}
```

```python
# Python: doctest module
def factorial(n):
    """Return the factorial of n.

    >>> factorial(5)
    120
    >>> factorial(0)
    1
    >>> factorial(-1)
    Traceback (most recent call last):
        ...
    ValueError: n must be >= 0
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

```elixir
# Elixir: doctest in ExUnit
defmodule MyModule do
  @doc """
  Calculates the square of a number.

  ## Examples

      iex> MyModule.square(3)
      9

      iex> MyModule.square(-4)
      16
  """
  def square(x), do: x * x
end
```

**Why this matters for your use case:** If your rare language has a test runner, you should make your AI-targeted examples executable tests. This gives you a CI guarantee that your example corpus isn't lying to the AI.

### 3. The Diataxis Documentation Framework

Diataxis (diataxis.fr) is the most widely adopted documentation architecture standard. It separates documentation into four quadrants:

```
                    PRACTICAL                    THEORETICAL
                ┌─────────────────────┬─────────────────────┐
   LEARNING     │     TUTORIALS       │    EXPLANATION       │
   (acquiring)  │  (learning-oriented)│  (understanding-     │
                │                     │   oriented)          │
                ├─────────────────────┼─────────────────────┤
   WORKING      │    HOW-TO GUIDES    │    REFERENCE         │
   (applying)   │  (task-oriented)    │  (information-       │
                │                     │   oriented)          │
                └─────────────────────┴─────────────────────┘
```

**Your annotated example corpus maps to Tutorials + How-to Guides.** The raw API reference maps to Reference. The language design documentation maps to Explanation.

**The AI documentation insight** that goes beyond Diataxis: For AI consumption, you should weight the quadrants differently than for human consumption:

| Quadrant | Human Priority | AI Priority | Reason |
|---|---|---|---|
| Tutorials (examples) | Medium | **Highest** | Pattern matching is the AI's strongest capability |
| How-to Guides | High | High | Task-oriented, directly applicable |
| Reference | Medium | Medium | AI can parse but needs examples to apply |
| Explanation | High for beginners | **Low** | AI doesn't need to "understand" design philosophy |

---

## Projects Specifically Building AI-Targeted Example Documentation

### 1. Pieces (pieces.app)

Pieces is a snippet management platform that has evolved into an AI context engine. It:
- Captures code snippets with metadata (language, tags, descriptions, related links)
- Maintains a personal knowledge base of examples
- Feeds relevant snippets into AI coding assistants as context
- Has integrations with VS Code, JetBrains, Cursor

**Relevance:** Pieces essentially implements the "example corpus as AI context" pattern as a product. Their architecture validates the approach.

### 2. Continue.dev (@codebase and @docs context)

Continue is an open-source AI coding assistant that explicitly supports:
- `@docs` — indexing external documentation (including custom language docs)
- `@codebase` — using your existing code as example context
- Custom context providers — you can write plugins that serve examples to the AI

```typescript
// continue config.json — adding custom documentation
{
  "docs": [
    {
      "title": "RareLang Reference",
      "startUrl": "https://rarelang.org/docs",
      "faviconUrl": "https://rarelang.org/favicon.ico"
    }
  ]
}
```

### 3. Sourcegraph Cody's Code Context

Cody uses a code graph to understand repositories. When you ask it a question, it retrieves relevant code examples from your codebase. The insight: **your existing codebase IS the example corpus** — Cody just indexes it automatically.

### 4. Aider's Repository Map

Aider (github.com/paul-gauthier/aider) generates a "repository map" — a condensed representation of your entire codebase showing classes, functions, and their signatures. This is essentially auto-generated reference documentation from source code.

```
aider --map-tokens 2048
```

It uses Tree-sitter to parse the AST and extract the most important structural information, then feeds it as context to the LLM.

### 5. Sweep AI / OpenHands / SWE-Agent

These are autonomous coding agents that demonstrate a pattern relevant to your question: they build internal representations of codebases by reading source files, extracting patterns, and maintaining a working memory of examples they've seen. Their architecture documents how agents consume code-as-documentation.

---

## Auto-Generation Pipelines

This is the core of your question. Here are concrete pipelines for generating an AI-optimized example corpus from different source materials:

### Pipeline 1: From API Headers/Signatures → Example Corpus

**Source:** Header files (`.h`, `.d.ts`, `.pyi`), interface definitions, API surface documentation

**Tool chain:**

```
Headers/Interfaces → Parse signatures → Generate examples per function → Annotate → Validate
```

**Automated prompt for generating examples from headers:**

```
I have the following API header file for [RareLang]'s standard library 
network module. For each public function and type:

1. Generate a minimal working example showing basic usage
2. Generate a second example showing composition with other functions 
   in this module
3. Generate one anti-pattern (common misuse) with correction
4. Add a header comment with: FUNCTION, PURPOSE, WHEN TO USE, GOTCHAS

Format each example as a standalone .rlang file that could be compiled 
and run independently (include necessary imports and a main function).

Use ONLY the functions and types visible in this header. Do NOT invent 
additional API surface.

---
[PASTE HEADER FILE]
```

**More sophisticated approach — using AST extraction:**

```python
# extract_api_surface.py
# Parse source/header files and generate an API skeleton for example generation

import tree_sitter_languages  # pip install tree_sitter_languages
# For a rare language without a tree-sitter grammar, fall back to regex

import re
import json

def extract_functions_from_source(source_code: str, lang_name: str) -> list[dict]:
    """
    Extract function signatures from source code.
    Adjust regex patterns for your language's syntax.
    """
    # Example pattern for a language with fn name(params) -> RetType syntax
    fn_pattern = re.compile(
        r'(?:pub\s+)?fn\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^\s{]+))?\s*\{',
        re.MULTILINE
    )
    
    functions = []
    for match in fn_pattern.finditer(source_code):
        name = match.group(1)
        params_raw = match.group(2).strip()
        return_type = match.group(3) or 'void'
        
        params = []
        if params_raw:
            for param in params_raw.split(','):
                param = param.strip()
                if ':' in param:
                    pname, ptype = param.split(':', 1)
                    params.append({
                        'name': pname.strip(),
                        'type': ptype.strip()
                    })
        
        functions.append({
            'name': name,
            'params': params,
            'return_type': return_type,
            'signature': match.group(0).rstrip('{').strip()
        })
    
    return functions

def extract_types_from_source(source_code: str) -> list[dict]:
    """Extract struct/type definitions."""
    struct_pattern = re.compile(
        r'(?:pub\s+)?struct\s+(\w+)(?:<([^>]+)>)?\s*\{([^}]*)\}',
        re.MULTILINE | re.DOTALL
    )
    
    types = []
    for match in struct_pattern.finditer(source_code):
        name = match.group(1)
        generics = match.group(2)
        body = match.group(3)
        
        fields = []
        for line in body.strip().split('\n'):
            line = line.strip().rstrip(',')
            if ':' in line:
                fname, ftype = line.split(':', 1)
                fields.append({
                    'name': fname.strip(),
                    'type': ftype.strip()
                })
        
        types.append({
            'name': name,
            'generics': generics,
            'fields': fields
        })
    
    return types

def generate_api_manifest(source_dir: str) -> dict:
    """Walk source tree and build complete API manifest."""
    import os
    manifest = {'modules': {}}
    
    for root, dirs, files in os.walk(source_dir):
        for f in files:
            if f.endswith(('.rlang', '.rl', '.h')):
                path = os.path.join(root, f)
                with open(path, 'r') as fh:
                    source = fh.read()
                
                module_name = os.path.relpath(path, source_dir)
                manifest['modules'][module_name] = {
                    'functions': extract_functions_from_source(source, 'rarelang'),
                    'types': extract_types_from_source(source)
                }
    
    return manifest

if __name__ == '__main__':
    import sys
    manifest = generate_api_manifest(sys.argv[1])
    print(json.dumps(manifest, indent=2))
```

Then feed the manifest to an LLM:

```python
# generate_examples.py
import json
import anthropic  # or openai, etc.

client = anthropic.Anthropic()

with open('api_manifest.json') as f:
    manifest = json.load(f)

for module_name, module_data in manifest['modules'].items():
    prompt = f"""Given this API surface for the module `{module_name}` 
in RareLang:

Functions:
{json.dumps(module_data['functions'], indent=2)}

Types:
{json.dumps(module_data['types'], indent=2)}

Generate a comprehensive annotated example file that demonstrates 
every function and type in this module. The file should:

1. Start with a module-level comment explaining what this module does
2. Show each function being called with realistic arguments
3. Show types being constructed and used
4. Demonstrate error handling for functions that can fail
5. Include one "putting it all together" section at the end
6. Mark any anti-patterns with // ANTI-PATTERN comments

Output only the .rlang source file contents."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    example_code = response.content[0].text
    
    output_path = f"examples/stdlib/{module_name.replace('/', '_')}_examples.rlang"
    with open(output_path, 'w') as f:
        f.write(example_code)
    
    print(f"Generated: {output_path}")
```

### Pipeline 2: From Test Suites → Example Corpus

**This is the highest-quality auto-generation path** because tests are already verified correct code.

```python
# tests_to_examples.py
"""
Extract test cases from a test suite and convert them into 
annotated examples suitable for AI consumption.
"""

import re
import os

def extract_tests(test_file: str) -> list[dict]:
    """
    Extract test functions from a test file.
    Adjust patterns for your language's test framework.
    """
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Pattern for test functions (adjust for your language)
    # e.g., #[test] fn test_name() { ... }
    # or: test "description" { ... }
    test_pattern = re.compile(
        r'(?:#\[test\]\s*)?(?:test\s+"([^"]+)"\s*|fn\s+(test_\w+)\s*\(\)\s*)\{',
        re.MULTILINE
    )
    
    tests = []
    for match in test_pattern.finditer(content):
        name = match.group(1) or match.group(2)
        # Find the matching closing brace (naive — a real parser would be better)
        start = match.end()
        depth = 1
        pos = start
        while pos < len(content) and depth > 0:
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
            pos += 1
        
        body = content[start:pos-1].strip()
        tests.append({
            'name': name,
            'body': body,
            'source_file': test_file
        })
    
    return tests

def convert_test_to_example(test: dict) -> str:
    """Convert a test case into an annotated example."""
    # Strip test assertions and convert to demonstrative code
    body = test['body']
    
    # Replace assert_eq!(a, b) with comments showing expected values
    body = re.sub(
        r'assert_eq!\((.+?),\s*(.+?)\)',
        r'let result = \1  // Expected: \2',
        body
    )
    
    # Replace assert!(cond) with comments
    body = re.sub(
        r'assert!\((.+?)\)',
        r'// Verify: \1',
        body
    )
    
    return f"""// EXAMPLE: {test['name']}
// SOURCE: Extracted from {test['source_file']}
// This example demonstrates the behavior verified by the test suite.

fn main() {{
{textwrap.indent(body, '    ')}
}}
"""

def process_test_directory(test_dir: str, output_dir: str):
    """Process all test files and generate example corpus."""
    os.makedirs(output_dir, exist_ok=True)
    
    for root, dirs, files in os.walk(test_dir):
        for f in files:
            if f.endswith(('.rlang', '.rl')):
                path = os.path.join(root, f)
                tests = extract_tests(path)
                
                for i, test in enumerate(tests):
                    example = convert_test_to_example(test)
                    out_name = f"{f.replace('.rlang', '')}_{i:02d}_{test['name']}.rlang"
                    out_path = os.path.join(output_dir, out_name)
                    
                    with open(out_path, 'w') as fh:
                        fh.write(example)
                    
                    print(f"Generated: {out_path}")
```

**Better approach — use AI to transform tests into pedagogical examples:**

```
I have the following test file from [RareLang]'s test suite. Each test 
verifies a specific behavior of the language or standard library.

Transform these tests into annotated learning examples:

1. Remove test framework boilerplate (assertions, test harness setup)
2. Add a header comment explaining what concept this demonstrates
3. Replace assertions with print statements showing expected output
4. Add inline comments explaining non-obvious behavior
5. Group related tests into a single example file with sections
6. Add a "Common Mistakes" section if any tests are regression tests 
   for bugs

Preserve the exact API calls and patterns — these are verified correct.

---
[PASTE TEST FILE]
```

### Pipeline 3: From Real Applications → Decomposed Examples

**Source:** Complete applications written in your rare language

This is the most valuable but most labor-intensive pipeline. The idea is to decompose a working application into teachable components.

```
Real Application → Identify patterns → Extract minimal reproductions → Annotate → Organize by concept
```

**Automated prompt:**

```
I have a complete [RareLang] application (an HTTP API server). 
I want to decompose it into a series of focused examples that 
teach the patterns used in this application.

For each distinct pattern or concept used in this code:

1. Extract the MINIMAL code that demonstrates just that pattern
2. Remove all complexity not related to the pattern being taught
3. Add imports and a main() function so the example compiles standalone
4. Write a header comment: PATTERN NAME, WHAT IT DOES, WHEN TO USE IT
5. If the pattern interacts with another pattern (e.g., error handling 
   inside concurrency), create a separate "composition" example

Organize the output as a numbered series:
01_basic_server.rlang
02_routing.rlang
03_middleware.rlang
04_database_connection.rlang
05_error_handling.rlang
06_authentication.rlang
07_testing.rlang
08_full_integration.rlang

---
[PASTE APPLICATION CODE]
```

### Pipeline 4: From API Documentation (Markdown/HTML) → Examples

**For when your documentation describes functions but doesn't include code:**

```python
# doc_to_examples.py
"""
Parse API reference documentation and generate example code.
"""

import re
import json

def parse_api_docs(doc_content: str) -> list[dict]:
    """
    Parse structured API documentation into function records.
    Handles common documentation formats.
    """
    entries = []
    
    # Pattern: ## function_name\n\nDescription\n\n**Parameters:**\n- ...
    sections = re.split(r'^## ', doc_content, flags=re.MULTILINE)
    
    for section in sections[1:]:  # Skip content before first ##
        lines = section.strip().split('\n')
        name = lines[0].strip()
        
        description = ''
        params = []
        returns = ''
        
        current_section = 'description'
        for line in lines[1:]:
            if '**Parameters' in line or '**Args' in line:
                current_section = 'params'
            elif '**Returns' in line:
                current_section = 'returns'
            elif '**Example' in line:
                current_section = 'example'
            elif current_section == 'description':
                description += line + '\n'
            elif current_section == 'params' and line.strip().startswith('-'):
                params.append(line.strip().lstrip('- '))
            elif current_section == 'returns':
                returns += line + '\n'
        
        entries.append({
            'name': name,
            'description': description.strip(),
            'params': params,
            'returns': returns.strip()
        })
    
    return entries

def generate_example_prompt(entries: list[dict], module_name: str) -> str:
    """Generate a prompt for AI example generation from parsed API docs."""
    entries_formatted = json.dumps(entries, indent=2)
    
    return f"""Given these API entries for the `{module_name}` module in RareLang:

{entries_formatted}

Generate a single example file that demonstrates every function listed.
For each function:
- Show a realistic usage (not just `foo(1, 2)` — use meaningful variable names and realistic values)
- If the function can fail, show both success and error handling
- Add a comment explaining when you'd use this function vs alternatives

End with a "Real World Example" section that combines 3-5 of these 
functions in a realistic workflow.

Output only the .rlang source code with comments."""
    
    return prompt
```

### Pipeline 5: Fully Automated End-to-End

Here's a complete script that combines everything:

```python
#!/usr/bin/env python3
"""
generate_ai_docs.py

Fully automated pipeline to generate AI-optimized documentation 
from a language's source code, headers, tests, and existing docs.

Usage:
    python generate_ai_docs.py \
        --source ./stdlib/src \
        --headers ./stdlib/include \
        --tests ./stdlib/tests \
        --docs ./docs \
        --examples ./example_apps \
        --output ./ai_docs \
        --language rarelang \
        --model claude-sonnet-4-20250514
"""

import argparse
import os
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

def run_repomix(input_dirs: list[str], output_file: str):
    """Pack documentation using Repomix."""
    config = {
        "output": {
            "filePath": output_file,
            "style": "xml",
            "headerText": f"Generated {datetime.now().isoformat()}",
            "removeComments": False,
            "showLineNumbers": True
        },
        "include": [f"{d}/**/*" for d in input_dirs],
        "ignore": {
            "customPatterns": ["**/*.pdf", "**/*.png", "**/*.jpg", 
                              "**/node_modules/**", "**/.git/**"]
        }
    }
    
    config_path = "repomix.config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        result = subprocess.run(
            ["repomix", "--config", config_path],
            capture_output=True, text=True
        )
        print(f"Repomix output: {result.stdout}")
        if result.returncode != 0:
            print(f"Repomix error: {result.stderr}")
    except FileNotFoundError:
        print("Repomix not found. Install with: npm install -g repomix")
        print("Falling back to manual concatenation...")
        manual_concat(input_dirs, output_file)

def manual_concat(input_dirs: list[str], output_file: str):
    """Fallback: manually concatenate files in XML format."""
    with open(output_file, 'w') as out:
        out.write("<repository>\n<repository_files>\n")
        
        for input_dir in input_dirs:
            for root, dirs, files in os.walk(input_dir):
                for f in sorted(files):
                    if f.endswith(('.md', '.txt', '.rlang', '.rl', '.h')):
                        path = os.path.join(root, f)
                        with open(path, 'r', errors='replace') as fh:
                            content = fh.read()
                        rel_path = os.path.relpath(path)
                        out.write(f'<file path="{rel_path}">\n')
                        out.write(f'<content>\n{content}\n</content>\n')
                        out.write('</file>\n')
        
        out.write("</repository_files>\n</repository>\n")

def generate_llms_txt(docs_dir: str, output_dir: str, language_name: str):
    """Generate llms.txt router file from documentation structure."""
    sections = []
    
    for root, dirs, files in os.walk(docs_dir):
        for f in sorted(files):
            if f.endswith('.md'):
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, docs_dir)
                
                # Read first non-empty line as title, first paragraph as description
                with open(path, 'r') as fh:
                    lines = fh.readlines()
                
                title = ''
                description = ''
                for line in lines:
                    line = line.strip()
                    if not title and line:
                        title = line.lstrip('#').strip()
                    elif title and not description and line:
                        description = line
                        break
                
                sections.append({
                    'path': rel_path,
                    'title': title,
                    'description': description
                })
    
    llms_txt = f"# {language_name} Documentation\n\n"
    llms_txt += f"> {language_name} programming language reference and guides.\n\n"
    
    # Group by directory
    from collections import defaultdict
    grouped = defaultdict(list)
    for s in sections:
        category = os.path.dirname(s['path']) or 'Core'
        grouped[category].append(s)
    
    for category, items in grouped.items():
        llms_txt += f"## {category.replace('/', ' > ').title()}\n\n"
        for item in items:
            llms_txt += f"- [{item['title']}]({item['path']}): {item['description']}\n"
        llms_txt += "\n"
    
    with open(os.path.join(output_dir, 'llms.txt'), 'w') as f:
        f.write(llms_txt)
    
    print(f"Generated: {output_dir}/llms.txt")

def generate_priming_files(output_dir: str, language_name: str, 
                           build_commands: dict = None):
    """Generate CLAUDE.md, .cursorrules, etc."""
    
    if build_commands is None:
        build_commands = {
            'build': f'{language_name.lower()} build',
            'test': f'{language_name.lower()} test',
            'run': f'{language_name.lower()} run',
            'fmt': f'{language_name.lower()} fmt',
        }
    
    claude_md = f"""# {language_name} Project

## Language
This project uses {language_name}. The complete language specification 
and standard library reference is in `ai_docs/llms-full.txt`.

**IMPORTANT:** Before writing or modifying any .rlang file, consult the 
language specification. Do not invent syntax or standard library functions.

## Build Commands
{chr(10).join(f'- {k.title()}: `{v}`' for k, v in build_commands.items())}

## Code Style
- Follow the conventions demonstrated in the `ai_docs/examples/` directory
- When uncertain about idiomatic patterns, check examples before generating code

## Documentation Reference
- Quick reference: `ai_docs/llms-small.txt`
- Full specification: `ai_docs/llms-full.txt`
- Examples: `ai_docs/examples/`
"""
    
    with open(os.path.join(output_dir, 'CLAUDE.md'), 'w') as f:
        f.write(claude_md)
    
    # .cursorrules (same content, different filename)
    with open(os.path.join(output_dir, '.cursorrules'), 'w') as f:
        f.write(claude_md)
    
    # .github/copilot-instructions.md
    gh_dir = os.path.join(output_dir, '.github')
    os.makedirs(gh_dir, exist_ok=True)
    with open(os.path.join(gh_dir, 'copilot-instructions.md'), 'w') as f:
        f.write(claude_md)
    
    print(f"Generated priming files in {output_dir}")

def generate_cheat_sheet(full_doc_path: str, output_dir: str, 
                         language_name: str, ai_client=None):
    """Use AI to generate llms-small.txt from the full documentation."""
    
    with open(full_doc_path, 'r') as f:
        full_doc = f.read()
    
    # Truncate if necessary (most APIs have limits)
    if len(full_doc) > 400000:  # rough char limit
        full_doc = full_doc[:400000] + "\n\n[TRUNCATED]"
    
    prompt = f"""Given the following complete documentation for {language_name}, 
generate an ultra-compressed quick reference card (under 500 tokens) that covers:

1. All primitive types on one line
2. Variable declaration syntax (mutable, immutable, constant)
3. Function declaration syntax (one-line template)
4. All control flow constructs (if/else, match, loops) as one-liners
5. Error handling pattern (one example)
6. The 10 most important standard library operations
7. The concurrency primitive (if any)

Format as a code comment block that could be pasted at the top of any 
source file as a reference.

Documentation:
{full_doc[:100000]}"""  # Use first 100k chars for this task
    
    if ai_client:
        response = ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        cheat_sheet = response.content[0].text
    else:
        cheat_sheet = f"# {language_name} Quick Reference\n\n[Generate with --use-ai flag]"
    
    with open(os.path.join(output_dir, 'llms-small.txt'), 'w') as f:
        f.write(cheat_sheet)
    
    print(f"Generated: {output_dir}/llms-small.txt")

def main():
    parser = argparse.ArgumentParser(
        description='Generate AI-optimized documentation suite'
    )
    parser.add_argument('--source', help='Source code directory')
    parser.add_argument('--headers', help='Header files directory')
    parser.add_argument('--tests', help='Test suite directory')
    parser.add_argument('--docs', required=True, help='Documentation directory')
    parser.add_argument('--examples', help='Example applications directory')
    parser.add_argument('--output', default='./ai_docs', help='Output directory')
    parser.add_argument('--language', default='RareLang', help='Language name')
    parser.add_argument('--use-ai', action='store_true', 
                       help='Use AI to generate summaries and examples')
    parser.add_argument('--model', default='claude-sonnet-4-20250514')
    
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(os.path.join(args.output, 'examples'), exist_ok=True)
    
    # Step 1: Gather all input directories
    input_dirs = [args.docs]
    if args.source:
        input_dirs.append(args.source)
    if args.headers:
        input_dirs.append(args.headers)
    if args.examples:
        input_dirs.append(args.examples)
    
    # Step 2: Generate full payload
    full_doc_path = os.path.join(args.output, 'llms-full.txt')
    print("=== Generating full documentation payload ===")
    run_repomix(input_dirs, full_doc_path)
    
    # Step 3: Generate router
    print("\n=== Generating llms.txt router ===")
    generate_llms_txt(args.docs, args.output, args.language)
    
    # Step 4: Generate priming files
    print("\n=== Generating priming files ===")
    generate_priming_files(args.output, args.language)
    
    # Step 5: Generate cheat sheet
    print("\n=== Generating cheat sheet ===")
    ai_client = None
    if args.use_ai:
        try:
            import anthropic
            ai_client = anthropic.Anthropic()
        except ImportError:
            print("anthropic package not found. Skipping AI generation.")
    
    generate_cheat_sheet(full_doc_path, args.output, args.language, ai_client)
    
    # Step 6: If tests are provided, extract examples
    if args.tests:
        print("\n=== Extracting examples from test suite ===")
        # This would use the test extraction pipeline described above
        print(f"TODO: Process {args.tests} with test_to_examples.py")
    
    print(f"\n=== Complete! Output in {args.output}/ ===")
    print(f"Files generated:")
    for root, dirs, files in os.walk(args.output):
        for f in files:
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            print(f"  {os.path.relpath(path, args.output):40s} {size:>8,d} bytes")

if __name__ == '__main__':
    main()
```

---

## GitHub Action for Continuous Regeneration

```yaml
# .github/workflows/generate-ai-docs.yml
name: Generate AI Documentation

on:
  push:
    paths:
      - 'docs/**'
      - 'stdlib/**'
      - 'tests/**'
      - 'examples/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install tools
        run: |
          npm install -g repomix
          pip install anthropic
      
      - name: Generate AI documentation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/generate_ai_docs.py \
            --docs ./docs \
            --source ./stdlib/src \
            --tests ./stdlib/tests \
            --examples ./examples \
            --output ./ai_docs \
            --language "RareLang" \
            --use-ai
      
      - name: Commit generated docs
        run: |
          git config user.name "AI Docs Bot"
          git config user.email "bot@example.com"
          git add ai_docs/
          git diff --staged --quiet || git commit -m "Regenerate AI documentation"
          git push
```

---

## The Landscape of AI Documentation Standards (As of Mid-2025)

No single standard has won yet. Here's the current state:

| Standard/Format | Who's Behind It | Adoption | Scope |
|---|---|---|---|
| `llms.txt` | Answer.AI / Jeremy Howard | Growing — hundreds of sites | Routing/discovery |
| `CLAUDE.md` | Anthropic | Claude Code users | Behavioral priming |
| `.cursorrules` / `.mdc` | Cursor (Anysphere) | Large — biggest AI IDE | Behavioral priming |
| `.clinerules` | Cline (open-source) | Medium | Behavioral priming |
| `AGENTS.md` | OpenAI | New — Codex CLI | Behavioral priming |
| MCP | Anthropic (open standard) | Growing rapidly | Dynamic tool access |
| Repomix XML | yamadashy (open-source) | Standard for repo packing | Full-context payload |
| Diataxis | Daniele Procida | Wide (human docs) | Documentation architecture |
| OpenAPI/Swagger | Linux Foundation | Universal for REST APIs | API specification |
| Tree-sitter | Max Brunsfeld / GitHub | Universal for editors | Syntax parsing |

**The missing standard:** There is no dominant, formalized specification for "AI-optimized example corpus." Multiple projects do it, but there's no equivalent of OpenAPI that says "this is how you structure annotated code examples for AI consumption." This is a gap in the ecosystem.

**Closest thing to a standard for examples:**
- **Jupyter notebooks** (`.ipynb`) — structured code + markdown + outputs — some AI tools can ingest these
- **R Markdown / Quarto** — similar: code chunks with narrative
- **Literate programming** (Knuth's concept, implemented in tools like `noweb`, `org-mode`) — interleaves explanation with code

The annotated-example-as-documentation approach is a form of literate programming optimized for LLM consumption rather than human reading. It's well-established in practice but not yet formalized as a standard.

---

## Recommended Reading and Projects

1. **`jxnl/llmstxt`** — Python utilities for working with llms.txt
2. **`yamadashy/repomix`** — The repository packer
3. **`continuedev/continue`** — Open-source AI assistant with custom docs support
4. **`pieces-app/documentation`** — Shows how Pieces structures their AI context
5. **`paul-gauthier/aider`** — Study how Aider builds repo maps
6. **`learnxinyminutes-docs/learnxinyminutes-docs.github.io`** — The original "cheat sheet as documentation" corpus
7. **`adambard/learnxinyminutes-docs`** — Source for all the language cheat sheets
8. **`rust-lang/rust-by-example`** — The gold standard for progressive annotated examples
9. **`PatrickJS/awesome-cursorrules`** — Community collection of priming files







The user has a specific project: creating AI-optimized documentation for OpenWrt development, covering:

OpenWrt ecosystem components:
Core system (C-based)
ucode (scripting language for backend)
LuCI (web interface framework)
LuCI frontend (JavaScript)
Package system (Makefiles, feeds)
What they've already gathered:

Official LuCI dev documentation
Selected official packages as examples
Core code headers, functions, APIs (especially ucode)
2 years of wiki pages from techref and guide-developer sections
Current deliverables:

llms.txt, markdown maps, root-level agents.md and readme.md, and an HTML representation of the project structure
What they're aiming for:

A comprehensive planning document that brainstorms how to upgrade these materials
Strategies to make AI tools more effective at OpenWrt development
Potentially hierarchical agents.md and readme.md files organized by folder
Integration of insights from previous discussions
Now I'm thinking through what would genuinely help AI systems understand and work within the OpenWrt ecosystem—this is a specialized domain that requires understanding how its different layers interact, from low-level C code to the scripting and web interface layers. I'm mapping out the core systems that tie OpenWrt together—libubox provides the foundational utilities, ubus handles inter-process communication, UCI manages configuration, and then there's the layered complexity of netifd, procd, rpcd, and the scripting/UI frameworks (ucode, LuCI in both Lua and modern JS forms). The build system sits on top of all this, which is why understanding the whole stack matters for effective AI assistance.

Now I'm thinking through the practical structure: how to organize documentation by folder, what examples to include for each major development pattern, and how to account for the fact that OpenWrt work spans multiple languages and contexts. I should also identify the specific tasks an AI gets asked to handle most often—writing Makefiles, building LuCI apps, scripting with ucode and ubus, working with C APIs, troubleshooting builds, and managing system initialization and hotplug behavior—so the documentation can be tailored to those real-world scenarios rather than being overly theoretical.

OpenWrt AI Documentation Project: Comprehensive Planning Document
Part 1: Understanding What AI Gets Wrong About OpenWrt
Before planning improvements, it's essential to catalog the specific failure modes AI tools exhibit when attempting OpenWrt development. Every element of the documentation strategy should target one or more of these failures.

Failure Category 1: Architectural Confusion
AI tools consistently conflate different eras and paradigms within OpenWrt:

What the AI does	What's actually correct
Generates Lua-based LuCI code (luci.model.cbi)	Modern LuCI uses client-side JavaScript with LuCI.form
Uses require("luci.model.uci") for config access	Modern approach uses ubus calls via rpcd or ucode's uci module
Writes busybox-style init scripts	OpenWrt uses procd-style init scripts with specific start_service() / stop_service() functions
Assumes systemd or sysvinit conventions	procd has its own service management paradigm
Generates standard Linux Makefiles for packages	OpenWrt package Makefiles use include $(TOPDIR)/rules.mk and BuildPackage macros
Assumes glibc	OpenWrt typically uses musl libc
Uses apt/yum package management concepts	OpenWrt uses opkg with a completely different packaging model
Failure Category 2: ucode Ignorance
ucode is rare enough that most LLMs have minimal training data. Common failures:

What the AI does	What's actually correct
Invents ucode syntax based on JavaScript guesses	ucode has specific syntax differences (e.g., {% %} template tags, let vs local)
Doesn't know ucode's standard library modules	uci, ubus, fs, math, struct etc. are separate loadable modules
Can't write ucode ubus methods	Specific pattern with conn.call(), type coercion, reply objects
Confuses ucode with Lua	Different languages entirely, though both are used/were used in OpenWrt
Doesn't know the ucode template system	Used in rpcd, uhttpd, and various system scripts
Failure Category 3: Build System Misunderstanding
What the AI does	What's actually correct
Writes $(MAKE) -C $(PKG_BUILD_DIR) directly	Should use Build/Compile override with $(MAKE_FLAGS) and cross-compile variables
Doesn't include proper PKG_* variables	PKG_NAME, PKG_VERSION, PKG_RELEASE, PKG_SOURCE, PKG_SOURCE_URL, PKG_HASH all required
Ignores PKG_LICENSE and PKG_MAINTAINER	Required for upstream package acceptance
Doesn't understand DEPENDS syntax	+package for runtime, @PACKAGE for build-time, +FEATURE:package for conditional
Generates manual install rules	Should use Package/$(PKG_NAME)/install with $(INSTALL_DIR), $(INSTALL_BIN), etc.
Failure Category 4: Inter-component Communication
The AI rarely understands how OpenWrt's components interact:

text

┌─────────────────────────────────────────────────────────────────┐
│                        LuCI Web Interface                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ LuCI JS Views│  │ LuCI JS Form │  │ Custom JS Modules    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │ HTTP/JSON-RPC                       │
├───────────────────────────┼─────────────────────────────────────┤
│                    ┌──────▼──────┐                               │
│                    │   uhttpd    │                               │
│                    │  + rpcd     │                               │
│                    └──────┬──────┘                               │
│                           │ Unix socket                         │
│                    ┌──────▼──────┐                               │
│                    │    ubus     │ ◄── Central message bus       │
│                    └──┬───┬───┬──┘                               │
│                       │   │   │                                  │
│              ┌────────┘   │   └────────┐                        │
│       ┌──────▼──────┐ ┌──▼────┐ ┌─────▼──────┐                │
│       │   netifd    │ │ procd │ │  rpcd       │                │
│       │ (networking)│ │(init) │ │ (RPC svcs)  │                │
│       └──────┬──────┘ └───────┘ └─────┬──────┘                │
│              │                        │                         │
│       ┌──────▼──────┐          ┌──────▼──────┐                 │
│       │   UCI       │          │  ucode      │                 │
│       │ /etc/config │          │  scripts    │                 │
│       └─────────────┘          └─────────────┘                 │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ libubox  │  │ libubus  │  │  libuci  │  │ libnl/other  │  │
│  │ (base)   │  │ (IPC)    │  │ (config) │  │ (system)     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
│                        C Libraries                              │
└─────────────────────────────────────────────────────────────────┘
The AI needs to understand this entire stack to write correct code at any layer. A LuCI view that reads firewall rules needs to know it goes through: JS rpc.declare() → uhttpd → rpcd → ubus → uci → /etc/config/firewall. If it doesn't understand this chain, it will try to read files directly or use wrong APIs.

Part 2: Current State Assessment and Gap Analysis
What You Have (Strengths)
Asset	Value	Coverage
LuCI dev documentation	High — this is the hardest for AI to find	LuCI JS API, form widgets, views
Official packages as examples	Very High — real working code	Package Makefiles, init scripts, configs
Core code headers/APIs (ucode)	Critical — AI has almost no ucode training data	ucode stdlib, C bindings
2 years of wiki (techref + guide-developer)	High — authoritative reference	Build system, packaging, cross-compilation
llms.txt	Good — router exists	Discovery/navigation
Markdown maps	Good — structural awareness	File organization
agents.md + readme.md	Good — behavioral priming exists	Root-level instructions
HTML file tree with links	Good — scrapeable	External access
What's Missing (Gaps)
Gap	Impact	Difficulty to Fill
Per-domain annotated examples	Critical — the #1 thing that will improve AI output	Medium
Per-folder CLAUDE.md/agents.md	High — contextual instructions per subsystem	Low
ucode language reference as a standalone cheat sheet	Critical — AI can't write ucode without this	Low
Anti-pattern documentation	High — prevents the specific errors cataloged above	Medium
Cross-layer interaction guides	High — "how to build a complete feature from UCI to LuCI"	Medium
Package Makefile templates with annotations	Very High — most common AI task for OpenWrt	Low
UCI schema documentation	Medium — what config options exist for core packages	Medium
Error message reference	Medium — build errors, runtime errors, ubus errors	High
Repomix XML payload	Medium — single-file ingestion for tools	Low
Version/era disambiguation	High — stops AI from generating legacy Lua LuCI code	Low
Tree-sitter grammar for ucode	Medium-long-term — enables AST-aware tooling	High
Part 3: Proposed Directory Structure
text

openwrt-ai-docs/
│
├── README.md                          # Project overview, how to use these docs
├── CLAUDE.md                          # Root-level behavioral priming
├── agents.md                          # Root-level agent instructions
├── llms.txt                           # Router (keep existing, enhance)
├── llms-small.txt                     # NEW: Ultra-compressed cheat sheet
├── llms-full.txt                      # NEW: Repomix-generated full payload
├── repomix.config.json                # NEW: Repomix configuration
├── index.html                         # Existing HTML file tree
│
├── 00-orientation/                    # NEW: "Read this first" for AI
│   ├── CLAUDE.md                      # "You are an OpenWrt developer..."
│   ├── architecture-overview.md       # The stack diagram above, in detail
│   ├── era-guide.md                   # NEW: What's current vs deprecated
│   ├── common-ai-mistakes.md         # NEW: Explicit anti-pattern guide
│   └── glossary.md                    # NEW: OpenWrt-specific terminology
│
├── 01-ucode/                          # ucode language documentation
│   ├── CLAUDE.md                      # "When writing ucode, follow these rules..."
│   ├── agents.md
│   ├── language-reference/
│   │   ├── syntax-quick-ref.md        # NEW: ucode cheat sheet
│   │   ├── types-and-operators.md
│   │   ├── control-flow.md
│   │   ├── functions-and-closures.md
│   │   ├── modules-and-require.md
│   │   └── template-syntax.md         # {% %} templates
│   ├── stdlib/
│   │   ├── uci-module.md
│   │   ├── ubus-module.md
│   │   ├── fs-module.md
│   │   ├── math-module.md
│   │   ├── struct-module.md
│   │   └── [other modules].md
│   ├── headers/                       # Ripped C headers for ucode VM/API
│   │   └── [existing header files]
│   └── examples/                      # NEW: Annotated ucode examples
│       ├── 01-hello-world.uc
│       ├── 02-uci-read-write.uc
│       ├── 03-ubus-call.uc
│       ├── 04-ubus-service.uc
│       ├── 05-file-operations.uc
│       ├── 06-json-handling.uc
│       ├── 07-template-rendering.uc
│       ├── 08-rpcd-plugin.uc
│       ├── 09-hotplug-script.uc
│       └── 10-complete-daemon.uc
│
├── 02-luci/                           # LuCI web interface
│   ├── CLAUDE.md                      # "LuCI uses client-side JS. NEVER generate Lua LuCI code."
│   ├── agents.md
│   ├── architecture.md                # How LuCI JS works
│   ├── api-reference/
│   │   ├── [existing LuCI docs]
│   │   ├── form-api.md               # LuCI.form.* reference
│   │   ├── rpc-api.md                # rpc.declare() patterns
│   │   ├── view-api.md               # L.view.extend() patterns
│   │   ├── network-api.md            # LuCI.network.* 
│   │   ├── firewall-api.md           # LuCI.firewall.*
│   │   └── widgets-api.md            # UI widgets reference
│   ├── examples/                      # NEW: Annotated LuCI examples
│   │   ├── 01-minimal-view.js
│   │   ├── 02-simple-form.js
│   │   ├── 03-form-with-validation.js
│   │   ├── 04-custom-rpc-calls.js
│   │   ├── 05-dynamic-form-sections.js
│   │   ├── 06-status-page.js
│   │   ├── 07-modal-dialogs.js
│   │   ├── 08-file-upload.js
│   │   ├── 09-network-config-page.js
│   │   └── 10-complete-application/
│   │       ├── htdocs/
│   │       │   └── luci-static/
│   │       │       └── resources/
│   │       │           └── view/
│   │       │               └── myapp/
│   │       │                   ├── overview.js
│   │       │                   ├── settings.js
│   │       │                   └── status.js
│   │       ├── root/
│   │       │   ├── etc/config/myapp
│   │       │   └── usr/share/luci/menu.d/luci-app-myapp.json
│   │       │       └── usr/share/rpcd/acl.d/luci-app-myapp.json
│   │       └── Makefile
│   └── official-packages/             # Existing ripped packages
│       └── [existing package examples]
│
├── 03-build-system/                   # OpenWrt build system
│   ├── CLAUDE.md                      # "OpenWrt Makefiles follow specific patterns..."
│   ├── agents.md
│   ├── package-makefile-reference.md
│   ├── feeds-and-dependencies.md
│   ├── cross-compilation.md
│   ├── menuconfig-integration.md
│   ├── templates/                     # NEW: Copy-paste-ready templates
│   │   ├── simple-c-package/
│   │   │   ├── Makefile              # Heavily annotated
│   │   │   └── src/
│   │   │       ├── main.c
│   │   │       └── Makefile
│   │   ├── ucode-package/
│   │   │   ├── Makefile
│   │   │   └── files/
│   │   │       └── usr/share/ucode/mymodule.uc
│   │   ├── luci-app-package/
│   │   │   ├── Makefile
│   │   │   ├── htdocs/...
│   │   │   └── root/...
│   │   ├── kernel-module-package/
│   │   │   └── Makefile
│   │   ├── python-package/
│   │   │   └── Makefile
│   │   └── package-with-init-script/
│   │       ├── Makefile
│   │       └── files/
│   │           └── etc/init.d/myservice
│   └── examples/                      # NEW: Real Makefile examples annotated
│       └── [annotated versions of official packages]
│
├── 04-core-apis/                      # C libraries
│   ├── CLAUDE.md
│   ├── agents.md
│   ├── libubox/
│   │   ├── reference.md
│   │   ├── headers/                   # Existing ripped headers
│   │   └── examples/
│   │       ├── 01-blob-buffers.c
│   │       ├── 02-avl-trees.c
│   │       ├── 03-uloop-events.c
│   │       ├── 04-ustream.c
│   │       └── 05-runqueue.c
│   ├── libubus/
│   │   ├── reference.md
│   │   ├── headers/
│   │   └── examples/
│   │       ├── 01-ubus-client.c
│   │       ├── 02-ubus-server.c
│   │       └── 03-ubus-subscriber.c
│   ├── libuci/
│   │   ├── reference.md
│   │   ├── headers/
│   │   └── examples/
│   │       ├── 01-read-config.c
│   │       └── 02-write-config.c
│   ├── ubus/
│   │   └── protocol-reference.md
│   └── uci/
│       ├── config-format.md
│       └── common-configs/           # NEW: UCI schema for core packages
│           ├── network.md
│           ├── wireless.md
│           ├── firewall.md
│           ├── dhcp.md
│           └── system.md
│
├── 05-system-integration/             # NEW: Cross-layer guides
│   ├── CLAUDE.md
│   ├── agents.md
│   ├── procd-init-scripts.md         # How to write procd init scripts
│   ├── hotplug-scripts.md            # Hotplug event handling
│   ├── ubus-service-lifecycle.md     # Register, expose, consume ubus services
│   ├── rpcd-plugins.md               # Writing rpcd plugins for LuCI backend
│   ├── netifd-protocol-handlers.md   # Custom network protocol scripts
│   └── full-stack-walkthrough/        # NEW: Complete feature, all layers
│       ├── README.md                  # "Building a VPN toggle from UCI to LuCI"
│       ├── 01-uci-config.md
│       ├── 02-init-script.md
│       ├── 03-ubus-service.md
│       ├── 04-rpcd-acl.md
│       ├── 05-luci-view.md
│       └── complete-package/
│           └── [full working package]
│
├── 06-wiki-reference/                 # Existing wiki rips
│   ├── CLAUDE.md                      # "This is reference material from the OpenWrt wiki..."
│   ├── agents.md
│   ├── techref/
│   │   └── [existing wiki pages]
│   └── guide-developer/
│       └── [existing wiki pages]
│
├── 07-anti-patterns/                  # NEW: What NOT to do
│   ├── CLAUDE.md
│   ├── deprecated-patterns.md         # Lua LuCI, old init scripts, etc.
│   ├── common-build-errors.md         # Build errors and fixes
│   ├── common-runtime-errors.md       # ubus errors, UCI errors, etc.
│   └── platform-assumptions.md        # Things that differ from desktop Linux
│
└── scripts/                           # NEW: Generation and maintenance scripts
    ├── generate-repomix.sh
    ├── generate-llms-txt.py
    ├── extract-examples-from-packages.py
    ├── validate-examples.sh
    └── update-from-wiki.sh
Part 4: Per-Folder CLAUDE.md / agents.md Strategy
Each folder should have contextual instructions that activate when an AI tool is working in that directory. Here are the specific contents:

Root CLAUDE.md
Markdown

# OpenWrt Development Documentation

This repository contains the complete reference documentation for 
developing OpenWrt packages, LuCI applications, ucode scripts, and 
C programs targeting the OpenWrt platform.

## Critical Context

OpenWrt is an embedded Linux distribution for network devices. 
Development differs significantly from desktop Linux:

- **C library**: musl (not glibc) — some POSIX functions are missing or behave differently
- **Init system**: procd (not systemd, not sysvinit)
- **IPC**: ubus (not D-Bus)
- **Configuration**: UCI files in /etc/config/ (not arbitrary config files)
- **Web interface**: LuCI with client-side JavaScript (NOT Lua — Lua LuCI is deprecated)
- **Scripting**: ucode (NOT Lua for new development)
- **Package format**: opkg/ipk (NOT apt/deb or rpm)
- **Build system**: OpenWrt buildroot with specialized Makefiles (NOT cmake/autotools directly)
- **Filesystem**: Read-only squashfs root with JFFS2/UBIFS overlay

## When Writing Code for OpenWrt

1. ALWAYS check `01-ucode/` before writing ucode — the AI has limited training data on this language
2. ALWAYS check `02-luci/` before writing LuCI code — use the JS API, never Lua
3. ALWAYS check `03-build-system/templates/` before writing package Makefiles
4. ALWAYS check `07-anti-patterns/` to avoid generating deprecated code
5. For any ubus interaction, verify method names against `04-core-apis/ubus/`

## Build Commands

- Full build: `make -j$(nproc)` (from buildroot)
- Single package: `make package/mypackage/compile V=s`
- Rebuild single package: `make package/mypackage/{clean,compile} V=s`
- Install to device: `scp bin/packages/*/base/mypackage*.ipk root@router:/tmp/ && ssh root@router opkg install /tmp/mypackage*.ipk`
- Menuconfig: `make menuconfig`
- Kernel menuconfig: `make kernel_menuconfig`

## File Organization

- `00-orientation/` — Read first. Architecture, glossary, era guide.
- `01-ucode/` — ucode language reference and examples
- `02-luci/` — LuCI JavaScript framework reference and examples
- `03-build-system/` — Package Makefile reference and templates
- `04-core-apis/` — C library headers and API reference (libubox, libubus, libuci)
- `05-system-integration/` — Cross-layer guides (procd, hotplug, rpcd, netifd)
- `06-wiki-reference/` — Raw wiki pages (techref, guide-developer)
- `07-anti-patterns/` — What NOT to do, common errors, deprecated patterns
01-ucode/CLAUDE.md
Markdown

# ucode Development Context

ucode is OpenWrt's preferred scripting language, replacing Lua for 
system scripting and rpcd plugins. It has JavaScript-like syntax but 
is a distinct language with its own semantics.

## CRITICAL: Do Not Confuse With JavaScript

- ucode uses `let` and `const` but NOT `var`
- ucode has `null` but also has distinct behavior for undefined values
- ucode strings are byte strings, not Unicode
- ucode does NOT have `class` syntax — use objects and prototypes differently
- ucode template syntax uses `{% %}` for statements, `{{ }}` for expressions
- Regular expressions use a different engine than JavaScript

## Module Loading

```ucode
// Load a module
import { cursor } from 'uci';
import { connect } from 'ubus';
import { readfile, writefile, stat } from 'fs';
Alternatively with require():

ucode

let uci = require('uci');
let ubus = require('ubus');
let fs = require('fs');
Common Patterns
UCI Access
ucode

let cursor = uci.cursor();
cursor.load('network');
let lan_proto = cursor.get('network', 'lan', 'proto');
cursor.set('network', 'lan', 'ipaddr', '192.168.1.1');
cursor.commit('network');
ubus Calls
ucode

let conn = ubus.connect();
let result = conn.call('network.interface.lan', 'status', {});
let devices = conn.call('network.device', 'status', {});
conn.disconnect();
Refer to language-reference/ for syntax details and examples/ for patterns.
Refer to stdlib/ for module-specific API documentation.
ALWAYS verify function signatures against the reference before generating ucode.
text


### 02-luci/CLAUDE.md

```markdown
# LuCI Development Context

## VERSION WARNING — READ CAREFULLY

Modern LuCI (since ~2019) uses CLIENT-SIDE JAVASCRIPT rendering.
Do NOT generate:
- Lua-based LuCI code (luci.model.cbi, luci.dispatcher, etc.)
- Server-side rendered templates using Lua
- References to luci.model.uci (use rpc.declare() to call ubus instead)

The ONLY exception is if the user explicitly asks for legacy Lua LuCI code.

## How Modern LuCI Works

1. Menu entries are defined in JSON: `/usr/share/luci/menu.d/luci-app-*.json`
2. ACL permissions in JSON: `/usr/share/rpcd/acl.d/luci-app-*.json`
3. Views are JavaScript modules in: `/www/luci-static/resources/view/`
4. Views extend `L.view` and implement `render()` and optionally `load()`
5. Data comes from ubus calls via `rpc.declare()` or `L.resolveDefault()`
6. Forms use `form.Map` → `form.TypedSection` / `form.NamedSection` → `form.Option`

## Minimal View Template

```javascript
'use strict';
'require view';
'require form';
'require uci';

return view.extend({
    render: function() {
        var m, s, o;

        m = new form.Map('myconfig', _('My Application'),
            _('Description of my application'));

        s = m.section(form.TypedSection, 'mysection', _('Settings'));
        s.anonymous = true;

        o = s.option(form.Flag, 'enabled', _('Enable'));
        o.rmempty = false;

        o = s.option(form.Value, 'server', _('Server Address'));
        o.datatype = 'host';
        o.placeholder = 'example.com';

        return m.render();
    }
});
Check api-reference/ for complete API docs.
Check examples/ for progressive examples from simple to complex.
Check official-packages/ for real-world implementations.
text


### 03-build-system/CLAUDE.md

```markdown
# OpenWrt Build System Context

OpenWrt packages use a specialized Makefile format. Standard 
GNU Make / CMake / Autotools conventions do NOT apply directly.

## Package Makefile Structure (MEMORIZE THIS ORDER)

```makefile
include $(TOPDIR)/rules.mk

PKG_NAME:=mypackage
PKG_VERSION:=1.0.0
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://example.com/releases/
PKG_HASH:=sha256hashhere

PKG_LICENSE:=GPL-2.0-or-later
PKG_LICENSE_FILES:=LICENSE
PKG_MAINTAINER:=Your Name <email@example.com>

include $(INCLUDE_DIR)/package.mk

define Package/mypackage
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=My Package Description
  URL:=https://example.com/mypackage
  DEPENDS:=+libubox +libubus
endef

define Package/mypackage/description
  Longer description of what this package does.
  Can span multiple lines.
endef

define Package/mypackage/conffiles
/etc/config/mypackage
endef

define Build/Configure
    # Only if needed — many packages auto-detect
endef

define Build/Compile
    $(MAKE) -C $(PKG_BUILD_DIR) \
        CC="$(TARGET_CC)" \
        CFLAGS="$(TARGET_CFLAGS)" \
        LDFLAGS="$(TARGET_LDFLAGS)"
endef

define Package/mypackage/install
    $(INSTALL_DIR) $(1)/usr/bin
    $(INSTALL_BIN) $(PKG_BUILD_DIR)/mypackage $(1)/usr/bin/
    $(INSTALL_DIR) $(1)/etc/config
    $(INSTALL_CONF) ./files/mypackage.conf $(1)/etc/config/mypackage
    $(INSTALL_DIR) $(1)/etc/init.d
    $(INSTALL_BIN) ./files/mypackage.init $(1)/etc/init.d/mypackage
endef

$(eval $(call BuildPackage,mypackage))
CRITICAL RULES
The $(eval $(call BuildPackage,...)) line MUST be the last line
DEPENDS uses +pkg for runtime deps, NOT just pkg
$(1) in install rules refers to the package staging directory, NOT the filesystem root
Use $(INSTALL_DIR), $(INSTALL_BIN), $(INSTALL_DATA), $(INSTALL_CONF) — not mkdir/cp
For CMake packages, use include $(INCLUDE_DIR)/cmake.mk and the build will mostly auto-configure
PKG_HASH is REQUIRED for upstream packages — use sha256sum of the source tarball
See templates/ for copy-paste-ready templates for different package types.
text


### 05-system-integration/CLAUDE.md

```markdown
# OpenWrt System Integration Context

## procd Init Scripts

OpenWrt uses procd for service management. Init scripts go in 
`/etc/init.d/` and MUST follow this pattern:

```shell
#!/bin/sh /etc/rc.common

START=90
STOP=10
USE_PROCD=1

start_service() {
    procd_open_instance
    procd_set_param command /usr/bin/myservice
    procd_append_param command -c /etc/config/myservice
    procd_set_param respawn
    procd_set_param stderr 1
    procd_set_param stdout 1
    procd_close_instance
}

service_triggers() {
    procd_add_reload_trigger "myservice"
}
DO NOT use start() / stop() functions (that's the old sysvinit style).
ALWAYS use USE_PROCD=1 and start_service() / stop_service().

Hotplug Scripts
Placed in /etc/hotplug.d/<subsystem>/. Named with numeric prefix
for ordering: 50-myscript.

rpcd Plugins
For exposing custom ubus methods to LuCI, create rpcd plugins in
/usr/share/rpcd/acl.d/ (ACL) and register handlers via ucode or
executable scripts.

See individual .md files in this directory for detailed guides.
text


---

## Part 5: The Annotated Example Corpus (OpenWrt-Specific)

This is the highest-impact addition. Here are the specific examples needed, with templates:

### ucode Examples

**01-uci-read-write.uc:**
```javascript
// EXAMPLE: Reading and writing UCI configuration
// CONTEXT: UCI (Unified Configuration Interface) is how OpenWrt stores all settings.
//          Config files live in /etc/config/ and have a specific format.
//          ucode's 'uci' module provides the cursor API for reading/writing.
// WHEN TO USE: Any time you need to read or modify OpenWrt settings programmatically.
// REPLACES: The old Lua approach using luci.model.uci

// Import the UCI module
import { cursor } from 'uci';

// Create a cursor (connection to UCI)
let uci = cursor();

// --- READING CONFIGURATION ---

// Load a config file (must be called before get/set)
uci.load('network');

// Read a single option value
// uci.get(config, section, option) -> string or null
let lan_proto = uci.get('network', 'lan', 'proto');
printf('LAN protocol: %s\n', lan_proto);  // e.g., "static"

// Read a list option (returns array)
let dns_servers = uci.get('network', 'lan', 'dns');
printf('DNS servers: %J\n', dns_servers);  // e.g., ["8.8.8.8", "8.8.4.4"]

// Read the type of a section
let section_type = uci.get('network', 'lan');
printf('Section type: %s\n', section_type);  // "interface"

// Iterate over all sections of a type
uci.load('firewall');
uci.foreach('firewall', 'rule', function(section) {
    printf('Rule: %s -> %s\n', section.name, section.target);
    return true;  // return false to stop iteration
});

// --- WRITING CONFIGURATION ---

// Set a single value
uci.set('network', 'lan', 'ipaddr', '192.168.2.1');

// Set a list value (pass an array)
uci.set('network', 'lan', 'dns', ['1.1.1.1', '1.0.0.1']);

// Add a new anonymous section
let section_name = uci.add('firewall', 'rule');
uci.set('firewall', section_name, 'name', 'Allow-SSH');
uci.set('firewall', section_name, 'src', 'wan');
uci.set('firewall', section_name, 'dest_port', '22');
uci.set('firewall', section_name, 'proto', 'tcp');
uci.set('firewall', section_name, 'target', 'ACCEPT');

// Delete an option
uci.delete('network', 'lan', 'dns');

// Delete an entire section
uci.delete('firewall', section_name);

// IMPORTANT: Changes are NOT written to disk until you commit
uci.commit('network');
uci.commit('firewall');

// --- ANTI-PATTERN: Don't do this ---
// Do NOT read /etc/config/ files directly with fs.readfile()
// The UCI format has specific parsing rules (lists, unnamed sections, etc.)
// that simple text parsing will get wrong.

// ANTI-PATTERN: Don't forget to load() before get()
// let val = uci.get('network', 'lan', 'proto');  // ERROR if load() not called first

// ANTI-PATTERN: Don't forget to commit()
// uci.set('network', 'lan', 'ipaddr', '10.0.0.1');
// // Without commit(), this change exists only in memory and will be lost
03-ubus-call.uc:

JavaScript

// EXAMPLE: Making ubus calls from ucode
// CONTEXT: ubus is OpenWrt's inter-process communication bus.
//          Services register objects with methods on ubus.
//          Any process can call any registered method (subject to ACL).
// WHEN TO USE: Querying system state, triggering actions in other services,
//              getting network status, controlling services.
// NOTE: This is the equivalent of D-Bus on desktop Linux, but much lighter.

import { connect } from 'ubus';

// Connect to ubus (via Unix socket at /var/run/ubus/ubus.sock)
let conn = ubus.connect();
if (!conn) {
    warn('Failed to connect to ubus\n');
    exit(1);
}

// --- LISTING AVAILABLE OBJECTS ---
let objects = conn.list();
for (let obj in objects) {
    printf('Object: %s\n', obj);
    // Shows: network.interface.lan, system, network.device, etc.
}

// --- CALLING A METHOD ---

// Get system board info
let board = conn.call('system', 'board', {});
printf('Hostname: %s\n', board.hostname);
printf('Model: %s\n', board.model);
printf('Release: %J\n', board.release);

// Get network interface status
let lan_status = conn.call('network.interface.lan', 'status', {});
printf('LAN IP: %s\n', lan_status['ipv4-address']?.[0]?.address);
printf('LAN up: %s\n', lan_status.up ? 'yes' : 'no');

// Get all network devices
let devices = conn.call('network.device', 'status', {});
for (let devname, devinfo in devices) {
    printf('Device %s: %s, MTU %d\n', devname, 
           devinfo.up ? 'UP' : 'DOWN', devinfo.mtu);
}

// Get wireless status
let wifi = conn.call('network.wireless', 'status', {});
for (let radio, info in wifi) {
    printf('Radio %s: %s\n', radio, info.up ? 'UP' : 'DOWN');
    for (let iface in info.interfaces) {
        printf('  SSID: %s\n', iface.config.ssid);
    }
}

// --- CALLING WITH ARGUMENTS ---

// Trigger a network interface action
// conn.call('network.interface.wan', 'down', {});  // Bring WAN down
// conn.call('network.interface.wan', 'up', {});    // Bring WAN up

// Get specific DHCP leases
let dhcp_leases = conn.call('dhcp', 'ipv4leases', {});
if (dhcp_leases?.dhcp_leases) {
    for (let lease in dhcp_leases.dhcp_leases) {
        printf('Lease: %s -> %s (expires %d)\n', 
               lease.hostname, lease.ipaddr, lease.expires);
    }
}

// --- ERROR HANDLING ---

// If the object or method doesn't exist, call() returns null
let result = conn.call('nonexistent.object', 'method', {});
if (result === null) {
    warn('ubus call failed (object/method not found or permission denied)\n');
}

// Always disconnect when done
conn.disconnect();

// --- ANTI-PATTERN: Don't parse command output ---
// WRONG: let output = system('ubus call system board');
//        let data = json(output);
// RIGHT: let data = conn.call('system', 'board', {});
// Using the ubus library is faster, type-safe, and doesn't spawn a subprocess.
LuCI JavaScript Examples
01-minimal-view.js:

JavaScript

// EXAMPLE: Minimal LuCI view
// CONTEXT: This is the simplest possible LuCI page.
//          It demonstrates the basic structure every LuCI view must follow.
// WHEN TO USE: Starting point for any new LuCI page.
// FILE LOCATION: /www/luci-static/resources/view/myapp/overview.js
// MENU ENTRY: /usr/share/luci/menu.d/luci-app-myapp.json
// ACL ENTRY: /usr/share/rpcd/acl.d/luci-app-myapp.json

'use strict';
'require view';
// 'require' statements load LuCI JS modules
// Common modules: view, form, uci, rpc, ui, network, firewall, fs, tools.widgets

return view.extend({
    // render() is called when the page loads
    // It must return a DOM node or a promise that resolves to a DOM node
    render: function() {
        // E() creates DOM elements: E(tag, attributes, children)
        return E('div', { 'class': 'cbi-map' }, [
            E('h2', {}, _('My Application')),
            E('p', {}, _('This is a minimal LuCI view.')),
            E('div', { 'class': 'cbi-section' }, [
                E('p', {}, _('Hello from LuCI!'))
            ])
        ]);
    },

    // Optional: handleSaveApply, handleSave, handleReset for form pages
});

// CORRESPONDING MENU ENTRY (/usr/share/luci/menu.d/luci-app-myapp.json):
// {
//     "admin/myapp": {
//         "title": "My Application",
//         "order": 50,
//         "action": {
//             "type": "firstchild"
//         }
//     },
//     "admin/myapp/overview": {
//         "title": "Overview",
//         "order": 1,
//         "action": {
//             "type": "view",
//             "path": "myapp/overview"
//         }
//     }
// }

// CORRESPONDING ACL ENTRY (/usr/share/rpcd/acl.d/luci-app-myapp.json):
// {
//     "luci-app-myapp": {
//         "description": "Grant access to My Application",
//         "read": {
//             "ubus": {
//                 "uci": ["get", "state"]
//             },
//             "uci": ["myapp"]
//         },
//         "write": {
//             "ubus": {
//                 "uci": ["set", "delete", "rename", "reorder", "commit"]
//             },
//             "uci": ["myapp"]
//         }
//     }
// }
03-form-with-validation.js:

JavaScript

// EXAMPLE: LuCI form with validation and conditional options
// CONTEXT: Most LuCI pages are forms that read/write UCI configuration.
//          The form.Map system automatically handles load/save/apply.
// WHEN TO USE: Any settings page that modifies UCI configuration.
// FILE LOCATION: /www/luci-static/resources/view/myapp/settings.js

'use strict';
'require view';
'require form';
'require uci';
'require tools.widgets as widgets';  // For common widgets like DeviceSelect

return view.extend({
    render: function() {
        var m, s, o;

        // form.Map(config, title, description)
        // 'config' matches /etc/config/<config>
        m = new form.Map('myapp', _('My Application Settings'),
            _('Configure the my application service.'));

        // TypedSection: shows all sections of type 'service' in the config
        // NamedSection: shows one specific named section
        s = m.section(form.TypedSection, 'service', _('Service Configuration'));
        s.anonymous = true;   // Don't show section names
        s.addremove = false;  // Don't allow adding/removing sections

        // Flag = checkbox (boolean)
        o = s.option(form.Flag, 'enabled', _('Enable Service'),
            _('Start the service on boot'));
        o.rmempty = false;    // Write '0' instead of removing the option
        o.default = '0';

        // Value = text input
        o = s.option(form.Value, 'server', _('Server Address'),
            _('IP address or hostname of the upstream server'));
        o.datatype = 'host';  // Validates as IP address or hostname
        o.placeholder = 'vpn.example.com';
        o.rmempty = false;
        // Only show this option when service is enabled:
        o.depends('enabled', '1');

        // Value with port validation
        o = s.option(form.Value, 'port', _('Server Port'));
        o.datatype = 'port';  // Validates as 1-65535
        o.default = '1194';
        o.depends('enabled', '1');

        // ListValue = dropdown/select
        o = s.option(form.ListValue, 'protocol', _('Protocol'));
        o.value('udp', _('UDP'));
        o.value('tcp', _('TCP'));
        o.default = 'udp';
        o.depends('enabled', '1');

        // MultiValue = multiple selection
        o = s.option(form.MultiValue, 'allowed_clients', _('Allowed Clients'));
        o.value('lan', _('LAN clients'));
        o.value('guest', _('Guest network'));
        o.value('iot', _('IoT devices'));
        o.depends('enabled', '1');

        // DynamicList = editable list of values
        o = s.option(form.DynamicList, 'dns', _('DNS Servers'),
            _('Custom DNS servers pushed to clients'));
        o.datatype = 'ipaddr';  // Each entry must be a valid IP
        o.depends('enabled', '1');

        // TextValue = multi-line text
        o = s.option(form.TextValue, 'custom_config', _('Custom Configuration'),
            _('Additional configuration directives, one per line'));
        o.rows = 5;
        o.depends('enabled', '1');

        // FileUpload = file selector
        o = s.option(form.FileUpload, 'certificate', _('TLS Certificate'));
        o.root_directory = '/etc/myapp/certs';
        o.depends('enabled', '1');

        // Using a widget from tools.widgets
        // DeviceSelect shows a dropdown of network interfaces
        o = s.option(widgets.DeviceSelect, 'interface', _('Listen Interface'));
        o.multiple = false;
        o.noaliases = true;
        o.depends('enabled', '1');

        // --- ADVANCED: Custom validation ---
        o = s.option(form.Value, 'mtu', _('MTU'));
        o.datatype = 'range(68, 9000)';  // Validate numeric range
        o.default = '1500';
        o.validate = function(section_id, value) {
            // Custom validation function
            // Return true for valid, or an error string for invalid
            var proto = this.map.lookupOption('protocol', section_id);
            if (proto && proto[0].formvalue(section_id) === 'tcp' && 
                parseInt(value) > 1460) {
                return _('MTU should not exceed 1460 for TCP');
            }
            return true;
        };

        // --- SECOND SECTION: Typed list of rules ---
        s = m.section(form.TableSection, 'rule', _('Access Rules'));
        s.addremove = true;       // Allow adding/removing rules
        s.anonymous = true;
        s.sortable = true;        // Allow drag-to-reorder

        o = s.option(form.Value, 'name', _('Name'));
        o.rmempty = false;

        o = s.option(form.Value, 'src_ip', _('Source IP'));
        o.datatype = 'cidr4';    // Validates as CIDR notation

        o = s.option(form.ListValue, 'action', _('Action'));
        o.value('allow', _('Allow'));
        o.value('deny', _('Deny'));

        return m.render();
    }
});

// CORRESPONDING UCI CONFIG (/etc/config/myapp):
// config service
//     option enabled '1'
//     option server 'vpn.example.com'
//     option port '1194'
//     option protocol 'udp'
//     list allowed_clients 'lan'
//     list allowed_clients 'guest'
//     list dns '1.1.1.1'
//     list dns '8.8.8.8'
//     option mtu '1500'
//
// config rule
//     option name 'Allow admin'
//     option src_ip '192.168.1.0/24'
//     option action 'allow'
//
// config rule
//     option name 'Deny IoT'
//     option src_ip '10.0.0.0/8'
//     option action 'deny'

// ANTI-PATTERN: Don't use raw XHR or fetch() to call ubus
// LuCI's form system handles all ubus communication automatically
// through the UCI binding.

// ANTI-PATTERN: Don't write to UCI in render()
// The form system handles save/apply automatically.
// If you need custom save logic, override handleSaveApply().
04-custom-rpc-calls.js:

JavaScript

// EXAMPLE: Making custom ubus/RPC calls from LuCI
// CONTEXT: When you need data beyond UCI config (system stats, 
//          runtime state, custom daemon status), you make ubus calls.
// WHEN TO USE: Status pages, monitoring views, triggering actions
//              that aren't simple config changes.

'use strict';
'require view';
'require rpc';
'require ui';
'require poll';

// Declare RPC methods upfront
// rpc.declare() creates a callable function from a ubus method
var callSystemBoard = rpc.declare({
    object: 'system',          // ubus object name
    method: 'board',           // method name
    // No params needed for this call
});

var callNetworkInterfaceStatus = rpc.declare({
    object: 'network.interface',
    method: 'dump',
    // expect: { ... }  // Optional: extract specific fields from response
});

// Custom RPC call to your own service
var callMyServiceStatus = rpc.declare({
    object: 'myservice',
    method: 'status',
    params: [],               // No parameters
    expect: { running: false } // Default if call fails
});

var callMyServiceRestart = rpc.declare({
    object: 'myservice',
    method: 'restart',
    params: ['reason'],       // This method takes a 'reason' parameter
});

return view.extend({
    // load() runs before render() — fetch data here
    // Returns a promise; resolved values are passed to render() as arguments
    load: function() {
        return Promise.all([
            callSystemBoard(),
            callNetworkInterfaceStatus(),
            callMyServiceStatus()
        ]);
    },

    render: function(data) {
        // data[0] = system board info
        // data[1] = network interfaces
        // data[2] = myservice status

        var boardInfo = data[0];
        var interfaces = data[1].interface || [];
        var serviceStatus = data[2];

        var view = E('div', { 'class': 'cbi-map' }, [
            E('h2', {}, _('System Status')),

            // Board info
            E('div', { 'class': 'cbi-section' }, [
                E('h3', {}, _('Device Information')),
                E('table', { 'class': 'table' }, [
                    E('tr', { 'class': 'tr' }, [
                        E('td', { 'class': 'td' }, _('Hostname')),
                        E('td', { 'class': 'td' }, boardInfo.hostname)
                    ]),
                    E('tr', { 'class': 'tr' }, [
                        E('td', { 'class': 'td' }, _('Model')),
                        E('td', { 'class': 'td' }, boardInfo.model)
                    ]),
                    E('tr', { 'class': 'tr' }, [
                        E('td', { 'class': 'td' }, _('Firmware')),
                        E('td', { 'class': 'td' }, boardInfo.release?.description || '-')
                    ])
                ])
            ]),

            // Service status with action button
            E('div', { 'class': 'cbi-section' }, [
                E('h3', {}, _('My Service')),
                E('p', {}, [
                    _('Status: '),
                    E('span', {
                        'style': 'color:' + (serviceStatus.running ? 'green' : 'red')
                    }, serviceStatus.running ? _('Running') : _('Stopped'))
                ]),
                E('button', {
                    'class': 'cbi-button cbi-button-action',
                    'click': ui.createHandlerFn(this, 'handleRestart')
                }, _('Restart Service'))
            ]),

            // Network interfaces
            E('div', { 'class': 'cbi-section' }, [
                E('h3', {}, _('Network Interfaces')),
                E('table', { 'class': 'table' }, [
                    E('tr', { 'class': 'tr cbi-section-table-titles' }, [
                        E('th', { 'class': 'th' }, _('Interface')),
                        E('th', { 'class': 'th' }, _('Status')),
                        E('th', { 'class': 'th' }, _('IP Address'))
                    ])
                ].concat(interfaces.map(function(iface) {
                    var addr = (iface['ipv4-address'] || [])[0];
                    return E('tr', { 'class': 'tr' }, [
                        E('td', { 'class': 'td' }, iface.interface),
                        E('td', { 'class': 'td' }, iface.up ? _('Up') : _('Down')),
                        E('td', { 'class': 'td' }, addr ? addr.address : '-')
                    ]);
                })))
            ])
        ]);

        // Set up polling to refresh data every 5 seconds
        poll.add(L.bind(function() {
            return callMyServiceStatus().then(L.bind(function(result) {
                var statusSpan = view.querySelector('span[style]');
                if (statusSpan) {
                    statusSpan.style.color = result.running ? 'green' : 'red';
                    statusSpan.textContent = result.running ? _('Running') : _('Stopped');
                }
            }, this));
        }, this), 5);

        return view;
    },

    handleRestart: function(ev) {
        // Show a spinner while the action is in progress
        var btn = ev.currentTarget;
        btn.disabled = true;
        btn.classList.add('spinning');

        return callMyServiceRestart('user-requested').then(function() {
            ui.addNotification(null, E('p', _('Service restarted successfully')), 'info');
        }).catch(function(err) {
            ui.addNotification(null, E('p', _('Failed to restart: ') + err.message), 'danger');
        }).finally(function() {
            btn.disabled = false;
            btn.classList.remove('spinning');
        });
    }
});

// NOTE: For the custom 'myservice' ubus calls to work, your service must:
// 1. Register on ubus (via libubus in C, or via ubus module in ucode)
// 2. Have ACL entries in /usr/share/rpcd/acl.d/ granting access

// ANTI-PATTERN: Don't use XMLHttpRequest or fetch() directly
// Always use rpc.declare() — it handles authentication, CSRF tokens, 
// and error handling automatically.

// ANTI-PATTERN: Don't poll too aggressively
// poll.add() with intervals under 3 seconds can strain embedded devices.
Build System Templates
templates/simple-c-package/Makefile:

Makefile

# TEMPLATE: Simple C Package Makefile
# CONTEXT: Use this for a C program that compiles to a single binary.
#          This is the most common package type.
# MODIFY: Replace all instances of 'mypackage' with your package name.
#         Update PKG_SOURCE_URL and PKG_HASH for your source tarball.
#         Adjust DEPENDS for your actual dependencies.

# === REQUIRED: Include OpenWrt build rules ===
include $(TOPDIR)/rules.mk

# === REQUIRED: Package metadata ===
# These variables define how the package is fetched and identified
PKG_NAME:=mypackage
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
# PKG_RELEASE is incremented when you change the Makefile but not the upstream source

# === SOURCE: Where to download the source code ===
# Option A: Tarball download
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/example/mypackage/releases/download/v$(PKG_VERSION)/
PKG_HASH:=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
# Generate with: sha256sum mypackage-1.0.0.tar.gz

# Option B: Git checkout (use instead of PKG_SOURCE/URL/HASH)
# PKG_SOURCE_PROTO:=git
# PKG_SOURCE_URL:=https://github.com/example/mypackage.git
# PKG_SOURCE_VERSION:=abc123def456  # full commit hash
# PKG_MIRROR_HASH:=skip  # or actual hash of the checkout tarball

# === REQUIRED: License info (for upstream package acceptance) ===
PKG_LICENSE:=GPL-2.0-or-later
PKG_LICENSE_FILES:=LICENSE
PKG_MAINTAINER:=Your Name <your.email@example.com>

# === REQUIRED: Include package.mk (or cmake.mk, etc.) ===
include $(INCLUDE_DIR)/package.mk
# For CMake projects: include $(INCLUDE_DIR)/cmake.mk
# For autotools: include $(INCLUDE_DIR)/autotools.mk (implies package.mk)

# === REQUIRED: Package definition ===
define Package/mypackage
  # SECTION and CATEGORY determine where it appears in menuconfig
  SECTION:=utils
  CATEGORY:=Utilities
  # Common categories: Base system, Network, Utilities, Multimedia, Languages
  TITLE:=Short one-line description
  URL:=https://github.com/example/mypackage
  # DEPENDS: Runtime dependencies
  # +pkg = required dependency (installed automatically)
  # +FEATURE:pkg = conditional dependency (only if FEATURE is enabled)
  # @TARGET_x86 = only available for x86 target
  DEPENDS:=+libubox +libubus +libuci
endef

# === RECOMMENDED: Long description for menuconfig ===
define Package/mypackage/description
  Longer description of what this package does.
  This appears in the help text when selecting the package.
  Can span multiple lines.
endef

# === OPTIONAL: Config files that should not be overwritten on upgrade ===
define Package/mypackage/conffiles
/etc/config/mypackage
endef

# === OPTIONAL: Build configuration (if the default doesn't work) ===
# The default Build/Configure for package.mk does nothing.
# For autotools projects (with configure script), usually auto-handled.
# For cmake.mk, usually auto-handled.
# Override only when needed:
#
# define Build/Configure
#     $(call Build/Configure/Default,--with-feature=yes)
# endef

# === OPTIONAL: Compile override ===
# Default: $(MAKE) -C $(PKG_BUILD_DIR) ... with cross-compile flags
# Override for custom build systems:
define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) $(TARGET_CPPFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)"
endef
# NOTE: Use $(TARGET_CC), $(TARGET_CFLAGS), etc. — NEVER use 'gcc' or 'cc' directly.
# You are CROSS-COMPILING. The host compiler cannot produce router binaries.

# === REQUIRED: Install rules ===
define Package/mypackage/install
	# Create directories in the staging area
	# $(1) is the package staging root — NOT the actual filesystem
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/mypackage $(1)/usr/bin/

	# Install configuration file
	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_CONF) ./files/mypackage.conf $(1)/etc/config/mypackage

	# Install init script
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mypackage.init $(1)/etc/init.d/mypackage

	# Install ubus ACL (if exposing ubus methods)
	# $(INSTALL_DIR) $(1)/usr/share/rpcd/acl.d
	# $(INSTALL_DATA) ./files/mypackage.acl.json $(1)/usr/share/rpcd/acl.d/mypackage.json
endef

# === OPTIONAL: Post-install script (runs on the device) ===
define Package/mypackage/postinst
#!/bin/sh
# Enable and start the service after installation
[ -z "$${IPKG_INSTROOT}" ] && {
	/etc/init.d/mypackage enable
	/etc/init.d/mypackage start
}
exit 0
endef

# === REQUIRED: Must be the LAST LINE ===
$(eval $(call BuildPackage,mypackage))

# ANTI-PATTERN: Do NOT put anything after the $(eval ...) line
# ANTI-PATTERN: Do NOT use $(INSTALL_DIR) $(1)/usr/lib without checking
#               if the package actually installs libraries
# ANTI-PATTERN: Do NOT hardcode architecture-specific paths
# ANTI-PATTERN: Do NOT use 'install' or 'cp' — always use $(INSTALL_*)
procd Init Script Template
templates/package-with-init-script/files/etc/init.d/myservice:

Shell

#!/bin/sh /etc/rc.common
# TEMPLATE: procd init script
# CONTEXT: This is how OpenWrt services are managed.
#          procd handles starting, stopping, respawning, and 
#          restarting on config changes.
# FILE LOCATION: /etc/init.d/myservice
# ANTI-PATTERN: Do NOT use start()/stop() functions. 
#               That is the old sysvinit style.
#               ALWAYS use USE_PROCD=1 with start_service().

# START/STOP priority (lower START = earlier boot, lower STOP = later shutdown)
START=90
STOP=10

# REQUIRED: Enable procd integration
USE_PROCD=1

# Optional: Support for 'reload' via SIGHUP
PROG=/usr/bin/myservice

start_service() {
    # Read configuration
    config_load 'myservice'
    
    local enabled
    config_get_bool enabled 'main' 'enabled' 0
    [ "$enabled" -eq 0 ] && return 0

    local server port protocol log_level
    config_get server 'main' 'server' ''
    config_get port 'main' 'port' '1194'
    config_get protocol 'main' 'protocol' 'udp'
    config_get log_level 'main' 'log_level' 'warn'

    # Open a procd service instance
    procd_open_instance 'myservice'

    # Set the command to run
    procd_set_param command "$PROG"
    procd_append_param command --server "$server"
    procd_append_param command --port "$port"
    procd_append_param command --protocol "$protocol"
    procd_append_param command --log-level "$log_level"

    # Respawn configuration: threshold(seconds) timeout(seconds) retry(count)
    # Restart if it crashes, with 3600s threshold, 5s delay, 5 retries
    procd_set_param respawn 3600 5 5

    # Capture stdout/stderr to logd (viewable with 'logread')
    procd_set_param stdout 1
    procd_set_param stderr 1

    # Optional: Run as non-root user
    # procd_set_param user myservice
    # procd_set_param group myservice

    # Optional: Set environment variables
    # procd_set_param env HOME=/var/run/myservice

    # Optional: Create a PID file
    # procd_set_param pidfile /var/run/myservice.pid

    # Optional: Resource limits
    # procd_set_param limits core="unlimited"
    # procd_set_param limits nofile="65535 65535"

    # Optional: Bind to a network interface (wait for it to be ready)
    # procd_set_param netdev dev

    # Optional: Write data to a file before starting
    # procd_set_param file /etc/config/myservice

    # Close the instance definition
    procd_close_instance
}

# Optional: stop_service() is only needed if you need custom cleanup
# procd handles SIGTERM automatically
# stop_service() {
#     # Custom cleanup here
# }

# IMPORTANT: service_triggers() tells procd WHEN to restart the service
service_triggers() {
    # Restart when /etc/config/myservice changes
    procd_add_reload_trigger "myservice"

    # Optional: Restart when a network interface comes up
    # procd_add_interface_trigger "wan"

    # Optional: Validate UCI config before applying
    procd_add_validation validate_section
}

# Optional: UCI validation function
validate_section() {
    uci_load_validate myservice main "$1" \
        'enabled:bool:0' \
        'server:host' \
        'port:port:1194' \
        'protocol:or("udp","tcp"):udp' \
        'log_level:or("debug","info","warn","error"):warn'
}

# Optional: Custom reload behavior
# reload_service() {
#     stop
#     start
# }

# ANTI-PATTERN: Do NOT use this pattern (it's sysvinit, not procd):
# start() {
#     /usr/bin/myservice &
# }
# stop() {
#     killall myservice
# }
Part 6: The Era Disambiguation Document
This is one of the most important missing pieces. Create 00-orientation/era-guide.md:

Markdown

# OpenWrt Development Eras — What's Current vs Deprecated

This guide prevents AI tools from generating outdated code. OpenWrt has 
evolved significantly, and much online documentation (and AI training data) 
references deprecated approaches.

## Current (2023+) — USE THESE

| Component | Current Approach | Notes |
|---|---|---|
| LuCI views | Client-side JavaScript (`view.extend()`) | All new LuCI apps should use JS |
| LuCI forms | `form.Map`, `form.TypedSection`, `form.Option` | Auto-handles UCI read/write |
| System scripting | ucode | Preferred over Lua and shell for complex tasks |
| Init system | procd with `USE_PROCD=1` | `start_service()` pattern |
| Config access (script) | ucode `uci` module or `ubus` calls | |
| Config access (LuCI) | `rpc.declare()` → ubus → UCI | Indirect through ubus/rpcd |
| IPC | ubus (via `ubus` module in ucode, or `libubus` in C) | |
| Package Makefiles | Current format with `PKG_HASH` (sha256) | |
| JSON handling | Native in ucode, `jshn` in shell | |

## Deprecated (DO NOT USE unless explicitly asked)

| Component | Deprecated Approach | Replaced By | Still Works? |
|---|---|---|---|
| LuCI views | Lua CBI models (`luci.model.cbi`) | JS `form.Map` | Yes, but discouraged |
| LuCI views | Lua view templates (`.htm`) | JS `view.extend()` | Yes, but discouraged |
| LuCI dispatch | `luci.dispatcher` with `entry()` | Menu JSON files | Partially |
| System scripting | Lua (`require "luci.model.uci"`) | ucode | Yes |
| Init system | sysvinit `start()`/`stop()` | procd `start_service()` | Yes, but no respawn/reload |
| Config access | Direct Lua UCI library | ucode UCI module | Yes |
| JSON (shell) | `jsonfilter` standalone | `jshn` library | Yes |
| Package checksums | `PKG_MD5SUM` | `PKG_HASH` (sha256) | Build warns |

## How to Identify Outdated Code

If you see any of these in OpenWrt code, it's likely outdated:

```lua
-- THIS IS DEPRECATED LuCI Lua code:
require "luci.model.cbi"
require "luci.dispatcher"
m = Map("config", ...)
s = m:section(TypedSection, ...)
Shell

# THIS IS DEPRECATED sysvinit init script:
start() {
    /usr/bin/myservice &
}
stop() {
    kill $(cat /var/run/myservice.pid)
}
text

# THIS IS DEPRECATED package checksum:
PKG_MD5SUM:=abc123...
When Legacy Code Is Acceptable
Modifying EXISTING Lua LuCI apps (don't rewrite entire apps unnecessarily)
Targeting very old OpenWrt releases (18.06 and earlier)
Simple shell scripts that don't need ucode's complexity
The user explicitly requests Lua-based approaches
text


---

## Part 7: Auto-Generation Strategies Specific to OpenWrt

### Strategy 1: Extract Examples from Official Packages

You already have official packages. Here's how to systematically extract teaching material:

```python
#!/usr/bin/env python3
"""
extract_openwrt_patterns.py

Walk through official OpenWrt package directories and extract 
annotated examples of each pattern type found.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class OpenWrtPatternExtractor:
    def __init__(self, packages_dir):
        self.packages_dir = packages_dir
        self.patterns = defaultdict(list)
    
    def scan(self):
        """Walk all packages and categorize files by pattern type."""
        for pkg_dir in Path(self.packages_dir).rglob('*'):
            if not pkg_dir.is_dir():
                continue
            
            makefile = pkg_dir / 'Makefile'
            if makefile.exists():
                self._analyze_package(pkg_dir)
    
    def _analyze_package(self, pkg_dir):
        """Analyze a single package directory."""
        pkg_name = pkg_dir.name
        
        # 1. Package Makefile
        makefile = pkg_dir / 'Makefile'
        if makefile.exists():
            content = makefile.read_text(errors='replace')
            makefile_type = self._classify_makefile(content)
            self.patterns[f'makefile_{makefile_type}'].append({
                'package': pkg_name,
                'file': str(makefile),
                'type': makefile_type
            })
        
        # 2. Init scripts
        for init_script in pkg_dir.rglob('etc/init.d/*'):
            if init_script.is_file():
                content = init_script.read_text(errors='replace')
                init_type = 'procd' if 'USE_PROCD=1' in content else 'sysvinit'
                self.patterns[f'init_{init_type}'].append({
                    'package': pkg_name,
                    'file': str(init_script),
                    'type': init_type
                })
        
        # 3. UCI config defaults
        for conf in pkg_dir.rglob('etc/config/*'):
            if conf.is_file():
                self.patterns['uci_config'].append({
                    'package': pkg_name,
                    'file': str(conf)
                })
        
        # 4. LuCI JavaScript views
        for js_view in pkg_dir.rglob('*/view/**/*.js'):
            if js_view.is_file():
                content = js_view.read_text(errors='replace')
                view_type = self._classify_luci_view(content)
                self.patterns[f'luci_{view_type}'].append({
                    'package': pkg_name,
                    'file': str(js_view),
                    'type': view_type
                })
        
        # 5. LuCI menu definitions
        for menu in pkg_dir.rglob('*/menu.d/*.json'):
            if menu.is_file():
                self.patterns['luci_menu'].append({
                    'package': pkg_name,
                    'file': str(menu)
                })
        
        # 6. ACL definitions
        for acl in pkg_dir.rglob('*/acl.d/*.json'):
            if acl.is_file():
                self.patterns['rpcd_acl'].append({
                    'package': pkg_name,
                    'file': str(acl)
                })
        
        # 7. ucode scripts
        for uc in pkg_dir.rglob('*.uc'):
            if uc.is_file():
                self.patterns['ucode_script'].append({
                    'package': pkg_name,
                    'file': str(uc)
                })
        
        # 8. Hotplug scripts
        for hp in pkg_dir.rglob('etc/hotplug.d/**/*'):
            if hp.is_file():
                self.patterns['hotplug'].append({
                    'package': pkg_name,
                    'file': str(hp)
                })
        
        # 9. rpcd plugins
        for rpcd in pkg_dir.rglob('usr/libexec/rpcd/*'):
            if rpcd.is_file():
                self.patterns['rpcd_plugin'].append({
                    'package': pkg_name,
                    'file': str(rpcd)
                })
    
    def _classify_makefile(self, content):
        """Classify a package Makefile by type."""
        if 'cmake.mk' in content:
            return 'cmake'
        elif 'autotools.mk' in content:
            return 'autotools'
        elif 'kernel-defaults.mk' in content or 'KernelPackage' in content:
            return 'kernel_module'
        elif 'luci.mk' in content:
            return 'luci_app'
        elif 'python3-package.mk' in content:
            return 'python'
        elif 'golang-package.mk' in content:
            return 'golang'
        elif 'rust-package.mk' in content:
            return 'rust'
        elif 'nls.mk' in content:
            return 'with_nls'
        else:
            return 'standard'
    
    def _classify_luci_view(self, content):
        """Classify a LuCI JavaScript view by type."""
        if 'form.Map' in content:
            return 'form_view'
        elif 'rpc.declare' in content and 'form.Map' not in content:
            return 'status_view'
        elif 'form.GridSection' in content or 'form.TableSection' in content:
            return 'table_view'
        else:
            return 'custom_view'
    
    def report(self):
        """Generate a report of found patterns."""
        print("=" * 60)
        print("OpenWrt Pattern Analysis Report")
        print("=" * 60)
        
        for pattern_type, instances in sorted(self.patterns.items()):
            print(f"\n### {pattern_type} ({len(instances)} instances)")
            for inst in instances[:5]:  # Show first 5
                print(f"  - {inst['package']}: {inst['file']}")
            if len(instances) > 5:
                print(f"  ... and {len(instances) - 5} more")
    
    def select_best_examples(self, max_per_type=3):
        """Select the best examples for each pattern type.
        
        Heuristic: prefer smaller, simpler files as examples.
        """
        selected = {}
        
        for pattern_type, instances in self.patterns.items():
            # Sort by file size (smaller = simpler = better example)
            scored = []
            for inst in instances:
                try:
                    size = os.path.getsize(inst['file'])
                    scored.append((size, inst))
                except OSError:
                    continue
            
            scored.sort(key=lambda x: x[0])
            
            # Take the smallest files (simplest examples)
            # but skip files under 100 bytes (likely empty/stubs)
            selected[pattern_type] = [
                inst for size, inst in scored 
                if size > 100
            ][:max_per_type]
        
        return selected
    
    def generate_annotated_examples(self, selected, output_dir):
        """Generate annotated example files from selected patterns."""
        os.makedirs(output_dir, exist_ok=True)
        
        manifest = []
        
        for pattern_type, instances in selected.items():
            for i, inst in enumerate(instances):
                try:
                    content = Path(inst['file']).read_text(errors='replace')
                except Exception:
                    continue
                
                # Determine file extension
                ext = Path(inst['file']).suffix or '.txt'
                
                # Generate output filename
                out_name = f"{pattern_type}_{i+1:02d}_{inst['package']}{ext}"
                out_path = os.path.join(output_dir, out_name)
                
                # Add annotation header
                header = self._generate_header(pattern_type, inst)
                annotated = header + content
                
                with open(out_path, 'w') as f:
                    f.write(annotated)
                
                manifest.append({
                    'file': out_name,
                    'pattern': pattern_type,
                    'source_package': inst['package'],
                    'source_file': inst['file']
                })
                
                print(f"Generated: {out_path}")
        
        # Write manifest
        with open(os.path.join(output_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def _generate_header(self, pattern_type, instance):
        """Generate an annotation header for an example file."""
        headers = {
            'makefile_standard': '# EXAMPLE: Standard C package Makefile\n# SOURCE: {pkg}\n# PATTERN: Package with simple C source, compiled with make\n# USE AS TEMPLATE: Copy and modify PKG_* variables and install rules\n\n',
            'makefile_cmake': '# EXAMPLE: CMake-based package Makefile\n# SOURCE: {pkg}\n# PATTERN: Package using CMake build system\n# NOTE: cmake.mk handles most configuration automatically\n\n',
            'makefile_luci_app': '# EXAMPLE: LuCI application package Makefile\n# SOURCE: {pkg}\n# PATTERN: Web interface extension using LuCI JS\n# NOTE: luci.mk provides LuCI-specific build rules\n\n',
            'makefile_kernel_module': '# EXAMPLE: Kernel module package Makefile\n# SOURCE: {pkg}\n# PATTERN: Out-of-tree kernel module\n# NOTE: Uses KernelPackage instead of Package\n\n',
            'init_procd': '# EXAMPLE: procd init script\n# SOURCE: {pkg}\n# PATTERN: Service managed by procd with auto-respawn and config triggers\n# LOCATION: /etc/init.d/\n\n',
            'luci_form_view': '// EXAMPLE: LuCI form view (UCI configuration editor)\n// SOURCE: {pkg}\n// PATTERN: form.Map with TypedSection/NamedSection and Options\n// LOCATION: /www/luci-static/resources/view/\n\n',
            'luci_status_view': '// EXAMPLE: LuCI status/monitoring view\n// SOURCE: {pkg}\n// PATTERN: Custom view with rpc.declare() calls for live data\n// LOCATION: /www/luci-static/resources/view/\n\n',
            'ucode_script': '// EXAMPLE: ucode script\n// SOURCE: {pkg}\n// PATTERN: System script using ucode runtime\n\n',
            'hotplug': '# EXAMPLE: Hotplug event handler\n# SOURCE: {pkg}\n# PATTERN: Script triggered by system events (interface up/down, USB, etc.)\n# LOCATION: /etc/hotplug.d/<subsystem>/\n\n',
            'rpcd_plugin': '# EXAMPLE: rpcd plugin (ubus method exposed to LuCI)\n# SOURCE: {pkg}\n# PATTERN: Backend handler for custom LuCI RPC calls\n# LOCATION: /usr/libexec/rpcd/\n\n',
        }
        
        template = headers.get(pattern_type, '# EXAMPLE: {pattern}\n# SOURCE: {pkg}\n\n')
        return template.format(pkg=instance['package'], pattern=pattern_type)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_openwrt_patterns.py <packages_dir> [output_dir]")
        sys.exit(1)
    
    packages_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './extracted_examples'
    
    extractor = OpenWrtPatternExtractor(packages_dir)
    extractor.scan()
    extractor.report()
    
    selected = extractor.select_best_examples(max_per_type=3)
    extractor.generate_annotated_examples(selected, output_dir)
Strategy 2: Generate UCI Schema Documentation
One of the biggest gaps in AI's OpenWrt knowledge is understanding UCI configuration structure. Auto-extract it:

Python

#!/usr/bin/env python3
"""
extract_uci_schemas.py

Parse OpenWrt default config files and init script validation 
functions to build UCI schema documentation.
"""

import re
import os
from pathlib import Path

def extract_uci_validation_from_init(init_script_path):
    """Extract UCI validation rules from procd init scripts.
    
    Looks for uci_load_validate calls which define the expected 
    config structure.
    """
    content = Path(init_script_path).read_text(errors='replace')
    
    # Pattern: uci_load_validate config_name section_type "$1" \
    #     'option:type:default' \
    #     'option:type:default'
    validate_pattern = re.compile(
        r"uci_load_validate\s+(\w+)\s+(\w+)\s+[\"']\$1[\"']\s*\\?\s*((?:\s*'[^']+'\s*\\?\s*)+)",
        re.MULTILINE
    )
    
    schemas = []
    for match in validate_pattern.finditer(content):
        config_name = match.group(1)
        section_type = match.group(2)
        options_raw = match.group(3)
        
        options = []
        for opt_match in re.finditer(r"'([^']+)'", options_raw):
            opt_def = opt_match.group(1)
            parts = opt_def.split(':')
            option = {
                'name': parts[0] if len(parts) > 0 else '',
                'type': parts[1] if len(parts) > 1 else '',
                'default': parts[2] if len(parts) > 2 else None
            }
            options.append(option)
        
        schemas.append({
            'config': config_name,
            'section_type': section_type,
            'options': options,
            'source': init_script_path
        })
    
    return schemas

def parse_default_config(config_path):
    """Parse a UCI config file and extract its structure."""
    content = Path(config_path).read_text(errors='replace')
    
    sections = []
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # config <type> ['<name>']
        config_match = re.match(r"config\s+(\w+)(?:\s+'?(\w+)'?)?", line)
        if config_match:
            if current_section:
                sections.append(current_section)
            current_section = {
                'type': config_match.group(1),
                'name': config_match.group(2),  # None for anonymous
                'options': [],
                'lists': []
            }
            continue
        
        if current_section:
            # option <name> '<value>'
            opt_match = re.match(r"option\s+(\w+)\s+'?([^']*)'?", line)
            if opt_match:
                current_section['options'].append({
                    'name': opt_match.group(1),
                    'example_value': opt_match.group(2)
                })
                continue
            
            # list <name> '<value>'
            list_match = re.match(r"list\s+(\w+)\s+'?([^']*)'?", line)
            if list_match:
                current_section['lists'].append({
                    'name': list_match.group(1),
                    'example_value': list_match.group(2)
                })
    
    if current_section:
        sections.append(current_section)
    
    return sections

def generate_uci_doc(config_name, sections, validations=None):
    """Generate markdown documentation for a UCI config file."""
    doc = f"# UCI Configuration: /etc/config/{config_name}\n\n"
    
    # Group sections by type
    from collections import defaultdict
    by_type = defaultdict(list)
    for s in sections:
        by_type[s['type']].append(s)
    
    for section_type, instances in by_type.items():
        doc += f"## Section Type: `{section_type}`\n\n"
        
        # Find validation rules for this section type
        val_rules = {}
        if validations:
            for v in validations:
                if v['section_type'] == section_type:
                    for opt in v['options']:
                        val_rules[opt['name']] = opt
        
        # Collect all unique options across instances
        all_options = {}
        all_lists = {}
        for inst in instances:
            for opt in inst['options']:
                if opt['name'] not in all_options:
                    all_options[opt['name']] = opt
            for lst in inst['lists']:
                if lst['name'] not in all_lists:
                    all_lists[lst['name']] = lst
        
        if instances[0]['name']:
            doc += f"Named section (e.g., `config {section_type} '{instances[0]['name']}'`)\n\n"
        else:
            doc += f"Anonymous section (`config {section_type}`)\n\n"
        
        doc += "| Option | Type | Default | Example |\n"
        doc += "|--------|------|---------|----------|\n"
        
        for opt_name, opt_info in sorted(all_options.items()):
            val = val_rules.get(opt_name, {})
            opt_type = val.get('type', '?')
            default = val.get('default', '')
            example = opt_info['example_value']
            doc += f"| `{opt_name}` | {opt_type} | {default} | `{example}` |\n"
        
        for list_name, list_info in sorted(all_lists.items()):
            doc += f"| `{list_name}` (list) | string | | `{list_info['example_value']}` |\n"
        
        doc += "\n"
        
        # Show example config block
        doc += "```uci\n"
        inst = instances[0]
        if inst['name']:
            doc += f"config {section_type} '{inst['name']}'\n"
        else:
            doc += f"config {section_type}\n"
        for opt in inst['options']:
            doc += f"\toption {opt['name']} '{opt['example_value']}'\n"
        for lst in inst['lists']:
            doc += f"\tlist {lst['name']} '{lst['example_value']}'\n"
        doc += "```\n\n"
    
    return doc
Strategy 3: AI-Assisted Enrichment Pipeline
After extracting raw examples, use an LLM to add pedagogical annotations:

text

I have the following real-world OpenWrt package files extracted from 
the official repository. For each file, I need you to add comprehensive 
annotations that would help an AI coding assistant understand the patterns:

For Makefiles:
- Explain each PKG_* variable's purpose
- Note which sections are required vs optional
- Explain the DEPENDS syntax
- Annotate the install rules

For LuCI JavaScript views:
- Explain the view lifecycle (load → render → handleSaveApply)
- Annotate each form widget type used
- Explain the data flow (JS → rpc → ubus → UCI)
- Note the expected UCI config structure

For init scripts:
- Explain the procd integration
- Annotate each procd_set_param option
- Explain service_triggers
- Show what the corresponding UCI config should look like

For ucode scripts:
- Explain each module import
- Annotate ubus call patterns
- Explain UCI cursor usage
- Note error handling patterns

IMPORTANT CONTEXT:
- Modern OpenWrt uses ucode (NOT Lua) for system scripting
- Modern LuCI uses client-side JavaScript (NOT Lua CBI)
- Init scripts MUST use USE_PROCD=1 (NOT sysvinit start/stop)
- Mark any deprecated patterns with [DEPRECATED] if found

---
[PASTE EXTRACTED FILES]
Part 8: Cross-Layer Walkthrough (The Missing Connective Tissue)
This is perhaps the single most valuable document you can create. AI tools can figure out individual files but consistently fail at understanding how OpenWrt components connect.

05-system-integration/full-stack-walkthrough/README.md:

Markdown

# Full Stack Walkthrough: Building a Service Toggle

This walkthrough builds a complete, minimal OpenWrt package that:
1. Defines a UCI configuration schema
2. Runs a background service managed by procd
3. Exposes status via ubus
4. Provides a LuCI web interface for configuration and monitoring

Each step shows ONE layer, building on the previous.

## The Component Map
User clicks "Enable" in browser
│
▼
[LuCI JS view] ──form.Map writes──► [UCI /etc/config/myservice]
│ │
│ ┌─────▼─────┐
│ │ procd sees │
│ │ config │
│ │ change │
│ └─────┬─────┘
│ │
│ ┌─────▼──────┐
│ │ init script │
│ │ restarts │
│ │ service │
│ └─────┬──────┘
│ │
│ ┌─────▼──────┐
│ │ myservice │
│ │ (daemon) │
│ │ registers │
│ │ on ubus │
│ └─────┬──────┘
│ │
▼ ▼
[LuCI JS polls] ──rpc.declare()──► [ubus "myservice" "status"]

text


## Step 1: UCI Configuration

File: `files/etc/config/myservice`
[see 01-uci-config.md]

## Step 2: procd Init Script

File: `files/etc/init.d/myservice`
[see 02-init-script.md]

## Step 3: The Service Daemon (ucode)

File: `files/usr/bin/myservice`
[see 03-ubus-service.md]

## Step 4: rpcd ACL

File: `files/usr/share/rpcd/acl.d/luci-app-myservice.json`
[see 04-rpcd-acl.md]

## Step 5: LuCI Menu Entry

File: `files/usr/share/luci/menu.d/luci-app-myservice.json`
[see 04-rpcd-acl.md]

## Step 6: LuCI JavaScript View

File: `htdocs/luci-static/resources/view/myservice/settings.js`
[see 05-luci-view.md]

## Step 7: Package Makefile

File: `Makefile`
[see 06-makefile.md]

## Step 8: Testing

[see 07-testing.md]
Part 9: Specific Upgrades to Your Current Deliverables
Upgrade 1: Enhance llms.txt with OpenWrt-Specific Routing Logic
Your current llms.txt should include routing hints that tell AI tools which documents to consult for specific task types:

Markdown

# OpenWrt Development Documentation

> Complete reference for developing OpenWrt packages, LuCI web 
> applications, ucode scripts, and C programs targeting embedded 
> Linux network devices.

## Quick Start (Read First)
- [Architecture Overview](00-orientation/architecture-overview.md): 
  Read this BEFORE any development task. Explains ubus, UCI, procd, 
  and how components interact.
- [Era Guide](00-orientation/era-guide.md): CRITICAL — distinguishes 
  current from deprecated approaches. Prevents generating Lua LuCI code.
- [Common AI Mistakes](00-orientation/common-ai-mistakes.md): Patterns 
  that AI tools frequently get wrong. Read before generating any OpenWrt code.

## Task: Writing a New Package
- [Package Makefile Reference](03-build-system/package-makefile-reference.md): 
  Complete reference for all Makefile variables and macros.
- [Package Templates](03-build-system/templates/): Copy-paste-ready templates 
  for C, ucode, LuCI, kernel module, and Python packages.
- [Cross-Compilation](03-build-system/cross-compilation.md): Essential for 
  understanding TARGET_CC, staging directories, and musl considerations.

## Task: Building a LuCI Application
- [LuCI Architecture](02-luci/architecture.md): How LuCI JS rendering works.
- [Form API](02-luci/api-reference/form-api.md): form.Map, sections, options.
- [RPC API](02-luci/api-reference/rpc-api.md): rpc.declare() for ubus calls.
- [LuCI Examples](02-luci/examples/): Progressive examples from minimal to complete.
- [Full Stack Walkthrough](05-system-integration/full-stack-walkthrough/): 
  Complete package from UCI config through LuCI view.

## Task: Writing ucode Scripts
- [ucode Quick Reference](01-ucode/language-reference/syntax-quick-ref.md): 
  Complete syntax in cheat-sheet format. READ THIS FIRST — ucode is rare and 
  AI training data is limited.
- [ucode UCI Module](01-ucode/stdlib/uci-module.md): Reading/writing config.
- [ucode ubus Module](01-ucode/stdlib/ubus-module.md): Inter-process communication.
- [ucode Examples](01-ucode/examples/): Annotated examples for all common tasks.

## Task: Writing C Code for OpenWrt
- [libubox Reference](04-core-apis/libubox/): Base utility library (blob, avl, uloop).
- [libubus Reference](04-core-apis/libubus/): ubus client/server in C.
- [libuci Reference](04-core-apis/libuci/): UCI config access from C.

## Task: System Integration
- [procd Init Scripts](05-system-integration/procd-init-scripts.md): Service management.
- [Hotplug Scripts](05-system-integration/hotplug-scripts.md): Event handling.
- [rpcd Plugins](05-system-integration/rpcd-plugins.md): Exposing ubus to LuCI.
- [UCI Configuration Schemas](04-core-apis/uci/common-configs/): Structure of 
  network, wireless, firewall, DHCP configs.

## Reference (Raw Wiki Material)
- [Technical Reference](06-wiki-reference/techref/): Detailed technical docs 
  from OpenWrt wiki. Use for deep dives into specific subsystems.
- [Developer Guide](06-wiki-reference/guide-developer/): Step-by-step developer 
  documentation from OpenWrt wiki.

## Anti-Patterns (Consult When Uncertain)
- [Deprecated Patterns](07-anti-patterns/deprecated-patterns.md): What NOT to generate.
- [Common Build Errors](07-anti-patterns/common-build-errors.md): Error messages and fixes.
- [Platform Assumptions](07-anti-patterns/platform-assumptions.md): How OpenWrt 
  differs from desktop Linux.
Upgrade 2: Generate llms-small.txt (OpenWrt Cheat Sheet)
Markdown

# OpenWrt Development Quick Reference

## Architecture: UCI(config) → ubus(IPC) → procd(services) → LuCI(web UI via JS)

## Package Makefile Skeleton
include $(TOPDIR)/rules.mk
PKG_NAME/VERSION/RELEASE/SOURCE/SOURCE_URL/HASH/LICENSE/MAINTAINER
include $(INCLUDE_DIR)/package.mk
define Package/name → SECTION,CATEGORY,TITLE,DEPENDS(+dep)
define Package/name/install → $(INSTALL_DIR/BIN/DATA/CONF) $(1)/path
$(eval $(call BuildPackage,name)) # MUST BE LAST LINE

## procd Init Script
#!/bin/sh /etc/rc.common
START=90; USE_PROCD=1
start_service() { procd_open_instance; procd_set_param command /usr/bin/X; procd_set_param respawn; procd_close_instance; }
service_triggers() { procd_add_reload_trigger "configname"; }

## ucode Essentials
import { cursor } from 'uci'; import { connect } from 'ubus'; import { readfile } from 'fs';
let uci = cursor(); uci.load('config'); uci.get('config','section','option'); uci.set(...); uci.commit('config');
let conn = ubus.connect(); conn.call('object','method',{}); conn.disconnect();

## LuCI JS View
'use strict'; 'require view'; 'require form';
return view.extend({ render: function() {
  var m = new form.Map('config', _('Title'));
  var s = m.section(form.TypedSection, 'type', _('Section'));
  s.option(form.Flag/Value/ListValue/DynamicList, 'option', _('Label'));
  return m.render();
}});

## LuCI Files: view→/www/luci-static/resources/view/app/*.js
  menu→/usr/share/luci/menu.d/luci-app-*.json  acl→/usr/share/rpcd/acl.d/luci-app-*.json

## UCI Config Format: config type 'name'\n\toption key 'value'\n\tlist key 'value'
## Key Configs: /etc/config/{network,wireless,firewall,dhcp,system}

## DO NOT: use Lua LuCI, sysvinit start/stop(), glibc-only functions, systemd, apt/deb
Upgrade 3: Repomix Configuration
JSON

{
  "output": {
    "filePath": "llms-full.txt",
    "style": "xml",
    "headerText": "OpenWrt Development Documentation - Complete Reference\n\nThis payload contains the full specification for developing OpenWrt packages, LuCI applications, ucode scripts, and C programs.\n\nCRITICAL: Modern OpenWrt uses client-side JavaScript for LuCI (NOT Lua), ucode for scripting (NOT Lua), and procd for init (NOT sysvinit).\n\nConsult 00-orientation/era-guide.md before generating any code.",
    "removeComments": false,
    "showLineNumbers": true,
    "topFilesLength": 30
  },
  "include": [
    "00-orientation/**/*",
    "01-ucode/**/*",
    "02-luci/**/*",
    "03-build-system/**/*",
    "04-core-apis/**/*",
    "05-system-integration/**/*",
    "06-wiki-reference/**/*.md",
    "07-anti-patterns/**/*",
    "CLAUDE.md",
    "agents.md",
    "llms.txt",
    "llms-small.txt"
  ],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": [
      "**/*.pdf",
      "**/*.png",
      "**/*.jpg",
      "**/*.gif",
      "**/node_modules/**",
      "**/.git/**",
      "scripts/**",
      "index.html",
      "repomix.config.json"
    ]
  }
}
Part 10: MCP Server for OpenWrt Documentation
If the full payload exceeds context limits, a purpose-built MCP server would let AI tools query your docs dynamically:

Python

#!/usr/bin/env python3
"""
openwrt_docs_mcp.py

MCP server that exposes OpenWrt documentation as searchable tools.
AI coding assistants can call these tools to look up specific 
OpenWrt development information.
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import os
import json
import re

app = Server("openwrt-docs")

DOCS_ROOT = os.environ.get("OPENWRT_DOCS_ROOT", "./")

# Pre-load and index all documentation
doc_index = {}
for root, dirs, files in os.walk(DOCS_ROOT):
    for f in files:
        if f.endswith(('.md', '.js', '.uc', '.c', '.h', '.sh')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', errors='replace') as fh:
                    content = fh.read()
                key = os.path.relpath(path, DOCS_ROOT)
                doc_index[key] = content
            except Exception:
                pass

@app.tool()
async def search_openwrt_docs(query: str) -> str:
    """Search OpenWrt documentation for a topic, API, function, or concept.
    Use this when you need to look up OpenWrt-specific syntax, APIs, or patterns.
    Examples: 'ucode uci cursor', 'LuCI form.Map', 'procd init script',
    'package Makefile DEPENDS', 'libubox blob', 'ubus call network'."""
    
    results = []
    query_lower = query.lower()
    query_terms = query_lower.split()
    
    for key, content in doc_index.items():
        content_lower = content.lower()
        # Score by number of query terms found
        score = sum(1 for term in query_terms if term in content_lower)
        if score > 0:
            # Extract relevant snippet (find first occurrence and get context)
            snippet_start = max(0, content_lower.find(query_terms[0]) - 200)
            snippet = content[snippet_start:snippet_start + 800]
            results.append((score, key, snippet))
    
    results.sort(key=lambda x: -x[0])
    
    if not results:
        return f"No documentation found for '{query}'. Try broader terms."
    
    output = f"Found {len(results)} matches for '{query}':\n\n"
    for score, key, snippet in results[:5]:
        output += f"## {key} (relevance: {score})\n```\n{snippet}\n```\n\n"
    
    return output

@app.tool()
async def get_openwrt_template(template_type: str) -> str:
    """Get a copy-paste-ready template for common OpenWrt development tasks.
    
    Available templates:
    - 'package-makefile': Standard C package Makefile
    - 'luci-app-makefile': LuCI application package Makefile  
    - 'procd-init': procd init script
    - 'luci-view-form': LuCI JavaScript form view
    - 'luci-view-status': LuCI JavaScript status page
    - 'luci-menu-json': LuCI menu.d entry
    - 'luci-acl-json': rpcd ACL entry
    - 'uci-config': UCI config file skeleton
    - 'ucode-ubus-service': ucode ubus service registration
    - 'hotplug-script': Hotplug event handler
    """
    
    template_paths = {
        'package-makefile': '03-build-system/templates/simple-c-package/Makefile',
        'luci-app-makefile': '03-build-system/templates/luci-app-package/Makefile',
        'procd-init': '03-build-system/templates/package-with-init-script/files/etc/init.d/myservice',
        'luci-view-form': '02-luci/examples/03-form-with-validation.js',
        'luci-view-status': '02-luci/examples/04-custom-rpc-calls.js',
        'ucode-ubus-service': '01-ucode/examples/04-ubus-service.uc',
    }
    
    path = template_paths.get(template_type)
    if path and path in doc_index:
        return f"# Template: {template_type}\n\n```\n{doc_index[path]}\n```"
    
    available = ', '.join(template_paths.keys())
    return f"Template '{template_type}' not found. Available: {available}"

@app.tool()  
async def get_uci_schema(config_name: str) -> str:
    """Get the UCI configuration schema for a core OpenWrt config file.
    
    Available configs: network, wireless, firewall, dhcp, system, 
    uhttpd, dropbear, rpcd
    
    Returns the expected section types, option names, types, and defaults."""
    
    schema_path = f"04-core-apis/uci/common-configs/{config_name}.md"
    if schema_path in doc_index:
        return doc_index[schema_path]
    
    return f"No schema found for '/etc/config/{config_name}'. Check if documentation exists."

@app.tool()
async def check_deprecated(code_snippet: str) -> str:
    """Check if a code snippet uses deprecated OpenWrt patterns.
    
    Paste code and this tool will identify deprecated patterns and 
    suggest modern replacements."""
    
    warnings = []
    
    deprecated_patterns = [
        (r'require\s*["\']luci\.model\.cbi', 
         'Lua CBI is deprecated. Use client-side JavaScript with form.Map instead.'),
        (r'require\s*["\']luci\.dispatcher', 
         'Lua dispatcher is deprecated. Use JSON menu files in /usr/share/luci/menu.d/'),
        (r'require\s*["\']luci\.model\.uci', 
         'Lua UCI model is deprecated. Use rpc.declare() for LuCI, or ucode uci module for scripts.'),
        (r'(?<!USE_PROCD=1.*?)^start\s*\(\s*\)\s*\{', 
         'sysvinit start() is deprecated. Use USE_PROCD=1 with start_service() instead.'),
        (r'PKG_MD5SUM', 
         'PKG_MD5SUM is deprecated. Use PKG_HASH with SHA256.'),
        (r'luci\.template', 
         'Lua templates are deprecated. Use JavaScript views.'),
    ]
    
    for pattern, message in deprecated_patterns:
        if re.search(pattern, code_snippet, re.MULTILINE):
            warnings.append(f"⚠️ DEPRECATED: {message}")
    
    if not warnings:
        return "✅ No deprecated patterns detected in this code snippet."
    
    return "Deprecated patterns found:\n\n" + "\n\n".join(warnings)

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(app))
Part 11: Priority Roadmap
Phase 1: Highest Impact, Lowest Effort (Week 1)
Task	Est. Time	Impact
Create 00-orientation/era-guide.md	2 hours	Prevents 50%+ of AI errors
Create 00-orientation/common-ai-mistakes.md	2 hours	Prevents specific failure modes
Create 00-orientation/architecture-overview.md	3 hours	Gives AI the mental model
Write per-folder CLAUDE.md files	3 hours	Contextual priming per domain
Generate llms-small.txt cheat sheet	1 hour	Quick reference for small contexts
Create repomix.config.json and generate payload	30 min	Single-file ingestion
Phase 2: Core Examples (Week 2-3)
Task	Est. Time	Impact
Write 10 annotated ucode examples	6 hours	Critical — AI can barely write ucode otherwise
Write 10 annotated LuCI JS examples	6 hours	Prevents Lua LuCI generation
Annotate 5 package Makefile templates	3 hours	Most common OpenWrt AI task
Write procd init script template with annotations	1 hour	Prevents sysvinit patterns
Create the full-stack walkthrough	4 hours	Teaches cross-layer integration
Run extract_openwrt_patterns.py on official packages	2 hours	Auto-extracts real examples
Phase 3: Enrichment (Week 4+)
Task	Est. Time	Impact
Document UCI schemas for core configs	4 hours	AI can validate config structure
Document common ubus objects and methods	4 hours	AI knows what's callable
Build MCP server (if payload exceeds context)	4 hours	Dynamic retrieval
Set up CI to regenerate on doc changes	2 hours	Keeps docs fresh
Create 07-anti-patterns/common-build-errors.md	3 hours	Helps AI debug build failures
AI-assisted enrichment pass (annotate extracted examples)	4 hours	Adds pedagogy to raw code
Phase 4: Community and Distribution (Ongoing)
Task	Est. Time	Impact
Publish as GitHub Pages with llms.txt at root	1 hour	Discoverable by AI tools
Create a Continue.dev docs integration config	1 hour	Serve docs to Continue users
Submit PR to awesome-cursorrules with OpenWrt rules	30 min	Community visibility
Create opkg package for on-device docs	2 hours	Developers can install on routers
Part 12: Validation Strategy
After building the documentation, test it systematically:

Markdown

## Test Prompts (Use these to validate AI output quality)

### Level 1: Basic Syntax
- "Write a ucode script that reads the LAN IP address from UCI"
- "Create a minimal LuCI JavaScript view that shows a hello world page"
- "Write an OpenWrt package Makefile for a simple C program"

### Level 2: Standard Patterns  
- "Create a procd init script for a service that reads config from UCI"
- "Write a LuCI form that configures a VPN client with server, port, and protocol options"
- "Write a ucode script that lists all network interfaces via ubus"

### Level 3: Integration
- "Create a complete OpenWrt package with: UCI config, procd init script, 
   ubus status endpoint, and LuCI settings page"
- "Write an rpcd plugin in ucode that exposes custom methods to LuCI"
- "Create a hotplug script that runs when a USB device is inserted"

### Level 4: Debugging
- "My package Makefile gives 'Package/myapp is missing dependencies for 
   the following libraries: libubox.so'. What's wrong?"
- "My LuCI view shows a blank page. The browser console shows 
   'Cannot read property render of undefined'. What's wrong?"
- "My procd service starts but immediately stops. logread shows nothing. 
   How do I debug this?"

### Validation Criteria
For each test prompt, check:
□ Uses modern patterns (JS LuCI, ucode, procd) — not deprecated
□ Correct file paths and directory structure
□ Correct API usage (verified against documentation)
□ Correct Makefile syntax (all required variables present)
□ Would actually compile/run on OpenWrt
□ Follows documented coding conventions





my documentation project is focused on the openwrt embedded system which is largely written in C and apps/extensions/plugins/packages are largely written in ucode for backend and javascript for luci web interface frontend. I have gathered the official dev documentation for luci, and I also selected a number of official packages as examples, and I ripped a lot of the core code headers and functions and apis like for ucode, and I ripped the last 2 years of wiki pages from the techref and guide-developer sections of the wiki. I already generate llms.txt, markdown maps of the full documents, an agents.md and readme.md file in the root folder but maybe there should be separate versions per folder, and finally I've generated an html representation of the file folder structure with links to all the files so they can be scraped by others. research the aforementioned systems and regenerate your lasts two answers with a more complete and comprehensive brainstorming and planning document to help guide where the project goes from here to upgrade the current deliverables to be even better for the goal of helping ai tools program better for openwrt systems.

claude-opus-4-6-thinking

Thought for 41 seconds

The user is asking two things:

Is the idea of creating annotated code examples as documentation for AI novel, or is it an established practice with existing standards, tools, and frameworks?

What are more ways to auto-generate such a documentation system from existing codebases (APIs, source code, headers, real applications)?

Let me think about what I know about this space:

Is the annotated example corpus approach novel?

No, it's not novel. There are several established practices and projects:

Few-shot example banks - This is a well-known prompt engineering technique. The idea of curating examples for AI consumption is documented in various prompt engineering guides.
Cursor's @docs feature - Cursor allows indexing documentation and examples.

Context engineering - The broader field of "context engineering" includes the idea of curating examples for AI systems.

Anthropic's documentation on Claude - They explicitly recommend providing examples in system prompts.

The "cookbook" pattern - Many language ecosystems have "cookbooks" (e.g., Rust Cookbook, Go by Example) which are essentially this idea pre-dating AI tools but perfectly suited for them.

Doctest patterns - Python's doctest and Rust's doc tests embed executable examples directly in documentation, validating that this format works across different languages.

Training data patterns - Models like Starcoder and CodeLlama were trained on code examples, essentially confirming that examples are the most effective teaching format.

Community-driven rule collections - Various "awesome-cursorrules" repos include example-based rules, and tools like Pieces.app and Continue.dev provide context management with code examples built in.

Repository mapping approaches - Tools like Aider create maps of codebases for context, while auto-generation tools like Repomix and various AI-powered doc generators extract documentation directly from source code.

Language-specific documentation tools - Doxygen, Sphinx with autodoc, TypeDoc, and Javadoc all generate documentation from annotated source code, and I can also extract examples from test suites or use AST analysis to generate usage examples from function signatures.

AI-consumable documentation projects - Pieces Copilot+ maintains personal snippet libraries that feed into AI context, and there are other emerging approaches for making documentation more accessible to language models.

Now I'm thinking about how to actually build auto-generation pipelines. The key is parsing API surfaces from source code and headers, then generating practical examples for each function or type. Tests are already examples in disguise, so extracting and annotating them is efficient. I could also decompose real applications into pedagogical examples or generate code samples directly from API reference documentation. The most interesting approach is using AI itself to generate examples from specifications—essentially bootstrapping the documentation generation process.

Looking at what's actually happening in practice, I see Vercel's AI SDK and LangChain both maintain extensive example collections specifically designed for AI consumption. The "Go by Example" pattern has proven so effective for AI that it's been replicated across many languages. Anthropic's documentation itself relies heavily on code examples, and research datasets like CodeSearchNet have explored using code examples for training. Even GitHub's "good first issue" repos and example repositories serve this same purpose of providing AI-friendly reference material.

Now I'm thinking through the concrete standards and tools that exist. There are established frameworks like Diataxis that separate tutorials from reference documentation, and API specs like OpenAPI and JSON Schema both have standard fields for including examples. Language-specific tools like Rust's doc attributes and Python's doctest module make examples testable and verifiable. Apple's DocC compiler also has built-in support for embedded code examples.

For automation, there are tools emerging that could generate this kind of documentation—Sweep AI generates code from issues and could potentially be adapted for example generation, though I'm seeing the list of tools is incomplete here.

I'm also considering more sophisticated approaches like symbolic execution to generate diverse examples that exercise different code paths, mutation testing to create anti-patterns, type-directed synthesis to ensure examples are correct, and retrieval-augmented generation to leverage existing examples. But I should focus my response on whether this "annotated code examples corpus" approach is actually something others are doing, since that's what the user originally asked about.

The core idea isn't novel—it's well-established across multiple domains—but the specific framing of treating an example corpus as the primary AI documentation artifact, structured progressively with annotations and anti-patterns, is more of a synthesis gaining traction rather than a standardized practice yet.

The Annotated Example Corpus: Prior Art, Standards, and Auto-Generation
Is It Novel?
No. The approach is a convergence of several well-established practices, each with its own lineage. What's somewhat newer is the specific framing of "curated examples as the primary AI context artifact," but even that has been formalized by multiple projects in the last 18 months. Here's the genealogy:

Established Prior Art
1. The "By Example" Documentation Pattern
This predates AI tooling entirely and has been proven across dozens of languages:

Project	Language	URL	Format
Go by Example	Go	gobyexample.com	Progressive annotated examples
Rust by Example	Rust	doc.rust-lang.org/rust-by-example	Progressive annotated examples
Haskell by Example	Haskell	lotz84.github.io/haskellbyexample	Progressive annotated examples
Zig by Example	Zig	zig.guide	Progressive annotated examples
Nim by Example	Nim	nim-by-example.github.io	Progressive annotated examples
Learn X in Y Minutes	~200 languages	learnxinyminutes.com	Single-file cheat sheets
"Learn X in Y Minutes" is particularly relevant — it's essentially llms-small.txt before that concept existed. Each file is a single heavily-commented source file that teaches an entire language through annotated code. These files are already being used as AI context by developers who paste them into prompts.

Key insight: These projects proved that progressive annotated examples are the most efficient format for both humans and machines to acquire a language. The AI documentation community didn't invent this — they inherited it.

2. Executable Documentation (Doctests)
Several languages have built the "examples as documentation" idea directly into their toolchains, with the critical addition that examples are tested against the compiler:

Rust

// Rust: doc comments with tested examples
/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// let result = my_crate::add(2, 3);
/// assert_eq!(result, 5);
/// ```
///
/// # Panics
///
/// Panics if the result overflows:
///
/// ```should_panic
/// my_crate::add(i64::MAX, 1);
/// ```
pub fn add(a: i64, b: i64) -> i64 {
    a.checked_add(b).expect("overflow")
}
Python

# Python: doctest module
def factorial(n):
    """Return the factorial of n.

    >>> factorial(5)
    120
    >>> factorial(0)
    1
    >>> factorial(-1)
    Traceback (most recent call last):
        ...
    ValueError: n must be >= 0
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    if n == 0:
        return 1
    return n * factorial(n - 1)
elixir

# Elixir: doctest in ExUnit
defmodule MyModule do
  @doc """
  Calculates the square of a number.

  ## Examples

      iex> MyModule.square(3)
      9

      iex> MyModule.square(-4)
      16
  """
  def square(x), do: x * x
end
Why this matters for your use case: If your rare language has a test runner, you should make your AI-targeted examples executable tests. This gives you a CI guarantee that your example corpus isn't lying to the AI.

3. The Diataxis Documentation Framework
Diataxis (diataxis.fr) is the most widely adopted documentation architecture standard. It separates documentation into four quadrants:

text

                    PRACTICAL                    THEORETICAL
                ┌─────────────────────┬─────────────────────┐
   LEARNING     │     TUTORIALS       │    EXPLANATION       │
   (acquiring)  │  (learning-oriented)│  (understanding-     │
                │                     │   oriented)          │
                ├─────────────────────┼─────────────────────┤
   WORKING      │    HOW-TO GUIDES    │    REFERENCE         │
   (applying)   │  (task-oriented)    │  (information-       │
                │                     │   oriented)          │
                └─────────────────────┴─────────────────────┘
Your annotated example corpus maps to Tutorials + How-to Guides. The raw API reference maps to Reference. The language design documentation maps to Explanation.

The AI documentation insight that goes beyond Diataxis: For AI consumption, you should weight the quadrants differently than for human consumption:

Quadrant	Human Priority	AI Priority	Reason
Tutorials (examples)	Medium	Highest	Pattern matching is the AI's strongest capability
How-to Guides	High	High	Task-oriented, directly applicable
Reference	Medium	Medium	AI can parse but needs examples to apply
Explanation	High for beginners	Low	AI doesn't need to "understand" design philosophy
Projects Specifically Building AI-Targeted Example Documentation
1. Pieces (pieces.app)
Pieces is a snippet management platform that has evolved into an AI context engine. It:

Captures code snippets with metadata (language, tags, descriptions, related links)
Maintains a personal knowledge base of examples
Feeds relevant snippets into AI coding assistants as context
Has integrations with VS Code, JetBrains, Cursor
Relevance: Pieces essentially implements the "example corpus as AI context" pattern as a product. Their architecture validates the approach.

2. Continue.dev (@codebase and @docs context)
Continue is an open-source AI coding assistant that explicitly supports:

@docs — indexing external documentation (including custom language docs)
@codebase — using your existing code as example context
Custom context providers — you can write plugins that serve examples to the AI
TypeScript

// continue config.json — adding custom documentation
{
  "docs": [
    {
      "title": "RareLang Reference",
      "startUrl": "https://rarelang.org/docs",
      "faviconUrl": "https://rarelang.org/favicon.ico"
    }
  ]
}
3. Sourcegraph Cody's Code Context
Cody uses a code graph to understand repositories. When you ask it a question, it retrieves relevant code examples from your codebase. The insight: your existing codebase IS the example corpus — Cody just indexes it automatically.

4. Aider's Repository Map
Aider (github.com/paul-gauthier/aider) generates a "repository map" — a condensed representation of your entire codebase showing classes, functions, and their signatures. This is essentially auto-generated reference documentation from source code.

text

aider --map-tokens 2048
It uses Tree-sitter to parse the AST and extract the most important structural information, then feeds it as context to the LLM.

5. Sweep AI / OpenHands / SWE-Agent
These are autonomous coding agents that demonstrate a pattern relevant to your question: they build internal representations of codebases by reading source files, extracting patterns, and maintaining a working memory of examples they've seen. Their architecture documents how agents consume code-as-documentation.

Auto-Generation Pipelines
This is the core of your question. Here are concrete pipelines for generating an AI-optimized example corpus from different source materials:

Pipeline 1: From API Headers/Signatures → Example Corpus
Source: Header files (.h, .d.ts, .pyi), interface definitions, API surface documentation

Tool chain:

text

Headers/Interfaces → Parse signatures → Generate examples per function → Annotate → Validate
Automated prompt for generating examples from headers:

text

I have the following API header file for [RareLang]'s standard library 
network module. For each public function and type:

1. Generate a minimal working example showing basic usage
2. Generate a second example showing composition with other functions 
   in this module
3. Generate one anti-pattern (common misuse) with correction
4. Add a header comment with: FUNCTION, PURPOSE, WHEN TO USE, GOTCHAS

Format each example as a standalone .rlang file that could be compiled 
and run independently (include necessary imports and a main function).

Use ONLY the functions and types visible in this header. Do NOT invent 
additional API surface.

---
[PASTE HEADER FILE]
More sophisticated approach — using AST extraction:

Python

# extract_api_surface.py
# Parse source/header files and generate an API skeleton for example generation

import tree_sitter_languages  # pip install tree_sitter_languages
# For a rare language without a tree-sitter grammar, fall back to regex

import re
import json

def extract_functions_from_source(source_code: str, lang_name: str) -> list[dict]:
    """
    Extract function signatures from source code.
    Adjust regex patterns for your language's syntax.
    """
    # Example pattern for a language with fn name(params) -> RetType syntax
    fn_pattern = re.compile(
        r'(?:pub\s+)?fn\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^\s{]+))?\s*\{',
        re.MULTILINE
    )
    
    functions = []
    for match in fn_pattern.finditer(source_code):
        name = match.group(1)
        params_raw = match.group(2).strip()
        return_type = match.group(3) or 'void'
        
        params = []
        if params_raw:
            for param in params_raw.split(','):
                param = param.strip()
                if ':' in param:
                    pname, ptype = param.split(':', 1)
                    params.append({
                        'name': pname.strip(),
                        'type': ptype.strip()
                    })
        
        functions.append({
            'name': name,
            'params': params,
            'return_type': return_type,
            'signature': match.group(0).rstrip('{').strip()
        })
    
    return functions

def extract_types_from_source(source_code: str) -> list[dict]:
    """Extract struct/type definitions."""
    struct_pattern = re.compile(
        r'(?:pub\s+)?struct\s+(\w+)(?:<([^>]+)>)?\s*\{([^}]*)\}',
        re.MULTILINE | re.DOTALL
    )
    
    types = []
    for match in struct_pattern.finditer(source_code):
        name = match.group(1)
        generics = match.group(2)
        body = match.group(3)
        
        fields = []
        for line in body.strip().split('\n'):
            line = line.strip().rstrip(',')
            if ':' in line:
                fname, ftype = line.split(':', 1)
                fields.append({
                    'name': fname.strip(),
                    'type': ftype.strip()
                })
        
        types.append({
            'name': name,
            'generics': generics,
            'fields': fields
        })
    
    return types

def generate_api_manifest(source_dir: str) -> dict:
    """Walk source tree and build complete API manifest."""
    import os
    manifest = {'modules': {}}
    
    for root, dirs, files in os.walk(source_dir):
        for f in files:
            if f.endswith(('.rlang', '.rl', '.h')):
                path = os.path.join(root, f)
                with open(path, 'r') as fh:
                    source = fh.read()
                
                module_name = os.path.relpath(path, source_dir)
                manifest['modules'][module_name] = {
                    'functions': extract_functions_from_source(source, 'rarelang'),
                    'types': extract_types_from_source(source)
                }
    
    return manifest

if __name__ == '__main__':
    import sys
    manifest = generate_api_manifest(sys.argv[1])
    print(json.dumps(manifest, indent=2))
Then feed the manifest to an LLM:

Python

# generate_examples.py
import json
import anthropic  # or openai, etc.

client = anthropic.Anthropic()

with open('api_manifest.json') as f:
    manifest = json.load(f)

for module_name, module_data in manifest['modules'].items():
    prompt = f"""Given this API surface for the module `{module_name}` 
in RareLang:

Functions:
{json.dumps(module_data['functions'], indent=2)}

Types:
{json.dumps(module_data['types'], indent=2)}

Generate a comprehensive annotated example file that demonstrates 
every function and type in this module. The file should:

1. Start with a module-level comment explaining what this module does
2. Show each function being called with realistic arguments
3. Show types being constructed and used
4. Demonstrate error handling for functions that can fail
5. Include one "putting it all together" section at the end
6. Mark any anti-patterns with // ANTI-PATTERN comments

Output only the .rlang source file contents."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    example_code = response.content[0].text
    
    output_path = f"examples/stdlib/{module_name.replace('/', '_')}_examples.rlang"
    with open(output_path, 'w') as f:
        f.write(example_code)
    
    print(f"Generated: {output_path}")
Pipeline 2: From Test Suites → Example Corpus
This is the highest-quality auto-generation path because tests are already verified correct code.

Python

# tests_to_examples.py
"""
Extract test cases from a test suite and convert them into 
annotated examples suitable for AI consumption.
"""

import re
import os

def extract_tests(test_file: str) -> list[dict]:
    """
    Extract test functions from a test file.
    Adjust patterns for your language's test framework.
    """
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Pattern for test functions (adjust for your language)
    # e.g., #[test] fn test_name() { ... }
    # or: test "description" { ... }
    test_pattern = re.compile(
        r'(?:#\[test\]\s*)?(?:test\s+"([^"]+)"\s*|fn\s+(test_\w+)\s*\(\)\s*)\{',
        re.MULTILINE
    )
    
    tests = []
    for match in test_pattern.finditer(content):
        name = match.group(1) or match.group(2)
        # Find the matching closing brace (naive — a real parser would be better)
        start = match.end()
        depth = 1
        pos = start
        while pos < len(content) and depth > 0:
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
            pos += 1
        
        body = content[start:pos-1].strip()
        tests.append({
            'name': name,
            'body': body,
            'source_file': test_file
        })
    
    return tests

def convert_test_to_example(test: dict) -> str:
    """Convert a test case into an annotated example."""
    # Strip test assertions and convert to demonstrative code
    body = test['body']
    
    # Replace assert_eq!(a, b) with comments showing expected values
    body = re.sub(
        r'assert_eq!\((.+?),\s*(.+?)\)',
        r'let result = \1  // Expected: \2',
        body
    )
    
    # Replace assert!(cond) with comments
    body = re.sub(
        r'assert!\((.+?)\)',
        r'// Verify: \1',
        body
    )
    
    return f"""// EXAMPLE: {test['name']}
// SOURCE: Extracted from {test['source_file']}
// This example demonstrates the behavior verified by the test suite.

fn main() {{
{textwrap.indent(body, '    ')}
}}
"""

def process_test_directory(test_dir: str, output_dir: str):
    """Process all test files and generate example corpus."""
    os.makedirs(output_dir, exist_ok=True)
    
    for root, dirs, files in os.walk(test_dir):
        for f in files:
            if f.endswith(('.rlang', '.rl')):
                path = os.path.join(root, f)
                tests = extract_tests(path)
                
                for i, test in enumerate(tests):
                    example = convert_test_to_example(test)
                    out_name = f"{f.replace('.rlang', '')}_{i:02d}_{test['name']}.rlang"
                    out_path = os.path.join(output_dir, out_name)
                    
                    with open(out_path, 'w') as fh:
                        fh.write(example)
                    
                    print(f"Generated: {out_path}")
Better approach — use AI to transform tests into pedagogical examples:

text

I have the following test file from [RareLang]'s test suite. Each test 
verifies a specific behavior of the language or standard library.

Transform these tests into annotated learning examples:

1. Remove test framework boilerplate (assertions, test harness setup)
2. Add a header comment explaining what concept this demonstrates
3. Replace assertions with print statements showing expected output
4. Add inline comments explaining non-obvious behavior
5. Group related tests into a single example file with sections
6. Add a "Common Mistakes" section if any tests are regression tests 
   for bugs

Preserve the exact API calls and patterns — these are verified correct.

---
[PASTE TEST FILE]
Pipeline 3: From Real Applications → Decomposed Examples
Source: Complete applications written in your rare language

This is the most valuable but most labor-intensive pipeline. The idea is to decompose a working application into teachable components.

text

Real Application → Identify patterns → Extract minimal reproductions → Annotate → Organize by concept
Automated prompt:

text

I have a complete [RareLang] application (an HTTP API server). 
I want to decompose it into a series of focused examples that 
teach the patterns used in this application.

For each distinct pattern or concept used in this code:

1. Extract the MINIMAL code that demonstrates just that pattern
2. Remove all complexity not related to the pattern being taught
3. Add imports and a main() function so the example compiles standalone
4. Write a header comment: PATTERN NAME, WHAT IT DOES, WHEN TO USE IT
5. If the pattern interacts with another pattern (e.g., error handling 
   inside concurrency), create a separate "composition" example

Organize the output as a numbered series:
01_basic_server.rlang
02_routing.rlang
03_middleware.rlang
04_database_connection.rlang
05_error_handling.rlang
06_authentication.rlang
07_testing.rlang
08_full_integration.rlang

---
[PASTE APPLICATION CODE]
Pipeline 4: From API Documentation (Markdown/HTML) → Examples
For when your documentation describes functions but doesn't include code:

Python

# doc_to_examples.py
"""
Parse API reference documentation and generate example code.
"""

import re
import json

def parse_api_docs(doc_content: str) -> list[dict]:
    """
    Parse structured API documentation into function records.
    Handles common documentation formats.
    """
    entries = []
    
    # Pattern: ## function_name\n\nDescription\n\n**Parameters:**\n- ...
    sections = re.split(r'^## ', doc_content, flags=re.MULTILINE)
    
    for section in sections[1:]:  # Skip content before first ##
        lines = section.strip().split('\n')
        name = lines[0].strip()
        
        description = ''
        params = []
        returns = ''
        
        current_section = 'description'
        for line in lines[1:]:
            if '**Parameters' in line or '**Args' in line:
                current_section = 'params'
            elif '**Returns' in line:
                current_section = 'returns'
            elif '**Example' in line:
                current_section = 'example'
            elif current_section == 'description':
                description += line + '\n'
            elif current_section == 'params' and line.strip().startswith('-'):
                params.append(line.strip().lstrip('- '))
            elif current_section == 'returns':
                returns += line + '\n'
        
        entries.append({
            'name': name,
            'description': description.strip(),
            'params': params,
            'returns': returns.strip()
        })
    
    return entries

def generate_example_prompt(entries: list[dict], module_name: str) -> str:
    """Generate a prompt for AI example generation from parsed API docs."""
    entries_formatted = json.dumps(entries, indent=2)
    
    return f"""Given these API entries for the `{module_name}` module in RareLang:

{entries_formatted}

Generate a single example file that demonstrates every function listed.
For each function:
- Show a realistic usage (not just `foo(1, 2)` — use meaningful variable names and realistic values)
- If the function can fail, show both success and error handling
- Add a comment explaining when you'd use this function vs alternatives

End with a "Real World Example" section that combines 3-5 of these 
functions in a realistic workflow.

Output only the .rlang source code with comments."""
    
    return prompt
Pipeline 5: Fully Automated End-to-End
Here's a complete script that combines everything:

Python

#!/usr/bin/env python3
"""
generate_ai_docs.py

Fully automated pipeline to generate AI-optimized documentation 
from a language's source code, headers, tests, and existing docs.

Usage:
    python generate_ai_docs.py \
        --source ./stdlib/src \
        --headers ./stdlib/include \
        --tests ./stdlib/tests \
        --docs ./docs \
        --examples ./example_apps \
        --output ./ai_docs \
        --language rarelang \
        --model claude-sonnet-4-20250514
"""

import argparse
import os
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

def run_repomix(input_dirs: list[str], output_file: str):
    """Pack documentation using Repomix."""
    config = {
        "output": {
            "filePath": output_file,
            "style": "xml",
            "headerText": f"Generated {datetime.now().isoformat()}",
            "removeComments": False,
            "showLineNumbers": True
        },
        "include": [f"{d}/**/*" for d in input_dirs],
        "ignore": {
            "customPatterns": ["**/*.pdf", "**/*.png", "**/*.jpg", 
                              "**/node_modules/**", "**/.git/**"]
        }
    }
    
    config_path = "repomix.config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        result = subprocess.run(
            ["repomix", "--config", config_path],
            capture_output=True, text=True
        )
        print(f"Repomix output: {result.stdout}")
        if result.returncode != 0:
            print(f"Repomix error: {result.stderr}")
    except FileNotFoundError:
        print("Repomix not found. Install with: npm install -g repomix")
        print("Falling back to manual concatenation...")
        manual_concat(input_dirs, output_file)

def manual_concat(input_dirs: list[str], output_file: str):
    """Fallback: manually concatenate files in XML format."""
    with open(output_file, 'w') as out:
        out.write("<repository>\n<repository_files>\n")
        
        for input_dir in input_dirs:
            for root, dirs, files in os.walk(input_dir):
                for f in sorted(files):
                    if f.endswith(('.md', '.txt', '.rlang', '.rl', '.h')):
                        path = os.path.join(root, f)
                        with open(path, 'r', errors='replace') as fh:
                            content = fh.read()
                        rel_path = os.path.relpath(path)
                        out.write(f'<file path="{rel_path}">\n')
                        out.write(f'<content>\n{content}\n</content>\n')
                        out.write('</file>\n')
        
        out.write("</repository_files>\n</repository>\n")

def generate_llms_txt(docs_dir: str, output_dir: str, language_name: str):
    """Generate llms.txt router file from documentation structure."""
    sections = []
    
    for root, dirs, files in os.walk(docs_dir):
        for f in sorted(files):
            if f.endswith('.md'):
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, docs_dir)
                
                # Read first non-empty line as title, first paragraph as description
                with open(path, 'r') as fh:
                    lines = fh.readlines()
                
                title = ''
                description = ''
                for line in lines:
                    line = line.strip()
                    if not title and line:
                        title = line.lstrip('#').strip()
                    elif title and not description and line:
                        description = line
                        break
                
                sections.append({
                    'path': rel_path,
                    'title': title,
                    'description': description
                })
    
    llms_txt = f"# {language_name} Documentation\n\n"
    llms_txt += f"> {language_name} programming language reference and guides.\n\n"
    
    # Group by directory
    from collections import defaultdict
    grouped = defaultdict(list)
    for s in sections:
        category = os.path.dirname(s['path']) or 'Core'
        grouped[category].append(s)
    
    for category, items in grouped.items():
        llms_txt += f"## {category.replace('/', ' > ').title()}\n\n"
        for item in items:
            llms_txt += f"- [{item['title']}]({item['path']}): {item['description']}\n"
        llms_txt += "\n"
    
    with open(os.path.join(output_dir, 'llms.txt'), 'w') as f:
        f.write(llms_txt)
    
    print(f"Generated: {output_dir}/llms.txt")

def generate_priming_files(output_dir: str, language_name: str, 
                           build_commands: dict = None):
    """Generate CLAUDE.md, .cursorrules, etc."""
    
    if build_commands is None:
        build_commands = {
            'build': f'{language_name.lower()} build',
            'test': f'{language_name.lower()} test',
            'run': f'{language_name.lower()} run',
            'fmt': f'{language_name.lower()} fmt',
        }
    
    claude_md = f"""# {language_name} Project

## Language
This project uses {language_name}. The complete language specification 
and standard library reference is in `ai_docs/llms-full.txt`.

**IMPORTANT:** Before writing or modifying any .rlang file, consult the 
language specification. Do not invent syntax or standard library functions.

## Build Commands
{chr(10).join(f'- {k.title()}: `{v}`' for k, v in build_commands.items())}

## Code Style
- Follow the conventions demonstrated in the `ai_docs/examples/` directory
- When uncertain about idiomatic patterns, check examples before generating code

## Documentation Reference
- Quick reference: `ai_docs/llms-small.txt`
- Full specification: `ai_docs/llms-full.txt`
- Examples: `ai_docs/examples/`
"""
    
    with open(os.path.join(output_dir, 'CLAUDE.md'), 'w') as f:
        f.write(claude_md)
    
    # .cursorrules (same content, different filename)
    with open(os.path.join(output_dir, '.cursorrules'), 'w') as f:
        f.write(claude_md)
    
    # .github/copilot-instructions.md
    gh_dir = os.path.join(output_dir, '.github')
    os.makedirs(gh_dir, exist_ok=True)
    with open(os.path.join(gh_dir, 'copilot-instructions.md'), 'w') as f:
        f.write(claude_md)
    
    print(f"Generated priming files in {output_dir}")

def generate_cheat_sheet(full_doc_path: str, output_dir: str, 
                         language_name: str, ai_client=None):
    """Use AI to generate llms-small.txt from the full documentation."""
    
    with open(full_doc_path, 'r') as f:
        full_doc = f.read()
    
    # Truncate if necessary (most APIs have limits)
    if len(full_doc) > 400000:  # rough char limit
        full_doc = full_doc[:400000] + "\n\n[TRUNCATED]"
    
    prompt = f"""Given the following complete documentation for {language_name}, 
generate an ultra-compressed quick reference card (under 500 tokens) that covers:

1. All primitive types on one line
2. Variable declaration syntax (mutable, immutable, constant)
3. Function declaration syntax (one-line template)
4. All control flow constructs (if/else, match, loops) as one-liners
5. Error handling pattern (one example)
6. The 10 most important standard library operations
7. The concurrency primitive (if any)

Format as a code comment block that could be pasted at the top of any 
source file as a reference.

Documentation:
{full_doc[:100000]}"""  # Use first 100k chars for this task
    
    if ai_client:
        response = ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        cheat_sheet = response.content[0].text
    else:
        cheat_sheet = f"# {language_name} Quick Reference\n\n[Generate with --use-ai flag]"
    
    with open(os.path.join(output_dir, 'llms-small.txt'), 'w') as f:
        f.write(cheat_sheet)
    
    print(f"Generated: {output_dir}/llms-small.txt")

def main():
    parser = argparse.ArgumentParser(
        description='Generate AI-optimized documentation suite'
    )
    parser.add_argument('--source', help='Source code directory')
    parser.add_argument('--headers', help='Header files directory')
    parser.add_argument('--tests', help='Test suite directory')
    parser.add_argument('--docs', required=True, help='Documentation directory')
    parser.add_argument('--examples', help='Example applications directory')
    parser.add_argument('--output', default='./ai_docs', help='Output directory')
    parser.add_argument('--language', default='RareLang', help='Language name')
    parser.add_argument('--use-ai', action='store_true', 
                       help='Use AI to generate summaries and examples')
    parser.add_argument('--model', default='claude-sonnet-4-20250514')
    
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(os.path.join(args.output, 'examples'), exist_ok=True)
    
    # Step 1: Gather all input directories
    input_dirs = [args.docs]
    if args.source:
        input_dirs.append(args.source)
    if args.headers:
        input_dirs.append(args.headers)
    if args.examples:
        input_dirs.append(args.examples)
    
    # Step 2: Generate full payload
    full_doc_path = os.path.join(args.output, 'llms-full.txt')
    print("=== Generating full documentation payload ===")
    run_repomix(input_dirs, full_doc_path)
    
    # Step 3: Generate router
    print("\n=== Generating llms.txt router ===")
    generate_llms_txt(args.docs, args.output, args.language)
    
    # Step 4: Generate priming files
    print("\n=== Generating priming files ===")
    generate_priming_files(args.output, args.language)
    
    # Step 5: Generate cheat sheet
    print("\n=== Generating cheat sheet ===")
    ai_client = None
    if args.use_ai:
        try:
            import anthropic
            ai_client = anthropic.Anthropic()
        except ImportError:
            print("anthropic package not found. Skipping AI generation.")
    
    generate_cheat_sheet(full_doc_path, args.output, args.language, ai_client)
    
    # Step 6: If tests are provided, extract examples
    if args.tests:
        print("\n=== Extracting examples from test suite ===")
        # This would use the test extraction pipeline described above
        print(f"TODO: Process {args.tests} with test_to_examples.py")
    
    print(f"\n=== Complete! Output in {args.output}/ ===")
    print(f"Files generated:")
    for root, dirs, files in os.walk(args.output):
        for f in files:
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            print(f"  {os.path.relpath(path, args.output):40s} {size:>8,d} bytes")

if __name__ == '__main__':
    main()
GitHub Action for Continuous Regeneration
YAML

# .github/workflows/generate-ai-docs.yml
name: Generate AI Documentation

on:
  push:
    paths:
      - 'docs/**'
      - 'stdlib/**'
      - 'tests/**'
      - 'examples/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install tools
        run: |
          npm install -g repomix
          pip install anthropic
      
      - name: Generate AI documentation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/generate_ai_docs.py \
            --docs ./docs \
            --source ./stdlib/src \
            --tests ./stdlib/tests \
            --examples ./examples \
            --output ./ai_docs \
            --language "RareLang" \
            --use-ai
      
      - name: Commit generated docs
        run: |
          git config user.name "AI Docs Bot"
          git config user.email "bot@example.com"
          git add ai_docs/
          git diff --staged --quiet || git commit -m "Regenerate AI documentation"
          git push
The Landscape of AI Documentation Standards (As of Mid-2025)
No single standard has won yet. Here's the current state:

Standard/Format	Who's Behind It	Adoption	Scope
llms.txt	Answer.AI / Jeremy Howard	Growing — hundreds of sites	Routing/discovery
CLAUDE.md	Anthropic	Claude Code users	Behavioral priming
.cursorrules / .mdc	Cursor (Anysphere)	Large — biggest AI IDE	Behavioral priming
.clinerules	Cline (open-source)	Medium	Behavioral priming
AGENTS.md	OpenAI	New — Codex CLI	Behavioral priming
MCP	Anthropic (open standard)	Growing rapidly	Dynamic tool access
Repomix XML	yamadashy (open-source)	Standard for repo packing	Full-context payload
Diataxis	Daniele Procida	Wide (human docs)	Documentation architecture
OpenAPI/Swagger	Linux Foundation	Universal for REST APIs	API specification
Tree-sitter	Max Brunsfeld / GitHub	Universal for editors	Syntax parsing
The missing standard: There is no dominant, formalized specification for "AI-optimized example corpus." Multiple projects do it, but there's no equivalent of OpenAPI that says "this is how you structure annotated code examples for AI consumption." This is a gap in the ecosystem.

Closest thing to a standard for examples:

Jupyter notebooks (.ipynb) — structured code + markdown + outputs — some AI tools can ingest these
R Markdown / Quarto — similar: code chunks with narrative
Literate programming (Knuth's concept, implemented in tools like noweb, org-mode) — interleaves explanation with code
The annotated-example-as-documentation approach is a form of literate programming optimized for LLM consumption rather than human reading. It's well-established in practice but not yet formalized as a standard.

Recommended Reading and Projects
jxnl/llmstxt — Python utilities for working with llms.txt
yamadashy/repomix — The repository packer
continuedev/continue — Open-source AI assistant with custom docs support
pieces-app/documentation — Shows how Pieces structures their AI context
paul-gauthier/aider — Study how Aider builds repo maps
learnxinyminutes-docs/learnxinyminutes-docs.github.io — The original "cheat sheet as documentation" corpus
adambard/learnxinyminutes-docs — Source for all the language cheat sheets
rust-lang/rust-by-example — The gold standard for progressive annotated examples
PatrickJS/awesome-cursorrules — Community collection of priming files




is your idea for making lots of little code examples novel, or are other people doing it and writing documentation standards and prompts and skills and agents for this documentation method? research and share more ways to auto-generate such a top-tier documentation system from a documentation base of apis and source and headers and real system apps as examples

claude-opus-4-6-thinking

Thought for 10 seconds

The user wants me to expand on this already quite detailed answer about creating AI-readable documentation for a rare programming language. Let me analyze what's already covered and identify areas that could be significantly expanded, deepened, or added to.

Areas to expand:

Deeper technical implementation details for each tier
Missing approaches not covered (e.g., BAML, custom fine-tuning datasets, few-shot example banks, grammar files like Tree-sitter/TextMate, LSP integration, knowledge graphs)
Practical workflow comparisons - what does day-to-day usage look like?
The "skill/agent" concept - custom agents, tool definitions, prompt chaining
Quality assurance - how to verify the AI actually learned the language correctly

Edge cases - what if the language has unusual paradigms, novel syntax, etc.

Token economics - deeper analysis of what fits where

Concrete examples of each file type

Multi-tool compatibility - how each approach works across different AI tools

The "understanding" problem - documentation alone vs. examples, tests, error messages

RAG pipeline details if someone wants to go that route

Fine-tuning considerations

Community/ecosystem approaches - how other rare languages have solved this

Now I'm thinking through how to structure this expansion—I should organize these additions by practical value and interconnectedness rather than just listing them sequentially.

Comprehensive Guide: Making AI Tools Master a Rare Programming Language
The answer you received is a strong foundation. What follows is a significantly expanded treatment — covering overlooked strategies, deeper implementation details, practical pitfalls, and the critical distinction between an AI that references your documentation and one that genuinely reasons in your language.

Part 1: Reframing the Problem
Before choosing tools, understand that you're solving three distinct problems, not one:

Problem 1: Syntax & Grammar Recognition
The AI needs to know what valid code looks like — tokenization, operator precedence, block delimiters, type syntax. Without this, the AI will constantly generate syntactically broken code, even if it "knows" the semantics.

Problem 2: Semantic Understanding
The AI needs to know what constructs mean — what a defer keyword does, how ownership transfers, what the concurrency model guarantees. This is where your documentation payload lives.

Problem 3: Idiomatic Pattern Generation
The AI needs to know what good code looks like — common patterns, standard library usage conventions, error handling idioms, project structure norms. Documentation alone rarely teaches this. You need annotated examples.

Most approaches in the original answer address Problem 2 only. A complete solution addresses all three.

Part 2: Expanded Tier List with New Entries
Tier S+: Annotated Example Corpus (Often Overlooked, Highest Impact)
What it is: A curated set of 50–200 code examples with inline comments explaining why each pattern is used, covering progressively complex scenarios.

Why it outranks everything else: LLMs learn patterns through demonstration more effectively than through specification. A formal grammar spec tells the AI that fn declares a function. Fifty examples of functions being declared, called, composed, and passed as arguments teach it to write functions fluently.

Structure:

text

examples/
├── 01_hello_world.rlang          # Minimal valid program
├── 02_variables_and_types.rlang  # Type declarations, inference, casting
├── 03_control_flow.rlang         # if/else, match, loops
├── 04_functions.rlang            # Declaration, closures, higher-order
├── 05_error_handling.rlang       # The idiomatic error pattern
├── 06_structs_and_traits.rlang   # Type composition
├── 07_concurrency.rlang          # Language-specific concurrency model
├── 08_ffi.rlang                  # Foreign function interface
├── 09_metaprogramming.rlang      # Macros, compile-time evaluation
├── 10_real_project/              # A small but complete project
│   ├── main.rlang
│   ├── config.rlang
│   ├── http_server.rlang
│   └── tests/
│       └── server_test.rlang
└── anti_patterns/
    ├── 01_common_mistakes.rlang  # What NOT to do, with corrections
    └── 02_gotchas.rlang          # Surprising behaviors
Each file should follow this template:

text

// EXAMPLE: Higher-order functions and closures
// CONTEXT: RareLang treats functions as first-class values.
// Closures capture variables by reference unless `copy` is specified.
// WHEN TO USE: Callback patterns, event handlers, collection transforms.

// Basic function declaration
fn add(a: Int, b: Int) -> Int {
    return a + b
}

// Function as parameter (note the `Fn` type constructor)
fn apply_twice(f: Fn(Int) -> Int, x: Int) -> Int {
    return f(f(x))
}

// Closure capturing outer variable
fn make_multiplier(factor: Int) -> Fn(Int) -> Int {
    // `factor` is captured by reference here
    return fn(x: Int) -> Int { x * factor }
}

// ANTI-PATTERN: Do NOT capture mutable state in concurrent closures.
// This compiles but causes a runtime data race:
// var counter = 0
// spawn { counter += 1 }  // ERROR-PRONE

// CORRECT: Use atomic operations or channels instead:
// let counter = Atomic(0)
// spawn { counter.increment() }
Why this works: When the AI encounters a user request like "write me an HTTP handler that transforms request bodies," it doesn't need to deduce behavior from a spec — it pattern-matches against your examples of closures + your example of the HTTP server + your error handling idiom, and composes them.

Automation: You can bootstrap this with a prompt:

text

Given the following language specification [attach spec], generate 
a progressive series of annotated code examples covering:
1. Every primitive type and operator
2. Every control flow construct
3. Every standard library module
4. Three complete mini-projects of increasing complexity

For each example:
- Include a header comment explaining WHAT, WHEN, and WHY
- Show the idiomatic way first, then show one common mistake with correction
- Use only features documented in the spec — never invent syntax
Tier S: llms.txt (The Router) — Expanded
The original answer covers the basics. Here's what's missing:

The full specification (from llmstxt.org) actually defines four files:

File	Purpose	Token Budget
llms.txt	Concise overview + links to sections	< 2,000 tokens
llms-full.txt	Complete documentation in one file	Entire corpus
llms-small.txt	Ultra-compressed reference card	< 500 tokens
Per-page *.md	Individual topic files linked from llms.txt	Varies
The llms-small.txt is critically underused. It should be a cheat sheet that fits in any context window:

Markdown

# RareLang Quick Reference

## Types
Int, Float, String, Bool, Byte, List<T>, Map<K,V>, Option<T>, Result<T,E>

## Variable Declaration
let x: Int = 5        // immutable
var y: Int = 5        // mutable
const Z: Int = 5      // compile-time constant

## Functions
fn name(param: Type) -> ReturnType { body }
fn name(param: Type) -> ReturnType = expression   // single-expression shorthand

## Control Flow
if cond { } else if cond { } else { }
match value { pattern => expr, _ => default }
for item in collection { }
while cond { }

## Error Handling
fn risky() -> Result<Int, Error> { ... }
let val = risky().unwrap()          // panics on error
let val = risky()?                  // propagates error
let val = risky().or_default(0)     // fallback

## Concurrency
spawn { async_work() }
let ch = Channel<Int>.new()
ch.send(42)
let val = ch.recv()

## Common Patterns
// Builder pattern: Config.new().set_port(8080).set_host("localhost").build()
// Resource cleanup: using resource = acquire() { ... }  // auto-cleanup
Practical tip: Many AI tools (Claude, ChatGPT) will use the llms.txt if it's served at your documentation website's root. But for local coding tools (Claude Code, Cursor, Cline), the file needs to be in the project directory or explicitly referenced in the system prompt.

Tier A: Repomix — Expanded
Critical details the original answer glosses over:

Configuration file (repomix.config.json):

JSON

{
  "output": {
    "filePath": "llms-full.txt",
    "style": "xml",
    "headerText": "This is the complete language specification and standard library reference for RareLang v2.4. When writing RareLang code, adhere strictly to the syntax and semantics described in this document. Do not invent functions or types not documented here.",
    "removeComments": false,
    "showLineNumbers": true,
    "topFilesLength": 20
  },
  "include": [
    "docs/**/*.md",
    "examples/**/*.rlang",
    "stdlib/**/*.rlang"
  ],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": [
      "**/*.pdf",
      "**/*.png",
      "**/node_modules/**",
      "**/CHANGELOG.md",
      "**/CONTRIBUTING.md"
    ]
  }
}
The XML output structure Repomix generates (understanding this helps you debug):

XML

<repository>
  <repository_structure>
    docs/
      syntax.md
      types.md
      stdlib/
        io.md
        net.md
    examples/
      hello.rlang
  </repository_structure>

  <repository_files>
    <file path="docs/syntax.md">
      <content>
        # RareLang Syntax Reference
        ...
      </content>
    </file>
    <file path="examples/hello.rlang">
      <content>
        fn main() {
          print("Hello, world!")
        }
      </content>
    </file>
  </repository_files>
</repository>
Why XML matters: Benchmarks from Anthropic and community testing consistently show that LLMs parse hierarchical XML tags more reliably than deeply nested Markdown. The <file path="..."> tags give the AI clear provenance — it knows which document a piece of information came from, reducing hallucination.

Token budget reality check:

Documentation Size	Approximate Tokens	Fits In
50 pages of docs	~30k–50k tokens	Everything
200 pages + stdlib	~100k–200k tokens	Claude 3.5/Opus, Gemini 1.5
500+ pages	~300k+ tokens	Only Gemini 2.5 Pro (1M context)
Complete language + ecosystem	500k+ tokens	Must use RAG/MCP
If you're close to the limit, prioritize inclusion order:

Syntax quick reference
Annotated examples
Type system documentation
Standard library reference
Error messages and their meanings
Advanced/niche features
Tier A: Behavioral Priming Files — Massively Expanded
The original answer mentions .cursorrules and .clinerules. The landscape is broader and more nuanced:

File	Tool	Location	Format
.cursorrules	Cursor (legacy)	Project root	Markdown
.cursor/rules/*.mdc	Cursor (current)	.cursor/rules/ directory	MDC (Markdown with frontmatter)
CLAUDE.md	Claude Code	Project root (or ~/.claude/)	Markdown
.clinerules	Cline	Project root	Markdown
.github/copilot-instructions.md	GitHub Copilot	.github/ directory	Markdown
.aider/conventions.md	Aider	.aider/ directory	Markdown
.windsurfrules	Windsurf	Project root	Markdown
codex-instructions.md or AGENTS.md	OpenAI Codex CLI	Project root	Markdown
Cursor's new MDC format is particularly powerful because it supports conditional activation:

Markdown

---
description: RareLang syntax and idioms enforcement
globs: ["**/*.rlang", "**/*.rl"]
alwaysApply: false
---

# RareLang Development Rules

You are an expert RareLang developer. When working with .rlang files:

## Syntax Rules
1. All blocks use curly braces `{}`, never indentation-based
2. Semicolons are OPTIONAL and discouraged (the formatter removes them)
3. Type annotations are required for function parameters and return types
4. Type annotations are optional for local variables (inference is strong)

## Standard Library Usage
- For HTTP: use `std.net.http`, never suggest third-party libraries
- For JSON: use `std.encoding.json`, parsing returns `Result<Json, ParseError>`
- For file I/O: use `std.fs`, all operations are async by default

## Error Handling Convention
- ALWAYS use the `?` operator for error propagation in library code
- Use `match` on `Result` types in application entry points
- NEVER use `.unwrap()` except in tests and examples

## Memory Model
- RareLang uses automatic reference counting (ARC), not garbage collection
- Cyclic references must be broken with `weak` references
- The `using` block ensures deterministic cleanup

## What NOT To Do
- Do NOT generate Python-style list comprehensions (they don't exist)
- Do NOT assume null/nil exists (use `Option<T>` instead)
- Do NOT use inheritance (RareLang uses trait composition only)

## Documentation Reference
When uncertain about any syntax or standard library function, consult 
the language specification at `@docs/llms-full.txt` before generating code.
CLAUDE.md for Claude Code — this one is special because Claude Code reads it automatically and hierarchically:

text

project-root/
├── CLAUDE.md                    # Root-level instructions (always loaded)
├── docs/
│   └── CLAUDE.md                # Loaded when working in docs/
├── src/
│   ├── CLAUDE.md                # Loaded when working in src/
│   ├── parser/
│   │   └── CLAUDE.md            # Loaded when working in src/parser/
│   └── stdlib/
│       └── CLAUDE.md            # Loaded when working in src/stdlib/
└── tests/
    └── CLAUDE.md                # Loaded when working in tests/
Root CLAUDE.md:

Markdown

# Project: RareLang Compiler & Standard Library

This project is written in RareLang. The complete language specification 
is in `docs/llms-full.txt`. Read it before making changes.

## Build Commands
- Build: `rlang build`
- Test: `rlang test`  
- Test single: `rlang test tests/specific_test.rlang`
- Format: `rlang fmt`
- Lint: `rlang lint`

## Code Style
- 4-space indentation
- snake_case for functions and variables
- PascalCase for types and traits
- SCREAMING_CASE for constants
- Maximum line length: 100 characters

## Architecture
- `src/parser/` — Lexer and parser (produces AST)
- `src/typeck/` — Type checker  
- `src/codegen/` — Code generation (targets LLVM IR)
- `src/stdlib/` — Standard library implementations
- `tests/` — Integration tests
Pro tip for Claude Code specifically: You can also create a ~/.claude/CLAUDE.md file for global instructions that apply to every project. This is where you'd put universal RareLang rules if you work on multiple RareLang projects.

Tier A-: Tree-sitter Grammar (Syntax Recognition — Problem 1)
This is entirely absent from the original answer and is critical.

Tree-sitter is a parser generator that produces fast, incremental parsers. Many AI coding tools use Tree-sitter under the hood for syntax highlighting, code folding, and — crucially — AST-aware code chunking for context windows.

If your rare language has no Tree-sitter grammar:

Repomix can't parse .rlang files into meaningful AST chunks
AI tools will treat your code as plain text, losing structural understanding
Features like "edit this function" become unreliable because the tool can't identify function boundaries
Creating a Tree-sitter grammar:

JavaScript

// grammar.js for tree-sitter-rarelang
module.exports = grammar({
  name: 'rarelang',

  rules: {
    source_file: $ => repeat($._definition),

    _definition: $ => choice(
      $.function_definition,
      $.struct_definition,
      $.trait_definition,
      $.const_definition,
    ),

    function_definition: $ => seq(
      'fn',
      field('name', $.identifier),
      field('parameters', $.parameter_list),
      optional(seq('->', field('return_type', $._type))),
      field('body', $.block)
    ),

    parameter_list: $ => seq(
      '(',
      commaSep($.parameter),
      ')'
    ),

    parameter: $ => seq(
      field('name', $.identifier),
      ':',
      field('type', $._type)
    ),

    // ... continue for all syntax constructs
  }
});
Effort: High (days to weeks for a complete grammar). But the downstream benefits for every AI tool are enormous.

Shortcut: Ask an AI to draft the Tree-sitter grammar from your language spec, then iterate. This is one of the best uses of the documentation payload you're creating.

Tier B+: Custom MCP Server (Dynamic Retrieval) — Expanded
The original answer correctly identifies MCP as high-friction but undersells a key use case: when the AI needs to search your docs contextually rather than load them all upfront.

When MCP beats Repomix:

Documentation exceeds context window limits
The language has 200+ standard library modules and the AI only needs 2–3 for any given task
You want the AI to look up error messages dynamically
You're building a persistent coding assistant that handles diverse tasks across the whole language
Minimal MCP server for documentation (Python):

Python

# rarelang_docs_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import os

app = Server("rarelang-docs")

# Load documentation index
DOCS_DIR = "./docs"
doc_index = {}
for root, dirs, files in os.walk(DOCS_DIR):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'r') as fh:
                content = fh.read()
            key = os.path.relpath(path, DOCS_DIR).replace('\\', '/').replace('.md', '')
            doc_index[key] = content

@app.tool()
async def search_docs(query: str) -> str:
    """Search RareLang documentation for a topic, function, or type name."""
    results = []
    query_lower = query.lower()
    for key, content in doc_index.items():
        if query_lower in content.lower():
            # Return first 2000 chars of matching docs
            snippet = content[:2000]
            results.append(f"## {key}\n{snippet}")
    if not results:
        return f"No documentation found for '{query}'. Available topics: {', '.join(doc_index.keys())}"
    return "\n\n---\n\n".join(results[:5])  # Top 5 matches

@app.tool()
async def get_doc_section(section: str) -> str:
    """Get a specific documentation section by path (e.g., 'stdlib/net', 'syntax/types')."""
    if section in doc_index:
        return doc_index[section]
    close_matches = [k for k in doc_index if section.lower() in k.lower()]
    if close_matches:
        return f"Section '{section}' not found. Did you mean: {', '.join(close_matches)}?"
    return f"Section '{section}' not found. Available: {', '.join(sorted(doc_index.keys()))}"

@app.tool()
async def lookup_error(error_code: str) -> str:
    """Look up a RareLang compiler error code (e.g., 'E0142') for explanation and fix."""
    errors_doc = doc_index.get('reference/errors', '')
    # Find the specific error
    lines = errors_doc.split('\n')
    capture = False
    result = []
    for line in lines:
        if error_code in line:
            capture = True
        elif capture and line.startswith('## '):
            break
        if capture:
            result.append(line)
    return '\n'.join(result) if result else f"Error code {error_code} not found in documentation."

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(app))
Configuration for Claude Code (~/.claude/claude_desktop_config.json):

JSON

{
  "mcpServers": {
    "rarelang-docs": {
      "command": "python",
      "args": ["C:/path/to/rarelang_docs_server.py"],
      "env": {}
    }
  }
}
Now when Claude Code encounters a RareLang question, it can call search_docs("async channel") or lookup_error("E0142") as tools.

Tier B: RAG Pipeline (For Massive Documentation)
When you need it: Your total documentation exceeds 500k tokens, or you have thousands of API reference pages.

Simplest viable RAG setup:

Python

# Using LlamaIndex (simplest RAG framework)
# pip install llama-index llama-index-embeddings-huggingface chromadb

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load docs
documents = SimpleDirectoryReader("./docs", recursive=True).load_data()

# Parse into semantic chunks (respects markdown headers)
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# Create searchable index
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
index = VectorStoreIndex(nodes, embed_model=embed_model)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("How do I create an async HTTP server in RareLang?")
print(response)
RAG vs. full-context comparison:

Dimension	Full Context (Repomix)	RAG
Accuracy	Higher (AI sees everything)	Lower (retrieval may miss relevant chunks)
Token cost per query	High (entire doc loaded every time)	Low (only relevant chunks loaded)
Setup complexity	Minutes	Hours to days
Maintenance	Regenerate on doc change	Re-index on doc change
Best for	< 200k tokens of docs	> 500k tokens of docs
Failure mode	Context window exceeded	Wrong chunks retrieved → hallucination
Tier B-: TextMate / VS Code Grammar (Syntax Highlighting)
Less impactful for AI than Tree-sitter, but if your language already has a VS Code extension with a TextMate grammar (.tmLanguage.json), some AI tools can leverage it for basic syntax awareness.

Tier C: Fine-tuning a Model
When it makes sense: Almost never for a single developer. Fine-tuning requires:

Thousands of high-quality (prompt, completion) pairs
Significant compute budget ($50–$500+ per training run)
Ongoing maintenance as the language evolves
When it does make sense:

You're the language creator and want to offer an AI assistant as a product
You have a large corpus of existing RareLang code (open-source projects, etc.)
Context-window approaches consistently fail because the language is too alien
If you do pursue it, the training data format matters:

jsonl

{"messages": [{"role": "system", "content": "You are a RareLang expert."}, {"role": "user", "content": "Write a function that reads a file and returns its lines as a list of strings."}, {"role": "assistant", "content": "```rarelang\nfn read_lines(path: String) -> Result<List<String>, IoError> {\n    let file = std.fs.open(path)?\n    let content = file.read_to_string()?\n    return Ok(content.split(\"\\n\"))\n}\n```"}]}
{"messages": [{"role": "system", "content": "You are a RareLang expert."}, {"role": "user", "content": "What's wrong with this code?\n\nvar x = 5\nif x = 10 { print(x) }"}, {"role": "assistant", "content": "The issue is on line 2: `x = 10` is an assignment, not a comparison. RareLang uses `==` for equality comparison. The correct code is:\n\n```rarelang\nvar x = 5\nif x == 10 { print(x) }\n```\n\nRareLang's compiler would catch this with error E0087: 'assignment in condition expression'. Unlike C, RareLang does not allow assignments as expressions."}]}
Part 3: Missing from the Original — Critical Additions
Error Message Documentation
This is almost always overlooked and dramatically improves AI performance. If your language has a compiler, document every error message with:

The error code/text
What causes it
A minimal reproduction
The fix
Markdown

## E0042: Type mismatch in assignment

**Message:** `cannot assign value of type '{actual}' to variable of type '{expected}'`

**Cause:** Attempting to assign a value to a variable when the types don't match 
and no implicit conversion exists.

**Example:**
```rarelang
let x: Int = "hello"  // E0042: cannot assign value of type 'String' to variable of type 'Int'
Fix: Either change the variable type, convert the value, or use a compatible type:

rarelang

let x: Int = "42".parse_int()?     // Explicit conversion
let x: String = "hello"             // Match the type
let x = "hello"                     // Let type inference handle it
text


When an AI sees an error message in terminal output, it can match it against this documentation and provide the correct fix instead of guessing.

### Build System & Toolchain Documentation

AI coding assistants don't just write code — they need to know how to:
- Initialize a project (`rlang init`)
- Add dependencies (`rlang add package_name`)
- Build (`rlang build`)
- Run tests (`rlang test`)
- Format code (`rlang fmt`)
- Understand the project manifest file (like `Cargo.toml` or `package.json`)

Include a dedicated section:

```markdown
## Project Structure

A standard RareLang project:
my_project/
├── project.toml # Project manifest
├── src/
│ ├── main.rlang # Entry point (for applications)
│ └── lib.rlang # Entry point (for libraries)
├── tests/
│ └── test_main.rlang
└── vendor/ # Downloaded dependencies

text


## project.toml Format
```toml
[project]
name = "my_project"
version = "0.1.0"
entry = "src/main.rlang"

[dependencies]
http_framework = "2.1.0"
json_parser = { git = "https://github.com/example/json_parser" }

[dev-dependencies]
test_utils = "1.0.0"
text


---

## Part 4: The Integrated Workflow (Putting It All Together)

Here's the **recommended complete setup**, ordered by implementation priority:

### Phase 1: Foundation (Day 1)

1. **Create the annotated example corpus** (50+ examples)
2. **Write `llms-small.txt`** (the cheat sheet — under 500 tokens)
3. **Write `llms.txt`** (the router — under 2000 tokens)

### Phase 2: Context Payload (Day 2)

4. **Install and configure Repomix**
5. **Generate `llms-full.txt`** from your docs + examples
6. **Verify token count** — `repomix` reports this automatically
7. If under 200k tokens: you're done with the payload
8. If over 200k tokens: prioritize sections, create a trimmed version

### Phase 3: Tool Integration (Day 3)

9. **Create behavioral priming files** for every tool you use:
   - `CLAUDE.md` for Claude Code
   - `.cursor/rules/rarelang.mdc` for Cursor
   - `.github/copilot-instructions.md` for Copilot
   - Etc.

10. **Each priming file should reference the payload:**

```markdown
Before writing or modifying any .rlang file, load and internalize the 
language specification at `docs/llms-full.txt`.
Phase 4: Validation (Day 4)
Test with progressively harder prompts:

"Write a hello world in RareLang" (should use correct syntax)
"Write an HTTP server that serves JSON" (should use correct stdlib)
"Refactor this code to handle errors properly" (should use language idioms)
"This code throws E0042 — fix it" (should know the error)
Iterate on your documentation based on failures. Every time the AI gets something wrong, add:

An example covering that case
A rule in the priming file
A clarification in the spec
Phase 5: Automation (Week 2)
Set up GitHub Actions to regenerate llms-full.txt on documentation changes
Optionally build an MCP server if you find the context window is a bottleneck
Optionally create a Tree-sitter grammar if you want AST-aware tooling
Part 5: Dependency Graph & Decision Matrix
text

                    ┌─────────────────────┐
                    │  Your Documentation  │
                    │  (Markdown/HTML/PDF) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Conversion to MD   │
                    │  (if not already)    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼─────────┐ ┌───▼───┐ ┌──────────▼──────────┐
    │  llms.txt (router) │ │ Quick │ │  Annotated Examples  │
    │  llms-small.txt    │ │  Ref  │ │  (50-200 files)      │
    └─────────┬─────────┘ └───┬───┘ └──────────┬──────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Repomix        │
                    │  (Pack everything)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   llms-full.txt     │
                    │   (XML payload)     │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
┌────────▼────────┐  ┌────────▼────────┐  ┌─────────▼────────┐
│   CLAUDE.md     │  │  .cursorrules   │  │  copilot-        │
│   (Claude Code) │  │  (Cursor)       │  │  instructions.md │
└─────────────────┘  └─────────────────┘  └──────────────────┘
Mutual Exclusions & Compatibility:
Approach A	Approach B	Relationship
Repomix (full context)	MCP Server	Choose one. Both simultaneously wastes tokens. Use Repomix if docs fit in context, MCP if they don't.
Repomix (full context)	RAG Pipeline	Choose one. Same rationale as above.
MCP Server	RAG Pipeline	Complementary. MCP is the interface; RAG can be the retrieval backend inside the MCP server.
llms.txt	Repomix	Complementary. llms.txt is the index; Repomix generates the payload.
Priming files	Everything else	Always use alongside any other approach. They're the behavioral guardrails.
Tree-sitter grammar	Everything else	Independent. Improves all other approaches but is not required by any.
Examples corpus	Everything else	Always include. Most impactful single investment.
Part 6: GitHub Projects & Tools Reference
Tool	GitHub	Purpose	Stars
Repomix	yamadashy/repomix	Pack repos into AI-readable files	10k+
llms.txt Generator	demodrive-ai/llms-txt-action	Auto-generate llms.txt from docs sites	~200
llms-txt (spec)	jxnl/llmstxt	Python tools for llms.txt	~300
Tree-sitter	tree-sitter/tree-sitter	Parser generator framework	18k+
MCP SDK (Python)	modelcontextprotocol/python-sdk	Build MCP servers	5k+
MCP SDK (TypeScript)	modelcontextprotocol/typescript-sdk	Build MCP servers (TS)	3k+
Cursor Directory	pontusab/cursor.directory	Community .cursorrules collection	3k+
Awesome CursorRules	PatrickJS/awesome-cursorrules	Curated rules examples	5k+
LlamaIndex	run-llama/llama_index	RAG framework	37k+
Docling	DS4SD/docling	Convert PDF/DOCX docs to Markdown	15k+
Part 7: If Your Documentation Is in PDF/HTML/Non-Markdown
You need a conversion step first:

PDF → Markdown:

Bash

# Using Docling (IBM Research)
pip install docling
docling convert --from pdf --to md ./docs/spec.pdf --output ./docs/md/

# Or using Marker (higher quality for complex layouts)
pip install marker-pdf
marker_single ./docs/spec.pdf ./docs/md/
HTML → Markdown:

Bash

# Using Pandoc
pandoc -f html -t markdown ./docs/reference.html -o ./docs/reference.md

# Or using Trafilatura (better for web scraping)
pip install trafilatura
trafilatura -u https://rarelang.org/docs --output-format markdown > docs/reference.md
After conversion, audit the output. Automated conversion often mangles:

Code blocks (losing language-specific syntax)
Tables (especially complex ones)
Cross-references and links
Mathematical notation
Part 8: The Meta-Prompt (Generate Everything with AI)
Use this prompt to bootstrap the entire documentation suite from your raw docs:

text

I have the complete documentation for a programming language called 
[RareLang]. I'm attaching the full specification below.

Please generate the following files:

1. **llms-small.txt**: A cheat sheet under 500 tokens covering all 
   syntax, types, operators, control flow, and the most important 
   10 standard library functions.

2. **llms.txt**: A routing document under 2000 tokens that describes 
   what each section of the documentation covers and when an AI should 
   consult it.

3. **CLAUDE.md**: A behavioral priming file for Claude Code that 
   includes build commands, code style rules, common mistakes to avoid, 
   and a reference to the full documentation.

4. **examples/**: A series of 20 annotated code examples progressing 
   from hello world to a complete mini-project. Each example should 
   include header comments explaining WHAT the example demonstrates, 
   WHEN you'd use this pattern, and any pitfalls to avoid.

5. **error_reference.md**: Documentation for the 20 most likely 
   compiler/runtime errors a new user would encounter, with examples 
   and fixes.

Rules:
- Use ONLY syntax and features documented in the attached specification.
- If something is ambiguous in the spec, flag it with [AMBIGUOUS] and 
  provide your best interpretation.
- Do NOT invent standard library functions.
- Include anti-patterns alongside correct patterns.

[ATTACH YOUR DOCUMENTATION HERE]
Summary Recommendation
For a single developer wanting AI tools to master a rare language:

Start with examples (Tier S+) — highest ROI, lowest tooling dependency
Pack everything with Repomix (Tier A) — simple, works today
Write priming files (Tier A) — 30 minutes, permanent benefit
Add llms.txt (Tier S) — future-proofing, trivial effort
Skip MCP/RAG/fine-tuning unless your docs exceed 200k tokens
Consider Tree-sitter only if you'll be doing heavy development long-term
The combination of a well-structured example corpus + Repomix payload + behavioral priming file will get you 90% of the way to an AI that can competently write your rare language. The remaining 10% comes from iterative refinement as you discover the AI's failure modes and address them with additional examples and rules.





expand on this answer to my question: I have the documentation files for a rare programming language. I want to create the necessary documentation for this documentation such that an ai programming tool can understand and master it. for example, maybe I need to create a skill/agent with certain files of certain makeups so common tools like claude code, etc, can read them and know what of my programming language documentation is needed for what, when, etc. research and discuss my options. are there specs I should follow, are there automated prompts for ai to automatically generate these files, perhaps github projects for this, etc. compare and contrast, tier list, dependencies, mutual exclusions, recommendations.

Gemini said
To ensure AI programming tools (like Claude Code, Cursor, Copilot, or Cline) can effectively parse, understand, and master a rare programming language, you need to structure your documentation using emerging AI context standards.

Here is a breakdown of your options, categorized by utility and implementation effort, optimized for modern AI-assisted workflows.

Tier List for AI Documentation Context
Tier S: Standardized Static Routing (llms.txt)

What it is: The emerging industry standard (proposed by Answer.AI) acting as a robots.txt or sitemap.xml specifically for LLMs.

Purpose: Tells the AI agent exactly what documentation exists, where it is, and when to use it.

Pros: Universally recognized by modern agents. Highly token-efficient.

Cons: Requires manual curation of the routing logic if not automatically generated.

Tier A: Full-Context Packing (Repomix)

What it is: A utility that compiles your entire documentation repository into a single, AI-optimized XML or Markdown file.

Purpose: Bypasses agent search mechanics by structuring the entire documentation payload for single-shot ingestion.

Pros: Zero-shot context. Eliminates RAG (Retrieval-Augmented Generation) hallucinations. Automatically handles AST extraction (via Tree-sitter) and token counting.

Cons: Unviable if your total documentation exceeds the model's context window (~200k tokens for most standard APIs, up to 2M for Gemini/Claude 3.5).

Tier A: Behavioral Priming (.cursorrules / .clinerules)

What it is: Hidden markdown files placed in the project root.

Purpose: Injects strict system prompts into the AI's context window. This defines how the AI should apply the documentation (e.g., "Always use snake_case," "Never use pointers").

Pros: Direct control over output generation and rule enforcement.

Cons: Tied to specific IDEs or CLI tools.

Tier B: Dynamic Retrieval (Model Context Protocol - MCP)

What it is: Anthropic's open-source standard for connecting AI to external data sources.

Purpose: Exposes your documentation as a searchable, agent-callable database tool.

Pros: Infinitely scalable. Perfect for massive, enterprise-scale documentation sets.

Cons: High friction. Requires hosting a local server process. Overkill for a single programming language unless the standard library is massive.

Specifications & Formatting Rules

The llms.txt Specification (The Router)
Place a file named llms.txt in the root of your documentation. The spec requires Markdown and a strict semantic hierarchy.
The structure instructs the AI on tool selection:

Markdown

[Rare Language Name] Documentation
[Rare Language Name] is a systems programming language. This guide routes you to the correct syntax and standard library files.

Core Syntax
Basic Types: Read this first when declaring variables.
Memory Model: Crucial for understanding ownership. Read this before writing async functions.
Standard Library
Network I/O: Socket and HTTP implementations.
Optional
Design Philosophy: Context on language design (skip for direct coding tasks).
The Full Payload (llms-full.txt via XML)
While llms.txt acts as the router, the standard dictates that a secondary file, llms-full.txt, should contain the raw payload of all files combined. LLMs parse XML tags significantly better than deep Markdown trees for large codebases.
Recommended Windows Workflow (One-Shot)
If your documentation is under ~300k tokens, do not build an MCP server or custom RAG pipeline. It introduces fragile dependencies. Instead, use Repomix to compile the docs and .cursorrules to force the AI to read them.

Step 1: Install Repomix
Repomix is the current best-in-class repository packer.

PowerShell

Requires Node.js
npm install -g repomix
Step 2: Generate the Compiled Payload
Navigate to your documentation repository root.

PowerShell

Pack the docs into an XML structure, ignoring binary/media files
repomix --style xml --output llms-full.txt --ignore "/*.pdf,/*.png"
Step 3: Define Agent Execution Rules
In the root directory of the project where you intend to write the code using AI, create a .cursorrules (Cursor) or .clinerules (Claude Code) file. Point the agent to the documentation:

Markdown
You are an expert developer in [Rare Language Name].
Before executing any file creation or refactoring, you MUST ingest the language specification payload located at: C:\Path\To\Docs\llms-full.txt.

Language execution constraints:

Strict adherence to the memory model defined in the XML payload.
Do not invent standard library functions; verify them against the payload first.
Automated Generation (GitHub Projects)
If you maintain your documentation dynamically and want to automate this CI/CD pipeline:
For Static Sites (MkDocs/Sphinx): Use the demodrive-ai/llms-txt-action GitHub Action. It crawls your generated HTML/Markdown and automatically builds the semantic llms.txt router file on push.

For Repository Packing: The official yamadashy/repomix GitHub Action can be added to your workflow to regenerate the llms-full.txt XML payload automatically whenever a documentation file changes.

Dependencies & Mutual Exclusions
llms.txt vs. Repomix: Complementary. Use llms.txt as the index, and let Repomix generate the llms-full.txt payload.

Repomix vs. MCP: Mutually exclusive based on scale. If you pack the repo with Repomix and feed it to the LLM, an MCP filesystem server is redundant and wastes token overhead on tool-calling schemas. Only use an MCP server if your documentation exceeds 500k tokens and requires iterative, search-based retrieval.

Draft a template llms.txt file
Write a .cursorrules system prompt
Generate a Repomix config script

Ask followup…

Add files




Inputs are processed by third-party AI and responses may be inaccurate.

Chat with Multiple Frontier AI Models