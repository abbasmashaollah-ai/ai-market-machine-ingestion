"""Build JSON-friendly price feature observations from close history."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.prices.price_feature_engine import (
    above_moving_average,
    calculate_atr_14d,
    calculate_drawdown_from_high,
    calculate_distance_from_moving_average,
    calculate_dollar_volume,
    calculate_high_low_range,
    calculate_moving_average,
    calculate_price_trend_state,
    calculate_realized_volatility,
    calculate_liquidity_score,
    calculate_relative_volume_20d,
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


def build_price_feature_observation(
    symbol,
    close_history,
    observation_date,
    timestamp=None,
    source="fixture_ohlcv",
    metadata=None,
):
    normalized_symbol = _normalize_symbol(symbol)
    rows = list(close_history or [])
    closes = [row.get("close") if isinstance(row, Mapping) else row for row in rows]
    closes = [value for value in closes if value is not None]
    latest_close = closes[-1] if closes else None
    has_ohlcv = any(isinstance(row, Mapping) and any(key in row for key in ("open", "high", "low", "volume")) for row in rows)

    returns = calculate_rolling_returns(closes, windows=(1, 5, 20, 60, 252))
    ma20 = calculate_moving_average(closes, 20)
    ma50 = calculate_moving_average(closes, 50)
    ma100 = calculate_moving_average(closes, 100)
    ma200 = calculate_moving_average(closes, 200)
    distance_20 = calculate_distance_from_moving_average(latest_close, ma20)
    distance_50 = calculate_distance_from_moving_average(latest_close, ma50)
    distance_100 = calculate_distance_from_moving_average(latest_close, ma100)
    distance_200 = calculate_distance_from_moving_average(latest_close, ma200)
    realized_vol_20d = calculate_realized_volatility(closes, 20)
    realized_vol_60d = calculate_realized_volatility(closes, 60)
    atr_14d = calculate_atr_14d(rows) if has_ohlcv else None
    average_dollar_volume_20d = None
    if has_ohlcv:
        dollar_volumes = [calculate_dollar_volume(row) for row in rows]
        dollar_volumes = [value for value in dollar_volumes if value is not None]
        if len(dollar_volumes) >= 20:
            average_dollar_volume_20d = sum(dollar_volumes[-20:]) / 20.0
    relative_volume_20d = calculate_relative_volume_20d(rows) if has_ohlcv else None
    liquidity_score = calculate_liquidity_score(rows) if has_ohlcv else None
    payload = {
        "symbol": normalized_symbol,
        "observation_date": _normalize_date(observation_date),
        "timestamp": _normalize_date(timestamp),
        "latest_close": latest_close,
        "return_1d": returns.get(1),
        "return_5d": returns.get(5),
        "return_20d": returns.get(20),
        "return_60d": returns.get(60),
        "return_252d": returns.get(252),
        "moving_average_20d": ma20,
        "moving_average_50d": ma50,
        "moving_average_100d": ma100,
        "moving_average_200d": ma200,
        "distance_from_ma_20d": distance_20,
        "distance_from_ma_50d": distance_50,
        "above_ma_20d": above_moving_average(latest_close, ma20),
        "above_ma_50d": above_moving_average(latest_close, ma50),
        "above_ma_100d": above_moving_average(latest_close, ma100),
        "above_ma_200d": above_moving_average(latest_close, ma200),
        "realized_vol_20d": realized_vol_20d,
        "realized_vol_60d": realized_vol_60d,
        "atr_14d": atr_14d,
        "dollar_volume": calculate_dollar_volume(rows[-1]) if rows and has_ohlcv else None,
        "average_dollar_volume_20d": average_dollar_volume_20d,
        "relative_volume_20d": relative_volume_20d,
        "liquidity_score": liquidity_score,
        "drawdown_from_20d_high": calculate_drawdown_from_high(closes, 20),
        "drawdown_from_60d_high": calculate_drawdown_from_high(closes, 60),
        "high_low_range_20d": calculate_high_low_range(closes, 20),
        "high_low_range_60d": calculate_high_low_range(closes, 60),
        "price_trend_state": calculate_price_trend_state(returns, distance_20, distance_50),
        "source": source,
        "dataset_version": "price_feature_v2",
        "source_attribution": source,
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
