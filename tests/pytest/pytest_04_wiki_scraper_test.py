import importlib.util
import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / ".github" / "scripts" / "openwrt-docs4ai-02a-scrape-wiki.py"


def load_wiki_module():
    spec = importlib.util.spec_from_file_location("wiki_scraper", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def configure_tmp_workdir(module, tmp_path):
    workdir = tmp_path / "work"
    module.config.WORKDIR = str(workdir)
    module.config.L1_RAW_WORKDIR = str(workdir / "L1-raw")
    module.config.L2_SEMANTIC_WORKDIR = str(workdir / "L2-semantic")
    module.config.WIKI_MAX_PAGES = 300
    module.config.ensure_dirs()


class FakeResponse:
    def __init__(self, status_code=200, text="", headers=None, url=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}
        self.url = url

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, timeout=None, headers=None, allow_redirects=True):
        self.calls.append(
            {
                "url": url,
                "timeout": timeout,
                "headers": headers or {},
                "allow_redirects": allow_redirects,
            }
        )
        return self.responses.pop(0)


def test_load_cache_normalizes_legacy_and_structured_entries(tmp_path):
    wiki = load_wiki_module()
    cache_file = tmp_path / "wiki-lastmod.json"
    cache_file.write_text(
        json.dumps(
            {
                "https://openwrt.org/docs/techref/ubus": "2025-03-08T12:00:00",
                "https://openwrt.org/docs/techref/procd": {
                    "last_modified": "unknown",
                    "last_modified_http": "Sat, 08 Mar 2025 12:00:00 GMT",
                    "raw_hash": "abc",
                    "content_hash": "def",
                },
            }
        ),
        encoding="utf-8",
    )

    cache = wiki.load_cache(str(cache_file))

    assert cache["https://openwrt.org/docs/techref/ubus"]["last_modified"] == "2025-03-08T12:00:00"
    assert cache["https://openwrt.org/docs/techref/procd"]["raw_hash"] == "abc"
    assert cache["https://openwrt.org/docs/techref/procd"]["last_modified_http"] == "Sat, 08 Mar 2025 12:00:00 GMT"


def test_load_cache_ignores_invalid_json(tmp_path):
    wiki = load_wiki_module()
    cache_file = tmp_path / "wiki-lastmod.json"
    cache_file.write_text("{not valid json", encoding="utf-8")

    cache = wiki.load_cache(str(cache_file))

    assert cache == {}


def test_process_page_uses_conditional_get_for_not_modified(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        "techref-ubus",
        "# Cached Ubus\n\nStill valid.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": "techref-ubus"},
    )

    cache = {
        "https://openwrt.org/docs/techref/ubus": {
            "path": "/docs/techref/ubus",
            "last_modified": "2025-03-08T12:00:00",
            "last_modified_http": "Sat, 08 Mar 2025 12:00:00 GMT",
            "raw_hash": "abc",
            "content_hash": "def",
        }
    }
    session = FakeSession([FakeResponse(status_code=304)])
    stats = wiki.build_stats()

    outcome = wiki.process_page(session, "/docs/techref/ubus", cache, stats, wiki.get_cutoff_date())

    assert outcome == "skipped_unchanged"
    assert stats["skipped_unchanged"] == 1
    assert session.calls[0]["headers"]["If-Modified-Since"] == "Sat, 08 Mar 2025 12:00:00 GMT"


def test_process_page_skips_rewrite_when_raw_hash_matches(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    raw_content = "====== ubus ======\n\nEnough text to exercise hash-based cache reuse.\n" * 4
    raw_hash = wiki.compute_hash(raw_content)
    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        "techref-ubus",
        "# Cached Ubus\n\nStill valid.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": "techref-ubus"},
    )

    cache = {
        "https://openwrt.org/docs/techref/ubus": {
            "path": "/docs/techref/ubus",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": raw_hash,
            "content_hash": "def",
        }
    }
    session = FakeSession([FakeResponse(status_code=200, text=raw_content, headers={})])
    stats = wiki.build_stats()

    monkeypatch.setattr(
        wiki,
        "convert_raw_to_markdown",
        lambda path, raw_content: pytest.fail("Conversion should be skipped when raw hash matches."),
    )

    outcome = wiki.process_page(session, "/docs/techref/ubus", cache, stats, wiki.get_cutoff_date())

    assert outcome == "skipped_unchanged"
    assert stats["skipped_unchanged"] == 1


