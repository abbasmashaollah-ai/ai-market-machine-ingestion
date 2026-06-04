from app.features.options.options_engine import (
    calculate_call_pressure_score,
    calculate_gamma_pressure_score,
    calculate_implied_volatility_level,
    calculate_iv_rank_score,
    calculate_iv_term_structure_score,
    calculate_put_call_pressure_score,
    calculate_realized_vs_implied_score,
    calculate_skew_pressure_score,
    determine_options_regime_label,
)
from tests.fixtures.options_data import build_options_metrics_scenario


def test_component_scores() -> None:
    metrics = build_options_metrics_scenario("high_volatility")["NVDA"]
    assert calculate_implied_volatility_level(metrics) is not None
    assert calculate_realized_vs_implied_score(metrics) is not None
    assert calculate_iv_rank_score(metrics) is not None
    assert calculate_put_call_pressure_score(metrics) is not None
    assert calculate_call_pressure_score(metrics) is not None
    assert calculate_gamma_pressure_score(metrics) is not None
    assert calculate_skew_pressure_score(metrics) is not None
    assert calculate_iv_term_structure_score(metrics) is not None


def test_regime_labels() -> None:
    high = build_options_metrics_scenario("high_volatility")["NVDA"]
    low = build_options_metrics_scenario("low_volatility")["AAPL"]
    assert determine_options_regime_label({
        "implied_volatility_level": calculate_implied_volatility_level(high),
        "realized_vs_implied_score": calculate_realized_vs_implied_score(high),
        "put_call_pressure_score": calculate_put_call_pressure_score(high),
        "skew_pressure_score": calculate_skew_pressure_score(high),
    }) == "HEDGING_PRESSURE"
    assert determine_options_regime_label({
        "implied_volatility_level": calculate_implied_volatility_level(low),
        "realized_vs_implied_score": calculate_realized_vs_implied_score(low),
        "put_call_pressure_score": calculate_put_call_pressure_score(low),
        "skew_pressure_score": calculate_skew_pressure_score(low),
    }) in {"LOW_VOLATILITY", "MIXED_OPTIONS"}
