from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from app.vendor_flat_files.local_ohlcv_parser import parse_local_ohlcv_fixture


EQUITIES_CSV = Path("tests/fixtures/vendor_flat_files/polygon/equities/daily/2026/01/15/equities_daily_2026-01-15_sample.csv")
EQUITIES_MANIFEST = Path("tests/fixtures/vendor_flat_files/polygon/equities/daily/2026/01/15/manifest.json")
ETFS_CSV = Path("tests/fixtures/vendor_flat_files/polygon/etfs/daily/2026/01/15/etfs_daily_2026-01-15_sample.csv")
ETFS_MANIFEST = Path("tests/fixtures/vendor_flat_files/polygon/etfs/daily/2026/01/15/manifest.json")


def test_parses_equities_synthetic_fixture_successfully() -> None:
    result = parse_local_ohlcv_fixture(EQUITIES_CSV, EQUITIES_MANIFEST, expected_asset_class="equities", expected_observation_date="2026-01-15")

    assert result.parse_status == "PASS"
    assert result.row_count == 3
    assert result.symbols == ("AAPL", "MSFT", "NVDA")
    assert result.source_file_sha256 == hashlib.sha256(EQUITIES_CSV.read_bytes()).hexdigest()
    assert result.rows[0]["symbol"] == "AAPL"
    assert result.rows[0]["observation_date"] == "2026-01-15"
    assert result.rows[0]["manifest_path"].endswith("manifest.json")
    assert result.rows[0]["lineage_id"] == "fixture-lineage-equities-2026-01-15"
    assert result.rows[0]["source_file_sha256"] == result.source_file_sha256


def test_parses_etf_synthetic_fixture_successfully() -> None:
    result = parse_local_ohlcv_fixture(ETFS_CSV, ETFS_MANIFEST, expected_asset_class="etfs", expected_observation_date="2026-01-15")

    assert result.parse_status == "PASS"
    assert result.row_count == 5
    assert result.symbols == ("DIA", "IWM", "QQQ", "SPY", "XLK")
    assert all(row["symbol"] == str(row["symbol"]).upper() for row in result.rows)
    assert all(row["observation_date"] == "2026-01-15" for row in result.rows)


def test_verifies_sha_before_parsing_and_blocks_mismatch() -> None:
    manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    manifest["source_file_sha256"] = "0" * 64
    temp_manifest = EQUITIES_MANIFEST.parent / "checksum_mismatch_manifest.json"
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        result = parse_local_ohlcv_fixture(EQUITIES_CSV, temp_manifest, expected_asset_class="equities", expected_observation_date="2026-01-15")
        assert result.parse_status == "FAIL"
        assert any(error.code == "CHECKSUM_MISMATCH" for error in result.errors)
    finally:
        temp_manifest.unlink(missing_ok=True)


def test_missing_required_column_returns_required_column_missing() -> None:
    csv_text = EQUITIES_CSV.read_text(encoding="utf-8").replace("volume", "amount", 1)
    temp_csv = EQUITIES_CSV.parent / "missing_column.csv"
    temp_csv.write_text(csv_text, encoding="utf-8")
    temp_manifest = EQUITIES_MANIFEST.parent / "missing_column_manifest.json"
    manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    manifest["source_file_sha256"] = hashlib.sha256(temp_csv.read_bytes()).hexdigest()
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        result = parse_local_ohlcv_fixture(temp_csv, temp_manifest, expected_asset_class="equities", expected_observation_date="2026-01-15")
        assert any(error.code == "REQUIRED_COLUMN_MISSING" for error in result.errors)
    finally:
        temp_csv.unlink(missing_ok=True)
        temp_manifest.unlink(missing_ok=True)


