"""Short-interest pressure evidence helpers."""

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


def calculate_short_interest_pressure_score(short_interest):
    values = []
    for item in short_interest or []:
        if not isinstance(item, dict):
            continue
        short_pct = _to_float(item.get("short_interest_percent_float"))
        days_to_cover = _to_float(item.get("days_to_cover"))
        if short_pct is None and days_to_cover is None:
            continue
        score = 0.0
        if short_pct is not None:
            score += short_pct
        if days_to_cover is not None:
            score += min(days_to_cover / 10.0, 1.0)
        values.append(_bounded(score / 2.0))
    return sum(values) / len(values) if values else None
