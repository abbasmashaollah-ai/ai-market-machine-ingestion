from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_safe_test_db_integration_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_safe_test_db_integration_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "stage e.2",
        "safe test db",
        "amm_test_database_url",
        "amm_ingestion_test_database_url",
        "market_feature_bundle_snapshots",
        "ai-market-machine-data",
        "no schema changes from ingestion repo",
        "dry_run=false only against safe test db",
        "idempotency duplicate behavior",
        "grain conflict behavior",
        "cleanup test row by idempotency_key only",
        "no production writes",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "no migrations from ingestion repo",
        "app/features remains calculation-only",
        "app/writers/market_feature_bundle_db_adapter.py",
        "explicit user approval",
        "target db confirmed migrated to 0020",
        "no db writes",
        "no vendor calls",
        "no scheduler activation",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio logic",
    ]:
        assert needle in text

