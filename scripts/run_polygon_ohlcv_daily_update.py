from __future__ import annotations

import argparse
import os
import time
from datetime import date, datetime, timezone

from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental
from app.state.data_lineage_store import DataLineageStore
from app.state.data_quality_result_store import DataQualityResultStore
from app.state.ingestion_run_store import IngestionRunStore
from app.state.errors import IngestionErrorRecord
from app.state.runs import IngestionRun, RunStatus
from app.state.manual_polygon_ohlcv_checkpoint_store import ManualPolygonOHLCVCheckpointStore
from app.writers.ohlcv_writer import OhlcvWriter
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available
from scripts.plan_polygon_ohlcv_daily_update import (
    DEFAULT_SYMBOLS,
    _as_date,
    _build_latest_existing_query,
    _latest_expected_trading_day,
    _parse_date,
)


DEFAULT_MAX_REQUESTS = 10
DEFAULT_SLEEP_SECONDS_BETWEEN_SYMBOLS = 2.0


def _format_date(value: date | None) -> str:
    return value.isoformat() if value is not None else "None"


def _is_rate_limit_failure(error_message: str | None) -> bool:
    if not error_message:
        return False
    lowered = error_message.lower()
    return "429" in lowered or "rate limit" in lowered or "ratelimit" in lowered


def _request_budget_status(*, estimated_vendor_requests: int, max_requests: int | None, allow_over_budget: bool) -> str:
    if allow_over_budget:
        return "override"
    if max_requests is None:
        return "within_budget"
    return "within_budget" if estimated_vendor_requests <= max_requests else "exceeds_budget"


def _sleep_between_symbols(seconds: float, *, dry_run_no_sleep: bool = False) -> None:
    if seconds > 0 and not dry_run_no_sleep:
        time.sleep(seconds)


