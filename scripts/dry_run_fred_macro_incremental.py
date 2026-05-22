from __future__ import annotations

import argparse
import os
from datetime import date

from app.ingestion.manual.fred_macro_incremental import select_incremental_series_ids
from app.ingestion.manual.fred_macro_dry_run import build_manual_fred_macro_incremental_dry_run, ManualFREDMacroIncrementalDryRun


def load_local_env_if_available() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    return bool(load_dotenv())


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _print_summary(summary: ManualFREDMacroIncrementalDryRun) -> None:
    for row in summary.series_summaries:
        print(
            f"series_id={row.series_id} "
            f"rows_fetched={row.rows_fetched} "
            f"rows_valid={row.rows_valid} "
            f"rows_invalid={row.rows_invalid} "
            f"validation_failures={row.validation_failures} "
            f"planned_start_date={row.planned_start_date.isoformat()} "
            f"planned_end_date={row.planned_end_date.isoformat()}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run manual FRED macro incremental updates.")
    parser.add_argument("--series-id", nargs="*", help="Specific FRED series IDs to dry run.")
    parser.add_argument("--category", help="Dry run a single category.")
    parser.add_argument("--all", action="store_true", help="Dry run all active catalog series.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    args = parser.parse_args()

    load_local_env_if_available()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is required")
    series_ids = select_incremental_series_ids(
        series_ids=tuple(args.series_id) if args.series_id else None,
        category=args.category,
        include_all=args.all,
    )
    summary = build_manual_fred_macro_incremental_dry_run(
        series_ids=series_ids,
        start_date=_parse_date(args.start_date),
        end_date=_parse_date(args.end_date),
        api_key=api_key,
    )
    _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
