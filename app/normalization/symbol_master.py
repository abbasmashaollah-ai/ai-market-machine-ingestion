from __future__ import annotations

from hashlib import sha256
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class NormalizedSymbolMasterRecord:
    symbol: str | None
    active: bool | None
    source: str | None = None
    vendor: str | None = None
    source_vendor: str | None = None
    source_dataset: str | None = None
    source_sha256: str | None = None
    source_file_name: str | None = None
    source_file_path: str | None = None
    producer_run_id: str | None = None
    vendor_symbol: str | None = None
    asset_type: str | None = None
    exchange: str | None = None
    name: str | None = None
    currency: str | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    normalization_version: str | None = None
    quality_status: str | None = None


@dataclass(frozen=True)
class SymbolMasterSourceRecord:
    symbol: str | None
    active: bool | None
    vendor: str | None = None
    source_vendor: str | None = None
    source_dataset: str | None = None
    source_sha256: str | None = None
    source_file_name: str | None = None
    source_file_path: str | None = None
    producer_run_id: str | None = None
    vendor_symbol: str | None = None
    asset_type: str | None = None
    exchange: str | None = None
    name: str | None = None
    currency: str | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def normalize_symbol_record(source: SymbolMasterSourceRecord) -> NormalizedSymbolMasterRecord:
    return NormalizedSymbolMasterRecord(
        symbol=_normalize_text(source.symbol),
        source=_normalize_text(source.symbol),
        vendor=_normalize_text(source.vendor),
        source_vendor=_normalize_text(source.source_vendor or source.vendor),
        source_dataset=_normalize_text(source.source_dataset),
        source_sha256=_normalize_text(source.source_sha256),
        source_file_name=_normalize_text(source.source_file_name),
        source_file_path=_normalize_text(source.source_file_path),
        producer_run_id=_normalize_text(source.producer_run_id),
        vendor_symbol=_normalize_text(source.vendor_symbol),
        name=_normalize_text(source.name),
        currency=_normalize_text(source.currency),
        first_seen_at=_normalize_datetime(source.first_seen_at),
        last_seen_at=_normalize_datetime(source.last_seen_at),
        normalization_version="symbol_master.v1",
        quality_status="pass" if source.active is True else "warn" if source.active is False else None,
        asset_type=_normalize_text(source.asset_type),
        exchange=_normalize_text(source.exchange),
        active=source.active,
    )


def validate_source_record(source: SymbolMasterSourceRecord) -> list[str]:
    errors: list[str] = []
    if not source.symbol or not source.symbol.strip():
        errors.append("symbol is required")
    if source.active is None:
        errors.append("active is required")
    if source.vendor is not None and not source.vendor.strip():
        errors.append("vendor cannot be empty")
    if source.source_vendor is not None and not source.source_vendor.strip():
        errors.append("source_vendor cannot be empty")
    if source.source_dataset is not None and not source.source_dataset.strip():
        errors.append("source_dataset cannot be empty")
    if source.source_sha256 is not None and not source.source_sha256.strip():
        errors.append("source_sha256 cannot be empty")
    if source.source_file_name is not None and not source.source_file_name.strip():
        errors.append("source_file_name cannot be empty")
    if source.source_file_path is not None and not source.source_file_path.strip():
        errors.append("source_file_path cannot be empty")
    if source.producer_run_id is not None and not source.producer_run_id.strip():
        errors.append("producer_run_id cannot be empty")
    if source.vendor_symbol is not None and not source.vendor_symbol.strip():
        errors.append("vendor_symbol cannot be empty")
    if source.vendor_symbol and not source.vendor:
        errors.append("vendor/vendor_symbol inconsistent")
    if source.asset_type is not None and not source.asset_type.strip():
        errors.append("asset_type cannot be empty")
    if source.exchange is not None and not source.exchange.strip():
        errors.append("exchange cannot be empty")
    return errors


def validate_symbol_record(record: NormalizedSymbolMasterRecord) -> list[str]:
    errors: list[str] = []
    if not record.symbol:
        errors.append("symbol is required")
    if record.active is None:
        errors.append("active is required")
    if record.vendor is not None and not record.vendor.strip():
        errors.append("vendor cannot be empty")
    if record.source_vendor is not None and not record.source_vendor.strip():
        errors.append("source_vendor cannot be empty")
    if record.source_dataset is not None and not record.source_dataset.strip():
        errors.append("source_dataset cannot be empty")
    if record.source_sha256 is not None and not record.source_sha256.strip():
        errors.append("source_sha256 cannot be empty")
    if record.source_file_name is not None and not record.source_file_name.strip():
        errors.append("source_file_name cannot be empty")
    if record.source_file_path is not None and not record.source_file_path.strip():
        errors.append("source_file_path cannot be empty")
    if record.producer_run_id is not None and not record.producer_run_id.strip():
        errors.append("producer_run_id cannot be empty")
    if record.vendor_symbol is not None and not record.vendor_symbol.strip():
        errors.append("vendor_symbol cannot be empty")
    if record.vendor_symbol and not record.vendor:
        errors.append("vendor/vendor_symbol inconsistent")
    if record.asset_type is not None and not record.asset_type.strip():
        errors.append("asset_type cannot be empty")
    if record.exchange is not None and not record.exchange.strip():
        errors.append("exchange cannot be empty")
    return errors


def build_symbol_identity_idempotency_key(
    source_vendor: str | None,
    source_dataset: str | None,
    source_sha256: str | None,
    asset_type: str | None,
    symbol: str | None,
) -> str | None:
    components = [source_vendor, source_dataset, source_sha256, asset_type, symbol]
    if any(component is None or not str(component).strip() for component in components):
        return None
    joined = "|".join(str(component).strip() for component in components)
    return sha256(joined.encode("utf-8")).hexdigest()
