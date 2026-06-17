from __future__ import annotations

import gzip
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.inspect_polygon_stock_day_agg_quarantine_file as cli


def _write_gzip_csv(path: Path, *, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")


def _run_cli(argv: list[str]) -> dict[str, object]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_missing_file_is_safe(tmp_path) -> None:
    payload = _run_cli(["--file", str(tmp_path / "missing.csv.gz"), "--date", "2026-06-15"])
    assert payload["local_file_exists"] is False
    assert payload["row_count"] == 0
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False


def test_valid_fixture_reports_headers_rows_symbols_and_date_match(tmp_path) -> None:
    path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    header = ["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"]
    rows = [
        ["SPY", "2026-06-15", "100", "101", "99", "100.5", "12345", "10"],
        ["XLB", "2026-06-15", "20", "21", "19", "20.1", "2345", "4"],
    ]
    _write_gzip_csv(path, header=header, rows=rows)
    payload = _run_cli(["--file", str(path), "--date", "2026-06-15"])
    assert payload["local_file_exists"] is True
    assert payload["header_fields"] == header
    assert payload["header_field_count"] == len(header)
    assert payload["row_count"] == 2
    assert payload["sampled_row_count"] == 2
    assert payload["benchmark_symbol_present"] is True
    assert "SPY" in payload["required_sector_symbols_present"] or payload["benchmark_symbol_present"] is True
    assert payload["date_matches_requested_date"] is True
    assert payload["min_date_seen"] == "2026-06-15"
    assert payload["max_date_seen"] == "2026-06-15"
    assert all(item["failed_count"] == 0 for item in payload["numeric_field_parse_summary"])
    text = json.dumps(payload).lower()
    for forbidden in ["endpoint", "bucket", "prefix", "etag", "us_stocks_sip/day_aggs_v1"]:
        assert forbidden not in text


def test_presence_logic_tracks_spy_and_sector_symbols(tmp_path) -> None:
    path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    header = ["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"]
    rows = [["SPY", "2026-06-15", "100", "101", "99", "100.5", "12345", "10"]]
    _write_gzip_csv(path, header=header, rows=rows)
    payload = _run_cli(["--file", str(path), "--date", "2026-06-15"])
    assert payload["benchmark_symbol_present"] is True
    assert payload["required_sector_symbols_present"] == []
    assert set(payload["required_sector_symbols_missing"]) == {"XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"}


def test_malformed_numeric_values_are_reported_safely(tmp_path) -> None:
    path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    header = ["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"]
    rows = [["SPY", "2026-06-15", "bad", "101", "99", "100.5", "oops", "10"]]
    _write_gzip_csv(path, header=header, rows=rows)
    payload = _run_cli(["--file", str(path), "--date", "2026-06-15"])
    open_summary = next(item for item in payload["numeric_field_parse_summary"] if item["field_name"] == "open")
    volume_summary = next(item for item in payload["numeric_field_parse_summary"] if item["field_name"] == "volume")
    assert open_summary["failed_count"] == 1
    assert volume_summary["failed_count"] == 1


def test_help_mentions_required_flags() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/inspect_polygon_stock_day_agg_quarantine_file.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--file" in result.stdout
    assert "--date" in result.stdout
