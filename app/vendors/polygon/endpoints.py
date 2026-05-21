from __future__ import annotations


def daily_aggregates_path(ticker: str, from_date: str, to_date: str) -> str:
    return f"/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"


def intraday_aggregates_path(ticker: str, multiplier: int, timespan: str, from_date: str, to_date: str) -> str:
    return f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"


def ticker_details_path(ticker: str) -> str:
    return f"/v3/reference/tickers/{ticker}"


def reference_tickers_path() -> str:
    return "/v3/reference/tickers"


def daily_aggregates_params(api_key: str | None = None, *, adjusted: bool = True, limit: int | None = None) -> dict[str, str]:
    params: dict[str, str] = {"adjusted": str(adjusted).lower()}
    if api_key is not None:
        params["apiKey"] = api_key
    if limit is not None:
        params["limit"] = str(limit)
    return params


def reference_tickers_params(api_key: str | None = None, *, active: bool | None = None, limit: int | None = None) -> dict[str, str]:
    params: dict[str, str] = {}
    if api_key is not None:
        params["apiKey"] = api_key
    if active is not None:
        params["active"] = str(active).lower()
    if limit is not None:
        params["limit"] = str(limit)
    return params
