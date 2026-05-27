from __future__ import annotations

import argparse

from app.normalization.earnings_calendar import (
    build_earnings_calendar_records,
    build_earnings_calendar_validation_results,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run fixture-backed earnings calendar planning.")
    parser.add_argument("--symbol", action="append", help="Filter to one or more symbols.")
    parser.add_argument("--show-events", action="store_true", help="Show normalized event records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    return parser


def _emit(*, normalized_records, invalid_records, show_events: bool, show_invalid: bool) -> None:
    print(f"event_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"symbols={[record.symbol for record in normalized_records]}")
    print("no_vendor_calls=True")
    print("no_db_reads=True")
    print("no_db_writes=True")
    if show_events:
        print(f"events={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    symbols = tuple(args.symbol) if args.symbol else None
    normalized_records = build_earnings_calendar_records(symbols)
    invalid_records = build_earnings_calendar_validation_results(symbols)
    _emit(
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        show_events=args.show_events,
        show_invalid=args.show_invalid,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

