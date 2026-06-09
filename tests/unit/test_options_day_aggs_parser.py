from __future__ import annotations

import gzip
from pathlib import Path

from app.vendor_flat_files.options.options_day_aggs_parser import (
    REQUIRED_COLUMNS,
    parse_opra_option_symbol,
    parse_options_day_aggs_quarantine_file,
)


def _write_gzip_csv(path: Path, *, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")


def test_parser_accepts_required_headers_and_streams_rows(tmp_path) -> None:
    path = tmp_path / "options.csv.gz"
    _write_gzip_csv(
        path,
        header=list(REQUIRED_COLUMNS),
        rows=[
            ["O:SPY251107C00670000", "10", "1.5", "1.6", "1.7", "1.4", "1762318800000000000", "2"],
            ["O:AAPL251107P00200000", "11", "2.5", "2.6", "2.7", "2.4", "1762318800000000000", "3"],
        ],
    )
    parsed = parse_options_day_aggs_quarantine_file(input_path=path, source_file_sha256="abc")
    assert parsed.parse_status == "PASS"
    assert parsed.header_columns == REQUIRED_COLUMNS
    assert parsed.row_count == 2
    assert parsed.rows[0]["row_number"] == 2
    assert parsed.rows[1]["row_number"] == 3
    assert parsed.rows[0]["volume"] == 10
    assert parsed.rows[0]["transactions"] == 2
    assert str(parsed.rows[0]["open"]) == "1.5"
    assert parsed.rows[0]["trade_date"] == "2025-11-05"


def test_parser_rejects_missing_required_headers(tmp_path) -> None:
    path = tmp_path / "bad.csv.gz"
    _write_gzip_csv(path, header=["ticker", "volume"], rows=[["O:SPY251107C00670000", "10"]])
    parsed = parse_options_day_aggs_quarantine_file(input_path=path)
    assert parsed.parse_status == "FAIL"
    assert any(error.code == "REQUIRED_HEADER_MISMATCH" for error in parsed.errors)


def test_parser_parses_opra_examples_and_malformed_symbols() -> None:
    spy = parse_opra_option_symbol("O:SPY251107C00670000")
    aapl = parse_opra_option_symbol("O:AAPL251107P00200000")
    bad = parse_opra_option_symbol("BAD")
    assert spy.parse_ok is True
    assert spy.underlying_symbol == "SPY"
    assert spy.expiration_date == "2025-11-07"
    assert spy.option_type == "C"
    assert str(spy.strike_price) == "670"
    assert aapl.parse_ok is True
    assert aapl.underlying_symbol == "AAPL"
    assert aapl.expiration_date == "2025-11-07"
    assert aapl.option_type == "P"
    assert bad.parse_ok is False
    assert bad.underlying_symbol is None

