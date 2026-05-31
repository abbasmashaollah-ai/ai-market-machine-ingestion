from __future__ import annotations

import argparse

from app.normalization.breadth_participation import (
    DEFAULT_FIXTURE_RECORDS,
    normalize_breadth_participation_record,
    validate_breadth_participation_record,
)


def _build_summary(source_records: tuple[dict[str, object], ...]):
    normalized_records = tuple(normalize_breadth_participation_record(record) for record in source_records)
    invalid_records = tuple(
        {"record": record, "errors": validate_breadth_participation_record(record)}
        for record in normalized_records
        if validate_breadth_participation_record(record)
    )
    return normalized_records, invalid_records


def _emit(*, normalized_records, invalid_records, show_records: bool, show_invalid: bool) -> None:
    print(f"record_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"metric_types={sorted({record.metric_type for record in normalized_records if record.metric_type})}")
    print(f"universes={sorted({record.universe for record in normalized_records if record.universe})}")
    print("no_vendor_calls=True")
    print("no_db_reads=True")
    print("no_db_writes=True")
    if show_records:
        print(f"records={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the breadth/participation foundation without database writes.")
    parser.add_argument("--metric-type", action="append", help="Filter to one or more metric types.")
    parser.add_argument("--universe", action="append", help="Filter to one or more universes.")
    parser.add_argument("--show-records", action="store_true", help="Show normalized records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    args = parser.parse_args(argv)

    records = tuple(DEFAULT_FIXTURE_RECORDS)
    if args.metric_type:
        allowed_metric_types = set(args.metric_type)
        records = tuple(record for record in records if record.get("metric_type") in allowed_metric_types)
    if args.universe:
        allowed_universes = set(args.universe)
        records = tuple(record for record in records if record.get("universe") in allowed_universes)
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
