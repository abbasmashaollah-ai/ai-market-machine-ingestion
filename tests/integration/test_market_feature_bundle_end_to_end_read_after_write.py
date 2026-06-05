from __future__ import annotations

import os
from uuid import uuid4
from urllib.parse import urlparse

import pytest
import requests

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_producer_payload import build_market_feature_bundle_producer_payload
from app.writers.market_feature_bundle_db_adapter import build_market_feature_bundle_session, validate_safe_test_database_url
from app.writers.market_feature_bundle_writer import MarketFeatureBundleWriter


INGESTION_DB_URL = os.getenv("AMM_INGESTION_TEST_DATABASE_URL") or os.getenv("AMM_TEST_DATABASE_URL")
DATA_BASE_URL = os.getenv("AMM_DATA_TEST_BASE_URL") or os.getenv("AI_MARKET_MACHINE_DATA_BASE_URL")
DATA_TOKEN = os.getenv("AMM_DATA_TEST_TOKEN") or os.getenv("OPS_INTERNAL_TOKEN")


def _skip_if_unavailable() -> None:
    if not INGESTION_DB_URL:
        pytest.skip("safe ingestion test DB URL is not configured")
    if not DATA_BASE_URL:
        pytest.skip("data test base URL is not configured")
    if not DATA_TOKEN:
        pytest.skip("data test token is not configured")


def _redacted_host(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or "<unknown>"
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://<redacted>@{host}{port}"


def _build_payload(run_id: str) -> dict:
    bundle = run_market_feature_bundle_dry_run(observation_date="2026-01-15", timestamp="2026-01-15T12:00:00Z")
    payload = build_market_feature_bundle_producer_payload(
        bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
        universe="SPY",
        dataset_version=f"end_to_end.safe.v1.{run_id}",
    )
    payload["source_run_id"] = f"e2e-safe-test-{run_id}"
    return payload


def _extract_market_feature_bundle(body: object) -> dict:
    if not isinstance(body, dict):
        raise AssertionError(f"unexpected response body type: {type(body)!r}")

    snapshot = body.get("market_feature_bundle")
    if isinstance(snapshot, dict):
        return snapshot

    data = body.get("data")
    if isinstance(data, dict):
        nested_snapshot = data.get("market_feature_bundle")
        if isinstance(nested_snapshot, dict):
            return nested_snapshot
        return data

    return body


def test_market_feature_bundle_end_to_end_read_after_write() -> None:
    _skip_if_unavailable()
    validate_safe_test_database_url(INGESTION_DB_URL or "")
    session = build_market_feature_bundle_session(INGESTION_DB_URL or "")
    writer = MarketFeatureBundleWriter(session, dry_run=False)
    run_id = uuid4().hex[:12]
    payload = _build_payload(run_id)
    route_url = f"{DATA_BASE_URL.rstrip('/')}/internal/read/market-feature-bundle/SPY"

    session.cleanup_by_idempotency_key(payload["idempotency_key"])

    primary_failure: BaseException | None = None
    cleanup_failure: BaseException | None = None
    try:
        write_result = writer.write_payload(payload)
        assert write_result["write_status"] in {"WRITE_ACCEPTED", "IDEMPOTENT_NOOP"}
        row = session.existing_by_idempotency_key(payload["idempotency_key"])
        assert row is not None
        assert row["idempotency_key"] == payload["idempotency_key"]

        response = requests.get(
            route_url,
            headers={"X-Ops-Internal-Token": DATA_TOKEN},
            timeout=30,
        )
        assert response.status_code == 200

        market_feature_bundle = _extract_market_feature_bundle(response.json())
        assert market_feature_bundle is not None
        assert market_feature_bundle["idempotency_key"] == payload["idempotency_key"]
        assert market_feature_bundle["universe"] == payload["universe"]
        assert market_feature_bundle["schema_version"] == payload["schema_version"]
        assert market_feature_bundle["dataset_version"] == payload["dataset_version"]
        assert market_feature_bundle["compact_summary"] == payload["compact_summary"]
        assert market_feature_bundle["full_bundle_payload"] == payload["full_bundle_payload"]
        assert market_feature_bundle["validation_status"] == payload["validation_status"]
        assert market_feature_bundle["certification_status"] == payload["certification_status"]
        assert "lineage_refs" in market_feature_bundle
        assert "quality_result_refs" in market_feature_bundle

        after_cleanup = requests.get(
            route_url,
            headers={"X-Ops-Internal-Token": DATA_TOKEN},
            timeout=30,
        )
        assert after_cleanup.status_code == 200
        assert payload["idempotency_key"] not in str(after_cleanup.json())
    except BaseException as exc:
        primary_failure = exc
        raise
    finally:
        try:
            deleted = session.cleanup_by_idempotency_key(payload["idempotency_key"])
            if primary_failure is None:
                assert deleted >= 1
                assert session.existing_by_idempotency_key(payload["idempotency_key"]) is None
            else:
                print(
                    "cleanup-after-primary-failure",
                    {
                        "deleted": deleted,
                        "idempotency_key_prefix": payload["idempotency_key"][:12],
                    },
                )
        except BaseException as cleanup_exc:
            cleanup_failure = cleanup_exc
            if primary_failure is None:
                raise
            print(
                "cleanup-failed-after-primary-failure",
                {
                    "error_type": type(cleanup_exc).__name__,
                    "idempotency_key_prefix": payload["idempotency_key"][:12],
                },
            )
        if primary_failure is None and cleanup_failure is not None:
            raise cleanup_failure


def test_end_to_end_env_is_redacted_only() -> None:
    if INGESTION_DB_URL:
        assert "<redacted>" in _redacted_host(INGESTION_DB_URL)

