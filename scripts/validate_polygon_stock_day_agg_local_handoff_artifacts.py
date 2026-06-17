from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXPECTED_DATASET = "ohlcv_equity_daily"
EXPECTED_SOURCE_VENDOR = "polygon_massive_flat_files"
EXPECTED_SOURCE_DATASET = "polygon_stocks_day_aggs"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate local Polygon stock day aggregate handoff artifacts.")
    parser.add_argument("--manifest", required=True, help="Path to the local batch manifest JSON.")
    return parser


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _safe_add_error(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def validate_polygon_stock_day_agg_local_handoff_artifacts(*, manifest_path: str | Path) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    errors: list[str] = []
    payload: dict[str, Any] = {
        "validator_attempted": True,
        "manifest_exists": manifest_path.exists(),
        "manifest_valid": False,
        "summary_files_checked": 0,
        "rows_files_checked": 0,
        "total_rows_expected": 0,
        "total_rows_observed": 0,
        "total_rejected_rows": 0,
        "validation_passed": False,
        "validation_errors": [],
        "vendor_call_attempted": False,
        "download_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
    }

    if not manifest_path.exists():
        _safe_add_error(errors, "manifest_missing")
        payload["validation_errors"] = errors
        return payload

    try:
        manifest = _read_json(manifest_path)
        payload["manifest_valid"] = True
    except Exception:
        _safe_add_error(errors, "manifest_invalid_json")
        payload["validation_errors"] = errors
        return payload

    start_date = manifest.get("start_date")
    end_date = manifest.get("end_date")
    expected_dates = []
    try:
        if start_date and end_date:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            current = start
            while current <= end:
                expected_dates.append(current.isoformat())
                current = date.fromordinal(current.toordinal() + 1)
    except Exception:
        _safe_add_error(errors, "manifest_date_range_invalid")

    total_expected = 0
    total_observed = 0
    total_rejected = 0
    summary_files_checked = 0
    rows_files_checked = 0
    date_artifact_count_checked = 0

    per_date_outputs = manifest.get("per_date_outputs", [])
    if not isinstance(per_date_outputs, list):
        _safe_add_error(errors, "manifest_per_date_outputs_invalid")
        per_date_outputs = []

    for item in per_date_outputs:
        if not isinstance(item, dict):
            _safe_add_error(errors, "manifest_per_date_output_invalid")
            continue
        summary_path = Path(item.get("summary_path", ""))
        rows_path = Path(item.get("rows_path", ""))
        if not summary_path.is_absolute():
            summary_path = REPO_ROOT / summary_path
        if not rows_path.is_absolute():
            rows_path = REPO_ROOT / rows_path
        summary_files_checked += 1
        rows_files_checked += 1
        if not summary_path.exists():
            _safe_add_error(errors, f"missing_summary:{summary_path.name}")
            continue
        if not rows_path.exists():
            _safe_add_error(errors, f"missing_rows:{rows_path.name}")
            continue
        date_artifact_count_checked += 1
        try:
            summary = _read_json(summary_path)
            rows = _read_jsonl(rows_path)
        except Exception:
            _safe_add_error(errors, f"invalid_summary_or_rows:{summary_path.name}")
            continue
        if summary.get("dataset") != EXPECTED_DATASET:
            _safe_add_error(errors, "summary_dataset_mismatch")
        if summary.get("source_vendor") != EXPECTED_SOURCE_VENDOR:
            _safe_add_error(errors, "summary_source_vendor_mismatch")
        if summary.get("source_dataset") != EXPECTED_SOURCE_DATASET:
            _safe_add_error(errors, "summary_source_dataset_mismatch")
        if summary.get("production_approved") is not False:
            _safe_add_error(errors, "summary_production_approved_not_false")
        for flag in (
            "db_write_attempted",
            "vendor_call_attempted",
            "download_attempted",
            "ingestion_attempted",
            "scheduler_activation_attempted",
            "production_mutation_attempted",
        ):
            if summary.get(flag) is not False:
                _safe_add_error(errors, f"summary_flag_not_false:{flag}")
        expected_rows = int(summary.get("row_count_written", 0))
        observed_rows = len(rows)
        rejected_rows = int(summary.get("rejected_row_count", 0))
        total_expected += expected_rows
        total_observed += observed_rows
        total_rejected += rejected_rows
        if expected_rows != observed_rows:
            _safe_add_error(errors, f"row_count_mismatch:{summary_path.name}")
        if int(manifest.get("total_rows_written", 0)) != total_expected:
            _safe_add_error(errors, "manifest_total_rows_written_mismatch")
        required_fields = {
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
            "source_quarantine_path",
            "preview_or_local_handoff_only",
        }
        for row in rows:
            if not required_fields.issubset(row):
                _safe_add_error(errors, "row_missing_required_field")
                break
            if row.get("dataset") != EXPECTED_DATASET:
                _safe_add_error(errors, "row_dataset_mismatch")
            if row.get("source_vendor") != EXPECTED_SOURCE_VENDOR:
                _safe_add_error(errors, "row_source_vendor_mismatch")
            if row.get("source_dataset") != EXPECTED_SOURCE_DATASET:
                _safe_add_error(errors, "row_source_dataset_mismatch")
            if row.get("preview_or_local_handoff_only") is not True:
                _safe_add_error(errors, "row_preview_flag_not_true")
            trade_date = str(row.get("trade_date", ""))
            if start_date and end_date and not (start_date <= trade_date <= end_date):
                _safe_add_error(errors, "row_trade_date_outside_manifest_range")
                break
        if len(rows) == observed_rows:
            pass

    if total_expected == total_observed and not errors:
        payload["validation_passed"] = True

    payload.update(
        {
            "summary_files_checked": summary_files_checked,
            "rows_files_checked": rows_files_checked,
            "date_artifact_count_checked": date_artifact_count_checked,
            "total_rows_expected": total_expected,
            "total_rows_observed": total_observed,
            "total_rejected_rows": total_rejected,
            "validation_errors": errors,
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = validate_polygon_stock_day_agg_local_handoff_artifacts(manifest_path=args.manifest)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
