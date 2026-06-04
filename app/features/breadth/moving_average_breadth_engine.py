"""Moving-average breadth evidence calculations for dry-run use only."""

from __future__ import annotations

from collections.abc import Mapping


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def calculate_percent_above_moving_average(close_history_by_symbol, window):
    window_value = int(window)
    if window_value <= 0:
        return None
    total = 0
    above = 0
    for history in close_history_by_symbol.values():
        closes = [_as_float(row["close"] if isinstance(row, Mapping) else row) for row in history]
        closes = [value for value in closes if value is not None]
        if len(closes) < window_value:
            continue
        subset = closes[-window_value:]
        moving_average = sum(subset) / float(window_value)
        latest_close = subset[-1]
        total += 1
        if latest_close > moving_average:
            above += 1
    if total == 0:
        return None
    return above / total


def calculate_percent_above_100d_ma(close_history_by_symbol):
    return calculate_percent_above_moving_average(close_history_by_symbol, 100)
