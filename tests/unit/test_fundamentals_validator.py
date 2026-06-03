from copy import deepcopy

from app.features.fundamentals.fundamentals_builder import build_fundamental_observation
from app.features.fundamentals.fundamentals_validator import validate_fundamental_observation
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_valid_observation_passes() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    result = validate_fundamental_observation(observation)
    assert result.is_valid is True


def test_invalid_observation_fails() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    invalid = dict(observation)
    invalid["fundamental_quality_label"] = None
    result = validate_fundamental_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "fundamental_quality_label" for error in result.errors)


def test_validator_does_not_mutate_input() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    snapshot = deepcopy(observation)
    validate_fundamental_observation(observation)
    assert observation == snapshot
