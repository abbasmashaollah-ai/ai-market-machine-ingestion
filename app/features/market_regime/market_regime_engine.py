"""Pure market regime calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Mapping


def _normalize_state(state: object) -> str:
    return str(state or "").strip().upper().replace("-", "_").replace(" ", "_")


def _bounded(value: float | None, lower: float = -1.0, upper: float = 1.0) -> float | None:
    if value is None:
        return None
    return max(lower, min(upper, value))


def map_macro_liquidity_state_to_score(state):
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


def map_market_risk_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "LOW_MARKET_RISK": 1.0,
        "NORMAL_MARKET_RISK": 0.5,
        "MIXED_MARKET_RISK": 0.0,
        "ELEVATED_MARKET_RISK": -0.25,
        "HIGH_MARKET_RISK": -0.75,
        "EXTREME_MARKET_RISK": -1.0,
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
        "RISK_ON_LEADERSHIP": 0.75,
        "BROAD_IMPROVEMENT": 0.5,
        "NARROW_LEADERSHIP": -0.25,
        "DEFENSIVE_LEADERSHIP": -0.75,
        "BROAD_DETERIORATION": -0.5,
        "MIXED_ROTATION": 0.0,
        "NO_CLEAR_ROTATION": 0.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_cross_asset_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "RISK_ON_CONFIRMATION": 0.75,
        "MIXED_INTERMARKET": 0.0,
        "EQUITY_CREDIT_DIVERGENCE": -0.25,
        "RATES_PRESSURE": -0.5,
        "DOLLAR_PRESSURE": -0.5,
        "RISK_OFF_PRESSURE": -0.75,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_price_states_to_trend_score(price_states_by_symbol):
    if not isinstance(price_states_by_symbol, Mapping) or not price_states_by_symbol:
        return None
    values = []
    for state in price_states_by_symbol.values():
        normalized = _normalize_state(state)
        mapping = {
            "STRONG_UPTREND": 1.0,
            "UPTREND": 0.5,
            "MIXED": 0.0,
            "DOWNTREND": -0.5,
            "STRONG_DOWNTREND": -1.0,
            "INSUFFICIENT_DATA": None,
        }
        value = mapping.get(normalized, 0.0)
        if value is not None:
            values.append(value)
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def map_volatility_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "LOW_VOLATILITY": 1.0,
        "NORMAL_VOLATILITY": 0.5,
        "MIXED_VOLATILITY": 0.0,
        "ELEVATED_VOLATILITY": -0.25,
        "HIGH_VOLATILITY": -0.75,
        "EXTREME_VOLATILITY": -1.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def calculate_composite_market_regime_score(component_scores):
    values = []
    for value in (component_scores or {}).values():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            values.append(_bounded(float(value)))
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def determine_market_regime_label(composite_score=None, component_scores=None):
    score = composite_score
    if score is None:
        score = calculate_composite_market_regime_score(component_scores)
    if score is None:
        return "INSUFFICIENT_DATA"
    if score >= 0.6:
        return "RISK_ON_EXPANSION"
    if score >= 0.25:
        return "RISK_ON_FRAGILE"
    if score <= -0.6:
        return "STRESS_REGIME"
    if score <= -0.25:
        return "DEFENSIVE_RISK_OFF"
    if -0.25 < score < 0.25:
        return "NEUTRAL_MIXED"
    return "TRANSITION_REGIME"

