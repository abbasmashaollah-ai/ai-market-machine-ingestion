from pathlib import Path


def test_market_feature_bundle_sector_rotation_shadow_integration_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_sector_rotation_shadow_integration_plan.md")
    text = path.read_text(encoding="utf-8")

    assert path.exists()
    required_phrases = [
        "shadow-mode",
        "sector rotation input migration",
        "app/features/sector_rotation/sector_rotation_reader.py",
        "app/clients/data_read_client.py",
        "tests/unit/test_market_feature_bundle_data_read_client.py",
        "replace only input-fetch/data-loading section",
        "keep sector rotation calculations unchanged",
        "do not modify rotation scoring",
        "do not modify leaderboards",
        "do not modify report generation",
        "do not modify market regime",
        "do not modify market risk",
        "do not modify macro liquidity",
        "do not modify flows positioning",
        "explicit shadow flag",
        "compare old/local input to new data API input",
        "log/report differences only",
        "no behavior change",
        "no capital impact",
        "no portfolio changes",
        "no user-facing recommendation",
        "route returns 200",
        "certification_status CERTIFIED",
        "validation_status PASS",
        "coverage_status COMPLETE",
        "quality_status PASS",
        "market_feature_bundle.v1",
        "missing/no-evidence means skip shadow comparison",
        "no judge posture changes",
        "no trading decision changes",
        "no risk posture changes",
        "no portfolio allocation changes",
        "no scheduler/backfill",
        "no production writes",
        "no vendor fetch added",
        "no DB imports",
        "no deletion of legacy data files",
        "no full idempotency_key",
        "no token/DB URL logging",
        "shadow flag disabled means current behavior unchanged",
        "shadow flag enabled compares but does not alter output",
        "no live API calls in tests",
        "authoritative switch requires separate approval",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
