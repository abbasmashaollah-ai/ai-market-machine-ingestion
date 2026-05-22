from __future__ import annotations

import argparse
from datetime import date

from app.ingestion.manual.fred_macro_incremental import select_incremental_series_ids
from app.ingestion.manual.fred_macro_preview import build_manual_fred_macro_incremental_preview


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _print_preview(preview) -> None:
    print(f"plan_id={preview.plan.plan_id}")
    print(f"series_ids={preview.plan.series_ids}")
    print(f"start_date={preview.plan.start_date.isoformat()}")
    print(f"end_date={preview.plan.end_date.isoformat()}")
    print(f"checkpoint_keys={preview.plan.checkpoint_keys}")
    for checkpoint in preview.checkpoints:
        print(
            f"checkpoint_key={checkpoint.checkpoint_key} "
            f"series_id={checkpoint.series_id} "
            f"status={checkpoint.status.value} "
            f"planned_start_date={checkpoint.planned_start_date.isoformat()} "
            f"planned_end_date={checkpoint.planned_end_date.isoformat()}"
        )
    for result in preview.results:
        print(
            f"result checkpoint_key={result.checkpoint_key} "
            f"series_id={result.series_id} "
            f"status={result.status.value} "
            f"rows_planned={result.rows_planned} "
            f"rows_fetched={result.rows_fetched} "
            f"rows_valid={result.rows_valid} "
            f"rows_invalid={result.rows_invalid} "
            f"rows_written={result.rows_written} "
            f"validation_failures={result.validation_failures}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview a manual FRED macro incremental run in memory.")
    parser.add_argument("--series-id", nargs="*", help="Specific FRED series IDs to preview.")
    parser.add_argument("--category", help="Preview a single category.")
    parser.add_argument("--all", action="store_true", help="Preview all active catalog series.")
    parser.add_argument("--start-date", required=True, help="Planned start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="Planned end date in YYYY-MM-DD format.")
    args = parser.parse_args()

    selected_series_ids = select_incremental_series_ids(
        series_ids=tuple(args.series_id) if args.series_id else None,
        category=args.category,
        include_all=args.all,
    )
    preview = build_manual_fred_macro_incremental_preview(
        plan_id="manual-preview",
        start_date=_parse_date(args.start_date),
        end_date=_parse_date(args.end_date),
        series_ids=selected_series_ids,
        category=args.category,
        include_all=args.all,
    )
    _print_preview(preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
