from pathlib import Path


def test_market_feature_bundle_data_api_adapter_implementation_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_data_api_adapter_implementation_plan.md")
    text = path.read_text(encoding="utf-8")

    assert path.exists()
    required_phrases = [
        "read-only Data API adapter",
        "shadow-only",
        "app/clients/data_read_client.py",
        "GET /internal/read/market-feature-bundle/{universe}",
        "SPY",
        "token from environment variable only",
        "base URL from environment variable only",
        "no DB URL",
        "no database imports",
        "no vendor imports",
        "no writes",
        "certification_status CERTIFIED",
        "validation_status PASS",
        "coverage_status COMPLETE",
        "quality_status PASS",
        "missing_data_evidence empty",
        "stale_data_evidence empty",
        "supported schema_version",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio allocation",
        "no capital logic",
        "no execution logic",
        "no scheduler/backfill",
        "no production writes",
        "no vendor fetch",
        "no raw data normalization",
        "unauthorized no-evidence result",
        "route failure no-evidence result",
        "never infer negative market state",
        "app/features/sector_rotation/sector_rotation_reader.py",
        "replace only input-fetch/data-loading portion",
        "keep sector rotation calculations unchanged",
        "log differences only",
        "adapter tests with mocked successful response",
        "401/403 mocked tests",
        "500 mocked test",
        "timeout mocked test",
        "malformed JSON mocked test",
        "no vendor import/source scan",
        "no DB import/source scan",
        "AI_MARKET_MACHINE_DATA_BASE_URL",
        "AI_MARKET_MACHINE_DATA_INTERNAL_TOKEN",
        "missing config returns disabled/no-evidence result",
        "no runtime route wiring without approval",
        "no legacy deletion without approval",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
