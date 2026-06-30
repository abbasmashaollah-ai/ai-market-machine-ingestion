from __future__ import annotations

import argparse
import os
from types import SimpleNamespace

from scripts.preflight_polygon_ohlcv_operations import build_preflight_report
from scripts.run_polygon_ohlcv_daily_update import main as run_daily_update_main
from scripts.persist_fred_macro import load_local_env_if_available


def _scheduler_enabled(args: argparse.Namespace) -> tuple[bool, str]:
    env_enabled = os.getenv("ENABLE_POLYGON_OHLCV_SCHEDULER", "").lower() == "true"
    if not args.enable_scheduler_cycle and not env_enabled:
        return False, "missing --enable-scheduler-cycle and ENABLE_POLYGON_OHLCV_SCHEDULER=true"
    if not args.enable_scheduler_cycle:
        return False, "missing --enable-scheduler-cycle"
    if not env_enabled:
        return False, "missing ENABLE_POLYGON_OHLCV_SCHEDULER=true"
    return True, "enabled"


def main() -> int:
    parser = argparse.ArgumentParser(description="Disabled-by-default Polygon OHLCV scheduler stub.")
    parser.add_argument("--enable-scheduler-cycle", action="store_true", help="Explicitly enable the scheduler cycle.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source", default="polygon_aggregates", help="Source filter, default polygon_aggregates.")
    parser.add_argument("--max-symbols", type=int, default=25, help="Maximum symbol count, default 25.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum request budget, default 10.")
    parser.add_argument("--confirm-write", action="store_true", help="Pass through to the daily runner when enabled.")
    parser.add_argument("--record-run", action="store_true", help="Pass through to the daily runner when enabled.")
    parser.add_argument("--record-quality", action="store_true", help="Pass through to the daily runner when enabled.")
    parser.add_argument("--record-lineage", action="store_true", help="Pass through to the daily runner when enabled.")
    parser.add_argument("--check-existing", action="store_true", help="Pass through to the daily runner when enabled.")
    parser.add_argument(
        "--sleep-seconds-between-symbols",
        type=float,
        default=2.0,
        help="Pass through to the daily runner when enabled.",
    )
    args = parser.parse_args()

    load_local_env_if_available()
    enabled, reason = _scheduler_enabled(args)
    if not enabled:
        print(f"status=scheduler_disabled reason={reason}")
        return 0

    preflight_args = SimpleNamespace(
        symbol=args.symbol,
        as_of_date=args.as_of_date,
        timeframe=args.timeframe,
        source=args.source,
        max_symbols=args.max_symbols,
        max_requests=args.max_requests,
        check_existing=args.check_existing,
    )
    per_symbol, summary = build_preflight_report(preflight_args)
    if summary["preflight_status"] == "blocked":
        print(
            f"status=blocked_preflight symbols_total={summary['symbols_total']} "
            f"request_budget_status={summary['request_budget_status']} "
            f"preflight_status={summary['preflight_status']}"
        )
        return 0

    symbols_to_run = [
        item["symbol"]
        for item in per_symbol
        if item["recommended_action"] in {"run_daily_update", "run_small_backfill_or_daily_update"}
    ]
    if not symbols_to_run:
        print(
            f"status=completed symbols_total={summary['symbols_total']} symbols_ran=0 "
            f"request_budget_status={summary['request_budget_status']}"
        )
        return 0

    runner_args = [
        "run_polygon_ohlcv_daily_update.py",
        "--as-of-date",
        args.as_of_date,
        "--timeframe",
        args.timeframe,
        "--source",
        args.source,
        "--max-requests",
        str(args.max_requests),
    ]
    for symbol in symbols_to_run:
        runner_args.extend(["--symbol", str(symbol)])
    if args.confirm_write:
        runner_args.append("--confirm-write")
    if args.record_run:
        runner_args.append("--record-run")
    if args.record_quality:
        runner_args.append("--record-quality")
    if args.record_lineage:
        runner_args.append("--record-lineage")
    if args.check_existing:
        runner_args.append("--check-existing")
    runner_args.extend(["--sleep-seconds-between-symbols", str(args.sleep_seconds_between_symbols)])

    original_argv = os.sys.argv
    try:
        os.sys.argv = runner_args
        run_daily_update_main()
    finally:
        os.sys.argv = original_argv

    print(
        f"status=completed symbols_total={summary['symbols_total']} symbols_ran={len(symbols_to_run)} "
        f"request_budget_status={summary['request_budget_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
