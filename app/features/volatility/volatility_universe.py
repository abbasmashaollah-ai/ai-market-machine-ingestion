"""Universe helpers for volatility series."""

from __future__ import annotations

VOLATILITY_SERIES = ("VIX", "VVIX", "VXN", "RVX")


def get_volatility_series() -> tuple[str, ...]:
    return VOLATILITY_SERIES


def get_required_volatility_series() -> tuple[str, ...]:
    return VOLATILITY_SERIES


def is_volatility_series(series: str) -> bool:
    return str(series).strip().upper() in VOLATILITY_SERIES
