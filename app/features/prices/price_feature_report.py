"""Compact dry-run report for price feature observations."""

from __future__ import annotations

from collections.abc import Mapping


def build_price_feature_report(observation):
    payload = dict(observation or {})
    return {
        "symbol": payload.get("symbol"),
        "observation_date": payload.get("observation_date"),
        "latest_close": payload.get("latest_close"),
        "price_trend_state": payload.get("price_trend_state"),
        "returns": {
            "return_1d": payload.get("return_1d"),
            "return_5d": payload.get("return_5d"),
            "return_20d": payload.get("return_20d"),
            "return_60d": payload.get("return_60d"),
        },
        "moving_average_context": {
            "moving_average_20d": payload.get("moving_average_20d"),
            "moving_average_50d": payload.get("moving_average_50d"),
            "distance_from_ma_20d": payload.get("distance_from_ma_20d"),
            "distance_from_ma_50d": payload.get("distance_from_ma_50d"),
        },
        "drawdown_context": {
            "drawdown_from_20d_high": payload.get("drawdown_from_20d_high"),
            "drawdown_from_60d_high": payload.get("drawdown_from_60d_high"),
        },
        "range_context": {
            "high_low_range_20d": payload.get("high_low_range_20d"),
            "high_low_range_60d": payload.get("high_low_range_60d"),
        },
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
