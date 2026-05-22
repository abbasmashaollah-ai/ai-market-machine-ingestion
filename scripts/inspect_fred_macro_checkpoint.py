from __future__ import annotations

import argparse
import os
from datetime import date

from app.ingestion.manual.fred_macro_incremental import select_incremental_series_ids
from app.ingestion.manual.fred_macro_incremental_persist import _build_checkpoint_key
from app.state.manual_fred_macro_checkpoint_store import ManualFREDMacroCheckpointStore
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _print_checkpoint(checkpoint) -> None:
    if checkpoint is None:
        print("checkpoint_found=false")
        return
    print(
        f"checkpoint_found=true "
        f"checkpoint_key={checkpoint.checkpoint_key} "
        f"series_id={checkpoint.series_id} "
        f"status={checkpoint.status.value} "
        f"planned_start_date={checkpoint.planned_start_date.isoformat()} "
        f"planned_end_date={checkpoint.planned_end_date.isoformat()} "
        f"last_successful_observation_date="
        f"{checkpoint.last_successful_observation_date.isoformat() if checkpoint.last_successful_observation_date else 'None'} "
        f"updated_at={checkpoint.updated_at.isoformat()}"
    )


def _print_aggregate(total: int, found: int) -> None:
    print(f"checkpoint_total={total} checkpoint_found_total={found}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect manual FRED macro checkpoint state.")
    parser.add_argument("--series-id", action="append", help="FRED series ID.")
    parser.add_argument("--category", help="Inspect a single category.")
    parser.add_argument("--all", action="store_true", help="Inspect all active catalog series.")
    parser.add_argument("--start-date", required=True, help="Planned start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="Planned end date in YYYY-MM-DD format.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to inspect manual checkpoint state")

    connection = None
    try:
        connection = _open_connection(database_url)
        checkpoint_store = ManualFREDMacroCheckpointStore(connection)
        series_ids = select_incremental_series_ids(
            series_ids=tuple(args.series_id) if args.series_id else None,
            category=args.category,
            include_all=args.all,
        )
        found = 0
        for series_id in series_ids:
            checkpoint = checkpoint_store.load(
                _build_checkpoint_key(
                    series_id=series_id,
                    start_date=_parse_date(args.start_date),
                    end_date=_parse_date(args.end_date),
                )
            )
            if checkpoint is not None:
                found += 1
            _print_checkpoint(checkpoint)
        _print_aggregate(len(series_ids), found)
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
