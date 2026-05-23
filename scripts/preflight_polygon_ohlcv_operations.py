from __future__ import annotations

import argparse
import os
from datetime import date, timedelta

from scripts.persist_fred_macro import _open_connection, load_local_env_if_available
from scripts.plan_polygon_ohlcv_daily_update import (
    DEFAULT_SYMBOLS,
    _as_date as _as_date_daily,
    _build_latest_existing_query,
    _exclusive_end_date,
    _latest_expected_trading_day,
    _parse_date,
)
from scripts.plan_polygon_ohlcv_symbol_universe import _latest_existing_date as _latest_existing_date_from_rows
from scripts.verify_polygon_ohlcv_evidence_chain import (
    _canonical_query,
    _coverage,
    _evidence_status,
    _lineage_fallback_query,
    _quality_fallback_query,
    _run_fallback_query,
    _load_with_fallback,
)


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


def _format_date(value: date | None) -> str:
    return value.isoformat() if value is not None else "None"


def _request_budget_status(*, estimated_vendor_requests: int, max_requests: int | None) -> str:
    if max_requests is None:
        return "within_budget"
    return "within_budget" if estimated_vendor_requests <= max_requests else "exceeds_budget"


def _build_daily_update_command(*, symbol: str, as_of_date: date, timeframe: str, source: str, max_requests: int) -> str:
    return (
        f"python -m scripts.run_polygon_ohlcv_daily_update --symbol {symbol} --as-of-date {as_of_date.isoformat()} "
        f"--timeframe {timeframe} --source {source} --max-requests {max_requests}"
    )


def _build_chunked_backfill_command(
    *, symbol: str, as_of_date: date, timeframe: str, source: str, chunk_days: int, max_requests: int
) -> str:
    return (
        f"python -m scripts.run_polygon_ohlcv_chunked_backfill --symbol {symbol} --start-date {as_of_date.isoformat()} "
        f"--end-date {as_of_date.isoformat()} --timeframe {timeframe} --chunk-days {chunk_days} "
        f"--max-requests {max_requests} --source {source}"
    )


def _build_evidence_command(*, symbol: str, start_date: date, end_date: date, timeframe: str) -> str:
    return (
        f"python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol {symbol} --start-date {start_date.isoformat()} "
        f"--end-date {end_date.isoformat()} --timeframe {timeframe}"
    )


def _recommended_action(
    *,
    budget_status: str,
    update_mode: str,
    evidence_status: str | None,
    symbol: str,
    as_of_date: date,
    timeframe: str,
    source: str,
    chunk_days: int,
    max_requests: int,
) -> tuple[str, str | None]:
    if budget_status == "exceeds_budget":
        return "reduce_scope_or_raise_budget", None
    if update_mode == "no_expected_trading_day":
        return "no_trading_day", None
    if update_mode == "up_to_date" and evidence_status == "complete":
        return "no_action_needed", None
    if update_mode == "incremental_update_needed":
        action = "run_daily_update"
        command = _build_daily_update_command(
            symbol=symbol,
            as_of_date=as_of_date,
            timeframe=timeframe,
            source=source,
            max_requests=max_requests,
        )
        if evidence_status in {"missing", "partial"}:
            command += " --record-run --record-quality --record-lineage"
        return action, command
    if update_mode == "no_existing_data":
        return (
            "run_small_backfill_or_daily_update",
            _build_daily_update_command(
                symbol=symbol,
                as_of_date=as_of_date,
                timeframe=timeframe,
                source=source,
                max_requests=max_requests,
            ),
        )
    if evidence_status in {"missing", "partial"}:
        return (
            "verify_or_record_evidence",
            _build_evidence_command(symbol=symbol, start_date=as_of_date, end_date=as_of_date, timeframe=timeframe),
        )
    if update_mode == "historical_gap_detected":
        return (
            "run_small_backfill_or_daily_update",
            _build_chunked_backfill_command(
                symbol=symbol,
                as_of_date=as_of_date,
                timeframe=timeframe,
                source=source,
                chunk_days=chunk_days,
                max_requests=max_requests,
            ),
        )
    return "manual_review", None


