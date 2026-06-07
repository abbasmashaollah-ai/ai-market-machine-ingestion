from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_fixture_dry_run_implementation_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_fixture_dry_run_implementation_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "qqq/iwm/dia fixture dry-run package",
        "tests/fixtures/market_feature_bundle/qqq_fixture_dry_run.json",
        "tests/fixtures/market_feature_bundle/iwm_fixture_dry_run.json",
        "tests/fixtures/market_feature_bundle/dia_fixture_dry_run.json",
        "spy_contract_reference.json",
        "fixture schema validator",
        "test-only validator",
        "no runtime writer integration",
        "no db integration",
        "no scheduler integration",
        "universe qqq/iwm/dia",
        "observation_date 2026-01-15",
        "schema_version market_feature_bundle.v1",
        "dataset_version production_pilot.fixture_dry_run.v1",
        "validation_status pass",
        "coverage_status complete",
        "quality_status pass",
        "certification_status fixture_certified",
        "dry_run_certified",
        "source_repo ai-market-machine-ingestion",
        "source_run_id fixture_dry_run.v1",
        "no secrets/tokens/raw provider credentials",
        "deterministic idempotency_key",
        "reject production certified status in fixture dry-run",
        "reject raw credentials/secrets/tokens",
        "reject non-deterministic idempotency behavior",
        "do not write to db",
        "do not expose fixtures through data api",
        "manual approval required before any production seed/write",
        "no ingestion execution",
        "no db writes",
        "no vendor calls",
        "no live api calls",
        "no scheduler activation",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text

