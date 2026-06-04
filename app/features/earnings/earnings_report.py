"""Compact dry-run report for earnings observations."""

from __future__ import annotations


def build_earnings_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "symbol": payload.get("symbol"),
        "observation_date": payload.get("observation_date"),
        "earnings_date": payload.get("earnings_date"),
        "days_to_earnings": payload.get("days_to_earnings"),
        "days_since_earnings": payload.get("days_since_earnings"),
        "eps_surprise_score": payload.get("eps_surprise_score"),
        "revenue_surprise_score": payload.get("revenue_surprise_score"),
        "guidance_score": payload.get("guidance_score"),
        "estimate_revision_score": payload.get("estimate_revision_score"),
        "pre_earnings_drift_score": payload.get("pre_earnings_drift_score"),
        "post_earnings_reaction_score": payload.get("post_earnings_reaction_score"),
        "implied_vs_actual_move_score": payload.get("implied_vs_actual_move_score"),
        "earnings_quality_score": payload.get("earnings_quality_score"),
        "earnings_risk_score": payload.get("earnings_risk_score"),
        "earnings_regime_label": payload.get("earnings_regime_label"),
        "source": payload.get("source"),
        "source_attribution": payload.get("source_attribution"),
        "dataset_version": payload.get("dataset_version"),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report

