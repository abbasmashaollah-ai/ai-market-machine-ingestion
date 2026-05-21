from __future__ import annotations

from datetime import datetime, timezone

from app.models.normalized import NormalizedOHLCVRecord, NormalizedSymbolRecord
from app.normalization.common import safe_bool, safe_number, safe_text


def polygon_aggregate_to_normalized_ohlcv(
    payload: dict[str, object],
    *,
    symbol_id: str | None = None,
    vendor: str = "polygon",
    source: str = "polygon_aggregates",
    normalization_version: str = "polygon.v1",
) -> NormalizedOHLCVRecord:
    timestamp = payload.get("t")
    if timestamp is None:
        raise ValueError("t is required")
    dt = datetime.fromtimestamp(float(timestamp) / 1000.0, tz=timezone.utc)
    return NormalizedOHLCVRecord(
        symbol=safe_text(payload.get("ticker")),
        symbol_id=symbol_id,
        timestamp=dt,
        timeframe="1d",
        adjusted=safe_bool(payload.get("adjusted"), default=True) or True,
        open=safe_number(payload.get("o")),
        high=safe_number(payload.get("h")),
        low=safe_number(payload.get("l")),
        close=safe_number(payload.get("c")),
        volume=safe_number(payload.get("v")),
        vendor=vendor,
        source=source,
        normalization_version=normalization_version,
    )


def polygon_ticker_to_normalized_symbol(
    payload: dict[str, object],
    *,
    vendor: str = "polygon",
    source: str = "polygon_reference",
    normalization_version: str = "polygon.v1",
) -> NormalizedSymbolRecord:
    return NormalizedSymbolRecord(
        symbol=safe_text(payload.get("ticker")),
        symbol_id=safe_text(payload.get("ticker")),
        vendor=vendor,
        source=source,
        normalization_version=normalization_version,
        asset_class=safe_text(payload.get("type")),
        exchange=safe_text(payload.get("primary_exchange")),
        active=safe_bool(payload.get("active")),
    )
