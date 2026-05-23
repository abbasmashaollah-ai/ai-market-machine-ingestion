from __future__ import annotations

import argparse
import os
from datetime import date, datetime, timedelta, timezone

from app.market_calendar.us_market_calendar import expected_trading_days
from app.ingestion.manual.polygon_ohlcv_incremental import _build_polygon_client, _normalize_and_validate
from app.writers.ohlcv_writer import OhlcvWriter
from scripts.diagnose_ohlcv_coverage import calculate_coverage
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _use_cursor(connection: object) -> bool:
    return hasattr(connection, "cursor") and not hasattr(connection, "execute")


def _fetch_all(connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    cursor = None
    try:
        if _use_cursor(connection):
            cursor = connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        else:
            result = connection.execute(sql, params)  # type: ignore[call-arg]
            rows = result.fetchall() if hasattr(result, "fetchall") else []
        if not rows:
            return []
        first = rows[0]
        if isinstance(first, dict):
            return [row for row in rows if isinstance(row, dict)]
        columns = [desc[0] for desc in getattr(cursor, "description", [])] if cursor is not None else []
        return [dict(zip(columns, row)) for row in rows]
    finally:
        if cursor is not None and hasattr(cursor, "close"):
            cursor.close()


def _coverage_query(source_filter: str | None) -> str:
    query = (
        "SELECT symbol, timestamp, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp < %s AND timeframe = %s"
    )
    if source_filter is not None:
        query += " AND source = %s"
    query += " ORDER BY timestamp ASC"
    return query


def _exclusive_end_date(end_date: date) -> date:
    return end_date + timedelta(days=1)


def _expected_weekdays(start_date: date, end_date: date) -> list[date]:
    return expected_trading_days(start_date, end_date)


def _observed_dates(rows: list[dict[str, object]]) -> list[date]:
    values: list[date] = []
    for row in rows:
        timestamp = row.get("timestamp")
        if hasattr(timestamp, "date"):
            observed = timestamp.date()
            if observed not in values:
                values.append(observed)
    return values


def _normalize_observed_dates(rows: list[dict[str, object]]) -> list[date]:
    return _observed_dates(rows)


def _format_dates(values: list[date]) -> str:
    return "[" + ", ".join(value.isoformat() for value in values) + "]" if values else "[]"


def _format_value(value: object) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[no-any-return]
    return "None" if value is None else str(value)


def _print_summary(
    *,
    symbol: str,
    timeframe: str,
    start_date: date,
    end_date: date,
    source_filter: str | None,
    missing_dates: list[date],
    rows_fetched: int,
    rows_valid: int,
    rows_written: int,
    validation_failures: int,
    write_confirmed: bool,
    status: str,
    fetched_dates: list[date] | None = None,
    writable_dates: list[date] | None = None,
    rows_filtered_out: int | None = None,
    remaining_missing_dates_count: int | None = None,
) -> None:
    extras = ""
    if missing_dates is not None:
        extras += f" missing_dates={_format_dates(missing_dates)}"
    if fetched_dates is not None:
        extras += f" fetched_dates={_format_dates(fetched_dates)}"
    if writable_dates is not None:
        extras += f" writable_dates={_format_dates(writable_dates)}"
    if rows_filtered_out is not None:
        extras += f" rows_filtered_out={rows_filtered_out}"
    if remaining_missing_dates_count is not None:
        extras += f" remaining_missing_dates_count={remaining_missing_dates_count}"
    print(
        f"symbol={symbol} "
        f"timeframe={timeframe} "
        f"start_date={start_date.isoformat()} "
        f"end_date={end_date.isoformat()} "
        f"source_filter={source_filter if source_filter is not None else 'None'} "
        f"missing_dates_count={len(missing_dates)} "
        f"rows_fetched={rows_fetched} "
        f"rows_valid={rows_valid} "
        f"rows_written={rows_written} "
        f"validation_failures={validation_failures} "
        f"write_confirmed={str(write_confirmed).lower()} "
        f"status={status}{extras}"
    )


def _build_gap_filled_records(
    *,
    symbol: str,
    timeframe: str,
    raw_records: list[dict[str, object]],
    missing_dates: list[date],
) -> tuple[list[object], int, int]:
    allowed = set(missing_dates)
    filtered = []
    for row in raw_records:
        timestamp = row.get("t")
        if timestamp is None:
            continue
        try:
            observed_date = datetime.fromtimestamp(float(timestamp) / 1000.0, tz=timezone.utc).date()
        except Exception:
            continue
        if observed_date in allowed:
            filtered.append(row)
    normalized, invalid, validation_failures = _normalize_and_validate(symbol, filtered, timeframe)
    return normalized, invalid, validation_failures


def _canonical_date_from_record(record: object) -> date | None:
    timestamp = getattr(record, "timestamp", None)
    if isinstance(timestamp, datetime):
        return timestamp.date()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Fill missing weekday Polygon OHLCV rows in canonical_ohlcv.")
    parser.add_argument("--symbol", required=True, help="Ticker symbol.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source-filter", default="polygon_aggregates", help="Coverage source filter, default polygon_aggregates.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write valid rows.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    connection = None
    writer = None
    try:
        connection = _open_connection(database_url)
        coverage_query = _coverage_query(args.source_filter)
        params = (args.symbol, start_date, _exclusive_end_date(end_date), args.timeframe)
        if args.source_filter is not None:
            params = params + (args.source_filter,)
        coverage_rows = _fetch_all(connection, coverage_query, params)
        coverage = calculate_coverage(rows=coverage_rows, start_date=start_date, end_date=end_date)
        missing_dates = list(coverage["missing_weekdays"])
        if not missing_dates:
            _print_summary(
                symbol=args.symbol,
                timeframe=args.timeframe,
                start_date=start_date,
                end_date=end_date,
                source_filter=args.source_filter,
                missing_dates=[],
                rows_fetched=0,
                rows_valid=0,
                rows_written=0,
                validation_failures=0,
                write_confirmed=args.confirm_write,
                status="skipped_no_gaps",
            )
            return 0

        polygon_api_key = os.getenv("POLYGON_API_KEY")
        if not polygon_api_key:
            raise RuntimeError("POLYGON_API_KEY is required when gap fill needs vendor fetch")

        client = _build_polygon_client(polygon_api_key)
        raw_records = client.fetch_aggregates_raw(args.symbol, start_date.isoformat(), end_date.isoformat())
        normalized, rows_invalid, validation_failures = _build_gap_filled_records(
            symbol=args.symbol,
            timeframe=args.timeframe,
            raw_records=raw_records,
            missing_dates=missing_dates,
        )
        fetched_dates = _observed_dates(
            [
                {"timestamp": datetime.fromtimestamp(float(row.get("t")) / 1000.0, tz=timezone.utc)}
                for row in raw_records
                if row.get("t") is not None
            ]
        )
        writable_dates = [_canonical_date_from_record(record) for record in normalized]
        writable_dates = [day for day in writable_dates if day is not None]
        rows_valid = len(normalized)
        rows_written = 0
        status = "planned"
        remaining_missing_dates_count = len(missing_dates)
        if args.confirm_write:
            writer = OhlcvWriter(connection)
            if normalized:
                write_result = writer.write(normalized)
                rows_written = write_result.written_count
                if write_result.status.value == "success":
                    post_coverage_rows = _fetch_all(connection, coverage_query, params)
                    post_coverage = calculate_coverage(rows=post_coverage_rows, start_date=start_date, end_date=end_date)
                    remaining_missing_dates_count = len(post_coverage["missing_weekdays"])
                    status = "completed" if remaining_missing_dates_count == 0 else "partial_fill"
                else:
                    status = "failed"
            else:
                status = "partial_fill" if remaining_missing_dates_count > 0 else "completed"
        _print_summary(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=start_date,
            end_date=end_date,
            source_filter=args.source_filter,
            missing_dates=missing_dates,
            rows_fetched=len(raw_records),
            rows_valid=rows_valid,
            rows_written=rows_written,
            validation_failures=validation_failures + rows_invalid,
            write_confirmed=args.confirm_write,
            status=status,
            fetched_dates=fetched_dates,
            writable_dates=writable_dates,
            rows_filtered_out=max(0, len(raw_records) - len(normalized)),
            remaining_missing_dates_count=remaining_missing_dates_count if args.confirm_write else None,
        )
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
