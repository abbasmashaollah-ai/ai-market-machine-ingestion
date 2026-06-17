from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.vendor_flat_files.polygon_flat_file_adapter import (
    BENCHMARK_SYMBOL,
    EXPECTED_FLAT_FILE_DATASET_TYPE,
    PolygonFlatFileAdapter,
    REQUIRED_CONFIG_NAMES,
    SECTOR_SYMBOLS,
    detect_config_presence,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guarded Polygon flat-file manifest preflight for sector ETF OHLCV readiness.")
    parser.add_argument("--enable-remote-listing", action="store_true", help="Allow read-only remote manifest listing only.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--max-days", type=int, default=5, help="Maximum number of dates to request, capped at 25.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _present_names(env: dict[str, str], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if env.get(name)]


def _safe_payload(*, enabled: bool, start_date: str, end_date: str, max_days_requested: int) -> dict[str, object]:
    env = dict(os.environ)
    presence = detect_config_presence(env)
    polygon_names = _present_names(env, tuple(name for name in REQUIRED_CONFIG_NAMES if name.startswith("POLYGON_FLAT_FILE")))
    aws_names = _present_names(env, ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION", "AWS_S3_BUCKET", "AWS_S3_PREFIX"))
    polygon_complete = len(polygon_names) == 5
    aws_complete = len(aws_names) == 5
    polygon_partial = 0 < len(polygon_names) < 5
    aws_partial = 0 < len(aws_names) < 5
    if polygon_complete and aws_complete:
        config_classification = "both_present"
    elif polygon_complete:
        config_classification = "polygon_flat_file"
    elif aws_complete:
        config_classification = "generic_aws_only"
    elif polygon_partial or aws_partial:
        config_classification = "ambiguous"
    else:
        config_classification = "missing"

    date_count_effective = min(max(max_days_requested, 1), 25)
    adapter = PolygonFlatFileAdapter(env=env)
    boto3_available = adapter.boto3_available()
    remote_object_list_attempted = False
    manifest_entries: list[dict[str, object]] = []
    blockers = [
        "production handoff generation is not authorized",
        "no downloads, remote file reads, exports, DB writes, ingestion, scheduler activation, or production mutation are permitted",
    ]
    if not enabled:
        blockers.append("remote listing is disabled by default")
    if config_classification != "polygon_flat_file":
        blockers.append("polygon flat-file configuration is required for remote manifest listing")
    if not boto3_available:
        blockers.append("boto3 is required for remote manifest preflight")
    if enabled and config_classification == "polygon_flat_file" and boto3_available:
        remote_object_list_attempted = True
        try:
            raw_entries = adapter.list_remote_manifest_objects(start_date=start_date, end_date=end_date, max_days=date_count_effective)
            for entry in raw_entries:
                day = str(entry.get("date") or "")
                tail = str(entry.get("redacted_key_tail") or "")
                key_present = bool(entry.get("Key"))
                manifest_entries.append(
                    {
                        "date": day,
                        "redacted_key_tail": tail or "<redacted>",
                        "object_present": bool(entry.get("object_present", False)),
                        "size_bytes": entry.get("Size"),
                        "last_modified_present": bool(entry.get("LastModified")),
                        "etag_present": bool(entry.get("ETag")),
                        "resolved_key_present": key_present,
                        "resolved_key_tail_matches_requested_date": bool(day and tail.endswith(f"{day}.csv.gz")),
                        "resolved_key_sha256_prefix": adapter.sha256_prefix(tail) if key_present else "",
                        "listed_key_sha256_prefix": adapter.sha256_prefix(tail) if key_present else "",
                        "resolved_key_matches_listed_key": key_present,
                    }
                )
        except Exception as exc:
            code, redacted_code, message = adapter.classify_remote_listing_error(exc)
            blockers.append(f"remote manifest listing blocked safely: {code}")
            return {
                "preflight_only": True,
                "manifest_listing_enabled": enabled,
                "vendor_call_attempted": True,
                "remote_object_list_attempted": True,
                "download_attempted": False,
                "remote_file_read_attempted": False,
                "export_attempted": False,
                "db_write_attempted": False,
                "ingestion_attempted": False,
                "scheduler_activation_attempted": False,
                "production_mutation_attempted": False,
                "config_classification": config_classification,
                "credentials_present": bool(presence["credentials_present"]),
                "credentials_printed": False,
                "endpoint_value_printed": False,
                "bucket_value_printed": False,
                "prefix_value_printed": False,
                "date_window_requested": {"start_date": start_date, "end_date": end_date},
                "date_count_effective": date_count_effective,
                "manifest_object_count_present": 0,
                "manifest_object_count_missing": 0,
                "manifest_entries": [],
                "expected_dataset_type": EXPECTED_FLAT_FILE_DATASET_TYPE,
                "benchmark_symbol": BENCHMARK_SYMBOL,
                "required_sector_symbols": list(SECTOR_SYMBOLS),
                "production_handoff_generation_authorized": False,
                "synthetic_forbidden": True,
                "fixture_only_forbidden": True,
                "remote_listing_status": code,
                "remote_listing_error_code_redacted": redacted_code,
                "remote_listing_error_message_redacted": message,
                "blockers": blockers,
                "next_allowed_step": "explicit read-only remote manifest listing only after Polygon flat-file configuration and boto3 availability are confirmed",
            }

    present_count = sum(1 for entry in manifest_entries if entry.get("object_present"))
    missing_count = len(manifest_entries) - present_count
    return {
        "preflight_only": True,
        "manifest_listing_enabled": enabled,
        "vendor_call_attempted": remote_object_list_attempted,
        "remote_object_list_attempted": remote_object_list_attempted,
        "download_attempted": False,
        "remote_file_read_attempted": False,
        "export_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "config_classification": config_classification,
        "credentials_present": bool(presence["credentials_present"]),
        "credentials_printed": False,
        "endpoint_value_printed": False,
        "bucket_value_printed": False,
        "prefix_value_printed": False,
        "date_window_requested": {"start_date": start_date, "end_date": end_date},
        "date_count_effective": date_count_effective,
        "manifest_object_count_present": present_count,
        "manifest_object_count_missing": missing_count,
        "remote_list_object_count_seen": len(manifest_entries),
        "manifest_entries": manifest_entries,
        "expected_dataset_type": EXPECTED_FLAT_FILE_DATASET_TYPE,
        "benchmark_symbol": BENCHMARK_SYMBOL,
        "required_sector_symbols": list(SECTOR_SYMBOLS),
        "production_handoff_generation_authorized": False,
        "synthetic_forbidden": True,
        "fixture_only_forbidden": True,
        "blockers": blockers,
        "next_allowed_step": "explicit read-only remote manifest listing only after Polygon flat-file configuration and boto3 availability are confirmed",
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload(
        enabled=bool(args.enable_remote_listing),
        start_date=args.start_date,
        end_date=args.end_date,
        max_days_requested=args.max_days,
    )
    safe_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(safe_json + "\n", encoding="utf-8")
    sys.stdout.write(safe_json)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
