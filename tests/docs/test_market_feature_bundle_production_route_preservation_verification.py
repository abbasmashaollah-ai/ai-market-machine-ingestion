from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_production_route_preservation_verification_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_production_route_preservation_verification.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "read-only production route verification passed",
        "preserved production pilot row is visible",
        "get /internal/read/market-feature-bundle/spy",
        "snapshot_count 1",
        "market_feature_bundle present",
        "observation_date 2026-01-15",
        "generated_at 2026-06-05t05:35:26.607789",
        "production_pilot.v1",
        "market_feature_bundle.v1",
        "validation_status pass",
        "certification_status certified",
        "source_repo ai-market-machine-ingestion",
        "source_run_id production_pilot.v1",
        "coverage_status complete",
        "quality_status pass",
        "freshness_status pass",
        "missing_data_evidence empty",
        "stale_data_evidence empty",
        "certified_only=true",
        "no db writes",
        "no production writes",
        "no scheduler activation",
        "no backfill",
        "no vendor calls",
        "no ai machine changes",
        "no data repo source changes",
        "no cleanup because row is preserved",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "no token documented",
        "no db url documented",
        "no full idempotency_key documented",
        "credential was exposed",
        "rotate",
        "production monitoring checkpoint",
        "ai machine consumption remains last",
    ]:
        assert needle in text
