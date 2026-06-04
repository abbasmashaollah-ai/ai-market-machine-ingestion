"""Pure earnings calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime


def _as_date(value: date | datetime | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _bounded(value: float | None, lower: float = -1.0, upper: float = 1.0) -> float | None:
    if value is None:
        return None
    return max(lower, min(upper, value))


def calculate_days_to_earnings(observation_date, earnings_date):
    obs = _as_date(observation_date)
    earnings = _as_date(earnings_date)
    if obs is None or earnings is None:
        return None
    return (earnings - obs).days


def calculate_days_since_earnings(observation_date, earnings_date):
    obs = _as_date(observation_date)
    earnings = _as_date(earnings_date)
    if obs is None or earnings is None:
        return None
    return (obs - earnings).days


def calculate_surprise_score(actual, estimate):
    actual_value = _to_float(actual)
    estimate_value = _to_float(estimate)
    if actual_value is None or estimate_value is None:
        return None
    denominator = abs(estimate_value) if estimate_value not in (0.0, -0.0) else max(abs(actual_value), 1.0)
    if denominator == 0:
        return 0.0
    return _bounded((actual_value - estimate_value) / denominator)


def calculate_guidance_score(guidance_direction):
    if guidance_direction is None:
        return None
    normalized = str(guidance_direction).strip().lower()
    mapping = {
        "raise": 1.0,
        "raised": 1.0,
        "positive": 1.0,
        "positive_guidance": 1.0,
        "beat_and_raise": 1.0,
        "reaffirm": 0.3,
        "reaffirmed": 0.3,
        "mixed": 0.0,
        "neutral": 0.0,
        "hold": 0.0,
        "lower": -1.0,
        "lowered": -1.0,
        "negative": -1.0,
        "negative_guidance": -1.0,
        "withdraw": -0.5,
        "withdrew": -0.5,
    }
    return mapping.get(normalized, 0.0)


def calculate_estimate_revision_score(analyst_revision_trend):
    if analyst_revision_trend is None:
        return None
    normalized = str(analyst_revision_trend).strip().lower()
    mapping = {
        "positive": 1.0,
        "up": 1.0,
        "raised": 1.0,
        "improving": 0.7,
        "flat": 0.0,
        "neutral": 0.0,
        "mixed": 0.0,
        "negative": -1.0,
        "down": -1.0,
        "lowered": -1.0,
        "deteriorating": -0.7,
    }
    return mapping.get(normalized, 0.0)


def calculate_pre_earnings_drift_score(pre_earnings_price_change_5d):
    value = _to_float(pre_earnings_price_change_5d)
    if value is None:
        return None
    return _bounded(value / 10.0)


def calculate_post_earnings_reaction_score(post_earnings_price_change_1d=None, post_earnings_price_change_5d=None):
    candidates = []
    one_day = _to_float(post_earnings_price_change_1d)
    five_day = _to_float(post_earnings_price_change_5d)
    if one_day is not None:
        candidates.append(one_day / 10.0)
    if five_day is not None:
        candidates.append(five_day / 20.0)
    if not candidates:
        return None
    return _bounded(sum(candidates) / len(candidates))


def calculate_implied_vs_actual_move_score(implied_move_percent=None, actual_move_percent=None):
    implied = _to_float(implied_move_percent)
    actual = _to_float(actual_move_percent)
    if implied is None or actual is None:
        return None
    if implied == 0:
        return _bounded(actual / 10.0)
    return _bounded((actual - implied) / abs(implied))


def calculate_earnings_quality_score(component_scores):
    values = []
    for value in (component_scores or {}).values():
        numeric = _to_float(value)
        if numeric is not None:
            values.append(_bounded(numeric))
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def calculate_earnings_risk_score(component_scores, days_to_earnings=None):
    quality = calculate_earnings_quality_score(component_scores)
    if quality is None and days_to_earnings is None:
        return None
    score = 0.0
    if quality is not None:
        score += (1.0 - quality) / 2.0
    days = None if days_to_earnings is None else int(days_to_earnings)
    if days is not None:
        if days > 21:
            score += 0.15
        elif days > 7:
            score += 0.08
        elif days >= 0:
            score += 0.25
        else:
            score += 0.1
    return round(_bounded(score, 0.0, 1.0) or 0.0, 3)


def determine_earnings_regime_label(component_scores, days_to_earnings=None, days_since_earnings=None):
    quality = calculate_earnings_quality_score(component_scores)
    risk = calculate_earnings_risk_score(component_scores, days_to_earnings=days_to_earnings)
    reaction = _to_float((component_scores or {}).get("post_earnings_reaction_score"))
    if quality is None and risk is None and reaction is None and days_to_earnings is None and days_since_earnings is None:
        return "INSUFFICIENT_DATA"
    if days_to_earnings is not None and days_to_earnings > 0:
        return "UPCOMING_EARNINGS_RISK"
    if days_since_earnings is not None and days_since_earnings >= 0:
        if reaction is not None and reaction >= 0.25:
            return "POSITIVE_EARNINGS_REACTION"
        if reaction is not None and reaction <= -0.25:
            return "NEGATIVE_EARNINGS_REACTION"
    if quality is not None and quality >= 0.5 and (risk is None or risk <= 0.5):
        return "STRONG_EARNINGS_QUALITY"
    if quality is not None and quality <= -0.35 and (risk is None or risk >= 0.4):
        return "WEAK_EARNINGS_QUALITY"
    if quality is not None or risk is not None or reaction is not None:
        return "MIXED_EARNINGS"
    return "LOW_EARNINGS_SIGNAL"

