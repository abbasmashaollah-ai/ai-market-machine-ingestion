from __future__ import annotations

import gzip
import json
from pathlib import Path

from app.vendor_flat_files.options.options_day_aggs_inspector import DEFAULT_INSPECT_PATH, inspect_options_day_aggs_quarantine_file, sha256_file


def _write_gzip_csv(path: Path, *, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")


def test_missing_input_file_returns_safe_json(tmp_path) -> None:
    payload = inspect_options_day_aggs_quarantine_file(input_path=tmp_path / "missing.csv.gz")
    assert payload["input_file_exists"] is False
    assert payload["row_count"] == 0
    assert payload["safe_sample_rows_count"] == 0
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False


def test_valid_small_gzip_csv_returns_header_row_count_samples_and_sha256(tmp_path) -> None:
    path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    _write_gzip_csv(
        path,
        header=["contract_symbol", "symbol", "date", "strike", "type", "bid", "ask"],
        rows=[
            ["OPT1", "SPY", "2025-11-05", "600", "call", "1.25", "1.30"],
            ["OPT2", "QQQ", "2025-11-05", "500", "put", "0.95", "1.05"],
            ["OPT3", "IWM", "2025-11-05", "250", "call", "2.10", "2.20"],
            ["OPT4", "XLF", "2025-11-05", "40", "put", "0.55", "0.60"],
        ],
    )
    payload = inspect_options_day_aggs_quarantine_file(input_path=path, sample_rows_limit=3)
    assert payload["input_file_exists"] is True
    assert payload["input_file_size_bytes"] == path.stat().st_size
    assert payload["input_sha256"] == sha256_file(path)
    assert payload["gzip_open_attempted"] is True
    assert payload["csv_header_read_attempted"] is True
    assert payload["row_count_attempted"] is True
    assert payload["row_count"] == 4
    assert payload["header_columns"] == ["contract_symbol", "symbol", "date", "strike", "type", "bid", "ask"]
    assert payload["header_column_count"] == 7
    assert payload["safe_sample_rows_count"] == 3
    assert len(payload["safe_sample_rows"]) == 3
    assert payload["safe_sample_rows"][0]["symbol"] == "SPY"
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["decompression_export_attempted"] is False
    assert payload["parse_to_domain_records_attempted"] is False
    assert payload["normalization_attempted"] is False
    assert payload["handoff_export_attempted"] is False
    assert payload["db_read_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False
    text = json.dumps(payload).lower()
    for forbidden in ["endpoint.invalid", "bucket", "prefix", "us_options_opra/day_aggs_v1", "etag", "secret"]:
        assert forbidden not in text


def test_sample_row_count_is_capped(tmp_path) -> None:
    path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    _write_gzip_csv(
        path,
        header=["contract_symbol", "symbol", "date"],
        rows=[[f"OPT{i}", "SPY", "2025-11-05"] for i in range(10)],
    )
    payload = inspect_options_day_aggs_quarantine_file(input_path=path, sample_rows_limit=2)
    assert payload["safe_sample_rows_count"] == 2
    assert len(payload["safe_sample_rows"]) == 2


def test_default_path_points_at_expected_quarantine_location() -> None:
    assert str(DEFAULT_INSPECT_PATH).endswith("massive_options_day_aggs_2025-11-05.csv.gz")
