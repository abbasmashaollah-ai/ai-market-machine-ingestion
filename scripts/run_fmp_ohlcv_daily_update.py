from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from typing import Any

from app.ingestion.ohlcv.fanout import FmpMultiSymbolOhlcvFanoutRequest, build_multi_symbol_ohlcv_fanout
from app.quality.validators import ValidationResult, ValidationSeverity, ValidationStatus
from app.state.data_lineage_store import DataLineageStore
from app.state.data_quality_result_store import DataQualityResultStore
from app.state.errors import IngestionErrorRecord
from app.state.ingestion_run_store import IngestionRunStore
from app.state.runs import IngestionRun, RunStatus
from app.writers.ohlcv_writer import OhlcvWriter
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


DEFAULT_SYMBOLS = ("AAPL", "MSFT", "SPY")
DEFAULT_MAX_SYMBOLS = 3


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _run_id(*, date_range_mode: str, start_date: date, end_date: date) -> str:
    return f"manual-fmp-daily-ohlcv:{date_range_mode}:{start_date.isoformat()}:{end_date.isoformat()}"


def _normalize_batch_status(result: object) -> RunStatus:
    completed = len(getattr(result, "completed_symbols", ()))
    failed = len(getattr(result, "failed_symbols", ()))
    if failed == 0:
        return RunStatus.SUCCESS
    if completed > 0:
        return RunStatus.PARTIAL
    return RunStatus.FAILED


def _quality_results_for_symbol(*, symbol_result: dict[str, object]) -> list[ValidationResult]:
    status = str(symbol_result.get("status") or "completed")
    raw_record_count = int(symbol_result.get("raw_record_count") or 0)
    normalized_record_count = int(symbol_result.get("normalized_record_count") or 0)
    writer_status = str(symbol_result.get("writer_status") or "not_requested")
    if status == "completed":
        return [
            ValidationResult(
                check_name="fmp_daily_summary",
                status=ValidationStatus.PASS,
                severity=ValidationSeverity.INFO,
                message="FMP daily symbol completed",
                details={
                    "observed_value": raw_record_count,
                    "expected_value": normalized_record_count,
                    "writer_status": writer_status,
                },
            )
        ]
    if status.startswith("skipped"):
        return [
            ValidationResult(
                check_name="fmp_daily_summary",
                status=ValidationStatus.WARN,
                severity=ValidationSeverity.WARN,
                message="FMP daily symbol skipped",
                details={
                    "observed_value": raw_record_count,
                    "expected_value": normalized_record_count,
                    "writer_status": writer_status,
                },
            )
        ]
    return [
        ValidationResult(
            check_name="fmp_daily_summary",
            status=ValidationStatus.FAIL,
            severity=ValidationSeverity.ERROR,
            message=str(symbol_result.get("status") or "failed"),
            details={
                "observed_value": raw_record_count,
                "expected_value": normalized_record_count,
                "writer_status": writer_status,
            },
        )
    ]


def _lineage_payload_for_symbol(*, symbol_result: dict[str, object], requested_start: date, requested_end: date, timeframe: str) -> dict[str, object]:
    symbol = str(symbol_result.get("symbol"))
    return {
        "vendor": "fmp",
        "dataset": "ohlcv",
        "symbol": symbol,
        "timeframe": timeframe,
        "source_endpoint": f"/api/v3/historical-price-full/{symbol}",
        "request_params": json.dumps(
            {"from": requested_start.isoformat(), "to": requested_end.isoformat()},
            sort_keys=True,
            separators=(",", ":"),
        ),
        "row_count": int(symbol_result.get("normalized_record_count") or 0),
        "normalization_version": "fmp.ohlcv.v1",
        "quality_status": "pass" if str(symbol_result.get("status") or "completed") == "completed" else "warn" if str(symbol_result.get("status") or "").startswith("skipped") else "fail",
        "intended_target": "canonical_ohlcv",
        "write_mode": "write" if bool(symbol_result.get("did_write_db")) else "dry_run",
        "did_write_db": bool(symbol_result.get("did_write_db")),
    }


