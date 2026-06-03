"""Pure breadth and participation calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _latest_value(history: Sequence[object]) -> float | None:
    if not history:
        return None
    latest = history[-1]
    return _as_float(latest)


def calculate_advancers_decliners_unchanged(previous_close_by_symbol, latest_close_by_symbol):
    advancers = decliners = unchanged = 0
    for symbol, latest in latest_close_by_symbol.items():
        previous = previous_close_by_symbol.get(symbol)
        if previous is None or latest is None:
            continue
        if latest > previous:
            advancers += 1
        elif latest < previous:
            decliners += 1
        else:
            unchanged += 1
    return advancers, decliners, unchanged


def calculate_advancing_declining_volume(previous_close_by_symbol, latest_close_by_symbol, latest_volume_by_symbol):
    advancing_volume = 0.0
    declining_volume = 0.0
    for symbol, latest in latest_close_by_symbol.items():
        previous = previous_close_by_symbol.get(symbol)
        volume = _as_float(latest_volume_by_symbol.get(symbol))
        if previous is None or latest is None or volume is None:
            continue
        if latest > previous:
            advancing_volume += volume
        elif latest < previous:
            declining_volume += volume
    return advancing_volume, declining_volume


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


def calculate_breadth_score(advancers, decliners, unchanged):
    total = advancers + decliners + unchanged
    if total <= 0:
        return None
    return (advancers - decliners) / float(total)


def calculate_participation_score(percent_above_20d=None, percent_above_50d=None, percent_above_200d=None):
    values = [_as_float(value) for value in (percent_above_20d, percent_above_50d, percent_above_200d)]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values) / float(len(values))
