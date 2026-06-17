from __future__ import annotations

import gzip
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import scripts.validate_polygon_stock_day_agg_local_handoff_artifacts as cli


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _run_cli(argv: list[str]) -> dict[str, object]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def _build_fixture(tmp_path: Path) -> Path:
    output_root = tmp_path / "outputs" / "handoff_candidates" / "polygon_stock_day_aggs"
    summary_path = output_root / "polygon_stock_day_aggs_2026-06-15_summary.json"
    rows_path = output_root / "polygon_stock_day_aggs_2026-06-15_rows.jsonl"
    manifest_path = output_root / "polygon_stock_day_aggs_batch_2026-06-15_2026-06-15_manifest.json"
    source_path = tmp_path / "quarantine" / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(source_path, "wt", encoding="utf-8", newline="") as handle:
        handle.write("ticker,window_start,open,high,low,close,volume,transactions\n")
        handle.write("SPY,2026-06-15,1,2,0.5,1.5,10,1\n")
    row = {
        "dataset": "ohlcv_equity_daily",
        "source_vendor": "polygon_massive_flat_files",
        "source_dataset": "polygon_stocks_day_aggs",
        "asset_type": "equity_or_etf_unknown_at_ingestion",
        "symbol": "SPY",
        "trade_date": "2026-06-15",
        "open": 1.0,
        "high": 2.0,
        "low": 0.5,
        "close": 1.5,
        "volume": 10.0,
        "transactions": 1,
        "adjusted_status": "unknown_or_vendor_default",
        "source_file_sha256": "abc",
        "source_file_size_bytes": 147,
        "source_quarantine_path": str(source_path),
        "preview_or_local_handoff_only": True,
    }
    _write_json(summary_path, {
        "dataset": "ohlcv_equity_daily",
        "source_vendor": "polygon_massive_flat_files",
        "source_dataset": "polygon_stocks_day_aggs",
        "production_approved": False,
        "db_write_attempted": False,
        "vendor_call_attempted": False,
        "download_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "row_count_written": 1,
        "rejected_row_count": 0,
    })
    _write_jsonl(rows_path, [row])
    _write_json(manifest_path, {
        "start_date": "2026-06-15",
        "end_date": "2026-06-15",
        "per_date_outputs": [
            {"summary_path": str(summary_path), "rows_path": str(rows_path), "row_count_written": 1, "rejected_row_count": 0}
        ],
        "total_rows_written": 1,
        "total_rows_rejected": 0,
    })
    return manifest_path


def test_valid_fixture_passes(tmp_path) -> None:
    manifest_path = _build_fixture(tmp_path)
    payload = _run_cli(["--manifest", str(manifest_path)])
    assert payload["manifest_exists"] is True
    assert payload["manifest_valid"] is True
    assert payload["validation_passed"] is True
    assert payload["total_rows_expected"] == 1
    assert payload["total_rows_observed"] == 1
    assert payload["validation_errors"] == []
    assert payload["date_artifact_count_checked"] == 1


def test_missing_rows_file_fails_safely(tmp_path) -> None:
    manifest_path = _build_fixture(tmp_path)
    rows_path = tmp_path / "outputs" / "handoff_candidates" / "polygon_stock_day_aggs" / "polygon_stock_day_aggs_2026-06-15_rows.jsonl"
    rows_path.unlink()
    payload = _run_cli(["--manifest", str(manifest_path)])
    assert payload["manifest_exists"] is True
    assert payload["validation_passed"] is False
    assert any("missing_rows" in error for error in payload["validation_errors"])


def test_row_missing_required_field_fails_safely(tmp_path) -> None:
    manifest_path = _build_fixture(tmp_path)
    rows_path = tmp_path / "outputs" / "handoff_candidates" / "polygon_stock_day_aggs" / "polygon_stock_day_aggs_2026-06-15_rows.jsonl"
    row = json.loads(rows_path.read_text(encoding="utf-8").splitlines()[0])
    row.pop("symbol")
    _write_jsonl(rows_path, [row])
    payload = _run_cli(["--manifest", str(manifest_path)])
    assert payload["validation_passed"] is False
    assert "row_missing_required_field" in payload["validation_errors"]


def test_summary_rows_mismatch_fails_safely(tmp_path) -> None:
    manifest_path = _build_fixture(tmp_path)
    summary_path = tmp_path / "outputs" / "handoff_candidates" / "polygon_stock_day_aggs" / "polygon_stock_day_aggs_2026-06-15_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["row_count_written"] = 2
    _write_json(summary_path, summary)
    payload = _run_cli(["--manifest", str(manifest_path)])
    assert payload["validation_passed"] is False
    assert "row_count_mismatch:polygon_stock_day_aggs_2026-06-15_summary.json" in payload["validation_errors"]
