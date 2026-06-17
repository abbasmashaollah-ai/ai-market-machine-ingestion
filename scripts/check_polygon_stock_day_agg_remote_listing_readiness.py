from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

REQUIRED_CONFIG_NAMES = (
    "POLYGON_API_KEY",
    "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
    "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
    "POLYGON_FLAT_FILE_ENDPOINT",
    "POLYGON_FLAT_FILE_BUCKET",
    "POLYGON_FLAT_FILE_PREFIX",
)


def _build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Check readiness for a metadata-only Polygon stock day aggregate remote listing probe.")


def _present(env: dict[str, str], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if env.get(name)]


def build_payload() -> dict[str, object]:
    env = dict(os.environ)
    boto3_available = importlib.util.find_spec("boto3") is not None
    present = _present(env, REQUIRED_CONFIG_NAMES)
    missing = [name for name in REQUIRED_CONFIG_NAMES if name not in present]
    flat_file_config_present = all(name in present for name in REQUIRED_CONFIG_NAMES[1:])
    credentials_present = bool(present)
    endpoint_configured = "POLYGON_FLAT_FILE_ENDPOINT" in present
    bucket_configured = "POLYGON_FLAT_FILE_BUCKET" in present
    stock_day_agg_prefix_configured = "POLYGON_FLAT_FILE_PREFIX" in present
    safe_to_attempt_metadata_listing = bool(boto3_available and flat_file_config_present and credentials_present and endpoint_configured and bucket_configured and stock_day_agg_prefix_configured)

    if not boto3_available:
        readiness_status = "BLOCKED_MISSING_DEPENDENCY"
        recommended_next_step = "Install or configure the missing local dependency, then rerun the vendor listing probe."
    elif not credentials_present:
        readiness_status = "BLOCKED_MISSING_CREDENTIALS"
        recommended_next_step = "Configure the required Polygon flat-file credential names locally, then rerun the checker."
    elif not flat_file_config_present:
        readiness_status = "BLOCKED_MISSING_CONFIG"
        recommended_next_step = "Configure the missing Polygon flat-file endpoint, bucket, and prefix names locally, then rerun the checker."
    else:
        readiness_status = "READY_FOR_METADATA_LISTING"
        recommended_next_step = "Rerun the metadata-only vendor listing probe."

    return {
        "boto3_available": boto3_available,
        "flat_file_config_present": flat_file_config_present,
        "credentials_present": credentials_present,
        "endpoint_configured": endpoint_configured,
        "bucket_configured": bucket_configured,
        "stock_day_agg_prefix_configured": stock_day_agg_prefix_configured,
        "safe_to_attempt_metadata_listing": safe_to_attempt_metadata_listing,
        "readiness_status": readiness_status,
        "recommended_next_step": recommended_next_step,
        "vendor_call_attempted": False,
        "remote_listing_attempted": False,
        "download_attempted": False,
        "secrets_printed": False,
    }


def main(argv: list[str] | None = None) -> int:
    _build_parser().parse_args(argv)
    payload = build_payload()
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
