from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import scripts.check_polygon_stock_day_agg_remote_listing_readiness as cli


def _run(monkeypatch, env: dict[str, str] | None = None) -> dict[str, object]:
    for name in cli.REQUIRED_CONFIG_NAMES:
        monkeypatch.delenv(name, raising=False)
    if env:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
    payload = cli.build_payload()
    return payload


def test_safe_run_with_missing_env_vars(monkeypatch) -> None:
    payload = _run(monkeypatch)
    assert payload["boto3_available"] in (True, False)
    assert payload["credentials_present"] is False
    assert payload["safe_to_attempt_metadata_listing"] is False
    assert payload["readiness_status"] in {"BLOCKED_MISSING_DEPENDENCY", "BLOCKED_MISSING_CREDENTIALS", "BLOCKED_MISSING_CONFIG"}


def test_presence_fields_and_json_output(monkeypatch) -> None:
    payload = _run(
        monkeypatch,
        {
            "POLYGON_API_KEY": "secret-key",
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "access-id",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret-access",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    text = json.dumps(payload)
    for key in [
        "boto3_available",
        "credentials_present",
        "safe_to_attempt_metadata_listing",
        "readiness_status",
    ]:
        assert key in payload
        assert key in text
    for forbidden in ["secret-key", "access-id", "secret-access", "endpoint.invalid"]:
        assert forbidden not in text


def test_script_source_is_import_and_network_safe() -> None:
    source = Path("scripts/check_polygon_stock_day_agg_remote_listing_readiness.py").read_text(encoding="utf-8").lower()
    for forbidden in [
        "boto3.client(",
        "list_objects_v2(",
        "get_object(",
        "download_file(",
        "requests",
        "httpx",
        "sqlalchemy",
        "create_engine(",
        "to_sql(",
        "commit(",
    ]:
        assert forbidden not in source


def test_help_runs_without_side_effects() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_polygon_stock_day_agg_remote_listing_readiness.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "metadata-only Polygon stock day aggregate remote listing" in result.stdout
