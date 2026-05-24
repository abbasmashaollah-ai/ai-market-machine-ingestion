from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose market calendar schema handoff planning without DB access.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    args = parser.parse_args()

    print(f"exchange={args.exchange}")
    print("planned_fields=exchange,calendar_date,is_trading_day,open_time,close_time,is_early_close,closure_reason,source,source_version,generated_at,verified_at")
    print("schema_owner=ai-market-machine-data")
    print("ingestion_role=read_only_consumer")
    print("schema_handoff_status=planning_only_not_enabled")
    print("migration_required_in_ingestion=false")
    print("required_before_consumer_integration=data_schema_created,calendar_loaded,calendar_verified,read_contract_documented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
