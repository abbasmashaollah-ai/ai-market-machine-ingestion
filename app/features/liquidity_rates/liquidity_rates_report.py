"""Compact dry-run report for liquidity/rates observations."""

from __future__ import annotations


def build_liquidity_rates_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "liquidity_regime_label": payload.get("liquidity_regime_label"),
        "short_rate_pressure_score": payload.get("short_rate_pressure_score"),
        "long_rate_pressure_score": payload.get("long_rate_pressure_score"),
        "yield_curve_slope": payload.get("yield_curve_slope"),
        "yield_curve_pressure_score": payload.get("yield_curve_pressure_score"),
        "real_yield_pressure_score": payload.get("real_yield_pressure_score"),
        "dollar_liquidity_pressure_score": payload.get("dollar_liquidity_pressure_score"),
        "credit_liquidity_score": payload.get("credit_liquidity_score"),
        "equity_liquidity_confirmation_score": payload.get("equity_liquidity_confirmation_score"),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report