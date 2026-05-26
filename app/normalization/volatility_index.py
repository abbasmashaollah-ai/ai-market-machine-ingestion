from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class NormalizedVolatilityIndexRecord:
    symbol: str | None
    observation_date: date | None
    value: float | None
    source: str | None
    vendor_symbol: str | None
    unit: str | None
    notes: str | None = None


STARTER_VOLATILITY_INDEX_SYMBOLS: tuple[str, ...] = ("VIX", "VVIX", "VXN", "RVX")


def normalize_volatility_index_record(payload: dict[str, object]) -> NormalizedVolatilityIndexRecord:
    observation_date_value = payload.get("observation_date")
    if isinstance(observation_date_value, date):
        observation_date = observation_date_value
    elif isinstance(observation_date_value, str) and observation_date_value:
        observation_date = date.fromisoformat(observation_date_value)
    else:
        observation_date = None

    value = payload.get("value")
    normalized_value = float(value) if isinstance(value, (int, float)) else None

    return NormalizedVolatilityIndexRecord(
        symbol=payload.get("symbol") if isinstance(payload.get("symbol"), str) else None,
        observation_date=observation_date,
        value=normalized_value,
        source=payload.get("source") if isinstance(payload.get("source"), str) else None,
        vendor_symbol=payload.get("vendor_symbol") if isinstance(payload.get("vendor_symbol"), str) else None,
        unit=payload.get("unit") if isinstance(payload.get("unit"), str) else None,
        notes=payload.get("notes") if isinstance(payload.get("notes"), str) else None,
    )


def validate_volatility_index_record(record: NormalizedVolatilityIndexRecord) -> list[str]:
    errors: list[str] = []
    if not record.symbol:
        errors.append("symbol is required")
    if record.observation_date is None:
        errors.append("observation_date is required")
    if record.value is None:
        errors.append("value is required")
    if not record.source:
        errors.append("source is required")
    if not record.vendor_symbol:
        errors.append("vendor_symbol is required")
    if not record.unit:
        errors.append("unit is required")
    return errors
