"""Compact dry-run report for event calendar observations."""

from __future__ import annotations


def build_event_calendar_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "event_risk_label": payload.get("event_risk_label"),
        "event_risk_score": payload.get("event_risk_score"),
        "event_count": payload.get("event_count"),
        "high_impact_event_count": payload.get("high_impact_event_count"),
        "macro_event_count": payload.get("macro_event_count"),
        "earnings_event_count": payload.get("earnings_event_count"),
        "fed_event_count": payload.get("fed_event_count"),
        "inflation_event_count": payload.get("inflation_event_count"),
        "jobs_event_count": payload.get("jobs_event_count"),
        "treasury_event_count": payload.get("treasury_event_count"),
        "opex_event_count": payload.get("opex_event_count"),
        "holiday_event_count": payload.get("holiday_event_count"),
        "next_high_impact_event": payload.get("next_high_impact_event"),
        "days_to_next_high_impact_event": payload.get("days_to_next_high_impact_event"),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report
