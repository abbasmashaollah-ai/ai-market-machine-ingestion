from __future__ import annotations

import argparse
import calendar
from datetime import date, time

from app.normalization.event_calendar import NormalizedEventCalendarRecord, normalize_event_calendar_record, validate_event_calendar_record


def _third_friday(year: int, month: int) -> date:
    month_days = calendar.monthcalendar(year, month)
    fridays = [week[calendar.FRIDAY] for week in month_days if week[calendar.FRIDAY] != 0]
    return date(year, month, fridays[2])


def build_opex_event_calendar_candidates(year: int, month: int | None = None) -> tuple[dict[str, object], ...]:
    months = (month,) if month is not None else tuple(range(1, 13))
    events: list[dict[str, object]] = []
    for current_month in months:
        event_date = _third_friday(year, current_month)
        events.append(
            {
                "event_id": f"OPEX-{event_date.isoformat()}",
                "event_type": "OPEX",
                "event_date": event_date.isoformat(),
                "event_time": "16:00",
                "timezone": "America/New_York",
                "source": "manual_rule",
                "symbol": None,
                "title": "Options Expiration",
                "importance": "high",
                "notes": "deterministic third-Friday rule",
            }
        )
    return tuple(events)


def build_opex_normalized_records(year: int, month: int | None = None) -> tuple[NormalizedEventCalendarRecord, ...]:
    return tuple(normalize_event_calendar_record(record) for record in build_opex_event_calendar_candidates(year, month))


def build_opex_validation_results(year: int, month: int | None = None) -> tuple[dict[str, object], ...]:
    normalized_records = build_opex_normalized_records(year, month)
    return tuple(
        {"record": record, "errors": validate_event_calendar_record(record)}
        for record in normalized_records
        if validate_event_calendar_record(record)
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan deterministic OPEX event-calendar candidates.")
    parser.add_argument("--year", type=int, required=True, help="Year to generate OPEX candidates for.")
    parser.add_argument("--month", type=int, choices=range(1, 13), help="Optional month to generate a single OPEX candidate.")
    return parser.parse_args(argv)

