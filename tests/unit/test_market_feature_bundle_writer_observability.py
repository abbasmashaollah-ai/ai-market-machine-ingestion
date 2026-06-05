from __future__ import annotations

from pathlib import Path

from app.observability.market_feature_bundle_writer_observability import (
    build_market_feature_bundle_writer_observability_event,
    summarize_market_feature_bundle_writer_results,
)


def test_writer_observability_event_redacts_idempotency_key_and_preserves_fields() -> None:
    writer_result = {
        "writer_type": "market_feature_bundle_writer",
        "target_repo": "ai-market-machine-data",
        "target_table": "market_feature_bundle_snapshots",
        "dry_run": False,
        "write_status": "WRITE_ACCEPTED",
        "conflict_status": "NONE",
        "would_write": True,
        "idempotency_key": "abc123def456ghi789",
        "grain": {
            "universe": "SPY",
            "schema_version": "market_feature_bundle.v1",
            "dataset_version": "test.safe.v1",
        },
        "payload_summary": {
            "validation_status": "PASS",
            "certification_status": "CERTIFIED",
            "total_warnings": 0,
        },
    }

    event = build_market_feature_bundle_writer_observability_event(
        writer_result,
        redacted_target="postgresql://<redacted>@host/db",
    )

    assert event["event_type"] == "market_feature_bundle_writer_result"
    assert event["write_status"] == "WRITE_ACCEPTED"
    assert event["conflict_status"] == "NONE"
    assert event["would_write"] is True
    assert event["idempotency_key_prefix"] == "abc123def456"
    assert "abc123def456ghi789" not in str(event)
    assert event["universe"] == "SPY"
    assert event["schema_version"] == "market_feature_bundle.v1"
    assert event["dataset_version"] == "test.safe.v1"
    assert event["validation_status"] == "PASS"
    assert event["certification_status"] == "CERTIFIED"
    assert event["redacted_target"] == "postgresql://<redacted>@host/db"
    assert event["error_type"] is None
    assert "observed_at" in event


def test_writer_observability_summary_counts_statuses() -> None:
    results = [
        {
            "write_status": "WRITE_ACCEPTED",
            "dry_run": False,
            "would_write": True,
            "payload_summary": {"observed_at": "2026-01-01T00:00:00Z", "dataset_version": "v1", "universe": "SPY"},
        },
        {
            "write_status": "WRITE_FAILED",
            "dry_run": False,
            "would_write": False,
            "payload_summary": {"observed_at": "2026-01-01T00:01:00Z", "dataset_version": "v2", "universe": "QQQ"},
        },
        {"write_status": "IDEMPOTENT_NOOP", "dry_run": False, "would_write": False, "payload_summary": {}},
        {"write_status": "CONFLICT", "dry_run": False, "would_write": False, "payload_summary": {}},
    ]

    summary = summarize_market_feature_bundle_writer_results(results)

    assert summary["write_attempt_count"] == 4
    assert summary["write_success_count"] == 1
    assert summary["write_failure_count"] == 1
    assert summary["idempotent_noop_count"] == 1
    assert summary["conflict_count"] == 1
    assert summary["rollback_count"] == 1
    assert summary["dry_run_count"] == 0
    assert summary["would_write_count"] == 1
    assert summary["last_successful_write_at"] == "2026-01-01T00:00:00Z"
    assert summary["last_failed_write_at"] == "2026-01-01T00:01:00Z"
    assert summary["last_written_dataset_version"] == "v1"
    assert summary["last_written_universe"] == "SPY"
    assert summary["status_distribution"] == {
        "WRITE_ACCEPTED": 1,
        "WRITE_FAILED": 1,
        "IDEMPOTENT_NOOP": 1,
        "CONFLICT": 1,
    }


def test_writer_observability_summary_handles_empty_list() -> None:
    summary = summarize_market_feature_bundle_writer_results([])

    assert summary["write_attempt_count"] == 0
    assert summary["write_success_count"] == 0
    assert summary["write_failure_count"] == 0
    assert summary["idempotent_noop_count"] == 0
    assert summary["conflict_count"] == 0
    assert summary["rollback_count"] == 0
    assert summary["last_successful_write_at"] is None


def test_observability_module_has_no_forbidden_import_markers() -> None:
    source = Path("app/observability/market_feature_bundle_writer_observability.py").read_text(encoding="utf-8").lower()
    for marker in [
        "sqlalchemy",
        "requests",
        "httpx",
        "aiohttp",
        "scheduler",
        "vendor",
        "app.database",
        "database_url",
        "judge posture",
        "trading decision",
        "risk posture",
        "portfolio logic",
    ]:
        assert marker not in source
