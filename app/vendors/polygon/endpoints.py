from __future__ import annotations


def daily_aggregates_path(ticker: str, from_date: str, to_date: str) -> str:
    return f"/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"


def intraday_aggregates_path(ticker: str, multiplier: int, timespan: str, from_date: str, to_date: str) -> str:
    return f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"


def ticker_details_path(ticker: str) -> str:
    return f"/v3/reference/tickers/{ticker}"


def reference_tickers_path() -> str:
    return "/v3/reference/tickers"
