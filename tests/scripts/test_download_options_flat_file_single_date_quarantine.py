from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import scripts.download_options_flat_file_single_date_quarantine as cli


class _FakeClientError(Exception):
    def __init__(self, response: dict[str, object]) -> None:
        super().__init__("client error")
        self.response = response


class _Body:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.offset = 0

    def read(self, size: int) -> bytes:
        if self.offset >= len(self.payload):
            return b""
        chunk = self.payload[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk


class _FakeClient:
    def __init__(self, *, ok: bool = True) -> None:
        self.ok = ok
        self.calls: list[tuple[str, dict[str, object]]] = []

    def head_object(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("head", kwargs))
        if not self.ok:
            raise _FakeClientError({"Error": {"Code": "AccessDenied", "Message": "Forbidden"}, "ResponseMetadata": {"HTTPStatusCode": 403}})
        return {"ContentLength": 16, "ETag": '"etag"'}

    def get_object(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("get", kwargs))
        if not self.ok:
            raise _FakeClientError({"Error": {"Code": "AccessDenied", "Message": "Forbidden"}, "ResponseMetadata": {"HTTPStatusCode": 403}})
        payload = b"fake gzip bytes"
        return {"Body": _Body(payload), "ContentLength": len(payload)}


def _run_cli(monkeypatch, argv: list[str], env: dict[str, str] | None = None) -> dict[str, object]:
    if env is None:
        env = {}
    for name in ["POLYGON_FLAT_FILE_ACCESS_KEY_ID", "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY", "POLYGON_FLAT_FILE_ENDPOINT", "POLYGON_FLAT_FILE_BUCKET"]:
        monkeypatch.delenv(name, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_default_run_does_not_download(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, [])
    assert payload["approval_required"] is True
    assert payload["approval_phrase_matched"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["download_succeeded"] is False
    assert payload["output_file_exists"] is False


def test_wrong_approval_phrase_does_not_download(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--approval-phrase", "wrong phrase"])
    assert payload["approval_phrase_matched"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["output_file_exists"] is False


def test_approved_run_downloads_one_object(monkeypatch, tmp_path) -> None:
    client = _FakeClient(ok=True)
    original_boto3 = cli.boto3
    cli.boto3 = SimpleNamespace(client=lambda *args, **kwargs: client)
    try:
        payload = cli._safe_payload(
            enabled=True,
            approval_phrase=cli.APPROVAL_PHRASE,
            date_value=cli.DEFAULT_DATE,
            quarantine_dir=str(tmp_path),
            overwrite_local_file=False,
            env={
                "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
                "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
                "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
                "POLYGON_FLAT_FILE_BUCKET": "bucket",
            },
        )
    finally:
        cli.boto3 = original_boto3
    assert payload["approval_phrase_matched"] is True
    assert payload["vendor_call_attempted"] is True
    assert payload["remote_head_object_attempted"] is True
    assert payload["download_attempted"] is True
    assert payload["download_succeeded"] is True
    assert payload["output_file_exists"] is True
    assert payload["output_file_size_bytes"] > 0
    assert payload["output_sha256"]
    assert payload["output_path"].endswith("massive_options_day_aggs_2025-11-05.csv.gz")
    assert any(call[1].get("Key") == "us_options_opra/day_aggs_v1/2025/11/2025-11-05.csv.gz" for call in client.calls)
    text = json.dumps(payload).lower()
    for forbidden in ["polygon_flat_file_endpoint", "bucket", "us_options_opra/day_aggs_v1/2025/11/2025-11-05.csv.gz", '"etag"']:
        assert forbidden not in text


def test_forbidden_client_error_returns_safe_json(monkeypatch, tmp_path) -> None:
    client = _FakeClient(ok=False)
    original_boto3 = cli.boto3
    cli.boto3 = SimpleNamespace(client=lambda *args, **kwargs: client)
    try:
        payload = cli._safe_payload(
            enabled=True,
            approval_phrase=cli.APPROVAL_PHRASE,
            date_value=cli.DEFAULT_DATE,
            quarantine_dir=str(tmp_path),
            overwrite_local_file=False,
            env={
                "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
                "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
                "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
                "POLYGON_FLAT_FILE_BUCKET": "bucket",
            },
        )
    finally:
        cli.boto3 = original_boto3
    assert payload["download_succeeded"] is False
    assert payload["output_file_exists"] is False
    assert payload["remote_download_error_code_redacted"] == "forbidden"
    text = json.dumps(payload).lower()
    for forbidden in ["POLYGON_FLAT_FILE_ACCESS_KEY_ID", "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY", "https://endpoint.invalid", "us_options_opra/day_aggs_v1/2025/11/2025-11-05.csv.gz", '"etag"']:
        assert forbidden not in text


def test_missing_boto3_returns_safe_blocker(monkeypatch) -> None:
    original_boto3 = cli.boto3
    cli.boto3 = None
    try:
        payload = cli._safe_payload(
            enabled=True,
            approval_phrase=cli.APPROVAL_PHRASE,
            date_value=cli.DEFAULT_DATE,
            quarantine_dir="outputs/quarantine/options_flat_files",
            overwrite_local_file=False,
            env={
                "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
                "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
                "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
                "POLYGON_FLAT_FILE_BUCKET": "bucket",
            },
        )
    finally:
        cli.boto3 = original_boto3
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["remote_download_error_code_redacted"] == "client_error"
    assert any("client_error" in blocker.lower() for blocker in payload["blockers"])


def test_help_mentions_required_flags() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/download_options_flat_file_single_date_quarantine.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--approval-phrase" in result.stdout
    assert "--approve-local-quarantine-download" in result.stdout
