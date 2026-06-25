from __future__ import annotations

import gzip
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import scripts.write_polygon_stock_day_agg_local_handoff_artifact as cli


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


def test_default_no_approval_blocks_and_writes_nothing(tmp_path) -> None:
    output_dir = tmp_path / "blocked" / "polygon_stock_day_aggs"
    payload = _run_cli(
        [
            "--file",
            str(tmp_path / "missing.csv.gz"),
            "--date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
        ]
    )
    assert payload["local_handoff_write_attempted"] is False
    assert payload["local_handoff_write_authorized"] is False
    assert payload["output_summary_exists"] is False
    assert payload["output_rows_exists"] is False
    assert not Path(payload["output_summary_path"]).exists()
    assert not Path(payload["output_rows_path"]).exists()
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False


def test_wrong_approval_phrase_blocks_and_writes_nothing(tmp_path) -> None:
    input_path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"],
        rows=[["SPY", "2026-06-15", "1", "2", "0.5", "1.5", "10", "1"]],
    )
    output_dir = Path("outputs") / "handoff_candidates" / "polygon_stock_day_aggs" / "wrong_approval_test"
    payload = _run_cli(
        [
            "--file",
            str(input_path),
            "--date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
            "--approve-local-handoff-write",
            "--approval-phrase",
            "WRONG",
        ]
    )
    assert payload["local_handoff_write_attempted"] is False
    assert payload["local_handoff_write_authorized"] is False
    assert payload["output_summary_exists"] is False
    assert payload["output_rows_exists"] is False
    assert not Path(payload["output_summary_path"]).exists()
    assert not Path(payload["output_rows_path"]).exists()


def test_approved_run_writes_summary_and_rows(tmp_path) -> None:
    input_path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"],
        rows=[
            ["SPY", "2026-06-15", "100", "101", "99", "100.5", "12345", "10"],
            ["XLB", "2026-06-15", "20", "21", "19", "20.1", "2345", "4"],
        ],
    )
    output_dir = Path("outputs") / "handoff_candidates" / "polygon_stock_day_aggs"
    payload = _run_cli(
        [
            "--file",
            str(input_path),
            "--date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
            "--approve-local-handoff-write",
            "--approval-phrase",
            "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE",
        ]
    )
    summary_path = Path(payload["output_summary_path"])
    rows_path = Path(payload["output_rows_path"])
    assert payload["local_handoff_write_attempted"] is True
    assert payload["local_handoff_write_authorized"] is True
    assert payload["output_summary_exists"] is True
    assert payload["output_rows_exists"] is True
    assert summary_path.exists()
    assert rows_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["dataset"] == "ohlcv_equity_daily"
    assert summary["source_vendor"] == "polygon_massive_flat_files"
    assert summary["source_dataset"] == "polygon_stocks_day_aggs"
    assert summary["preview_or_local_handoff_only"] is True
    rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 2
    assert rows[0]["symbol"] == "SPY"
    assert rows[0]["preview_or_local_handoff_only"] is True
    assert rows[0]["source_file_sha256"] == summary["source_file_sha256"]
    assert rows[0]["source_file_size_bytes"] == summary["source_file_size_bytes"]
    assert rows[0]["adjusted"] is False
    assert rows[0]["adjustment_status"] == "unknown_or_vendor_default"
    assert rows[0]["adjusted_status"] == "unknown_or_vendor_default"
    assert rows[0]["lineage_id"] == summary["lineage_id"]
    assert rows[0]["idempotency_key"]
    assert payload["row_count_written"] == 2
    assert payload["rejected_row_count"] == 0
    assert payload["benchmark_symbol_present"] is True
    assert payload["required_sector_symbols_present"] == ["XLB"]


def test_output_dir_outside_approved_path_is_refused(tmp_path) -> None:
    input_path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"],
        rows=[["SPY", "2026-06-15", "1", "2", "0.5", "1.5", "10", "1"]],
    )
    output_dir = tmp_path / "not_allowed"
    payload = _run_cli(
        [
            "--file",
            str(input_path),
            "--date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
            "--approve-local-handoff-write",
            "--approval-phrase",
            "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE",
        ]
    )
    assert payload["local_handoff_write_attempted"] is False
    assert payload["local_handoff_write_authorized"] is False
    assert payload["output_summary_exists"] is False
    assert payload["output_rows_exists"] is False


def test_malformed_rows_are_rejected_and_counted(tmp_path) -> None:
    input_path = tmp_path / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"],
        rows=[
            ["SPY", "2026-06-15", "bad", "2", "0.5", "1.5", "10", "1"],
            ["XLB", "2026-06-15", "1", "2", "0.5", "oops", "10", "x"],
        ],
    )
    output_dir = Path("outputs") / "handoff_candidates" / "polygon_stock_day_aggs"
    payload = _run_cli(
        [
            "--file",
            str(input_path),
            "--date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
            "--approve-local-handoff-write",
            "--approval-phrase",
            "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE",
        ]
    )
    assert payload["row_count_written"] == 0
    assert payload["rejected_row_count"] == 2
    assert payload["output_summary_exists"] is True
    assert payload["output_rows_exists"] is True
    summary = json.loads(Path(payload["output_summary_path"]).read_text(encoding="utf-8"))
    assert summary["rejected_row_count"] == 2
    assert summary["rejection_reasons_summary"]["invalid_open"] == 1
    assert summary["rejection_reasons_summary"]["invalid_close"] == 1


def test_help_mentions_required_flags() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/write_polygon_stock_day_agg_local_handoff_artifact.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--file" in result.stdout
    assert "--date" in result.stdout
    assert "--output-dir" in result.stdout
    assert "--approve-local-handoff-write" in result.stdout