def _emit_payload(payload: dict[str, Any]) -> None:
    for key in (
        "run_type",
        "vendor",
        "requested_start_date",
        "requested_end_date",
        "requested_as_of_date",
        "date_range_mode",
        "requested_symbols",
        "completed_symbols",
        "failed_symbols",
        "raw_record_count",
        "normalized_record_count",
        "writer_status",
        "checkpoint_status",
        "did_write_db",
        "batch_errors",
        "dry_run",
    ):
        print(f"{key}={payload.get(key)}")


def _result_to_payload(
    *,
    request: FmpMultiSymbolOhlcvFanoutRequest,
    result: object,
    as_of_date: date | None,
    start_date: date,
    end_date: date,
    date_range_mode: str,
    dry_run: bool,
) -> dict[str, Any]:
    return {
        "run_type": "manual_fmp_daily_ohlcv",
        "vendor": getattr(result, "vendor", "fmp"),
        "requested_start_date": start_date.isoformat(),
        "requested_end_date": end_date.isoformat(),
        "requested_as_of_date": as_of_date.isoformat() if as_of_date is not None else None,
        "date_range_mode": date_range_mode,
        "requested_symbols": tuple(getattr(result, "requested_symbols", request.symbols)),
        "completed_symbols": tuple(getattr(result, "completed_symbols", ())),
        "failed_symbols": tuple(getattr(result, "failed_symbols", ())),
        "raw_record_count": getattr(result, "raw_record_count", 0),
        "normalized_record_count": getattr(result, "normalized_record_count", 0),
        "writer_status": getattr(result, "writer_status", "not_requested"),
        "checkpoint_status": getattr(result, "checkpoint_status", "not_requested"),
        "did_write_db": getattr(result, "did_write_db", False),
        "batch_errors": tuple(getattr(result, "batch_errors", ())),
        "per_symbol_results": tuple(getattr(result, "per_symbol_results", ())),
        "dry_run": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a manual daily FMP OHLCV update for a small symbol set.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to AAPL, MSFT, SPY.")
    parser.add_argument("--as-of-date", help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed symbol.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write valid rows through the approved writer.")
    parser.add_argument("--dry-run", action="store_true", help="Explicitly keep writer execution disabled.")
    parser.add_argument("--record-run", action="store_true", help="Persist operational run history when the approved contract is available.")
    parser.add_argument("--record-quality", action="store_true", help="Persist compact quality outcomes when the approved contract is available.")
    parser.add_argument("--record-lineage", action="store_true", help="Persist compact lineage rows when the approved contract is available.")
    parser.add_argument("--max-symbols", type=int, default=DEFAULT_MAX_SYMBOLS, help="Safety cap for symbol count.")
    args = parser.parse_args()

    load_local_env_if_available()
    if args.confirm_write and args.dry_run:
        raise RuntimeError("Use either --confirm-write or --dry-run, not both")

    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    if len(symbols) > args.max_symbols:
        raise RuntimeError(f"symbol count exceeds safety cap: {len(symbols)} > {args.max_symbols}")

    if args.as_of_date and (args.start_date or args.end_date):
        raise RuntimeError("Use either --as-of-date or --start-date/--end-date, not both")
    if bool(args.start_date) != bool(args.end_date):
        raise RuntimeError("--start-date and --end-date must be provided together")

    if args.as_of_date:
        requested_start = requested_end = _parse_date(args.as_of_date)
        date_range_mode = "as_of_date"
    elif args.start_date and args.end_date:
        requested_start = _parse_date(args.start_date)
        requested_end = _parse_date(args.end_date)
        date_range_mode = "explicit_range"
    else:
        raise RuntimeError("Either --as-of-date or --start-date/--end-date is required")

    execute_writer = bool(args.confirm_write and not args.dry_run)
    database_url = os.getenv("DATABASE_URL")
    if (execute_writer or args.record_run or args.record_quality or args.record_lineage) and not database_url:
        raise RuntimeError("DATABASE_URL is required when write or evidence recording is requested")

    connection = None
    writer = None
    run_store = None
    quality_store = None
    lineage_store = None
    if database_url and (execute_writer or args.record_run or args.record_quality or args.record_lineage):
        connection = _open_connection(database_url)
        if execute_writer:
            writer = OhlcvWriter(connection)
        if args.record_run:
            run_store = IngestionRunStore(connection)
        if args.record_quality:
            quality_store = DataQualityResultStore(connection)
        if args.record_lineage:
            lineage_store = DataLineageStore(connection)

    request = FmpMultiSymbolOhlcvFanoutRequest(
        symbols=symbols,
        start_date=requested_start,
        end_date=requested_end,
        timeframe=args.timeframe,
    )
    result = build_multi_symbol_ohlcv_fanout(
        request,
        writer=writer,
        execute_writer=execute_writer,
        execute_checkpoint_persistence=False,
        fail_fast=args.fail_fast,
    )
    run_id = _run_id(date_range_mode=date_range_mode, start_date=requested_start, end_date=requested_end)

    if run_store is not None:
        run_status = _normalize_batch_status(result)
        run_store.save_run(
            IngestionRun(
                run_id=run_id,
                job_id="manual_fmp_daily_ohlcv",
                status=run_status,
                rows_fetched=result.raw_record_count,
                rows_written=result.normalized_record_count if result.did_write_db else 0,
                rows_rejected=0,
                error_count=len(result.failed_symbols) + len(result.batch_errors),
                metadata={
                    "vendor": "fmp",
                    "dataset": "ohlcv",
                    "status": run_status.value,
                    "started_at": datetime.now(timezone.utc),
                    "finished_at": datetime.now(timezone.utc),
                    "date_range_mode": date_range_mode,
                    "requested_start_date": requested_start.isoformat(),
                    "requested_end_date": requested_end.isoformat(),
                    "requested_symbols": symbols,
                    "confirmed_write": execute_writer,
                    "dry_run": not execute_writer,
                    "fail_fast": args.fail_fast,
                },
            )
        )
        if result.batch_errors:
            run_store.save_errors(
                run_id,
                [
                    IngestionErrorRecord(
                        error_id=f"fmp:{error.get('symbol', 'batch')}:{index}",
                        run_id=run_id,
                        error_type=str(error.get("kind", "batch_error")),
                        message=str(error.get("message", "batch error")),
                        retryable=bool(error.get("retryable", False)),
                        metadata={
                            "vendor": "fmp",
                            "dataset": "ohlcv",
                            "symbol": error.get("symbol"),
                            "timeframe": args.timeframe,
                            "status": "failed",
                        },
                    )
                    for index, error in enumerate(result.batch_errors)
                ],
            )

    if quality_store is not None:
        for symbol_result in result.per_symbol_results:
            quality_store.save_validation_results(
                vendor="fmp",
                dataset="ohlcv",
                symbol=str(symbol_result.get("symbol")) if symbol_result.get("symbol") is not None else None,
                timeframe=args.timeframe,
                results=_quality_results_for_symbol(symbol_result=symbol_result),
                run_id=run_id if args.record_run else None,
                job_id=None,
            )

    if lineage_store is not None:
        for symbol_result in result.per_symbol_results:
            lineage_payload = _lineage_payload_for_symbol(
                symbol_result=symbol_result,
                requested_start=requested_start,
                requested_end=requested_end,
                timeframe=args.timeframe,
            )
            lineage_store.save_chunk_lineage(
                vendor="fmp",
                dataset="ohlcv",
                symbol=str(symbol_result.get("symbol")) if symbol_result.get("symbol") is not None else None,
                timeframe=args.timeframe,
                source_endpoint=str(lineage_payload["source_endpoint"]),
                request_params=str(lineage_payload["request_params"]),
                response_status=200 if symbol_result.get("status") == "completed" else 500 if symbol_result.get("status") == "failed" else 204,
                row_count=int(lineage_payload["row_count"]),
                normalization_version=str(lineage_payload["normalization_version"]),
                quality_status=str(lineage_payload["quality_status"]),
                run_id=run_id if args.record_run else None,
                job_id="manual_fmp_daily_ohlcv",
            )

    payload = _result_to_payload(
        request=request,
        result=result,
        as_of_date=_parse_date(args.as_of_date) if args.as_of_date else None,
        start_date=requested_start,
        end_date=requested_end,
        date_range_mode=date_range_mode,
        dry_run=not execute_writer,
    )
    _emit_payload(payload)
    if connection is not None and hasattr(connection, "close"):
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
