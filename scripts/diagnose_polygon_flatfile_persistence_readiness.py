from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file persistence readiness without writing data.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("persistence_enabled=false")
    print("persistence_mode=planning_only_not_enabled")
    print("required_input_state=parsed_validated_integrity_passed")
    print("writer_target=shared_ohlcv_writer")
    print("checkpoint_target=shared_checkpoint_store")
    print("evidence_target=run_history,quality,lineage")
    print("canonical_table_target=canonical_ohlcv")
    print("separate_canonical_path_allowed=false")
    print("persistence_readiness_status=planning_only_not_enabled")
    print(
        "required_before_persistence_enablement=official_layout_verified, download_dry_run_complete, parse_dry_run_complete, validation_passed, manifest_write_enabled, evidence_recording_enabled"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
