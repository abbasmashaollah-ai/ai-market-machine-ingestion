from __future__ import annotations

from datetime import datetime, timezone

from app.models.normalized import NormalizedOHLCVRecord
from app.normalization.common import safe_bool, safe_number, safe_text


def normalize_fmp_ohlcv_record(
    payload: dict[str, object],
    *,
    symbol: str | None = None,
    vendor: str = "fmp",
    source: str = "fmp_historical_price_full",
    normalization_version: str = "fmp.ohlcv.v1",
) -> NormalizedOHLCVRecord:
    raw_symbol = safe_text(symbol) or safe_text(payload.get("symbol")) or safe_text(payload.get("ticker"))
    date_value = safe_text(payload.get("date"))
    if not raw_symbol:
        raise ValueError("symbol is required")
    if not date_value:
        raise ValueError("date is required")
    timestamp = datetime.fromisoformat(f"{date_value}T00:00:00").replace(tzinfo=timezone.utc)
    adjusted = safe_bool(payload.get("adjusted"), default=None)
    if adjusted is None:
        adjusted = payload.get("adjClose") is not None
    return NormalizedOHLCVRecord(
        symbol=raw_symbol,
        symbol_id=raw_symbol,
        timestamp=timestamp,
        market_date=timestamp.date(),
        timeframe="1d",
        adjusted=bool(adjusted),
        open=safe_number(payload.get("open")),
        high=safe_number(payload.get("high")),
        low=safe_number(payload.get("low")),
        close=safe_number(payload.get("close")),
        volume=safe_number(payload.get("volume")),
        vendor=vendor,
        source=source,
        normalization_version=normalization_version,
        quality_status="pending",
    )


def normalize_fmp_ohlcv_records(
    payloads: list[dict[str, object]],
    *,
    symbol: str | None = None,
    vendor: str = "fmp",
    source: str = "fmp_historical_price_full",
    normalization_version: str = "fmp.ohlcv.v1",
) -> tuple[NormalizedOHLCVRecord, ...]:
    return tuple(
        normalize_fmp_ohlcv_record(
            payload,
            symbol=symbol,
            vendor=vendor,
            source=source,
            normalization_version=normalization_version,
        )
        for payload in payloads
    )
