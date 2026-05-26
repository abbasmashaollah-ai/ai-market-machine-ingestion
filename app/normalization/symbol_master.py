from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.models.normalized import NormalizedSymbolRecord


@dataclass(frozen=True)
class SymbolMasterSourceRecord:
    symbol: str | None
    active: bool | None
    vendor: str | None = None
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


def normalize_symbol_record(source: SymbolMasterSourceRecord) -> NormalizedSymbolRecord:
    return NormalizedSymbolRecord(
        symbol=_normalize_text(source.symbol),
        symbol_id=None,
        vendor=_normalize_text(source.vendor),
        source=_normalize_text(source.vendor_symbol) or _normalize_text(source.vendor),
        ingestion_run_id=None,
        normalization_version="symbol_master.v1",
        quality_status="pass" if source.active is True else "warn" if source.active is False else None,
        asset_class=_normalize_text(source.asset_type),
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
    if source.vendor_symbol is not None and not source.vendor_symbol.strip():
        errors.append("vendor_symbol cannot be empty")
    if source.vendor_symbol and not source.vendor:
        errors.append("vendor/vendor_symbol inconsistent")
    if source.asset_type is not None and not source.asset_type.strip():
        errors.append("asset_type cannot be empty")
    if source.exchange is not None and not source.exchange.strip():
        errors.append("exchange cannot be empty")
    return errors


def validate_symbol_record(record: NormalizedSymbolRecord) -> list[str]:
    errors: list[str] = []
    if not record.symbol:
        errors.append("symbol is required")
    if record.active is None:
        errors.append("active is required")
    if record.vendor is not None and not record.vendor.strip():
        errors.append("vendor cannot be empty")
    if record.source is not None and not record.source.strip():
        errors.append("source cannot be empty")
    if record.asset_class is not None and not record.asset_class.strip():
        errors.append("asset_type cannot be empty")
    if record.exchange is not None and not record.exchange.strip():
        errors.append("exchange cannot be empty")
    return errors