def test_invalid_ohlc_returns_invalid_ohlc() -> None:
    temp_csv = EQUITIES_CSV.parent / "invalid_ohlc.csv"
    temp_csv.write_text(EQUITIES_CSV.read_text(encoding="utf-8").replace("232.55", "-1.00", 1), encoding="utf-8")
    temp_manifest = EQUITIES_MANIFEST.parent / "invalid_ohlc_manifest.json"
    manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    manifest["source_file_sha256"] = hashlib.sha256(temp_csv.read_bytes()).hexdigest()
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        result = parse_local_ohlcv_fixture(temp_csv, temp_manifest, expected_asset_class="equities", expected_observation_date="2026-01-15")
        assert any(error.code == "INVALID_OHLC" for error in result.errors)
    finally:
        temp_csv.unlink(missing_ok=True)
        temp_manifest.unlink(missing_ok=True)


def test_negative_volume_returns_negative_volume() -> None:
    temp_csv = EQUITIES_CSV.parent / "negative_volume.csv"
    temp_csv.write_text(EQUITIES_CSV.read_text(encoding="utf-8").replace("51234000", "-1", 1), encoding="utf-8")
    temp_manifest = EQUITIES_MANIFEST.parent / "negative_volume_manifest.json"
    manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    manifest["source_file_sha256"] = hashlib.sha256(temp_csv.read_bytes()).hexdigest()
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        result = parse_local_ohlcv_fixture(temp_csv, temp_manifest, expected_asset_class="equities", expected_observation_date="2026-01-15")
        assert any(error.code == "NEGATIVE_VOLUME" for error in result.errors)
    finally:
        temp_csv.unlink(missing_ok=True)
        temp_manifest.unlink(missing_ok=True)


def test_duplicate_ticker_date_returns_duplicate_symbol_date() -> None:
    temp_csv = EQUITIES_CSV.parent / "duplicate.csv"
    temp_csv.write_text(EQUITIES_CSV.read_text(encoding="utf-8") + EQUITIES_CSV.read_text(encoding="utf-8").splitlines()[1] + "\n", encoding="utf-8")
    temp_manifest = EQUITIES_MANIFEST.parent / "duplicate_manifest.json"
    manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    manifest["row_count"] = 4
    manifest["symbols_count"] = 3
    manifest["source_file_sha256"] = hashlib.sha256(temp_csv.read_bytes()).hexdigest()
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        result = parse_local_ohlcv_fixture(temp_csv, temp_manifest, expected_asset_class="equities", expected_observation_date="2026-01-15")
        assert any(error.code == "DUPLICATE_SYMBOL_DATE" for error in result.errors)
    finally:
        temp_csv.unlink(missing_ok=True)
        temp_manifest.unlink(missing_ok=True)


def test_missing_optional_vwap_transactions_warns_but_passes() -> None:
    temp_csv = EQUITIES_CSV.parent / "optional_missing.csv"
    temp_csv.write_text(
        "ticker,date,open,high,low,close,volume,adjusted\n"
        "AAPL,2026-01-15,230.10,232.55,228.90,231.40,51234000,true\n",
        encoding="utf-8",
    )
    temp_manifest = EQUITIES_MANIFEST.parent / "optional_missing_manifest.json"
    manifest = json.loads(EQUITIES_MANIFEST.read_text(encoding="utf-8"))
    manifest["row_count"] = 1
    manifest["symbols_count"] = 1
    manifest["source_file_sha256"] = hashlib.sha256(temp_csv.read_bytes()).hexdigest()
    temp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    try:
        result = parse_local_ohlcv_fixture(temp_csv, temp_manifest, expected_asset_class="equities", expected_observation_date="2026-01-15")
        assert result.parse_status == "PASS"
        assert result.warnings
    finally:
        temp_csv.unlink(missing_ok=True)
        temp_manifest.unlink(missing_ok=True)


def test_no_env_vars_read_no_output_files_written() -> None:
    with patch("os.getenv") as getenv_mock:
        result = parse_local_ohlcv_fixture(EQUITIES_CSV, EQUITIES_MANIFEST, expected_asset_class="equities", expected_observation_date="2026-01-15")
    assert getenv_mock.call_count == 0
    assert result.rows


def test_no_requests_http_vendor_or_db_imports() -> None:
    source = Path("app/vendor_flat_files/local_ohlcv_parser.py").read_text(encoding="utf-8").lower()
    for marker in ["requests", "httpx", "vendor sdk", "database", "sqlalchemy", "writer", "session"]:
        assert marker not in source

