from __future__ import annotations

import argparse
import os
from datetime import date

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


def _format_date(value: date | None) -> str:
    return value.isoformat() if value is not None else "None"


def _latest_existing_query() -> str:
    return (
        "SELECT symbol, timestamp, source "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timeframe = %s "
        "ORDER BY timestamp DESC LIMIT 1"
    )


def _symbol_master_query() -> str:
    return "SELECT symbol FROM symbol_master WHERE symbol = %s LIMIT 1"


def _latest_existing_date(rows: list[dict[str, object]]) -> date | None:
    if not rows:
        return None
    timestamp = rows[0].get("timestamp")
    if hasattr(timestamp, "date"):
        candidate = timestamp.date()
        return candidate if isinstance(candidate, date) else None
    if isinstance(timestamp, date):
        return timestamp
    return None


def _symbol_status(*, index: int, max_symbols: int, latest_existing_date: date | None) -> str:
    if index >= max_symbols:
        return "exceeds_cap"
    if latest_existing_date is None:
        return "no_existing_data"
    return "has_existing_data"


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a Polygon OHLCV symbol universe safely.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--max-symbols", type=int, default=25, help="Maximum symbol count, default 25.")
    parser.add_argument("--universe-name", default="manual_tiny_universe", help="Universe name, default manual_tiny_universe.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing canonical coverage if DATABASE_URL is available.")
    args = parser.parse_args()

    load_local_env_if_available()
    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    database_url = os.getenv("DATABASE_URL")
    if args.check_existing and not database_url:
        raise RuntimeError("DATABASE_URL is required when --check-existing is used")

    per_symbol: list[dict[str, object]] = []
    symbols_selected = 0
    symbols_over_cap = 0
    symbols_with_existing_data = 0
    symbols_without_existing_data = 0

    for index, symbol in enumerate(symbols):
        latest_existing_date = None
        if args.check_existing and database_url:
            connection = None
            try:
                connection = _open_connection(database_url)
                rows = _fetch_all(connection, _latest_existing_query(), (symbol, args.timeframe))
                if not rows:
                    symbol_master_rows = _fetch_all(connection, _symbol_master_query(), (symbol,))
                    if symbol_master_rows:
                        latest_existing_date = None
                else:
                    latest_existing_date = _latest_existing_date(rows)
            finally:
                if connection is not None and hasattr(connection, "close"):
                    connection.close()

        status = _symbol_status(index=index, max_symbols=args.max_symbols, latest_existing_date=latest_existing_date)
        if status == "exceeds_cap":
            symbols_over_cap += 1
        else:
            symbols_selected += 1
            if status == "has_existing_data":
                symbols_with_existing_data += 1
            elif status == "no_existing_data":
                symbols_without_existing_data += 1

        print(
            f"symbol={symbol} "
            f"universe_name={args.universe_name} "
            f"timeframe={args.timeframe} "
            f"source=polygon_aggregates "
            f"symbol_status={status} "
            f"latest_existing_date={_format_date(latest_existing_date)}"
        )
        per_symbol.append({"symbol": symbol, "status": status})

    universe_readiness_status = "ready" if symbols_over_cap == 0 else "manual_review_needed"
    print(
        f"universe_name={args.universe_name} "
        f"symbols_requested={len(symbols)} "
        f"symbols_selected={symbols_selected} "
        f"symbols_over_cap={symbols_over_cap} "
        f"symbols_with_existing_data={symbols_with_existing_data} "
        f"symbols_without_existing_data={symbols_without_existing_data} "
        f"max_symbols={args.max_symbols} "
        f"universe_readiness_status={universe_readiness_status}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
