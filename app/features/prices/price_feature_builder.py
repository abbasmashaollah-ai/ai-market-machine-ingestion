"""Build JSON-friendly price feature observations from close history."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.prices.price_feature_engine import (
    calculate_drawdown_from_high,
    calculate_distance_from_moving_average,
    calculate_high_low_range,
    calculate_moving_average,
    calculate_price_trend_state,
    calculate_rolling_returns,
)


def _normalize_symbol(symbol: object) -> str:
    normalized = str(symbol).strip().upper()
    if not normalized:
        raise ValueError("symbol is required")
    return normalized


def _normalize_date(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _metadata_dict(metadata: Mapping[str, object] | None) -> dict[str, object]:
    result = dict(metadata or {})
    result.setdefault("lineage", {})
    result.setdefault("evidence", {})
    result.setdefault("quality_status", "PENDING")
    result.setdefault("certification_status", "PENDING")
    result.setdefault("freshness_status", "PENDING")
    return result


def build_price_feature_observation(symbol, close_history, observation_date, timestamp=None, source="fixture_ohlcv", metadata=None):
    normalized_symbol = _normalize_symbol(symbol)
    closes = list(close_history or [])
    if not closes:
        latest_close = None
    else:
        latest_close = closes[-1]

    returns = calculate_rolling_returns(closes)
    ma20 = calculate_moving_average(closes, 20)
    ma50 = calculate_moving_average(closes, 50)
    distance_20 = calculate_distance_from_moving_average(latest_close, ma20)
    distance_50 = calculate_distance_from_moving_average(latest_close, ma50)
    payload = {
        "symbol": normalized_symbol,
        "observation_date": _normalize_date(observation_date),
        "timestamp": _normalize_date(timestamp),
        "latest_close": latest_close,
        "return_1d": returns.get(1),
        "return_5d": returns.get(5),
        "return_20d": returns.get(20),
        "return_60d": returns.get(60),
        "moving_average_20d": ma20,
        "moving_average_50d": ma50,
        "distance_from_ma_20d": distance_20,
        "distance_from_ma_50d": distance_50,
        "drawdown_from_20d_high": calculate_drawdown_from_high(closes, 20),
        "drawdown_from_60d_high": calculate_drawdown_from_high(closes, 60),
        "high_low_range_20d": calculate_high_low_range(closes, 20),
        "high_low_range_60d": calculate_high_low_range(closes, 60),
        "price_trend_state": calculate_price_trend_state(returns, distance_20, distance_50),
        "source": source,
    }
    metadata_dict = _metadata_dict(metadata)
    payload.update(
        {
            "quality_status": metadata_dict["quality_status"],
            "certification_status": metadata_dict["certification_status"],
            "freshness_status": metadata_dict["freshness_status"],
            "lineage": metadata_dict["lineage"],
            "evidence": metadata_dict["evidence"],
        }
    )
    return payload
