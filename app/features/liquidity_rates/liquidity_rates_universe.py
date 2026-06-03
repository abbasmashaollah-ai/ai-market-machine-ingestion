"""Liquidity/rates series universe helpers."""

from __future__ import annotations


LIQUIDITY_RATES_SERIES = (
    "FED_FUNDS",
    "US10Y",
    "US2Y",
    "REAL_YIELD_10Y",
    "DXY",
    "HYG",
    "SPY",
    "M2",
    "QT_QE_PROXY",
)


def get_liquidity_rates_series() -> tuple[str, ...]:
    return LIQUIDITY_RATES_SERIES


def get_required_liquidity_rates_series() -> tuple[str, ...]:
    return LIQUIDITY_RATES_SERIES


def is_liquidity_rates_series(series) -> bool:
    return str(series).strip().upper() in LIQUIDITY_RATES_SERIES