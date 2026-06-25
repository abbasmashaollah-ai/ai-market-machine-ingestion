from __future__ import annotations

import inspect
import json
from pathlib import Path
from unittest.mock import patch

from app.handoff.news_sentiment_handoff import (
    DEFAULT_FIXTURE_BATCH_METADATA,
    DEFAULT_FIXTURE_RECORDS,
    read_news_sentiment_handoff_jsonl,
    validate_news_sentiment_record,
    write_news_sentiment_handoff_jsonl,
)
from app.warehouse.news_sentiment_handoff_acceptance import import_news_sentiment_handoff_jsonl


def _record() -> dict[str, object]:
    return dict(DEFAULT_FIXTURE_RECORDS[0])


def test_helper_has_no_data_orm_dependency() -> None:
    import app.warehouse.news_sentiment_handoff_acceptance as helper_module

    source = inspect.getsource(helper_module)
    assert "app.database" not in source
    assert "sqlalchemy.orm" not in source


def test_round_trip_handoff_jsonl_uses_ingestion_owned_handoff_contract(tmp_path: Path) -> None:
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


def test_validate_minimal_record_and_idempotency_are_ingestion_owned() -> None:
    result = validate_news_sentiment_record(_record())
    assert result.accepted is True
    assert result.record is not None
    assert result.idempotency_key
    assert result.idempotency_components is not None
    assert result.record["vendor"] == "fixture_vendor"
    assert result.record["raw_sentiment_label"] == "positive"
    assert result.record["raw_sentiment_score"] == 0.7


def test_validation_rejections_do_not_require_database_access() -> None:
    record = _record()
    record.pop("headline")
    result = validate_news_sentiment_record(record)
    assert result.accepted is False
    assert "headline is required" in result.rejection_reasons


def test_strategy_fields_are_rejected_without_strategy_logic() -> None:
    record = _record()
    record["buy_signal"] = True
    result = validate_news_sentiment_record(record)
    assert result.accepted is False
    assert "strategy fields are not allowed in ingestion handoff" in result.rejection_reasons


def test_writer_quarantines_invalid_records_without_vendor_or_db_side_effects(tmp_path: Path) -> None:
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


def test_no_internal_commit_or_vendor_calls_are_performed(tmp_path: Path) -> None:
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


def test_boundary_helper_can_parse_and_report_without_db_writes(tmp_path: Path) -> None:
    input_path = tmp_path / "news.jsonl"
    input_path.write_text(json.dumps(dict(DEFAULT_FIXTURE_RECORDS[0])) + "\n", encoding="utf-8")
    summary = import_news_sentiment_handoff_jsonl(input_path)
    assert summary.records_parsed == 1
    assert summary.records_accepted == 1
    assert summary.records_written == 0
    assert summary.records_rejected == 0
