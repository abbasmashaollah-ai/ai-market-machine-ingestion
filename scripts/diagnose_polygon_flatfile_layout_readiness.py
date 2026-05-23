from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnose Polygon flat-file layout readiness without contacting external systems."
    )
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("current_layout_mode=provisional")
    print("official_layout_verified=false")
    print("live_discovery_enabled=false")
    print("live_download_enabled=false")
    print("readiness_status=blocked_until_official_layout_verified")
    print(
        "required_next_steps=obtain_official_polygon_flatfile_layout, map_dataset_paths, add_mocked_layout_tests, add_download_dry_run"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
