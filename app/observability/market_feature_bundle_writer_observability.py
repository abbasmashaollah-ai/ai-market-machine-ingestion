from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _idempotency_prefix(value: object, prefix_length: int = 12) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return value[:prefix_length]


def build_market_feature_bundle_writer_observability_event(
    writer_result: dict,
    *,
    redacted_target: str | None = None,
) -> dict:
    payload_summary = writer_result.get("payload_summary")
    grain = writer_result.get("grain") if isinstance(writer_result.get("grain"), dict) else {}
    validation_errors = writer_result.get("validation_errors")
    error_type = None
    if isinstance(validation_errors, list) and validation_errors:
        first_error = validation_errors[0]
        if isinstance(first_error, dict):
            error_type = first_error.get("field_name") or first_error.get("message")
    if writer_result.get("write_status") == "WRITE_FAILED" and error_type is None:
        error_type = "WRITE_FAILED"

    return {
        "event_type": "market_feature_bundle_writer_result",
        "writer_type": writer_result.get("writer_type"),
        "target_repo": writer_result.get("target_repo"),
        "target_table": writer_result.get("target_table"),
        "dry_run": writer_result.get("dry_run"),
        "write_status": writer_result.get("write_status"),
        "conflict_status": writer_result.get("conflict_status"),
        "would_write": writer_result.get("would_write"),
        "idempotency_key_prefix": _idempotency_prefix(writer_result.get("idempotency_key")),
        "universe": grain.get("universe"),
        "schema_version": grain.get("schema_version"),
        "dataset_version": grain.get("dataset_version"),
        "validation_status": None if not isinstance(payload_summary, dict) else payload_summary.get("validation_status"),
        "certification_status": None if not isinstance(payload_summary, dict) else payload_summary.get("certification_status"),
        "total_warnings": None if not isinstance(payload_summary, dict) else payload_summary.get("total_warnings"),
        "redacted_target": redacted_target,
        "error_type": error_type,
        "observed_at": _utc_now_iso(),
    }


def summarize_market_feature_bundle_writer_results(writer_results: list[dict]) -> dict:
    if not writer_results:
        return {
            "write_attempt_count": 0,
            "write_success_count": 0,
            "write_failure_count": 0,
            "idempotent_noop_count": 0,
            "conflict_count": 0,
            "rollback_count": 0,
            "dry_run_count": 0,
            "would_write_count": 0,
            "last_successful_write_at": None,
            "last_failed_write_at": None,
            "last_written_dataset_version": None,
            "last_written_universe": None,
            "status_distribution": {},
        }

    status_distribution = Counter()
    write_success_count = 0
    write_failure_count = 0
    idempotent_noop_count = 0
    conflict_count = 0
    rollback_count = 0
    dry_run_count = 0
    would_write_count = 0
    last_successful_write_at = None
    last_failed_write_at = None
    last_written_dataset_version = None
    last_written_universe = None

    for writer_result in writer_results:
        status = str(writer_result.get("write_status") or "UNKNOWN")
        status_distribution[status] += 1
        if writer_result.get("dry_run"):
            dry_run_count += 1
        if writer_result.get("would_write"):
            would_write_count += 1
        if status in {"WRITE_ACCEPTED", "DRY_RUN_READY"}:
            write_success_count += 1
            last_successful_write_at = writer_result.get("payload_summary", {}).get("observed_at") if isinstance(writer_result.get("payload_summary"), dict) else last_successful_write_at
            summary = writer_result.get("payload_summary")
            if isinstance(summary, dict):
                last_written_dataset_version = summary.get("dataset_version", last_written_dataset_version)
                last_written_universe = summary.get("universe", last_written_universe)
        elif status in {"WRITE_FAILED", "REJECTED"}:
            write_failure_count += 1
            last_failed_write_at = writer_result.get("payload_summary", {}).get("observed_at") if isinstance(writer_result.get("payload_summary"), dict) else last_failed_write_at
            if status == "WRITE_FAILED":
                rollback_count += 1
        elif status == "IDEMPOTENT_NOOP":
            idempotent_noop_count += 1
        elif status == "CONFLICT":
            conflict_count += 1

    return {
        "write_attempt_count": len(writer_results),
        "write_success_count": write_success_count,
        "write_failure_count": write_failure_count,
        "idempotent_noop_count": idempotent_noop_count,
        "conflict_count": conflict_count,
        "rollback_count": rollback_count,
        "dry_run_count": dry_run_count,
        "would_write_count": would_write_count,
        "last_successful_write_at": last_successful_write_at,
        "last_failed_write_at": last_failed_write_at,
        "last_written_dataset_version": last_written_dataset_version,
        "last_written_universe": last_written_universe,
        "status_distribution": dict(status_distribution),
    }
