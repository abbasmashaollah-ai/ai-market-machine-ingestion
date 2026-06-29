from __future__ import annotations

import json
import os
import subprocess
import sys
import types

import scripts.verify_polygon_stock_day_agg_read_only_source_access as cli
import app.vendor_flat_files.polygon_flat_file_adapter as adapter_mod


def test_read_only_source_access_env_missing_fails_closed(monkeypatch) -> None:
    for name in cli.REQUIRED_READ_ONLY_CONFIG_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr("scripts.verify_polygon_stock_day_agg_read_only_source_access.PolygonFlatFileAdapter.boto3_available", staticmethod(lambda: False))
    payload = cli.verify_read_only_source_access(env={}, date_value="2026-06-15")
    assert payload["source_access_status"] == "env_missing"
    assert payload["safe_to_proceed"] is False
    assert payload["remote_listing_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False


def test_read_only_source_access_success_classifies_source_reachable(monkeypatch) -> None:
    monkeypatch.setattr("scripts.verify_polygon_stock_day_agg_read_only_source_access.PolygonFlatFileAdapter.boto3_available", staticmethod(lambda: True))
    payload = cli.verify_read_only_source_access(
        env={
            "POLYGON_API_KEY": "x",
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "x",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "x",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
        date_value="2026-06-15",
    )
    assert payload["source_access_status"] in {"source_reachable", "date_object_not_found", "source_unreachable"}
    assert payload["endpoint_looks_valid"] is True
    assert payload["bucket_looks_valid"] is True
    assert payload["prefix_looks_valid"] is True
    assert payload["date_path"] == "us_stocks_sip/day_aggs_v1/2026/06/2026-06-15.csv.gz"
    assert payload["object_key_used"] == "us_stocks_sip/day_aggs_v1/2026/06/2026-06-15.csv.gz"
    assert payload["object_key_includes_bucket_prefix"] is False
    assert payload["massive_compatible_client_mode"] is True
    assert payload["addressing_style_used"] == "virtual"
    assert payload["signature_version_used"] == "s3v4"
    assert payload["path_style_addressing_used"] is False
    assert payload["region_configured"] is True
    assert payload["region_value_redacted"] == "us-east-1"
    assert payload["download_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["explicit_session_client_build_status"] in {"not_attempted", "built", "ValueError", "RuntimeError", "client_error", "ModuleNotFoundError"}
    assert payload["environment_driven_client_build_status"] in {"not_attempted", "built", "ValueError", "RuntimeError", "client_error", "ModuleNotFoundError"}


def test_diagnose_remote_listing_error_maps_safe_client_failure_details() -> None:
    class RequestTimeoutError(Exception):
        pass

    error = RequestTimeoutError("placeholder")
    error.response = {"Error": {"Code": "RequestTimeout"}, "ResponseMetadata": {"HTTPStatusCode": 504}}  # type: ignore[attr-defined]
    diagnostics = cli.PolygonFlatFileAdapter.diagnose_remote_listing_error(error)
    assert diagnostics["boto_error_code"] == "RequestTimeout"
    assert diagnostics["http_status_code"] == 504
    assert diagnostics["safe_classification_code"] in {"network_client_error", "client_error"}
    assert diagnostics["ssl_verification_failed"] is False
    assert diagnostics["connection_timed_out"] in {True, False}
    assert "redacted_exception_summary" in diagnostics


def test_redacted_exception_summary_reports_safe_markers() -> None:
    error = RuntimeError("SSL handshake timeout talking to proxy files.massive.com")
    summary = cli.PolygonFlatFileAdapter.redacted_exception_summary(error, endpoint_url_used="https://files.massive.com")
    assert summary["exception_class"] == "RuntimeError"
    assert summary["root_exception_class"] == "RuntimeError"
    assert summary["target_host"] == "files.massive.com"
    assert summary["message_contains_ssl"] is True
    assert summary["message_contains_timeout"] is True
    assert summary["message_contains_proxy"] is True
    assert summary["proxy_env_var_names_present"] == []
    assert summary["value_error_category"] == "not_value_error"


def test_value_error_classification_is_safe_and_specific() -> None:
    assert cli.PolygonFlatFileAdapter.classify_value_error(ValueError("invalid endpoint URL")) == "invalid_endpoint_url"
    assert cli.PolygonFlatFileAdapter.classify_value_error(ValueError("invalid header value")) == "invalid_header_value"
    assert cli.PolygonFlatFileAdapter.classify_value_error(ValueError("credential format invalid")) == "invalid_credential_format"


def test_no_auth_endpoint_probe_is_read_only_and_machine_readable(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []

    class FakeResponse:
        status = 403

        def read(self):
            return b""

    class FakeHTTPSConnection:
        def __init__(self, host, port=None, context=None, timeout=None):
            calls.append(("init", host))

        def request(self, method, path, headers=None):
            calls.append(("request", method))

        def getresponse(self):
            calls.append(("response", True))
            return FakeResponse()

        def close(self):
            calls.append(("close", True))

    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeContext:
        def wrap_socket(self, sock, server_hostname=None):
            calls.append(("wrap_socket", server_hostname))
            return FakeSocket()

    monkeypatch.setattr(adapter_mod.socket, "create_connection", lambda *args, **kwargs: object())
    monkeypatch.setattr(adapter_mod.ssl, "create_default_context", lambda: FakeContext())
    monkeypatch.setattr(adapter_mod.http.client, "HTTPSConnection", FakeHTTPSConnection)
    probe = cli.PolygonFlatFileAdapter.no_auth_endpoint_probe("https://files.massive.com")
    assert probe["no_auth_probe_attempted"] is True
    assert probe["no_auth_probe_tcp_connected"] is True
    assert probe["no_auth_probe_tls_connected"] is True
    assert probe["no_auth_probe_reachable"] is True
    assert probe["no_auth_probe_http_status_code"] == 403
    assert probe["no_auth_probe_error"] == ""
    assert ("request", "HEAD") in calls


def test_read_only_source_access_cli_json_runs_without_secret_echo(monkeypatch) -> None:
    env = os.environ.copy()
    env.update(
        {
            "POLYGON_API_KEY": "secret-value",
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "access-id",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret-access",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        }
    )
    result = subprocess.run(
        [sys.executable, "scripts/verify_polygon_stock_day_agg_read_only_source_access.py", "--date", "2026-06-15"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    data = json.loads(result.stdout)
    assert data["source_access_status"] in {"env_missing", "credentials_missing", "unsafe_to_proceed", "source_unreachable", "source_reachable", "date_object_not_found"}
    assert data["download_attempted"] is False
    assert data["db_write_attempted"] is False
    assert data["scheduler_activation_attempted"] is False
    assert data["object_key_includes_bucket_prefix"] is False
    assert data["explicit_session_client_mode"] is True
    assert data["environment_driven_client_mode"] is True
    for leaked in ["secret-value", "access-id", "secret-access"]:
        assert leaked not in result.stdout


def test_build_remote_listing_client_uses_massive_compatible_session_client(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        pass

    class FakeSession:
        def __init__(self, **kwargs):
            captured["session_kwargs"] = kwargs

        def client(self, service_name, **kwargs):
            captured["service_name"] = service_name
            captured["client_kwargs"] = kwargs
            return FakeClient()

    fake_boto3 = types.SimpleNamespace(Session=FakeSession)
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)
    monkeypatch.setattr(adapter_mod, "Config", lambda **kwargs: kwargs)
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    adapter = cli.PolygonFlatFileAdapter(
        env={
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "access-id",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret-access",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://files.massive.com/",
            "POLYGON_FLAT_FILE_BUCKET": "flatfiles",
            "POLYGON_FLAT_FILE_PREFIX": "us_stocks_sip/day_aggs_v1/",
        }
    )
    client = adapter.build_remote_listing_client()
    assert isinstance(client, FakeClient)
    assert captured["session_kwargs"] == {
        "aws_access_key_id": "access-id",
        "aws_secret_access_key": "secret-access",
        "region_name": "us-east-1",
    }
    assert captured["service_name"] == "s3"
    assert captured["client_kwargs"]["endpoint_url"] == "https://files.massive.com"


def test_build_remote_listing_client_env_driven_uses_endpoint_and_signature(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        pass

    def fake_client(service_name, **kwargs):
        captured["service_name"] = service_name
        captured["client_kwargs"] = kwargs
        return FakeClient()

    fake_boto3 = types.SimpleNamespace(client=fake_client)
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)
    monkeypatch.setattr(adapter_mod, "Config", lambda **kwargs: kwargs)
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    adapter = cli.PolygonFlatFileAdapter(
        env={
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "access-id",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret-access",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://files.massive.com/",
            "POLYGON_FLAT_FILE_BUCKET": "flatfiles",
            "POLYGON_FLAT_FILE_PREFIX": "us_stocks_sip/day_aggs_v1/",
        }
    )
    client = adapter.build_remote_listing_client_env_driven()
    assert isinstance(client, FakeClient)
    assert captured["service_name"] == "s3"
    assert captured["client_kwargs"]["endpoint_url"] == "https://files.massive.com"
