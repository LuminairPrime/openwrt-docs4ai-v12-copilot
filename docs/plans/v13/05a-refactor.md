# 05a Cross-Link Resolution Bug Fix

## Problem Analysis

The `process` job failed during `[08] Security & Quality Validation` with broken link errors originating from the new `cookbook` module:

```
FAIL: Broken relative link in release-tree/cookbook/bundled-reference.md: ../../chunked-reference/luci-examples/example_app...
FAIL: Broken relative link in release-tree/cookbook/chunked-reference/luci-form-with-uci.md: ../../../chunked-reference/luci-examples/example_app...
```

The root cause is a catastrophic regex matching flaw in `.github/scripts/openwrt-docs4ai-05a-assemble-references.py`.

The script uses this regex to identify and rewrite cross-module relative links:
```python
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)'
```

When a markdown file contains a link starting with `../../` (as hand-authored in the `cookbook` sources), the regex matches it incorrectly:
1. `\.\./` matches the **first** `../`
2. `([^/)]+)` captures the **second** `..` and treats it as the `{module}` name!
3. `([^)]*?\.md)` captures the rest of the path, including the real module name (e.g., `luci-examples/example_app.md`)

When `rewrite_release_chunked_links` performs the substitution:
```python
rf'[\1](../../\2/{config.MODULE_CHUNKED_REF_DIRNAME}/\3)'
```
It injects `\2` (which is `..`), resulting in the invalid path `../../../chunked-reference/luci-examples/...` instead of the correct path `../../luci-examples/chunked-reference/...`.

## Proposed Fix

We must tighten the module-matching capture group in all three regexes (`rewrite_relative_links`, `rewrite_release_relative_links`, and `rewrite_release_chunked_links`) so it cannot capture `..`.

A valid OpenWrt docs module name consists only of alphanumeric characters and hyphens (e.g., `luci-examples`, `procd`, `wiki`).

**Change:**
```python
r'\[(.*?)\]\(\.\./((?!L2-semantic)[^/)]+)/([^)]*?\.md)\)'
```

**To:**
```python
# Match one OR MORE `../` sequences to handle both `../` and `../../` links gracefully
r'\[(.*?)\]\((?:\.\./)+((?!L2-semantic)[a-zA-Z0-9-]+)/([^)]*?\.md)\)'
```

Alternatively, standardizing the hand-authored links in `content/cookbook-source/` to strictly use `../` (to match the L2 module depth) would immediately prevent the regex from hitting the double-dot sequence. However, fixing the regex is the most robust solution to ensure `05a` never treats `..` as a legitimate module name.
