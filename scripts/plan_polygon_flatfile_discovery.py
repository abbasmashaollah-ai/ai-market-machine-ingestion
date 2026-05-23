from __future__ import annotations

import argparse
from datetime import date

from app.market_calendar.us_market_calendar import expected_trading_days


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _storage_root_configured(storage_root: str | None) -> bool:
    return bool(storage_root and storage_root.strip())


def _candidate_files(*, dataset: str, asset_class: str, timeframe: str, start_date: date, end_date: date) -> list[str]:
    candidates: list[str] = []
    for day in expected_trading_days(start_date, end_date):
        candidates.append(
            f"polygon/flatfiles/{asset_class}/{dataset}/{timeframe}/{day.isoformat()}.parquet"
        )
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan Polygon flat-file discovery safely.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--storage-root", default=None, help="Optional local storage root.")
    args = parser.parse_args()

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    candidate_files = _candidate_files(
        dataset=args.dataset,
        asset_class=args.asset_class,
        timeframe=args.timeframe,
        start_date=start_date,
        end_date=end_date,
    )
    sample_candidates = candidate_files[:5]
    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print(f"start_date={start_date.isoformat()}")
    print(f"end_date={end_date.isoformat()}")
    print(f"expected_trading_days={len(candidate_files)}")
    print(f"candidate_files_count={len(candidate_files)}")
    print(f"storage_root_configured={'true' if _storage_root_configured(args.storage_root) else 'false'}")
    print("discovery_mode=dry_run_only")
    print("readiness_status=planning_only_not_enabled")
    print(f"sample_candidate_files={sample_candidates}")
    print("candidate_layout_note=provisional_and_must_be_reconciled_with_official_polygon_flatfile_layout_before_live_use")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
