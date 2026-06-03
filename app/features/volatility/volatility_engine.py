"""Pure volatility calculations for dry-run feature building."""

from __future__ import annotations


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


def calculate_latest_level(series_history):
    values = [_as_float(value) for value in series_history]
    values = [value for value in values if value is not None]
    return values[-1] if values else None


def calculate_volatility_of_volatility_score(vvix_level=None, vvix_change_5d=None):
    level = _as_float(vvix_level)
    change = _as_float(vvix_change_5d)
    values = [value for value in (level, change) if value is not None]
    if not values:
        return None
    return (level or 0.0) / 100.0 + (change or 0.0) if change is not None else (level or 0.0) / 100.0


def calculate_equity_volatility_pressure_score(vix_level=None, vix_change_5d=None):
    level = _as_float(vix_level)
    change = _as_float(vix_change_5d)
    values = [value for value in (level, change) if value is not None]
    if not values:
        return None
    return (level or 0.0) / 100.0 + (change or 0.0) if change is not None else (level or 0.0) / 100.0


def calculate_small_cap_volatility_pressure_score(rvx_level=None, rvx_change_5d=None):
    level = _as_float(rvx_level)
    change = _as_float(rvx_change_5d)
    values = [value for value in (level, change) if value is not None]
    if not values:
        return None
    return (level or 0.0) / 100.0 + (change or 0.0) if change is not None else (level or 0.0) / 100.0


def calculate_nasdaq_volatility_pressure_score(vxn_level=None, vxn_change_5d=None):
    level = _as_float(vxn_level)
    change = _as_float(vxn_change_5d)
    values = [value for value in (level, change) if value is not None]
    if not values:
        return None
    return (level or 0.0) / 100.0 + (change or 0.0) if change is not None else (level or 0.0) / 100.0


def calculate_composite_volatility_stress_score(component_scores):
    values = [_as_float(component_scores.get(name)) for name in (
        "volatility_of_volatility_score",
        "equity_volatility_pressure_score",
        "nasdaq_volatility_pressure_score",
        "small_cap_volatility_pressure_score",
    )]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values) / float(len(values))


def determine_volatility_regime_label(vix_level=None, composite_score=None):
    level = _as_float(vix_level)
    composite = _as_float(composite_score)
    if level is None and composite is None:
        return "INSUFFICIENT_DATA"
    if level is not None and level < 15 and (composite is None or composite < 0.2):
        return "LOW_VOLATILITY"
    if level is not None and level < 20 and (composite is None or composite < 0.4):
        return "NORMAL_VOLATILITY"
    if level is not None and level < 28:
        return "ELEVATED_VOLATILITY"
    if level is not None and level < 40:
        return "HIGH_VOLATILITY"
    if level is not None:
        return "EXTREME_VOLATILITY"
    if composite is not None and composite < 0.2:
        return "LOW_VOLATILITY"
    if composite is not None and composite < 0.4:
        return "NORMAL_VOLATILITY"
    if composite is not None and composite < 0.6:
        return "ELEVATED_VOLATILITY"
    return "MIXED_VOLATILITY"
