from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


EXPECTED_VENDOR = "polygon"
EXPECTED_SCHEMA_VERSION = "vendor_flat_file_ohlcv.v1"
EXPECTED_DATASET_VERSION = "fixture.v1"
REQUIRED_COLUMNS = ("ticker", "date", "open", "high", "low", "close", "volume")
OPTIONAL_COLUMNS = ("vwap", "transactions", "adjusted")


@dataclass(frozen=True, slots=True)
class LocalFlatFileParseError:
    code: str
    message: str
    row_number: int | None = None
    field_name: str | None = None


@dataclass(frozen=True, slots=True)
class LocalFlatFileParseResult:
    parse_status: str
    rows: tuple[dict[str, object], ...] = field(default_factory=tuple)
    row_count: int = 0
    symbols: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[LocalFlatFileParseError, ...] = field(default_factory=tuple)
    manifest: dict[str, Any] | None = None
    source_file_sha256: str | None = None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _normalize_optional_number(value: object, *, field_name: str, errors: list[LocalFlatFileParseError], row_number: int, allow_missing: bool = True) -> float | int | None:
    if value in (None, ""):
        if allow_missing:
            return None
        errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message=f"{field_name} is required", row_number=row_number, field_name=field_name))
        return None
    try:
        if field_name == "transactions":
            return int(float(value))
        return float(value)
    except (TypeError, ValueError):
        errors.append(LocalFlatFileParseError(code="INVALID_OHLC", message=f"{field_name} must be numeric", row_number=row_number, field_name=field_name))
        return None


def _validate_manifest(manifest: dict[str, Any], expected_asset_class: str) -> list[LocalFlatFileParseError]:
    errors: list[LocalFlatFileParseError] = []
    if manifest.get("vendor") != EXPECTED_VENDOR:
        errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="vendor must be polygon", field_name="vendor"))
    if manifest.get("asset_class") != expected_asset_class:
        errors.append(LocalFlatFileParseError(code="ASSET_CLASS_MISMATCH", message="asset_class mismatch", field_name="asset_class"))
    if manifest.get("data_type") != "daily_ohlcv":
        errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="data_type must be daily_ohlcv", field_name="data_type"))
    if manifest.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append(LocalFlatFileParseError(code="SCHEMA_VERSION_MISMATCH", message="schema_version mismatch", field_name="schema_version"))
    if manifest.get("dataset_version") != EXPECTED_DATASET_VERSION:
        errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="dataset_version mismatch", field_name="dataset_version"))
    if manifest.get("validation_status") != "PASS":
        errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="validation_status must be PASS", field_name="validation_status"))
    if manifest.get("certification_status") != "FIXTURE_ONLY":
        errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="certification_status must be FIXTURE_ONLY", field_name="certification_status"))
    return errors


