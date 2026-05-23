from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose ingestion retry and recovery readiness without enabling retries.")
    parser.add_argument("--vendor", default="polygon", help="Vendor name, default polygon.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    args = parser.parse_args()

    print(f"vendor={args.vendor}")
    print(f"dataset={args.dataset}")
    print("retry_enabled=false")
    print("automatic_recovery_enabled=false")
    print("manual_recovery_supported=planned")
    print("checkpoint_recovery_available=available")
    print("run_history_required=true")
    print("quality_required=true")
    print("lineage_required=true")
    print("retry_policy_status=planning_only_not_enabled")
    print(
        "required_failure_classes=rate_limit,vendor_http_error,validation_failed,coverage_missing,checkpoint_missing,lineage_missing,quality_failed,storage_integrity_failed,parse_failed"
    )
    print(
        "required_recovery_actions=retry_later,resume_from_checkpoint,reduce_scope,quarantine,manual_review,skip_non_trading_day,rebuild_evidence"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
