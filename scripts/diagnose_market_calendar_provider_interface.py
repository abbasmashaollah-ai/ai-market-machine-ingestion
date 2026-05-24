from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose market calendar provider interface planning without external calls.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    args = parser.parse_args()

    print(f"exchange={args.exchange}")
    print("planned_interface_methods=is_trading_day(date),previous_trading_day(date),next_trading_day(date),trading_days(start_date,end_date),market_open_close(date),is_early_close(date),closure_reason(date)")
    print("provider_interface_status=planning_only_not_enabled")
    print("current_provider=minimal_static_helper")
    print("future_provider=verified_calendar_consumer")
    print("data_owner=ai-market-machine-data")
    print("ingestion_role=read_only_calendar_consumer")
    print("required_before_implementation=data_schema_contract, mock_provider_tests, fallback_behavior, deterministic_fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
