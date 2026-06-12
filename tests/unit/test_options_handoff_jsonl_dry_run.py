from __future__ import annotations

import socket
from pathlib import Path
from unittest.mock import patch

from app.options.options_handoff_jsonl import read_options_handoff_jsonl, write_options_handoff_jsonl


def _base_metadata() -> dict[str, object]:
    return {
        "source_dataset": "dry_run_options_handoff",
        "vendor": "fixture_vendor",
        "producer_run_id": "dry_run_options_handoff_run",
        "source_file_name": "dry_run_options_fixture.jsonl",
        "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "lineage": {"dry_run": True, "source": "fixture"},
        "warnings": [],
    }


def _base_contract() -> dict[str, object]:
    return {
        "contract_symbol": "O:SPY251205C00600000",
        "underlying_symbol": "SPY",
        "expiration_date": "2025-12-05",
        "strike_price": 600,
        "option_type": "C",
    }


def _build_batch() -> list[dict[str, object]]:
    contract = _base_contract()
    return [
        {
            **_base_metadata(),
            **contract,
            "source_dataset": "options_contracts_master",
        },
        {
            **_base_metadata(),
            **contract,
            "source_dataset": "options_open_interest",
            "observation_date": "2025-11-05",
            "open_interest": 12345,
        },
        {
            **_base_metadata(),
            **contract,
            "source_dataset": "options_greeks_iv",
            "observation_timestamp": "2025-11-05T16:00:00Z",
            "implied_volatility": 0.25,
            "delta": 0.50,
            "gamma": 0.02,
            "theta": -0.03,
            "vega": 0.12,
            "rho": 0.01,
            "mark_price": 5.25,
            "underlying_price": 600.00,
            "bid": 5.20,
            "ask": 5.30,
            "mid": 5.25,
        },
        {
            **_base_metadata(),
            **contract,
            "source_dataset": "options_day_aggregates",
            "trade_date": "2025-11-05",
            "open": 5.10,
            "high": 5.50,
            "low": 5.00,
            "close": 5.25,
            "volume": 100,
            "transactions": 10,
        },
    ]


def test_fixture_based_options_handoff_dry_run_round_trip(tmp_path: Path) -> None:
    output_path = tmp_path / "dry_run_options_handoff.jsonl"
    with patch("socket.create_connection") as network_mock:
        summary = write_options_handoff_jsonl(
            _build_batch(),
            output_path,
            producer_run_id="dry_run_options_handoff_run",
            source_dataset="dry_run_options_handoff",
            vendor="fixture_vendor",
            source_file_name="dry_run_options_fixture.jsonl",
            source_sha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            lineage={"dry_run": True, "source": "fixture"},
            warnings=[],
        )
    assert network_mock.called is False
    assert summary["attempted_count"] == 4
    assert summary["written_count"] == 4
    assert summary["rejected_count"] == 0
    assert summary["output_path"] == str(output_path)
    assert summary["producer_run_id"] == "dry_run_options_handoff_run"
    assert summary["source_dataset"] == "dry_run_options_handoff"
    assert summary["vendor"] == "fixture_vendor"
    assert summary["errors"] == ()
    assert output_path.exists()

    records = read_options_handoff_jsonl(output_path)
    assert len(records) == 4
    assert [record["source_dataset"] for record in records] == [
        "options_contracts_master",
        "options_open_interest",
        "options_greeks_iv",
        "options_day_aggregates",
    ]
    for record in records:
        assert record["vendor"] == "fixture_vendor"
        assert record["producer_run_id"] == "dry_run_options_handoff_run"
        assert record["source_sha256"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        assert record["lineage"] == {"dry_run": True, "source": "fixture"}
        assert record["warnings"] == []
        assert record["contract_symbol"] == "O:SPY251205C00600000"
        assert record["underlying_symbol"] == "SPY"
        assert record["expiration_date"] == "2025-12-05"
        assert record["strike_price"] == 600
        assert record["option_type"] == "C"

    assert records[1]["observation_date"] == "2025-11-05"
    assert records[1]["open_interest"] == 12345
    assert records[2]["observation_timestamp"] == "2025-11-05T16:00:00Z"
    assert records[2]["implied_volatility"] == 0.25
    assert records[2]["delta"] == 0.50
    assert records[2]["gamma"] == 0.02
    assert records[2]["theta"] == -0.03
    assert records[2]["vega"] == 0.12
    assert records[2]["rho"] == 0.01
    assert records[2]["mark_price"] == 5.25
    assert records[2]["underlying_price"] == 600.0
    assert records[2]["bid"] == 5.20
    assert records[2]["ask"] == 5.30
    assert records[2]["mid"] == 5.25
    assert records[3]["trade_date"] == "2025-11-05"
    assert records[3]["open"] == 5.10
    assert records[3]["high"] == 5.50
    assert records[3]["low"] == 5.00
    assert records[3]["close"] == 5.25
    assert records[3]["volume"] == 100
    assert records[3]["transactions"] == 10


def test_fixture_based_options_handoff_dry_run_rejects_invalid_record(tmp_path: Path) -> None:
    output_path = tmp_path / "dry_run_options_handoff.jsonl"
    batch = _build_batch()
    batch.insert(
        2,
        {
            **_base_metadata(),
            **_base_contract(),
            "source_dataset": "options_open_interest",
            "observation_date": "2025-11-05",
        },
    )

    summary = write_options_handoff_jsonl(
        batch,
        output_path,
        producer_run_id="dry_run_options_handoff_run",
        source_dataset="dry_run_options_handoff",
        vendor="fixture_vendor",
        source_file_name="dry_run_options_fixture.jsonl",
        source_sha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        lineage={"dry_run": True, "source": "fixture"},
        warnings=[],
    )

    assert summary["attempted_count"] == 5
    assert summary["written_count"] == 4
    assert summary["rejected_count"] == 1
    assert output_path.exists()
    assert "missing required field: open_interest" in summary["errors"][0]["errors"]
    records = read_options_handoff_jsonl(output_path)
    assert len(records) == 4
    assert [record["source_dataset"] for record in records] == [
        "options_contracts_master",
        "options_open_interest",
        "options_greeks_iv",
        "options_day_aggregates",
    ]
    assert records[1]["open_interest"] == 12345
    assert records[3]["trade_date"] == "2025-11-05"
