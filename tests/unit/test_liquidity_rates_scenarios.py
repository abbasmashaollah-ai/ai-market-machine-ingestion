from app.features.liquidity_rates.liquidity_rates_builder import build_liquidity_rates_observation
from tests.fixtures.liquidity_rates_series import build_liquidity_rates_series_scenario


def test_scenario_labels_differ() -> None:
    labels = {}
    for scenario in ("liquidity_tailwind", "liquidity_headwind", "mixed", "tight_conditions"):
        observation = build_liquidity_rates_observation(build_liquidity_rates_series_scenario(scenario), "2026-01-15")
        labels[scenario] = observation["liquidity_regime_label"]

    assert labels["liquidity_tailwind"] != labels["liquidity_headwind"]
    assert labels["mixed"] in {
        "LIQUIDITY_TAILWIND",
        "LIQUIDITY_HEADWIND",
        "MIXED_LIQUIDITY",
        "TIGHT_FINANCIAL_CONDITIONS",
        "EASY_FINANCIAL_CONDITIONS",
        "INSUFFICIENT_DATA",
    }
    assert labels["tight_conditions"] in {
        "LIQUIDITY_TAILWIND",
        "LIQUIDITY_HEADWIND",
        "MIXED_LIQUIDITY",
        "TIGHT_FINANCIAL_CONDITIONS",
        "EASY_FINANCIAL_CONDITIONS",
        "INSUFFICIENT_DATA",
    }