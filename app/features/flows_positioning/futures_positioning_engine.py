"""Futures positioning evidence helpers."""

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


def calculate_futures_positioning_score(futures_positioning):
    values = []
    for item in futures_positioning or []:
        if not isinstance(item, dict):
            continue
        percentile = _to_float(item.get("net_position_percentile"))
        if percentile is not None:
            values.append(_bounded((percentile * 2.0) - 1.0))
    return sum(values) / len(values) if values else None
