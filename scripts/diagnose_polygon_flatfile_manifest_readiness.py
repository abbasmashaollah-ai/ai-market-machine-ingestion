from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file manifest readiness without writing manifests.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("object_key=planned")
    print("local_raw_path=planned")
    print("local_staging_path=planned")
    print("checksum=planned")
    print("size_bytes=planned")
    print("discovered_at=planned")
    print("downloaded_at=planned")
    print("parsed_at=planned")
    print("validation_status=planned")
    print("quarantine_status=planned")
    print("lineage_status=planned")
    print("manifest_enabled=false")
    print("manifest_write_enabled=false")
    print("readiness_status=planning_only_not_enabled")
    print(
        "required_before_enablement=official_layout_verified, storage_policy_reviewed, checksum_policy_defined, cleanup_policy_defined"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
