from __future__ import annotations

from app.models.normalized import NormalizedMacroObservation
from app.normalization.common import safe_bool, safe_datetime, safe_number, safe_text


def normalize_macro_observation(
    payload: dict[str, object],
    *,
    symbol_key: str = "symbol",
    symbol_id_key: str = "symbol_id",
    timestamp_key: str = "timestamp",
    market_date_key: str = "market_date",
    timeframe_key: str = "timeframe",
    adjusted_key: str = "adjusted",
    value_key: str = "value",
    vendor_key: str = "vendor",
    source_key: str = "source",
    ingestion_run_id_key: str = "ingestion_run_id",
    normalization_version_key: str = "normalization_version",
    quality_status_key: str = "quality_status",
) -> NormalizedMacroObservation:
    timestamp = safe_datetime(payload.get(timestamp_key))
    if timestamp is None:
        raise ValueError("timestamp is required")

    return NormalizedMacroObservation(
        symbol=safe_text(payload.get(symbol_key)),
        symbol_id=safe_text(payload.get(symbol_id_key)),
        timestamp=timestamp,
        market_date=None if payload.get(market_date_key) is None else payload.get(market_date_key),  # type: ignore[arg-type]
        timeframe=safe_text(payload.get(timeframe_key), default="1d") or "1d",
        adjusted=safe_bool(payload.get(adjusted_key), default=False) or False,
        value=safe_number(payload.get(value_key)),
        vendor=safe_text(payload.get(vendor_key)),
        source=safe_text(payload.get(source_key)),
        ingestion_run_id=safe_text(payload.get(ingestion_run_id_key)),
        normalization_version=safe_text(payload.get(normalization_version_key)),
        quality_status=safe_text(payload.get(quality_status_key)),
    )
