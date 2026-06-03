"""Build JSON-friendly event calendar observations from fixture events."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime, timezone

from app.features.event_calendar.event_calendar_engine import (
    calculate_days_to_event,
    calculate_event_risk_score,
    count_events_by_type,
    count_high_impact_events,
    determine_event_risk_label,
    filter_events_by_lookahead,
    find_next_high_impact_event,
    normalize_event_type,
)


def _normalize_date(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _metadata_dict(metadata: Mapping[str, object] | None) -> dict[str, object]:
    result = dict(metadata or {})
    result.setdefault("quality_status", "PENDING")
    result.setdefault("certification_status", "PENDING")
    result.setdefault("freshness_status", "PENDING")
    result.setdefault("lineage", {})
    result.setdefault("evidence", {})
    return result


def build_event_calendar_observation(events, observation_date, timestamp=None, lookahead_days=10, source="fixture_event_calendar"):
    event_rows = [dict(event) for event in events or [] if isinstance(event, Mapping)]
    filtered_events = filter_events_by_lookahead(event_rows, observation_date, lookahead_days)
    event_count = len(filtered_events)
    type_counts = count_events_by_type(filtered_events)
    high_impact_event_count = count_high_impact_events(filtered_events)
    next_high_impact_event = find_next_high_impact_event(filtered_events, observation_date)
    next_high_impact_event_payload = dict(next_high_impact_event) if isinstance(next_high_impact_event, Mapping) else None
    days_to_next_high_impact_event = None
    if next_high_impact_event_payload is not None:
        days_to_next_high_impact_event = calculate_days_to_event(observation_date, next_high_impact_event_payload.get("event_date"))
    event_risk_score = calculate_event_risk_score(filtered_events, observation_date, lookahead_days=lookahead_days)
    event_risk_label = determine_event_risk_label(event_risk_score=event_risk_score, high_impact_event_count=high_impact_event_count)

    payload = {
        "observation_date": _normalize_date(observation_date),
        "timestamp": _normalize_date(timestamp),
        "lookahead_days": int(lookahead_days),
        "events": filtered_events,
        "event_count": event_count,
        "high_impact_event_count": high_impact_event_count,
        "macro_event_count": sum(type_counts.get(event_type, 0) for event_type in ("FED", "CPI", "PPI", "JOBS", "GDP", "TREASURY_AUCTION")),
        "earnings_event_count": type_counts.get("EARNINGS", 0),
        "fed_event_count": type_counts.get("FED", 0),
        "inflation_event_count": type_counts.get("CPI", 0) + type_counts.get("PPI", 0) + type_counts.get("INFLATION", 0),
        "jobs_event_count": type_counts.get("JOBS", 0),
        "treasury_event_count": type_counts.get("TREASURY_AUCTION", 0),
        "opex_event_count": type_counts.get("OPEX", 0),
        "holiday_event_count": type_counts.get("HOLIDAY", 0),
        "next_high_impact_event": next_high_impact_event_payload,
        "days_to_next_high_impact_event": days_to_next_high_impact_event,
        "event_risk_score": event_risk_score,
        "event_risk_label": event_risk_label,
        "source": source,
    }
    metadata = _metadata_dict(None)
    payload.update(
        {
            "quality_status": metadata["quality_status"],
            "certification_status": metadata["certification_status"],
            "freshness_status": metadata["freshness_status"],
            "lineage": metadata["lineage"],
            "evidence": metadata["evidence"],
        }
    )
    return payload
