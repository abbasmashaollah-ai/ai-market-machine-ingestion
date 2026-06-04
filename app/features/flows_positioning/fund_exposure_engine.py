"""Fund exposure evidence helpers."""

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
