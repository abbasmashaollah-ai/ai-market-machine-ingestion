from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_observability_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_observability_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "market_feature_bundle observability",
        "write_attempt_count",
        "write_success_count",
        "write_failure_count",
        "idempotent_noop_count",
        "conflict_count",
        "rollback_count",
        "last_successful_write_at",
        "validation_status distribution",
        "certification_status distribution",
        "market_feature_bundle_snapshots row count",
        "latest observation_date by universe",
        "protected route success/failure",
        "read-after-write verification result",
        "production writes disabled by default",
        "scheduler disabled by default",
        "cleanup only by `idempotency_key`",
        "credentials redacted",
        "no secrets in logs",
        "feature engines remain calculation-only",
        "writer health panel",
        "latest bundle freshness panel",
        "future grafana",
        "no production writes",
        "no scheduler activation",
        "no vendor calls",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio logic",
        "ai machine consumption remains last",
    ]:
        assert needle in text
