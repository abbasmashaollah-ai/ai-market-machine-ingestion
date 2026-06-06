from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from app.clients.data_read_client import MarketFeatureBundleReadResult
from scripts.run_sector_rotation_market_feature_bundle_shadow_diagnostic import main


def _successful_bundle_result(**overrides: object) -> MarketFeatureBundleReadResult:
    payload = {
        "universe": "SPY",
        "evidence_available": True,
        "dataset_version": "production_pilot.v1",
        "schema_version": "market_feature_bundle.v1",
        "validation_status": "PASS",
        "certification_status": "CERTIFIED",
        "coverage_status": "COMPLETE",
        "quality_status": "PASS",
        "missing_data_evidence": [],
        "stale_data_evidence": [],
        "compact_summary": {"feature_sections_present": {"prices": True, "sector_rotation": True, "market_risk": True, "market_regime": True, "macro_liquidity": True, "flows_positioning": True}},
        "full_bundle_payload": {"ok": True},
        "idempotency_key_prefix": "abcdef123456",
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def test_without_enable_shadow_exits_safely_and_does_not_call_data_api(monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.run_sector_rotation_market_feature_bundle_shadow_diagnostic.DataReadClient.from_environment",
        classmethod(lambda cls, http_client=None: (_ for _ in ()).throw(AssertionError("Data API should not be called without --enable-shadow"))),
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main([])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 0
    assert payload["shadow_enabled"] is False
    assert payload["comparison_status"] == "skipped"
    assert payload["data_api_authoritative"] is False
    assert payload["primary_output_changed"] is False
    assert payload["no_capital_impact"] is True
    assert payload["no_portfolio_changes"] is True
    assert payload["no_user_facing_recommendation"] is True


def test_enable_shadow_with_mocked_success_returns_diagnostic_report(monkeypatch) -> None:
    shadow_client = Mock()
    shadow_client.get_market_feature_bundle.return_value = _successful_bundle_result()
    monkeypatch.setattr(
        "scripts.run_sector_rotation_market_feature_bundle_shadow_diagnostic.DataReadClient.from_environment",
        classmethod(lambda cls, http_client=None: shadow_client),
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--enable-shadow"])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 0
    assert payload["shadow_enabled"] is True
    assert payload["universe"] == "SPY"
    assert payload["data_api_authoritative"] is False
    assert payload["primary_output_changed"] is False
    assert payload["evidence_available"] is True
    assert payload["dataset_version"] == "production_pilot.v1"
    assert payload["schema_version"] == "market_feature_bundle.v1"
    assert payload["certification_status"] == "CERTIFIED"
    assert payload["validation_status"] == "PASS"
    assert payload["coverage_status"] == "COMPLETE"
    assert payload["quality_status"] == "PASS"
    assert payload["comparison_status"] == "matched"
    assert payload["warnings_count"] == len(payload["warnings"])
    assert payload["differences_count"] == len(payload["differences"])
    assert payload["primary_output"]["accepted_observation_count"] == 11
    assert payload["primary_output"]["accepted_summary_count"] == 1
    assert payload["no_capital_impact"] is True
    assert payload["no_portfolio_changes"] is True
    assert payload["no_user_facing_recommendation"] is True


def test_missing_config_returns_skipped_no_evidence(monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.run_sector_rotation_market_feature_bundle_shadow_diagnostic.DataReadClient.from_environment",
        classmethod(lambda cls, http_client=None: None),
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--enable-shadow"])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 0
    assert payload["shadow_enabled"] is True
    assert payload["comparison_status"] == "skipped"
    assert payload["no_evidence_reason"] == "missing_configuration"
    assert payload["evidence_available"] is False


def test_mocked_no_evidence_response_returns_skipped_comparison(monkeypatch) -> None:
    shadow_client = Mock()
    shadow_client.get_market_feature_bundle.return_value = _successful_bundle_result(
        evidence_available=False,
        validation_status=None,
        certification_status=None,
        coverage_status=None,
        quality_status=None,
        compact_summary=None,
    )
    monkeypatch.setattr(
        "scripts.run_sector_rotation_market_feature_bundle_shadow_diagnostic.DataReadClient.from_environment",
        classmethod(lambda cls, http_client=None: shadow_client),
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--enable-shadow"])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 0
    assert payload["comparison_status"] == "skipped"
    assert payload["evidence_available"] is False
    assert payload["no_evidence_reason"] == "no_evidence"
    assert payload["primary_output_changed"] is False


def test_mocked_route_failure_returns_no_behavior_change(monkeypatch) -> None:
    shadow_client = Mock()
    shadow_client.get_market_feature_bundle.return_value = _successful_bundle_result(
        evidence_available=False,
        route_failure=True,
    )
    monkeypatch.setattr(
        "scripts.run_sector_rotation_market_feature_bundle_shadow_diagnostic.DataReadClient.from_environment",
        classmethod(lambda cls, http_client=None: shadow_client),
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--enable-shadow"])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 0
    assert payload["comparison_status"] == "skipped"
    assert payload["no_evidence_reason"] == "route_failure"
    assert payload["primary_output_changed"] is False


def test_script_source_has_no_db_vendor_write_or_decision_logic() -> None:
    text = Path("scripts/run_sector_rotation_market_feature_bundle_shadow_diagnostic.py").read_text(encoding="utf-8").lower()
    assert "sqlalchemy" not in text
    assert "app.database" not in text
    assert "vendor" not in text
    assert "post(" not in text
    assert "put(" not in text
    assert "delete(" not in text
    assert "write_text(" not in text
    assert "commit(" not in text
    assert "judge posture" not in text
    assert "trading decision" not in text
    assert "risk posture" not in text
    assert "portfolio allocation" not in text
    assert "capital logic" not in text
    assert "execution logic" not in text
    assert "token-123" not in text
    assert "database_url" not in text
    assert "full idempotency_key" not in text


def test_tests_do_not_require_live_api_calls() -> None:
    text = Path("scripts/run_sector_rotation_market_feature_bundle_shadow_diagnostic.py").read_text(encoding="utf-8").lower()
    assert "requests.get" not in text
    assert "urllib3" not in text
    assert "httpx" not in text
    assert "aiohttp" not in text
