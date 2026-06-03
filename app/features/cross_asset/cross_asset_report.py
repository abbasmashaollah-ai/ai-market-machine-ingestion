"""Compact dry-run report for cross-asset observations."""

from __future__ import annotations


def build_cross_asset_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "descriptive_intermarket_state": payload.get("descriptive_intermarket_state"),
        "equity_leadership_score": payload.get("equity_leadership_score"),
        "credit_risk_score": payload.get("credit_risk_score"),
        "rates_pressure_score": payload.get("rates_pressure_score"),
        "dollar_pressure_score": payload.get("dollar_pressure_score"),
        "commodity_pressure_score": payload.get("commodity_pressure_score"),
        "volatility_pressure_score": payload.get("volatility_pressure_score"),
        "intermarket_alignment_score": payload.get("intermarket_alignment_score"),
        "risk_on_alignment_flag": payload.get("risk_on_alignment_flag"),
        "risk_off_alignment_flag": payload.get("risk_off_alignment_flag"),
        "divergence_flag": payload.get("divergence_flag"),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report