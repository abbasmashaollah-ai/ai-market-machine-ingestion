from __future__ import annotations

import argparse
import os
from datetime import date, timedelta

from app.market_calendar.us_market_calendar import expected_trading_days
from scripts.evidence_chain_helpers import evidence_status_from_counts, status_from_requirement
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


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


def _canonical_query() -> str:
    return (
        "SELECT symbol, timestamp, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp < %s AND timeframe = %s "
        "ORDER BY timestamp ASC"
    )


def _run_exact_query() -> str:
    return (
        "SELECT run_id, job_id, status, started_at, finished_at "
        "FROM ingestion_runs "
        "WHERE vendor = %s AND dataset = %s AND symbol = %s AND started_at >= %s AND finished_at < %s "
        "ORDER BY finished_at DESC NULLS LAST, started_at DESC NULLS LAST "
        "LIMIT %s"
    )


def _run_fallback_query() -> str:
    return (
        "SELECT run_id, job_id, status, started_at, finished_at "
        "FROM ingestion_runs "
        "WHERE vendor = %s AND dataset = %s AND symbol = %s "
        "ORDER BY finished_at DESC NULLS LAST, started_at DESC NULLS LAST "
        "LIMIT %s"
    )


def _quality_exact_query() -> str:
    return (
        "SELECT status, severity, created_at "
        "FROM data_quality_results "
        "WHERE vendor = %s AND dataset = %s AND symbol = %s AND timeframe = %s AND created_at >= %s AND created_at < %s "
        "ORDER BY created_at DESC "
        "LIMIT %s"
    )


def _quality_fallback_query() -> str:
    return (
        "SELECT status, severity, created_at "
        "FROM data_quality_results "
        "WHERE vendor = %s AND dataset = %s AND symbol = %s AND timeframe = %s "
        "ORDER BY created_at DESC "
        "LIMIT %s"
    )


def _lineage_exact_query() -> str:
    return (
        "SELECT quality_status, created_at "
        "FROM data_lineage "
        "WHERE vendor = %s AND dataset = %s AND symbol = %s AND timeframe = %s AND created_at >= %s AND created_at < %s "
        "ORDER BY created_at DESC "
        "LIMIT %s"
    )


def _lineage_fallback_query() -> str:
    return (
        "SELECT quality_status, created_at "
        "FROM data_lineage "
        "WHERE vendor = %s AND dataset = %s AND symbol = %s AND timeframe = %s "
        "ORDER BY created_at DESC "
        "LIMIT %s"
    )


def _ordered_unique(values: list[object]) -> list[object]:
    seen: list[object] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return seen


def _coverage(rows: list[dict[str, object]], start_date: date, end_date: date) -> dict[str, object]:
    expected = expected_trading_days(start_date, end_date)
    observed = []
    for row in rows:
        ts = row.get("timestamp")
        if hasattr(ts, "date"):
            observed.append(ts.date())
        elif isinstance(ts, date):
            observed.append(ts)
    observed = [day for day in _ordered_unique(observed) if isinstance(day, date)]
    missing = [day for day in expected if day not in observed]
    return {
        "expected": expected,
        "observed": observed,
        "missing": missing,
        "coverage_ratio": (len(expected) - len(missing)) / len(expected) if expected else 0.0,
    }


