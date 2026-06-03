"""Compact dry-run report for breadth observations."""

from __future__ import annotations


def build_breadth_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "universe": payload.get("universe"),
        "observation_date": payload.get("observation_date"),
        "advancers": payload.get("advancers"),
        "decliners": payload.get("decliners"),
        "unchanged": payload.get("unchanged"),
        "advancing_volume": payload.get("advancing_volume"),
        "declining_volume": payload.get("declining_volume"),
        "new_highs": payload.get("new_highs"),
        "new_lows": payload.get("new_lows"),
        "percent_above_20d": payload.get("percent_above_20d"),
        "percent_above_50d": payload.get("percent_above_50d"),
        "percent_above_200d": payload.get("percent_above_200d"),
        "breadth_score": payload.get("breadth_score"),
        "participation_score": payload.get("participation_score"),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report