def _fetch_all(connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    execute = getattr(connection, "execute", None)
    if callable(execute):
        result = connection.execute(sql, params)  # type: ignore[call-arg]
        rows = result.fetchall() if hasattr(result, "fetchall") else []
        return list(rows)
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        if not rows:
            return []
        columns = [desc[0] for desc in getattr(cursor, "description", [])]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        if hasattr(cursor, "close"):
            cursor.close()


def _print_symbol_summary(
    *,
    symbol: str,
    status: str,
    rows_fetched: int,
    rows_written: int,
    latest_expected_trading_day: date | None,
    latest_existing_date: date | None,
    needed_start_date: date | None,
    needed_end_date: date | None,
    error_message: str | None,
) -> None:
    print(
        f"symbol={symbol} "
        f"latest_expected_trading_day={_format_date(latest_expected_trading_day)} "
        f"latest_existing_date={_format_date(latest_existing_date)} "
        f"needed_start_date={_format_date(needed_start_date)} "
        f"needed_end_date={_format_date(needed_end_date)} "
        f"rows_fetched={rows_fetched} "
        f"rows_written={rows_written} "
        f"status={status} "
        f"error_message={error_message if error_message else 'None'}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a manual daily Polygon OHLCV update for a tiny universe.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source", default="polygon_aggregates", help="Source filter, default polygon_aggregates.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write valid rows through the approved writer.")
    parser.add_argument("--record-run", action="store_true", help="Persist operational run history when the approved contract is available.")
    parser.add_argument("--record-quality", action="store_true", help="Persist compact quality outcomes when the approved contract is available.")
    parser.add_argument("--record-lineage", action="store_true", help="Persist compact lineage rows when the approved contract is available.")
    parser.add_argument("--max-requests", type=int, default=DEFAULT_MAX_REQUESTS, help="Maximum safe manual request budget, default 10.")
    parser.add_argument("--allow-over-budget", action="store_true", help="Proceed even if the estimated request budget is exceeded.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing canonical coverage if DATABASE_URL is present.")
    parser.add_argument(
        "--sleep-seconds-between-symbols",
        type=float,
        default=DEFAULT_SLEEP_SECONDS_BETWEEN_SYMBOLS,
        help="Sleep between symbols, default 2 seconds.",
    )
    args = parser.parse_args()

    load_local_env_if_available()
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    if not polygon_api_key:
        raise RuntimeError("POLYGON_API_KEY is required")

    database_url = os.getenv("DATABASE_URL")
    if args.confirm_write and not database_url:
        raise RuntimeError("DATABASE_URL is required when --confirm-write is used")
    if args.record_run and not database_url:
        raise RuntimeError("DATABASE_URL is required when --record-run is used")
    if args.record_quality and not database_url:
        raise RuntimeError("DATABASE_URL is required when --record-quality is used")
    if args.record_lineage and not database_url:
        raise RuntimeError("DATABASE_URL is required when --record-lineage is used")
    if args.check_existing and not database_url:
        raise RuntimeError("DATABASE_URL is required when --check-existing is used")

    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    as_of_date = _parse_date(args.as_of_date)
    latest_expected_trading_day = _latest_expected_trading_day(as_of_date)

    plan: list[dict[str, object]] = []
    existing_connection = None
    if args.check_existing:
        existing_connection = _open_connection(database_url)  # type: ignore[arg-type]
    for symbol in symbols:
        status = "update_needed"
        needed_start_date = latest_expected_trading_day
        needed_end_date = as_of_date + (date.resolution)
        latest_existing_date = None
        if args.check_existing and existing_connection is not None and latest_expected_trading_day is not None:
            query, _ = _build_latest_existing_query(args.source)
            rows = _fetch_all(
                existing_connection,
                query,
                (symbol, args.timeframe, as_of_date + date.resolution, args.source),
            )
            latest_row = rows[0] if rows else None
            latest_existing_date = _as_date(latest_row.get("timestamp")) if latest_row else None
            if latest_existing_date is None:
                status = "no_existing_data"
            elif latest_existing_date >= latest_expected_trading_day:
                status = "up_to_date"
            else:
                status = "update_needed"
                needed_start_date = latest_existing_date + date.resolution
        if latest_expected_trading_day is None:
            status = "no_expected_trading_day"
            needed_start_date = None
        plan.append(
            {
                "symbol": symbol,
                "status": status,
                "needed_start_date": needed_start_date,
                "needed_end_date": needed_end_date,
                "latest_expected_trading_day": latest_expected_trading_day,
                "latest_existing_date": latest_existing_date,
            }
        )

    run_store = None
    quality_store = None
    lineage_store = None
    run_connection = None
    quality_connection = None
    lineage_connection = None
    if args.record_run:
        run_connection = _open_connection(database_url)  # type: ignore[arg-type]
        run_store = IngestionRunStore(run_connection)
    if args.record_quality:
        quality_connection = _open_connection(database_url)  # type: ignore[arg-type]
        quality_store = DataQualityResultStore(quality_connection)
    if args.record_lineage:
        lineage_connection = _open_connection(database_url)  # type: ignore[arg-type]
        lineage_store = DataLineageStore(lineage_connection)

    estimated_vendor_requests = sum(1 for item in plan if item["status"] in {"update_needed", "no_existing_data"})
    request_budget_status = _request_budget_status(
        estimated_vendor_requests=estimated_vendor_requests,
        max_requests=args.max_requests,
        allow_over_budget=args.allow_over_budget,
    )
    if request_budget_status == "exceeds_budget":
        print(
            f"status=blocked_over_budget symbols_total={len(symbols)} estimated_vendor_requests={estimated_vendor_requests} "
            f"max_requests={args.max_requests} request_budget_status={request_budget_status}"
        )
        return 0

    chunks_updated = 0
    chunks_skipped = 0
    chunks_failed = 0
    total_rows_fetched = 0
    total_rows_written = 0
    run_errors: list[IngestionErrorRecord] = []
    run_started_at = datetime.now(timezone.utc)

    connection = None
    writer = None
    checkpoint_store = None
    if args.confirm_write:
        connection = _open_connection(database_url)  # type: ignore[arg-type]
        writer = OhlcvWriter(connection)
        checkpoint_store = ManualPolygonOHLCVCheckpointStore(connection)

    try:
        for item in plan:
            symbol = str(item["symbol"])
            status = str(item["status"])
            latest_expected = item["latest_expected_trading_day"]
            latest_existing = item["latest_existing_date"]
            needed_start_date = item["needed_start_date"]
            needed_end_date = item["needed_end_date"]

            if status in {"up_to_date", "no_expected_trading_day"}:
                chunks_skipped += 1
                _print_symbol_summary(
                    symbol=symbol,
                    status=status,
                    rows_fetched=0,
                    rows_written=0,
                    latest_expected_trading_day=latest_expected if isinstance(latest_expected, date) else None,
                    latest_existing_date=latest_existing if isinstance(latest_existing, date) else None,
                    needed_start_date=needed_start_date if isinstance(needed_start_date, date) else None,
                    needed_end_date=needed_end_date if isinstance(needed_end_date, date) else None,
                    error_message=None,
                )
                _sleep_between_symbols(args.sleep_seconds_between_symbols)
                continue

            if not isinstance(needed_start_date, date) or not isinstance(needed_end_date, date):
                chunks_failed += 1
                _print_symbol_summary(
                    symbol=symbol,
                    status="failed",
                    rows_fetched=0,
                    rows_written=0,
                    latest_expected_trading_day=latest_expected if isinstance(latest_expected, date) else None,
                    latest_existing_date=latest_existing if isinstance(latest_existing, date) else None,
                    needed_start_date=None,
                    needed_end_date=None,
                    error_message="planning failed",
                )
                continue

            try:
                summary = build_manual_polygon_ohlcv_incremental(
                    symbols=(symbol,),
                    start_date=needed_start_date,
                    end_date=needed_end_date - date.resolution,
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
                    _print_symbol_summary(
                        symbol=symbol,
                        status="skipped",
                        rows_fetched=0,
                        rows_written=0,
                        latest_expected_trading_day=latest_expected if isinstance(latest_expected, date) else None,
                        latest_existing_date=latest_existing if isinstance(latest_existing, date) else None,
                        needed_start_date=needed_start_date,
                        needed_end_date=needed_end_date,
                        error_message=None,
                    )
                    continue

                chunks_updated += 1
                total_rows_fetched += row.rows_fetched
                total_rows_written += row.rows_written
                _print_symbol_summary(
                    symbol=symbol,
                    status=row.status,
                    rows_fetched=row.rows_fetched,
                    rows_written=row.rows_written,
                    latest_expected_trading_day=latest_expected if isinstance(latest_expected, date) else None,
                    latest_existing_date=latest_existing if isinstance(latest_existing, date) else None,
                    needed_start_date=needed_start_date,
                    needed_end_date=needed_end_date,
                    error_message=row.error_message,
                )
                if run_store is not None:
                    run_store.save_run(
                        IngestionRun(
                            run_id=f"polygon-ohlcv-daily-update:{symbol}:{as_of_date.isoformat()}",
                            job_id="polygon_ohlcv_daily_update",
                            status=RunStatus.SUCCESS if row.status == "completed" else RunStatus.FAILED,
                            rows_fetched=row.rows_fetched,
                            rows_written=row.rows_written,
                            rows_rejected=row.rows_invalid,
                            error_count=1 if row.error_message else 0,
                            metadata={"vendor": "polygon", "dataset": "ohlcv"},
                        )
                    )
                if quality_store is not None:
                    quality_store.save_results(
                        vendor="polygon",
                        dataset="ohlcv",
                        symbol=symbol,
                        timeframe=args.timeframe,
                        check_name="daily_update_summary",
                        status="pass" if row.status == "completed" else "fail",
                        severity="info" if row.status == "completed" else "error",
                        message=row.error_message or "daily update completed",
                        observed_value=row.rows_fetched,
                        expected_value=row.rows_valid + row.rows_invalid,
                    )
                if lineage_store is not None:
                    lineage_store.save_chunk_lineage(
                        vendor="polygon",
                        dataset="ohlcv",
                        symbol=symbol,
                        timeframe=args.timeframe,
                        source_endpoint="v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}",
                        request_params=f"symbol={symbol};start_date={needed_start_date.isoformat()};end_date={(needed_end_date - date.resolution).isoformat()}",
                        response_status=200 if row.status == "completed" else 500,
                        row_count=row.rows_fetched,
                        normalization_version="polygon_ohlcv_normalization_v1",
                        quality_status="pass" if row.status == "completed" else "fail",
                    )
            except Exception as exc:
                chunks_failed += 1
                error_message = f"{exc.__class__.__name__}: {exc}"
                run_errors.append(
                    IngestionErrorRecord(
                        error_id=f"{symbol}:{as_of_date.isoformat()}",
                        run_id=f"polygon-ohlcv-daily-update:{symbol}:{as_of_date.isoformat()}",
                        error_type=exc.__class__.__name__,
                        message=error_message,
                        retryable=_is_rate_limit_failure(error_message),
                        metadata={"vendor": "polygon", "dataset": "ohlcv", "symbol": symbol, "timeframe": args.timeframe},
                    )
                )
                _print_symbol_summary(
                    symbol=symbol,
                    status="failed",
                    rows_fetched=0,
                    rows_written=0,
                    latest_expected_trading_day=latest_expected if isinstance(latest_expected, date) else None,
                    latest_existing_date=latest_existing if isinstance(latest_existing, date) else None,
                    needed_start_date=needed_start_date,
                    needed_end_date=needed_end_date,
                    error_message=error_message,
                )
            _sleep_between_symbols(args.sleep_seconds_between_symbols)
    finally:
        if existing_connection is not None and hasattr(existing_connection, "close"):
            existing_connection.close()
        if run_connection is not None and hasattr(run_connection, "close"):
            run_connection.close()
        if quality_connection is not None and hasattr(quality_connection, "close"):
            quality_connection.close()
        if lineage_connection is not None and hasattr(lineage_connection, "close"):
            lineage_connection.close()
        if connection is not None and hasattr(connection, "close"):
            connection.close()

    if run_store is not None and run_errors:
        run_store.save_errors(f"polygon-ohlcv-daily-update:{as_of_date.isoformat()}", run_errors)

    print(
        f"symbols_total={len(symbols)} "
        f"symbols_updated={chunks_updated} "
        f"symbols_skipped={chunks_skipped} "
        f"symbols_failed={chunks_failed} "
        f"total_rows_fetched={total_rows_fetched} "
        f"total_rows_written={total_rows_written} "
        f"request_budget_status={request_budget_status}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
