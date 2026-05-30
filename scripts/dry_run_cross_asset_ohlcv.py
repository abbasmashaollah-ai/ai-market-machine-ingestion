from __future__ import annotations

import argparse

from app.normalization.cross_asset_ohlcv import (
    DEFAULT_FIXTURE_RECORDS,
    normalize_cross_asset_ohlcv_record,
    validate_cross_asset_ohlcv_record,
)


def _build_summary(source_records: tuple[dict[str, object], ...]):
    normalized_records = tuple(normalize_cross_asset_ohlcv_record(record) for record in source_records)
    invalid_records = tuple(
        {"record": record, "errors": validate_cross_asset_ohlcv_record(record)}
        for record in normalized_records
        if validate_cross_asset_ohlcv_record(record)
    )
    return normalized_records, invalid_records


def _emit(*, normalized_records, invalid_records, show_records: bool, show_invalid: bool) -> None:
    print(f"record_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"asset_groups={sorted({record.asset_group for record in normalized_records if record.asset_group})}")
    print(f"symbols={sorted({record.symbol for record in normalized_records if record.symbol})}")
    print("no_vendor_calls=True")
    print("no_db_reads=True")
    print("no_db_writes=True")
    if show_records:
        print(f"records={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the cross-asset OHLCV foundation without database writes.")
    parser.add_argument("--symbol", action="append", help="Filter to one or more symbols.")
    parser.add_argument("--asset-group", action="append", help="Filter to one or more asset groups.")
    parser.add_argument("--show-records", action="store_true", help="Show normalized records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    args = parser.parse_args(argv)

    records = tuple(DEFAULT_FIXTURE_RECORDS)
    if args.symbol:
        allowed_symbols = set(args.symbol)
        records = tuple(record for record in records if record.get("symbol") in allowed_symbols)
    if args.asset_group:
        allowed_groups = set(args.asset_group)
        records = tuple(record for record in records if record.get("asset_group") in allowed_groups)
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
