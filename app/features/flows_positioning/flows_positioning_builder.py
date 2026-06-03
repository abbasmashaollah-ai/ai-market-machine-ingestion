"""Builder for dry-run flows and positioning observations."""

from __future__ import annotations

from datetime import datetime, timezone

from .flows_positioning_engine import (
    calculate_crowdedness_score,
    calculate_credit_flow_score,
    calculate_defensive_flow_score,
    calculate_equity_flow_score,
    calculate_fund_exposure_score,
    calculate_futures_positioning_score,
    calculate_options_positioning_score,
    calculate_positioning_risk_score,
    calculate_short_interest_pressure_score,
    determine_flow_regime_label,
)


def _normalize_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def build_flows_positioning_observation(input_payload, observation_date, timestamp=None, source="fixture_flows_positioning"):
    payload = dict(input_payload or {})
    etf_flows = payload.get("etf_flows") or []
    options_positioning = payload.get("options_positioning") or {}
    futures_positioning = payload.get("futures_positioning") or []
    short_interest = payload.get("short_interest") or []
    fund_exposure = payload.get("fund_exposure") or {}
    equity_flow_score = calculate_equity_flow_score(etf_flows)
    defensive_flow_score = calculate_defensive_flow_score(etf_flows)
    credit_flow_score = calculate_credit_flow_score(etf_flows)
    options_positioning_score = calculate_options_positioning_score(options_positioning)
    futures_positioning_score = calculate_futures_positioning_score(futures_positioning)
    short_interest_pressure_score = calculate_short_interest_pressure_score(short_interest)
    fund_exposure_score = calculate_fund_exposure_score(fund_exposure)
    component_scores = {
        "equity_flow_score": equity_flow_score,
        "defensive_flow_score": defensive_flow_score,
        "credit_flow_score": credit_flow_score,
        "options_positioning_score": options_positioning_score,
        "futures_positioning_score": futures_positioning_score,
        "short_interest_pressure_score": short_interest_pressure_score,
        "fund_exposure_score": fund_exposure_score,
    }
    crowdedness_score = calculate_crowdedness_score(component_scores)
    positioning_risk_score = calculate_positioning_risk_score(component_scores)
    component_scores["crowdedness_score"] = crowdedness_score
    component_scores["positioning_risk_score"] = positioning_risk_score
    flow_regime_label = determine_flow_regime_label(component_scores)
    return {
        "observation_date": str(observation_date),
        "timestamp": _normalize_timestamp(timestamp),
        **component_scores,
        "flow_regime_label": flow_regime_label,
        "source": source,
        "quality_status": "PENDING",
        "certification_status": "PENDING",
        "freshness_status": "PENDING",
        "lineage": {},
        "evidence": {"source_payload": payload},
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
