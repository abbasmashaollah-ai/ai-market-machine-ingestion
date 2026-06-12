from __future__ import annotations

import json
from pathlib import Path

from app.handoff.news_sentiment_fixture_normalizer import (
    load_fixture_news_records,
    normalize_fixture_news_records,
)
from app.handoff.news_sentiment_handoff import DEFAULT_FIXTURE_BATCH_METADATA, read_news_sentiment_handoff_jsonl, write_news_sentiment_handoff_jsonl


def test_fixture_to_jsonl_round_trip(tmp_path: Path) -> None:
    raw_records = load_fixture_news_records(Path("tests/fixtures/news_sentiment_fixture_sample.json"))
    normalized = normalize_fixture_news_records(raw_records, batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)

    output_path = tmp_path / "news_sentiment.jsonl"
    summary = write_news_sentiment_handoff_jsonl(
        normalized.normalized_records,
        output_path,
        batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA,
    )
    assert summary.records_written > 0
    assert summary.records_rejected == 0

    read_result = read_news_sentiment_handoff_jsonl(output_path)
    assert read_result.records_read == summary.records_written
    assert len(read_result.records) == summary.records_written

    first = read_result.records[0]
    for field_name in (
        "news_id",
        "vendor",
        "source_dataset",
        "source_name",
        "source_domain",
        "headline",
        "published_at",
        "collected_at",
        "producer_run_id",
    ):
        assert field_name in first
        assert isinstance(first[field_name], str)
        assert first[field_name]
    assert first["published_at"].endswith("Z")
    assert first["collected_at"].endswith("Z")
    assert first["raw_sentiment_score"] == 0.7
    assert first["raw_sentiment_label"] == "positive"
    assert "buy_signal" not in first
    assert "sell_signal" not in first
    assert "bullish" not in first
    assert "bearish" not in first
    assert "regime_impact" not in first
    assert "risk_posture" not in first
    assert "portfolio_action" not in first


def test_invalid_fixture_record_is_rejected_and_not_silently_written(tmp_path: Path) -> None:
    raw_records = load_fixture_news_records(Path("tests/fixtures/news_sentiment_fixture_sample.json"))
    raw_records.append(
        {
            "id": "fixture-news-bad",
            "source": "Fixture Newswire",
            "domain": "example.com",
            "title": "Bad fixture",
            "published_at": "2026-05-30T16:00:00Z",
            "collected_at": "2026-05-30T16:05:00Z",
            "url": "https://example.com/news/bad?token=secret",
            "summary": "Rejected fixture.",
            "symbols": ["SPY"],
            "sentiment_score": 0.1,
            "sentiment_label": "neutral",
            "buy_signal": True,
        }
    )
    normalized = normalize_fixture_news_records(raw_records, batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA)
    assert normalized.rejected_records
    assert normalized.normalized_records
    assert len(normalized.normalized_records) + len(normalized.rejected_records) == len(raw_records)

    output_path = tmp_path / "news_sentiment.jsonl"
    summary = write_news_sentiment_handoff_jsonl(
        normalized.normalized_records,
        output_path,
        batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA,
        quarantine_path=tmp_path / "quarantine.jsonl",
    )
    assert summary.records_written == len(normalized.normalized_records)
    assert summary.records_rejected == 0
    assert output_path.exists()


def test_reader_reports_malformed_jsonl_line_number(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"ok": True}) + "\nnot-json\n", encoding="utf-8")
    result = read_news_sentiment_handoff_jsonl(path)
    assert result.records_read == 1
    assert result.malformed_lines == ({"line_number": 2, "error": "Expecting value"},)
