from copy import deepcopy

from app.features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_feature_bundle_validator import validate_market_feature_bundle


def test_valid_bundle_passes() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-01-15")
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is True
    assert result.errors == ()


def test_missing_required_top_level_field_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("prices")
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "prices" for error in result.errors)


def test_false_safety_flag_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle["no_vendor_calls"] = False
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "no_vendor_calls" for error in result.errors)


def test_missing_feature_section_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle["breadth"] = {}
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "breadth" for error in result.errors)


def test_validator_does_not_mutate_input() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-01-15")
    snapshot = deepcopy(bundle)
    validate_market_feature_bundle(bundle)
    assert bundle == snapshot


def test_errors_are_deterministic() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("prices")
    bundle["no_scheduler_activation"] = False
    result = validate_market_feature_bundle(bundle)
    messages = [(error.field_name, error.message) for error in result.errors]
    assert messages == [
        ("prices", "field is required"),
        ("no_scheduler_activation", "field must be True"),
        ("prices", "field must be an object"),
    ]
