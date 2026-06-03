"""Cyclical, growth, and risk-on leadership score helpers."""

from __future__ import annotations

from collections.abc import Mapping

from app.features.sector_rotation.defensive_rotation_engine import calculate_group_leadership_score
from app.features.sector_rotation.sector_universe import SectorDefinition, get_sector_definition, is_sector_symbol


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol is required")
    return normalized


def _resolve_definition(symbol: str, sector_definitions: Mapping[str, SectorDefinition] | None = None) -> SectorDefinition | None:
    normalized = _normalize_symbol(symbol)
    if sector_definitions is not None:
        candidate = sector_definitions.get(normalized)
        if candidate is not None:
            return candidate
    if is_sector_symbol(normalized):
        return get_sector_definition(normalized)
    return None


def calculate_cyclical_leadership_score(
    symbol_scores: Mapping[str, float | int | None],
    sector_definitions: Mapping[str, SectorDefinition] | None = None,
) -> float | None:
    """Calculate the cyclical leadership score."""

    return calculate_group_leadership_score(symbol_scores, sector_definitions, "is_cyclical_sector")


def calculate_growth_leadership_score(
    symbol_scores: Mapping[str, float | int | None],
    sector_definitions: Mapping[str, SectorDefinition] | None = None,
) -> float | None:
    """Calculate the growth leadership score."""

    return calculate_group_leadership_score(symbol_scores, sector_definitions, "is_growth_sector")


def calculate_risk_on_leadership_score(
    symbol_scores: Mapping[str, float | int | None],
    sector_definitions: Mapping[str, SectorDefinition] | None = None,
) -> float | None:
    """Calculate a bounded risk-on leadership evidence score.

    The score is the average of cyclical and growth group leadership evidence,
    scaled into the range [-1, 1] when possible.
    """

    cyclical = calculate_cyclical_leadership_score(symbol_scores, sector_definitions)
    growth = calculate_growth_leadership_score(symbol_scores, sector_definitions)
    components = [value for value in (cyclical, growth) if value is not None]
    if not components:
        return None
    average = sum(components) / len(components)
    return max(-1.0, min(1.0, average))
