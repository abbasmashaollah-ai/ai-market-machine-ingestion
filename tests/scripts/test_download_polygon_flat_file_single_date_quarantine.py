from __future__ import annotations

import ast
import io
import json
import hashlib
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.download_polygon_flat_file_single_date_quarantine as cli


class _FakeClientError(Exception):
    def __init__(self, response: dict[str, object]) -> None:
        super().__init__("client error")
        self.response = response


class _FakeClient:
    def __init__(self, *, has_object: bool) -> None:
        self.has_object = has_object
        self.list_calls: list[dict[str, object]] = []
        self.get_calls: list[dict[str, object]] = []

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        self.list_calls.append(kwargs)
        prefix = str(kwargs.get("Prefix") or "")
        if not self.has_object:
            return {"Contents": []}
        if prefix.endswith("us_stocks_sip/day_aggs_v1/2003/09/") or prefix.endswith("us_stocks_sip/day_aggs_v1/2026/06/"):
            return {
                "Contents": [
                    {
                        "Key": "us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz",
                        "Size": 15,
                        "LastModified": "x",
                        "ETag": "etag-1",
                    },
                    {
                        "Key": "us_stocks_sip/day_aggs_v1/2026/06/2026-06-15.csv.gz",
                        "Size": 19,
                        "LastModified": "x",
                        "ETag": "etag-2",
                    }
                ]
            }
        return {"Contents": []}

    def download_file(self, **kwargs: object) -> None:
        self.get_calls.append(kwargs)
        path = Path(str(kwargs["Filename"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake gzip bytes")

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

    def get_object(self, **kwargs: object) -> dict[str, object]:
        self.get_calls.append(kwargs)
        if kwargs.get("Key") in {
            "us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz",
            "us_stocks_sip/day_aggs_v1/2026/06/2026-06-15.csv.gz",
        }:
            payload = b"fake gzip bytes"
            return {"Body": self._Body(payload), "ContentLength": len(payload)}
        raise RuntimeError("unexpected key")

def _run_cli(monkeypatch, argv: list[str], env: dict[str, str] | None = None) -> dict[str, object]:
    for name in cli.REQUIRED_CONFIG_NAMES:
        monkeypatch.delenv(name, raising=False)
    if env:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_default_run_does_not_download(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--date", "2026-06-15"])
    assert payload["local_quarantine_download_enabled"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_object_download_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["decompression_attempted"] is False
    assert payload["parse_attempted"] is False


def test_wrong_approval_phrase_does_not_download(monkeypatch) -> None:
    payload = _run_cli(
        monkeypatch,
        ["--date", "2026-06-15", "--approve-local-quarantine-download", "--approval-phrase", "wrong phrase"],
    )
    assert payload["local_quarantine_download_enabled"] is False
    assert payload["download_attempted"] is False
    assert any("approval phrase" in blocker for blocker in payload["blockers"])


def test_approved_run_downloads_exactly_one_mocked_object(monkeypatch, tmp_path) -> None:
    fake = _FakeClient(has_object=True)
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    quarantine_dir = tmp_path / "quarantine"
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2026-06-15",
            "--approve-local-quarantine-download",
            "--approval-phrase",
            cli.APPROVAL_PHRASE,
            "--quarantine-dir",
            str(quarantine_dir),
        ],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["local_quarantine_download_enabled"] is True
    assert payload["vendor_call_attempted"] is True
    assert payload["remote_object_download_attempted"] is True
    assert payload["download_attempted"] is True
    assert payload["local_file_exists"] is True
    assert payload["local_file_size_bytes"] > 0
    assert payload["local_file_sha256"]
    assert payload["local_quarantine_path"].endswith("polygon_stocks_day_aggs_2026-06-15.csv.gz")
    assert fake.list_calls and len(fake.list_calls) >= 1
    assert any(call.get("Key") == "us_stocks_sip/day_aggs_v1/2026/06/2026-06-15.csv.gz" for call in fake.get_calls)
    assert not any("download_file" in call for call in fake.get_calls if isinstance(call, dict))
    assert payload["resolved_key_present"] is True
    assert payload["resolved_key_tail_matches_requested_date"] is True
    assert payload["resolved_key_matches_listed_key"] is True
    assert len(payload["resolved_key_sha256_prefix"]) == 12
    assert len(payload["listed_key_sha256_prefix"]) == 12
    text = json.dumps(payload).lower()
    for forbidden in ["polygon-key", "polygon-secret", "endpoint.invalid", "prefix/2003", "us_stocks_sip/day_aggs_v1"]:
        assert forbidden not in text


def test_existing_file_skips_until_overwrite(monkeypatch, tmp_path) -> None:
    fake = _FakeClient(has_object=True)
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    quarantine_dir = tmp_path / "quarantine"
    path = quarantine_dir / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"existing")
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2026-06-15",
            "--approve-local-quarantine-download",
            "--approval-phrase",
            cli.APPROVAL_PHRASE,
            "--quarantine-dir",
            str(quarantine_dir),
        ],
    )
    assert payload["download_attempted"] is False
    assert payload["local_file_exists"] is True
    assert payload["local_file_size_bytes"] == len(b"existing")
    assert fake.get_calls == []


def test_overwrite_flag_allows_rewrite(monkeypatch, tmp_path) -> None:
    fake = _FakeClient(has_object=True)
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    quarantine_dir = tmp_path / "quarantine"
    path = quarantine_dir / "polygon_stocks_day_aggs_2026-06-15.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"existing")
    original_size = path.stat().st_size
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2026-06-15",
            "--approve-local-quarantine-download",
            "--approval-phrase",
            cli.APPROVAL_PHRASE,
            "--quarantine-dir",
            str(quarantine_dir),
            "--overwrite-local-file",
        ],
    )
    assert payload["download_attempted"] is True
    assert payload["local_file_exists"] is True
    assert payload["local_file_sha256"]
    assert path.stat().st_size != original_size
    assert any(call.get("Key") == "us_stocks_sip/day_aggs_v1/2026/06/2026-06-15.csv.gz" for call in fake.get_calls)


