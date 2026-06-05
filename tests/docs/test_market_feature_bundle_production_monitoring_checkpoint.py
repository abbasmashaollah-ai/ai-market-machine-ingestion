from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_production_monitoring_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_production_monitoring_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "production monitoring checkpoint",
        "preserved production row exists",
        "production_pilot.v1",
        "market_feature_bundle.v1",
        "validation_status pass",
        "certification_status certified",
        "coverage_status complete",
        "quality_status pass",
        "source_repo ai-market-machine-ingestion",
        "source_run_id production_pilot.v1",
        "preserve_first_production_row",
        "latest market_feature_bundle row by universe",
        "snapshot_count by universe",
        "latest observation_date by universe",
        "latest generated_at by universe",
        "write_attempt_count",
        "write_success_count",
        "write_failure_count",
        "status_distribution",
        "idempotency_key_prefix only",
        "protected route health",
        "get /internal/read/market-feature-bundle/spy",
        "route status code",
        "certified_only behavior",
        "no scheduler activation yet",
        "no backfill yet",
        "no vendor live fetch",
        "no ai machine changes",
        "no data repo source changes",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "credentials redacted",
        "no secrets in logs",
        "credential was exposed",
        "rotate production db credential",
        "ai machine consumption remains last",
    ]:
        assert needle in text
