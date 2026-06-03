"""Pure helpers for deterministic fundamentals evidence."""

from __future__ import annotations


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _scale_between(value: float | None, low: float, high: float) -> float | None:
    if value is None:
        return None
    if high == low:
        return 0.0
    normalized = (value - low) / (high - low)
    return max(-1.0, min(1.0, (normalized * 2.0) - 1.0))


def calculate_growth_score(financials):
    revenue_growth = _to_float(financials.get("revenue_growth_yoy"))
    eps_growth = _to_float(financials.get("eps_growth_yoy"))
    score = 0.0
    weight = 0.0
    for value in (revenue_growth, eps_growth):
        if value is None:
            continue
        score += max(-1.0, min(1.0, value))
        weight += 1.0
    return score / weight if weight else None


def calculate_profitability_score(financials):
    gross = _to_float(financials.get("gross_margin_ttm"))
    operating = _to_float(financials.get("operating_margin_ttm"))
    net = _to_float(financials.get("net_margin_ttm"))
    roe = _to_float(financials.get("return_on_equity"))
    values = [value for value in (gross, operating, net, roe) if value is not None]
    return sum(max(-1.0, min(1.0, value)) for value in values) / len(values) if values else None


def calculate_balance_sheet_score(financials):
    debt_to_equity = _to_float(financials.get("debt_to_equity"))
    current_ratio = _to_float(financials.get("current_ratio"))
    score = 0.0
    weight = 0.0
    if debt_to_equity is not None:
        score += max(-1.0, min(1.0, 1.0 - debt_to_equity / 2.0))
        weight += 1.0
    if current_ratio is not None:
        score += max(-1.0, min(1.0, (current_ratio - 1.0) / 2.0))
        weight += 1.0
    return score / weight if weight else None


def calculate_valuation_score(financials):
    pe = _to_float(financials.get("pe_ratio"))
    forward_pe = _to_float(financials.get("forward_pe"))
    price_to_sales = _to_float(financials.get("price_to_sales"))
    price_to_fcf = _to_float(financials.get("price_to_free_cash_flow"))
    values = []
    for value in (pe, forward_pe, price_to_sales, price_to_fcf):
        if value is None:
            continue
        values.append(max(-1.0, min(1.0, 1.0 - value / 30.0)))
    return sum(values) / len(values) if values else None


def calculate_cash_flow_score(financials):
    fcf = _to_float(financials.get("free_cash_flow_ttm"))
    margin = _to_float(financials.get("free_cash_flow_margin"))
    score = 0.0
    weight = 0.0
    if fcf is not None:
        score += max(-1.0, min(1.0, fcf / 100_000_000_000.0))
        weight += 1.0
    if margin is not None:
        score += max(-1.0, min(1.0, margin))
        weight += 1.0
    return score / weight if weight else None


def calculate_composite_fundamental_score(component_scores):
    values = [float(value) for value in component_scores.values() if isinstance(value, (int, float))]
    return sum(values) / len(values) if values else None


def determine_fundamental_quality_label(composite_score=None, component_scores=None):
    if composite_score is None:
        return "INSUFFICIENT_DATA"
    if composite_score >= 0.55:
        return "STRONG_FUNDAMENTALS"
    if composite_score >= 0.25:
        return "HEALTHY_FUNDAMENTALS"
    if composite_score <= -0.15:
        return "DISTRESSED_FUNDAMENTALS"
    if composite_score <= -0.05:
        return "WEAK_FUNDAMENTALS"
    if component_scores and any(value is None for value in component_scores.values()):
        return "MIXED_FUNDAMENTALS"
    return "MIXED_FUNDAMENTALS"
