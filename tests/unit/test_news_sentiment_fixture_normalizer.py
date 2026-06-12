from __future__ import annotations

from pathlib import Path

from app.handoff.news_sentiment_fixture_normalizer import (
    load_fixture_news_records,
    normalize_fixture_news_record,
    normalize_fixture_news_records,
)
from app.handoff.news_sentiment_handoff import DEFAULT_FIXTURE_BATCH_METADATA, validate_news_sentiment_record


def _fixture() -> dict[str, object]:
    return {
        "id": "fixture-news-010",
        "source": "Fixture Newswire",
        "domain": "example.com",
        "title": "Apple expands services coverage",
        "published_at": "2026-05-30T14:30:00Z",
        "collected_at": "2026-05-30T14:35:00Z",
        "url": "https://example.com/news/aapl-1",
        "summary": "Deterministic fixture article for AAPL.",
        "symbols": ["AAPL", "MSFT"],
        "topics": ["services", "earnings"],
        "sentiment_score": 0.7,
        "sentiment_label": "positive",
    }


def test_normalizes_valid_fixture_record() -> None:
    normalized = normalize_fixture_news_record(_fixture(), batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert normalized["headline"] == "Apple expands services coverage"
    assert normalized["tickers"] == ("AAPL", "MSFT")
    assert normalized["raw_sentiment_score"] == 0.7
    assert normalized["raw_sentiment_label"] == "positive"
    assert normalized["vendor"] == DEFAULT_FIXTURE_BATCH_METADATA.vendor
    assert normalized["producer_run_id"] == DEFAULT_FIXTURE_BATCH_METADATA.producer_run_id
    assert normalized["news_id"].startswith("news-")
    assert normalized["published_at"].endswith("Z")
    assert normalized["collected_at"].endswith("Z")


def test_preserves_vendor_article_id_when_present() -> None:
    record = _fixture()
    record["vendor_article_id"] = "vendor-article-123"
    normalized = normalize_fixture_news_record(record, batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert normalized["vendor_article_id"] == "vendor-article-123"


def test_batch_normalization_outputs_handoff_valid_records() -> None:
    normalized = normalize_fixture_news_records([_fixture()], batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert len(normalized.normalized_records) == 1
    assert normalized.rejected_records == ()
    validation = validate_news_sentiment_record(normalized.normalized_records[0])
    assert validation.accepted is True
    assert "buy_signal" not in normalized.normalized_records[0]


def test_invalid_fixture_record_is_reported() -> None:
    record = _fixture()
    record["sentiment_score"] = 2.5
    normalized = normalize_fixture_news_records([record], batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert normalized.normalized_records == ()
    assert normalized.rejected_records


def test_load_fixture_file() -> None:
    records = load_fixture_news_records(Path("tests/fixtures/news_sentiment_fixture_sample.json"))
    assert len(records) == 3
    assert records[0]["title"].startswith("Apple")


def test_secret_like_url_is_not_passed_through() -> None:
    record = _fixture()
    record["url"] = "https://example.com?token=secret"
    normalized = normalize_fixture_news_records([record], batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert normalized.normalized_records == ()
    assert normalized.rejected_records
