from __future__ import annotations

from pathlib import Path

from app.handoff.news_sentiment_handoff import DEFAULT_FIXTURE_BATCH_METADATA, validate_news_sentiment_record
from app.handoff.news_sentiment_rss_sample_adapter import (
    load_rss_sample_items,
    normalize_rss_sample_item,
    normalize_rss_sample_items,
)


def _rss_item() -> dict[str, object]:
    return {
        "guid": "rss-news-010",
        "title": "Apple expands services coverage",
        "link": "https://example.com/news/aapl-1",
        "source_name": "RSS Fixture Wire",
        "source_domain": "example.com",
        "published": "2026-05-30T14:30:00Z",
        "collected_at": "2026-05-30T14:35:00Z",
        "summary": "Deterministic RSS sample for AAPL.",
        "categories": ["services", "earnings"],
        "symbols": ["AAPL", "MSFT"],
        "sentiment_score": 0.7,
        "sentiment_label": "positive",
    }


def test_normalizes_valid_rss_sample_item() -> None:
    normalized = normalize_rss_sample_item(_rss_item(), batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert normalized["vendor_article_id"] == "rss-news-010"
    assert normalized["headline"] == "Apple expands services coverage"
    assert normalized["tickers"] == ("AAPL", "MSFT")
    assert normalized["topics"] == ("services", "earnings")
    assert normalized["raw_sentiment_score"] == 0.7
    assert normalized["raw_sentiment_label"] == "positive"
    assert normalized["published_at"].endswith("Z")
    assert normalized["collected_at"].endswith("Z")
    assert normalized["news_id"].startswith("news-")


def test_normalizes_rss_batch_and_validates_output() -> None:
    normalized = normalize_rss_sample_items([_rss_item()], batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert len(normalized.normalized_records) == 1
    assert normalized.rejected_records == ()
    validation = validate_news_sentiment_record(normalized.normalized_records[0])
    assert validation.accepted is True
    assert "buy_signal" not in normalized.normalized_records[0]


def test_load_rss_sample_file() -> None:
    items = load_rss_sample_items(Path("tests/fixtures/news_sentiment_rss_sample.json"))
    assert len(items) == 2
    assert items[0]["guid"] == "rss-news-001"


def test_rss_sample_rejections() -> None:
    bad = _rss_item()
    bad.pop("title")
    result = normalize_rss_sample_items([bad], batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert result.normalized_records == ()
    assert result.rejected_records


def test_secret_like_link_rejected() -> None:
    bad = _rss_item()
    bad["link"] = "https://example.com/news/aapl-1?token=secret"
    result = normalize_rss_sample_items([bad], batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert result.normalized_records == ()
    assert result.rejected_records


def test_invalid_published_timestamp_rejected() -> None:
    bad = _rss_item()
    bad["published"] = "not-a-timestamp"
    result = normalize_rss_sample_items([bad], batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert result.normalized_records == ()
    assert result.rejected_records

