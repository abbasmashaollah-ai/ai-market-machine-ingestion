"""Pure price evidence calculations for dry-run feature building."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _mapping_value(row: object, key: str) -> float | None:
    if not isinstance(row, Mapping):
        return _as_float(row)
    return _as_float(row.get(key))


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


def calculate_return_252d(close_history):
    return calculate_rolling_returns(close_history, windows=(252,)).get(252)


def calculate_moving_average(close_history, window):
    closes = [_as_float(value) for value in close_history]
    closes = [value for value in closes if value is not None]
    window_value = int(window)
    if window_value <= 0 or len(closes) < window_value:
        return None
    subset = closes[-window_value:]
    return sum(subset) / float(window_value)


def calculate_moving_average_100d(close_history):
    return calculate_moving_average(close_history, 100)


def calculate_moving_average_200d(close_history):
    return calculate_moving_average(close_history, 200)


def calculate_distance_from_moving_average(latest_close, moving_average):
    latest = _as_float(latest_close)
    average = _as_float(moving_average)
    if latest is None or average is None or average == 0:
        return None
    return (latest - average) / average


def above_moving_average(latest_close, moving_average):
    latest = _as_float(latest_close)
    average = _as_float(moving_average)
    if latest is None or average is None:
        return None
    return latest > average


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


def _daily_returns(close_history):
    closes = [_as_float(value) for value in close_history]
    closes = [value for value in closes if value is not None]
    if len(closes) < 2:
        return []
    returns = []
    for index in range(1, len(closes)):
        previous = closes[index - 1]
        current = closes[index]
        if previous == 0:
            continue
        returns.append((current - previous) / previous)
    return returns


def calculate_realized_volatility(close_history, window):
    window_value = int(window)
    if window_value <= 1:
        return None
    returns = _daily_returns(close_history)
    if len(returns) < window_value:
        return None
    subset = returns[-window_value:]
    mean = sum(subset) / float(window_value)
    variance = sum((value - mean) ** 2 for value in subset) / float(window_value)
    return math.sqrt(variance) * math.sqrt(252.0)


def calculate_true_range(previous_close, high, low, close):
    previous = _as_float(previous_close)
    high_value = _as_float(high)
    low_value = _as_float(low)
    close_value = _as_float(close)
    if high_value is None or low_value is None or close_value is None:
        return None
    if previous is None:
        return high_value - low_value
    return max(high_value - low_value, abs(high_value - previous), abs(low_value - previous))


def calculate_atr_14d(ohlcv_history):
    rows = list(ohlcv_history or [])
    true_ranges: list[float] = []
    previous_close = None
    for row in rows:
        high = _mapping_value(row, "high")
        low = _mapping_value(row, "low")
        close = _mapping_value(row, "close")
        true_range = calculate_true_range(previous_close, high, low, close)
        if true_range is not None:
            true_ranges.append(true_range)
        previous_close = close if close is not None else previous_close
    if len(true_ranges) < 14:
        return None
    subset = true_ranges[-14:]
    return sum(subset) / 14.0


def calculate_dollar_volume(ohlcv_row):
    close = _mapping_value(ohlcv_row, "close")
    volume = _mapping_value(ohlcv_row, "volume")
    if close is None or volume is None:
        return None
    return close * volume


def calculate_average_dollar_volume_20d(ohlcv_history):
    rows = list(ohlcv_history or [])
    dollar_volumes = [calculate_dollar_volume(row) for row in rows]
    dollar_volumes = [value for value in dollar_volumes if value is not None]
    if len(dollar_volumes) < 20:
        return None
    subset = dollar_volumes[-20:]
    return sum(subset) / 20.0


def calculate_relative_volume_20d(ohlcv_history):
    rows = list(ohlcv_history or [])
    if not rows:
        return None
    latest = rows[-1]
    latest_volume = _mapping_value(latest, "volume")
    average_volume = None
    volumes = [_mapping_value(row, "volume") for row in rows]
    volumes = [value for value in volumes if value is not None]
    if len(volumes) >= 20:
        average_volume = sum(volumes[-20:]) / 20.0
    if latest_volume is None or average_volume is None or average_volume == 0:
        return None
    return latest_volume / average_volume


def calculate_liquidity_score(ohlcv_history):
    average_dollar_volume = calculate_average_dollar_volume_20d(ohlcv_history)
    relative_volume = calculate_relative_volume_20d(ohlcv_history)
    if average_dollar_volume is None and relative_volume is None:
        return None
    score_components = []
    if average_dollar_volume is not None:
        score_components.append(min(1.0, max(0.0, average_dollar_volume / 10_000_000.0)))
    if relative_volume is not None:
        score_components.append(min(1.0, max(0.0, relative_volume / 2.0)))
    if not score_components:
        return None
    return sum(score_components) / len(score_components)


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
