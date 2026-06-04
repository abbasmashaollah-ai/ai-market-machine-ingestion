"""Pure helpers for deterministic options evidence."""

from __future__ import annotations


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _bounded(value: float | None) -> float | None:
    if value is None:
        return None
    return max(-1.0, min(1.0, value))


def calculate_implied_volatility_level(metrics):
    values = [_to_float(metrics.get("implied_volatility_30d")), _to_float(metrics.get("implied_volatility_60d"))]
    usable = [value for value in values if value is not None]
    return sum(usable) / len(usable) if usable else None


def calculate_realized_vs_implied_score(metrics):
    iv30 = _to_float(metrics.get("implied_volatility_30d"))
    rv20 = _to_float(metrics.get("realized_volatility_20d"))
    if iv30 is None or rv20 is None:
        return None
    return _bounded((iv30 - rv20) / max(abs(iv30), abs(rv20), 1e-9))


def calculate_iv_rank_score(metrics):
    iv_rank = _to_float(metrics.get("iv_rank"))
    iv_percentile = _to_float(metrics.get("iv_percentile"))
    values = []
    if iv_rank is not None:
        values.append(_bounded((iv_rank / 100.0) * 2.0 - 1.0))
    if iv_percentile is not None:
        values.append(_bounded((iv_percentile / 100.0) * 2.0 - 1.0))
    return sum(values) / len(values) if values else None


def calculate_put_call_pressure_score(metrics):
    put_call = _to_float(metrics.get("put_call_ratio"))
    if put_call is None:
        return None
    return _bounded(1.0 - put_call)


def calculate_call_pressure_score(metrics):
    call_volume = _to_float(metrics.get("call_volume"))
    put_volume = _to_float(metrics.get("put_volume"))
    if call_volume is None and put_volume is None:
        return None
    total = (call_volume or 0.0) + (put_volume or 0.0)
    if total == 0:
        return None
    return _bounded((call_volume or 0.0) / total * 2.0 - 1.0)


def calculate_gamma_pressure_score(metrics):
    gamma = _to_float(metrics.get("gamma_exposure"))
    if gamma is None:
        return None
    return _bounded(gamma / 10_000_000.0)


def calculate_skew_pressure_score(metrics):
    skew = _to_float(metrics.get("skew_25_delta"))
    if skew is None:
        return None
    return _bounded(-skew)


def calculate_iv_term_structure_score(metrics):
    slope = _to_float(metrics.get("term_structure_slope"))
    if slope is None:
        return None
    return _bounded(slope)


def determine_options_regime_label(component_scores):
    iv_level = _to_float(component_scores.get("implied_volatility_level"))
    pressure = _to_float(component_scores.get("realized_vs_implied_score"))
    if iv_level is None and pressure is None:
        return "INSUFFICIENT_DATA"
    if iv_level is not None and iv_level >= 0.7 and pressure is not None and pressure > 0.15:
        return "HIGH_VOLATILITY"
    if iv_level is not None and iv_level <= 0.25 and pressure is not None and pressure < -0.15:
        return "LOW_VOLATILITY"
    if pressure is not None and abs(pressure) < 0.1:
        return "MIXED_OPTIONS"
    if component_scores.get("put_call_pressure_score") is not None and component_scores.get("put_call_pressure_score") < -0.2:
        return "HEDGING_PRESSURE"
    if component_scores.get("skew_pressure_score") is not None and component_scores.get("skew_pressure_score") > 0.2:
        return "SKEWED_PROTECTIVE"
    return "MIXED_OPTIONS"
