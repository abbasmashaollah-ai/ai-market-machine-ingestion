"""Pure helpers for deterministic flows and positioning evidence."""

from __future__ import annotations


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _bounded(value: float | None) -> float | None:
    if value is None:
        return None
    return max(-1.0, min(1.0, value))


def calculate_equity_flow_score(etf_flows):
    values = []
    for item in etf_flows or []:
        if not isinstance(item, dict):
            continue
        flow_1d = _to_float(item.get("flow_1d"))
        flow_5d = _to_float(item.get("flow_5d"))
        flow_20d = _to_float(item.get("flow_20d"))
        aum = _to_float(item.get("aum"))
        if aum is None or aum == 0:
            continue
        score = sum(v for v in (flow_1d, flow_5d, flow_20d) if v is not None) / 3.0 if any(v is not None for v in (flow_1d, flow_5d, flow_20d)) else None
        if score is not None:
            values.append(_bounded(score / aum * 100_000_000.0))
    return sum(values) / len(values) if values else None


def calculate_defensive_flow_score(etf_flows):
    values = []
    for item in etf_flows or []:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").upper()
        flow_1d = _to_float(item.get("flow_1d")) or 0.0
        if symbol in {"XLP", "XLU", "XLV"}:
            values.append(_bounded(-flow_1d / 100_000_000.0))
    return sum(values) / len(values) if values else None


def calculate_credit_flow_score(etf_flows):
    values = []
    for item in etf_flows or []:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").upper()
        if symbol != "HYG":
            continue
        flow_1d = _to_float(item.get("flow_1d"))
        aum = _to_float(item.get("aum"))
        if flow_1d is None or not aum:
            continue
        values.append(_bounded(flow_1d / aum * 100_000_000.0))
    return sum(values) / len(values) if values else None


def calculate_options_positioning_score(options_positioning):
    if not isinstance(options_positioning, dict):
        return None
    ratios = [
        _to_float(options_positioning.get("put_call_ratio")),
        _to_float(options_positioning.get("equity_put_call_ratio")),
        _to_float(options_positioning.get("index_put_call_ratio")),
    ]
    usable = [value for value in ratios if value is not None]
    if not usable:
        return None
    score = 1.0 - (sum(usable) / len(usable))
    return _bounded(score)


def calculate_futures_positioning_score(futures_positioning):
    values = []
    for item in futures_positioning or []:
        if not isinstance(item, dict):
            continue
        percentile = _to_float(item.get("net_position_percentile"))
        if percentile is not None:
            values.append(_bounded((percentile * 2.0) - 1.0))
    return sum(values) / len(values) if values else None


def calculate_short_interest_pressure_score(short_interest):
    values = []
    for item in short_interest or []:
        if not isinstance(item, dict):
            continue
        short_pct = _to_float(item.get("short_interest_percent_float"))
        days_to_cover = _to_float(item.get("days_to_cover"))
        if short_pct is None and days_to_cover is None:
            continue
        score = 0.0
        if short_pct is not None:
            score += short_pct
        if days_to_cover is not None:
            score += min(days_to_cover / 10.0, 1.0)
        values.append(_bounded(score / 2.0))
    return sum(values) / len(values) if values else None


def calculate_fund_exposure_score(fund_exposure):
    if not isinstance(fund_exposure, dict):
        return None
    gross = _to_float(fund_exposure.get("gross_exposure"))
    net = _to_float(fund_exposure.get("net_exposure"))
    cash = _to_float(fund_exposure.get("cash_level"))
    values = []
    if gross is not None:
        values.append(_bounded(gross / 2.0))
    if net is not None:
        values.append(_bounded(net))
    if cash is not None:
        values.append(_bounded(-cash))
    return sum(values) / len(values) if values else None


def calculate_crowdedness_score(component_scores):
    values = [abs(float(value)) for value in component_scores.values() if isinstance(value, (int, float))]
    return min(1.0, sum(values) / len(values)) if values else None


def calculate_positioning_risk_score(component_scores):
    values = [float(value) for value in component_scores.values() if isinstance(value, (int, float))]
    return max(-1.0, min(1.0, sum(values) / len(values))) if values else None


def determine_flow_regime_label(component_scores):
    crowded = _to_float(component_scores.get("crowdedness_score"))
    risk = _to_float(component_scores.get("positioning_risk_score"))
    equity = _to_float(component_scores.get("equity_flow_score"))
    defensive = _to_float(component_scores.get("defensive_flow_score"))
    credit = _to_float(component_scores.get("credit_flow_score"))
    if crowded is None and risk is None:
        return "INSUFFICIENT_DATA"
    if crowded is not None and crowded >= 0.65 and risk is not None and risk >= 0.25:
        return "CROWDED_LONG"
    if crowded is not None and crowded >= 0.65 and risk is not None and risk <= -0.25:
        return "CROWDED_SHORT"
    if risk is not None and risk <= -0.25:
        return "RISK_OFF_FLOWS"
    if defensive is not None and defensive > 0.2 and risk is not None and risk <= 0:
        return "RISK_OFF_FLOWS"
    if equity is not None and equity > 0.2 and credit is not None and credit > 0 and risk is not None and risk > 0:
        return "RISK_ON_FLOWS"
    if risk is not None and abs(risk) < 0.2:
        return "LOW_SIGNAL_POSITIONING"
    return "MIXED_POSITIONING"
