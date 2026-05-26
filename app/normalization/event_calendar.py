from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class NormalizedEventCalendarRecord:
    event_id: str | None
    event_type: str | None
    event_date: date | None
    event_time: time | None
    timezone: str | None
    source: str | None
    symbol: str | None = None
    title: str | None = None
    importance: str | None = None
    notes: str | None = None


STARTER_EVENT_TYPES: tuple[str, ...] = ("CPI", "FOMC", "NFP", "OPEX", "earnings_date")


def normalize_event_calendar_record(payload: dict[str, object]) -> NormalizedEventCalendarRecord:
    event_date_value = payload.get("event_date")
    if isinstance(event_date_value, date):
        event_date = event_date_value
    elif isinstance(event_date_value, str) and event_date_value:
        event_date = date.fromisoformat(event_date_value)
    else:
        event_date = None

    event_time_value = payload.get("event_time")
    if isinstance(event_time_value, time):
        event_time = event_time_value
    elif isinstance(event_time_value, str) and event_time_value:
        parts = event_time_value.split(":")
        event_time = time(int(parts[0]), int(parts[1])) if len(parts) >= 2 else None
    else:
        event_time = None

    return NormalizedEventCalendarRecord(
        event_id=payload.get("event_id") if isinstance(payload.get("event_id"), str) else None,
        event_type=payload.get("event_type") if isinstance(payload.get("event_type"), str) else None,
        event_date=event_date,
        event_time=event_time,
        timezone=payload.get("timezone") if isinstance(payload.get("timezone"), str) else None,
        source=payload.get("source") if isinstance(payload.get("source"), str) else None,
        symbol=payload.get("symbol") if isinstance(payload.get("symbol"), str) else None,
        title=payload.get("title") if isinstance(payload.get("title"), str) else None,
        importance=payload.get("importance") if isinstance(payload.get("importance"), str) else None,
        notes=payload.get("notes") if isinstance(payload.get("notes"), str) else None,
    )


def validate_event_calendar_record(record: NormalizedEventCalendarRecord) -> list[str]:
    errors: list[str] = []
    if not record.event_id:
        errors.append("event_id is required")
    if not record.event_type:
        errors.append("event_type is required")
    if record.event_date is None:
        errors.append("event_date is required")
    if not record.timezone:
        errors.append("timezone is required")
    if not record.source:
        errors.append("source is required")
    if not record.title:
        errors.append("title is required")
    if not record.importance:
        errors.append("importance is required")
    return errors
