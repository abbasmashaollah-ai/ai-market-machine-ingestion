from app.features.fundamentals.fundamentals_engine import (
    calculate_balance_sheet_score,
    calculate_cash_flow_score,
    calculate_composite_fundamental_score,
    calculate_growth_score,
    calculate_profitability_score,
    calculate_valuation_score,
    determine_fundamental_quality_label,
)


def test_component_scores() -> None:
    financials = {
        "revenue_growth_yoy": 0.1,
        "eps_growth_yoy": 0.2,
        "gross_margin_ttm": 0.4,
        "operating_margin_ttm": 0.3,
        "net_margin_ttm": 0.2,
        "return_on_equity": 0.25,
        "debt_to_equity": 0.5,
        "current_ratio": 1.5,
        "pe_ratio": 20.0,
        "forward_pe": 18.0,
        "price_to_sales": 5.0,
        "price_to_free_cash_flow": 25.0,
        "free_cash_flow_ttm": 100,
        "free_cash_flow_margin": 0.2,
    }
    assert calculate_growth_score(financials) is not None
    assert calculate_profitability_score(financials) is not None
    assert calculate_balance_sheet_score(financials) is not None
    assert calculate_valuation_score(financials) is not None
    assert calculate_cash_flow_score(financials) is not None


def test_composite_and_labels() -> None:
    component_scores = {"growth_score": 0.5, "profitability_score": 0.4, "balance_sheet_score": 0.3, "valuation_score": 0.2, "cash_flow_score": 0.6}
    composite = calculate_composite_fundamental_score(component_scores)
    assert composite is not None
    assert determine_fundamental_quality_label(composite_score=0.6, component_scores=component_scores) == "STRONG_FUNDAMENTALS"
    assert determine_fundamental_quality_label(composite_score=0.3, component_scores=component_scores) == "HEALTHY_FUNDAMENTALS"
    assert determine_fundamental_quality_label(composite_score=-0.6, component_scores=component_scores) == "DISTRESSED_FUNDAMENTALS"
