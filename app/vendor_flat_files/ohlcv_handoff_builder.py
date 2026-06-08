from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.vendor_flat_files.local_ohlcv_parser import LocalFlatFileParseError, LocalFlatFileParseResult


CANONICAL_SCHEMA_VERSION = "canonical_ohlcv.v1"
EVIDENCE_TYPE = "vendor_flat_file_ohlcv"


@dataclass(frozen=True, slots=True)
class LocalOhlcvHandoffError:
    code: str
    message: str
    row_number: int | None = None
    field_name: str | None = None


@dataclass(frozen=True, slots=True)
class LocalOhlcvHandoffResult:
    handoff_status: str
    records: tuple[dict[str, object], ...] = field(default_factory=tuple)
    record_count: int = 0
    symbols: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[LocalOhlcvHandoffError, ...] = field(default_factory=tuple)
    idempotency_key_prefixes: tuple[str, ...] = field(default_factory=tuple)
    safe_summary: dict[str, object] | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _prefix(value: str, length: int = 12) -> str:
    return value[:length]


def _convert_parser_error(error: LocalFlatFileParseError) -> LocalOhlcvHandoffError:
    return LocalOhlcvHandoffError(
        code=error.code,
        message=error.message,
        row_number=error.row_number,
        field_name=error.field_name,
    )


def _idempotency_key(
    *,
    vendor: str,
    asset_class: str,
    symbol: str,
    observation_date: str,
    dataset_version: str,
    source_file_sha256: str,
) -> str:
    seed = "|".join([vendor, asset_class, symbol, observation_date, dataset_version, source_file_sha256])
    return _hash_text(seed)


def build_ohlcv_handoff(
    parsed: LocalFlatFileParseResult,
    *,
    source_schema_version: str | None = None,
) -> LocalOhlcvHandoffResult:
    errors: list[LocalOhlcvHandoffError] = [_convert_parser_error(error) for error in parsed.errors]
    warnings: list[str] = list(parsed.warnings)
    records: list[dict[str, object]] = []
    prefixes: list[str] = []

    manifest = parsed.manifest or {}
    certification_status = str(manifest.get("certification_status") or "")
    validation_status = str(manifest.get("validation_status") or "")
    dataset_version = str(manifest.get("dataset_version") or "")
    asset_class = str(manifest.get("asset_class") or "")
    source_file_name = str(manifest.get("source_file_name") or "")
    lineage_id = str(manifest.get("lineage_id") or "")
    source_file_sha256 = str(parsed.source_file_sha256 or manifest.get("source_file_sha256") or "")
    vendor = str(manifest.get("vendor") or "polygon")

    if not source_file_sha256:
        errors.append(LocalOhlcvHandoffError(code="HANDOFF_BLOCKED_CHECKSUM_MISSING", message="source_file_sha256 missing"))

    if not validation_status:
        errors.append(LocalOhlcvHandoffError(code="HANDOFF_BLOCKED_VALIDATION_FAILED", message="validation_status missing"))

    if not certification_status:
        errors.append(LocalOhlcvHandoffError(code="HANDOFF_BLOCKED_CERTIFICATION_MISSING", message="certification_status missing"))

    if certification_status == "FIXTURE_ONLY":
        errors.append(LocalOhlcvHandoffError(code="HANDOFF_BLOCKED_FIXTURE_ONLY", message="fixture-only parser output is not production evidence"))

    if validation_status != "PASS" or any(err.code.startswith("REQUIRED_") or err.code in {"INVALID_OHLC", "NEGATIVE_VOLUME", "DUPLICATE_SYMBOL_DATE", "SCHEMA_VERSION_MISMATCH", "ASSET_CLASS_MISMATCH", "CHECKSUM_MISMATCH"} for err in errors):
        if not any(err.code == "HANDOFF_BLOCKED_VALIDATION_FAILED" for err in errors):
            errors.append(LocalOhlcvHandoffError(code="HANDOFF_BLOCKED_VALIDATION_FAILED", message="validation failure blocks warehouse handoff"))

    if parsed.parse_status != "PASS":
        if not any(err.code == "HANDOFF_BLOCKED_VALIDATION_FAILED" for err in errors):
            errors.append(LocalOhlcvHandoffError(code="HANDOFF_BLOCKED_VALIDATION_FAILED", message="parser failure blocks warehouse handoff"))

    for row in parsed.rows:
        symbol = str(row.get("symbol") or "").upper()
        observation_date = str(row.get("observation_date") or "")
        source_hash = str(row.get("source_file_sha256") or source_file_sha256)
        key = _idempotency_key(
            vendor=str(row.get("vendor") or vendor),
            asset_class=str(row.get("asset_class") or asset_class),
            symbol=symbol,
            observation_date=observation_date,
            dataset_version=str(row.get("dataset_version") or dataset_version),
            source_file_sha256=source_hash,
        )
        prefixes.append(_prefix(key))
        record = {
            "symbol": symbol,
            "observation_date": observation_date,
            "open": row.get("open"),
            "high": row.get("high"),
            "low": row.get("low"),
            "close": row.get("close"),
            "volume": row.get("volume"),
            "vwap": row.get("vwap"),
            "transactions": row.get("transactions"),
            "adjusted": row.get("adjusted"),
            "vendor": str(row.get("vendor") or vendor),
            "asset_class": str(row.get("asset_class") or asset_class),
            "source_schema_version": source_schema_version or str(row.get("schema_version") or ""),
            "canonical_schema_version": CANONICAL_SCHEMA_VERSION,
            "dataset_version": str(row.get("dataset_version") or dataset_version),
            "source_file_sha256": source_hash,
            "lineage_id": str(row.get("lineage_id") or lineage_id),
            "manifest_path": str(row.get("manifest_path") or ""),
            "source_file_name": str(row.get("source_file_name") or source_file_name),
            "validation_status": str(row.get("validation_status") or validation_status),
            "certification_status": str(row.get("certification_status") or certification_status),
            "evidence_type": EVIDENCE_TYPE,
            "created_at": _now_iso(),
            "idempotency_key": key,
            "idempotency_key_prefix": _prefix(key),
        }
        records.append(record)

    handoff_status = "PASS"
    if any(err.code == "HANDOFF_BLOCKED_FIXTURE_ONLY" for err in errors):
        handoff_status = "BLOCKED"
    elif any(err.code.startswith("HANDOFF_BLOCKED_") for err in errors):
        handoff_status = "BLOCKED"
    elif errors:
        handoff_status = "FAIL"

    if certification_status == "FIXTURE_ONLY":
        handoff_status = "BLOCKED"

    safe_summary = {
        "handoff_status": handoff_status,
        "record_count": len(records),
        "symbols": tuple(sorted({str(record["symbol"]) for record in records})),
        "idempotency_key_prefixes": tuple(prefixes),
        "not_production_evidence": True,
        "manifest_checksum_lineage_refs_preserved": True,
    }

    return LocalOhlcvHandoffResult(
        handoff_status=handoff_status,
        records=tuple(records),
        record_count=len(records),
        symbols=tuple(sorted({str(record["symbol"]) for record in records})),
        warnings=tuple(warnings),
        errors=tuple(errors),
        idempotency_key_prefixes=tuple(prefixes),
        safe_summary=safe_summary,
    )