def parse_local_ohlcv_fixture(
    csv_path: str | Path,
    manifest_path: str | Path,
    *,
    expected_asset_class: str,
    expected_observation_date: str,
) -> LocalFlatFileParseResult:
    csv_file = Path(csv_path)
    manifest_file = Path(manifest_path)

    errors: list[LocalFlatFileParseError] = []
    warnings: list[str] = []

    if not manifest_file.exists():
        return LocalFlatFileParseResult(
            parse_status="FAIL",
            errors=(LocalFlatFileParseError(code="MANIFEST_MISSING", message="manifest file missing"),),
        )
    if not csv_file.exists():
        return LocalFlatFileParseResult(
            parse_status="FAIL",
            errors=(LocalFlatFileParseError(code="CSV_MISSING", message="csv file missing"),),
            manifest=_load_manifest(manifest_file),
        )

    manifest = _load_manifest(manifest_file)
    csv_hash = _sha256(csv_file)
    if manifest.get("source_file_sha256") != csv_hash:
        return LocalFlatFileParseResult(
            parse_status="FAIL",
            errors=(LocalFlatFileParseError(code="CHECKSUM_MISMATCH", message="source_file_sha256 mismatch"),),
            manifest=manifest,
            source_file_sha256=csv_hash,
        )

    errors.extend(_validate_manifest(manifest, expected_asset_class))

    rows = _load_rows(csv_file)
    if not rows:
        errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="csv contains no rows"))

    header = list(rows[0].keys()) if rows else []
    for column in REQUIRED_COLUMNS:
        if column not in header:
            errors.append(LocalFlatFileParseError(code="REQUIRED_COLUMN_MISSING", message=f"missing required column {column}", field_name=column))

    parsed_rows: list[dict[str, object]] = []
    seen_pairs: set[tuple[str, str]] = set()

    for index, row in enumerate(rows, start=2):
        ticker = str(row.get("ticker") or "").strip()
        observation_date = str(row.get("date") or "").strip()
        if not ticker:
            errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="missing ticker", row_number=index, field_name="ticker"))
            continue
        if not observation_date:
            errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="missing date", row_number=index, field_name="date"))
            continue
        if observation_date != expected_observation_date:
            errors.append(LocalFlatFileParseError(code="REQUIRED_VALUE_MISSING", message="date mismatch", row_number=index, field_name="date"))
            continue

        try:
            open_value = float(row.get("open"))
            high_value = float(row.get("high"))
            low_value = float(row.get("low"))
            close_value = float(row.get("close"))
        except (TypeError, ValueError):
            errors.append(LocalFlatFileParseError(code="INVALID_OHLC", message="ohlc fields must be numeric", row_number=index))
            continue

        if open_value <= 0 or high_value <= 0 or low_value <= 0 or close_value <= 0:
            errors.append(LocalFlatFileParseError(code="INVALID_OHLC", message="ohlc values must be greater than zero", row_number=index))
            continue
        if high_value < low_value:
            errors.append(LocalFlatFileParseError(code="INVALID_OHLC", message="high cannot be less than low", row_number=index))
            continue

        try:
            volume = int(float(row.get("volume")))
        except (TypeError, ValueError):
            errors.append(LocalFlatFileParseError(code="INVALID_OHLC", message="volume must be numeric", row_number=index, field_name="volume"))
            continue
        if volume < 0:
            errors.append(LocalFlatFileParseError(code="NEGATIVE_VOLUME", message="volume cannot be negative", row_number=index, field_name="volume"))
            continue

        symbol = ticker.upper()
        pair = (symbol, observation_date)
        if pair in seen_pairs:
            errors.append(LocalFlatFileParseError(code="DUPLICATE_SYMBOL_DATE", message="duplicate symbol/date row", row_number=index))
            continue
        seen_pairs.add(pair)

        vwap_value = row.get("vwap")
        if vwap_value in (None, ""):
            warnings.append(f"{symbol}:{observation_date}: missing optional vwap")
        transactions_value = row.get("transactions")
        if transactions_value in (None, ""):
            warnings.append(f"{symbol}:{observation_date}: missing optional transactions")

        normalized = {
            "symbol": symbol,
            "observation_date": observation_date,
            "open": open_value,
            "high": high_value,
            "low": low_value,
            "close": close_value,
            "volume": volume,
            "vwap": _normalize_optional_number(vwap_value, field_name="vwap", errors=errors, row_number=index),
            "transactions": _normalize_optional_number(transactions_value, field_name="transactions", errors=errors, row_number=index),
            "adjusted": str(row.get("adjusted") or "").strip().lower() in {"true", "1", "yes", "y"},
            "vendor": EXPECTED_VENDOR,
            "asset_class": expected_asset_class,
            "schema_version": EXPECTED_SCHEMA_VERSION,
            "dataset_version": EXPECTED_DATASET_VERSION,
            "source_file_sha256": csv_hash,
            "lineage_id": manifest.get("lineage_id"),
            "manifest_path": str(manifest_file),
            "source_file_name": manifest.get("source_file_name"),
            "validation_status": manifest.get("validation_status"),
            "certification_status": manifest.get("certification_status"),
        }
        parsed_rows.append(normalized)

    parse_status = "PASS" if not errors else "FAIL"
    return LocalFlatFileParseResult(
        parse_status=parse_status,
        rows=tuple(parsed_rows),
        row_count=len(parsed_rows),
        symbols=tuple(sorted({row["symbol"] for row in parsed_rows})),
        warnings=tuple(warnings),
        errors=tuple(errors),
        manifest=manifest,
        source_file_sha256=csv_hash,
    )
