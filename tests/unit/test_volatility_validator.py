from copy import deepcopy

from app.features.volatility.volatility_builder import build_volatility_observation
from app.features.volatility.volatility_validator import validate_volatility_observation, validate_volatility_observations
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_valid_observation_passes() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    result = validate_volatility_observation(observation)
    assert result.is_valid is True


def test_missing_field_fails_and_does_not_mutate() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    snapshot = deepcopy(observation)
    observation.pop("source")
    result = validate_volatility_observation(observation)
    assert result.is_valid is False
    assert any(error.field_name == "source" for error in result.errors)
    assert snapshot["source"] == "fixture_volatility"


def test_duplicate_batch_key_fails() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    result = validate_volatility_observations([observation, dict(observation)])
    assert result.is_valid is False
