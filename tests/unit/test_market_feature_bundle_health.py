from __future__ import annotations

import json
import subprocess
import sys

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_features.market_feature_bundle_validator import validate_market_feature_bundle


def test_market_feature_bundle_health_and_summary_are_complete() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-06-03")
    validation_result = validate_market_feature_bundle(bundle)
    assert validation_result.is_valid is True
    assert validation_result.errors == ()

    summary = build_market_feature_bundle_summary(bundle)

    expected_sections = (
        "prices",
        "breadth",
        "sector_rotation",
        "cross_asset",
        "liquidity_rates",
        "volatility",
        "event_calendar",
        "news_sentiment",
        "earnings",
        "macro_liquidity",
        "market_risk",
        "fundamentals",
        "flows_positioning",
        "options",
    )
    assert all(summary["feature_sections_present"][section] is True for section in expected_sections)
    assert summary["total_warnings"] == 0

    for flag_name, flag_value in summary["safety_flags"].items():
        assert flag_value is True, flag_name

    assert summary["rejected_counts_by_section"]["prices"] == 0
    assert summary["rejected_counts_by_section"]["breadth"] == 0
    assert summary["rejected_counts_by_section"]["cross_asset"] == 0
    assert summary["rejected_counts_by_section"]["liquidity_rates"] == 0
    assert summary["rejected_counts_by_section"]["volatility"] == 0
    assert summary["rejected_counts_by_section"]["event_calendar"] == 0
    assert summary["rejected_counts_by_section"]["news_sentiment"] == 0
    assert summary["rejected_counts_by_section"]["earnings"] == 0
    assert summary["rejected_counts_by_section"]["macro_liquidity"] == 0
    assert summary["rejected_counts_by_section"]["market_risk"] == 0
    assert summary["rejected_counts_by_section"]["fundamentals"] == 0
    assert summary["rejected_counts_by_section"]["flows_positioning"] == 0
    assert summary["rejected_counts_by_section"]["options"] == 0
    assert summary["accepted_counts_by_section"]["sector_rotation"]["rejected"] == 0
    assert summary["accepted_counts_by_section"]["sector_rotation"]["rejected_summary"] == 0

    for field_name in (
        "earnings_regime_labels_by_symbol",
        "macro_liquidity_state",
        "market_risk_state",
        "options_regime_labels_by_symbol",
        "flows_positioning_state",
        "fundamental_quality_labels_by_symbol",
        "news_sentiment_state",
        "event_calendar_state",
        "volatility_state",
        "liquidity_rates_state",
    ):
        assert field_name in summary


def test_market_feature_bundle_health_cli_summary_only_is_json_friendly() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_market_feature_bundle_dry_run.py", "--observation-date", "2026-06-03", "--summary-only"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["feature_sections_present"]["earnings"] is True
    assert payload["earnings_regime_labels_by_symbol"]["AAPL"]
    assert payload["macro_liquidity_state"]
    assert payload["market_risk_state"]
    assert payload["options_regime_labels_by_symbol"]["AAPL"]
    assert payload["flows_positioning_state"]
    assert payload["fundamental_quality_labels_by_symbol"]["AAPL"]
    assert payload["news_sentiment_state"]
    assert payload["event_calendar_state"]
    assert payload["volatility_state"]
    assert payload["liquidity_rates_state"]
    assert payload["safety_flags"]["no_db_writes"] is True
    assert payload["safety_flags"]["no_vendor_calls"] is True
    assert payload["safety_flags"]["no_live_api_calls"] is True
    assert payload["safety_flags"]["no_scheduler_activation"] is True
