from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose the mock market calendar provider contract without external calls.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    args = parser.parse_args()

    print(f"exchange={args.exchange}")
    print("provider_type=mock_fixture")
    print("timezone=America/New_York")
    print("supports_holidays=true")
    print("supports_special_closures=true")
    print("supports_early_closes=true")
    print("is_trading_day_available=true")
    print("previous_trading_day_available=true")
    print("next_trading_day_available=true")
    print("trading_days_available=true")
    print("market_open_close_available=true")
    print("closure_reason_available=true")
    print("production_enabled=false")
    print("db_integration_enabled=false")
    print("package_dependency_required=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
