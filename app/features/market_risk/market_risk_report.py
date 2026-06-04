"""Compact dry-run report for market risk observations."""

from __future__ import annotations


def build_market_risk_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "volatility_state": payload.get("volatility_state"),
        "options_state": payload.get("options_state"),
        "flows_positioning_state": payload.get("flows_positioning_state"),
        "event_calendar_state": payload.get("event_calendar_state"),
        "news_sentiment_state": payload.get("news_sentiment_state"),
        "breadth_participation_label": payload.get("breadth_participation_label"),
        "macro_liquidity_state": payload.get("macro_liquidity_state"),
        "price_states_by_symbol": payload.get("price_states_by_symbol"),
        "volatility_risk_score": payload.get("volatility_risk_score"),
        "options_risk_score": payload.get("options_risk_score"),
        "positioning_risk_score": payload.get("positioning_risk_score"),
        "event_risk_score": payload.get("event_risk_score"),
        "sentiment_risk_score": payload.get("sentiment_risk_score"),
        "breadth_risk_score": payload.get("breadth_risk_score"),
        "macro_liquidity_risk_score": payload.get("macro_liquidity_risk_score"),
        "composite_market_risk_score": payload.get("composite_market_risk_score"),
        "market_risk_label": payload.get("market_risk_label"),
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

