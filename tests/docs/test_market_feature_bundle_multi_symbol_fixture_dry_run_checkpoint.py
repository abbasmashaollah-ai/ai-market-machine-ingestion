from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_fixture_dry_run_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_fixture_dry_run_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "qqq/iwm/dia fixture dry-run payload creation and validation",
        "local, non-production, and not data api certified evidence",
        "qqq_fixture_dry_run.json",
        "iwm_fixture_dry_run.json",
        "dia_fixture_dry_run.json",
        "fixture_validator.py",
        "test_market_feature_bundle_multi_symbol_fixture_payloads.py",
        "qqq `fixture_certified`",
        "iwm `dry_run_certified`",
        "dia `fixture_certified`",
        "observation_date `2026-01-15`",
        "schema_version `market_feature_bundle.v1`",
        "dataset_version `production_pilot.fixture_dry_run.v1`",
        "source_repo `ai-market-machine-ingestion`",
        "source_run_id `fixture_dry_run.v1`",
        "deterministic fixture-style idempotency keys",
        "fixture-only lineage/quality refs",
        "empty validation errors",
        "fixture-only disclaimers",
        "test_market_feature_bundle_multi_symbol_fixture_payloads.py passed",
        "fixture evidence is not production evidence",
        "fixture evidence is not data api certified evidence",
        "not ingestion execution",
        "not db write",
        "not production seed",
        "not vendor call",
        "not live api call",
        "not scheduler activation",
        "not data api exposure",
        "not ai machine runtime wiring",
        "not approval for production expansion",
        "production seed/write approval checklist",
        "qqq/iwm/dia certified before ai machine multi-symbol diagnostic can proceed",
        "no ingestion run",
        "no db writes",
        "no vendor calls",
        "no live api calls",
        "no scheduler activation",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text
