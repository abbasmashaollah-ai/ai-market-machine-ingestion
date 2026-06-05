from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_end_to_end_read_after_write_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_end_to_end_read_after_write_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "end-to-end",
        "read-after-write",
        "market_feature_bundle_snapshots",
        "0020_market_feature_bundle_snapshots",
        "get /internal/read/market-feature-bundle/{universe}",
        "amm_ingestion_test_database_url",
        "amm_test_database_url",
        "database_url",
        "same safe test db",
        "idempotency_key",
        "compact_summary",
        "full_bundle_payload",
        "cleanup by idempotency_key",
        "no production writes",
        "no seed rows",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "no migrations from ingestion repo",
        "no vendor calls",
        "no scheduler activation",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio logic",
        "ai machine consumption remains last",
    ]:
        assert needle in text

