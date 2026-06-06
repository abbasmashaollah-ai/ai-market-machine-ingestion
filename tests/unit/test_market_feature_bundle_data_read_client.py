from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.clients.data_read_client import (
    DataReadClient,
    DataReadClientConfig,
    HttpResponse,
    MarketFeatureBundleReadResult,
    ResponseMetadata,
)


def _response(status_code: int, payload: object) -> HttpResponse:
    return HttpResponse(metadata=ResponseMetadata(status_code=status_code, elapsed_seconds=0.01), text="{}", json=payload)


def _success_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "universe": "SPY",
        "dataset_version": "production_pilot.v1",
        "schema_version": "market_feature_bundle.v1",
        "validation_status": "PASS",
        "certification_status": "CERTIFIED",
        "coverage_status": "COMPLETE",
        "quality_status": "PASS",
        "missing_data_evidence": [],
        "stale_data_evidence": [],
        "compact_summary": {"example": True},
        "full_bundle_payload": {"example": True},
        "idempotency_key": "abcdef1234567890",
    }
    payload.update(overrides)
    return payload


def test_successful_mocked_response_preserves_bundle_contract() -> None:
    transport = Mock()
    transport.request.return_value = _response(200, _success_payload())
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com/", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("spy")

    metadata = transport.request.call_args[0][0]
    assert metadata.method == "GET"
    assert metadata.url == "https://example.com/internal/read/market-feature-bundle/SPY"
    assert metadata.headers["X-Ops-Internal-Token"] == "secret"
    assert result.evidence_available is True
    assert result.universe == "SPY"
    assert result.dataset_version == "production_pilot.v1"
    assert result.schema_version == "market_feature_bundle.v1"
    assert result.validation_status == "PASS"
    assert result.certification_status == "CERTIFIED"
    assert result.coverage_status == "COMPLETE"
    assert result.quality_status == "PASS"
    assert result.compact_summary == {"example": True}
    assert result.full_bundle_payload == {"example": True}
    assert result.idempotency_key_prefix == "abcdef123456"
    assert not hasattr(result, "idempotency_key")


def test_missing_config_returns_disabled_no_evidence_result() -> None:
    with patch.dict("os.environ", {}, clear=True):
        result = DataReadClient.read_market_feature_bundle_from_environment("SPY")

    assert result.disabled is True
    assert result.evidence_available is False
    assert result.universe == "SPY"


@pytest.mark.parametrize("status_code", [401, 403])
def test_unauthorized_responses_return_no_evidence(status_code: int) -> None:
    transport = Mock()
    transport.request.return_value = _response(status_code, {"error": "unauthorized"})
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("SPY")

    assert result.evidence_available is False
    assert result.unauthorized is True


def test_route_failure_returns_no_evidence() -> None:
    transport = Mock()
    transport.request.return_value = _response(500, {"error": "server"})
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("SPY")

    assert result.evidence_available is False
    assert result.route_failure is True


def test_timeout_returns_no_evidence_without_crash() -> None:
    transport = Mock()
    transport.request.side_effect = RuntimeError("timed out")
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("SPY")

    assert result.evidence_available is False
    assert result.disabled is True


def test_malformed_json_returns_no_evidence() -> None:
    transport = Mock()
    transport.request.return_value = _response(200, ["not-a-dict"])
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("SPY")

    assert result.evidence_available is False


@pytest.mark.parametrize(
    "payload, field",
    [
        (_success_payload(certification_status="UNCERTIFIED"), "certification_status"),
        (_success_payload(validation_status="WARN"), "validation_status"),
        (_success_payload(coverage_status="PARTIAL"), "coverage_status"),
        (_success_payload(quality_status="WARN"), "quality_status"),
        (_success_payload(missing_data_evidence=[{"missing": True}]), "missing_data_evidence"),
        (_success_payload(stale_data_evidence=[{"stale": True}]), "stale_data_evidence"),
        (_success_payload(schema_version="legacy_bundle.v0"), "schema_version"),
    ],
)
def test_consumption_gate_failures_return_no_evidence(payload: dict[str, object], field: str) -> None:
    transport = Mock()
    transport.request.return_value = _response(200, payload)
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("SPY")

    assert result.evidence_available is False
    assert getattr(result, field) in {None, (), "UNCERTIFIED", "WARN", "PARTIAL", "legacy_bundle.v0"}


def test_missing_row_response_is_no_evidence_not_negative_evidence() -> None:
    transport = Mock()
    transport.request.return_value = _response(404, {"error": "not found"})
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("SPY")

    assert result.evidence_available is False
    assert result.route_failure is False
    assert result.unauthorized is False


def test_token_and_url_are_redacted_from_disabled_result_errors() -> None:
    transport = Mock()
    transport.request.side_effect = RuntimeError("https://example.com/secret-token secret")
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_market_feature_bundle("SPY")

    assert "secret" not in (result.error_message or "")
    assert "https://example.com" not in (result.error_message or "")


def test_source_scans_cover_no_vendor_no_db_no_write_behavior() -> None:
    text = Path("app/clients/data_read_client.py").read_text(encoding="utf-8").lower()

    assert "sqlalchemy" not in text
    assert "app.database" not in text
    assert "database_url" not in text
    assert "app.database" not in text
    assert "write(" not in text
    assert "post(" not in text
    assert "put(" not in text
    assert "delete(" not in text
    assert "patch(" not in text
    assert "market_risk" not in text
    assert "market_regime" not in text
    assert "macro_liquidity" not in text
    assert "flows_positioning" not in text


def test_reasoning_modules_are_not_imported_here() -> None:
    text = Path("app/clients/data_read_client.py").read_text(encoding="utf-8")
    assert "from app.features.market_risk" not in text
    assert "from app.features.market_regime" not in text
    assert "from app.features.macro_liquidity" not in text
    assert "from app.features.flows_positioning" not in text


def test_client_repr_does_not_expose_token() -> None:
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"))
    text = repr(client)
    assert "secret" not in text


def test_no_full_idempotency_key_field_is_exposed() -> None:
    result = MarketFeatureBundleReadResult(universe="SPY", evidence_available=True, idempotency_key_prefix="abc123")
    assert not hasattr(result, "idempotency_key")
