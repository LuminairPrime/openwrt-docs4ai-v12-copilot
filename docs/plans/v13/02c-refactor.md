# 02c Extractor CI Optimization Plan

## Problem
The `extract` matrix job in GitHub Actions spends over 5 minutes repeatedly installing heavy dependencies (Pandoc and NPM packages) for every single script, even though most extractors don't need them. Specifically:
- `apt-get update` takes several minutes synchronizing with Ubuntu mirrors.
- `npm install -g jsdoc-to-markdown` installs 80+ packages concurrently in 7 parallel matrix legs, but only `02c-scrape-jsdoc.py` uses it.

## Proposed Fixes

### 1. Remove `apt-get update` and `apt install pandoc`
Pandoc isn't needed by the `02b` through `02h` extractors. The only scraper that uses Pandoc is `02a-scrape-wiki.py` (which runs in its own isolated `extract_wiki` job).
- **Action:** Delete `sudo apt-get update -qq && sudo apt-get install -y -qq pandoc` from the main `extract` job.

### 2. Isolate NPM Dependencies
`jsdoc-to-markdown` should not be installed globally across the whole matrix.
- **Action:** Move the NPM installation to its own conditional step that only executes when the `02c` script is running.
- **Implementation:**
  ```yaml
  - name: Install JS dependencies
    if: matrix.script == '02c-scrape-jsdoc.py'
    run: npm install -g jsdoc-to-markdown
  ```

## Expected Outcome
The `extract` job execution time for scripts `02b`, `02d`, `02e`, `02f`, `02g`, `02h` will drop from ~5.5 minutes to roughly **15-20 seconds**. The `02c` job will also run faster by avoiding the `apt-get` penalty.
