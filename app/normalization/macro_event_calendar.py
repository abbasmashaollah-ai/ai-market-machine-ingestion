from __future__ import annotations

from app.normalization.event_calendar import NormalizedEventCalendarRecord, normalize_event_calendar_record, validate_event_calendar_record


DEFAULT_MACRO_EVENT_FIXTURES: tuple[dict[str, object], ...] = (
    {
        "event_id": "CPI-2026-06-11",
        "event_type": "CPI",
        "event_date": "2026-06-11",
        "event_time": "08:30",
        "timezone": "America/New_York",
        "source": "manual_fixture",
        "title": "Consumer Price Index",
        "importance": "high",
        "notes": "deterministic fixture",
    },
    {
        "event_id": "FOMC-2026-06-17",
        "event_type": "FOMC",
        "event_date": "2026-06-17",
        "event_time": "14:00",
        "timezone": "America/New_York",
        "source": "manual_fixture",
        "title": "FOMC Statement",
        "importance": "high",
        "notes": "deterministic fixture",
    },
    {
        "event_id": "NFP-2026-06-05",
        "event_type": "NFP",
        "event_date": "2026-06-05",
        "event_time": "08:30",
        "timezone": "America/New_York",
        "source": "manual_fixture",
        "title": "Non-Farm Payrolls",
        "importance": "high",
        "notes": "deterministic fixture",
    },
)


def build_macro_event_calendar_fixtures() -> tuple[dict[str, object], ...]:
    return DEFAULT_MACRO_EVENT_FIXTURES


def build_macro_event_calendar_records(event_types: tuple[str, ...] | None = None) -> tuple[NormalizedEventCalendarRecord, ...]:
    selected_types = set(event_types) if event_types else None
    fixtures = build_macro_event_calendar_fixtures()
    if selected_types is not None:
        fixtures = tuple(record for record in fixtures if record.get("event_type") in selected_types)
    return tuple(normalize_event_calendar_record(record) for record in fixtures)


def build_macro_event_calendar_validation_results(event_types: tuple[str, ...] | None = None) -> tuple[dict[str, object], ...]:
    records = build_macro_event_calendar_records(event_types)
    return tuple(
        {"record": record, "errors": validate_event_calendar_record(record)}
        for record in records
        if validate_event_calendar_record(record)
    )

