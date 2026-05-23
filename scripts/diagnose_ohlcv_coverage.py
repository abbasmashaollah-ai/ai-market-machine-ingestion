from __future__ import annotations

import argparse
import os
from datetime import date, timedelta

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


def _build_query(source: str | None) -> tuple[str, tuple[object, ...]]:
    base = (
        "SELECT symbol, timestamp, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp <= %s AND timeframe = %s"
    )
    if source is not None:
        base += " AND source = %s"
    base += " ORDER BY timestamp ASC"
    return base, ()


def _expected_weekdays(start_date: date, end_date: date) -> list[date]:
    days: list[date] = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def _format_date_list(values: list[date]) -> str:
    return "[" + ", ".join(value.isoformat() for value in values) + "]" if values else "[]"


def _ordered_unique(values: list[object]) -> list[object]:
    seen: list[object] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return seen


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
    rows: list[dict[str, object]],
) -> None:
    expected_weekdays = _expected_weekdays(start_date, end_date)
    observed_dates = _ordered_unique([
        row.get("timestamp").date() if hasattr(row.get("timestamp"), "date") else row.get("timestamp")
        for row in rows
        if row.get("timestamp") is not None
    ])
    observed_dates = [value for value in observed_dates if isinstance(value, date)]
    missing_weekdays = [day for day in expected_weekdays if day not in observed_dates]
    coverage_ratio = (len(observed_dates) / len(expected_weekdays)) if expected_weekdays else 0.0
    sources = _ordered_unique([row.get("source") for row in rows])
    adjusted_values = _ordered_unique([row.get("adjusted") for row in rows])
    first_timestamp = rows[0].get("timestamp") if rows else None
    last_timestamp = rows[-1].get("timestamp") if rows else None
    print(
        f"symbol={symbol} "
        f"timeframe={timeframe} "
        f"start_date={start_date.isoformat()} "
        f"end_date={end_date.isoformat()} "
        f"source_filter={source_filter if source_filter is not None else 'None'} "
        f"expected_weekdays={len(expected_weekdays)} "
        f"observed_dates={_format_date_list(observed_dates)} "
        f"missing_weekdays={_format_date_list(missing_weekdays)} "
        f"coverage_ratio={coverage_ratio:.3f} "
        f"first_timestamp={_format_value(first_timestamp)} "
        f"last_timestamp={_format_value(last_timestamp)} "
        f"sources={sources} "
        f"adjusted_values={adjusted_values}"
    )
    sample_limit = 5
    for index, day in enumerate(missing_weekdays[:sample_limit], start=1):
        print(f"sample_missing_date_{index}={day.isoformat()}")
    if len(missing_weekdays) > sample_limit:
        print(f"sample_missing_dates_truncated={len(missing_weekdays) - sample_limit}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose weekday coverage for canonical_ohlcv.")
    parser.add_argument("--symbol", required=True, help="Ticker symbol.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source", help="Optional source filter.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    query, _ = _build_query(args.source)
    params: tuple[object, ...] = (args.symbol, start_date, end_date, args.timeframe) + ((args.source,) if args.source is not None else ())

    connection = None
    try:
        connection = _open_connection(database_url)
        rows = _fetch_all(connection, query, params)
        _print_summary(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=start_date,
            end_date=end_date,
            source_filter=args.source,
            rows=rows,
        )
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