def test_manifest_missing_prevents_download(monkeypatch, tmp_path) -> None:
    fake = _FakeClient(has_object=False)
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    quarantine_dir = tmp_path / "quarantine"
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2026-06-15",
            "--approve-local-quarantine-download",
            "--approval-phrase",
            cli.APPROVAL_PHRASE,
            "--quarantine-dir",
            str(quarantine_dir),
        ],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["download_attempted"] is False
    assert payload["local_file_exists"] is False
    assert fake.get_calls == []
    assert any("not present in the manifest listing" in blocker for blocker in payload["blockers"])


def test_forbidden_get_object_returns_safe_json(monkeypatch, tmp_path) -> None:
    fake = _FakeClient(has_object=True)

    def _raise_forbidden(**kwargs: object) -> dict[str, object]:
        fake.get_calls.append(kwargs)
        raise _FakeClientError({"Error": {"Code": "AccessDenied", "Message": "Forbidden"}, "ResponseMetadata": {"HTTPStatusCode": 403}})

    fake.get_object = _raise_forbidden  # type: ignore[assignment]
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    quarantine_dir = tmp_path / "quarantine"
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2026-06-15",
            "--approve-local-quarantine-download",
            "--approval-phrase",
            cli.APPROVAL_PHRASE,
            "--quarantine-dir",
            str(quarantine_dir),
        ],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["download_attempted"] is True
    assert payload["remote_object_download_attempted"] is True
    assert payload["remote_download_status"] == "forbidden"
    assert payload["local_file_exists"] is False
    assert not (quarantine_dir / "polygon_stocks_day_aggs_2026-06-15.csv.gz").exists()
    text = json.dumps(payload).lower()
    for forbidden in ["polygon-key", "polygon-secret", "endpoint.invalid", "prefix/2003", "us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz"]:
        assert forbidden not in text


def test_source_scan_blocks_decompression_parse_export_db_scheduler_and_mutation() -> None:
    source = Path("scripts/download_polygon_flat_file_single_date_quarantine.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    imports = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.lower())
    for forbidden in ["requests", "httpx", "sqlalchemy", "alembic", "app.api", "app.scheduler.jobs"]:
        assert forbidden not in imports
    for forbidden_phrase in ["gzip.open(", "parse_csv", "to_sql(", "commit(", "create_engine(", "build_production_handoff("]:
        assert forbidden_phrase not in source


def test_help_mentions_required_approval_flags() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/download_polygon_flat_file_single_date_quarantine.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--approve-local-quarantine-download" in result.stdout
    assert "--approval-phrase" in result.stdout
