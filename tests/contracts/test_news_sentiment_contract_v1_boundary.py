from pathlib import Path


def test_news_sentiment_contract_v1_boundary_helper_is_orm_free() -> None:
    helper = Path(__file__).resolve().parents[2] / "app" / "warehouse" / "news_sentiment_handoff_acceptance.py"
    text = helper.read_text(encoding="utf-8")
    assert "app.database" not in text
    assert "sqlalchemy.orm" not in text
    assert "Session" not in text
    assert "quarantine" in text


def test_news_sentiment_contract_v1_boundary_documented_as_ingestion_owned() -> None:
    doc = Path(__file__).resolve().parents[2] / "docs" / "news_sentiment_deferred_helper_resolution.md"
    text = doc.read_text(encoding="utf-8")
    assert "ingestion-owned" in text
    assert "NewsArticle" in text