def _load_with_fallback(
    *,
    connection: object,
    exact_sql: str,
    exact_params: tuple[object, ...],
    fallback_sql: str,
    fallback_params: tuple[object, ...],
) -> tuple[list[dict[str, object]], str]:
    exact_rows = _fetch_all(connection, exact_sql, exact_params)
    if exact_rows:
        return exact_rows, "exact"
    fallback_rows = _fetch_all(connection, fallback_sql, fallback_params)
    if fallback_rows:
        return fallback_rows, "fallback"
    return [], "none"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the FMP OHLCV evidence chain safely.")
    parser.add_argument("--symbol", required=True, help="Ticker symbol.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--confirmed-write", action="store_true", help="Require canonical rows for the inspected window.")
    parser.add_argument("--record-run", action="store_true", help="Require run history rows for the inspected window.")
    parser.add_argument("--record-quality", action="store_true", help="Require quality rows for the inspected window.")
    parser.add_argument("--record-lineage", action="store_true", help="Require lineage rows for the inspected window.")
    parser.add_argument("--limit", type=int, default=3, help="Maximum operational records to inspect, default 3.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    exclusive_end = end_date + timedelta(days=1)
    connection = _open_connection(database_url)
    try:
        canonical_rows = _fetch_all(connection, _canonical_query(), (args.symbol, start_date, exclusive_end, args.timeframe))
        coverage = _coverage(canonical_rows, start_date, end_date)
        run_rows, run_match_mode = _load_with_fallback(
            connection=connection,
            exact_sql=_run_exact_query(),
            exact_params=("fmp", "ohlcv", args.symbol, start_date, exclusive_end, args.limit),
            fallback_sql=_run_fallback_query(),
            fallback_params=("fmp", "ohlcv", args.symbol, args.limit),
        )
        quality_rows, quality_match_mode = _load_with_fallback(
            connection=connection,
            exact_sql=_quality_exact_query(),
            exact_params=("fmp", "ohlcv", args.symbol, args.timeframe, start_date, exclusive_end, args.limit),
            fallback_sql=_quality_fallback_query(),
            fallback_params=("fmp", "ohlcv", args.symbol, args.timeframe, args.limit),
        )
        lineage_rows, lineage_match_mode = _load_with_fallback(
            connection=connection,
            exact_sql=_lineage_exact_query(),
            exact_params=("fmp", "ohlcv", args.symbol, args.timeframe, start_date, exclusive_end, args.limit),
            fallback_sql=_lineage_fallback_query(),
            fallback_params=("fmp", "ohlcv", args.symbol, args.timeframe, args.limit),
        )
        _evidence_shape = evidence_status_from_counts(
            canonical_count=len(canonical_rows),
            run_count=len(run_rows),
            quality_count=len(quality_rows),
            lineage_count=len(lineage_rows),
            missing_dates=coverage["missing"],
        )

        latest_run_status = run_rows[0].get("status") if run_rows else None
        latest_quality_status = quality_rows[0].get("status") if quality_rows else None
        latest_lineage_quality_status = lineage_rows[0].get("quality_status") if lineage_rows else None

        canonical_status = status_from_requirement(required=args.confirmed_write, present=bool(canonical_rows))
        if args.confirmed_write and canonical_rows and not coverage["missing"]:
            canonical_status = "PASS"

        run_status = status_from_requirement(required=args.record_run, present=bool(run_rows))
        quality_status = status_from_requirement(required=args.record_quality, present=bool(quality_rows))
        lineage_status = status_from_requirement(required=args.record_lineage, present=bool(lineage_rows))
        component_statuses = [canonical_status, run_status, quality_status, lineage_status]
        evidence_status = "FAIL" if "FAIL" in component_statuses else "WARN" if "WARN" in component_statuses else "PASS"

        print(
            f"symbol={args.symbol} "
            f"timeframe={args.timeframe} "
            f"start_date={start_date.isoformat()} "
            f"end_date={end_date.isoformat()} "
            f"row_count={len(canonical_rows)} "
            f"coverage_ratio={coverage['coverage_ratio']:.3f} "
            f"missing_dates={[day.isoformat() for day in coverage['missing']]} "
            f"canonical_status={canonical_status} "
            f"latest_run_status={latest_run_status} "
            f"run_status={run_status} "
            f"run_match_mode={run_match_mode} "
            f"quality_results_count={len(quality_rows)} "
            f"latest_quality_status={latest_quality_status} "
            f"quality_status={quality_status} "
            f"quality_match_mode={quality_match_mode} "
            f"lineage_rows_count={len(lineage_rows)} "
            f"latest_lineage_quality_status={latest_lineage_quality_status} "
            f"lineage_status={lineage_status} "
            f"lineage_match_mode={lineage_match_mode} "
            f"evidence_status={evidence_status}"
        )
    finally:
        if hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
