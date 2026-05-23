from __future__ import annotations

import argparse
import os
from datetime import date, timedelta

from app.ingestion.backfill.planner import split_date_range_into_chunks
from app.market_calendar.us_market_calendar import expected_trading_days
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available
from scripts.plan_polygon_ohlcv_daily_update import (
    DEFAULT_SYMBOLS,
    _as_date,
    _build_latest_existing_query,
    _exclusive_end_date,
    _latest_expected_trading_day,
    _parse_date,
)


DEFAULT_DAILY_WINDOW_DAYS = 5


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


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}".rstrip("0").rstrip(".")


def _request_budget_status(*, estimated_vendor_requests: int, max_requests: int | None) -> str:
    if max_requests is None:
        return "within_budget"
    return "within_budget" if estimated_vendor_requests <= max_requests else "exceeds_budget"


def _recommended_command(*, update_mode: str, symbol: str, as_of_date: date, timeframe: str, chunk_days: int, source: str) -> str:
    base = "python -m scripts"
    if update_mode == "up_to_date" or update_mode == "no_expected_trading_day":
        return "None"
    if update_mode == "historical_gap_detected":
        return (
            f"{base}.run_polygon_ohlcv_chunked_backfill --symbol {symbol} --start-date {as_of_date.isoformat()} "
            f"--end-date {as_of_date.isoformat()} --timeframe {timeframe} --chunk-days {chunk_days} --source {source}"
        )
    return (
        f"{base}.run_polygon_ohlcv_daily_update --symbol {symbol} --as-of-date {as_of_date.isoformat()} "
        f"--timeframe {timeframe} --source {source}"
    )


def _print_symbol_summary(
    *,
    symbol: str,
    latest_expected_trading_day: date | None,
    latest_existing_date: date | None,
    update_mode: str,
    estimated_requests: int,
    estimated_missing_days: int,
    recommended_command: str,
) -> None:
    print(
        f"symbol={symbol} "
        f"latest_expected_trading_day={_format_date(latest_expected_trading_day)} "
        f"latest_existing_date={_format_date(latest_existing_date)} "
        f"update_mode={update_mode} "
        f"estimated_requests={estimated_requests} "
        f"estimated_missing_days={estimated_missing_days} "
        f"recommended_command={recommended_command}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a Polygon OHLCV scheduler cycle safely.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source", default="polygon_aggregates", help="Source filter, default polygon_aggregates.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum safe manual request budget, default 10.")
    parser.add_argument("--chunk-days", type=int, default=10, help="Chunk size for historical gaps, default 10.")
    parser.add_argument("--daily-window-days", type=int, default=5, help="Daily update window size, default 5.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing canonical coverage if DATABASE_URL is available.")
    args = parser.parse_args()

    load_local_env_if_available()
    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    as_of_date = _parse_date(args.as_of_date)
    database_url = os.getenv("DATABASE_URL")
    if args.check_existing and not database_url:
        raise RuntimeError("DATABASE_URL is required when --check-existing is used")

    latest_expected = _latest_expected_trading_day(as_of_date)
    per_symbol: list[dict[str, object]] = []
    estimated_total_requests = 0

    for symbol in symbols:
        latest_existing_date = None
        if args.check_existing and database_url and latest_expected is not None:
            connection = None
            try:
                connection = _open_connection(database_url)
                query, _ = _build_latest_existing_query(args.source)
                rows = _fetch_all(connection, query, (symbol, args.timeframe, _exclusive_end_date(as_of_date), args.source))
                if rows:
                    latest_existing_date = _as_date(rows[0].get("timestamp"))
            finally:
                if connection is not None and hasattr(connection, "close"):
                    connection.close()

        if latest_expected is None:
            update_mode = "no_expected_trading_day"
            estimated_missing_days = 0
            estimated_requests = 0
        elif latest_existing_date is None:
            update_mode = "no_existing_data"
            estimated_missing_days = len(expected_trading_days(as_of_date - timedelta(days=args.daily_window_days), as_of_date))
            estimated_requests = 1 + max(estimated_missing_days // max(args.chunk_days, 1), 0)
        elif latest_existing_date >= latest_expected:
            update_mode = "up_to_date"
            estimated_missing_days = 0
            estimated_requests = 0
        else:
            missing_days = [day for day in expected_trading_days(latest_existing_date + timedelta(days=1), as_of_date) if day <= as_of_date]
            estimated_missing_days = len(missing_days)
            if estimated_missing_days <= max(args.daily_window_days, 0):
                update_mode = "incremental_update_needed"
                estimated_requests = 1
            else:
                update_mode = "historical_gap_detected"
                estimated_requests = max(1, (estimated_missing_days + max(args.chunk_days, 1) - 1) // max(args.chunk_days, 1))

        estimated_total_requests = estimated_total_requests + estimated_requests
        per_symbol.append(
            {
                "symbol": symbol,
                "latest_expected_trading_day": latest_expected,
                "latest_existing_date": latest_existing_date,
                "update_mode": update_mode,
                "estimated_requests": estimated_requests,
                "estimated_missing_days": estimated_missing_days,
                "recommended_command": _recommended_command(
                    update_mode=update_mode,
                    symbol=symbol,
                    as_of_date=as_of_date,
                    timeframe=args.timeframe,
                    chunk_days=args.chunk_days,
                    source=args.source,
                ),
            }
        )

    historical_gap_symbols = 0
    incremental_updates_needed = 0
    no_existing_data_symbols = 0
    ready = True
    for item in per_symbol:
        update_mode = str(item["update_mode"])
        if update_mode == "historical_gap_detected":
            historical_gap_symbols += 1
        elif update_mode == "incremental_update_needed":
            incremental_updates_needed += 1
        elif update_mode == "no_existing_data":
            no_existing_data_symbols += 1
        elif update_mode in {"up_to_date", "no_expected_trading_day"}:
            pass
        else:
            ready = False
        _print_symbol_summary(
            symbol=str(item["symbol"]),
            latest_expected_trading_day=item["latest_expected_trading_day"] if isinstance(item["latest_expected_trading_day"], date) else None,
            latest_existing_date=item["latest_existing_date"] if isinstance(item["latest_existing_date"], date) else None,
            update_mode=update_mode,
            estimated_requests=int(item["estimated_requests"]),
            estimated_missing_days=int(item["estimated_missing_days"]),
            recommended_command=str(item["recommended_command"]),
        )

    request_budget_status = _request_budget_status(
        estimated_vendor_requests=estimated_total_requests,
        max_requests=args.max_requests,
    )
    if request_budget_status == "exceeds_budget":
        ready = False
    print(
        f"symbols_total={len(symbols)} "
        f"incremental_updates_needed={incremental_updates_needed} "
        f"historical_gap_symbols={historical_gap_symbols} "
        f"no_existing_data_symbols={no_existing_data_symbols} "
        f"estimated_total_requests={estimated_total_requests} "
        f"request_budget_status={request_budget_status} "
        f"scheduler_readiness_status={'safe_manual_ready' if ready else 'not_ready'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
