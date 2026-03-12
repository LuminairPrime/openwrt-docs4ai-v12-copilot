from tests.support.pytest_pipeline_support import (
    WIKI_ARTIFACT_PATTERNS,
    WIKI_L2_DIR,
    classify_wiki_l2_sanity,
    summarize_wiki_l2_corpus,
)


def test_wiki_l2_committed_corpus_sanity_snapshot():
    assert WIKI_L2_DIR.exists(), f"Missing committed wiki corpus: {WIKI_L2_DIR}"

    summary = summarize_wiki_l2_corpus(WIKI_L2_DIR)
    status = classify_wiki_l2_sanity(summary)
    artifact_stats = " ".join(
        f"{name}={summary[f'{name}_files']}/{summary[f'{name}_occurrences']}"
        for name in WIKI_ARTIFACT_PATTERNS
    )

    print(
        "[sanity] wiki-l2 "
        f"status={status} "
        f"files={summary['files']} "
        f"{artifact_stats} "
        f"duplicate_lead_heading={summary['duplicate_lead_heading_files']}"
    )

    assert status == "clean"
    assert summary["duplicate_lead_heading_files"] == 0
    for key in WIKI_ARTIFACT_PATTERNS:
        assert summary[f"{key}_files"] == 0