def build_preflight_report(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if args.check_existing and not database_url:
        raise RuntimeError("DATABASE_URL is required when --check-existing is used")

    symbols = tuple(args.symbol) if args.symbol else DEFAULT_SYMBOLS
    as_of_date = _parse_date(args.as_of_date)
    latest_expected = _latest_expected_trading_day(as_of_date)

    per_symbol: list[dict[str, object]] = []
    estimated_total_requests = 0
    symbols_ready = 0
    symbols_needing_update = 0
    symbols_with_complete_evidence = 0
    symbols_requiring_manual_review = 0
    next_step_counts: dict[str, int] = {
        "run_daily_update": 0,
        "reduce_scope_or_raise_budget": 0,
        "verify_evidence": 0,
        "no_action_needed": 0,
        "manual_review": 0,
    }

    connection = None
    try:
        if args.check_existing:
            connection = _open_connection(database_url)  # type: ignore[arg-type]
        for index, symbol in enumerate(symbols):
            universe_status = "selected" if index < args.max_symbols else "exceeds_cap"
            latest_existing_date = None
            update_mode = "no_existing_data"
            evidence_status = None
            estimated_requests = 0

            if args.check_existing and connection is not None:
                universe_rows = _fetch_all(
                    connection,
                    _build_latest_existing_query(args.source)[0],
                    (symbol, args.timeframe, _exclusive_end_date(as_of_date), args.source),
                )
                latest_existing_date = _latest_existing_date_from_rows(universe_rows)
                if latest_expected is None:
                    update_mode = "no_expected_trading_day"
                elif latest_existing_date is None:
                    update_mode = "no_existing_data"
                elif latest_existing_date >= latest_expected:
                    update_mode = "up_to_date"
                else:
                    gap_days = (latest_expected - latest_existing_date).days
                    update_mode = "historical_gap_detected" if gap_days > 5 else "incremental_update_needed"

                canonical_rows = _fetch_all(
                    connection,
                    _canonical_query(),
                    (symbol, as_of_date, _exclusive_end_date(as_of_date), args.timeframe),
                )
                coverage = _coverage(canonical_rows, as_of_date, as_of_date)
                run_rows, _ = _load_with_fallback(
                    connection=connection,
                    exact_sql=_run_fallback_query(),
                    exact_params=("polygon", "ohlcv", args.max_requests),
                    fallback_sql=_run_fallback_query(),
                    fallback_params=("polygon", "ohlcv", args.max_requests),
                )
                quality_rows, _ = _load_with_fallback(
                    connection=connection,
                    exact_sql=_quality_fallback_query(),
                    exact_params=("polygon", "ohlcv", symbol, args.timeframe, args.max_requests),
                    fallback_sql=_quality_fallback_query(),
                    fallback_params=("polygon", "ohlcv", symbol, args.timeframe, args.max_requests),
                )
                lineage_rows, _ = _load_with_fallback(
                    connection=connection,
                    exact_sql=_lineage_fallback_query(),
                    exact_params=("polygon", "ohlcv", symbol, args.timeframe, args.max_requests),
                    fallback_sql=_lineage_fallback_query(),
                    fallback_params=("polygon", "ohlcv", symbol, args.timeframe, args.max_requests),
                )
                evidence_status = _evidence_status(
                    canonical_count=len(canonical_rows),
                    run_count=len(run_rows),
                    quality_count=len(quality_rows),
                    lineage_count=len(lineage_rows),
                    missing_dates=coverage["missing"],
                )

            if update_mode in {"incremental_update_needed", "no_existing_data"}:
                estimated_requests = 1
            elif update_mode == "historical_gap_detected":
                estimated_requests = 2
            estimated_total_requests += estimated_requests

            if index >= args.max_symbols:
                universe_status = "exceeds_cap"

            if universe_status == "selected" and update_mode == "up_to_date" and evidence_status == "complete":
                symbols_ready += 1
            else:
                symbols_requiring_manual_review += 1
            if update_mode in {"incremental_update_needed", "historical_gap_detected", "no_existing_data"}:
                symbols_needing_update += 1
            if evidence_status == "complete":
                symbols_with_complete_evidence += 1

            budget_status = _request_budget_status(estimated_vendor_requests=estimated_total_requests, max_requests=args.max_requests)
            recommended_action, recommended_command = _recommended_action(
                budget_status=budget_status,
                update_mode=update_mode,
                evidence_status=evidence_status,
                symbol=symbol,
                as_of_date=as_of_date,
                timeframe=args.timeframe,
                source=args.source,
                chunk_days=10,
                max_requests=args.max_requests,
            )
            next_step_key = (
                "reduce_scope_or_raise_budget"
                if budget_status == "exceeds_budget"
                else "no_action_needed"
                if recommended_action == "no_action_needed"
                else "verify_evidence"
                if recommended_action == "verify_or_record_evidence"
                else "run_daily_update"
                if recommended_action in {"run_daily_update", "run_small_backfill_or_daily_update"}
                else "manual_review"
            )
            next_step_counts[next_step_key] += 1
            per_symbol.append(
                {
                    "symbol": symbol,
                    "universe_status": universe_status,
                    "update_mode": update_mode,
                    "latest_existing_date": latest_existing_date,
                    "evidence_status": evidence_status,
                    "estimated_requests": estimated_requests,
                    "recommended_action": recommended_action,
                    "recommended_command": recommended_command,
                }
            )
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()

    request_budget_status = _request_budget_status(estimated_vendor_requests=estimated_total_requests, max_requests=args.max_requests)
    if request_budget_status == "exceeds_budget":
        preflight_status = "blocked"
    elif symbols_requiring_manual_review == 0:
        preflight_status = "ready"
    else:
        preflight_status = "manual_review_needed"
    recommended_next_step = "manual_review"
    if request_budget_status == "exceeds_budget":
        recommended_next_step = "reduce_scope_or_raise_budget"
    elif next_step_counts["run_daily_update"]:
        recommended_next_step = "run_daily_update"
    elif next_step_counts["verify_evidence"]:
        recommended_next_step = "verify_evidence"
    elif next_step_counts["no_action_needed"]:
        recommended_next_step = "no_action_needed"

    summary = {
        "symbols_total": len(symbols),
        "symbols_ready": symbols_ready,
        "symbols_needing_update": symbols_needing_update,
        "symbols_with_complete_evidence": symbols_with_complete_evidence,
        "symbols_requiring_manual_review": symbols_requiring_manual_review,
        "estimated_total_requests": estimated_total_requests,
        "request_budget_status": request_budget_status,
        "preflight_status": preflight_status,
        "recommended_next_step": recommended_next_step,
    }
    return per_symbol, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight Polygon OHLCV operations safely.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source", default="polygon_aggregates", help="Source filter, default polygon_aggregates.")
    parser.add_argument("--max-symbols", type=int, default=25, help="Maximum symbol count, default 25.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum request budget, default 10.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing canonical coverage if DATABASE_URL is available.")
    args = parser.parse_args()

    per_symbol, summary = build_preflight_report(args)
    for item in per_symbol:
        print(
            f"symbol={item['symbol']} "
            f"universe_status={item['universe_status']} "
            f"update_mode={item['update_mode']} "
            f"latest_existing_date={_format_date(item['latest_existing_date'])} "
            f"evidence_status={item['evidence_status'] if item['evidence_status'] is not None else 'None'} "
            f"estimated_requests={item['estimated_requests']} "
            f"recommended_action={item['recommended_action']} "
            f"recommended_command={item['recommended_command'] if item['recommended_command'] is not None else 'None'}"
        )

    print(
        f"symbols_total={summary['symbols_total']} "
        f"symbols_ready={summary['symbols_ready']} "
        f"symbols_needing_update={summary['symbols_needing_update']} "
        f"symbols_with_complete_evidence={summary['symbols_with_complete_evidence']} "
        f"symbols_requiring_manual_review={summary['symbols_requiring_manual_review']} "
        f"estimated_total_requests={summary['estimated_total_requests']} "
        f"request_budget_status={summary['request_budget_status']} "
        f"preflight_status={summary['preflight_status']} "
        f"recommended_next_step={summary['recommended_next_step']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
