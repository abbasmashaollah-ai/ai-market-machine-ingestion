from __future__ import annotations

import argparse
import os
from datetime import date

from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental
from scripts.persist_fred_macro import load_local_env_if_available


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _print_summary(summary) -> None:
    for row in summary.symbol_summaries:
        print(
            f"symbol={row.symbol} "
            f"requested_start_date={row.requested_start_date.isoformat()} "
            f"effective_start_date={row.effective_start_date.isoformat()} "
            f"rows_fetched={row.rows_fetched} "
            f"rows_valid={row.rows_valid} "
            f"rows_invalid={row.rows_invalid} "
            f"validation_failures={row.validation_failures} "
            f"planned_start_date={row.planned_start_date.isoformat()} "
            f"planned_end_date={row.planned_end_date.isoformat()} "
            f"status={row.status}"
        )
    print(
        f"series_total={summary.series_total} "
        f"series_completed={summary.series_completed} "
        f"series_failed={summary.series_failed} "
        f"series_skipped={summary.series_skipped} "
        f"total_rows_fetched={summary.total_rows_fetched} "
        f"total_rows_valid={summary.total_rows_valid} "
        f"total_rows_invalid={summary.total_rows_invalid} "
        f"total_rows_written={summary.total_rows_written} "
        f"total_validation_failures={summary.total_validation_failures}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run Polygon OHLCV incremental fetch/normalize/validate.")
    parser.add_argument("--symbol", action="append", required=True, help="Ticker symbol.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    load_local_env_if_available()
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        raise RuntimeError("POLYGON_API_KEY is required")

    summary = build_manual_polygon_ohlcv_incremental(
        symbols=tuple(args.symbol),
        start_date=_parse_date(args.start_date),
        end_date=_parse_date(args.end_date),
        timeframe=args.timeframe,
        api_key=api_key,
    )
    _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
