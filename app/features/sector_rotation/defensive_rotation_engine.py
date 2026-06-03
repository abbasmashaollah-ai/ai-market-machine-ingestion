"""Defensive, rate-sensitive, and group leadership score helpers."""

from __future__ import annotations

from collections.abc import Mapping

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


def _group_members(
    symbol_scores: Mapping[str, float | int | None],
    sector_definitions: Mapping[str, SectorDefinition] | None,
    group_flag: str,
) -> list[float]:
    values: list[float] = []
    for symbol, score in symbol_scores.items():
        definition = _resolve_definition(symbol, sector_definitions)
        if definition is None or not getattr(definition, group_flag, False):
            continue
        if score is None:
            continue
        try:
            values.append(float(score))
        except (TypeError, ValueError):
            continue
    return values


def calculate_group_leadership_score(
    symbol_scores: Mapping[str, float | int | None],
    sector_definitions: Mapping[str, SectorDefinition] | None,
    group_flag: str,
) -> float | None:
    """Calculate an average score for the requested sector group."""

    values = _group_members(symbol_scores, sector_definitions, group_flag)
    if not values:
        return None
    return sum(values) / len(values)


def calculate_defensive_leadership_score(
    symbol_scores: Mapping[str, float | int | None],
    sector_definitions: Mapping[str, SectorDefinition] | None = None,
) -> float | None:
    """Calculate the defensive leadership score."""

    return calculate_group_leadership_score(symbol_scores, sector_definitions, "is_defensive_sector")


def calculate_rate_sensitive_leadership_score(
    symbol_scores: Mapping[str, float | int | None],
    sector_definitions: Mapping[str, SectorDefinition] | None = None,
) -> float | None:
    """Calculate the rate-sensitive leadership score."""

    return calculate_group_leadership_score(symbol_scores, sector_definitions, "is_rate_sensitive_sector")