def test_process_page_expires_old_page_even_when_raw_hash_matches(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    path = "/docs/techref/old-page"
    slug = wiki.path_to_filename(path)
    raw_content = "====== Old Page ======\n\nThis content is old but unchanged.\n" * 6
    raw_hash = wiki.compute_hash(raw_content)

    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        slug,
        "# Old Page\n\nCached content.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": slug},
    )

    cache = {
        "https://openwrt.org/docs/techref/old-page": {
            "path": path,
            "last_modified": "2022-01-01T00:00:00",
            "last_modified_http": "Sat, 01 Jan 2022 00:00:00 GMT",
            "raw_hash": raw_hash,
            "content_hash": "deadbeef",
        }
    }
    session = FakeSession(
        [FakeResponse(status_code=200, text=raw_content, headers={"Last-Modified": "Sat, 01 Jan 2022 00:00:00 GMT"})]
    )
    stats = wiki.build_stats()

    outcome = wiki.process_page(session, path, cache, stats, cutoff=wiki.datetime.datetime(2024, 1, 1))

    assert outcome == "skipped_old"
    assert stats["skipped_old"] == 1
    assert not (tmp_path / "work" / "L1-raw" / "wiki" / f"wiki_page-{slug}.md").exists()


def test_discover_pages_ignores_bot_page_links_and_disables_cleanup(monkeypatch):
    wiki = load_wiki_module()
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    responses = {
        "docs%3Atechref": '<!doctype html><html><body><h1>Testing to determine if you are a bot</h1><a href="/docs/techref/procd">procd</a></body></html>',
        "docs%3Aguide-developer": '<!doctype html><html><body><h1>Testing to determine if you are a bot</h1><a href="/docs/guide-developer/example">example</a></body></html>',
        "docs%3Aguide-user%3Abase-system%3Auci": '<!doctype html><html><body><h1>Testing to determine if you are a bot</h1><a href="/docs/guide-user/base-system/uci/foo">foo</a></body></html>',
    }

    class NamespaceSession:
        def get(self, url, timeout=None):
            for key, value in responses.items():
                if key in url:
                    return FakeResponse(text=value)
            raise AssertionError(url)

    pages, allow_cleanup = wiki.discover_pages(NamespaceSession())

    assert pages == set(wiki.MANDATORY_PAGES)
    assert allow_cleanup is False


def test_discover_pages_ignores_offsite_absolute_urls(monkeypatch):
    wiki = load_wiki_module()
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    responses = {
        "docs%3Atechref": '<html><body><a href="https://evil.example/docs/techref/pwned">bad</a><a href="https://openwrt.org/docs/techref/valid.page">good</a></body></html>',
        "docs%3Aguide-developer": "<html><body></body></html>",
        "docs%3Aguide-user%3Abase-system%3Auci": "<html><body></body></html>",
    }

    class NamespaceSession:
        def get(self, url, timeout=None):
            for key, value in responses.items():
                if key in url:
                    return FakeResponse(text=value)
            raise AssertionError(url)

    pages, allow_cleanup = wiki.discover_pages(NamespaceSession())

    assert "/docs/techref/valid.page" in pages
    assert "/docs/techref/pwned" not in pages
    assert allow_cleanup is True


def test_fetch_raw_page_rejects_unexpected_redirect_target(monkeypatch):
    wiki = load_wiki_module()
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    session = FakeSession(
        [
            FakeResponse(
                status_code=200,
                text="====== ubus ======\n\ncontent\n" * 5,
                headers={},
                url="https://evil.example/docs/techref/ubus?do=export_raw",
            )
        ]
    )

    with pytest.raises(RuntimeError, match="Unexpected redirect target"):
        wiki.fetch_raw_page(session, "https://openwrt.org/docs/techref/ubus")


