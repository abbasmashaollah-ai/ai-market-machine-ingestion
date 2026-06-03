"""Report helpers for fundamentals dry-run outputs."""

from __future__ import annotations


def build_fundamental_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "symbol": payload.get("symbol"),
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "growth_score": payload.get("growth_score"),
        "profitability_score": payload.get("profitability_score"),
        "balance_sheet_score": payload.get("balance_sheet_score"),
        "valuation_score": payload.get("valuation_score"),
        "cash_flow_score": payload.get("cash_flow_score"),
        "composite_fundamental_score": payload.get("composite_fundamental_score"),
        "fundamental_quality_label": payload.get("fundamental_quality_label"),
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
