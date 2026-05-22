from __future__ import annotations

import argparse
import os
from datetime import date

from app.ingestion.manual.polygon_ohlcv_incremental import _build_checkpoint_key
from app.state.manual_polygon_ohlcv_checkpoint_store import ManualPolygonOHLCVCheckpointStore
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
        f"symbol={checkpoint.symbol} "
        f"status={checkpoint.status.value} "
        f"planned_start_date={checkpoint.planned_start_date.isoformat()} "
        f"planned_end_date={checkpoint.planned_end_date.isoformat()} "
        f"last_successful_observation_date={checkpoint.last_successful_observation_date.isoformat() if checkpoint.last_successful_observation_date else 'None'} "
        f"updated_at={checkpoint.updated_at.isoformat()}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect manual Polygon OHLCV checkpoint state.")
    parser.add_argument("--symbol", action="append", required=True, help="Ticker symbol.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to inspect manual checkpoint state")

    connection = None
    try:
        connection = _open_connection(database_url)
        store = ManualPolygonOHLCVCheckpointStore(connection)
        found = 0
        for symbol in tuple(args.symbol):
            checkpoint = store.load(
                _build_checkpoint_key(
                    symbol=symbol,
                    timeframe=args.timeframe,
                    start_date=_parse_date(args.start_date),
                    end_date=_parse_date(args.end_date),
                )
            )
            if checkpoint is not None:
                found += 1
            _print_checkpoint(checkpoint)
        print(f"checkpoint_total={len(tuple(args.symbol))} checkpoint_found_total={found}")
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
