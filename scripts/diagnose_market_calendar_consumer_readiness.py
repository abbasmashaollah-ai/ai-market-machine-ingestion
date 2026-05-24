from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose market calendar consumer readiness without DB access.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    args = parser.parse_args()

    print(f"exchange={args.exchange}")
    print("consumer_enabled=false")
    print("consumer_mode=planning_only_not_enabled")
    print("schema_owner=ai-market-machine-data")
    print("ingestion_role=read_only_consumer")
    print("read_source=planned_table_or_view_or_api")
    print("required_contract_fields=exchange,calendar_date,is_trading_day,open_time,close_time,is_early_close,closure_reason,source,source_version,generated_at,verified_at")
    print("fallback_mode=manual_only_minimal_helper")
    print("consumer_readiness_status=planning_only_not_enabled")
    print("required_before_enablement=data_schema_created,calendar_loaded,calendar_verified,read_contract_documented,consumer_tests_added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
