"""Pure market risk calculations for dry-run feature building."""

from __future__ import annotations


def _normalize_state(state: object) -> str:
    return str(state or "").strip().upper().replace("-", "_").replace(" ", "_")


def _bounded(value: float | None, lower: float = -1.0, upper: float = 1.0) -> float | None:
    if value is None:
        return None
    return max(lower, min(upper, value))


def map_volatility_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "LOW_VOLATILITY": -1.0,
        "NORMAL_VOLATILITY": -0.25,
        "MIXED_VOLATILITY": 0.0,
        "ELEVATED_VOLATILITY": 0.5,
        "HIGH_VOLATILITY": 0.8,
        "EXTREME_VOLATILITY": 1.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_options_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "LOW_VOLATILITY": -0.5,
        "HEDGING_PRESSURE": 0.6,
        "SKEWED_PROTECTIVE": 0.75,
        "MIXED_OPTIONS": 0.0,
        "HIGH_VOLATILITY": 0.5,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_flows_positioning_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "EASY_FLOW_CONDITIONS": -0.5,
        "FLOW_TAILWIND": -0.25,
        "MIXED_POSITIONING": 0.0,
        "FLOW_HEADWIND": 0.5,
        "TIGHT_FLOW_CONDITIONS": 0.8,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_event_calendar_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "NO_MAJOR_EVENTS": -0.5,
        "LOW_EVENT_RISK": -0.25,
        "MODERATE_EVENT_RISK": 0.25,
        "HIGH_EVENT_RISK": 0.75,
        "EXTREME_EVENT_RISK": 1.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_news_sentiment_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "POSITIVE_SENTIMENT": -0.5,
        "NEUTRAL_SENTIMENT": 0.0,
        "NEGATIVE_SENTIMENT": 0.6,
        "HIGH_NEGATIVE_SENTIMENT": 1.0,
        "MIXED_SENTIMENT": 0.2,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_breadth_participation_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "BROAD_PARTICIPATION": -0.5,
        "HEALTHY_PARTICIPATION": -0.25,
        "MIXED_PARTICIPATION": 0.0,
        "NARROW_PARTICIPATION": 0.5,
        "DIVERGENT_PARTICIPATION": 0.75,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def map_macro_liquidity_state_to_score(state):
    normalized = _normalize_state(state)
    mapping = {
        "STRONG_LIQUIDITY_TAILWIND": -0.75,
        "LIQUIDITY_TAILWIND": -0.5,
        "MIXED_MACRO_LIQUIDITY": 0.0,
        "LIQUIDITY_HEADWIND": 0.6,
        "STRONG_LIQUIDITY_HEADWIND": 1.0,
        "INSUFFICIENT_DATA": None,
    }
    return mapping.get(normalized, 0.0)


def calculate_composite_market_risk_score(component_scores):
    values = []
    for value in (component_scores or {}).values():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            values.append(_bounded(float(value)))
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def determine_market_risk_label(composite_score=None, component_scores=None):
    score = composite_score
    if score is None:
        score = calculate_composite_market_risk_score(component_scores)
    if score is None:
        return "INSUFFICIENT_DATA"
    if score <= -0.65:
        return "LOW_MARKET_RISK"
    if score <= -0.2:
        return "NORMAL_MARKET_RISK"
    if score <= 0.2:
        return "MIXED_MARKET_RISK"
    if score <= 0.55:
        return "ELEVATED_MARKET_RISK"
    if score <= 0.85:
        return "HIGH_MARKET_RISK"
    return "EXTREME_MARKET_RISK"

