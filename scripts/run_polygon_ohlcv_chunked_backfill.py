from __future__ import annotations

import argparse
import os
import time
from datetime import date

from app.ingestion.backfill.planner import split_date_range_into_chunks
from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental
from app.state.manual_polygon_ohlcv_checkpoint_store import ManualPolygonOHLCVCheckpointStore
from app.writers.ohlcv_writer import OhlcvWriter
from scripts.persist_fred_macro import _open_connection
from scripts.persist_fred_macro import load_local_env_if_available


DEFAULT_SYMBOLS = ("SPY", "QQQ", "IWM")
DEFAULT_MAX_SYMBOLS = 3
DEFAULT_MAX_CHUNKS = 6
DEFAULT_SLEEP_SECONDS_BETWEEN_CHUNKS = 2.0
DEFAULT_MAX_RATE_LIMIT_FAILURES = 1


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _print_symbol_summary(row, *, chunk_start_date: date, chunk_end_date: date) -> None:
    print(
        f"symbol={row.symbol} "
        f"chunk_start_date={chunk_start_date.isoformat()} "
        f"chunk_end_date={chunk_end_date.isoformat()} "
        f"requested_start_date={row.requested_start_date.isoformat()} "
        f"effective_start_date={row.effective_start_date.isoformat()} "
        f"rows_fetched={row.rows_fetched} "
        f"rows_written={row.rows_written} "
        f"write_confirmed={str(row.write_confirmed).lower()} "
        f"status={row.status} "
        f"error_message={row.error_message if row.error_message else 'None'}"
    )


def _print_summary(*, symbols_total: int, chunks_total: int, chunks_completed: int, chunks_failed: int, chunks_skipped: int, total_rows_fetched: int, total_rows_written: int) -> None:
    print(
        f"symbols_total={symbols_total} "
        f"chunks_total={chunks_total} "
        f"chunks_completed={chunks_completed} "
        f"chunks_failed={chunks_failed} "
        f"chunks_skipped={chunks_skipped} "
        f"total_rows_fetched={total_rows_fetched} "
        f"total_rows_written={total_rows_written}"
    )


def _is_rate_limit_failure(error_message: str | None) -> bool:
    if not error_message:
        return False
    lowered = error_message.lower()
    return "429" in lowered or "rate limit" in lowered or "ratelimit" in lowered


