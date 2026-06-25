from pathlib import Path


def test_news_sentiment_deferred_helper_resolution_doc_has_required_sections() -> None:
    doc = Path(__file__).resolve().parents[2] / "docs" / "news_sentiment_deferred_helper_resolution.md"
    assert doc.exists()

    text = doc.read_text(encoding="utf-8")
    for required in [
        "# News/Sentiment Deferred Helper Resolution",
        "## Boundary Decision",
        "## Runtime File Ownership",
        "## Test Ownership",
        "## What Changed",
        "## What Remains In Data",
        "## Why This Is Compliant",
        "## Readiness",
    ]:
        assert required in text

    assert "app/warehouse/news_sentiment_handoff_acceptance.py" in text
    assert "app.database.*" in text
    assert "NewsArticle" in text
    assert "ingestion-owned" in text
