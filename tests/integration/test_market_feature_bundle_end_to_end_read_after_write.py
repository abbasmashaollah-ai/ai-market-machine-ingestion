from __future__ import annotations

import os
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


def _build_payload() -> dict:
    bundle = run_market_feature_bundle_dry_run(observation_date="2026-01-15", timestamp="2026-01-15T12:00:00Z")
    payload = build_market_feature_bundle_producer_payload(
        bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
        universe="SPY",
        dataset_version="end_to_end.safe.v1",
    )
    payload["source_run_id"] = "e2e-safe-test"
    return payload


def test_market_feature_bundle_end_to_end_read_after_write() -> None:
    _skip_if_unavailable()
    validate_safe_test_database_url(INGESTION_DB_URL or "")
    session = build_market_feature_bundle_session(INGESTION_DB_URL or "")
    writer = MarketFeatureBundleWriter(session, dry_run=False)
    payload = _build_payload()

    write_result = writer.write_payload(payload)
    assert write_result["write_status"] == "WRITE_ACCEPTED"

    row = session.existing_by_idempotency_key(payload["idempotency_key"])
    assert row is not None

    route_url = f"{DATA_BASE_URL.rstrip('/')}/internal/read/market-feature-bundle/SPY"
    response = requests.get(
        route_url,
        headers={"X-Ops-Internal-Token": DATA_TOKEN},
        timeout=30,
    )
    assert response.status_code == 200

    body = response.json()
    market_feature_bundle = body.get("market_feature_bundle") or body.get("data") or body
    assert market_feature_bundle is not None
    assert payload["idempotency_key"] in str(market_feature_bundle)
    assert "compact_summary" in str(market_feature_bundle)
    assert "full_bundle_payload" in str(market_feature_bundle)
    assert str(payload["validation_status"]) in str(market_feature_bundle)
    assert str(payload["certification_status"]) in str(market_feature_bundle)

    deleted = session.cleanup_by_idempotency_key(payload["idempotency_key"])
    assert deleted >= 1
    assert session.existing_by_idempotency_key(payload["idempotency_key"]) is None

    after_cleanup = requests.get(
        route_url,
        headers={"X-Ops-Internal-Token": DATA_TOKEN},
        timeout=30,
    )
    assert after_cleanup.status_code == 200
    assert payload["idempotency_key"] not in str(after_cleanup.json())


def test_end_to_end_env_is_redacted_only() -> None:
    if INGESTION_DB_URL:
        assert "<redacted>" in _redacted_host(INGESTION_DB_URL)

