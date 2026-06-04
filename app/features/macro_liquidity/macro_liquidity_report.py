"""Compact dry-run report for macro liquidity observations."""

from __future__ import annotations


def build_macro_liquidity_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "liquidity_rates_state": payload.get("liquidity_rates_state"),
        "cross_asset_state": payload.get("cross_asset_state"),
        "flows_positioning_state": payload.get("flows_positioning_state"),
        "volatility_state": payload.get("volatility_state"),
        "breadth_participation_label": payload.get("breadth_participation_label"),
        "sector_rotation_state": payload.get("sector_rotation_state"),
        "rates_liquidity_pressure_score": payload.get("rates_liquidity_pressure_score"),
        "cross_asset_confirmation_score": payload.get("cross_asset_confirmation_score"),
        "positioning_liquidity_score": payload.get("positioning_liquidity_score"),
        "volatility_liquidity_stress_score": payload.get("volatility_liquidity_stress_score"),
        "participation_confirmation_score": payload.get("participation_confirmation_score"),
        "composite_macro_liquidity_score": payload.get("composite_macro_liquidity_score"),
        "macro_liquidity_label": payload.get("macro_liquidity_label"),
        "source": payload.get("source"),
        "quality_status": payload.get("quality_status"),
        "certification_status": payload.get("certification_status"),
        "freshness_status": payload.get("freshness_status"),
        "lineage": payload.get("lineage"),
        "evidence": payload.get("evidence"),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report

