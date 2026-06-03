"""Build JSON-friendly liquidity/rates observations from fixture histories."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.liquidity_rates.liquidity_rates_engine import (
    calculate_credit_liquidity_score,
    calculate_dollar_liquidity_pressure_score,
    calculate_equity_liquidity_confirmation_score,
    calculate_long_rate_pressure_score,
    calculate_real_yield_pressure_score,
    calculate_series_change,
    calculate_short_rate_pressure_score,
    calculate_yield_curve_pressure_score,
    calculate_yield_curve_slope,
    determine_liquidity_regime_label,
)
from app.features.liquidity_rates.liquidity_rates_universe import get_required_liquidity_rates_series


def _normalize_date(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _metadata_dict(metadata: Mapping[str, object] | None) -> dict[str, object]:
    result = dict(metadata or {})
    result.setdefault("quality_status", "PENDING")
    result.setdefault("certification_status", "PENDING")
    result.setdefault("freshness_status", "PENDING")
    result.setdefault("lineage", {})
    result.setdefault("evidence", {})
    return result


def _series_values(history) -> list[float]:
    values = [row["value"] if isinstance(row, Mapping) else row for row in history]
    return [float(value) for value in values if isinstance(value, (int, float))]


def build_liquidity_rates_observation(series_history_by_name, observation_date, timestamp=None, source="fixture_macro"):
    series_keys = {str(name).upper() for name in series_history_by_name}
    required_series = get_required_liquidity_rates_series()

    latest_values: dict[str, float | None] = {}
    series_map: dict[str, list[object]] = {}
    for series in required_series:
        history = list(series_history_by_name.get(series, []))
        series_map[series] = history
        values = _series_values(history)
        latest_values[series] = float(values[-1]) if values else None

    fed_funds_change = calculate_series_change(_series_values(series_map["FED_FUNDS"]), 20)
    us10y_change = calculate_series_change(_series_values(series_map["US10Y"]), 20)
    us2y_change = calculate_series_change(_series_values(series_map["US2Y"]), 20)
    real_yield_change = calculate_series_change(_series_values(series_map["REAL_YIELD_10Y"]), 20)
    dxy_change = calculate_series_change(_series_values(series_map["DXY"]), 20)
    hyg_return = calculate_series_change(_series_values(series_map["HYG"]), 20)
    spy_return = calculate_series_change(_series_values(series_map["SPY"]), 20)
    yield_curve_slope = calculate_yield_curve_slope(latest_values["US10Y"], latest_values["US2Y"])
    previous_yield_curve_slope = None
    if latest_values["US10Y"] is not None and latest_values["US2Y"] is not None:
        # Use the 20d change in the spread as a simple deterministic proxy.
        us10y_series = _series_values(series_map["US10Y"])
        us2y_series = _series_values(series_map["US2Y"])
        if len(us10y_series) > 20 and len(us2y_series) > 20:
            previous_yield_curve_slope = calculate_yield_curve_slope(us10y_series[-21], us2y_series[-21])
    yield_curve_change = None if yield_curve_slope is None or previous_yield_curve_slope is None else yield_curve_slope - previous_yield_curve_slope

    component_scores = {
        "short_rate_pressure_score": calculate_short_rate_pressure_score(fed_funds_change=fed_funds_change, us2y_change=us2y_change),
        "long_rate_pressure_score": calculate_long_rate_pressure_score(us10y_change=us10y_change),
        "yield_curve_slope": yield_curve_slope,
        "yield_curve_pressure_score": calculate_yield_curve_pressure_score(yield_curve_slope=yield_curve_slope, yield_curve_change=yield_curve_change),
        "real_yield_pressure_score": calculate_real_yield_pressure_score(real_yield_change=real_yield_change),
        "dollar_liquidity_pressure_score": calculate_dollar_liquidity_pressure_score(dxy_change=dxy_change),
        "credit_liquidity_score": calculate_credit_liquidity_score(hyg_return=hyg_return),
        "equity_liquidity_confirmation_score": calculate_equity_liquidity_confirmation_score(spy_return=spy_return),
    }
    component_scores["liquidity_regime_label"] = determine_liquidity_regime_label(component_scores)

    payload = {
        "observation_date": _normalize_date(observation_date),
        "timestamp": _normalize_date(timestamp),
        "series": sorted(series_keys),
        **component_scores,
        "source": source,
    }
    metadata_dict = _metadata_dict(None)
    payload.update(
        {
            "quality_status": metadata_dict["quality_status"],
            "certification_status": metadata_dict["certification_status"],
            "freshness_status": metadata_dict["freshness_status"],
            "lineage": metadata_dict["lineage"],
            "evidence": metadata_dict["evidence"],
        }
    )
    return payload