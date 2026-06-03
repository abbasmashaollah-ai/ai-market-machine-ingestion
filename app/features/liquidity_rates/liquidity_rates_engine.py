"""Pure liquidity and rates calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def calculate_series_change(series_history, window):
    values = [_as_float(value) for value in series_history]
    values = [value for value in values if value is not None]
    window_value = int(window)
    if window_value <= 0 or len(values) <= window_value:
        return None
    latest = values[-1]
    start = values[-(window_value + 1)]
    return latest - start


def calculate_yield_curve_slope(us10y_latest, us2y_latest):
    us10y = _as_float(us10y_latest)
    us2y = _as_float(us2y_latest)
    if us10y is None or us2y is None:
        return None
    return us10y - us2y


def calculate_short_rate_pressure_score(fed_funds_change=None, us2y_change=None):
    values = [_as_float(fed_funds_change), _as_float(us2y_change)]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return -sum(values) / float(len(values))


def calculate_long_rate_pressure_score(us10y_change=None):
    value = _as_float(us10y_change)
    return None if value is None else -value


def calculate_yield_curve_pressure_score(yield_curve_slope=None, yield_curve_change=None):
    slope = _as_float(yield_curve_slope)
    change = _as_float(yield_curve_change)
    values = [value for value in (slope, change) if value is not None]
    if not values:
        return None
    return -sum(values) / float(len(values))


def calculate_real_yield_pressure_score(real_yield_change=None):
    value = _as_float(real_yield_change)
    return None if value is None else -value


def calculate_dollar_liquidity_pressure_score(dxy_change=None):
    value = _as_float(dxy_change)
    return None if value is None else value


def calculate_credit_liquidity_score(hyg_return=None):
    return _as_float(hyg_return)


def calculate_equity_liquidity_confirmation_score(spy_return=None):
    return _as_float(spy_return)


def determine_liquidity_regime_label(component_scores):
    short = _as_float(component_scores.get("short_rate_pressure_score"))
    long = _as_float(component_scores.get("long_rate_pressure_score"))
    curve = _as_float(component_scores.get("yield_curve_pressure_score"))
    real = _as_float(component_scores.get("real_yield_pressure_score"))
    dollar = _as_float(component_scores.get("dollar_liquidity_pressure_score"))
    credit = _as_float(component_scores.get("credit_liquidity_score"))
    equity = _as_float(component_scores.get("equity_liquidity_confirmation_score"))

    values = [short, long, curve, real, dollar, credit, equity]
    if all(value is None for value in values):
        return "INSUFFICIENT_DATA"

    pressure_values = [value for value in (short, long, curve, real, dollar) if value is not None]
    tailwind_values = [value for value in (credit, equity) if value is not None]
    tight_count = sum(1 for value in pressure_values if value is not None and value >= 0.15)
    easy_count = sum(1 for value in pressure_values if value is not None and value <= -0.05)
    positive_tailwind = sum(1 for value in tailwind_values if value > 0)
    negative_tailwind = sum(1 for value in tailwind_values if value < 0)

    if credit is not None and equity is not None and credit > 0 and equity > 0 and dollar is not None and dollar < 0 and short is not None and short <= 0.5 and long is not None and long <= 0.5:
        return "LIQUIDITY_TAILWIND"
    if credit is not None and equity is not None and credit < 0 and equity < 0 and dollar is not None and dollar > 0 and (short is not None and short > 0 or long is not None and long > 0):
        return "LIQUIDITY_HEADWIND"
    if tight_count >= 3 and negative_tailwind >= 1:
        return "TIGHT_FINANCIAL_CONDITIONS"
    if easy_count >= 3 and positive_tailwind >= 1:
        return "EASY_FINANCIAL_CONDITIONS"
    if positive_tailwind >= 2 and tight_count <= 1:
        return "LIQUIDITY_TAILWIND"
    if tight_count >= 2 and negative_tailwind >= 1:
        return "LIQUIDITY_HEADWIND"
    return "MIXED_LIQUIDITY"