def test_convert_raw_to_markdown_falls_back_when_pandoc_fails(monkeypatch):
    wiki = load_wiki_module()

    class PandocResult:
        returncode = 64
        stdout = ""
        stderr = "dokuwiki parse failed"

    monkeypatch.setattr(wiki.subprocess, "run", lambda *args, **kwargs: PandocResult())

    converted = wiki.convert_raw_to_markdown(
        "/docs/techref/initscripts",
        "====== Init Scripts ======\n\nThis page documents OpenWrt init scripts in raw DokuWiki syntax.\n" * 4,
    )

    assert converted["mode"] == "fallback-raw"
    assert converted["content"].startswith("# Init Scripts")
    assert "raw DokuWiki syntax" in converted["content"]


def test_process_page_reuses_cached_output_after_fetch_failure(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    slug = "techref-ubus"
    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        slug,
        "# Cached Ubus\n\nStill valid.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": slug},
    )

    class FailingSession:
        def get(self, url, timeout=None, headers=None, allow_redirects=True):
            raise RuntimeError("network down")

    cache = {
        "https://openwrt.org/docs/techref/ubus": {
            "path": "/docs/techref/ubus",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": None,
            "content_hash": None,
            "skip_reason": None,
        }
    }
    stats = wiki.build_stats()

    outcome = wiki.process_page(FailingSession(), "/docs/techref/ubus", cache, stats, wiki.get_cutoff_date())

    assert outcome == "reused_cached"
    assert stats["reused_cached"] == 1


def test_process_page_reuses_cached_output_after_html_error(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    slug = "techref-ubus"
    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        slug,
        "# Cached Ubus\n\nStill valid.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": slug},
    )

    session = FakeSession(
        [
            FakeResponse(
                status_code=200,
                text="<!doctype html><html><body><h1>Just a moment...</h1></body></html>",
                headers={},
                url="https://openwrt.org/docs/techref/ubus?do=export_raw",
            )
        ]
    )
    cache = {
        "https://openwrt.org/docs/techref/ubus": {
            "path": "/docs/techref/ubus",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": None,
            "content_hash": None,
            "skip_reason": None,
        }
    }
    stats = wiki.build_stats()

    outcome = wiki.process_page(session, "/docs/techref/ubus", cache, stats, wiki.get_cutoff_date())

    assert outcome == "reused_cached"
    assert stats["reused_cached"] == 1


def test_process_page_discards_inconsistent_cached_output_and_refetches(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    slug = "techref-ubus"
    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        slug,
        "# Cached Ubus\n\nOriginal content.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": slug},
    )
    md_path = tmp_path / "work" / "L1-raw" / "wiki" / f"wiki_page-{slug}.md"
    md_path.write_text("# Corrupted\n\nThis content no longer matches metadata.\n", encoding="utf-8")

    raw_content = "====== ubus ======\n\nEnough text to trigger a fresh rewrite after corruption.\n" * 5
    session = FakeSession(
        [
            FakeResponse(
                status_code=200, text=raw_content, headers={}, url="https://openwrt.org/docs/techref/ubus?do=export_raw"
            )
        ]
    )
    cache = {
        "https://openwrt.org/docs/techref/ubus": {
            "path": "/docs/techref/ubus",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": "stale-raw-hash",
            "content_hash": "stale-content-hash",
            "skip_reason": None,
        }
    }
    stats = wiki.build_stats()

    outcome = wiki.process_page(session, "/docs/techref/ubus", cache, stats, wiki.get_cutoff_date())

    assert outcome == "saved"
    assert stats["saved"] == 1
    assert "Corrupted" not in md_path.read_text(encoding="utf-8")


