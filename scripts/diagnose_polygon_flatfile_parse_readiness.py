from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file parse readiness without reading files.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("parse_enabled=false")
    print("parse_mode=dry_run_planning_only")
    print("required_input_state=downloaded_and_integrity_passed")
    print("required_columns=symbol,timestamp,open,high,low,close,volume")
    print("normalization_target=shared_ohlcv_normalization")
    print("validation_target=shared_ohlcv_validation")
    print("writer_target=shared_ohlcv_writer")
    print("evidence_target=run_history,quality,lineage")
    print("parse_readiness_status=planning_only_not_enabled")
    print(
        "required_before_parse_enablement=official_layout_verified, download_dry_run_complete, integrity_policy_defined, quarantine_policy_defined"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
