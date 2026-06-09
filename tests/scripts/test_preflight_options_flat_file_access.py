from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import scripts.preflight_options_flat_file_access as cli


class _FakeClientError(Exception):
    def __init__(self, response: dict[str, object]) -> None:
        super().__init__("client error")
        self.response = response


class _FakeClient:
    def __init__(self, *, ok: bool = True) -> None:
        self.ok = ok
        self.calls: list[tuple[str, dict[str, object]]] = []

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("list", kwargs))
        if not self.ok:
            raise _FakeClientError({"Error": {"Code": "AccessDenied", "Message": "Forbidden"}, "ResponseMetadata": {"HTTPStatusCode": 403}})
        return {"Contents": [{"Key": "us_options_opra/day_aggs_v1/2025/11/2025-11-05.csv.gz", "Size": 1}]}

    def head_object(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("head", kwargs))
        if not self.ok:
            raise _FakeClientError({"Error": {"Code": "AccessDenied", "Message": "Forbidden"}, "ResponseMetadata": {"HTTPStatusCode": 403}})
        return {"ContentLength": 1, "ETag": '"etag"'}


def _run_cli(monkeypatch, argv: list[str], env: dict[str, str] | None = None) -> dict[str, object]:
    for name in cli.OPTIONS_CONFIG_NAMES:
        monkeypatch.delenv(name, raising=False)
    if env:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_default_run_does_not_call_vendor(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, [])
    assert payload["options_remote_check_enabled"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_object_list_attempted"] is False
    assert payload["remote_head_object_attempted"] is False
    assert payload["download_attempted"] is False


def test_explicit_remote_check_with_mocked_success(monkeypatch) -> None:
    fake = _FakeClient(ok=True)
    original_boto3 = cli.boto3
    cli.boto3 = SimpleNamespace(client=lambda *args, **kwargs: fake)
    payload = cli._safe_payload(
        enabled=True,
        env={
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
        },
    )
    cli.boto3 = original_boto3
    assert payload["options_remote_check_enabled"] is True
    assert payload["vendor_call_attempted"] is True
    assert payload["remote_object_list_attempted"] is True
    assert payload["remote_head_object_attempted"] is True
    assert payload["known_object_present"] is True
    assert payload["content_length_present"] is True
    assert payload["redacted_key_tail"] == "11/2025-11-05.csv.gz"
    text = json.dumps(payload).lower()
    for forbidden in ["POLYGON_FLAT_FILE_ACCESS_KEY_ID", "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY", "endpoint.invalid", "us_options_opra/day_aggs_v1/2025/11/2025-11-05.csv.gz", '"etag"']:
        assert forbidden not in text


def test_forbidden_client_error_returns_safe_json(monkeypatch) -> None:
    fake = _FakeClient(ok=False)
    original_boto3 = cli.boto3
    cli.boto3 = SimpleNamespace(client=lambda *args, **kwargs: fake)
    payload = cli._safe_payload(
        enabled=True,
        env={
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
        },
    )
    cli.boto3 = original_boto3
    assert payload["vendor_call_attempted"] is True
    assert payload["known_object_present"] is False
    assert payload["content_length_present"] is False
    assert payload["remote_status"] == "forbidden"
    assert payload["remote_error_message_redacted"] == "remote check failed safely"
    text = json.dumps(payload).lower()
    for forbidden in ["POLYGON_FLAT_FILE_ACCESS_KEY_ID", "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY", "https://endpoint.invalid", "us_options_opra/day_aggs_v1/2025/11/2025-11-05.csv.gz", '"etag"']:
        assert forbidden not in text


def test_help_mentions_remote_check_flag() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_options_flat_file_access.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--enable-remote-check" in result.stdout
