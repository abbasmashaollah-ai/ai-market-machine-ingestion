from __future__ import annotations

import gzip
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import scripts.preview_normalize_polygon_stock_day_agg_quarantine_file as cli


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
    assert payload["normalized_candidate_count"] == 0
    assert payload["rejected_row_count"] == 0
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False


def test_valid_fixture_normalizes_preview_rows_and_respects_sample_limit(tmp_path) -> None:
    path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    header = ["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"]
    rows = [
        ["SPY", "2026-06-15", "100", "101", "99", "100.5", "12345", "10"],
        ["XLB", "2026-06-15", "20", "21", "19", "20.1", "2345", "4"],
    ]
    _write_gzip_csv(path, header=header, rows=rows)
    payload = _run_cli(["--file", str(path), "--date", "2026-06-15", "--sample-limit", "1"])
    assert payload["raw_header_fields"] == header
    assert payload["raw_row_count"] == 2
    assert payload["normalized_candidate_count"] == 2
    assert payload["rejected_row_count"] == 0
    assert payload["benchmark_symbol_present"] is True
    assert payload["required_sector_symbols_present"] == ["XLB"]
    assert set(payload["required_sector_symbols_missing"]) == {"XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"}
    assert payload["trade_date_matches_requested_date"] is True
    assert payload["min_trade_date"] == "2026-06-15"
    assert payload["max_trade_date"] == "2026-06-15"
    assert len(payload["sample_normalized_rows"]) == 1
    sample = payload["sample_normalized_rows"][0]
    assert sample["symbol"] == "SPY"
    assert sample["trade_date"] == "2026-06-15"
    assert sample["source_dataset"] == "polygon_stocks_day_aggs"
    assert sample["source_vendor"] == "polygon_massive_flat_files"
    assert sample["adjusted_status"] == "unknown_or_vendor_default"
    assert sample["preview_only"] is True
    assert sample["open"] == 100.0
    assert sample["volume"] == 12345.0
    assert payload["numeric_validation_summary"]["open"]["failed_count"] == 0
    assert payload["numeric_validation_summary"]["transactions"]["failed_count"] == 0
    text = json.dumps(payload).lower()
    for forbidden in ["endpoint", "bucket", "prefix", "etag", "us_stocks_sip/day_aggs_v1"]:
        assert forbidden not in text


def test_malformed_numeric_values_are_rejected_and_counted(tmp_path) -> None:
    path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    header = ["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"]
    rows = [
        ["SPY", "2026-06-15", "bad", "101", "99", "100.5", "12345", "10"],
        ["XLB", "2026-06-15", "20", "21", "19", "oops", "2345", "x"],
    ]
    _write_gzip_csv(path, header=header, rows=rows)
    payload = _run_cli(["--file", str(path), "--date", "2026-06-15"])
    assert payload["normalized_candidate_count"] == 0
    assert payload["rejected_row_count"] == 2
    assert payload["rejection_reasons_summary"]["invalid_open"] == 1
    assert payload["rejection_reasons_summary"]["invalid_close"] == 1
    assert payload["rejection_reasons_summary"]["invalid_transactions"] == 1


def test_help_mentions_required_flags() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/preview_normalize_polygon_stock_day_agg_quarantine_file.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--file" in result.stdout
    assert "--date" in result.stdout
    assert "--sample-limit" in result.stdout
