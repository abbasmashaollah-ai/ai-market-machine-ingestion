from __future__ import annotations

from datetime import date


def is_weekend(trading_date: date) -> bool:
    return trading_date.weekday() >= 5


def is_market_day(trading_date: date) -> bool:
    return not is_weekend(trading_date)

