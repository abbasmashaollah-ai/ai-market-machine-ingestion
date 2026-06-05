from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_production_writer_activation_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_production_writer_activation_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "production writer activation",
        "explicit user approval",
        "production writes disabled",
        "0020_market_feature_bundle_snapshots",
        "protected data route healthy",
        "safe test db writer validation passed",
        "end-to-end read-after-write verification passed",
        "observability plan exists",
        "exposed test db credential rotated",
        "one controlled write",
        "one universe",
        "spy",
        "cleanup only by `idempotency_key`",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "no scheduler/backfill activation",
        "no vendor live fetch",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio logic",
        "credentials redacted",
        "no secrets in logs",
        "blocked_pending_approval",
        "approved_for_one_row_production_pilot",
        "ai machine consumption remains last",
    ]:
        assert needle in text
