from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.handoff.news_sentiment_handoff import (
    DEFAULT_FIXTURE_BATCH_METADATA,
    DEFAULT_FIXTURE_RECORDS,
    NewsSentimentBatchMetadata,
    read_news_sentiment_handoff_jsonl,
    validate_news_sentiment_record,
    write_news_sentiment_handoff_jsonl,
)


def _record() -> dict[str, object]:
    return dict(DEFAULT_FIXTURE_RECORDS[0])


def test_write_and_read_round_trip(tmp_path: Path) -> None:
    output_path = tmp_path / "handoff.jsonl"
    summary = write_news_sentiment_handoff_jsonl(
        DEFAULT_FIXTURE_RECORDS,
        output_path,
        batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA,
    )

    assert summary.records_received == 3
    assert summary.records_written == 3
    assert summary.records_rejected == 0
    assert summary.producer_run_id == DEFAULT_FIXTURE_BATCH_METADATA.producer_run_id
    assert output_path.exists()

    read_result = read_news_sentiment_handoff_jsonl(output_path)
    assert read_result.records_read == 3
    assert read_result.malformed_lines == ()
    assert read_result.records[0]["headline"] == "Apple expands services coverage"
    assert read_result.records[0]["raw_sentiment_label"] == "positive"
    assert read_result.records[0]["raw_sentiment_score"] == 0.7
    assert read_result.records[0]["lineage"] == ["fixture", "news"]
    assert read_result.records[0]["warnings"] == ["fixture-only"]
    assert "buy_signal" not in read_result.records[0]
    assert "sell_signal" not in read_result.records[0]


def test_validate_minimal_record_and_idempotency() -> None:
    result = validate_news_sentiment_record(_record())
    assert result.accepted is True
    assert result.record is not None
    assert result.idempotency_key
    assert result.idempotency_components is not None
    assert result.record["vendor"] == "fixture_vendor"
    assert result.record["raw_sentiment_label"] == "positive"
    assert result.record["raw_sentiment_score"] == 0.7


@pytest.mark.parametrize(
    "mutator, expected_reason",
    [
        (lambda record: record.pop("headline"), "headline is required"),
        (lambda record: record.pop("published_at"), "missing or invalid published_at"),
        (lambda record: record.pop("collected_at"), "missing or invalid collected_at"),
        (lambda record: record.pop("vendor"), "vendor is required"),
        (lambda record: record.pop("source_dataset"), "source_dataset is required"),
        (lambda record: (record.pop("vendor_article_id"), record.pop("url"), record.pop("canonical_url"), record.pop("news_id")), "one of vendor_article_id, url, canonical_url, or news_id is required"),
        (lambda record: record.__setitem__("raw_sentiment_score", 2.5), "raw_sentiment_score must be between -1 and 1 when provided"),
        (lambda record: record.__setitem__("entities", object()), "entities is not JSON-compatible"),
        (lambda record: record.__setitem__("source_file_path", "https://token.example.com/secret?token=abc"), "unsafe source_file_path"),
        (lambda record: record.__setitem__("url", "https://example.com?api_key=secret"), "possible secret or credential detected in url"),
    ],
)
def test_validation_rejections(mutator, expected_reason: str) -> None:
    record = _record()
    mutator(record)
    result = validate_news_sentiment_record(record)
    assert result.accepted is False
    assert expected_reason in result.rejection_reasons


def test_strategy_fields_are_rejected() -> None:
    record = _record()
    record["buy_signal"] = True
    result = validate_news_sentiment_record(record)
    assert result.accepted is False
    assert "strategy fields are not allowed in ingestion handoff" in result.rejection_reasons


def test_reader_reports_malformed_lines(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"ok": true}\nnot-json\n{"also": "ok"}\n', encoding="utf-8")
    result = read_news_sentiment_handoff_jsonl(path)
    assert result.records_read == 2
    assert result.malformed_lines == ({"line_number": 2, "error": "Expecting value"},)


def test_writer_quarantines_invalid_records(tmp_path: Path) -> None:
    output_path = tmp_path / "handoff.jsonl"
    quarantine_path = tmp_path / "quarantine.jsonl"
    records = [dict(DEFAULT_FIXTURE_RECORDS[0]), {"headline": "bad"}]
    summary = write_news_sentiment_handoff_jsonl(
        records,
        output_path,
        batch_metadata=DEFAULT_FIXTURE_BATCH_METADATA,
        quarantine_path=quarantine_path,
    )
    assert summary.records_received == 2
    assert summary.records_written == 1
    assert summary.records_rejected == 1
    assert quarantine_path.exists()
    quarantined = quarantine_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(quarantined) == 1
    quarantined_record = json.loads(quarantined[0])
    assert quarantined_record["index"] == 1
    assert quarantined_record["rejection_reasons"]


def test_dry_run_script_uses_fixture_only(tmp_path: Path) -> None:
    from scripts import run_news_sentiment_handoff_dry_run as script

    output_file = tmp_path / "news_sentiment.jsonl"
    with patch("builtins.print") as print_mock:
        exit_code = script.main(["--output-file", str(output_file), "--summary-only"])
    assert exit_code == 0
    assert output_file.exists()
    printed = " ".join(str(arg) for call in print_mock.mock_calls for arg in call.args)
    assert '"records_written": 3' in printed
    assert '"no_vendor_calls": true' in printed
    assert '"no_db_writes": true' in printed

