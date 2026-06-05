from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_scheduler_backfill_approval_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_scheduler_backfill_approval_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "scheduler and backfill approval plan",
        "repeated production writes blocked",
        "one production row preserved",
        "production_pilot.v1",
        "certification_status certified",
        "validation_status pass",
        "production route read-back verified",
        "credential rotation verified",
        "explicit user approval",
        "dry-run schedule simulation",
        "dry-run backfill manifest",
        "max one scheduled write per approved interval",
        "idempotency and conflict behavior reviewed",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "no migrations from ingestion repo",
        "no vendor live fetch",
        "no scheduler activation",
        "no backfill execution",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio logic",
        "data repo remains warehouse/read owner",
        "blocked_pending_scheduler_approval",
        "blocked_pending_backfill_approval",
        "approved_for_scheduled_single_universe_writes",
        "approved_for_limited_backfill",
        "blocked_by_monitoring_gap",
        "blocked_by_route_health_gap",
        "ai machine read-consumption contract planning",
        "scheduler/backfill remains blocked until explicit approval",
    ]:
        assert needle in text
