from pathlib import Path


def test_news_sentiment_handoff_acceptance_boundary_resolution_doc_has_required_sections() -> None:
    doc = Path(__file__).resolve().parents[2] / "docs" / "news_sentiment_handoff_acceptance_boundary_resolution.md"
    assert doc.exists()

    text = doc.read_text(encoding="utf-8")
    for required in [
        "# News/Sentiment Handoff Acceptance Boundary Resolution",
        "## Boundary Decision",
        "## Runtime File Ownership",
        "## Test Ownership",
        "## Why Deferred",
        "## Generated Outputs",
        "## Recommended Next Step",
        "## Readiness",
    ]:
        assert required in text
