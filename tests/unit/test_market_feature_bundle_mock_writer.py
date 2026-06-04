from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_producer_payload import build_market_feature_bundle_producer_payload
from app.features.market_features.market_feature_bundle_mock_writer import (
    MarketFeatureBundleMockWriter,
    build_market_feature_bundle_mock_write_result,
)


def _payload() -> dict:
    bundle = run_market_feature_bundle_dry_run(observation_date="2026-01-15", timestamp="2026-01-15T12:00:00Z")
    return build_market_feature_bundle_producer_payload(
        bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )


def test_valid_producer_payload_returns_mock_write_ready() -> None:
    result = build_market_feature_bundle_mock_write_result(_payload())

    assert result["dry_run_only"] is True
    assert result["write_status"] == "MOCK_WRITE_READY"
    assert result["would_write"] is True


def test_missing_required_field_returns_rejected() -> None:
    payload = _payload()
    payload.pop("compact_summary")

    result = build_market_feature_bundle_mock_write_result(payload)

    assert result["write_status"] == "MOCK_WRITE_REJECTED"
    assert result["validation_errors"]


def test_same_payload_produces_stable_result() -> None:
    payload = _payload()
    result_a = build_market_feature_bundle_mock_write_result(payload)
    result_b = build_market_feature_bundle_mock_write_result(payload)

    assert result_a == result_b


def test_mock_writer_does_not_mutate_input_payload() -> None:
    payload = _payload()
    snapshot = deepcopy(payload)
    writer = MarketFeatureBundleMockWriter()

    writer.write(payload)

    assert payload == snapshot


def test_payload_summary_includes_target_table_and_idempotency_key() -> None:
    result = build_market_feature_bundle_mock_write_result(_payload())

    assert result["payload_summary"]["target_table"] == "market_feature_bundle_snapshots"
    assert result["payload_summary"]["idempotency_key"]


def test_mock_writer_rejects_invalid_source_repo() -> None:
    payload = _payload()
    payload["source_repo"] = "wrong-repo"

    result = build_market_feature_bundle_mock_write_result(payload)

    assert result["write_status"] == "MOCK_WRITE_REJECTED"
    assert any(error["field_name"] == "source_repo" for error in result["validation_errors"])


def test_mock_writer_module_has_no_live_dependencies() -> None:
    source = Path("app/features/market_features/market_feature_bundle_mock_writer.py").read_text(encoding="utf-8").lower()

    for forbidden in [
        "sqlalchemy",
        "app.database",
        "psycopg2",
        "requests",
        "httpx",
        "scheduler",
        "vendor",
        "insert",
        "update",
        "delete",
        "commit",
        "execute",
        "session",
        "engine",
        "database_url",
        "api_key",
    ]:
        assert forbidden not in source


def test_mock_writer_source_has_no_snapshot_language() -> None:
    source = Path("app/features/market_features/market_feature_bundle_mock_writer.py").read_text(encoding="utf-8")
    assert "import FeatureSnapshot" not in source
    assert "import MarketSnapshot" not in source
    assert "featuresnapshot" not in source.lower()
    assert "marketsnapshot" not in source.lower()
