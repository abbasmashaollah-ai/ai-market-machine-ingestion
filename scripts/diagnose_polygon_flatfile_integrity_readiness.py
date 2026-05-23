from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file integrity readiness without inspecting files.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("checksum_policy_defined=false")
    print("checksum_algorithm=planned")
    print("size_check_required=true")
    print("empty_file_check_required=true")
    print("schema_probe_required=true")
    print("quarantine_policy_required=true")
    print("manifest_integration_required=true")
    print("integrity_readiness_status=planning_only_not_enabled")
    print("required_before_download_enablement=checksum_policy_defined, quarantine_policy_defined, manifest_write_enabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
