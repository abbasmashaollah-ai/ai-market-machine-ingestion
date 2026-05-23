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


def _build_latest_existing_query(source: str | None) -> tuple[str, tuple[object, ...]]:
    sql = (
        "SELECT timestamp, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timeframe = %s AND timestamp < %s"
    )
    if source is not None:
        sql += " AND source = %s"
    sql += " ORDER BY timestamp DESC LIMIT 1"
    return sql, ()


def _latest_expected_trading_day(as_of_date: date) -> date | None:
    days = expected_trading_days(as_of_date, as_of_date)
    if days:
        return days[-1]
    cursor = as_of_date
    for _ in range(10):
        cursor -= timedelta(days=1)
        days = expected_trading_days(cursor, cursor)
        if days:
            return days[-1]
    return None


def _format_date(value: date | None) -> str:
    return value.isoformat() if value is not None else "None"


def _format_dates(values: list[date]) -> str:
    return "[" + ", ".join(value.isoformat() for value in values) + "]" if values else "[]"


def _print_symbol_summary(
    *,
    symbol: str,
    timeframe: str,
    source: str,
    as_of_date: date,
    latest_expected_trading_day: date | None,
    latest_existing_date: date | None,
    needed_start_date: date | None,
    needed_end_date: date | None,
    status: str,
) -> None:
    print(
        f"symbol={symbol} "
        f"timeframe={timeframe} "
        f"source={source} "
        f"as_of_date={as_of_date.isoformat()} "
        f"latest_expected_trading_day={_format_date(latest_expected_trading_day)} "
        f"latest_existing_date={_format_date(latest_existing_date)} "
        f"needed_start_date={_format_date(needed_start_date)} "
        f"needed_end_date={_format_date(needed_end_date)} "
        f"status={status}"
    )


def _as_date(value: object | None) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if hasattr(value, "date"):
        candidate = value.date()
        return candidate if isinstance(candidate, date) else None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a daily Polygon OHLCV update safely.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source", default="polygon_aggregates", help="Source filter, default polygon_aggregates.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing canonical coverage if DATABASE_URL is available.")
    args = parser.parse_args()

    load_local_env_if_available()
    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    as_of_date = _parse_date(args.as_of_date)
    database_url = os.getenv("DATABASE_URL")
    if args.check_existing and not database_url:
        raise RuntimeError("DATABASE_URL is required when --check-existing is used")

    per_symbol_status: dict[str, str] = {}
    per_symbol_existing_date: dict[str, date | None] = {}

    if args.check_existing and database_url:
        connection = None
        try:
            connection = _open_connection(database_url)
            query, _ = _build_latest_existing_query(args.source)
            for symbol in symbols:
                params: tuple[object, ...] = (symbol, args.timeframe, _exclusive_end_date(as_of_date))
                if args.source is not None:
                    params += (args.source,)
                rows = _fetch_all(connection, query, params)
                if not rows:
                    per_symbol_status[symbol] = "no_existing_data"
                    per_symbol_existing_date[symbol] = None
                    continue
                row = rows[0]
                latest_existing = _as_date(row.get("timestamp"))
                per_symbol_existing_date[symbol] = latest_existing
                expected_day = _latest_expected_trading_day(as_of_date)
                if expected_day is None:
                    per_symbol_status[symbol] = "no_expected_trading_day"
                    continue
                if latest_existing is not None and latest_existing >= expected_day:
                    per_symbol_status[symbol] = "up_to_date"
                else:
                    per_symbol_status[symbol] = "update_needed"
        finally:
            if connection is not None and hasattr(connection, "close"):
                connection.close()
    else:
        expected_day = _latest_expected_trading_day(as_of_date)
        for symbol in symbols:
            per_symbol_existing_date[symbol] = None
            if expected_day is None:
                per_symbol_status[symbol] = "no_expected_trading_day"
            else:
                per_symbol_status[symbol] = "update_needed"

    latest_expected = _latest_expected_trading_day(as_of_date)
    if latest_expected is None:
        needed_start_date = None
        needed_end_date = None
    else:
        needed_start_date = None
        if args.check_existing:
            known_existing_dates = [value for value in per_symbol_existing_date.values() if value is not None]
            if known_existing_dates:
                next_needed = max(known_existing_dates) + timedelta(days=1)
                needed_start_date = next_needed if next_needed <= latest_expected else None
            else:
                needed_start_date = latest_expected
        else:
            needed_start_date = latest_expected
        needed_end_date = _exclusive_end_date(as_of_date)

    symbols_up_to_date = 0
    symbols_update_needed = 0
    symbols_no_existing_data = 0
    symbols_no_expected_trading_day = 0
    for symbol in symbols:
        status = per_symbol_status.get(symbol, "update_needed")
        latest_existing = per_symbol_existing_date.get(symbol)
        if status == "up_to_date":
            symbols_up_to_date += 1
        elif status == "update_needed":
            symbols_update_needed += 1
        elif status == "no_existing_data":
            symbols_no_existing_data += 1
        elif status == "no_expected_trading_day":
            symbols_no_expected_trading_day += 1
        _print_symbol_summary(
            symbol=symbol,
            timeframe=args.timeframe,
            source=args.source,
            as_of_date=as_of_date,
            latest_expected_trading_day=latest_expected,
            latest_existing_date=latest_existing,
            needed_start_date=needed_start_date,
            needed_end_date=needed_end_date,
            status=status,
        )

    print(
        f"symbols_total={len(symbols)} "
        f"symbols_up_to_date={symbols_up_to_date} "
        f"symbols_update_needed={symbols_update_needed} "
        f"symbols_no_existing_data={symbols_no_existing_data} "
        f"symbols_no_expected_trading_day={symbols_no_expected_trading_day}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
