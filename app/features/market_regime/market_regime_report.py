"""Compact dry-run report for market regime observations."""

from __future__ import annotations


def build_market_regime_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "macro_liquidity_state": payload.get("macro_liquidity_state"),
        "market_risk_state": payload.get("market_risk_state"),
        "breadth_participation_label": payload.get("breadth_participation_label"),
        "sector_rotation_state": payload.get("sector_rotation_state"),
        "cross_asset_state": payload.get("cross_asset_state"),
        "volatility_state": payload.get("volatility_state"),
        "price_states_by_symbol": payload.get("price_states_by_symbol"),
        "liquidity_regime_score": payload.get("liquidity_regime_score"),
        "risk_regime_score": payload.get("risk_regime_score"),
        "participation_regime_score": payload.get("participation_regime_score"),
        "rotation_regime_score": payload.get("rotation_regime_score"),
        "cross_asset_regime_score": payload.get("cross_asset_regime_score"),
        "trend_regime_score": payload.get("trend_regime_score"),
        "volatility_regime_score": payload.get("volatility_regime_score"),
        "composite_market_regime_score": payload.get("composite_market_regime_score"),
        "market_regime_label": payload.get("market_regime_label"),
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

