from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.preflight_polygon_flat_file_manifest as cli


class _FakeClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        prefix = str(kwargs.get("Prefix") or "")
        if prefix.endswith("09/2003"):
            return {
                "Contents": [
                    {"Key": "09/2003-09-10.csv.gz", "Size": 101, "LastModified": "x", "ETag": "etag-1"},
                    {"Key": "09/2003-09-11.csv.gz", "Size": 102},
                ]
            }
        return {"Contents": []}


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


def test_default_run_does_not_list_remote_objects(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--start-date", "2026-01-01", "--end-date", "2026-01-05"])
    assert payload["manifest_listing_enabled"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_object_list_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["remote_file_read_attempted"] is False


def test_explicit_flag_required(monkeypatch) -> None:
    payload = _run_cli(
        monkeypatch,
        ["--enable-remote-listing", "--start-date", "2026-01-01", "--end-date", "2026-01-05"],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["manifest_listing_enabled"] is True


def test_date_count_is_capped_at_25(monkeypatch) -> None:
    payload = _run_cli(
        monkeypatch,
        ["--enable-remote-listing", "--start-date", "2026-01-01", "--end-date", "2026-02-01", "--max-days", "99"],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["date_count_effective"] == 25


def test_mocked_listing_returns_redacted_manifest_entries(monkeypatch) -> None:
    fake = _FakeClient()
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    adapter = cli.PolygonFlatFileAdapter(
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        }
    )
    entries = adapter.list_remote_manifest_objects(start_date="2003-09-10", end_date="2003-09-12", max_days=5)
    assert entries[0]["redacted_key_tail"] == "09/2003-09-10.csv.gz"
    assert entries[0]["object_present"] is True
    assert entries[1]["redacted_key_tail"] == "09/2003-09-11.csv.gz"
    assert entries[1]["object_present"] is True
    assert entries[2]["redacted_key_tail"] == "09/2003-09-12.csv.gz"
    assert entries[2]["object_present"] is False
    text = json.dumps(entries).lower()
    for forbidden in ["polygon-key", "polygon-secret", "endpoint.invalid", "prefix/"]:
        assert forbidden not in text
    assert fake.calls
    assert all("manifest.json" not in json.dumps(entry).lower() for entry in entries)


def test_detects_known_visible_object_by_redacted_tail(monkeypatch) -> None:
    fake = _FakeClient()
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    adapter = cli.PolygonFlatFileAdapter(
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        }
    )
    entries = adapter.list_remote_manifest_objects(start_date="2003-09-10", end_date="2003-09-16", max_days=7)
    assert any(entry["redacted_key_tail"] == "09/2003-09-10.csv.gz" and entry["object_present"] is True for entry in entries)
    assert any(entry["date"] == "2003-09-12" and entry["object_present"] is False for entry in entries)


def test_missing_boto3_is_safe(monkeypatch) -> None:
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: False))
    payload = _run_cli(
        monkeypatch,
        ["--enable-remote-listing", "--start-date", "2026-01-01", "--end-date", "2026-01-05"],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_object_list_attempted"] is False
    assert any("boto3" in blocker for blocker in payload["blockers"])


def test_source_scan_blocks_download_read_export_db_scheduler_and_mutation() -> None:
    source = Path("scripts/preflight_polygon_flat_file_manifest.py").read_text(encoding="utf-8").lower()
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
    for forbidden_phrase in ["get_object(", "download_file(", "to_sql(", "commit(", "create_engine(", "put_object(", "build_production_handoff("]:
        assert forbidden_phrase not in source


def test_help_mentions_required_flags() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_polygon_flat_file_manifest.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--enable-remote-listing" in result.stdout
    assert "--start-date" in result.stdout
    assert "--end-date" in result.stdout
    assert "--max-days" in result.stdout
