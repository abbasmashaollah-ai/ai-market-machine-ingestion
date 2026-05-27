from __future__ import annotations

from app.normalization.event_calendar import NormalizedEventCalendarRecord, normalize_event_calendar_record, validate_event_calendar_record


DEFAULT_EARNINGS_FIXTURES: tuple[dict[str, object], ...] = (
    {
        "event_id": "EARNINGS-AAPL-2026-07-30",
        "event_type": "earnings_date",
        "event_date": "2026-07-30",
        "event_time": "16:05",
        "timezone": "America/New_York",
        "source": "manual_fixture",
        "symbol": "AAPL",
        "title": "Apple earnings date",
        "importance": "high",
        "notes": "deterministic fixture",
    },
    {
        "event_id": "EARNINGS-MSFT-2026-07-22",
        "event_type": "earnings_date",
        "event_date": "2026-07-22",
        "event_time": None,
        "timezone": "America/New_York",
        "source": "manual_fixture",
        "symbol": "MSFT",
        "title": "Microsoft earnings date",
        "importance": "high",
        "notes": "deterministic fixture",
    },
    {
        "event_id": "EARNINGS-NVDA-2026-08-27",
        "event_type": "earnings_date",
        "event_date": "2026-08-27",
        "event_time": "16:20",
        "timezone": "America/New_York",
        "source": "manual_fixture",
        "symbol": "NVDA",
        "title": "NVIDIA earnings date",
        "importance": "high",
        "notes": "deterministic fixture",
    },
)


def build_earnings_calendar_fixtures() -> tuple[dict[str, object], ...]:
    return DEFAULT_EARNINGS_FIXTURES


def build_earnings_calendar_records(symbols: tuple[str, ...] | None = None) -> tuple[NormalizedEventCalendarRecord, ...]:
    selected_symbols = set(symbols) if symbols else None
    fixtures = build_earnings_calendar_fixtures()
    if selected_symbols is not None:
        fixtures = tuple(record for record in fixtures if record.get("symbol") in selected_symbols)
    return tuple(normalize_event_calendar_record(record) for record in fixtures)


def build_earnings_calendar_validation_results(symbols: tuple[str, ...] | None = None) -> tuple[dict[str, object], ...]:
    records = build_earnings_calendar_records(symbols)
    return tuple(
        {"record": record, "errors": validate_event_calendar_record(record)}
        for record in records
        if validate_event_calendar_record(record)
    )

