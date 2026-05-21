from __future__ import annotations

from datetime import datetime

from app.models.normalized import NormalizedMacroObservation
from app.normalization.common import safe_number, safe_text


def fred_observation_to_normalized_macro(
    payload: dict[str, object],
    *,
    vendor: str = "fred",
    source: str = "fred_observations",
    normalization_version: str = "fred.v1",
) -> NormalizedMacroObservation:
    series_id = safe_text(payload.get("series_id")) or safe_text(payload.get("id"))
    if not series_id:
        raise ValueError("series_id is required")
    date_value = safe_text(payload.get("date"))
    if not date_value:
        raise ValueError("date is required")
    timestamp = datetime.fromisoformat(f"{date_value}T00:00:00")
    return NormalizedMacroObservation(
        symbol=series_id,
        symbol_id=series_id,
        timestamp=timestamp,
        market_date=timestamp.date(),
        timeframe="1d",
        adjusted=False,
        value=safe_number(payload.get("value")),
        vendor=vendor,
        source=source,
        normalization_version=normalization_version,
        quality_status="pending",
    )


def fred_series_metadata_to_dict(payload: dict[str, object]) -> dict[str, object]:
    return {
        "series_id": safe_text(payload.get("series_id")) or safe_text(payload.get("id")),
        "title": safe_text(payload.get("title")),
        "frequency": safe_text(payload.get("frequency")),
        "units": safe_text(payload.get("units")),
        "seasonal_adjustment": safe_text(payload.get("seasonal_adjustment")),
        "observation_start": safe_text(payload.get("observation_start")),
        "observation_end": safe_text(payload.get("observation_end")),
    }
