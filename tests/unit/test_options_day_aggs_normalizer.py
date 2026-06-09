from __future__ import annotations

import gzip
from pathlib import Path

from app.vendor_flat_files.options.options_day_aggs_normalizer import normalize_options_day_aggs_records
from app.vendor_flat_files.options.options_day_aggs_parser import parse_options_day_aggs_quarantine_file


def _write_gzip_csv(path: Path, *, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")


def test_normalizer_parses_contract_fields_and_lineage(tmp_path) -> None:
    path = tmp_path / "sample.csv.gz"
    _write_gzip_csv(
        path,
        header=["ticker", "volume", "open", "close", "high", "low", "window_start", "transactions"],
        rows=[["O:SPY251107C00670000", "10", "1.5", "1.6", "1.7", "1.4", "1762318800000000000", "2"]],
    )
    parsed = parse_options_day_aggs_quarantine_file(input_path=path, source_file_sha256="abc")
    normalized = normalize_options_day_aggs_records(parsed)
    assert normalized.normalization_status == "PASS"
    assert normalized.record_count == 1
    record = normalized.records[0]
    assert record["contract_symbol"] == "O:SPY251107C00670000"
    assert record["raw_ticker"] == "O:SPY251107C00670000"
    assert record["underlying_symbol"] == "SPY"
    assert record["expiration_date"] == "2025-11-07"
    assert str(record["strike_price"]) == "670"
    assert record["option_type"] == "C"
    assert record["trade_date"] == "2025-11-05"
    assert record["volume"] == 10
    assert record["transactions"] == 2
    assert record["source_dataset"] == "us_options_opra/day_aggs_v1"
    assert record["vendor"] == "polygon_or_massive"
    assert record["lineage"]["row_number"] == 2
    assert record["lineage"]["source_file_sha256"] == "abc"


def test_normalizer_handles_malformed_ticker_and_warns_on_high_low_order(tmp_path) -> None:
    path = tmp_path / "bad.csv.gz"
    _write_gzip_csv(
        path,
        header=["ticker", "volume", "open", "close", "high", "low", "window_start", "transactions"],
        rows=[
            ["BADTICKER", "3", "1.0", "1.1", "1.2", "0.9", "1762318800000000000", "1"],
            ["O:SPY251107C00670000", "4", "1.5", "1.6", "1.4", "1.7", "1762318800000000000", "2"],
        ],
    )
    parsed = parse_options_day_aggs_quarantine_file(input_path=path)
    normalized = normalize_options_day_aggs_records(parsed)
    assert normalized.record_count == 2
    assert normalized.records[0]["underlying_symbol"] is None
    assert normalized.records[0]["contract_symbol"] == "BADTICKER"
    assert any("symbol" in warning.lower() for warning in normalized.warnings)
    assert any("high lower than low" in warning.lower() for warning in normalized.warnings)


def test_normalizer_rejects_negative_volume_and_transactions(tmp_path) -> None:
    path = tmp_path / "negative.csv.gz"
    _write_gzip_csv(
        path,
        header=["ticker", "volume", "open", "close", "high", "low", "window_start", "transactions"],
        rows=[["O:SPY251107C00670000", "-1", "1.5", "1.6", "1.7", "1.4", "1762318800000000000", "-2"]],
    )
    parsed = parse_options_day_aggs_quarantine_file(input_path=path)
    normalized = normalize_options_day_aggs_records(parsed)
    assert normalized.record_count == 0
    assert any(error.code == "NEGATIVE_VOLUME" for error in normalized.errors)
