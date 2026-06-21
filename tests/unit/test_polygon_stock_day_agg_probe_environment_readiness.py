from __future__ import annotations

import json

from app.vendors.polygon_stock_day_agg_probe_environment_readiness import (
    check_probe_environment_readiness,
    render_probe_environment_readiness_json,
)


def test_probe_environment_readiness_missing_boto3_and_missing_config(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.vendors.polygon_stock_day_agg_probe_environment_readiness._import_boto3_available",
        lambda: (False, "ModuleNotFoundError"),
    )
    result = check_probe_environment_readiness(
        {
            "POLYGON_API_KEY": "",
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "",
            "POLYGON_FLAT_FILE_ENDPOINT": "",
            "POLYGON_FLAT_FILE_BUCKET": "",
            "POLYGON_FLAT_FILE_PREFIX": "",
        }
    )
    payload = result.to_dict()
    assert payload["readiness_passed"] is False
    assert payload["boto3_available"] is False
    assert payload["boto3_error_type"] == "ModuleNotFoundError"
    assert payload["required_config_keys_present"] == []
    assert payload["required_config_keys_missing"] == [
        "POLYGON_API_KEY",
        "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
        "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
        "POLYGON_FLAT_FILE_ENDPOINT",
        "POLYGON_FLAT_FILE_BUCKET",
        "POLYGON_FLAT_FILE_PREFIX",
    ]
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_listing_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["file_write_attempted"] is False
    assert payload["secrets_printed"] is False
    assert payload["safe_to_retry_probe"] is False


def test_probe_environment_readiness_present_config_and_boto3(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.vendors.polygon_stock_day_agg_probe_environment_readiness._import_boto3_available",
        lambda: (True, None),
    )
    result = check_probe_environment_readiness(
        {
            "POLYGON_API_KEY": "x",
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "x",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "x",
            "POLYGON_FLAT_FILE_ENDPOINT": "x",
            "POLYGON_FLAT_FILE_BUCKET": "x",
            "POLYGON_FLAT_FILE_PREFIX": "x",
        }
    )
    payload = result.to_dict()
    assert payload["readiness_passed"] is True
    assert payload["boto3_available"] is True
    assert payload["boto3_error_type"] is None
    assert payload["required_config_keys_missing"] == []
    assert payload["safe_to_retry_probe"] is True


def test_probe_environment_readiness_cli_json_is_safe(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "app.vendors.polygon_stock_day_agg_probe_environment_readiness._import_boto3_available",
        lambda: (False, "ModuleNotFoundError"),
    )
    payload = render_probe_environment_readiness_json(
        {
            "POLYGON_API_KEY": "secret-value",
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "secret-value",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret-value",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://example.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        }
    )
    data = json.loads(payload)
    assert data["vendor_call_attempted"] is False
    assert data["remote_listing_attempted"] is False
    assert data["download_attempted"] is False
    assert data["file_write_attempted"] is False
    assert data["secrets_printed"] is False
    assert "secret-value" not in payload
    assert "https://example.invalid" not in payload
