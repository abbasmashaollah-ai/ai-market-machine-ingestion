from __future__ import annotations

import argparse
from datetime import date
from typing import Any

from app.ingestion.ohlcv.fanout import FmpMultiSymbolOhlcvFanoutRequest, build_multi_symbol_ohlcv_fanout


DEFAULT_SYMBOLS = ("AAPL", "MSFT", "SPY")


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _emit_payload(payload: dict[str, Any]) -> None:
    for key in (
        "run_type",
        "vendor",
        "requested_start_date",
        "requested_end_date",
        "requested_symbols",
        "completed_symbols",
        "failed_symbols",
        "raw_record_count",
        "normalized_record_count",
        "writer_status",
        "checkpoint_status",
        "did_write_db",
        "batch_errors",
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
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a manual daily FMP OHLCV update for a small symbol set.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to AAPL, MSFT, SPY.")
    parser.add_argument("--as-of-date", help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed symbol.")
    parser.add_argument("--confirm-write", action="store_true", help="Reserved explicit writer toggle; disabled by default.")
    parser.add_argument(
        "--confirm-checkpoint",
        action="store_true",
        help="Reserved explicit checkpoint toggle; disabled by default.",
    )
    args = parser.parse_args()

    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
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

    request = FmpMultiSymbolOhlcvFanoutRequest(
        symbols=symbols,
        start_date=requested_start,
        end_date=requested_end,
        timeframe=args.timeframe,
    )
    result = build_multi_symbol_ohlcv_fanout(
        request,
        execute_writer=False,
        execute_checkpoint_persistence=False,
        fail_fast=args.fail_fast,
    )
    payload = _result_to_payload(
        request=request,
        result=result,
        as_of_date=_parse_date(args.as_of_date) if args.as_of_date else None,
        start_date=requested_start,
        end_date=requested_end,
        date_range_mode=date_range_mode,
    )
    _emit_payload(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
