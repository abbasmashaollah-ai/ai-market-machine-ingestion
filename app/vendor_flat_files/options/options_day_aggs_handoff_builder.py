from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from .options_day_aggs_normalizer import normalize_options_day_aggs_records
from .options_day_aggs_parser import parse_options_day_aggs_quarantine_file

APPROVAL_PHRASE = "APPROVE OPTIONS DAY AGGS SAMPLE HANDOFF BUILD"
DEFAULT_INPUT_PATH = Path("outputs/quarantine/options_flat_files/massive_options_day_aggs_2025-11-05.csv.gz")
DEFAULT_OUTPUT_PATH = Path("outputs/handoff/options_day_aggs/options_day_aggs_2025-11-05_sample.jsonl")
DEFAULT_SAMPLE_LIMIT = 100
MAX_SAMPLE_LIMIT = 1000


@dataclass(frozen=True, slots=True)
class OptionsDayAggsHandoffSampleResult:
    approval_required: bool
    approval_phrase_matched: bool
    input_path: str
    input_file_exists: bool
    input_file_size_bytes: int
    input_sha256: str
    output_path: str
    output_file_exists: bool
    output_file_size_bytes: int
    output_sha256: str
    requested_sample_limit: int
    effective_sample_limit: int
    records_written: int
    source_rows_scanned: int
    warning_count: int
    vendor_call_attempted: bool
    download_attempted: bool
    handoff_export_attempted: bool
    production_export_attempted: bool
    db_read_attempted: bool
    db_write_attempted: bool
    ingestion_attempted: bool
    scheduler_activation_attempted: bool
    production_mutation_attempted: bool
    blockers: tuple[str, ...]
    next_allowed_step: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(_json_safe(record), sort_keys=True, ensure_ascii=False))
            handle.write("\n")


def build_options_day_aggs_handoff_sample(
    *,
    approval_phrase: str = "",
    input_path: str | Path = DEFAULT_INPUT_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    requested_sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, object]:
    input_path = Path(input_path)
    output_path = Path(output_path)
    approval_phrase_matched = approval_phrase == APPROVAL_PHRASE
    effective_sample_limit = max(1, min(int(requested_sample_limit), MAX_SAMPLE_LIMIT))
    input_file_exists = input_path.exists()
    input_file_size_bytes = input_path.stat().st_size if input_file_exists else 0
    input_sha256 = _sha256_file(input_path) if input_file_exists else ""
    blockers: list[str] = []
    if not input_file_exists:
        blockers.append("input file is missing")
    if not approval_phrase_matched:
        blockers.append("approval phrase did not match")

    if not approval_phrase_matched or not input_file_exists:
        return {
            "approval_required": True,
            "approval_phrase_matched": approval_phrase_matched,
            "input_path": str(input_path),
            "input_file_exists": input_file_exists,
            "input_file_size_bytes": input_file_size_bytes,
            "input_sha256": input_sha256,
            "output_path": str(output_path),
            "output_file_exists": output_path.exists(),
            "output_file_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
            "output_sha256": _sha256_file(output_path) if output_path.exists() else "",
            "requested_sample_limit": int(requested_sample_limit),
            "effective_sample_limit": effective_sample_limit,
            "records_written": 0,
            "source_rows_scanned": 0,
            "warning_count": 0,
            "vendor_call_attempted": False,
            "download_attempted": False,
            "handoff_export_attempted": False,
            "production_export_attempted": False,
            "db_read_attempted": False,
            "db_write_attempted": False,
            "ingestion_attempted": False,
            "scheduler_activation_attempted": False,
            "production_mutation_attempted": False,
            "blockers": blockers,
            "next_allowed_step": "provide the exact approval phrase and rerun the sample handoff build",
        }

    parsed = parse_options_day_aggs_quarantine_file(input_path=input_path, source_file_sha256=input_sha256)
    normalized = normalize_options_day_aggs_records(parsed, source="local_sample_handoff")
    sample_records = list(normalized.records[:effective_sample_limit])
    _write_jsonl(output_path, sample_records)
    output_file_size_bytes = output_path.stat().st_size
    output_sha256 = _sha256_file(output_path)

    return {
        "approval_required": True,
        "approval_phrase_matched": approval_phrase_matched,
        "input_path": str(input_path),
        "input_file_exists": input_file_exists,
        "input_file_size_bytes": input_file_size_bytes,
        "input_sha256": input_sha256,
        "output_path": str(output_path),
        "output_file_exists": True,
        "output_file_size_bytes": output_file_size_bytes,
        "output_sha256": output_sha256,
        "requested_sample_limit": int(requested_sample_limit),
        "effective_sample_limit": effective_sample_limit,
        "records_written": len(sample_records),
        "source_rows_scanned": parsed.row_count,
        "warning_count": len(normalized.warnings),
        "vendor_call_attempted": False,
        "download_attempted": False,
        "handoff_export_attempted": True,
        "production_export_attempted": False,
        "db_read_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "blockers": tuple(),
        "next_allowed_step": "review the sample handoff jsonl and decide whether a fixture or downstream sample builder is needed",
    }
