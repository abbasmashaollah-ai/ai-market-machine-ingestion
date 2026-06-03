"""Compact dry-run report for volatility observations."""

from __future__ import annotations


def build_volatility_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "vix_level": payload.get("vix_level"),
        "vvix_level": payload.get("vvix_level"),
        "vxn_level": payload.get("vxn_level"),
        "rvx_level": payload.get("rvx_level"),
        "vix_change_1d": payload.get("vix_change_1d"),
        "vix_change_5d": payload.get("vix_change_5d"),
        "vix_change_20d": payload.get("vix_change_20d"),
        "vvix_change_5d": payload.get("vvix_change_5d"),
        "volatility_of_volatility_score": payload.get("volatility_of_volatility_score"),
        "equity_volatility_pressure_score": payload.get("equity_volatility_pressure_score"),
        "nasdaq_volatility_pressure_score": payload.get("nasdaq_volatility_pressure_score"),
        "small_cap_volatility_pressure_score": payload.get("small_cap_volatility_pressure_score"),
        "composite_volatility_stress_score": payload.get("composite_volatility_stress_score"),
        "volatility_regime_label": payload.get("volatility_regime_label"),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report
