"""Pure price evidence calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Sequence


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def calculate_price_return(start_close, end_close):
    start = _as_float(start_close)
    end = _as_float(end_close)
    if start is None or end is None or start == 0:
        return None
    return (end - start) / start


def calculate_rolling_returns(close_history, windows=(1, 5, 20, 60)):
    closes = [_as_float(value) for value in close_history]
    closes = [value for value in closes if value is not None]
    result: dict[int, float | None] = {}
    latest_index = len(closes) - 1
    if latest_index < 0:
        return {int(window): None for window in windows}
    for window in windows:
        window_value = int(window)
        start_index = latest_index - window_value
        if start_index < 0:
            result[window_value] = None
            continue
        result[window_value] = calculate_price_return(closes[start_index], closes[latest_index])
    return result


def calculate_moving_average(close_history, window):
    closes = [_as_float(value) for value in close_history]
    closes = [value for value in closes if value is not None]
    window_value = int(window)
    if window_value <= 0 or len(closes) < window_value:
        return None
    subset = closes[-window_value:]
    return sum(subset) / float(window_value)


def calculate_distance_from_moving_average(latest_close, moving_average):
    latest = _as_float(latest_close)
    average = _as_float(moving_average)
    if latest is None or average is None or average == 0:
        return None
    return (latest - average) / average


def calculate_high_low_range(close_history, window):
    closes = [_as_float(value) for value in close_history]
    closes = [value for value in closes if value is not None]
    window_value = int(window)
    if window_value <= 0 or len(closes) < window_value:
        return None
    subset = closes[-window_value:]
    low = min(subset)
    high = max(subset)
    if low == 0:
        return None
    return (high - low) / low


def calculate_drawdown_from_high(close_history, window):
    closes = [_as_float(value) for value in close_history]
    closes = [value for value in closes if value is not None]
    window_value = int(window)
    if window_value <= 0 or len(closes) < window_value:
        return None
    subset = closes[-window_value:]
    high = max(subset)
    latest = subset[-1]
    if high == 0:
        return None
    return (latest - high) / high


def calculate_price_trend_state(returns_by_window, distance_from_ma_20=None, distance_from_ma_50=None):
    if not returns_by_window:
        return "INSUFFICIENT_DATA"

    r1 = _as_float(returns_by_window.get(1) or returns_by_window.get("1d"))
    r5 = _as_float(returns_by_window.get(5) or returns_by_window.get("5d"))
    r20 = _as_float(returns_by_window.get(20) or returns_by_window.get("20d"))
    r60 = _as_float(returns_by_window.get(60) or returns_by_window.get("60d"))
    ma20 = _as_float(distance_from_ma_20)
    ma50 = _as_float(distance_from_ma_50)

    if r20 is None or r60 is None:
        return "INSUFFICIENT_DATA"

    strong_up = sum(1 for value in (r1, r5, r20, r60) if value is not None and value > 0.0)
    strong_down = sum(1 for value in (r1, r5, r20, r60) if value is not None and value < 0.0)

    if strong_up >= 3 and (ma20 is None or ma20 > 0) and (ma50 is None or ma50 > 0):
        return "STRONG_UPTREND"
    if strong_down >= 3 and (ma20 is None or ma20 < 0) and (ma50 is None or ma50 < 0):
        return "STRONG_DOWNTREND"
    if r20 > 0 and r60 > 0 and (ma20 is None or ma20 >= 0) and (ma50 is None or ma50 >= 0):
        return "UPTREND"
    if r20 < 0 and r60 < 0 and (ma20 is None or ma20 <= 0) and (ma50 is None or ma50 <= 0):
        return "DOWNTREND"
    return "MIXED"
