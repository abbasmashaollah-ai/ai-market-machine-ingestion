from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_producer_payload import build_market_feature_bundle_producer_payload
from app.writers.market_feature_bundle_db_adapter import (
    _row_from_payload,
    build_market_feature_bundle_session,
    redact_database_url,
    validate_safe_test_database_url,
)
from app.writers.market_feature_bundle_writer import MarketFeatureBundleWriter


SAFE_DB_URL = os.getenv("AMM_INGESTION_TEST_DATABASE_URL") or os.getenv("AMM_TEST_DATABASE_URL")


def _skip_if_no_safe_db() -> None:
    if not SAFE_DB_URL:
        pytest.skip("safe test DB URL is not configured")


def _payload(dataset_version: str, idempotency_key_suffix: str = "") -> dict:
    bundle = run_market_feature_bundle_dry_run(observation_date="2026-01-15", timestamp="2026-01-15T12:00:00Z")
    payload = build_market_feature_bundle_producer_payload(
        bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
        dataset_version=dataset_version,
    )
    if idempotency_key_suffix:
        payload["idempotency_key"] = f"{payload['idempotency_key']}{idempotency_key_suffix}"
    return payload


def test_safe_test_db_writer_round_trip_and_conflict_and_cleanup() -> None:
    _skip_if_no_safe_db()
    validate_safe_test_database_url(SAFE_DB_URL or "")
    session = build_market_feature_bundle_session(SAFE_DB_URL or "")
    writer = MarketFeatureBundleWriter(session, dry_run=False)

    payload = _payload("test.safe.v1")
    result = writer.write_payload(payload)
    assert result["write_status"] == "WRITE_ACCEPTED"

    same_result = writer.write_payload(payload)
    assert same_result["write_status"] in {"IDEMPOTENT_NOOP", "ALREADY_EXISTS"}

    conflict_payload = _payload("test.safe.v1", idempotency_key_suffix="-conflict")
    conflict_result = writer.write_payload(conflict_payload)
    assert conflict_result["write_status"] == "CONFLICT"

    row = session.existing_by_idempotency_key(payload["idempotency_key"])
    assert row is not None
    assert row["idempotency_key"] == payload["idempotency_key"]

    deleted = session.cleanup_by_idempotency_key(payload["idempotency_key"])
    assert deleted >= 1
    assert session.existing_by_idempotency_key(payload["idempotency_key"]) is None


def test_safe_test_db_url_redaction_and_rejection() -> None:
    assert "<redacted>" in redact_database_url("postgresql://user:secret@localhost/db")
    with pytest.raises(ValueError):
        validate_safe_test_database_url("")


def test_adapter_row_mapping_backfills_missing_generated_at() -> None:
    row = _row_from_payload({"observation_date": "2026-01-15", "generated_at": None})

    assert row["generated_at"] is not None
    assert isinstance(row["generated_at"], str)
    assert row["observation_date"] == "2026-01-15"


def test_adapter_source_has_no_forbidden_markers() -> None:
    source = Path("app/writers/market_feature_bundle_db_adapter.py").read_text(encoding="utf-8").lower()
    for marker in [
        "database_url=",
        "read database_url",
        "os.getenv(\"database_url\")",
        "os.getenv('database_url')",
        "drop table",
        "truncate",
        "create_all",
        "alembic",
        "scheduler",
        "vendor",
        "requests",
        "httpx",
        "app.database",
    ]:
        assert marker not in source
