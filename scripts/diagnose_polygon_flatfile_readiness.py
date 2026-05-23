from __future__ import annotations

import argparse
from datetime import date


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _storage_root_configured(storage_root: str | None) -> bool:
    return bool(storage_root and storage_root.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file readiness safely.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--storage-root", default=None, help="Optional local storage root.")
    parser.add_argument("--dry-run-only", action="store_true", default=True, help="Read-only dry-run planning mode.")
    args = parser.parse_args()

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    storage_root_configured = _storage_root_configured(args.storage_root)
    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"start_date={start_date.isoformat()}")
    print(f"end_date={end_date.isoformat()}")
    print(f"storage_root_configured={'true' if storage_root_configured else 'false'}")
    print("flatfile_download_enabled=false")
    print("flatfile_parse_enabled=false")
    print("readiness_status=planning_only_not_enabled")
    print("downstream_pipeline=normalization, validation, writer, checkpoint, run_history, quality, lineage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