def test_process_page_skips_short_result_when_cached_short_hash_matches(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    raw_content = "====== Tiny ======\n\nshort\n"
    raw_hash = wiki.compute_hash(raw_content)
    cache = {
        "https://openwrt.org/docs/techref/tiny-page": {
            "path": "/docs/techref/tiny-page",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": raw_hash,
            "content_hash": None,
            "skip_reason": "short",
        }
    }
    session = FakeSession(
        [
            FakeResponse(
                status_code=200,
                text=raw_content,
                headers={},
                url="https://openwrt.org/docs/techref/tiny-page?do=export_raw",
            )
        ]
    )
    stats = wiki.build_stats()

    monkeypatch.setattr(
        wiki,
        "convert_raw_to_markdown",
        lambda path, raw_content: pytest.fail("Conversion should be skipped when cached short hash matches."),
    )

    outcome = wiki.process_page(session, "/docs/techref/tiny-page", cache, stats, wiki.get_cutoff_date())

    assert outcome == "skipped_short"
    assert stats["skipped_short"] == 1


def test_process_page_records_short_skip_reason_when_no_output_exists(tmp_path, monkeypatch):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)
    monkeypatch.setattr(wiki, "sleep_with_rate_limit", lambda reason: None)

    raw_content = "====== Tiny ======\n\nshort\n"
    session = FakeSession(
        [
            FakeResponse(
                status_code=200,
                text=raw_content,
                headers={},
                url="https://openwrt.org/docs/techref/tiny-page?do=export_raw",
            )
        ]
    )
    cache = {}
    stats = wiki.build_stats()

    monkeypatch.setattr(
        wiki,
        "convert_raw_to_markdown",
        lambda path, raw_content: {"title": "Tiny", "content": "too short", "mode": "pandoc", "error": None},
    )

    outcome = wiki.process_page(session, "/docs/techref/tiny-page", cache, stats, wiki.get_cutoff_date())

    assert outcome == "skipped_short"
    assert stats["skipped_short"] == 1
    assert cache["https://openwrt.org/docs/techref/tiny-page"]["skip_reason"] == "short"


def test_cleanup_orphaned_outputs_removes_stale_cached_files(tmp_path):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)

    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        "techref-keep-page",
        "# Keep\n\nCurrent page.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": "techref-keep-page"},
    )
    wiki.extractor.write_l1_markdown(
        "wiki",
        "wiki_page",
        "techref-stale-page",
        "# Stale\n\nOld page.\n",
        {"module": "wiki", "origin_type": "wiki_page", "slug": "techref-stale-page"},
    )

    cache = {
        "https://openwrt.org/docs/techref/keep.page": {
            "path": "/docs/techref/keep.page",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": None,
            "content_hash": None,
        },
        "https://openwrt.org/docs/techref/stale.page": {
            "path": "/docs/techref/stale.page",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": None,
            "content_hash": None,
        },
    }

    removed = wiki.cleanup_orphaned_outputs({"/docs/techref/keep.page"}, cache, hit_cap=False)

    assert removed == 1
    assert "https://openwrt.org/docs/techref/stale.page" not in cache
    assert not (tmp_path / "work" / "L1-raw" / "wiki" / "wiki_page-techref-stale-page.md").exists()


def test_cleanup_orphaned_outputs_prunes_stale_cache_without_files(tmp_path):
    wiki = load_wiki_module()
    configure_tmp_workdir(wiki, tmp_path)

    cache = {
        "https://openwrt.org/docs/techref/keep.page": {
            "path": "/docs/techref/keep.page",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": None,
            "content_hash": None,
        },
        "https://openwrt.org/docs/techref/stale.page": {
            "path": "/docs/techref/stale.page",
            "last_modified": "unknown",
            "last_modified_http": None,
            "raw_hash": None,
            "content_hash": None,
        },
    }

    removed = wiki.cleanup_orphaned_outputs({"/docs/techref/keep.page"}, cache, hit_cap=False)

    assert removed == 0
    assert list(cache) == ["https://openwrt.org/docs/techref/keep.page"]
