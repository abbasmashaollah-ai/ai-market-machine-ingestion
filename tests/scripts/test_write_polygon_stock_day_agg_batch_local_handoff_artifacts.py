from __future__ import annotations

import gzip
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import scripts.write_polygon_stock_day_agg_batch_local_handoff_artifacts as cli


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


def test_no_approval_blocks_and_writes_nothing(tmp_path) -> None:
    input_dir = tmp_path / "quarantine"
    input_path = input_dir / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"],
        rows=[["SPY", "2026-06-15", "1", "2", "0.5", "1.5", "10", "1"]],
    )
    output_dir = tmp_path / "blocked" / "polygon_stock_day_aggs"
    payload = _run_cli(
        [
            "--input-dir",
            str(input_dir),
            "--start-date",
            "2026-06-15",
            "--end-date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
        ]
    )
    assert payload["approval_phrase_matched"] is False
    assert payload["local_handoff_write_authorized"] is False
    assert "manifest_path" not in payload
    assert "manifest_exists" not in payload
    assert not (output_dir / "polygon_stock_day_aggs_batch_2026-06-15_2026-06-15_manifest.json").exists()


def test_approved_batch_writes_per_date_outputs_and_manifest(tmp_path) -> None:
    input_dir = tmp_path / "quarantine"
    input_path = input_dir / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"],
        rows=[["SPY", "2026-06-15", "1", "2", "0.5", "1.5", "10", "1"]],
    )
    output_dir = Path("outputs") / "handoff_candidates" / "polygon_stock_day_aggs"
    payload = _run_cli(
        [
            "--input-dir",
            str(input_dir),
            "--start-date",
            "2026-06-15",
            "--end-date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
            "--approve-local-handoff-write",
            "--approval-phrase",
            "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE",
        ]
    )
    manifest_path = Path(payload["manifest_path"])
    assert payload["approval_phrase_matched"] is True
    assert payload["local_handoff_write_authorized"] is True
    assert payload["requested_date_count"] == 1
    assert payload["local_files_found_count"] == 1
    assert payload["local_files_missing_count"] == 0
    assert payload["total_rows_written"] == 1
    assert payload["total_rows_rejected"] == 0
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["total_rows_written"] == 1
    assert manifest["per_date_outputs"][0]["row_count_written"] == 1
    summary_path = Path(manifest["per_date_outputs"][0]["summary_path"])
    rows_path = Path(manifest["per_date_outputs"][0]["rows_path"])
    assert summary_path.exists()
    assert rows_path.exists()


def test_output_dir_outside_approved_path_is_refused(tmp_path) -> None:
    input_dir = tmp_path / "quarantine"
    input_path = input_dir / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "window_start", "open", "high", "low", "close", "volume", "transactions"],
        rows=[["SPY", "2026-06-15", "1", "2", "0.5", "1.5", "10", "1"]],
    )
    output_dir = tmp_path / "not_allowed"
    payload = _run_cli(
        [
            "--input-dir",
            str(input_dir),
            "--start-date",
            "2026-06-15",
            "--end-date",
            "2026-06-15",
            "--output-dir",
            str(output_dir),
            "--approve-local-handoff-write",
            "--approval-phrase",
            "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE",
        ]
    )
    assert payload["approval_phrase_matched"] is False
    assert payload["local_handoff_write_authorized"] is False
    assert "output_dir must be within" in payload["blockers"][-1]
