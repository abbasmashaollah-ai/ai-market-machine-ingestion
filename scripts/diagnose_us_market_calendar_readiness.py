from __future__ import annotations

import argparse
from datetime import date, timedelta

from app.market_calendar.us_market_calendar import KNOWN_CLOSURES, expected_trading_days


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose US market calendar readiness safely.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    args = parser.parse_args()

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    expected_days = expected_trading_days(start_date, end_date)
    excluded_weekend_days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() >= 5:
            excluded_weekend_days += 1
        current += timedelta(days=1)

    known_closure_days = [day.isoformat() for day in KNOWN_CLOSURES if start_date <= day <= end_date]
    print(f"start_date={start_date.isoformat()}")
    print(f"end_date={end_date.isoformat()}")
    print(f"expected_trading_days={len(expected_days)}")
    print(f"excluded_weekend_days={excluded_weekend_days}")
    print(f"known_closure_days={known_closure_days}")
    print("calendar_mode=minimal_explicit_closures")
    print("calendar_readiness_status=manual_only_not_production_complete")
    print("missing_capabilities=holiday_calendar, early_close_calendar, exchange_schedule_source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
