"""Options positioning evidence helpers."""

from __future__ import annotations


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _bounded(value: float | None) -> float | None:
    if value is None:
        return None
    return max(-1.0, min(1.0, value))


def calculate_options_positioning_score(options_positioning):
    if not isinstance(options_positioning, dict):
        return None
    ratios = [
        _to_float(options_positioning.get("put_call_ratio")),
        _to_float(options_positioning.get("equity_put_call_ratio")),
        _to_float(options_positioning.get("index_put_call_ratio")),
    ]
    usable = [value for value in ratios if value is not None]
    if not usable:
        return None
    score = 1.0 - (sum(usable) / len(usable))
    return _bounded(score)
