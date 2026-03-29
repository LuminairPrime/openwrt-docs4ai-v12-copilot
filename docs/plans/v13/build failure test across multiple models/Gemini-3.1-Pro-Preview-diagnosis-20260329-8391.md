## Plan: Resolve CI Failure from Folder Refactor

The recent CI failure following the `pipeline-folder-refactor-04.md` implementation is highly likely due to path mismatches between the newly reorganized folder structure and the CI configuration or hardcoded script path resolutions.

**Tiered Diagnosis of Failure Causes**

- **S Tier (Most Likely / High Confidence): Workflow Path Mismatches**
  The `.github/workflows/openwrt-docs4ai-pipeline.yml` file still references old folder paths for artifacts, caching, or script execution. For example, it might be looking for `openwrt-condensed-docs-renamed/` or old L1/L2 intermediate paths instead of the newly standardized `tmp/pipeline-ci/L1-raw/` locations to upload artifacts or push to `gh-pages`.

- **A Tier (Highly Likely): Python Configuration Path Drift**
  `lib/config.py` or associated path resolution logic (like `repo_manifest.py`) is trying to resolve to the old directory structure for L1-raw/L2-semantic/staged directories, causing scripts to immediately throw a `FileNotFoundError`.

- **B Tier (Likely): Missing or Moved Test Fixtures**
  CI test steps running via `tests/run_smoke_and_pytest.py` are failing because `tests/artifacts/`, `tests/sample-inputs/`, or other test configuration setup (often within `tests/conftest.py`) were not updated to point to the new refactored L0/L1 test suite locations.

- **C Tier (Possible): Module Import Errors**
  Moving pipeline scripts broke relative imports of `lib/` components within the refactored folders, forcing the Python interpreter to throw `ModuleNotFoundError`s because `sys.path` or default PYTHONPATH expectations were disrupted.

**Steps**
1. Check `.github/workflows/*.yml` for outdated hardcoded paths (especially `deploy` and `upload-artifact` steps).
2. Inspect `lib/config.py` against the new folder structure mapping to ensure it correctly resolves `config.WORK_DIR` and other layer definitions.
3. Review the latest CI run logs specifically for the first `FileNotFoundError`, `ModuleNotFoundError`, or `actionlint` warnings that triggered the crash.
4. Run `python tests/run_smoke_and_pytest.py` locally with the newly refactored structure to reproduce the path failure.

**Relevant files**
- `.github/workflows/openwrt-docs4ai-pipeline.yml` — To hunt down mismatched path expectations in CI.
- `lib/config.py` — For core path resolution logic updates.
- `tests/conftest.py` — For test suite setup path dependencies.

**Verification**
1. Run `gh run list --workflow "openwrt-docs4ai-pipeline"` and `gh run view <run_id> --log-failed` to rapidly triage the exact failing step.
2. Run `python tests/check_linting.py` locally to reveal any hidden static import errors.