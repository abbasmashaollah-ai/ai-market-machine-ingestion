from __future__ import annotations

import argparse

from app.normalization.options import (
    DEFAULT_FIXTURE_RECORDS,
    normalize_options_record,
    validate_options_record,
)


def _build_summary(source_records: tuple[dict[str, object], ...]):
    normalized_records = tuple(normalize_options_record(record) for record in source_records)
    invalid_records = tuple(
        {"record": record, "errors": validate_options_record(record)}
        for record in normalized_records
        if validate_options_record(record)
    )
    return normalized_records, invalid_records


def _emit(*, normalized_records, invalid_records, show_records: bool, show_invalid: bool) -> None:
    print(f"record_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"underlying_symbols={sorted({record.underlying_symbol for record in normalized_records if record.underlying_symbol})}")
    print(f"option_types={sorted({record.option_type for record in normalized_records if record.option_type})}")
    print("no_vendor_calls=True")
    print("no_db_reads=True")
    print("no_db_writes=True")
    if show_records:
        print(f"records={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the options foundation without database writes.")
    parser.add_argument("--underlying-symbol", action="append", help="Filter to one or more underlying symbols.")
    parser.add_argument("--option-type", action="append", help="Filter to one or more option types.")
    parser.add_argument("--show-records", action="store_true", help="Show normalized records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    args = parser.parse_args(argv)

    records = tuple(DEFAULT_FIXTURE_RECORDS)
    if args.underlying_symbol:
        allowed_underlyings = set(args.underlying_symbol)
        records = tuple(record for record in records if record.get("underlying_symbol") in allowed_underlyings)
    if args.option_type:
        allowed_option_types = set(args.option_type)
        records = tuple(record for record in records if record.get("option_type") in allowed_option_types)
    normalized_records, invalid_records = _build_summary(records)
    _emit(
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        show_records=args.show_records,
        show_invalid=args.show_invalid,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
