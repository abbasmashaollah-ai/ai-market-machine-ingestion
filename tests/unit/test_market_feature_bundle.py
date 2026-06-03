import json
from datetime import datetime, timezone
from pathlib import Path

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run


def test_bundle_contains_all_sections_and_is_json_friendly() -> None:
    bundle = run_market_feature_bundle_dry_run(
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    assert bundle["no_db_writes"] is True
    assert bundle["no_vendor_calls"] is True
    assert bundle["no_live_api_calls"] is True
    assert bundle["no_scheduler_activation"] is True
    assert set(bundle) >= {"observation_date", "timestamp", "prices", "breadth", "sector_rotation", "cross_asset", "liquidity_rates", "news_sentiment", "fundamentals", "warnings"}
    assert "event_calendar" in bundle
    assert "news_sentiment" in bundle
    assert "fundamentals" in bundle
    assert "SPY" in bundle["prices"]["reports_by_symbol"]
    assert bundle["breadth"]["report"]["participation_label"]
    assert bundle["sector_rotation"]["descriptive_rotation_state"]
    assert bundle["cross_asset"]["descriptive_intermarket_state"]
    assert bundle["liquidity_rates"]["liquidity_regime_label"]
    assert bundle["volatility"]["volatility_regime_label"]
    json.dumps(bundle)


def test_bundle_uses_fixture_dry_run_inputs_only() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-01-15")
    assert bundle["prices"]["accepted_count"] == 3
    assert bundle["breadth"]["accepted_count"] == 1
    assert bundle["sector_rotation"]["accepted_observation_count"] == 11
    assert bundle["cross_asset"]["accepted_count"] == 1
    assert bundle["liquidity_rates"]["accepted_count"] == 1
    assert bundle["volatility"]["accepted_count"] == 1
    assert bundle["event_calendar"]["accepted_count"] == 1
    assert bundle["news_sentiment"]["accepted_count"] == 1
    assert bundle["fundamentals"]["accepted_count"] == 6
    assert bundle["prices"]["no_db_writes"] is True
    assert bundle["breadth"]["no_vendor_calls"] is True
    assert bundle["sector_rotation"]["no_live_api_calls"] is True
    assert bundle["cross_asset"]["no_scheduler_activation"] is True


def test_bundle_module_does_not_import_tests_fixtures() -> None:
    text = Path("app/features/market_features/market_feature_bundle.py").read_text(encoding="utf-8")
    assert "tests.fixtures" not in text
    for path in Path("app/features/market_features").rglob("*.py"):
        assert "tests.fixtures" not in path.read_text(encoding="utf-8")
