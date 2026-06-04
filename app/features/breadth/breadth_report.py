"""Compact dry-run report for breadth observations."""

from __future__ import annotations


def _ratio(numerator, denominator):
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    if denominator == 0:
        return None
    return float(numerator) / float(denominator)


def _participation_label(observation):
    advancers = observation.get("advancers")
    decliners = observation.get("decliners")
    unchanged = observation.get("unchanged")
    breadth_score = observation.get("breadth_score")
    participation_score = observation.get("participation_score")
    total = None
    if isinstance(advancers, int) and isinstance(decliners, int) and isinstance(unchanged, int):
        total = advancers + decliners + unchanged
    if total in (None, 0) or participation_score is None or breadth_score is None:
        return "INSUFFICIENT_DATA"
    advancer_share = advancers / total
    decliner_share = decliners / total
    if advancer_share >= 0.55 and breadth_score > 0.2 and participation_score >= 0.55:
        return "BROAD_STRENGTH"
    if decliner_share >= 0.55 and breadth_score < -0.2 and participation_score <= 0.45:
        return "BROAD_WEAKNESS"
    if breadth_score > 0 and participation_score is not None and participation_score < 0.4:
        return "NARROW_PARTICIPATION"
    if advancer_share >= 0.45 and decliner_share >= 0.2:
        return "MIXED_PARTICIPATION"
    return "MIXED_PARTICIPATION"


def build_breadth_report(observation, writer_result=None):
    payload = dict(observation or {})
    advancers = payload.get("advancers")
    decliners = payload.get("decliners")
    unchanged = payload.get("unchanged")
    advancing_volume = payload.get("advancing_volume")
    declining_volume = payload.get("declining_volume")
    report = {
        "universe": payload.get("universe"),
        "observation_date": payload.get("observation_date"),
        "advancers": advancers,
        "decliners": decliners,
        "unchanged": unchanged,
        "advance_decline_ratio": payload.get("advance_decline_ratio"),
        "advance_decline_line": payload.get("advance_decline_line"),
        "advancing_volume": advancing_volume,
        "declining_volume": declining_volume,
        "new_highs": payload.get("new_highs"),
        "new_lows": payload.get("new_lows"),
        "percent_above_20d": payload.get("percent_above_20d"),
        "percent_above_50d": payload.get("percent_above_50d"),
        "percent_above_100d_ma": payload.get("percent_above_100d_ma"),
        "percent_above_200d": payload.get("percent_above_200d"),
        "breadth_score": payload.get("breadth_score"),
        "participation_score": payload.get("participation_score"),
        "participation_label": _participation_label(payload),
        "advancer_decliner_ratio": _ratio(advancers, decliners),
        "advancing_volume_share": _ratio(advancing_volume, (advancing_volume or 0) + (declining_volume or 0)),
        "declining_volume_share": _ratio(declining_volume, (advancing_volume or 0) + (declining_volume or 0)),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report
