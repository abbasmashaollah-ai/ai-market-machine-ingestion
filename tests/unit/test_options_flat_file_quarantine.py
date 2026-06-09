from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.vendor_flat_files.options.options_flat_file_manifest import OPTIONS_PREFIX, OPTIONS_SAMPLE_DATE, OPTIONS_SAMPLE_KEY, classify_config, missing_names, present_names, redacted_key_tail
from app.vendor_flat_files.options.options_flat_file_quarantine import APPROVAL_PHRASE, DEFAULT_DATE, DEFAULT_LOCAL_RELATIVE_PATH, download_single_date_quarantine, options_object_key, options_output_path, redacted_options_tail, sha256_file


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


class _Boto3Stub:
    def __init__(self, client: _FakeClient) -> None:
        self.client_obj = client

    def client(self, *_args: object, **_kwargs: object) -> _FakeClient:
        return self.client_obj


def test_manifest_helpers_are_options_specific() -> None:
    assert OPTIONS_PREFIX == "us_options_opra/day_aggs_v1"
    assert OPTIONS_SAMPLE_DATE == "2025-11-05"
    assert OPTIONS_SAMPLE_KEY.endswith("2025/11/2025-11-05.csv.gz")
    assert redacted_key_tail(OPTIONS_SAMPLE_KEY) == "11/2025-11-05.csv.gz"
    assert options_object_key("2025-11-05") == OPTIONS_SAMPLE_KEY
    assert redacted_options_tail("2025-11-05") == "11/2025-11-05.csv.gz"
    assert classify_config({"POLYGON_FLAT_FILE_ACCESS_KEY_ID": "a", "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "b", "POLYGON_FLAT_FILE_ENDPOINT": "c", "POLYGON_FLAT_FILE_BUCKET": "d"}) == "polygon_flat_file"
    assert present_names({"POLYGON_FLAT_FILE_ACCESS_KEY_ID": "a"}) == ["POLYGON_FLAT_FILE_ACCESS_KEY_ID"]
    assert missing_names({"POLYGON_FLAT_FILE_ACCESS_KEY_ID": "a"}) == ["POLYGON_FLAT_FILE_SECRET_ACCESS_KEY", "POLYGON_FLAT_FILE_ENDPOINT", "POLYGON_FLAT_FILE_BUCKET"]


def test_output_path_and_sha256_helpers(tmp_path) -> None:
    output = options_output_path("2025-11-05", tmp_path)
    assert str(output).endswith("massive_options_day_aggs_2025-11-05.csv.gz")
    path = tmp_path / "sample.bin"
    path.write_bytes(b"abc")
    assert sha256_file(path) == hashlib.sha256(b"abc").hexdigest()


def test_default_run_blocks_without_approval() -> None:
    payload = download_single_date_quarantine(env={}, enabled=False, approval_phrase="", date_value=DEFAULT_DATE, quarantine_dir=DEFAULT_LOCAL_RELATIVE_PATH.parent)
    assert payload["approval_required"] is True
    assert payload["approval_phrase_matched"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["output_file_exists"] is False


def test_approved_run_downloads_one_object(tmp_path) -> None:
    client = _FakeClient(ok=True)
    payload = download_single_date_quarantine(
        env={
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
        },
        enabled=True,
        approval_phrase=APPROVAL_PHRASE,
        date_value=DEFAULT_DATE,
        quarantine_dir=tmp_path,
        boto3_module=_Boto3Stub(client),
    )
    assert payload["approval_phrase_matched"] is True
    assert payload["vendor_call_attempted"] is True
    assert payload["remote_head_object_attempted"] is True
    assert payload["download_attempted"] is True
    assert payload["download_succeeded"] is True
    assert payload["output_file_exists"] is True
    assert payload["output_file_size_bytes"] > 0
    assert payload["output_sha256"]
    assert payload["redacted_key_tail"] == "11/2025-11-05.csv.gz"
    assert any(call[1].get("Key") == OPTIONS_SAMPLE_KEY for call in client.calls)
    assert payload["decompression_attempted"] is False
    assert payload["parse_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_read_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False


def test_forbidden_client_error_returns_safe_json(tmp_path) -> None:
    client = _FakeClient(ok=False)
    payload = download_single_date_quarantine(
        env={
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
        },
        enabled=True,
        approval_phrase=APPROVAL_PHRASE,
        date_value=DEFAULT_DATE,
        quarantine_dir=tmp_path,
        boto3_module=_Boto3Stub(client),
    )
    assert payload["download_succeeded"] is False
    assert payload["output_file_exists"] is False
    assert payload["remote_download_error_code_redacted"] == "forbidden"
    text = json.dumps(payload).lower()
    for forbidden in ["POLYGON_FLAT_FILE_ACCESS_KEY_ID", "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY", "https://endpoint.invalid", OPTIONS_SAMPLE_KEY.lower(), '"etag"']:
        assert forbidden not in text
