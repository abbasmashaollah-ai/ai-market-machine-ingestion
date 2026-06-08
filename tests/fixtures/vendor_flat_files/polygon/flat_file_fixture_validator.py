from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


EXPECTED_SCHEMA_VERSION = "vendor_flat_file_ohlcv.v1"
EXPECTED_DATASET_VERSION = "fixture.v1"
ALLOWED_ASSET_CLASSES = {"equities", "etfs"}
REQUIRED_COLUMNS = ("ticker", "date", "open", "high", "low", "close", "volume")
OPTIONAL_COLUMNS = {"vwap", "transactions", "adjusted"}


def _csv_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _has_forbidden_secret(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in ("secret", "token", "credential", "api_key", "raw_provider"))


def validate_manifest_and_csv(csv_path: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    if not csv_path.exists():
        errors.append("missing csv")
        return errors
    if not manifest_path.exists():
        errors.append("missing manifest")
        return errors

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _load_csv(csv_path)
    csv_hash = _csv_sha256(csv_path)

    if manifest.get("vendor") != "polygon":
        errors.append("invalid vendor")
    if manifest.get("asset_class") not in ALLOWED_ASSET_CLASSES:
        errors.append("invalid asset_class")
    if manifest.get("data_type") != "daily_ohlcv":
        errors.append("invalid data_type")
    if manifest.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append("invalid schema_version")
    if manifest.get("dataset_version") != EXPECTED_DATASET_VERSION:
        errors.append("invalid dataset_version")
    if manifest.get("source_file_sha256") != csv_hash:
        errors.append("source_file_sha256 mismatch")
    if int(manifest.get("row_count") or -1) != len(rows):
        errors.append("row_count mismatch")
    unique_tickers = {str(row.get("ticker") or "").strip().upper() for row in rows if row.get("ticker")}
    if int(manifest.get("symbols_count") or -1) != len(unique_tickers):
        errors.append("symbols_count mismatch")
    if manifest.get("compression") != "none":
        errors.append("invalid compression")
    if manifest.get("download_mode") != "fixture":
        errors.append("invalid download_mode")
    if manifest.get("validation_status") != "PASS":
        errors.append("invalid validation_status")
    if manifest.get("validation_errors") not in ([], None):
        errors.append("validation_errors must be empty")
    if manifest.get("certification_status") != "FIXTURE_ONLY":
        errors.append("invalid certification_status")
    note = str(manifest.get("note") or "").lower()
    if "synthetic fixture only" not in note or "not vendor data" not in note or "not production evidence" not in note:
        errors.append("invalid note")
    if _has_forbidden_secret(json.dumps(manifest, sort_keys=True)) or _has_forbidden_secret(csv_path.read_text(encoding="utf-8")):
        errors.append("forbidden secret material")

    header = rows[0].keys() if rows else []
    for column in REQUIRED_COLUMNS:
        if column not in header:
            errors.append(f"missing required column {column}")

    seen_pairs: set[tuple[str, str]] = set()
    for row in rows:
        ticker = str(row.get("ticker") or "").strip().upper()
        date = str(row.get("date") or "").strip()
        if not ticker:
            errors.append("missing ticker")
        if not date:
            errors.append("missing date")
        try:
            open_value = float(row.get("open"))
            high_value = float(row.get("high"))
            low_value = float(row.get("low"))
            close_value = float(row.get("close"))
        except (TypeError, ValueError):
            errors.append("invalid ohlc values")
            continue
        if not (low_value <= open_value <= high_value and low_value <= close_value <= high_value):
            errors.append("invalid ohlc values")
        try:
            volume = int(float(row.get("volume")))
        except (TypeError, ValueError):
            errors.append("invalid volume")
            continue
        if volume < 0:
            errors.append("negative volume")
        pair = (ticker, date)
        if pair in seen_pairs:
            errors.append("duplicate ticker/date rows")
        seen_pairs.add(pair)
        for optional in OPTIONAL_COLUMNS:
            if optional not in header:
                continue
    return errors

