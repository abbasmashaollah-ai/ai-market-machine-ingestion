from __future__ import annotations

import argparse
import os
from collections import OrderedDict
from datetime import date

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


def _build_query() -> str:
    return (
        "SELECT symbol, timestamp, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp <= %s AND timeframe = %s "
        "ORDER BY timestamp ASC"
    )


def _summarize_rows(rows: list[dict[str, object]]) -> tuple[int, object, object, list[object], list[object]]:
    row_count = len(rows)
    first_timestamp = rows[0].get("timestamp") if rows else None
    last_timestamp = rows[-1].get("timestamp") if rows else None
    adjusted_values = list(OrderedDict.fromkeys(row.get("adjusted") for row in rows))
    sources = list(OrderedDict.fromkeys(row.get("source") for row in rows))
    return row_count, first_timestamp, last_timestamp, adjusted_values, sources


def _format_value(value: object) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[no-any-return]
    return "None" if value is None else str(value)


def _print_summary(*, symbol: str, timeframe: str, start_date: date, end_date: date, rows: list[dict[str, object]]) -> None:
    row_count, first_timestamp, last_timestamp, adjusted_values, sources = _summarize_rows(rows)
    print(
        f"symbol={symbol} "
        f"timeframe={timeframe} "
        f"start_date={start_date.isoformat()} "
        f"end_date={end_date.isoformat()} "
        f"row_count={row_count} "
        f"first_timestamp={_format_value(first_timestamp)} "
        f"last_timestamp={_format_value(last_timestamp)} "
        f"adjusted_values={adjusted_values} "
        f"sources={sources}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify read-only Polygon OHLCV rows in canonical_ohlcv.")
    parser.add_argument("--symbol", required=True, help="Ticker symbol.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    connection = None
    try:
        connection = _open_connection(database_url)
        rows = _fetch_all(
            connection,
            _build_query(),
            (args.symbol, _parse_date(args.start_date), _parse_date(args.end_date), args.timeframe),
        )
        _print_summary(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=_parse_date(args.start_date),
            end_date=_parse_date(args.end_date),
            rows=rows,
        )
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
