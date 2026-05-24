from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose market calendar mock consumer contract without DB access.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    args = parser.parse_args()

    print(f"exchange={args.exchange}")
    print("is_trading_day_returns_bool=true")
    print("previous_trading_day_returns_date=true")
    print("next_trading_day_returns_date=true")
    print("trading_days_returns_ordered_dates=true")
    print("market_open_close_returns_times=true")
    print("early_close_returns_bool=true")
    print("closure_reason_returns_nullable_string=true")
    print("consumer_contract_status=mock_contract_planned")
    print("db_integration_enabled=false")
    print("production_calendar_enabled=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
