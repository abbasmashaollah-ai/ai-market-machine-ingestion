"""Pure cross-asset and intermarket calculations for dry-run feature building."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def _as_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def calculate_asset_returns(close_history_by_symbol, windows=(5, 20, 60)):
    result: dict[str, dict[int, float | None]] = {}
    for symbol, history in close_history_by_symbol.items():
        closes = [row["close"] if isinstance(row, Mapping) else row for row in history]
        closes = [_as_float(value) for value in closes]
        closes = [value for value in closes if value is not None]
        symbol_returns: dict[int, float | None] = {}
        latest_index = len(closes) - 1
        for window in windows:
            window_value = int(window)
            start_index = latest_index - window_value
            if start_index < 0:
                symbol_returns[window_value] = None
            else:
                start = closes[start_index]
                latest = closes[latest_index]
                symbol_returns[window_value] = None if start == 0 else (latest - start) / start
        result[str(symbol).upper()] = symbol_returns
    return result


def calculate_equity_leadership_score(returns_by_symbol):
    values = [_as_float(returns_by_symbol.get(symbol, {}).get(20)) for symbol in ("SPY", "QQQ", "IWM")]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values) / float(len(values))


def calculate_credit_risk_score(returns_by_symbol):
    return _as_float(returns_by_symbol.get("HYG", {}).get(20))


def calculate_rates_pressure_score(returns_by_symbol):
    tlt = _as_float(returns_by_symbol.get("TLT", {}).get(20))
    return None if tlt is None else -tlt


def calculate_dollar_pressure_score(returns_by_symbol):
    dxy = _as_float(returns_by_symbol.get("DXY", {}).get(20))
    return None if dxy is None else -dxy


def calculate_commodity_pressure_score(returns_by_symbol):
    values = [_as_float(returns_by_symbol.get(symbol, {}).get(20)) for symbol in ("GLD", "USO")]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return -sum(values) / float(len(values))


def calculate_volatility_pressure_score(returns_by_symbol):
    vix = _as_float(returns_by_symbol.get("VIX", {}).get(20))
    return None if vix is None else -vix


def calculate_intermarket_alignment_score(component_scores):
    values = [_as_float(value) for value in component_scores.values()]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values) / float(len(values))


def determine_descriptive_intermarket_state(component_scores):
    equity = _as_float(component_scores.get("equity_leadership_score"))
    credit = _as_float(component_scores.get("credit_risk_score"))
    rates = _as_float(component_scores.get("rates_pressure_score"))
    dollar = _as_float(component_scores.get("dollar_pressure_score"))
    commodity = _as_float(component_scores.get("commodity_pressure_score"))
    volatility = _as_float(component_scores.get("volatility_pressure_score"))
    alignment = _as_float(component_scores.get("intermarket_alignment_score"))

    if all(value is None for value in (equity, credit, rates, dollar, commodity, volatility)):
        return "INSUFFICIENT_DATA"
    if alignment is not None and alignment >= 0.02:
        return "RISK_ON_CONFIRMATION"
    if equity is not None and credit is not None and equity > 0 and credit < 0:
        return "EQUITY_CREDIT_DIVERGENCE"
    if rates is not None and rates > 0.15:
        return "RATES_PRESSURE"
    if dollar is not None and dollar > 0.15:
        return "DOLLAR_PRESSURE"
    if alignment is not None and alignment <= -0.02:
        return "RISK_OFF_PRESSURE"
    return "MIXED_INTERMARKET"