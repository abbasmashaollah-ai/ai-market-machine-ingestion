import json
from datetime import datetime, timezone

from app.features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_feature_bundle_validator import validate_market_feature_bundle


def test_summary_contains_required_fields_and_states() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert validate_market_feature_bundle(bundle).is_valid is True

    summary = build_market_feature_bundle_summary(bundle)

    assert summary["observation_date"] == "2026-01-15"
    assert summary["timestamp"]
    assert "SPY" in summary["price_states_by_symbol"]
    assert "AAPL" in summary["price_states_by_symbol"]
    assert "MSFT" in summary["price_states_by_symbol"]
    assert summary["breadth_participation_label"]
    assert summary["sector_rotation_state"]
    assert summary["cross_asset_state"]
    assert summary["liquidity_rates_state"]
    assert "prices" not in summary
    assert "breadth" not in summary
    assert "sector_rotation" not in summary
    assert "cross_asset" not in summary
    assert "liquidity_rates" not in summary
    assert summary["accepted_counts_by_section"]["prices"]["accepted"] == 3
    assert summary["accepted_counts_by_section"]["liquidity_rates"]["accepted"] == 1
    assert summary["safety_flags"]["no_db_writes"] is True
    assert summary["safety_flags"]["no_vendor_calls"] is True
    assert summary["safety_flags"]["no_live_api_calls"] is True
    assert summary["safety_flags"]["no_scheduler_activation"] is True
    assert summary["descriptive_market_evidence_state"] in {
        "RISK_ON_EVIDENCE",
        "RISK_OFF_EVIDENCE",
        "MIXED_EVIDENCE",
        "INSUFFICIENT_EVIDENCE",
    }
    json.dumps(summary)


def test_summary_does_not_mutate_bundle_and_remains_json_friendly() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-01-15")
    snapshot = json.loads(json.dumps(bundle))

    summary = build_market_feature_bundle_summary(bundle)

    assert bundle == snapshot
    assert summary["feature_sections_present"]["prices"] is True
    assert summary["feature_sections_present"]["breadth"] is True
    assert summary["feature_sections_present"]["sector_rotation"] is True
    assert summary["feature_sections_present"]["cross_asset"] is True
    assert summary["feature_sections_present"]["liquidity_rates"] is True
