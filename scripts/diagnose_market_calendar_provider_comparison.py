from __future__ import annotations

import argparse
from datetime import date, timedelta

from app.market_calendar.mock_calendar_provider import MockMarketCalendarProvider
from app.market_calendar.us_market_calendar import expected_trading_days


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare the minimal market calendar helper with the mock provider.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    args = parser.parse_args()

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)
    comparison_end_date = end_date - timedelta(days=1)
    mock_provider = MockMarketCalendarProvider()
    minimal_days = expected_trading_days(start_date, comparison_end_date)
    mock_days = mock_provider.trading_days(start_date, comparison_end_date)
    matching_dates = [day for day in minimal_days if day in mock_days]
    differing_dates = sorted(set(minimal_days).symmetric_difference(set(mock_days)))

    print(f"exchange={args.exchange}")
    print(f"start_date={start_date.isoformat()}")
    print(f"end_date={end_date.isoformat()}")
    print(f"minimal_trading_days_count={len(minimal_days)}")
    print(f"mock_trading_days_count={len(mock_days)}")
    print(f"matching_dates_count={len(matching_dates)}")
    print(f"differing_dates_count={len(differing_dates)}")
    print(f"differing_dates={','.join(day.isoformat() for day in differing_dates)}")
    print("comparison_status=diagnostic_only")
    print("production_switch_enabled=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
