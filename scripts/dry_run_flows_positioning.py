from __future__ import annotations

import argparse

from app.normalization.flows_positioning import (
    DEFAULT_FIXTURE_RECORDS,
    normalize_flows_positioning_record,
    validate_flows_positioning_record,
)


def _build_summary(source_records: tuple[dict[str, object], ...]):
    normalized_records = tuple(normalize_flows_positioning_record(record) for record in source_records)
    invalid_records = tuple(
        {"record": record, "errors": validate_flows_positioning_record(record)}
        for record in normalized_records
        if validate_flows_positioning_record(record)
    )
    return normalized_records, invalid_records


def _emit(*, normalized_records, invalid_records, show_records: bool, show_invalid: bool) -> None:
    print(f"record_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"record_types={sorted({record.record_type for record in normalized_records if record.record_type})}")
    print(f"symbols={sorted({record.symbol for record in normalized_records if record.symbol})}")
    print(f"asset_classes={sorted({record.asset_class for record in normalized_records if record.asset_class})}")
    print("no_vendor_calls=True")
    print("no_db_reads=True")
    print("no_db_writes=True")
    if show_records:
        print(f"records={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the flows/positioning foundation without database writes.")
    parser.add_argument("--record-type", action="append", help="Filter to one or more record types.")
    parser.add_argument("--symbol", action="append", help="Filter to one or more symbols.")
    parser.add_argument("--asset-class", action="append", help="Filter to one or more asset classes.")
    parser.add_argument("--show-records", action="store_true", help="Show normalized records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    args = parser.parse_args(argv)

    records = tuple(DEFAULT_FIXTURE_RECORDS)
    if args.record_type:
        allowed_record_types = set(args.record_type)
        records = tuple(record for record in records if record.get("record_type") in allowed_record_types)
    if args.symbol:
        allowed_symbols = set(args.symbol)
        records = tuple(record for record in records if record.get("symbol") in allowed_symbols)
    if args.asset_class:
        allowed_asset_classes = set(args.asset_class)
        records = tuple(record for record in records if record.get("asset_class") in allowed_asset_classes)
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
