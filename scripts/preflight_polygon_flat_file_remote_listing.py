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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guarded Polygon flat-file remote listing preflight for sector ETF OHLCV readiness.")
    parser.add_argument("--enable-remote-listing", action="store_true", help="Allow read-only remote object listing only.")
    parser.add_argument("--max-keys", type=int, default=5, help="Maximum remote object count to request, capped at 25.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _present_names(env: dict[str, str], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if env.get(name)]


def _redact_object_key(key: str) -> str:
    parts = [part for part in key.split("/") if part]
    if not parts:
        return "<redacted>"
    tail = parts[-1]
    if len(parts) == 1:
        return tail
    return f"{parts[-2]}/{tail}"


def _safe_payload(*, enabled: bool, max_keys_requested: int) -> dict[str, object]:
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
    max_keys_effective = min(max(max_keys_requested, 1), 25)
    adapter = PolygonFlatFileAdapter(env=env)
    boto3_available = adapter.boto3_available()
    remote_bucket_list_attempted = False
    remote_object_list_attempted = False
    object_count_seen = 0
    object_key_samples_redacted: list[str] = []
    blockers = [
        "production handoff generation is not authorized",
        "no downloads, remote file reads, exports, DB writes, ingestion, scheduler activation, or production mutation are permitted",
    ]
    if not enabled:
        blockers.append("remote listing is disabled by default")
    if config_classification != "polygon_flat_file":
        blockers.append("polygon flat-file configuration is required for remote listing")
    if not boto3_available:
        blockers.append("boto3 is required for remote listing preflight")
    if enabled and config_classification == "polygon_flat_file" and boto3_available:
        remote_bucket_list_attempted = True
        remote_object_list_attempted = True
        objects = adapter.list_remote_objects(max_keys=max_keys_effective)
        object_count_seen = len(objects)
        object_key_samples_redacted = [_redact_object_key(str(obj.get("Key", ""))) for obj in objects[:max_keys_effective]]
    return {
        "preflight_only": True,
        "remote_listing_enabled": enabled,
        "vendor_call_attempted": remote_bucket_list_attempted,
        "remote_bucket_list_attempted": remote_bucket_list_attempted,
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
        "boto3_available": boto3_available,
        "max_keys_requested": max_keys_requested,
        "max_keys_effective": max_keys_effective,
        "object_count_seen": object_count_seen,
        "object_key_samples_redacted": object_key_samples_redacted,
        "expected_dataset_type": EXPECTED_FLAT_FILE_DATASET_TYPE,
        "benchmark_symbol": BENCHMARK_SYMBOL,
        "required_sector_symbols": list(SECTOR_SYMBOLS),
        "production_handoff_generation_authorized": False,
        "synthetic_forbidden": True,
        "fixture_only_forbidden": True,
        "blockers": blockers,
        "next_allowed_step": "explicit read-only remote object listing only after Polygon flat-file configuration and boto3 availability are confirmed",
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload(enabled=bool(args.enable_remote_listing), max_keys_requested=args.max_keys)
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
