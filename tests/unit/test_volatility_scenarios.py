from app.features.volatility.volatility_job import run_volatility_dry_run
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_scenario_labels_differ() -> None:
    labels = {}
    for scenario in ("low_volatility", "elevated_volatility", "high_volatility", "extreme_volatility", "mixed_volatility"):
        histories = build_volatility_series_scenario(scenario)
        result = run_volatility_dry_run(histories, "2026-01-15")
        labels[scenario] = result.reports[0]["volatility_regime_label"]
    assert len(set(labels.values())) >= 3
