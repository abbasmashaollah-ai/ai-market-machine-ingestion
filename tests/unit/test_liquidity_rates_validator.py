from app.features.liquidity_rates.liquidity_rates_builder import build_liquidity_rates_observation
from app.features.liquidity_rates.liquidity_rates_validator import validate_liquidity_rates_observation, validate_liquidity_rates_observations
from tests.fixtures.liquidity_rates_series import build_liquidity_rates_series_fixtures


def test_valid_observation_passes() -> None:
    observation = build_liquidity_rates_observation(build_liquidity_rates_series_fixtures(), "2026-01-15")
    assert validate_liquidity_rates_observation(observation).is_valid is True


def test_invalid_rows_and_duplicates_fail() -> None:
    observation = dict(build_liquidity_rates_observation(build_liquidity_rates_series_fixtures(), "2026-01-15"))
    observation["liquidity_regime_label"] = "NOT_VALID"
    result = validate_liquidity_rates_observation(observation)
    assert result.is_valid is False
    dup = validate_liquidity_rates_observations([observation, observation])
    assert dup[1].is_valid is False