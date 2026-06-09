from __future__ import annotations

import csv
import gzip
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_INSPECT_PATH = Path("outputs/quarantine/options_flat_files/massive_options_day_aggs_2025-11-05.csv.gz")
DEFAULT_SAMPLE_ROWS = 3


@dataclass(frozen=True, slots=True)
class OptionsDayAggsInspectionResult:
    input_path: str
    input_file_exists: bool
    input_file_size_bytes: int
    input_sha256: str
    gzip_open_attempted: bool
    csv_header_read_attempted: bool
    row_count_attempted: bool
    row_count: int
    header_columns: tuple[str, ...]
    header_column_count: int
    safe_sample_rows_attempted: bool
    safe_sample_rows_count: int
    safe_sample_rows: tuple[dict[str, object], ...]
    vendor_call_attempted: bool
    download_attempted: bool
    decompression_export_attempted: bool
    parse_to_domain_records_attempted: bool
    normalization_attempted: bool
    handoff_export_attempted: bool
    db_read_attempted: bool
    db_write_attempted: bool
    ingestion_attempted: bool
    scheduler_activation_attempted: bool
    production_mutation_attempted: bool
    blockers: tuple[str, ...]
    next_allowed_step: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_column_summary(columns: list[str], row: dict[str, str]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for column in columns:
        value = row.get(column, "")
        if column.lower() in {"symbol", "option_symbol", "underlying_symbol", "ticker", "date", "expiration_date", "strike", "type", "side"}:
            summary[column] = value
        else:
            text = str(value)
            summary[column] = text if len(text) <= 32 else text[:29] + "..."
    return summary


def inspect_options_day_aggs_quarantine_file(*, input_path: str | Path = DEFAULT_INSPECT_PATH, sample_rows_limit: int = DEFAULT_SAMPLE_ROWS) -> dict[str, object]:
    path = Path(input_path)
    blockers = [
        "no vendor call, download, normalization, handoff export, DB read/write, ingestion, scheduler activation, or production mutation is permitted",
    ]
    file_exists = path.exists()
    file_size = path.stat().st_size if file_exists else 0
    input_sha256 = sha256_file(path) if file_exists else ""
    gzip_open_attempted = False
    csv_header_read_attempted = False
    row_count_attempted = False
    row_count = 0
    header_columns: list[str] = []
    samples: list[dict[str, object]] = []
    safe_sample_rows_attempted = False

    if not file_exists:
        blockers.append("input file is missing")
        return {
            "input_path": str(path),
            "input_file_exists": False,
            "input_file_size_bytes": 0,
            "input_sha256": "",
            "gzip_open_attempted": False,
            "csv_header_read_attempted": False,
            "row_count_attempted": False,
            "row_count": 0,
            "header_columns": [],
            "header_column_count": 0,
            "safe_sample_rows_attempted": False,
            "safe_sample_rows_count": 0,
            "safe_sample_rows": [],
            "vendor_call_attempted": False,
            "download_attempted": False,
            "decompression_export_attempted": False,
            "parse_to_domain_records_attempted": False,
            "normalization_attempted": False,
            "handoff_export_attempted": False,
            "db_read_attempted": False,
            "db_write_attempted": False,
            "ingestion_attempted": False,
            "scheduler_activation_attempted": False,
            "production_mutation_attempted": False,
            "blockers": blockers,
            "next_allowed_step": "download the approved quarantine file, then rerun local inspection",
        }

    try:
        gzip_open_attempted = True
        csv_header_read_attempted = True
        row_count_attempted = True
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            header_columns = list(reader.fieldnames or [])
            safe_sample_rows_attempted = True
            for index, row in enumerate(reader, start=1):
                row_count += 1
                if len(samples) < sample_rows_limit:
                    samples.append(_safe_column_summary(header_columns, row))
    except Exception as exc:
        blockers.append(f"inspection failed safely: {exc.__class__.__name__}")
        return {
            "input_path": str(path),
            "input_file_exists": True,
            "input_file_size_bytes": file_size,
            "input_sha256": input_sha256,
            "gzip_open_attempted": gzip_open_attempted,
            "csv_header_read_attempted": csv_header_read_attempted,
            "row_count_attempted": row_count_attempted,
            "row_count": 0,
            "header_columns": [],
            "header_column_count": 0,
            "safe_sample_rows_attempted": safe_sample_rows_attempted,
            "safe_sample_rows_count": 0,
            "safe_sample_rows": [],
            "vendor_call_attempted": False,
            "download_attempted": False,
            "decompression_export_attempted": False,
            "parse_to_domain_records_attempted": False,
            "normalization_attempted": False,
            "handoff_export_attempted": False,
            "db_read_attempted": False,
            "db_write_attempted": False,
            "ingestion_attempted": False,
            "scheduler_activation_attempted": False,
            "production_mutation_attempted": False,
            "blockers": blockers,
            "next_allowed_step": "review the local inspection output only",
        }

    return {
        "input_path": str(path),
        "input_file_exists": True,
        "input_file_size_bytes": file_size,
        "input_sha256": input_sha256,
        "gzip_open_attempted": gzip_open_attempted,
        "csv_header_read_attempted": csv_header_read_attempted,
        "row_count_attempted": row_count_attempted,
        "row_count": row_count,
        "header_columns": header_columns,
        "header_column_count": len(header_columns),
        "safe_sample_rows_attempted": safe_sample_rows_attempted,
        "safe_sample_rows_count": len(samples),
        "safe_sample_rows": samples,
        "vendor_call_attempted": False,
        "download_attempted": False,
        "decompression_export_attempted": False,
        "parse_to_domain_records_attempted": False,
        "normalization_attempted": False,
        "handoff_export_attempted": False,
        "db_read_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "blockers": blockers,
        "next_allowed_step": "review the local inspection output only",
    }
