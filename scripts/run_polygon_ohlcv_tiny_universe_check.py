from __future__ import annotations

import argparse
import os
from datetime import date, timedelta

from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental
from app.market_calendar.us_market_calendar import expected_trading_days
from app.state.manual_polygon_ohlcv_checkpoint_store import ManualPolygonOHLCVCheckpointStore
from app.writers.ohlcv_writer import OhlcvWriter
from scripts.dry_run_polygon_ohlcv_incremental import _parse_date
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


DEFAULT_SYMBOLS = ("SPY", "QQQ", "IWM")


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
        "SELECT timestamp "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp < %s AND timeframe = %s "
        "ORDER BY timestamp ASC"
    )


def _calculate_coverage(rows: list[dict[str, object]], *, start_date: date, end_date: date) -> tuple[int, int]:
    expected = expected_trading_days(start_date, end_date)
    observed = []
    for row in rows:
        timestamp = row.get("timestamp")
        if hasattr(timestamp, "date"):
            observed.append(timestamp.date())
    observed_unique = set(observed)
    missing = [day for day in expected if day not in observed_unique]
    return len(expected), len(missing)


def _print_symbol_summary(row) -> None:
    print(
        f"symbol={row.symbol} "
        f"requested_start_date={row.requested_start_date.isoformat()} "
        f"effective_start_date={row.effective_start_date.isoformat()} "
        f"rows_fetched={row.rows_fetched} "
        f"rows_valid={row.rows_valid} "
        f"rows_invalid={row.rows_invalid} "
        f"rows_written={row.rows_written} "
        f"validation_failures={row.validation_failures} "
        f"planned_start_date={row.planned_start_date.isoformat()} "
        f"planned_end_date={row.planned_end_date.isoformat()} "
        f"write_confirmed={str(row.write_confirmed).lower()} "
        f"checkpoint_loaded={str(row.checkpoint_loaded).lower()} "
        f"status={row.status} "
        f"error_message={row.error_message if row.error_message else 'None'}"
    )


def _print_coverage_summary(*, symbol: str, rows: list[dict[str, object]], start_date: date, end_date: date) -> None:
    expected_total, missing_total = _calculate_coverage(rows, start_date=start_date, end_date=end_date)
    print(
        f"symbol={symbol} "
        f"coverage_expected_days={expected_total} "
        f"coverage_missing_days={missing_total} "
        f"coverage_status={'full' if missing_total == 0 else 'gaps'}"
    )


def _print_summary(summary, *, symbols_with_full_coverage: int, symbols_with_gaps: int) -> None:
    for row in summary.symbol_summaries:
        _print_symbol_summary(row)
    print(
        f"symbols_total={summary.series_total} "
        f"symbols_completed={summary.series_completed} "
        f"symbols_failed={summary.series_failed} "
        f"symbols_skipped={summary.series_skipped} "
        f"total_rows_fetched={summary.total_rows_fetched} "
        f"total_rows_written={summary.total_rows_written} "
        f"symbols_with_full_coverage={symbols_with_full_coverage} "
        f"symbols_with_gaps={symbols_with_gaps}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a manual tiny-universe Polygon OHLCV check.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write valid rows through the writer.")
    args = parser.parse_args()

    load_local_env_if_available()
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    if not polygon_api_key:
        raise RuntimeError("POLYGON_API_KEY is required")

    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS

    connection = None
    checkpoint_store = None
    writer = None
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            connection = _open_connection(database_url)
            checkpoint_store = ManualPolygonOHLCVCheckpointStore(connection)
        elif args.confirm_write:
            raise RuntimeError("DATABASE_URL is required when --confirm-write is used")
        if args.confirm_write:
            writer = OhlcvWriter(connection)

        summary = build_manual_polygon_ohlcv_incremental(
            symbols=symbols,
            start_date=_parse_date(args.start_date),
            end_date=_parse_date(args.end_date),
            timeframe=args.timeframe,
            api_key=polygon_api_key,
            writer=writer,
            confirmed_write=args.confirm_write,
            checkpoint_store=checkpoint_store,
            use_checkpoint=checkpoint_store is not None,
            update_checkpoint=args.confirm_write,
        )

        symbols_with_full_coverage = 0
        symbols_with_gaps = 0
        if connection is not None:
            query = _build_coverage_query()
            for row in summary.symbol_summaries:
                coverage_rows = _fetch_all(
                    connection,
                    query,
                    (row.symbol, row.planned_start_date, _exclusive_end_date(row.planned_end_date), args.timeframe),
                )
                _, missing_total = _calculate_coverage(
                    coverage_rows,
                    start_date=row.planned_start_date,
                    end_date=row.planned_end_date,
                )
                if missing_total == 0:
                    symbols_with_full_coverage += 1
                else:
                    symbols_with_gaps += 1
                _print_coverage_summary(
                    symbol=row.symbol,
                    rows=coverage_rows,
                    start_date=row.planned_start_date,
                    end_date=row.planned_end_date,
                )

        _print_summary(summary, symbols_with_full_coverage=symbols_with_full_coverage, symbols_with_gaps=symbols_with_gaps)
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
