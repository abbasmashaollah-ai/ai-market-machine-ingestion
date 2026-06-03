"""Build JSON-friendly cross-asset observations from close histories."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.cross_asset.cross_asset_engine import (
    calculate_asset_returns,
    calculate_commodity_pressure_score,
    calculate_credit_risk_score,
    calculate_dollar_pressure_score,
    calculate_equity_leadership_score,
    calculate_intermarket_alignment_score,
    calculate_rates_pressure_score,
    calculate_volatility_pressure_score,
    determine_descriptive_intermarket_state,
)


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


def _latest_symbols(close_history_by_symbol):
    return sorted(str(symbol).upper() for symbol in close_history_by_symbol.keys())


def build_cross_asset_observation(close_history_by_symbol, observation_date, timestamp=None, source="fixture_ohlcv"):
    returns_by_symbol = calculate_asset_returns(close_history_by_symbol)
    component_scores = {
        "equity_leadership_score": calculate_equity_leadership_score(returns_by_symbol),
        "credit_risk_score": calculate_credit_risk_score(returns_by_symbol),
        "rates_pressure_score": calculate_rates_pressure_score(returns_by_symbol),
        "dollar_pressure_score": calculate_dollar_pressure_score(returns_by_symbol),
        "commodity_pressure_score": calculate_commodity_pressure_score(returns_by_symbol),
        "volatility_pressure_score": calculate_volatility_pressure_score(returns_by_symbol),
    }
    component_scores["intermarket_alignment_score"] = calculate_intermarket_alignment_score(component_scores)
    descriptive_state = determine_descriptive_intermarket_state(component_scores)
    alignment = component_scores["intermarket_alignment_score"]
    payload = {
        "observation_date": _normalize_date(observation_date),
        "timestamp": _normalize_date(timestamp),
        "symbols": _latest_symbols(close_history_by_symbol),
        **component_scores,
        "risk_on_alignment_flag": bool(alignment is not None and alignment > 0.2),
        "risk_off_alignment_flag": bool(alignment is not None and alignment < -0.2),
        "divergence_flag": descriptive_state in {"EQUITY_CREDIT_DIVERGENCE", "MIXED_INTERMARKET"},
        "descriptive_intermarket_state": descriptive_state,
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