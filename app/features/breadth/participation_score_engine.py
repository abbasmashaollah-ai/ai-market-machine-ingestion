"""Participation score evidence calculations for dry-run use only."""

from __future__ import annotations


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


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
