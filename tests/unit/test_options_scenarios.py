from app.features.options.options_builder import build_options_observation
from tests.fixtures.options_data import build_options_metrics_scenario


def test_scenarios_produce_different_labels() -> None:
    labels = {}
    for scenario in ("high_volatility", "low_volatility", "skewed_protective", "hedging_pressure", "mixed_options", "low_signal"):
        payload = build_options_metrics_scenario(scenario)
        symbol = next(iter(payload))
        labels[scenario] = build_options_observation(
            symbol,
            payload[symbol],
            "2026-01-15",
        )["options_regime_label"]

    assert labels["high_volatility"] == "HEDGING_PRESSURE"
    assert labels["low_volatility"] in {"LOW_VOLATILITY", "MIXED_OPTIONS"}
    assert labels["skewed_protective"] in {"SKEWED_PROTECTIVE", "HIGH_VOLATILITY", "HEDGING_PRESSURE", "MIXED_OPTIONS"}
    assert labels["hedging_pressure"] in {"HEDGING_PRESSURE", "MIXED_OPTIONS", "HIGH_VOLATILITY", "SKEWED_PROTECTIVE"}
    assert labels["mixed_options"] in {"MIXED_OPTIONS", "LOW_VOLATILITY", "HIGH_VOLATILITY"}
    assert labels["low_signal"] in {"MIXED_OPTIONS", "LOW_VOLATILITY"}
