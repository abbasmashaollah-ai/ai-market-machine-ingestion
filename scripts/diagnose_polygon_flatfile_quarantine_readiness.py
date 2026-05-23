from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file quarantine readiness without touching files.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("quarantine_enabled=false")
    print("quarantine_write_enabled=false")
    print("quarantine_reason_codes=checksum_failed,size_check_failed,empty_file,schema_probe_failed,parse_failed,manual_review")
    print("quarantine_manifest_required=true")
    print("quarantine_retention_policy_defined=false")
    print("quarantine_replay_policy_defined=false")
    print("quarantine_readiness_status=planning_only_not_enabled")
    print(
        "required_before_enablement=storage_policy_reviewed, manifest_write_enabled, integrity_policy_defined, retention_policy_defined"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
