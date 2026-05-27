from __future__ import annotations

import argparse

from app.normalization.event_calendar import NormalizedEventCalendarRecord
from app.normalization.macro_event_calendar import (
    build_macro_event_calendar_records,
    build_macro_event_calendar_validation_results,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run fixture-backed macro event calendar planning.")
    parser.add_argument("--event-type", action="append", help="Filter to one or more event types.")
    parser.add_argument("--show-events", action="store_true", help="Show normalized event records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    return parser


def _emit(
    *,
    normalized_records: tuple[NormalizedEventCalendarRecord, ...],
    invalid_records: tuple[dict[str, object], ...],
    show_events: bool,
    show_invalid: bool,
) -> None:
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
    args = build_parser().parse_args(argv)
    event_types = tuple(args.event_type) if args.event_type else None
    normalized_records = build_macro_event_calendar_records(event_types)
    invalid_records = build_macro_event_calendar_validation_results(event_types)
    _emit(
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        show_events=args.show_events,
        show_invalid=args.show_invalid,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
