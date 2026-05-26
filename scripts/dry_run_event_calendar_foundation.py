from __future__ import annotations

import argparse

from app.normalization.event_calendar import (
    STARTER_EVENT_TYPES,
    NormalizedEventCalendarRecord,
    normalize_event_calendar_record,
    validate_event_calendar_record,
)


DEFAULT_SAMPLE_EVENTS: tuple[dict[str, object], ...] = (
    {"event_id": "cpi-2026-05-21", "event_type": "CPI", "event_date": "2026-05-21", "event_time": "08:30", "timezone": "America/New_York", "source": "manual_fixture", "title": "Consumer Price Index", "importance": "high", "notes": "deterministic fixture"},
    {"event_id": "fomc-2026-06-17", "event_type": "FOMC", "event_date": "2026-06-17", "event_time": "14:00", "timezone": "America/New_York", "source": "manual_fixture", "title": "FOMC Statement", "importance": "high", "notes": "deterministic fixture"},
    {"event_id": "nfp-2026-06-05", "event_type": "NFP", "event_date": "2026-06-05", "event_time": "08:30", "timezone": "America/New_York", "source": "manual_fixture", "title": "Non-Farm Payrolls", "importance": "high", "notes": "deterministic fixture"},
    {"event_id": "opex-2026-06-19", "event_type": "OPEX", "event_date": "2026-06-19", "event_time": "16:00", "timezone": "America/New_York", "source": "manual_fixture", "title": "Options Expiration", "importance": "medium", "notes": "deterministic fixture"},
    {"event_id": "earnings-aapl-2026-06-01", "event_type": "earnings_date", "event_date": "2026-06-01", "event_time": None, "timezone": "America/New_York", "source": "manual_fixture", "symbol": "AAPL", "title": "Apple earnings date", "importance": "medium", "notes": "deterministic fixture"},
)


def _build_summary(source_records: tuple[dict[str, object], ...]) -> tuple[tuple[NormalizedEventCalendarRecord, ...], tuple[dict[str, object], ...]]:
    normalized_records = tuple(normalize_event_calendar_record(record) for record in source_records)
    invalid_records = tuple(
        {"record": record, "errors": validate_event_calendar_record(record)}
        for record in normalized_records
        if validate_event_calendar_record(record)
    )
    return normalized_records, invalid_records


def _emit(*, normalized_records: tuple[NormalizedEventCalendarRecord, ...], invalid_records: tuple[dict[str, object], ...], show_events: bool, show_invalid: bool) -> None:
    print(f"event_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"event_types={[record.event_type for record in normalized_records]}")
    print("no_vendor_calls=True")
    print("no_db_writes=True")
    if show_events:
        print(f"events={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the event calendar foundation without database writes.")
    parser.add_argument("--show-events", action="store_true", help="Show normalized event records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    parser.add_argument("--event-type", action="append", help="Filter to one or more event types.")
    args = parser.parse_args(argv)

    selected_event_types = [event_type for event_type in args.event_type] if args.event_type else list(STARTER_EVENT_TYPES)
    records = tuple(record for record in DEFAULT_SAMPLE_EVENTS if record.get("event_type") in selected_event_types)
    normalized_records, invalid_records = _build_summary(records)
    _emit(
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        show_events=args.show_events,
        show_invalid=args.show_invalid,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
