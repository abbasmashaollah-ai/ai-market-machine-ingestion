from __future__ import annotations

import argparse

from app.normalization.event_calendar import NormalizedEventCalendarRecord
from app.normalization.opex_calendar import build_opex_normalized_records, build_opex_validation_results, parse_args


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


def main(argv: list[str] | None = None) -> int:
    normalized_argv = [arg for arg in (argv or []) if arg not in {"--show-events", "--show-invalid"}]
    parser_args = parse_args(normalized_argv)
    flag_parser = argparse.ArgumentParser(add_help=False)
    flag_parser.add_argument("--show-events", action="store_true")
    flag_parser.add_argument("--show-invalid", action="store_true")
    flag_args, _ = flag_parser.parse_known_args(argv)
    normalized_records = build_opex_normalized_records(parser_args.year, parser_args.month)
    invalid_records = build_opex_validation_results(parser_args.year, parser_args.month)
    _emit(
        year=parser_args.year,
        month=parser_args.month,
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        show_events=flag_args.show_events,
        show_invalid=flag_args.show_invalid,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
