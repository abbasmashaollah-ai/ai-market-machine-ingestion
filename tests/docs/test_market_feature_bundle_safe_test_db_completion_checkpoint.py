from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_safe_test_db_completion_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_safe_test_db_completion_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "safe railway test postgres db",
        "0020_market_feature_bundle_snapshots",
        "market_feature_bundle_snapshots",
        "tests/integration/test_market_feature_bundle_safe_test_db_writer.py",
        "3 passed",
        "amm_ingestion_test_database_url",
        "env var removed",
        "idempotency duplicate behavior",
        "grain conflict behavior",
        "cleanup by idempotency_key",
        "no production database_url use",
        "no production writes",
        "no vendor calls",
        "no scheduler activation",
        "no data repo changes",
        "no ai machine changes",
        "app/features remains calculation-only",
        "credential was exposed",
        "rotate, delete, or recreate",
        "ai machine consumption remains last",
    ]:
        assert needle in text

