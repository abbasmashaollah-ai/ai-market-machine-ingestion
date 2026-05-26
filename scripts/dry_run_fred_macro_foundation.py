from __future__ import annotations

import argparse

from app.normalization.fred_macro import build_fred_macro_fixture_records, get_starter_fred_macro_series


def _emit(records: tuple[object, ...], *, show_series: bool, show_invalid: bool, invalid_records: tuple[dict[str, object], ...]) -> None:
    print(f"series_count={len(get_starter_fred_macro_series())}")
    print(f"normalized_count={len(records)}")
    print(f"valid_count={len(records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"starter_series={[series.series_id for series in get_starter_fred_macro_series()]}")
    print("no_vendor_calls=True")
    print("no_db_writes=True")
    if show_series:
        print(f"series={[series.series_id for series in get_starter_fred_macro_series()]}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run FRED macro foundation planning.")
    parser.add_argument("--show-series", action="store_true", help="Show starter series IDs.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid fixture records.")
    args = parser.parse_args(argv)

    records = build_fred_macro_fixture_records()
    invalid_records: tuple[dict[str, object], ...] = ()
    _emit(records, show_series=args.show_series, show_invalid=args.show_invalid, invalid_records=invalid_records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
