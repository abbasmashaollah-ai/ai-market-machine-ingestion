from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file end-to-end readiness without enabling the pipeline.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("official_layout_status=planning_only_not_enabled")
    print("config_status=planning_only_not_enabled")
    print("storage_policy_status=planning_only_not_enabled")
    print("discovery_status=planning_only_not_enabled")
    print("download_status=planning_only_not_enabled")
    print("manifest_status=planning_only_not_enabled")
    print("integrity_status=planning_only_not_enabled")
    print("quarantine_status=planning_only_not_enabled")
    print("parse_status=planning_only_not_enabled")
    print("persistence_status=planning_only_not_enabled")
    print("flatfile_e2e_status=planning_only_not_enabled")
    print("live_flatfile_pipeline_enabled=false")
    print("api_path_current_live=true")
    print("flatfiles_future_historical_backfill=true")
    print("websocket_future_live_streaming=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
