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


class _FakeAdapter(cli.PolygonFlatFileAdapter):
    @staticmethod
    def boto3_available() -> bool:
        return True

    def __init__(self, env: dict[str, str] | None = None) -> None:
        super().__init__(env=env)
        self.download_calls: list[dict[str, object]] = []

    def download_single_date_object(self, *, value: str, local_path: str | Path, overwrite: bool = False) -> dict[str, object]:
        self.download_calls.append({"value": value, "local_path": str(local_path), "overwrite": overwrite})
        path = Path(local_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake gzip bytes")
        return {
            "downloaded": True,
            "skipped_existing": False,
            "local_file_exists": True,
            "local_file_size_bytes": path.stat().st_size,
            "local_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "redacted_key_tail": self.redacted_csv_gzip_tail(value),
            "local_quarantine_path": str(path),
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


def test_default_run_does_not_download(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--date", "2003-09-10"])
    assert payload["local_quarantine_download_enabled"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_object_download_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["decompression_attempted"] is False
    assert payload["parse_attempted"] is False


def test_wrong_approval_phrase_does_not_download(monkeypatch) -> None:
    payload = _run_cli(
        monkeypatch,
        ["--date", "2003-09-10", "--approve-local-quarantine-download", "--approval-phrase", "wrong phrase"],
    )
    assert payload["local_quarantine_download_enabled"] is False
    assert payload["download_attempted"] is False
    assert any("approval phrase" in blocker for blocker in payload["blockers"])


def test_approved_run_downloads_exactly_one_mocked_object(monkeypatch, tmp_path) -> None:
    fake = _FakeAdapter({})
    monkeypatch.setattr(cli, "PolygonFlatFileAdapter", lambda env=None: fake)
    quarantine_dir = tmp_path / "quarantine"
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2003-09-10",
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
    assert payload["local_quarantine_path"].endswith("polygon_stocks_day_aggs_2003-09-10.csv.gz")
    assert fake.download_calls and len(fake.download_calls) == 1
    text = json.dumps(payload).lower()
    for forbidden in ["polygon-key", "polygon-secret", "endpoint.invalid", "prefix/2003", "us_stocks_sip/day_aggs_v1"]:
        assert forbidden not in text


def test_existing_file_skips_until_overwrite(monkeypatch, tmp_path) -> None:
    fake = _FakeAdapter({})
    monkeypatch.setattr(cli, "PolygonFlatFileAdapter", lambda env=None: fake)
    quarantine_dir = tmp_path / "quarantine"
    path = quarantine_dir / "polygon_stocks_day_aggs_2003-09-10.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"existing")
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2003-09-10",
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
    assert fake.download_calls == []


def test_overwrite_flag_allows_rewrite(monkeypatch, tmp_path) -> None:
    fake = _FakeAdapter({})
    monkeypatch.setattr(cli, "PolygonFlatFileAdapter", lambda env=None: fake)
    quarantine_dir = tmp_path / "quarantine"
    path = quarantine_dir / "polygon_stocks_day_aggs_2003-09-10.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"existing")
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2003-09-10",
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
    assert fake.download_calls and fake.download_calls[0]["overwrite"] is True


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
    for forbidden_phrase in ["gzip.open(", "parse_csv", "to_sql(", "commit(", "create_engine(", "build_production_handoff(", "get_object("]:
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
