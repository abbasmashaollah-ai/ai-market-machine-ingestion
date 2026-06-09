from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import boto3  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - boto3 is expected in normal runs.
    boto3 = None  # type: ignore[assignment]

from app.vendor_flat_files.options.options_flat_file_manifest import (
    OPTIONS_CONFIG_NAMES,
    OPTIONS_PREFIX,
    OPTIONS_SAMPLE_KEY,
    classify_config,
    missing_names,
    redacted_key_tail,
    present_names,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only options flat-file access preflight.")
    parser.add_argument("--enable-remote-check", action="store_true", help="Enable safe list/head checks.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _safe_client_error(error: Exception) -> tuple[str, str]:
    error_name = error.__class__.__name__
    if error_name == "EndpointConnectionError":
        return "endpoint_connection_error", "endpoint connection error"
    response = getattr(error, "response", {}) if hasattr(error, "response") else {}
    error_data = response.get("Error", {}) if isinstance(response, dict) else {}
    raw_code = str(error_data.get("Code") or "client_error")
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode") if isinstance(response, dict) else None
    if str(status) == "403":
        return "forbidden", "remote check failed safely"
    if raw_code == "AccessDenied":
        return "access_denied", "remote check failed safely"
    if raw_code == "NoSuchKey":
        return "missing_object", "remote check failed safely"
    if raw_code == "NoSuchBucket":
        return "bucket_not_found", "remote check failed safely"
    return "client_error", "remote check failed safely"


def _list_and_head(client: Any, bucket: str, prefix: str, key: str) -> tuple[bool, bool, bool]:
    list_result = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=5)
    contents = list_result.get("Contents", []) if isinstance(list_result, dict) else []
    known_object_present = any(str(obj.get("Key") or "") == key for obj in contents if isinstance(obj, dict))
    head_result = client.head_object(Bucket=bucket, Key=key)
    content_length_present = bool(isinstance(head_result, dict) and head_result.get("ContentLength") is not None)
    return True, known_object_present, content_length_present


def _safe_payload(*, enabled: bool, env: dict[str, str] | None = None) -> dict[str, object]:
    env = dict(env or os.environ)
    config_classification = classify_config(env)
    presence = {
        "credentials_present": config_classification == "polygon_flat_file",
        "present_config_names": present_names(env),
        "missing_config_names": missing_names(env),
    }
    blockers = [
        "production handoff generation is not authorized",
        "no downloads, decompression, parsing, export, DB writes, ingestion, scheduler activation, or production mutation are permitted",
    ]
    if not enabled:
        blockers.append("remote check is disabled by default")
    if config_classification != "polygon_flat_file":
        blockers.append("Polygon flat-file configuration is incomplete or ambiguous")

    payload = {
        "preflight_only": True,
        "options_remote_check_enabled": bool(enabled),
        "vendor_call_attempted": False,
        "remote_object_list_attempted": False,
        "remote_head_object_attempted": False,
        "download_attempted": False,
        "decompression_attempted": False,
        "parse_attempted": False,
        "export_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "config_classification": config_classification,
        "credentials_present": presence["credentials_present"],
        "credentials_printed": False,
        "endpoint_value_printed": False,
        "bucket_value_printed": False,
        "prefix_value_printed": False,
        "known_object_present": False,
        "content_length_present": False,
        "redacted_key_tail": redacted_key_tail(OPTIONS_SAMPLE_KEY),
        "blockers": blockers,
        "next_allowed_step": "explicit approved read-only options list/head check only, not download or export",
    }

    if enabled and config_classification == "polygon_flat_file":
        bucket = env.get("POLYGON_FLAT_FILE_BUCKET", "")
        endpoint = env.get("POLYGON_FLAT_FILE_ENDPOINT", "")
        key = OPTIONS_SAMPLE_KEY
        prefix = OPTIONS_PREFIX
        try:
            if boto3 is None:
                raise RuntimeError("dependency_missing")
            client = boto3.client(
                "s3",
                aws_access_key_id=env.get("POLYGON_FLAT_FILE_ACCESS_KEY_ID"),
                aws_secret_access_key=env.get("POLYGON_FLAT_FILE_SECRET_ACCESS_KEY"),
                endpoint_url=endpoint,
            )
            payload["vendor_call_attempted"] = True
            payload["remote_object_list_attempted"] = True
            payload["remote_head_object_attempted"] = True
            _, known_object_present, content_length_present = _list_and_head(client, bucket, prefix, key)
            payload["known_object_present"] = known_object_present
            payload["content_length_present"] = content_length_present
        except Exception as exc:
            code, message = _safe_client_error(exc)
            payload["vendor_call_attempted"] = True
            payload["remote_object_list_attempted"] = True
            payload["remote_head_object_attempted"] = False
            payload["known_object_present"] = False
            payload["content_length_present"] = False
            payload["remote_status"] = code
            payload["remote_error_message_redacted"] = message
            if code == "client_error" and str(exc) == "dependency_missing":
                payload["vendor_call_attempted"] = False
                payload["remote_object_list_attempted"] = False
                payload["remote_status"] = "dependency_missing"
                payload["remote_error_message_redacted"] = "remote check requires boto3"
            payload["blockers"].append(f"remote check blocked safely: {code}")
            return payload

    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload(enabled=bool(args.enable_remote_check))
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
