from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_one_row_production_pilot_checklist_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_one_row_production_pilot_checklist.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "one-row production pilot",
        "production writes blocked",
        "0020_market_feature_bundle_snapshots",
        "protected data route is healthy",
        "safe test db writer validation passed",
        "end-to-end read-after-write verification passed",
        "observability helpers exist",
        "exposed test db credential has been rotated",
        "one universe only",
        "spy",
        "one dataset_version",
        "one controlled market_feature_bundle row",
        "dry_run=true",
        "observability event",
        "market_feature_bundle_snapshots",
        "explicit user approval",
        "no full db url printed",
        "no secrets in logs",
        "get /internal/read/market-feature-bundle/spy",
        "idempotency_key",
        "compact_summary",
        "full_bundle_payload",
        "validation_status",
        "certification_status",
        "lineage_refs",
        "quality_result_refs",
        "cleanup only by `idempotency_key`",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "no scheduler activation",
        "no backfill",
        "no vendor live fetch",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio logic",
        "blocked_pending_approval",
        "approved_for_one_row_production_pilot",
        "ai machine consumption remains last",
    ]:
        assert needle in text
