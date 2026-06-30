from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import scripts.download_polygon_stock_day_agg_single_date_quarantine as cli
import scripts.download_polygon_flat_file_single_date_quarantine as base_cli


class _FakeClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

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

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        if str(kwargs.get("Prefix") or "").endswith("2026/06/"):
            return {"Contents": [{"Key": "us_stocks_sip/day_aggs_v1/2026/06/2026-06-26.csv.gz", "Size": 316221, "LastModified": "x", "ETag": "etag"}]}
        return {"Contents": []}

    def get_object(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        payload = b"fake gzip bytes"
        return {"Body": self._Body(payload), "ContentLength": len(payload)}


def _run_cli(monkeypatch, argv: list[str], env: dict[str, str] | None = None) -> dict[str, object]:
    for name in base_cli.REQUIRED_CONFIG_NAMES:
        monkeypatch.delenv(name, raising=False)
    if env:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_wrong_approval_phrase_blocks(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--date", "2026-06-26", "--approve-local-quarantine-download", "--approval-phrase", "wrong"])
    assert payload["download_attempted"] is False
    assert payload["date_authorized"] is False
    assert any("approval phrase" in blocker for blocker in payload["blockers"])


def test_missing_approval_phrase_blocks(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--date", "2026-06-26", "--approve-local-quarantine-download"])
    assert payload["download_attempted"] is False
    assert payload["date_authorized"] is False


def test_wrong_date_blocks(monkeypatch) -> None:
    payload = _run_cli(monkeypatch, ["--date", "2026-06-15", "--approve-local-quarantine-download", "--approval-phrase", cli.APPROVAL_PHRASE])
    assert payload["download_attempted"] is False
    assert payload["date_authorized"] is False
    assert any("date does not match" in blocker for blocker in payload["blockers"])


def test_approved_one_date_path_permits_download_code_path(monkeypatch, tmp_path) -> None:
    fake = _FakeClient()
    monkeypatch.setattr(base_cli.PolygonFlatFileAdapter, "boto3_available", staticmethod(lambda: True))
    monkeypatch.setattr(base_cli.PolygonFlatFileAdapter, "build_remote_listing_client", lambda self: fake)
    payload = _run_cli(
        monkeypatch,
        [
            "--date",
            "2026-06-26",
            "--approve-local-quarantine-download",
            "--approval-phrase",
            cli.APPROVAL_PHRASE,
            "--quarantine-dir",
            str(tmp_path),
        ],
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        },
    )
    assert payload["download_attempted"] is True
    assert payload["local_quarantine_path"].endswith("polygon_stocks_day_aggs_2026-06-26.csv.gz")
    assert payload["remote_file_read_attempted"] is False
    assert payload["parse_attempted"] is False
    assert payload["normalization_attempted"] is False
    assert payload["handoff_generation_attempted"] is False
    assert payload["intake_package_generation_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["ai_wiring_attempted"] is False
