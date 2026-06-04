"""Advance/decline breadth evidence calculations for dry-run use only."""

from __future__ import annotations


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


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


def calculate_advance_decline_ratio(advancers, decliners):
    advancers_value = _as_float(advancers)
    decliners_value = _as_float(decliners)
    if advancers_value is None or decliners_value is None:
        return None
    if decliners_value == 0:
        if advancers_value > 0:
            return advancers_value
        return 0.0
    return advancers_value / decliners_value


def calculate_advance_decline_line(advancers, decliners):
    advancers_value = _as_float(advancers)
    decliners_value = _as_float(decliners)
    if advancers_value is None or decliners_value is None:
        return None
    return advancers_value - decliners_value
