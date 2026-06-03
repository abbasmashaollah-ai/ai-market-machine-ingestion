"""Validation helpers for event calendar observations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EventCalendarValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class EventCalendarValidationResult:
    is_valid: bool
    errors: tuple[EventCalendarValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


ALLOWED_LABELS = (
    "NO_MAJOR_EVENTS",
    "LOW_EVENT_RISK",
    "MODERATE_EVENT_RISK",
    "HIGH_EVENT_RISK",
    "EXTREME_EVENT_RISK",
    "INSUFFICIENT_DATA",
)


def _is_mapping(value: object) -> bool:
    return isinstance(value, Mapping)


def _is_numeric_or_none(value: object) -> bool:
    return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool))


def validate_event_calendar_observation(row: Mapping[str, object]) -> EventCalendarValidationResult:
    errors: list[EventCalendarValidationError] = []
    required = ("observation_date", "source", "lookahead_days", "events", "event_count", "event_risk_label")
    for field_name in required:
        if field_name not in row:
            errors.append(EventCalendarValidationError(field_name, "field is required"))

    lookahead_days = row.get("lookahead_days")
    if not isinstance(lookahead_days, int) or lookahead_days <= 0:
        errors.append(EventCalendarValidationError("lookahead_days", "lookahead_days must be a positive integer"))

    events = row.get("events")
    if not isinstance(events, list):
        errors.append(EventCalendarValidationError("events", "events must be a list"))

    event_count = row.get("event_count")
    if not isinstance(event_count, int) or event_count < 0:
        errors.append(EventCalendarValidationError("event_count", "event_count must be a non-negative integer"))

    for field_name in (
        "high_impact_event_count",
        "macro_event_count",
        "earnings_event_count",
        "fed_event_count",
        "inflation_event_count",
        "jobs_event_count",
        "treasury_event_count",
        "opex_event_count",
        "holiday_event_count",
    ):
        value = row.get(field_name)
        if not isinstance(value, int) or value < 0:
            errors.append(EventCalendarValidationError(field_name, f"{field_name} must be a non-negative integer"))

    if row.get("event_risk_label") not in ALLOWED_LABELS:
        errors.append(EventCalendarValidationError("event_risk_label", "event_risk_label must be an allowed label"))

    if not _is_numeric_or_none(row.get("event_risk_score")):
        errors.append(EventCalendarValidationError("event_risk_score", "event_risk_score must be numeric or None"))

    if row.get("days_to_next_high_impact_event") is not None and not isinstance(row.get("days_to_next_high_impact_event"), int):
        errors.append(EventCalendarValidationError("days_to_next_high_impact_event", "days_to_next_high_impact_event must be an integer or None"))

    return EventCalendarValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_event_calendar_observations(rows: Sequence[Mapping[str, object]]) -> EventCalendarValidationResult:
    errors: list[EventCalendarValidationError] = []
    seen: set[tuple[object, object]] = set()
    for row in rows:
        result = validate_event_calendar_observation(row)
        errors.extend(result.errors)
        key = (row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(EventCalendarValidationError("observation_date+source", "duplicate batch key"))
        seen.add(key)
    return EventCalendarValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())
