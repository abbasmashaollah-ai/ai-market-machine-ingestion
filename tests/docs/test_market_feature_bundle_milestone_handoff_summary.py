from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_milestone_handoff_summary_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_milestone_handoff_summary.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "market_feature_bundle clean data bridge milestone",
        "production-pilot complete",
        "preserved production row verified",
        "ai machine read contract recorded",
        "ingestion producer path complete",
        "writer path complete",
        "safe db validation complete",
        "production pilot complete",
        "route preservation verification complete",
        "credential rotation verification complete",
        "monitoring checkpoint complete",
        "scheduler/backfill approval plan complete",
        "ai machine read-consumption contract complete",
        "spy",
        "production_pilot.v1",
        "market_feature_bundle.v1",
        "validation_status pass",
        "certification_status certified",
        "coverage_status complete",
        "quality_status pass",
        "preserve_first_production_row",
        "market_feature_bundle_snapshots",
        "get /internal/read/market-feature-bundle/{universe}",
        "certified_only",
        "data repo owns warehouse/read",
        "ingestion owns calculation/producer/writer handoff only",
        "no scheduler activation",
        "no backfill execution",
        "no vendor live fetch",
        "no ai machine code",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio allocation",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "cleanup only by idempotency_key",
        "credentials redacted",
        "idempotency_key_prefix only",
        "production db credential was exposed earlier and rotated",
        "preserved row survived credential rotation",
        "scheduler/backfill remains blocked until explicit approval",
        "99/100",
        "83/100",
        "67/100",
        "app/features calculation-only",
        "read-only shadow first",
    ]:
        assert needle in text
