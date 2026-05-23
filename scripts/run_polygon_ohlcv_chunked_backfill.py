from __future__ import annotations

import argparse
import os
import json
import time
from datetime import date, datetime, timezone

from app.ingestion.backfill.planner import split_date_range_into_chunks
from app.market_calendar.us_market_calendar import expected_trading_days
from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental
from app.quality.validators import ValidationResult, ValidationSeverity, ValidationStatus
from app.state.data_lineage_store import DataLineageStore
from app.state.data_quality_result_store import DataQualityResultStore
from app.state.ingestion_run_store import IngestionRunStore
from app.state.errors import IngestionErrorRecord
from app.state.runs import IngestionRun, RunStatus
from app.state.manual_polygon_ohlcv_checkpoint_store import ManualPolygonOHLCVCheckpointStore
from app.writers.ohlcv_writer import OhlcvWriter
from scripts.persist_fred_macro import _open_connection
from scripts.persist_fred_macro import load_local_env_if_available


DEFAULT_SYMBOLS = ("SPY", "QQQ", "IWM")
DEFAULT_MAX_SYMBOLS = 3
DEFAULT_MAX_CHUNKS = 6
DEFAULT_SLEEP_SECONDS_BETWEEN_CHUNKS = 2.0
DEFAULT_MAX_RATE_LIMIT_FAILURES = 1
DEFAULT_MAX_REQUESTS = 25


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


def _estimated_vendor_requests(*, symbol_count: int, chunk_count: int) -> int:
    return symbol_count * chunk_count


def _request_budget_status(*, estimated_vendor_requests: int, max_requests: int | None, allow_over_budget: bool) -> str:
    if allow_over_budget:
        return "override"
    if max_requests is None:
        return "within_budget"
    return "within_budget" if estimated_vendor_requests <= max_requests else "exceeds_budget"


def _run_id(start_date: date, end_date: date) -> str:
    return f"polygon-ohlcv-chunked-backfill:{start_date.isoformat()}:{end_date.isoformat()}"


