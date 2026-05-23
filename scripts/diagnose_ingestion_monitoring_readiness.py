from __future__ import annotations

import argparse


def _planned_or_available() -> str:
    return "planned_or_available"


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose ingestion monitoring readiness without enabling alerts.")
    parser.add_argument("--vendor", default="polygon", help="Vendor name, default polygon.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    args = parser.parse_args()

    print(f"vendor={args.vendor}")
    print(f"dataset={args.dataset}")
    print("monitoring_enabled=false")
    print("alerting_enabled=false")
    print(f"run_history_available={_planned_or_available()}")
    print(f"quality_results_available={_planned_or_available()}")
    print(f"lineage_available={_planned_or_available()}")
    print(f"evidence_verification_available={_planned_or_available()}")
    print("required_alerts=failed_run,rate_limit,missing_coverage,quality_failed,lineage_missing,scheduler_disabled,scheduler_blocked")
    print("required_metrics=rows_fetched,rows_written,rows_rejected,error_count,coverage_ratio,latency_seconds,request_count")
    print("monitoring_readiness_status=planning_only_not_enabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
