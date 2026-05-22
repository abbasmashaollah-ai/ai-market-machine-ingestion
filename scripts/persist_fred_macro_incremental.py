from __future__ import annotations

import argparse
import os
from datetime import date

from app.ingestion.manual.fred_macro_incremental import select_incremental_series_ids
from app.ingestion.manual.fred_macro_incremental_persist import build_manual_fred_macro_incremental_persist
from app.state.manual_fred_macro_checkpoint_store import ManualFREDMacroCheckpointStore
from app.writers.macro_writer import MacroWriter
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _print_summary(summary) -> None:
    for row in summary.series_summaries:
        print(
            f"series_id={row.series_id} "
            f"requested_start_date={row.requested_start_date.isoformat()} "
            f"effective_start_date={row.effective_start_date.isoformat()} "
            f"rows_fetched={row.rows_fetched} "
            f"rows_valid={row.rows_valid} "
            f"rows_invalid={row.rows_invalid} "
            f"rows_written={row.rows_written} "
            f"validation_failures={row.validation_failures} "
            f"planned_start_date={row.planned_start_date.isoformat()} "
            f"planned_end_date={row.planned_end_date.isoformat()} "
            f"write_confirmed={str(row.write_confirmed).lower()} "
            f"status={row.status} "
            f"error_message={row.error_message if row.error_message else 'None'}"
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
    parser = argparse.ArgumentParser(description="Persist incremental FRED macro observations.")
    parser.add_argument("--series-id", action="append", help="Specific FRED series IDs to persist.")
    parser.add_argument("--category", help="Persist a single category.")
    parser.add_argument("--all", action="store_true", help="Persist all active catalog series.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write valid rows.")
    parser.add_argument("--use-checkpoint", action="store_true", help="Load checkpoint state before fetching.")
    parser.add_argument("--update-checkpoint", action="store_true", help="Persist checkpoint state after successful confirmed writes.")
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

    writer = None
    checkpoint_store = None
    connection = None
    try:
        if args.confirm_write or args.use_checkpoint or args.update_checkpoint:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise RuntimeError("DATABASE_URL is required when checkpoint or confirm-write options are used")
            connection = _open_connection(database_url)
            checkpoint_store = ManualFREDMacroCheckpointStore(connection)
            if args.confirm_write:
                writer = MacroWriter(connection)

        summary = build_manual_fred_macro_incremental_persist(
            series_ids=series_ids,
            start_date=_parse_date(args.start_date),
            end_date=_parse_date(args.end_date),
            api_key=api_key,
            writer=writer,
            confirmed_write=args.confirm_write,
            checkpoint_store=checkpoint_store,
            use_checkpoint=args.use_checkpoint,
            update_checkpoint=args.update_checkpoint,
        )
        _print_summary(summary)
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
