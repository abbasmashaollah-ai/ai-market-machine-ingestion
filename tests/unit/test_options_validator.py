from copy import deepcopy

from app.features.options.options_builder import build_options_observation
from app.features.options.options_validator import validate_options_observation
from tests.fixtures.options_data import build_options_metrics_scenario


def test_valid_observation_passes() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    result = validate_options_observation(observation)
    assert result.is_valid is True


def test_invalid_observation_fails() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["options_regime_label"] = None
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "options_regime_label" for error in result.errors)


def test_validator_does_not_mutate_input() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    snapshot = deepcopy(observation)
    validate_options_observation(observation)
    assert observation == snapshot
