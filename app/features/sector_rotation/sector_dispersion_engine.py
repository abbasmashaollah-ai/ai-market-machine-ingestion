"""Sector dispersion, breadth, and concentration evidence helpers."""

from __future__ import annotations

from collections.abc import Mapping
from math import sqrt


def _valid_values(values_by_symbol: Mapping[str, float | int | None]) -> list[tuple[str, float]]:
    values: list[tuple[str, float]] = []
    for symbol, value in values_by_symbol.items():
        if value is None:
            continue
        try:
            values.append((symbol.strip().upper(), float(value)))
        except (AttributeError, TypeError, ValueError):
            continue
    values.sort(key=lambda item: item[0])
    return values


def calculate_sector_dispersion_score(values_by_symbol: Mapping[str, float | int | None]) -> float | None:
    """Calculate a normalized dispersion score using population standard deviation."""

    values = [value for _, value in _valid_values(values_by_symbol)]
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return sqrt(variance)


def calculate_leadership_concentration_score(
    values_by_symbol: Mapping[str, float | int | None],
    top_n: int = 3,
) -> float | None:
    """Measure how much of the absolute score mass sits in the top_n symbols."""

    values = _valid_values(values_by_symbol)
    if not values:
        return None
    top_value_count = max(1, min(int(top_n), len(values)))
    ranked = sorted(values, key=lambda item: (-item[1], item[0]))
    total_abs = sum(abs(value) for _, value in ranked)
    if total_abs == 0:
        return 0.0
    top_abs = sum(abs(value) for _, value in ranked[:top_value_count])
    return top_abs / total_abs


def calculate_breadth_of_positive_scores(
    values_by_symbol: Mapping[str, float | int | None],
    threshold: float = 0.0,
) -> float | None:
    """Return the share of valid scores above threshold."""

    values = [value for _, value in _valid_values(values_by_symbol)]
    if not values:
        return None
    positive_count = sum(1 for value in values if value > threshold)
    return positive_count / len(values)


def detect_broad_rotation(
    values_by_symbol: Mapping[str, float | int | None],
    threshold: float = 0.0,
    min_positive_ratio: float = 0.6,
) -> bool:
    """Return True when enough sectors are above the threshold."""

    breadth = calculate_breadth_of_positive_scores(values_by_symbol, threshold=threshold)
    if breadth is None:
        return False
    return breadth >= float(min_positive_ratio)


def detect_narrow_rotation(
    values_by_symbol: Mapping[str, float | int | None],
    top_n: int = 3,
    concentration_threshold: float = 0.5,
) -> bool:
    """Return True when leadership is concentrated in the top_n symbols."""

    concentration = calculate_leadership_concentration_score(values_by_symbol, top_n=top_n)
    if concentration is None:
        return False
    return concentration >= float(concentration_threshold)

