from __future__ import annotations

import argparse
import json
import os
import sys
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

APPROVAL_PHRASE = "APPROVE POLYGON FLAT FILE SINGLE DATE LOCAL QUARANTINE DOWNLOAD"
DEFAULT_QUARANTINE_DIR = Path("outputs/quarantine/polygon_flat_files")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guarded Polygon flat-file single-date local quarantine download preflight.")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format.")
    parser.add_argument("--quarantine-dir", default=str(DEFAULT_QUARANTINE_DIR), help="Local quarantine directory.")
    parser.add_argument("--approve-local-quarantine-download", action="store_true", help="Approve a single local quarantine download.")
    parser.add_argument("--approval-phrase", default="", help="Exact approval phrase required for download.")
    parser.add_argument("--overwrite-local-file", action="store_true", help="Overwrite an existing local file instead of skipping.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _safe_payload(
    *,
    enabled: bool,
    approval_phrase: str,
    value: str,
    quarantine_dir: str,
    overwrite_local_file: bool,
    required_approval_phrase: str = APPROVAL_PHRASE,
) -> dict[str, object]:
    env = dict(os.environ)
    presence = detect_config_presence(env)
    polygon_names = [name for name in REQUIRED_CONFIG_NAMES if name.startswith("POLYGON_FLAT_FILE") and env.get(name)]
    config_classification = "polygon_flat_file" if len(polygon_names) == 5 else "missing"
    adapter = PolygonFlatFileAdapter(env=env)
    path = Path(quarantine_dir) / f"polygon_stocks_day_aggs_{value}.csv.gz"
    blockers = [
        "production handoff generation is not authorized",
        "no decompression, parsing, export, DB writes, ingestion, scheduler activation, or production mutation are permitted",
    ]
    local_quarantine_download_enabled = bool(enabled and approval_phrase == required_approval_phrase)
    if not enabled:
        blockers.append("local quarantine download is disabled by default")
    elif approval_phrase != required_approval_phrase:
        blockers.append("approval phrase does not match")
    if path.exists() and not overwrite_local_file:
        blockers.append("local file already exists and overwrite is not approved")
    remote_object_download_attempted = False
    download_attempted = False
    local_file_exists = path.exists()
    local_file_size_bytes = path.stat().st_size if path.exists() else 0
    local_file_sha256 = ""
    content_length_present = False
    resolved_key_present = False
    resolved_key_tail_matches_requested_date = False
    resolved_key_sha256_prefix = ""
    listed_key_sha256_prefix = ""
    resolved_key_matches_listed_key = False
    remote_download_status = ""
    remote_download_error_code_redacted = ""
    remote_download_error_message_redacted = ""
    resolved = None
    if local_quarantine_download_enabled:
        try:
            resolved = adapter.resolve_remote_manifest_object_for_date(value)
        except Exception as exc:
            code, redacted_code, message = adapter.classify_remote_listing_error(exc)
            blockers.append(f"local quarantine download blocked safely: {code}")
            return {
                "preflight_only": False,
                "local_quarantine_download_enabled": local_quarantine_download_enabled,
                "vendor_call_attempted": True,
                "remote_object_download_attempted": False,
                "download_attempted": False,
                "remote_file_read_attempted": False,
                "decompression_attempted": False,
                "parse_attempted": False,
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
                "requested_date": value,
                "redacted_key_tail": adapter.redacted_csv_gzip_tail(value),
                "resolved_key_present": False,
                "resolved_key_tail_matches_requested_date": False,
                "resolved_key_sha256_prefix": "",
                "listed_key_sha256_prefix": "",
                "resolved_key_matches_listed_key": False,
                "local_quarantine_path": str(path),
                "local_file_exists": False,
                "local_file_size_bytes": 0,
                "local_file_sha256": "",
                "production_handoff_generation_authorized": False,
                "synthetic_forbidden": True,
                "fixture_only_forbidden": True,
                "remote_listing_status": code,
                "remote_listing_error_code_redacted": redacted_code,
                "remote_listing_error_message_redacted": message,
                "blockers": blockers,
                "next_allowed_step": "explicit approved single-date local quarantine download only, not export",
            }
    if local_quarantine_download_enabled and resolved is not None and (overwrite_local_file or not path.exists()):
        try:
            remote_object_download_attempted = True
            download_attempted = True
            result = adapter.download_single_date_object(value=value, local_path=path, overwrite=overwrite_local_file)
            local_file_exists = bool(result.get("local_file_exists"))
            local_file_size_bytes = int(result.get("local_file_size_bytes") or 0)
            local_file_sha256 = str(result.get("local_file_sha256") or "")
            content_length_present = bool(result.get("content_length_present"))
            resolved_key_present = bool(result.get("resolved_key_present"))
            resolved_key_tail_matches_requested_date = bool(result.get("resolved_key_tail_matches_requested_date"))
            resolved_key_sha256_prefix = str(result.get("resolved_key_sha256_prefix") or "")
            listed_key_sha256_prefix = str(result.get("listed_key_sha256_prefix") or "")
            resolved_key_matches_listed_key = bool(result.get("resolved_key_matches_listed_key"))
            remote_download_status = str(result.get("remote_download_status") or "")
            remote_download_error_code_redacted = str(result.get("remote_download_error_code_redacted") or "")
            remote_download_error_message_redacted = str(result.get("remote_download_error_message_redacted") or "")
            if result.get("remote_download_status"):
                blockers.append(f"local quarantine download blocked safely: {result.get('remote_download_status')}")
        except Exception as exc:
            code, redacted_code, message = adapter.classify_remote_listing_error(exc)
            blockers.append(f"local quarantine download blocked safely: {code}")
            return {
                "preflight_only": False,
                "local_quarantine_download_enabled": local_quarantine_download_enabled,
                "vendor_call_attempted": True,
                "remote_object_download_attempted": remote_object_download_attempted,
                "download_attempted": download_attempted,
                "remote_file_read_attempted": False,
                "decompression_attempted": False,
                "parse_attempted": False,
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
                "requested_date": value,
                "redacted_key_tail": adapter.redacted_csv_gzip_tail(value),
                "resolved_key_present": resolved_key_present,
                "resolved_key_tail_matches_requested_date": resolved_key_tail_matches_requested_date,
                "resolved_key_sha256_prefix": resolved_key_sha256_prefix,
                "listed_key_sha256_prefix": listed_key_sha256_prefix,
                "resolved_key_matches_listed_key": resolved_key_matches_listed_key,
                "local_quarantine_path": str(path),
                "local_file_exists": False,
                "local_file_size_bytes": 0,
                "local_file_sha256": "",
                "content_length_present": False,
                "remote_download_status": code,
                "remote_download_error_code_redacted": redacted_code,
                "remote_download_error_message_redacted": message,
                "production_handoff_generation_authorized": False,
                "synthetic_forbidden": True,
                "fixture_only_forbidden": True,
                "remote_listing_status": code,
                "remote_listing_error_code_redacted": redacted_code,
                "remote_listing_error_message_redacted": message,
                "blockers": blockers,
                "next_allowed_step": "explicit approved single-date local quarantine download only, not export",
            }
    if local_quarantine_download_enabled and resolved is None:
        blockers.append("requested date was not present in the manifest listing")
    return {
        "preflight_only": False if local_quarantine_download_enabled else True,
        "local_quarantine_download_enabled": local_quarantine_download_enabled,
        "vendor_call_attempted": remote_object_download_attempted,
        "remote_object_download_attempted": remote_object_download_attempted,
        "download_attempted": download_attempted,
        "remote_file_read_attempted": False,
        "decompression_attempted": False,
        "parse_attempted": False,
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
        "requested_date": value,
        "redacted_key_tail": adapter.redacted_csv_gzip_tail(value),
        "resolved_key_present": resolved_key_present,
        "resolved_key_tail_matches_requested_date": resolved_key_tail_matches_requested_date,
        "resolved_key_sha256_prefix": resolved_key_sha256_prefix,
        "listed_key_sha256_prefix": listed_key_sha256_prefix,
        "resolved_key_matches_listed_key": resolved_key_matches_listed_key,
        "local_quarantine_path": str(path),
        "local_file_exists": local_file_exists,
        "local_file_size_bytes": local_file_size_bytes,
        "local_file_sha256": local_file_sha256,
        "content_length_present": content_length_present,
        "remote_download_status": remote_download_status,
        "remote_download_error_code_redacted": remote_download_error_code_redacted,
        "remote_download_error_message_redacted": remote_download_error_message_redacted,
        "production_handoff_generation_authorized": False,
        "synthetic_forbidden": True,
        "fixture_only_forbidden": True,
        "blockers": blockers,
        "next_allowed_step": "explicit approved single-date local quarantine download only, not export",
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload(
        enabled=bool(args.approve_local_quarantine_download),
        approval_phrase=args.approval_phrase,
        value=args.date,
        quarantine_dir=args.quarantine_dir,
        overwrite_local_file=bool(args.overwrite_local_file),
        required_approval_phrase=APPROVAL_PHRASE,
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