def _sleep_between_chunks(seconds: float, *, dry_run_no_sleep: bool) -> None:
    if seconds > 0 and not dry_run_no_sleep:
        time.sleep(seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a manual chunked Polygon OHLCV backfill for a tiny universe.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--chunk-days", type=int, default=30, help="Chunk size in days, default 30.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write valid rows through the approved writer.")
    parser.add_argument("--max-symbols", type=int, default=DEFAULT_MAX_SYMBOLS, help="Safety cap for symbol count.")
    parser.add_argument("--max-chunks", type=int, default=DEFAULT_MAX_CHUNKS, help="Safety cap for chunk count.")
    parser.add_argument(
        "--sleep-seconds-between-chunks",
        type=float,
        default=DEFAULT_SLEEP_SECONDS_BETWEEN_CHUNKS,
        help="Sleep between chunks, default 2.",
    )
    parser.add_argument(
        "--stop-on-rate-limit",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Stop after first rate limit failure; use --no-stop-on-rate-limit to continue.",
    )
    parser.add_argument(
        "--max-rate-limit-failures",
        type=int,
        default=DEFAULT_MAX_RATE_LIMIT_FAILURES,
        help="Maximum rate-limit failures before stopping, default 1.",
    )
    parser.add_argument(
        "--dry-run-no-sleep",
        action="store_true",
        help="Disable sleeping between chunks for tests and local dry runs.",
    )
    args = parser.parse_args()

    load_local_env_if_available()
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    if not polygon_api_key:
        raise RuntimeError("POLYGON_API_KEY is required")
    database_url = os.getenv("DATABASE_URL")
    if args.confirm_write and not database_url:
        raise RuntimeError("DATABASE_URL is required when --confirm-write is used")

    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    if len(symbols) > args.max_symbols:
        raise RuntimeError(f"symbol count exceeds safety cap: {len(symbols)} > {args.max_symbols}")

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    chunks = split_date_range_into_chunks(start_date, end_date, max_days_per_chunk=args.chunk_days)
    if len(chunks) > args.max_chunks:
        raise RuntimeError(f"chunk count exceeds safety cap: {len(chunks)} > {args.max_chunks}")

    chunks_completed = 0
    chunks_failed = 0
    chunks_skipped = 0
    total_rows_fetched = 0
    total_rows_written = 0
    rate_limit_failures = 0
    stopped_due_to_rate_limit = False
    chunks_not_run = 0
    connection = None
    checkpoint_store = None
    writer = None
    try:
        if args.confirm_write:
            connection = _open_connection(database_url)  # type: ignore[arg-type]
            checkpoint_store = ManualPolygonOHLCVCheckpointStore(connection)
            writer = OhlcvWriter(connection)

        for symbol in symbols:
            stop_symbol = False
            for chunk in chunks:
                if stop_symbol or stopped_due_to_rate_limit:
                    chunks_not_run += 1
                    continue
                try:
                    summary = build_manual_polygon_ohlcv_incremental(
                        symbols=(symbol,),
                        start_date=chunk.start_date,
                        end_date=chunk.end_date,
                        timeframe=args.timeframe,
                        api_key=polygon_api_key,
                        writer=writer,
                        confirmed_write=args.confirm_write,
                        checkpoint_store=checkpoint_store,
                        use_checkpoint=args.confirm_write,
                        update_checkpoint=args.confirm_write,
                    )
                    row = summary.symbol_summaries[0] if summary.symbol_summaries else None
                    if row is None:
                        chunks_skipped += 1
                        continue
                    _print_symbol_summary(row, chunk_start_date=chunk.start_date, chunk_end_date=chunk.end_date)
                    if row.status.startswith("skipped"):
                        chunks_skipped += 1
                    elif row.status == "failed":
                        chunks_failed += 1
                    else:
                        chunks_completed += 1
                    total_rows_fetched += row.rows_fetched
                    total_rows_written += row.rows_written
                    if row.status == "failed" and _is_rate_limit_failure(row.error_message):
                        rate_limit_failures += 1
                        if rate_limit_failures >= args.max_rate_limit_failures:
                            stopped_due_to_rate_limit = True
                        if args.stop_on_rate_limit:
                            stop_symbol = True
                except Exception as exc:
                    chunks_failed += 1
                    error_message = f"{exc.__class__.__name__}: {exc}"
                    if _is_rate_limit_failure(error_message):
                        rate_limit_failures += 1
                        if rate_limit_failures >= args.max_rate_limit_failures:
                            stopped_due_to_rate_limit = True
                        if args.stop_on_rate_limit:
                            stop_symbol = True
                    print(
                        f"symbol={symbol} "
                        f"chunk_start_date={chunk.start_date.isoformat()} "
                        f"chunk_end_date={chunk.end_date.isoformat()} "
                        f"status=failed "
                        f"error_message={error_message}"
                    )
                _sleep_between_chunks(args.sleep_seconds_between_chunks, dry_run_no_sleep=args.dry_run_no_sleep)
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()

    _print_summary(
        symbols_total=len(symbols),
        chunks_total=len(symbols) * len(chunks),
        chunks_completed=chunks_completed,
        chunks_failed=chunks_failed,
        chunks_skipped=chunks_skipped,
        total_rows_fetched=total_rows_fetched,
        total_rows_written=total_rows_written,
    )
    print(
        f"rate_limit_failures={rate_limit_failures} "
        f"stopped_due_to_rate_limit={str(stopped_due_to_rate_limit).lower()} "
        f"chunks_not_run={chunks_not_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
