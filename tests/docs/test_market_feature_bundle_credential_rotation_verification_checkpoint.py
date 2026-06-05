from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_credential_rotation_verification_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_credential_rotation_verification_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "credential rotation",
        "protected route verification passed after rotation",
        "preserved production row survived rotation",
        "get /internal/read/market-feature-bundle/spy",
        "snapshot_count 1",
        "market_feature_bundle present",
        "observation_date 2026-01-15",
        "generated_at 2026-06-05t05:35:26.607789",
        "production_pilot.v1",
        "market_feature_bundle.v1",
        "validation_status pass",
        "certification_status certified",
        "coverage_status complete",
        "quality_status pass",
        "missing_data_evidence empty",
        "stale_data_evidence empty",
        "certified_only=true",
        "no db writes",
        "no production writes",
        "no ingestion writer rerun",
        "no scheduler activation",
        "no backfill",
        "no vendor calls",
        "no ai machine changes",
        "no data repo source changes",
        "no cleanup because row remains preserved",
        "no token documented",
        "no db url documented",
        "no password documented",
        "no full idempotency_key documented",
        "credential rotation completed",
        "railway/local secret env vars only",
        "ai machine read-consumption contract remains last",
    ]:
        assert needle in text
