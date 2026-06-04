"""Crowdedness evidence helpers."""

from __future__ import annotations


def calculate_crowdedness_score(component_scores):
    values = [abs(float(value)) for value in component_scores.values() if isinstance(value, (int, float))]
    return min(1.0, sum(values) / len(values)) if values else None
