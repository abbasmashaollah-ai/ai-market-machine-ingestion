from __future__ import annotations

import argparse
import os

from app.normalization.fred_macro import build_fred_macro_fixture_records, get_starter_fred_macro_series
from app.vendors.common.http import UrlLibHttpClient
from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient
from app.vendors.fred_macro import fetch_fred_macro_series
from app.writers.fred_macro_writer import FredMacroWriter


def _load_local_env_if_available() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    return bool(load_dotenv())


def _emit(
    *,
    requested_series: list[str],
    normalized_count: int,
    valid_count: int,
    invalid_count: int,
    latest_observation_dates: dict[str, str | None],
    no_vendor_calls: bool,
    no_db_writes: bool,
    show_series: bool,
    show_values: bool,
    show_invalid: bool,
    invalid_records: tuple[dict[str, object], ...],
    rows_written: int = 0,
    rows_skipped: int = 0,
    write_confirmed: bool = False,
    write_status: str = "DRY_RUN",
    normalized_records: tuple[object, ...] = (),
) -> None:
    print(f"series_count={len(get_starter_fred_macro_series())}")
    print(f"requested_series={requested_series}")
    print(f"normalized_count={normalized_count}")
    print(f"valid_count={valid_count}")
    print(f"invalid_count={invalid_count}")
    print(f"latest_observation_dates={latest_observation_dates}")
    print(f"rows_written={rows_written}")
    print(f"rows_skipped={rows_skipped}")
    print(f"write_confirmed={write_confirmed}")
    print(f"write_status={write_status}")
    print(f"starter_series={[series.series_id for series in get_starter_fred_macro_series()]}")
    print(f"no_vendor_calls={no_vendor_calls}")
    print(f"no_db_writes={no_db_writes}")
    if show_series:
        print(f"series={[series.series_id for series in get_starter_fred_macro_series()]}")
    if show_values:
        print(f"normalized_values={[getattr(record, 'value', None) for record in normalized_records]}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run FRED macro foundation planning.")
    parser.add_argument("--show-series", action="store_true", help="Show starter series IDs.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid fixture records.")
    parser.add_argument("--live-check", action="store_true", help="Fetch live FRED observations.")
    parser.add_argument("--series", action="append", help="Specific series to fetch; defaults to starter series.")
    parser.add_argument("--show-values", action="store_true", help="Show normalized record values.")
    parser.add_argument("--max-observations", type=int, default=None, help="Limit observations per series.")
    parser.add_argument("--confirm-write", action="store_true", help="Write normalized live observations.")
    args = parser.parse_args(argv)

    starter_series = get_starter_fred_macro_series()
    requested_series = [series.upper() for series in args.series] if args.series else [series.series_id for series in starter_series]
    if args.confirm_write and not args.live_check:
        raise RuntimeError("--confirm-write requires --live-check")

    if args.confirm_write and not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is required when --confirm-write is used")

    if args.live_check:
        _load_local_env_if_available()
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise RuntimeError("FRED_API_KEY is required when --live-check is used")
        client = UnsupportedFredClient(FredClientConfig(api_key=api_key), http_client=UrlLibHttpClient())
        requested_definitions = {series.series_id: series for series in starter_series}
        normalized_records = []
        latest_observation_dates: dict[str, str | None] = {}
        invalid_records: list[dict[str, object]] = []
        for series_id in requested_series:
            definition = requested_definitions.get(series_id)
            if definition is None:
                invalid_records.append({"series_id": series_id, "error": "missing_or_unsupported_series"})
                latest_observation_dates[series_id] = None
                continue
            result = fetch_fred_macro_series(client, definition, max_observations=args.max_observations)
            normalized_records.extend(result.records)
            invalid_records.extend(result.invalid_rows)
            latest_observation_dates[series_id] = result.latest_observation_date
        rows_written = 0
        rows_skipped = 0
        write_status = "DRY_RUN"
        no_db_writes = True
        if args.confirm_write and normalized_records:
            writer = FredMacroWriter()
            writer_result = writer.write(list(normalized_records))
            rows_written = writer_result.written_count
            rows_skipped = writer_result.skipped_count
            no_db_writes = False
            writer_status = getattr(getattr(writer_result, "status", None), "value", None)
            if writer_status in (None, "success"):
                if rows_written > 0:
                    write_status = "WRITTEN"
                elif rows_skipped > 0:
                    write_status = "SKIPPED"
                else:
                    write_status = "NO_EFFECT"
            else:
                write_status = "FAILED"
        elif args.confirm_write:
            no_db_writes = False
            write_status = "NO_EFFECT"
        _emit(
            requested_series=requested_series,
            normalized_count=len(normalized_records),
            valid_count=len(normalized_records),
            invalid_count=len(invalid_records),
            latest_observation_dates=latest_observation_dates,
            no_vendor_calls=False,
            no_db_writes=no_db_writes,
            show_series=args.show_series,
            show_values=args.show_values,
            show_invalid=args.show_invalid,
            invalid_records=tuple(invalid_records),
            rows_written=rows_written,
            rows_skipped=rows_skipped,
            write_confirmed=bool(args.confirm_write),
            write_status=write_status,
            normalized_records=tuple(normalized_records),
        )
    else:
        records = build_fred_macro_fixture_records()
        _emit(
            requested_series=requested_series,
            normalized_count=len(records),
            valid_count=len(records),
            invalid_count=0,
            latest_observation_dates={series.series_id: "2026-01-01" for series in starter_series},
            no_vendor_calls=True,
            no_db_writes=True,
            show_series=args.show_series,
            show_values=args.show_values,
            show_invalid=args.show_invalid,
            invalid_records=(),
            rows_written=0,
            rows_skipped=0,
            write_confirmed=False,
            write_status="DRY_RUN",
            normalized_records=records,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
