import json

from app.features.liquidity_rates.liquidity_rates_builder import build_liquidity_rates_observation
from tests.fixtures.liquidity_rates_series import build_liquidity_rates_series_fixtures


def test_observation_includes_expected_fields() -> None:
    observation = build_liquidity_rates_observation(build_liquidity_rates_series_fixtures(), "2026-01-15")
    expected = {
        "observation_date",
        "timestamp",
        "series",
        "short_rate_pressure_score",
        "long_rate_pressure_score",
        "yield_curve_slope",
        "yield_curve_pressure_score",
        "real_yield_pressure_score",
        "dollar_liquidity_pressure_score",
        "credit_liquidity_score",
        "equity_liquidity_confirmation_score",
        "liquidity_regime_label",
        "source",
        "quality_status",
        "certification_status",
        "freshness_status",
        "lineage",
        "evidence",
    }
    assert set(observation) == expected
    json.dumps(observation)