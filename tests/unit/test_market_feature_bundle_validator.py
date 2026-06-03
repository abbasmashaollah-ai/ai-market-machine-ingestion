from copy import deepcopy

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_validator import validate_market_feature_bundle


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


def test_missing_liquidity_rates_section_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("liquidity_rates")
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "liquidity_rates" for error in result.errors)


def test_missing_volatility_section_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("volatility")
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "volatility" for error in result.errors)


def test_missing_event_calendar_section_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("event_calendar")
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "event_calendar" for error in result.errors)


def test_missing_news_sentiment_section_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("news_sentiment")
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "news_sentiment" for error in result.errors)


def test_missing_fundamentals_section_fails() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("fundamentals")
    result = validate_market_feature_bundle(bundle)
    assert result.is_valid is False
    assert any(error.field_name == "fundamentals" for error in result.errors)


def test_missing_section_labels_fail() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle["breadth"] = {"report": {}}
    bundle["sector_rotation"] = {"report": {}}
    bundle["cross_asset"] = {"report": {}}
    bundle["liquidity_rates"] = {"report": {}}
    bundle["volatility"] = {"report": {}}
    bundle["event_calendar"] = {"report": {}}
    bundle["news_sentiment"] = {"report": {}}
    bundle["fundamentals"] = {}
    result = validate_market_feature_bundle(bundle)
    field_names = {error.field_name for error in result.errors}
    assert "breadth" in field_names
    assert "sector_rotation" in field_names
    assert "cross_asset" in field_names
    assert "liquidity_rates" in field_names
    assert "volatility" in field_names
    assert "event_calendar" in field_names
    assert "news_sentiment" in field_names
    assert "fundamentals" in field_names


def test_validator_does_not_mutate_input() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-01-15")
    snapshot = deepcopy(bundle)
    validate_market_feature_bundle(bundle)
    assert bundle == snapshot


def test_errors_are_deterministic() -> None:
    bundle = dict(run_market_feature_bundle_dry_run("2026-01-15"))
    bundle.pop("prices")
    bundle["no_scheduler_activation"] = False
    bundle["liquidity_rates"] = {}
    bundle["volatility"] = {}
    bundle["event_calendar"] = {}
    bundle["news_sentiment"] = {}
    bundle["fundamentals"] = {}
    result = validate_market_feature_bundle(bundle)
    messages = [(error.field_name, error.message) for error in result.errors]
    assert messages == [
        ("prices", "field is required"),
        ("no_scheduler_activation", "field must be True"),
        ("prices", "field must be an object"),
        ("liquidity_rates", "liquidity_rates must include a non-empty liquidity_regime_label or report"),
        ("volatility", "volatility must include a non-empty volatility_regime_label or report"),
        ("event_calendar", "event_calendar must include a non-empty event_risk_label or report"),
        ("news_sentiment", "news_sentiment must include a non-empty sentiment_regime_label or report"),
        ("fundamentals", "fundamentals must include reports or fundamental_quality_labels_by_symbol"),
    ]
