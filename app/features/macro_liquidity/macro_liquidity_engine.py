"""Pure macro liquidity calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Mapping


def _normalize_state(state: object) -> str:
    return str(state or "").strip().upper().replace("-", "_").replace(" ", "_")


def _bounded(value: float | None, lower: float = -1.0, upper: float = 1.0) -> float | None:
    if value is None:
        return None
    return max(lower, min(upper, value))


def map_liquidity_rates_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "STRONG_LIQUIDITY_TAILWIND": 1.0,
        "LIQUIDITY_TAILWIND": 0.75,
        "MIXED_MACRO_LIQUIDITY": 0.0,
        "LIQUIDITY_HEADWIND": -0.75,
        "STRONG_LIQUIDITY_HEADWIND": -1.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_cross_asset_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "RISK_ON": 0.75,
        "RISK_ON_EVIDENCE": 0.75,
        "MIXED_EVIDENCE": 0.0,
        "RISK_OFF": -0.75,
        "RISK_OFF_EVIDENCE": -0.75,
        "INSUFFICIENT_EVIDENCE": None,
    }
    return mapping.get(normalized, 0.0)


def map_flows_positioning_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "TIGHT_FLOW_CONDITIONS": -1.0,
        "FLOW_HEADWIND": -0.75,
        "MIXED_POSITIONING": 0.0,
        "FLOW_TAILWIND": 0.75,
        "EASY_FLOW_CONDITIONS": 1.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_volatility_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "LOW_VOLATILITY": 1.0,
        "NORMAL_VOLATILITY": 0.5,
        "ELEVATED_VOLATILITY": -0.25,
        "HIGH_VOLATILITY": -0.75,
        "EXTREME_VOLATILITY": -1.0,
        "MIXED_VOLATILITY": 0.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_breadth_participation_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "BROAD_PARTICIPATION": 1.0,
        "HEALTHY_PARTICIPATION": 0.75,
        "MIXED_PARTICIPATION": 0.0,
        "NARROW_PARTICIPATION": -0.75,
        "DIVERGENT_PARTICIPATION": -0.5,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_sector_rotation_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "RISK_ON_EVIDENCE": 0.75,
        "RISK_OFF_EVIDENCE": -0.75,
        "MIXED_EVIDENCE": 0.0,
        "INSUFFICIENT_EVIDENCE": None,
    }
    return mapping.get(normalized, 0.0)


def calculate_composite_macro_liquidity_score(component_scores):
    values = []
    for value in (component_scores or {}).values():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            values.append(_bounded(float(value)))
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def determine_macro_liquidity_label(composite_score=None, component_scores=None):
    score = composite_score
    if score is None:
        score = calculate_composite_macro_liquidity_score(component_scores)
    if score is None:
        return "INSUFFICIENT_DATA"
    if score >= 0.65:
        return "STRONG_LIQUIDITY_TAILWIND"
    if score >= 0.2:
        return "LIQUIDITY_TAILWIND"
    if score <= -0.65:
        return "STRONG_LIQUIDITY_HEADWIND"
    if score <= -0.2:
        return "LIQUIDITY_HEADWIND"
    return "MIXED_MACRO_LIQUIDITY"

