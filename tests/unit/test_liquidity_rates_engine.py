from app.features.liquidity_rates.liquidity_rates_engine import (
    calculate_credit_liquidity_score,
    calculate_dollar_liquidity_pressure_score,
    calculate_equity_liquidity_confirmation_score,
    calculate_long_rate_pressure_score,
    calculate_real_yield_pressure_score,
    calculate_series_change,
    calculate_short_rate_pressure_score,
    calculate_yield_curve_pressure_score,
    calculate_yield_curve_slope,
    determine_liquidity_regime_label,
)


def test_series_change_and_yield_slope() -> None:
    assert calculate_series_change([1, 2, 3, 4, 5, 6], 5) == 5
    assert calculate_yield_curve_slope(4.0, 3.0) == 1.0


def test_component_scores_and_label() -> None:
    scores = {
        "short_rate_pressure_score": calculate_short_rate_pressure_score(-0.1, -0.1),
        "long_rate_pressure_score": calculate_long_rate_pressure_score(-0.2),
        "yield_curve_pressure_score": calculate_yield_curve_pressure_score(1.0, -0.1),
        "real_yield_pressure_score": calculate_real_yield_pressure_score(-0.1),
        "dollar_liquidity_pressure_score": calculate_dollar_liquidity_pressure_score(-0.1),
        "credit_liquidity_score": calculate_credit_liquidity_score(0.2),
        "equity_liquidity_confirmation_score": calculate_equity_liquidity_confirmation_score(0.3),
    }
    assert determine_liquidity_regime_label(scores) in {
        "LIQUIDITY_TAILWIND",
        "LIQUIDITY_HEADWIND",
        "MIXED_LIQUIDITY",
        "TIGHT_FINANCIAL_CONDITIONS",
        "EASY_FINANCIAL_CONDITIONS",
        "INSUFFICIENT_DATA",
    }