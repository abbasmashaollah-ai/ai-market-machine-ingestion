from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.vendor_flat_files.polygon_flat_file_adapter import PolygonFlatFileAdapter, REQUIRED_CONFIG_NAMES

REQUIRED_READ_ONLY_CONFIG_NAMES = REQUIRED_CONFIG_NAMES

DEFAULT_DATE = "2026-06-15"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only live Polygon source access verification for stock day aggregates.")
    parser.add_argument("--date", default=DEFAULT_DATE, help="Date in YYYY-MM-DD format to probe by month listing.")
    parser.add_argument("--output-file", default=None, help="Optional path for machine-readable JSON evidence output.")
    return parser


def _classify_missing(env: dict[str, str]) -> tuple[str, list[str]]:
    missing = [name for name in REQUIRED_READ_ONLY_CONFIG_NAMES if not env.get(name)]
    if missing:
        return "env_missing", missing
    return "ok", []


def _looks_nonempty(value: str | None) -> bool:
    return bool(value and value.strip())


def verify_read_only_source_access(*, env: dict[str, str], date_value: str) -> dict[str, object]:
    adapter = PolygonFlatFileAdapter(env=env)
    boto3_available = adapter.boto3_available()
    env_status, missing_env_vars = _classify_missing(env)
    credentials_present = bool(env.get("POLYGON_API_KEY")) and all(
        env.get(name)
        for name in (
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
            "POLYGON_FLAT_FILE_ENDPOINT",
            "POLYGON_FLAT_FILE_BUCKET",
            "POLYGON_FLAT_FILE_PREFIX",
        )
    )
    endpoint_looks_valid = _looks_nonempty(env.get("POLYGON_FLAT_FILE_ENDPOINT"))
    bucket_looks_valid = _looks_nonempty(env.get("POLYGON_FLAT_FILE_BUCKET"))
    prefix_looks_valid = _looks_nonempty(env.get("POLYGON_FLAT_FILE_PREFIX"))
    date_path = adapter.stock_day_aggs_object_key(date_value)
    object_key_used = date_path
    object_key_includes_bucket_prefix = object_key_used.startswith("flatfiles/")
    endpoint_url_used = (env.get("POLYGON_FLAT_FILE_ENDPOINT") or "").strip().rstrip("/") or None
    region_name = (env.get("POLYGON_FLAT_FILE_REGION") or "us-east-1").strip() or "us-east-1"
    path_style_addressing_used = env.get("POLYGON_FLAT_FILE_FORCE_PATH_STYLE", "").strip().lower() in {"1", "true", "yes", "on"}
    no_auth_probe = adapter.no_auth_endpoint_probe(endpoint_url_used) if endpoint_url_used else {
        "no_auth_probe_attempted": False,
        "no_auth_probe_reachable": False,
        "no_auth_probe_http_status_code": None,
        "no_auth_probe_error": "missing_endpoint",
        "no_auth_probe_tcp_connected": False,
        "no_auth_probe_tls_connected": False,
        "no_auth_probe_host": "",
        "no_auth_probe_port": None,
    }
    client_mode_diagnostics = adapter.client_mode_diagnostics()
    client_mode_build = adapter.compare_client_mode_construction() if credentials_present and boto3_available else {
        "explicit_session_client_build_status": "not_attempted",
        "environment_driven_client_build_status": "not_attempted",
    }

    payload: dict[str, object] = {
        "read_only_source_access_attempted": False,
        "read_only_source_access_authorized": False,
        "source_access_status": "unsafe_to_proceed",
        "env_status": env_status,
        "missing_env_vars": missing_env_vars,
        "credentials_present": credentials_present,
        "boto3_available": boto3_available,
        "remote_listing_attempted": False,
        "remote_listing_reachable": False,
        "remote_listing_error_code": "",
        "remote_listing_error_message": "",
        "boto_exception_type": "",
        "boto_error_code": "",
        "http_status_code": None,
        "endpoint_url_used": endpoint_url_used,
        "addressing_style_used": "path" if path_style_addressing_used else "virtual",
        "signature_version_used": "s3v4",
        "massive_compatible_client_mode": True,
        "path_style_addressing_used": path_style_addressing_used,
        "region_configured": bool(region_name),
        "region_value_redacted": region_name,
        "ssl_verification_failed": False,
        "connection_timed_out": False,
        "dns_resolution_failed": False,
        "endpoint_looks_valid": endpoint_looks_valid,
        "bucket_looks_valid": bucket_looks_valid,
        "prefix_looks_valid": prefix_looks_valid,
        "date_path": date_path,
        "object_key_used": object_key_used,
        "object_key_includes_bucket_prefix": object_key_includes_bucket_prefix,
        **no_auth_probe,
        **client_mode_diagnostics,
        **client_mode_build,
        "download_attempted": False,
        "db_write_attempted": False,
        "scheduler_activation_attempted": False,
        "secrets_printed": False,
        "safe_to_proceed": False,
        "required_config_names": list(REQUIRED_READ_ONLY_CONFIG_NAMES),
        "probe_date": date_value,
        "next_allowed_step": "complete Railway/deployment verification after read-only source access passes",
    }

    if env_status != "ok":
        payload["source_access_status"] = "env_missing"
        return payload
    if not credentials_present:
        payload["source_access_status"] = "credentials_missing"
        return payload
    if not boto3_available:
        payload["source_access_status"] = "unsafe_to_proceed"
        return payload

    payload["read_only_source_access_attempted"] = True
    payload["read_only_source_access_authorized"] = True
    payload["remote_listing_attempted"] = True
    try:
        result = adapter.resolve_remote_manifest_object_for_date(date_value)
    except Exception as exc:
        diagnostics = adapter.diagnose_remote_listing_error(
            exc,
            endpoint_url_used=endpoint_url_used,
            region_name=region_name,
            path_style_addressing_used=path_style_addressing_used,
        )
        code, redacted_code, message = adapter.classify_remote_listing_error(exc)
        payload["source_access_status"] = "source_unreachable"
        payload["remote_listing_error_code"] = redacted_code or code
        payload["remote_listing_error_message"] = message
        payload.update(diagnostics)
        payload.update(adapter.redacted_exception_summary(exc, endpoint_url_used=endpoint_url_used))
        return payload

    if result and result.get("object_present") is True:
        payload["source_access_status"] = "source_reachable"
        payload["remote_listing_reachable"] = True
        payload["safe_to_proceed"] = True
        return payload

    payload["source_access_status"] = "date_object_not_found"
    payload["remote_listing_error_code"] = "not_found"
    payload["remote_listing_error_message"] = "remote listing completed safely but no object matched the requested date"
    payload["remote_listing_reachable"] = True
    payload["boto_exception_type"] = "None"
    payload["region_configured"] = bool(region_name)
    payload["region_value_redacted"] = region_name
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    env = dict(os.environ)
    payload = verify_read_only_source_access(env=env, date_value=args.date)
    output = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output + "\n", encoding="utf-8")
    sys.stdout.write(output)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
