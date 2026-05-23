from __future__ import annotations

from datetime import date, timedelta


# This is intentionally small and explicit for now. It is not a full exchange calendar.
KNOWN_CLOSURES = {
    date(2025, 1, 9),
}


def expected_trading_days(start_date: date, end_date: date) -> list[date]:
    days: list[date] = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5 and current not in KNOWN_CLOSURES:
            days.append(current)
        current += timedelta(days=1)
    return days
