from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


_CLOSED_DATES = {
    date(2025, 1, 1),
    date(2025, 1, 9),
}

_EARLY_CLOSE_DATES = {
    date(2025, 7, 3),
}

_TIMEZONE = "America/New_York"


def _is_weekend(day: date) -> bool:
    return day.weekday() >= 5


def _regular_open_close(day: date) -> tuple[time, time]:
    return time(9, 30), time(16, 0)


def _early_close_open_close(day: date) -> tuple[time, time]:
    return time(9, 30), time(13, 0)


@dataclass(frozen=True)
class MarketOpenClose:
    open_time: time
    close_time: time
    timezone: str = _TIMEZONE


class MockMarketCalendarProvider:
    def is_trading_day(self, day: date) -> bool:
        return not _is_weekend(day) and day not in _CLOSED_DATES

    def previous_trading_day(self, day: date) -> date:
        cursor = day - timedelta(days=1)
        while not self.is_trading_day(cursor):
            cursor -= timedelta(days=1)
        return cursor

    def next_trading_day(self, day: date) -> date:
        cursor = day + timedelta(days=1)
        while not self.is_trading_day(cursor):
            cursor += timedelta(days=1)
        return cursor

    def trading_days(self, start_date: date, end_date: date) -> list[date]:
        days: list[date] = []
        cursor = start_date
        while cursor <= end_date:
            if self.is_trading_day(cursor):
                days.append(cursor)
            cursor += timedelta(days=1)
        return days

    def market_open_close(self, day: date) -> MarketOpenClose:
        if day in _EARLY_CLOSE_DATES:
            open_time, close_time = _early_close_open_close(day)
        else:
            open_time, close_time = _regular_open_close(day)
        return MarketOpenClose(open_time=open_time, close_time=close_time)

    def is_early_close(self, day: date) -> bool:
        return day in _EARLY_CLOSE_DATES

    def closure_reason(self, day: date) -> str | None:
        if day in _CLOSED_DATES:
            return "holiday_or_known_closure"
        if _is_weekend(day):
            return "weekend"
        return None
