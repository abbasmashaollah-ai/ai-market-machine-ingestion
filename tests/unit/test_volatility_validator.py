from copy import deepcopy

from app.features.volatility.volatility_builder import build_volatility_observation
from app.features.volatility.volatility_validator import validate_volatility_observation, validate_volatility_observations
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_valid_observation_passes() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    result = validate_volatility_observation(observation)
    assert result.is_valid is True


def test_valid_alias_fields_pass() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    observation = dict(observation)
    observation["vix_close"] = observation["vix_level"]
    observation["vvix_close"] = observation["vvix_level"]
    observation["vxn_close"] = observation["vxn_level"]
    observation["rvx_close"] = observation["rvx_level"]
    observation["volatility_stress_score"] = observation["composite_volatility_stress_score"]
    observation["descriptive_volatility_state"] = observation["volatility_regime_label"]
    result = validate_volatility_observation(observation)
    assert result.is_valid is True


def test_valid_metadata_fields_pass() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    observation = dict(observation)
    observation["dataset_version"] = "volatility_dry_run_v1"
    observation["created_at"] = "2026-01-15T00:00:00Z[created_at]"
    observation["updated_at"] = "2026-01-15T00:00:00Z[updated_at]"
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


def test_invalid_descriptive_volatility_state_fails() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    observation = dict(observation)
    observation["descriptive_volatility_state"] = "NOT_ALLOWED"
    result = validate_volatility_observation(observation)
    assert result.is_valid is False
    assert any(error.field_name == "descriptive_volatility_state" for error in result.errors)


def test_invalid_empty_metadata_fields_fail() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    observation = dict(observation)
    observation["dataset_version"] = ""
    observation["created_at"] = ""
    observation["updated_at"] = ""
    result = validate_volatility_observation(observation)
    assert result.is_valid is False
    assert any(error.field_name == "dataset_version" for error in result.errors)
    assert any(error.field_name == "created_at" for error in result.errors)
    assert any(error.field_name == "updated_at" for error in result.errors)