def _chunk_lineage_request_params(*, symbol: str, start_date: date, end_date: date, timeframe: str, chunk_days: int) -> str:
    return json.dumps(
        {
            "symbol": symbol,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timeframe": timeframe,
            "chunk_days": chunk_days,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _final_run_status(*, chunks_completed: int, chunks_failed: int) -> RunStatus:
    if chunks_failed == 0:
        return RunStatus.SUCCESS
    if chunks_completed > 0:
        return RunStatus.PARTIAL
    return RunStatus.FAILED


def _build_quality_results(*, symbol: str, timeframe: str, row) -> list[ValidationResult]:
    status = ValidationStatus.PASS if row.status == "completed" else ValidationStatus.FAIL if row.status == "failed" else ValidationStatus.WARN
    severity = ValidationSeverity.INFO if status == ValidationStatus.PASS else ValidationSeverity.ERROR if status == ValidationStatus.FAIL else ValidationSeverity.WARN
    results = [
        ValidationResult(
            check_name="chunk_validation_summary",
            status=status,
            severity=severity,
            message="chunk completed" if status == ValidationStatus.PASS else row.error_message or "chunk not completed",
            details={
                "observed_value": row.rows_fetched,
                "expected_value": row.rows_valid + row.rows_invalid,
            },
        )
    ]
    if row.rows_invalid:
        results.append(
            ValidationResult(
                check_name="chunk_invalid_rows",
                status=ValidationStatus.WARN if row.rows_invalid > 0 else ValidationStatus.PASS,
                severity=ValidationSeverity.WARN,
                message="invalid rows were observed",
                details={"observed_value": row.rows_invalid, "expected_value": 0},
            )
        )
    if row.validation_failures:
        results.append(
            ValidationResult(
                check_name="chunk_validation_failures",
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.ERROR,
                message="validation failures were observed",
                details={"observed_value": row.validation_failures, "expected_value": 0},
            )
        )
    return results


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
    parser.add_argument("--max-requests", type=int, default=DEFAULT_MAX_REQUESTS, help="Maximum safe manual request budget, default 25.")
    parser.add_argument("--allow-over-budget", action="store_true", help="Proceed even if the estimated request budget is exceeded.")
    parser.add_argument("--record-run", action="store_true", help="Persist operational run history when the approved contract is available.")
    parser.add_argument("--record-quality", action="store_true", help="Persist compact quality outcomes when the approved contract is available.")
    parser.add_argument("--record-lineage", action="store_true", help="Persist compact lineage rows when the approved contract is available.")
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
    if args.record_run and not database_url:
        raise RuntimeError("DATABASE_URL is required when --record-run is used")
    if args.record_quality and not database_url:
        raise RuntimeError("DATABASE_URL is required when --record-quality is used")
    if args.record_lineage and not database_url:
        raise RuntimeError("DATABASE_URL is required when --record-lineage is used")

    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    if len(symbols) > args.max_symbols:
        raise RuntimeError(f"symbol count exceeds safety cap: {len(symbols)} > {args.max_symbols}")

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    run_started_at = datetime.now(timezone.utc)
    chunks = split_date_range_into_chunks(start_date, end_date, max_days_per_chunk=args.chunk_days)
    expected_days = expected_trading_days(start_date, end_date)
    if len(chunks) > args.max_chunks:
        raise RuntimeError(f"chunk count exceeds safety cap: {len(chunks)} > {args.max_chunks}")
    estimated_vendor_requests = _estimated_vendor_requests(symbol_count=len(symbols), chunk_count=len(chunks))
    request_budget_status = _request_budget_status(
        estimated_vendor_requests=estimated_vendor_requests,
        max_requests=args.max_requests,
        allow_over_budget=args.allow_over_budget,
    )
    run_store = None
    run_connection = None
    quality_connection = None
    lineage_connection = None
    run_errors: list[IngestionErrorRecord] = []
    quality_records: list[tuple[str, str, object]] = []
    run_history_blocked = False
    blocked_over_budget = False
    if args.record_run:
        run_connection = _open_connection(database_url)  # type: ignore[arg-type]
        run_store = IngestionRunStore(run_connection)
    quality_store = None
    if args.record_quality:
        quality_connection = _open_connection(database_url)  # type: ignore[arg-type]
        quality_store = DataQualityResultStore(quality_connection)
    lineage_store = None
    if args.record_lineage:
        lineage_connection = _open_connection(database_url)  # type: ignore[arg-type]
        lineage_store = DataLineageStore(lineage_connection)
    if request_budget_status == "exceeds_budget" and not args.allow_over_budget:
        print(
            f"status=blocked_over_budget "
            f"symbols_total={len(symbols)} "
            f"date_chunks_total={len(chunks)} "
            f"estimated_vendor_requests={estimated_vendor_requests} "
            f"max_requests={args.max_requests} "
            f"request_budget_status={request_budget_status} "
            f"expected_trading_days={len(expected_days)}"
        )
        run_history_blocked = True
        blocked_over_budget = True

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
        if not blocked_over_budget:
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
                        if quality_store is not None:
                            quality_store.save_validation_results(
                                vendor="polygon",
                                dataset="ohlcv",
                                symbol=row.symbol,
                                timeframe=args.timeframe,
                                results=_build_quality_results(symbol=row.symbol, timeframe=args.timeframe, row=row),
                                run_id=_run_id(start_date, end_date) if args.record_run else None,
                            )
                        if lineage_store is not None:
                            lineage_store.save_chunk_lineage(
                                vendor="polygon",
                                dataset="ohlcv",
                                symbol=row.symbol,
                                timeframe=args.timeframe,
                                source_endpoint="v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}",
                                request_params=_chunk_lineage_request_params(
                                    symbol=row.symbol,
                                    start_date=chunk.start_date,
                                    end_date=chunk.end_date,
                                    timeframe=args.timeframe,
                                    chunk_days=args.chunk_days,
                                ),
                                response_status=200 if row.status == "completed" else 500 if row.status == "failed" else 204,
                                row_count=row.rows_fetched,
                                normalization_version="polygon_ohlcv_normalization_v1",
                                quality_status="pass" if row.status == "completed" else "fail" if row.status == "failed" else "warn",
                                run_id=_run_id(start_date, end_date) if args.record_run else None,
                                job_id="polygon_ohlcv_chunked_backfill" if args.record_run else None,
                            )
                        if row.status.startswith("skipped"):
                            chunks_skipped += 1
                        elif row.status == "failed":
                            chunks_failed += 1
                            run_errors.append(
                                IngestionErrorRecord(
                                    error_id=f"{symbol}:{chunk.start_date.isoformat()}:{chunk.end_date.isoformat()}",
                                    run_id=_run_id(start_date, end_date),
                                    error_type="chunk_failed",
                                    message=row.error_message or "chunk failed",
                                    retryable=_is_rate_limit_failure(row.error_message),
                                    metadata={
                                        "vendor": "polygon",
                                        "dataset": "ohlcv",
                                        "symbol": symbol,
                                        "timeframe": args.timeframe,
                                        "chunk_start_date": chunk.start_date.isoformat(),
                                        "chunk_end_date": chunk.end_date.isoformat(),
                                        "status": row.status,
                                    },
                                )
                            )
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
                            else:
                                stop_symbol = False
                    except Exception as exc:
                        chunks_failed += 1
                        error_message = f"{exc.__class__.__name__}: {exc}"
                        run_errors.append(
                            IngestionErrorRecord(
                                error_id=f"{symbol}:{chunk.start_date.isoformat()}:{chunk.end_date.isoformat()}",
                                run_id=_run_id(start_date, end_date),
                                error_type=exc.__class__.__name__,
                                message=error_message,
                                retryable=_is_rate_limit_failure(error_message),
                                metadata={
                                    "vendor": "polygon",
                                    "dataset": "ohlcv",
                                    "symbol": symbol,
                                    "timeframe": args.timeframe,
                                    "chunk_start_date": chunk.start_date.isoformat(),
                                    "chunk_end_date": chunk.end_date.isoformat(),
                                },
                            )
                        )
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
        if run_store is not None:
            if blocked_over_budget:
                run_store.save_run(
                    IngestionRun(
                        run_id=_run_id(start_date, end_date),
                        job_id="polygon_ohlcv_chunked_backfill",
                        status=RunStatus.SKIPPED,
                        rows_fetched=0,
                        rows_written=0,
                        rows_rejected=0,
                        error_count=0,
                        metadata={
                            "vendor": "polygon",
                            "dataset": "ohlcv",
                            "status": "blocked_over_budget",
                            "started_at": run_started_at,
                            "finished_at": datetime.now(timezone.utc),
                            "estimated_vendor_requests": estimated_vendor_requests,
                            "max_requests": args.max_requests,
                            "request_budget_status": request_budget_status,
                        },
                    )
                )
            elif not run_history_blocked:
                final_status = _final_run_status(chunks_completed=chunks_completed, chunks_failed=chunks_failed)
                run_store.save_run(
                    IngestionRun(
                        run_id=_run_id(start_date, end_date),
                        job_id="polygon_ohlcv_chunked_backfill",
                        status=final_status,
                        rows_fetched=total_rows_fetched,
                        rows_written=total_rows_written,
                        rows_rejected=0,
                        error_count=chunks_failed + rate_limit_failures,
                        metadata={
                            "vendor": "polygon",
                            "dataset": "ohlcv",
                            "status": final_status.value,
                            "started_at": run_started_at,
                            "finished_at": datetime.now(timezone.utc),
                            "estimated_vendor_requests": estimated_vendor_requests,
                            "max_requests": args.max_requests,
                            "request_budget_status": request_budget_status,
                            "allow_over_budget": args.allow_over_budget,
                            "rate_limit_failures": rate_limit_failures,
                            "stopped_due_to_rate_limit": stopped_due_to_rate_limit,
                            "chunks_not_run": chunks_not_run,
                        },
                    )
                )
                if run_errors:
                    run_store.save_errors(_run_id(start_date, end_date), run_errors)
        if run_connection is not None and hasattr(run_connection, "close"):
            run_connection.close()
        if quality_connection is not None and hasattr(quality_connection, "close"):
            quality_connection.close()
        if lineage_connection is not None and hasattr(lineage_connection, "close"):
            lineage_connection.close()
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
    print(
        f"request_budget_status={request_budget_status} "
        f"estimated_vendor_requests={estimated_vendor_requests} "
        f"max_requests={args.max_requests} "
        f"allow_over_budget={str(args.allow_over_budget).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
