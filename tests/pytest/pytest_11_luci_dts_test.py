"""
pytest_11_luci_dts_test.py

Tests for Phase 12 (A1 LuCI Type Definitions):
  - release-tree/luci/types/luci-env.d.ts exists after 05e runs
  - The file declares the core form API (Map, TypedSection, Value)
  - The file declares rpc.declare and uci access methods
  - The _generate_dts function produces valid content without requiring the JS repo
  - The file does not contain any hardcoded/fabricated source URLs
  - The file is consistent with the Approach-2 docstring requirement
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from tests.support.pytest_pipeline_support import OUTDIR, PROJECT_ROOT, load_script_module

RELEASE_LUCI_TYPES_DIR = OUTDIR / "release-tree" / "luci" / "types"
DTS_PATH = RELEASE_LUCI_TYPES_DIR / "luci-env.d.ts"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _load_stage05e():
    return load_script_module("stage05e_luci_dts", "openwrt-docs4ai-05e-generate-luci-dts.py")


# ---------------------------------------------------------------------------
# Existence & structure tests
# ---------------------------------------------------------------------------

def test_luci_env_dts_file_exists() -> None:
    """release-tree/luci/types/luci-env.d.ts must exist after 05e runs."""
    if not RELEASE_LUCI_TYPES_DIR.exists():
        pytest.skip(f"no pipeline output at {RELEASE_LUCI_TYPES_DIR}")
    assert DTS_PATH.exists(), (
        f"Expected {DTS_PATH} to exist. "
        "Run .github/scripts/openwrt-docs4ai-05e-generate-luci-dts.py first."
    )


def test_luci_env_dts_min_length() -> None:
    """File must have at least 200 lines (substantive, not a stub)."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    assert len(lines) >= 200, (
        f"luci-env.d.ts is unexpectedly short ({len(lines)} lines). "
        "Expected at least 200 lines."
    )


def test_luci_env_dts_declares_form_map() -> None:
    """File must declare LuCI.form.Map class."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "class Map" in content, "Expected 'class Map' in luci-env.d.ts"


def test_luci_env_dts_declares_form_typed_section() -> None:
    """File must declare LuCI.form.TypedSection class."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "class TypedSection" in content, "Expected 'class TypedSection' in luci-env.d.ts"


def test_luci_env_dts_declares_form_value() -> None:
    """File must declare LuCI.form.Value class."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "class Value" in content, "Expected 'class Value' in luci-env.d.ts"


def test_luci_env_dts_declares_rpc_declare() -> None:
    """File must declare rpc.declare function."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "function declare(" in content or "declare(" in content, (
        "Expected rpc.declare declaration in luci-env.d.ts"
    )


def test_luci_env_dts_declares_uci_load() -> None:
    """File must declare uci.load function."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "function load(" in content, "Expected 'function load(' in luci-env.d.ts"


def test_luci_env_dts_declares_uci_get() -> None:
    """File must declare uci.get function."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "function get(" in content, "Expected 'function get(' in luci-env.d.ts"


def test_luci_env_dts_declares_uci_set() -> None:
    """File must declare uci.set function."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "function set(" in content, "Expected 'function set(' in luci-env.d.ts"


def test_luci_env_dts_declares_view_lifecycle() -> None:
    """File must declare view lifecycle methods (load and render)."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "load():" in content or "load(): " in content, (
        "Expected view.load() lifecycle method in luci-env.d.ts"
    )
    assert "render(" in content, (
        "Expected view.render() lifecycle method in luci-env.d.ts"
    )


def test_luci_env_dts_declares_dom_namespace() -> None:
    """File must declare the dom namespace."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "namespace dom" in content, "Expected 'namespace dom' in luci-env.d.ts"


def test_luci_env_dts_declares_global_E() -> None:
    """File must declare the global E() DOM helper."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "declare function E(" in content, (
        "Expected 'declare function E(' global helper in luci-env.d.ts"
    )


def test_luci_env_dts_declares_global_translate() -> None:
    """File must declare the global _() i18n helper."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    assert "declare function _(" in content, (
        "Expected 'declare function _(' i18n helper in luci-env.d.ts"
    )


def test_luci_env_dts_approach2_marker_in_script() -> None:
    """The 05e script docstring must document Approach 2 as the chosen parsing strategy."""
    stage05e_path = (
        PROJECT_ROOT / ".github" / "scripts" / "openwrt-docs4ai-05e-generate-luci-dts.py"
    )
    content = stage05e_path.read_text(encoding="utf-8")
    assert "Approach 2" in content, (
        "Expected 'Approach 2' documentation in 05e script docstring. "
        "The chosen parsing strategy must be documented per A1 acceptance criteria."
    )


# ---------------------------------------------------------------------------
# Functional test: _generate_dts works without real JS sources
# ---------------------------------------------------------------------------

def test_generate_dts_works_without_js_sources() -> None:
    """_generate_dts must produce a non-empty valid string even with all None sources."""
    stage05e = _load_stage05e()
    sources = {"form": None, "rpc": None, "uci": None, "luci": None, "network": None}
    result = stage05e._generate_dts(sources)
    assert isinstance(result, str)
    assert len(result) > 500, "Expected >500 chars even from stub generation"
    assert "declare namespace LuCI" in result
    assert "namespace uci" in result
    assert "namespace rpc" in result
    assert "namespace form" in result


def test_generate_dts_contains_no_fabricated_http_urls() -> None:
    """The generated .d.ts must not contain any fabricated http(s) source URLs."""
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    content = DTS_PATH.read_text(encoding="utf-8")
    import re
    # The .d.ts must not reference any specific external URLs (it's a type declaration
    # file — no upstream commit URLs or wiki URLs should be embedded)
    external_url_pattern = re.compile(r'https?://(?!www\.typescriptlang\.org)')
    matches = external_url_pattern.findall(content)
    assert len(matches) == 0, (
        f"Found unexpected external URLs in luci-env.d.ts: {matches[:5]}"
    )


# ---------------------------------------------------------------------------
# TypeScript validity test (requires tsc on PATH)
# ---------------------------------------------------------------------------

def _tsc_cmd() -> list[str] | None:
    """Return the tsc command list if tsc is available, else None.

    On Windows, npm installs tsc as tsc.cmd (not tsc), so we probe both.
    """
    candidates = ["tsc.cmd", "tsc"] if sys.platform == "win32" else ["tsc"]
    for candidate in candidates:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return [candidate]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def test_luci_env_dts_is_valid_typescript() -> None:
    """
    Verify luci-env.d.ts is valid TypeScript via tsc --noEmit.
    Skipped if tsc is not available on PATH.
    """
    if not DTS_PATH.exists():
        pytest.skip(f"no pipeline output at {DTS_PATH}")
    tsc = _tsc_cmd()
    if tsc is None:
        pytest.skip("tsc not available on PATH — skipping TypeScript validation")

    result = subprocess.run(
        tsc + [
            "--noEmit",
            "--strict",
            "--moduleResolution", "node",
            "--target", "es2020",
            str(DTS_PATH),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"tsc --noEmit failed with exit code {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
