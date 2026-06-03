"""Pure event calendar calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime


def _as_date(value: date | datetime | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def normalize_event_type(event_type):
    normalized = str(event_type).strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "EMPLOYMENT": "JOBS",
        "NONFARM_PAYROLLS": "JOBS",
        "NFP": "JOBS",
        "FOMC": "FED",
        "RATE_DECISION": "FED",
        "CPI_RELEASE": "CPI",
        "PCE": "INFLATION",
        "INFLATION": "INFLATION",
        "AUCTION": "TREASURY_AUCTION",
        "OPEX_EXPIRY": "OPEX",
        "HALF_DAY": "HOLIDAY",
        "CLOSE_DUE_TO_HOLIDAY": "HOLIDAY",
    }
    return aliases.get(normalized, normalized)


def normalize_event_impact(impact):
    normalized = str(impact).strip().upper()
    aliases = {
        "LOW": "LOW",
        "MED": "MEDIUM",
        "MEDIUM": "MEDIUM",
        "MODERATE": "MEDIUM",
        "HIGH": "HIGH",
        "CRITICAL": "HIGH",
        "EXTREME": "EXTREME",
    }
    return aliases.get(normalized, normalized)


def filter_events_by_lookahead(events, observation_date, lookahead_days):
    obs = _as_date(observation_date)
    if obs is None:
        return []
    horizon = obs.toordinal() + int(lookahead_days)
    filtered = []
    for event in events:
        event_date = _as_date(event.get("event_date")) if isinstance(event, Mapping) else None
        if event_date is None:
            continue
        if obs.toordinal() <= event_date.toordinal() <= horizon:
            filtered.append(event)
    return filtered


def count_events_by_type(events):
    counts: dict[str, int] = {}
    for event in events:
        if not isinstance(event, Mapping):
            continue
        key = normalize_event_type(event.get("event_type"))
        counts[key] = counts.get(key, 0) + 1
    return counts


def count_high_impact_events(events):
    return sum(1 for event in events if isinstance(event, Mapping) and normalize_event_impact(event.get("impact")) == "HIGH")


def find_next_high_impact_event(events, observation_date):
    obs = _as_date(observation_date)
    if obs is None:
        return None
    candidates = []
    for event in events:
        if not isinstance(event, Mapping):
            continue
        event_date = _as_date(event.get("event_date"))
        if event_date is None or event_date < obs:
            continue
        if normalize_event_impact(event.get("impact")) != "HIGH":
            continue
        candidates.append((event_date, event))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], str(item[1].get("event_id") or "")))
    return candidates[0][1]


def calculate_days_to_event(observation_date, event_date):
    obs = _as_date(observation_date)
    event = _as_date(event_date)
    if obs is None or event is None:
        return None
    return (event - obs).days


def calculate_event_risk_score(events, observation_date, lookahead_days=10):
    filtered = filter_events_by_lookahead(events, observation_date, lookahead_days)
    if not filtered:
        return 0.0
    score = 0.0
    for event in filtered:
        impact = normalize_event_impact(event.get("impact"))
        event_type = normalize_event_type(event.get("event_type"))
        if impact == "HIGH":
            score += 3.0
        elif impact == "MEDIUM":
            score += 1.5
        else:
            score += 0.5
        if event_type in {"FED", "CPI", "PPI", "JOBS", "GDP", "TREASURY_AUCTION", "OPEX"}:
            score += 0.75
        if event_type == "HOLIDAY":
            score += 0.2
    return round(score, 3)


def determine_event_risk_label(event_risk_score=None, high_impact_event_count=None):
    score = _as_float(event_risk_score)
    high_impact = int(high_impact_event_count) if isinstance(high_impact_event_count, int) else None
    if score is None and high_impact is None:
        return "INSUFFICIENT_DATA"
    if (high_impact or 0) == 0 and (score is None or score <= 0.5):
        return "NO_MAJOR_EVENTS"
    if score is not None and score < 3:
        return "LOW_EVENT_RISK"
    if score is not None and score < 7:
        return "MODERATE_EVENT_RISK"
    if score is not None and score < 12:
        return "HIGH_EVENT_RISK"
    return "EXTREME_EVENT_RISK"
