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


def test_valid_metadata_fields_pass() -> None:
    financials = dict(build_fundamentals_financials_scenario("strong_quality")["AAPL"])
    financials["source_attribution"] = "custom_source"
    financials["dataset_version"] = "custom_dataset_v2"
    financials["created_at"] = "2026-01-14T22:00:00Z"
    financials["updated_at"] = "2026-01-15T10:00:00Z"
    observation = build_fundamental_observation("AAPL", financials, "2026-01-15")
    result = validate_fundamental_observation(observation)
    assert result.is_valid is True


def test_blank_dataset_version_fails_when_provided() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    invalid = dict(observation)
    invalid["dataset_version"] = ""
    result = validate_fundamental_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "dataset_version" for error in result.errors)


def test_blank_created_at_fails_when_provided() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    invalid = dict(observation)
    invalid["created_at"] = ""
    result = validate_fundamental_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "created_at" for error in result.errors)


def test_blank_updated_at_fails_when_provided() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    invalid = dict(observation)
    invalid["updated_at"] = ""
    result = validate_fundamental_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "updated_at" for error in result.errors)
