"""Positioning risk and flow regime evidence helpers."""

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
