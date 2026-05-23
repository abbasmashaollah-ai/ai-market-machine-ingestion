from __future__ import annotations

import argparse
import os
from datetime import date, datetime, timedelta, timezone

from app.ingestion.manual.polygon_ohlcv_incremental import _build_polygon_client, _normalize_and_validate
from app.writers.ohlcv_writer import OhlcvWriter
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


def _coverage_query(source_filter: str | None) -> tuple[str, tuple[object, ...]]:
    query = (
        "SELECT symbol, timestamp, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp <= %s AND timeframe = %s"
    )
    params: tuple[object, ...] = ()
    if source_filter is not None:
        query += " AND source = %s"
    query += " ORDER BY timestamp ASC"
    return query, params


def _expected_weekdays(start_date: date, end_date: date) -> list[date]:
    days: list[date] = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def _observed_dates(rows: list[dict[str, object]]) -> list[date]:
    values: list[date] = []
    for row in rows:
        timestamp = row.get("timestamp")
        if hasattr(timestamp, "date"):
            observed = timestamp.date()
            if observed not in values:
                values.append(observed)
    return values


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
) -> None:
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
        f"status={status}"
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
        coverage_query, _ = _coverage_query(args.source_filter)
        params: tuple[object, ...] = (args.symbol, start_date, end_date, args.timeframe)
        if args.source_filter is not None:
            params = params + (args.source_filter,)
        coverage_rows = _fetch_all(connection, coverage_query, params)
        expected_weekdays = _expected_weekdays(start_date, end_date)
        observed = _observed_dates(coverage_rows)
        missing_dates = [day for day in expected_weekdays if day not in observed]
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
        rows_valid = len(normalized)
        rows_written = 0
        status = "planned"
        if args.confirm_write:
            writer = OhlcvWriter(connection)
            if normalized:
                write_result = writer.write(normalized)
                rows_written = write_result.written_count
                status = "completed" if write_result.status.value == "success" else "failed"
            else:
                status = "completed"
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
        )
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
