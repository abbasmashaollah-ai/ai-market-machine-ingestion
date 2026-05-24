from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Describe the verified calendar consumer implementation plan.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    args = parser.parse_args()

    print(f"exchange={args.exchange}")
    print("implementation_status=planning_only_not_enabled")
    print("current_minimal_helper_status=manual_only_fallback")
    print("mock_provider_status=test_support_only")
    print("verified_consumer_status=not_implemented")
    print("data_owner=ai-market-machine-data")
    print("ingestion_role=read_only_consumer")
    print(
        "required_next_steps="
        "data_schema_created,calendar_loaded,calendar_verified,read_contract_documented,"
        "consumer_adapter_added,consumer_tests_added"
    )
    print("production_switch_enabled=false")
    print("known_comparison_gap=2025-01-01 closure difference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
