"""Report helpers for flows and positioning dry-run outputs."""

from __future__ import annotations


def build_flows_positioning_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "equity_flow_score": payload.get("equity_flow_score"),
        "defensive_flow_score": payload.get("defensive_flow_score"),
        "credit_flow_score": payload.get("credit_flow_score"),
        "options_positioning_score": payload.get("options_positioning_score"),
        "futures_positioning_score": payload.get("futures_positioning_score"),
        "short_interest_pressure_score": payload.get("short_interest_pressure_score"),
        "fund_exposure_score": payload.get("fund_exposure_score"),
        "crowdedness_score": payload.get("crowdedness_score"),
        "positioning_risk_score": payload.get("positioning_risk_score"),
        "flow_regime_label": payload.get("flow_regime_label"),
        "safety_flags": {
            "no_db_writes": bool(payload.get("no_db_writes") is True),
            "no_vendor_calls": bool(payload.get("no_vendor_calls") is True),
            "no_scheduler_activation": bool(payload.get("no_scheduler_activation") is True),
        },
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report
