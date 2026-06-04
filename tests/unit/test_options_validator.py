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


def test_valid_optional_fields_pass() -> None:
    metrics = dict(build_options_metrics_scenario("high_volatility")["NVDA"])
    metrics["source_attribution"] = "custom_source"
    metrics["dataset_version"] = "custom_dataset_v2"
    metrics["created_at"] = "2026-01-14T22:00:00Z"
    metrics["updated_at"] = "2026-01-15T10:00:00Z"
    metrics["underlying_symbol"] = "QQQ"
    metrics["expiration_date"] = "2026-06-19"
    metrics["total_volume"] = 123456
    metrics["total_open_interest"] = 789012
    observation = build_options_observation("NVDA", metrics, "2026-01-15")
    result = validate_options_observation(observation)
    assert result.is_valid is True


def test_metadata_defaults_and_existing_observations_pass() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    result = validate_options_observation(observation)
    assert result.is_valid is True


def test_negative_total_volume_fails() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["total_volume"] = -1
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "total_volume" for error in result.errors)


def test_negative_total_open_interest_fails() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["total_open_interest"] = -1
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "total_open_interest" for error in result.errors)


def test_blank_underlying_symbol_fails_when_provided() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["underlying_symbol"] = ""
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "underlying_symbol" for error in result.errors)


def test_blank_expiration_date_fails_when_provided() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["expiration_date"] = ""
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "expiration_date" for error in result.errors)


def test_blank_source_attribution_fails_when_provided() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["source_attribution"] = ""
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "source_attribution" for error in result.errors)


def test_blank_dataset_version_fails_when_provided() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["dataset_version"] = ""
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "dataset_version" for error in result.errors)


def test_blank_created_at_fails_when_provided() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["created_at"] = ""
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "created_at" for error in result.errors)


def test_blank_updated_at_fails_when_provided() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    invalid = dict(observation)
    invalid["updated_at"] = ""
    result = validate_options_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "updated_at" for error in result.errors)
