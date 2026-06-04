"""ETF flow evidence helpers."""

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
        score = (
            sum(v for v in (flow_1d, flow_5d, flow_20d) if v is not None) / 3.0
            if any(v is not None for v in (flow_1d, flow_5d, flow_20d))
            else None
        )
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
