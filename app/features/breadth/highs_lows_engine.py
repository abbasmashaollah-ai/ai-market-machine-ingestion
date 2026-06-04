"""Highs/lows breadth evidence calculations for dry-run use only."""

from __future__ import annotations

from collections.abc import Mapping


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def calculate_new_highs_lows(close_history_by_symbol, window=252):
    window_value = int(window)
    new_highs = 0
    new_lows = 0
    for history in close_history_by_symbol.values():
        closes = [_as_float(row["close"] if isinstance(row, Mapping) else row) for row in history]
        closes = [value for value in closes if value is not None]
        if len(closes) < window_value:
            continue
        subset = closes[-window_value:]
        latest_close = subset[-1]
        if latest_close >= max(subset):
            new_highs += 1
        if latest_close <= min(subset):
            new_lows += 1
    return new_highs, new_lows
