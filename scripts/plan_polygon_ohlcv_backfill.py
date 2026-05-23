from __future__ import annotations

import argparse
import os
from datetime import date, datetime, timedelta

from app.market_calendar.us_market_calendar import expected_trading_days
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


DEFAULT_SYMBOLS = ("SPY", "QQQ", "IWM")


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


def _exclusive_end_date(end_date: date) -> date:
    return end_date + timedelta(days=1)


def _build_coverage_query() -> str:
    return (
        "SELECT timestamp, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp < %s AND timeframe = %s "
        "ORDER BY timestamp ASC"
    )


def _observed_dates(rows: list[dict[str, object]]) -> list[date]:
    observed: list[date] = []
    for row in rows:
        timestamp = row.get("timestamp")
        if isinstance(timestamp, datetime):
            value = timestamp.date()
            if value not in observed:
                observed.append(value)
            continue
        if isinstance(timestamp, date):
            value = timestamp
            if value not in observed:
                observed.append(value)
            continue
        if hasattr(timestamp, "date"):
            value = timestamp.date()
            if value not in observed:
                observed.append(value)
    return observed


def _format_dates(values: list[date]) -> str:
    return "[" + ", ".join(value.isoformat() for value in values) + "]" if values else "[]"


def _parse_adjusted_filter(value: str | None) -> bool | None:
    if value is None or value == "all":
        return None
    normalized = value.lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError("--adjusted must be true, false, or all")


def _coverage_for_symbol(
    *,
    rows: list[dict[str, object]],
    expected_dates: list[date],
    source_filter: str | None,
    adjusted_filter: bool | None,
) -> tuple[list[date], list[date]]:
    observed: set[date] = set()
    for row in rows:
        row_source = row.get("source")
        row_adjusted = row.get("adjusted")
        if source_filter is not None and row_source != source_filter:
            continue
        if adjusted_filter is not None and row_adjusted is not adjusted_filter:
            continue
        timestamp = row.get("timestamp")
        if isinstance(timestamp, datetime):
            observed.add(timestamp.date())
        elif isinstance(timestamp, date):
            observed.add(timestamp)
        elif hasattr(timestamp, "date"):
            observed.add(timestamp.date())
    missing_dates = [day for day in expected_dates if day not in observed]
    present_dates = [day for day in expected_dates if day in observed]
    return present_dates, missing_dates


def _print_symbol_summary(
    *,
    symbol: str,
    timeframe: str,
    start_date: date,
    end_date: date,
    expected_rows: int,
    existing_dates: list[date] | None,
    missing_dates: list[date] | None,
    source_filter: str | None,
    adjusted_filter: bool | None,
) -> None:
    extras = ""
    if existing_dates is not None:
        extras += f" per_symbol_existing_dates={_format_dates(existing_dates)}"
    if missing_dates is not None:
        extras += f" per_symbol_missing_dates={_format_dates(missing_dates)}"
        extras += f" per_symbol_missing_rows={len(missing_dates)}"
    print(
        f"symbol={symbol} "
        f"timeframe={timeframe} "
        f"start_date={start_date.isoformat()} "
        f"end_date={end_date.isoformat()} "
        f"source_filter={source_filter if source_filter is not None else 'None'} "
        f"adjusted_filter={adjusted_filter if adjusted_filter is not None else 'all'} "
        f"per_symbol_expected_rows={expected_rows}{extras}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a small Polygon OHLCV backfill.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing coverage if DATABASE_URL is available.")
    parser.add_argument("--source", help="Optional source filter for existing coverage.")
    parser.add_argument("--adjusted", default="all", help="Adjusted filter: true, false, or all. Default all.")
    args = parser.parse_args()

    load_local_env_if_available()
    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    expected_dates = expected_trading_days(start_date, end_date)
    expected_rows = len(expected_dates)
    estimated_vendor_requests = expected_rows * len(symbols)
    adjusted_filter = _parse_adjusted_filter(args.adjusted)
    database_url = os.getenv("DATABASE_URL")

    per_symbol_existing: dict[str, list[date]] = {}
    per_symbol_missing: dict[str, list[date]] = {}
    if args.check_existing and database_url:
        connection = None
        try:
            connection = _open_connection(database_url)
            query = _build_coverage_query()
            for symbol in symbols:
                rows = _fetch_all(connection, query, (symbol, start_date, _exclusive_end_date(end_date), args.timeframe))
                existing_dates, missing_dates = _coverage_for_symbol(
                    rows=rows,
                    expected_dates=expected_dates,
                    source_filter=args.source,
                    adjusted_filter=adjusted_filter,
                )
                per_symbol_existing[symbol] = existing_dates
                per_symbol_missing[symbol] = missing_dates
        finally:
            if connection is not None and hasattr(connection, "close"):
                connection.close()

    for symbol in symbols:
        existing_dates = per_symbol_existing.get(symbol) if per_symbol_existing else None
        missing_dates = per_symbol_missing.get(symbol) if per_symbol_missing else None
        _print_symbol_summary(
            symbol=symbol,
            timeframe=args.timeframe,
            start_date=start_date,
            end_date=end_date,
            expected_rows=expected_rows,
            existing_dates=existing_dates,
            missing_dates=missing_dates,
            source_filter=args.source,
            adjusted_filter=adjusted_filter,
        )

    total_missing_rows = sum(len(per_symbol_missing.get(symbol, [])) for symbol in symbols) if per_symbol_missing else None
    print(
        f"symbols_total={len(symbols)} "
        f"timeframe={args.timeframe} "
        f"start_date={start_date.isoformat()} "
        f"end_date={end_date.isoformat()} "
        f"source_filter={args.source if args.source is not None else 'None'} "
        f"adjusted_filter={adjusted_filter if adjusted_filter is not None else 'all'} "
        f"expected_trading_days={expected_rows} "
        f"estimated_vendor_requests={estimated_vendor_requests} "
        f"per_symbol_expected_rows={expected_rows} "
        f"total_expected_rows={expected_rows * len(symbols)}"
        + (
            f" total_missing_rows={total_missing_rows}" if total_missing_rows is not None else ""
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
