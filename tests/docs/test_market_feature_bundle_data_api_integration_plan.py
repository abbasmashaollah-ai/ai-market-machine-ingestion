from pathlib import Path


def test_market_feature_bundle_data_api_integration_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_data_api_integration_plan.md")
    text = path.read_text(encoding="utf-8")

    assert path.exists()
    required_phrases = [
        "READY_FOR_DATA_API_INTEGRATION_PLANNING",
        "GET /internal/read/market-feature-bundle/{universe}",
        "SPY",
        "production_pilot.v1",
        "validation_status",
        "validation_status: PASS",
        "certification_status",
        "certification_status: CERTIFIED",
        "coverage_status",
        "coverage_status: COMPLETE",
        "quality_status",
        "quality_status: PASS",
        "preserve AI Machine judgment",
        "evidence, not judgment",
        "app/features/market_risk/**",
        "app/features/market_regime/**",
        "app/features/macro_liquidity/**",
        "app/features/flows_positioning/**",
        "app/vendors/**",
        "app/normalization/**",
        "app/ingestion/**",
        "app/clients/data_read_client.py",
        "app/features/sector_rotation/sector_rotation_reader.py",
        "replace only input-fetch/data-loading portion",
        "keep sector rotation calculations unchanged",
        "read-only",
        "shadow mode",
        "no capital impact",
        "no portfolio changes",
        "no judge posture changes",
        "no trading decision changes",
        "no risk posture changes",
        "no portfolio allocation changes",
        "no scheduler/backfill activation",
        "no production writes",
        "no deletion of legacy data files in the first phase",
        "adapter unit tests with mocked route responses",
        "no vendor call tests",
        "no DB write/import tests",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
