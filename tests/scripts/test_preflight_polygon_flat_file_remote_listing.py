from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.preflight_polygon_flat_file_remote_listing as cli


class _FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("list_objects_v2", kwargs))
        return {
            "Contents": [
                {"Key": "polygon/etfs/daily/2026/01/15/etfs_daily_2026-01-15_sample.csv"},
                {"Key": "polygon/etfs/daily/2026/01/15/manifest.json"},
            ]
        }


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
    payload = _run_cli(monkeypatch, [])
    assert payload["remote_listing_enabled"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_bucket_list_attempted"] is False
    assert payload["remote_object_list_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["remote_file_read_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False


def test_remote_listing_requires_explicit_flag(monkeypatch) -> None:
    payload = _run_cli(
        monkeypatch,
        ["--enable-remote-listing"],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    if payload["boto3_available"]:
        assert payload["vendor_call_attempted"] is True
        assert payload["remote_object_list_attempted"] is True
    else:
        assert payload["vendor_call_attempted"] is False
        assert payload["remote_object_list_attempted"] is False


def test_max_keys_is_capped_at_25(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--max-keys", "99"])
    assert payload["max_keys_requested"] == 99
    assert payload["max_keys_effective"] == 25


def test_safe_payload_redacts_key_samples(monkeypatch) -> None:
    fake = _FakeS3Client()
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    payload = _run_cli(
        monkeypatch,
        ["--enable-remote-listing", "--max-keys", "5"],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["object_count_seen"] == 2
    assert payload["object_key_samples_redacted"] == [
        "15/etfs_daily_2026-01-15_sample.csv",
        "15/manifest.json",
    ]
    assert "polygon/etfs" not in json.dumps(payload).lower()
    assert fake.calls and fake.calls[0][0] == "list_objects_v2"


def test_missing_boto3_is_blocked_safely(monkeypatch) -> None:
    monkeypatch.setattr(cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: False))
    payload = _run_cli(
        monkeypatch,
        ["--enable-remote-listing"],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["boto3_available"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_object_list_attempted"] is False
    assert any("boto3 is required" in blocker for blocker in payload["blockers"])


def test_source_scan_blocks_download_read_write_db_scheduler_ingestion_and_mutation() -> None:
    source = Path("scripts/preflight_polygon_flat_file_remote_listing.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())
    for forbidden in ["requests", "httpx", "sqlalchemy", "alembic", "app.api", "app.scheduler.jobs"]:
        assert forbidden not in import_names
    for forbidden_phrase in [
        "get_object(",
        "download_file(",
        "to_sql(",
        "commit(",
        "create_engine(",
        "scheduler.start",
        "ingest(",
        "put_object(",
        "build_production_handoff(",
    ]:
        assert forbidden_phrase not in source
    for required_phrase in [
        "remote_file_read_attempted",
        "production_handoff_generation_authorized",
        "db_write_attempted",
        "scheduler_activation_attempted",
        "ingestion_attempted",
        "production_mutation_attempted",
    ]:
        assert required_phrase in source


def test_help_mentions_enable_remote_listing_and_max_keys() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_polygon_flat_file_remote_listing.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--enable-remote-listing" in result.stdout
    assert "--max-keys" in result.stdout
