from __future__ import annotations

import socket
from pathlib import Path
from unittest.mock import patch

import pytest

from app.options.options_handoff_jsonl import (
    SUPPORTED_OPTIONS_HANDBACK_DOMAINS,
    read_options_handoff_jsonl,
    write_options_handoff_jsonl,
)


def _record(domain: str) -> dict[str, object]:
    base = {
        "source_dataset": domain,
        "vendor": "polygon",
        "producer_run_id": "run-123",
        "lineage": ["ingestion", "options"],
        "warnings": ["warn-a"],
    }
    if domain == "options_day_aggregates":
        base.update(
            {
                "contract_symbol": "OPT1",
                "underlying_symbol": "SPY",
                "expiration_date": "2026-01-16",
                "strike_price": 670,
                "option_type": "call",
                "trade_date": "2026-01-15",
                "open": 1,
                "high": 2,
                "low": 0.5,
                "close": 1.5,
                "volume": 10,
                "transactions": 2,
            }
        )
    elif domain == "options_contracts_master":
        base.update(
            {
                "contract_symbol": "OPT2",
                "underlying_symbol": "QQQ",
                "expiration_date": "2026-02-20",
                "strike_price": 500,
                "option_type": "put",
            }
        )
    elif domain == "options_open_interest":
        base.update(
            {
                "contract_symbol": "OPT3",
                "underlying_symbol": "IWM",
                "expiration_date": "2026-03-20",
                "strike_price": 250,
                "option_type": "call",
                "observation_date": "2026-01-15",
                "open_interest": 100,
            }
        )
    elif domain == "options_greeks_iv":
        base.update(
            {
                "contract_symbol": "OPT4",
                "underlying_symbol": "XLF",
                "expiration_date": "2026-04-17",
                "strike_price": 40,
                "option_type": "call",
                "observation_timestamp": "2026-01-15T16:00:00Z",
                "implied_volatility": 0.2,
            }
        )
    return base


def test_supported_domains_defined() -> None:
    assert set(SUPPORTED_OPTIONS_HANDBACK_DOMAINS) == {
        "options_day_aggregates",
        "options_contracts_master",
        "options_open_interest",
        "options_greeks_iv",
    }


def test_write_and_read_round_trip_preserves_order_and_metadata(tmp_path: Path) -> None:
    output_path = tmp_path / "handoff.jsonl"
    records = [_record("options_day_aggregates"), _record("options_contracts_master")]

    summary = write_options_handoff_jsonl(
        records,
        output_path,
        producer_run_id="run-123",
        source_dataset="options_day_aggregates",
        vendor="polygon",
        source_file_name="sample.csv",
        source_file_path="C:/safe/sample.csv",
        source_sha256="abc123",
    )

    assert summary["attempted_count"] == 2
    assert summary["written_count"] == 2
    assert summary["rejected_count"] == 0
    assert summary["producer_run_id"] == "run-123"
    assert summary["source_dataset"] == "options_day_aggregates"
    assert summary["vendor"] == "polygon"
    assert output_path.exists()

    round_tripped = read_options_handoff_jsonl(output_path)
    assert [item["contract_symbol"] for item in round_tripped] == ["OPT1", "OPT2"]
    assert round_tripped[0]["source_dataset"] == "options_day_aggregates"
    assert round_tripped[0]["vendor"] == "polygon"
    assert round_tripped[0]["producer_run_id"] == "run-123"
    assert round_tripped[0]["source_sha256"] == "abc123"
    assert round_tripped[0]["source_file_name"] == "sample.csv"
    assert round_tripped[0]["source_file_path"] == "C:/safe/sample.csv"
    assert round_tripped[0]["lineage"] == ["ingestion", "options"]
    assert round_tripped[0]["warnings"] == ["warn-a"]


def test_writer_rejects_missing_domain(tmp_path: Path) -> None:
    output_path = tmp_path / "handoff.jsonl"
    summary = write_options_handoff_jsonl(
        [{**_record("options_day_aggregates"), "source_dataset": None}],
        output_path,
        producer_run_id="run-123",
        source_dataset="options_day_aggregates",
        vendor="polygon",
    )
    assert summary["written_count"] == 0
    assert summary["rejected_count"] == 1
    assert "missing domain" in summary["errors"][0]["errors"]


def test_writer_rejects_unsupported_domain(tmp_path: Path) -> None:
    output_path = tmp_path / "handoff.jsonl"
    record = _record("options_day_aggregates")
    record["source_dataset"] = "unknown_domain"
    summary = write_options_handoff_jsonl([record], output_path, producer_run_id="run-123", source_dataset="options_day_aggregates", vendor="polygon")
    assert summary["written_count"] == 0
    assert summary["rejected_count"] == 1
    assert "unsupported domain: unknown_domain" in summary["errors"][0]["errors"]


def test_writer_rejects_missing_required_field(tmp_path: Path) -> None:
    output_path = tmp_path / "handoff.jsonl"
    record = _record("options_open_interest")
    record.pop("open_interest")
    summary = write_options_handoff_jsonl([record], output_path, producer_run_id="run-123", source_dataset="options_open_interest", vendor="polygon")
    assert summary["written_count"] == 0
    assert summary["rejected_count"] == 1
    assert "missing required field: open_interest" in summary["errors"][0]["errors"]


def test_reader_raises_clear_error_for_malformed_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"a": 1}\nnot-json\n', encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed JSONL at line 2"):
        read_options_handoff_jsonl(path)


def test_no_vendor_db_or_network_behavior(tmp_path: Path) -> None:
    output_path = tmp_path / "handoff.jsonl"
    record = _record("options_greeks_iv")
    with patch("socket.create_connection") as network_mock:
        write_options_handoff_jsonl([record], output_path, producer_run_id="run-123", source_dataset="options_greeks_iv", vendor="polygon")
    assert network_mock.called is False
