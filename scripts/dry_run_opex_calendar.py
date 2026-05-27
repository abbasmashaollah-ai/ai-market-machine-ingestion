from __future__ import annotations

import argparse

from app.normalization.event_calendar import NormalizedEventCalendarRecord
from app.normalization.opex_calendar import build_opex_normalized_records, build_opex_validation_results


def _emit(
    *,
    year: int,
    month: int | None,
    normalized_records: tuple[NormalizedEventCalendarRecord, ...],
    invalid_records: tuple[dict[str, object], ...],
    show_events: bool,
    show_invalid: bool,
) -> None:
    print(f"event_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"year={year}")
    print(f"month={month if month is not None else 'all'}")
    print("no_vendor_calls=True")
    print("no_db_writes=True")
    if show_events:
        print(f"events={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan deterministic OPEX event-calendar candidates.")
    parser.add_argument("--year", type=int, required=True, help="Year to generate OPEX candidates for.")
    parser.add_argument("--month", type=int, choices=range(1, 13), help="Optional month to generate a single OPEX candidate.")
    parser.add_argument("--show-events", action="store_true", help="Show normalized event records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    normalized_records = build_opex_normalized_records(args.year, args.month)
    invalid_records = build_opex_validation_results(args.year, args.month)
    _emit(
        year=args.year,
        month=args.month,
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        show_events=args.show_events,
        show_invalid=args.show_invalid,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
