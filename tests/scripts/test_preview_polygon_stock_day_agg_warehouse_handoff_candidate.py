from __future__ import annotations

import gzip
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import scripts.preview_polygon_stock_day_agg_warehouse_handoff_candidate as cli


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
    assert payload["handoff_candidate_count"] == 0
    assert payload["rejected_row_count"] == 0
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["handoff_export_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False


def test_valid_fixture_produces_handoff_candidates_and_respects_sample_limit(tmp_path) -> None:
    path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    header = ["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"]
    rows = [
        ["SPY", "2026-06-15", "100", "101", "99", "100.5", "12345", "10"],
        ["XLB", "2026-06-15", "20", "21", "19", "20.1", "2345", "4"],
    ]
    _write_gzip_csv(path, header=header, rows=rows)
    payload = _run_cli(["--file", str(path), "--date", "2026-06-15", "--sample-limit", "1"])
    assert payload["candidate_dataset"] == "ohlcv_equity_daily"
    assert payload["candidate_source_vendor"] == "polygon_massive_flat_files"
    assert payload["candidate_source_dataset"] == "polygon_stocks_day_aggs"
    assert payload["handoff_candidate_count"] == 2
    assert payload["normalized_candidate_count"] == 2
    assert len(payload["sample_handoff_candidate_rows"]) == 1
    sample = payload["sample_handoff_candidate_rows"][0]
    assert sample["dataset"] == "ohlcv_equity_daily"
    assert sample["source_vendor"] == "polygon_massive_flat_files"
    assert sample["source_dataset"] == "polygon_stocks_day_aggs"
    assert sample["asset_type"] == "equity_or_etf_unknown_at_ingestion"
    assert sample["symbol"] == "SPY"
    assert sample["trade_date"] == "2026-06-15"
    assert sample["preview_only"] is True
    assert payload["candidate_field_names"] == [
        "dataset",
        "source_vendor",
        "source_dataset",
        "asset_type",
        "symbol",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "transactions",
        "adjusted_status",
        "source_file_sha256",
        "source_file_size_bytes",
        "quarantine_path",
        "preview_only",
    ]
    assert payload["benchmark_symbol_present"] is True
    assert payload["required_sector_symbols_present"] == ["XLB"]
    assert set(payload["required_sector_symbols_missing"]) == {"XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"}


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
    assert payload["handoff_candidate_count"] == 0
    assert payload["rejected_row_count"] == 2
    assert payload["rejection_reasons_summary"]["invalid_open"] == 1
    assert payload["rejection_reasons_summary"]["invalid_close"] == 1
    assert payload["rejection_reasons_summary"]["invalid_transactions"] == 1


def test_help_mentions_required_flags() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/preview_polygon_stock_day_agg_warehouse_handoff_candidate.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--file" in result.stdout
    assert "--date" in result.stdout
    assert "--sample-limit" in result.stdout
