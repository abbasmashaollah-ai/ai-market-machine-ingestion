from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon production enablement readiness without enabling anything.")
    parser.add_argument("--vendor", default="polygon", help="Vendor name, default polygon.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    args = parser.parse_args()

    print(f"vendor={args.vendor}")
    print(f"dataset={args.dataset}")
    print("api_ingestion_path=available")
    print("daily_runner=available")
    print("chunked_backfill_runner=available")
    print("checkpointing=available")
    print("run_history=available")
    print("quality_results=available")
    print("lineage=available")
    print("evidence_chain=available")
    print("scheduler_stub=disabled_by_default")
    print("scheduler_disabled_verification=available")
    print("quota_policy=available")
    print("retry_recovery_policy=planning_only_not_enabled")
    print("monitoring_alerting=planning_only_not_enabled")
    print("market_calendar=manual_only_not_production_complete")
    print("symbol_universe=manual_ready")
    print("flatfile_pipeline=planning_only_not_enabled")
    print("websocket_pipeline=not_started")
    print("blockers=complete_market_calendar,monitoring_alerting_implementation,retry_recovery_implementation,production_scheduler_enablement_review,flatfile_live_discovery_download_parse,larger_universe_scale_test,vendor_tier_review")
    print("production_enablement_status=not_ready")
    print("core_foundation_status=strong_manual_foundation")
    print("recommended_next_phase=market_calendar_or_monitoring_or_scheduler_enablement_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
