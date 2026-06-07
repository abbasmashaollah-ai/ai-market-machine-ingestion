from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_fixture_dry_run_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_fixture_dry_run_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "fixture-only dry-run",
        "qqq",
        "iwm",
        "dia",
        "spy remains existing certified baseline",
        "no production writes",
        "no live api calls",
        "no vendor calls",
        "no scheduler activation",
        "market_feature_bundle.v1",
        "production_pilot.fixture_dry_run.v1",
        "validation_status pass",
        "coverage_status complete",
        "quality_status pass",
        "dry_run_certified",
        "fixture_certified",
        "insufficient_evidence",
        "compare fixture output shape against existing spy pilot contract",
        "idempotency key behavior is deterministic and safe",
        "no secrets/tokens/raw provider credentials",
        "manual approval required before any production seed/write",
        "ai machine multi-symbol diagnostic remains blocked until qqq/iwm/dia are certified",
        "no ingestion execution",
        "no db writes",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text

