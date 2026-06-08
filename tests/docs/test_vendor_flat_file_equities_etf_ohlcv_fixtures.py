from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from tests.fixtures.vendor_flat_files.polygon.flat_file_fixture_validator import validate_manifest_and_csv


EQUITIES_CSV = Path("tests/fixtures/vendor_flat_files/polygon/equities/daily/2026/01/15/equities_daily_2026-01-15_sample.csv")
EQUITIES_MANIFEST = Path("tests/fixtures/vendor_flat_files/polygon/equities/daily/2026/01/15/manifest.json")
ETFS_CSV = Path("tests/fixtures/vendor_flat_files/polygon/etfs/daily/2026/01/15/etfs_daily_2026-01-15_sample.csv")
ETFS_MANIFEST = Path("tests/fixtures/vendor_flat_files/polygon/etfs/daily/2026/01/15/manifest.json")


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_fixture_files_exist_and_validate() -> None:
    assert EQUITIES_CSV.exists()
    assert EQUITIES_MANIFEST.exists()
    assert ETFS_CSV.exists()
    assert ETFS_MANIFEST.exists()

    assert validate_manifest_and_csv(EQUITIES_CSV, EQUITIES_MANIFEST) == []
    assert validate_manifest_and_csv(ETFS_CSV, ETFS_MANIFEST) == []


def test_manifest_sha256_matches_csv_content() -> None:
    equities_manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    etfs_manifest = json.loads(ETFS_MANIFEST.read_text(encoding="utf-8"))

    assert equities_manifest["source_file_sha256"] == hashlib.sha256(EQUITIES_CSV.read_bytes()).hexdigest()
    assert etfs_manifest["source_file_sha256"] == hashlib.sha256(ETFS_CSV.read_bytes()).hexdigest()


def test_validator_rejects_bad_rows() -> None:
    rows = _csv_rows(EQUITIES_CSV)
    bad_missing_ticker = [dict(rows[0], ticker="")]
    bad_missing_date = [dict(rows[0], date="")]
    bad_negative_volume = [dict(rows[0], volume="-1")]
    bad_duplicate = [rows[0], dict(rows[0])]
    bad_invalid_ohlc = [dict(rows[0], open="9999", high="1", low="0", close="1")]

    def _write_temp_csv(rows_to_write: list[dict[str, str]], path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows_to_write)

    tmp_dir = Path("tests/fixtures/vendor_flat_files/polygon/_tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    temp_csv = tmp_dir / "temp.csv"
    temp_manifest = tmp_dir / "manifest.json"
    temp_manifest.write_text(EQUITIES_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")

    for rows_to_write, expected in [
        (bad_missing_ticker, "missing ticker"),
        (bad_missing_date, "missing date"),
        (bad_negative_volume, "negative volume"),
        (bad_duplicate, "duplicate ticker/date rows"),
        (bad_invalid_ohlc, "invalid ohlc values"),
    ]:
        _write_temp_csv(rows_to_write, temp_csv)
        errors = validate_manifest_and_csv(temp_csv, temp_manifest)
        assert expected in errors


def test_validator_allows_missing_optional_vwap_and_transactions() -> None:
    rows = _csv_rows(EQUITIES_CSV)
    temp_dir = Path("tests/fixtures/vendor_flat_files/polygon/_tmp_optional")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_csv = temp_dir / "temp.csv"
    temp_manifest = temp_dir / "manifest.json"
    temp_manifest.write_text(EQUITIES_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")

    with temp_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["ticker", "date", "open", "high", "low", "close", "volume", "adjusted"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: value for key, value in row.items() if key in writer.fieldnames})

    manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    manifest["source_file_sha256"] = hashlib.sha256(temp_csv.read_bytes()).hexdigest()
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    errors = validate_manifest_and_csv(temp_csv, temp_manifest)
    assert errors == []
