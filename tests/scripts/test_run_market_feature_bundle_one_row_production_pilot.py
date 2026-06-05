from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.run_market_feature_bundle_one_row_production_pilot as pilot_module
from scripts.run_market_feature_bundle_one_row_production_pilot import (
    APPROVAL_ENV,
    APPROVAL_VALUE,
    DATA_BASE_ENV,
    DATA_TOKEN_ENV,
    DATABASE_ENV,
    _build_pilot_report,
    _redact_database_url,
    main,
)


class _FakeSession:
    def __init__(self):
        self.added = None
        self.merged = None
        self.committed = False
        self.rolled_back = False

    def existing_by_idempotency_key(self, key):
        return None

    def existing_by_grain(self, grain):
        return None

    def add(self, payload):
        self.added = payload

    def merge(self, payload):
        self.merged = payload

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class _WriteFailedSession(_FakeSession):
    def commit(self):
        raise RuntimeError(
            "INSERT INTO market_feature_bundle_snapshots parameters: "
            "{'full_bundle_payload': {'token': 'token-123'}, 'idempotency_key': 'placeholder-idempotency-key'} "
            "postgresql://user:secret@host.example.com:5432/railway"
        )


def test_production_pilot_refuses_to_run_without_env_vars(monkeypatch, capsys) -> None:
    for name in (APPROVAL_ENV, DATABASE_ENV, DATA_BASE_ENV, DATA_TOKEN_ENV):
        monkeypatch.delenv(name, raising=False)

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing required production pilot env vars" in captured.err.lower()


def test_production_pilot_refuses_to_run_with_wrong_approval_flag(monkeypatch, capsys) -> None:
    monkeypatch.setenv(APPROVAL_ENV, "NO")
    monkeypatch.setenv(DATABASE_ENV, "postgresql://user:secret@host:5432/db")
    monkeypatch.setenv(DATA_BASE_ENV, "http://127.0.0.1:8001")
    monkeypatch.setenv(DATA_TOKEN_ENV, "token-123")

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "invalid production pilot approval flag" in captured.err.lower()


def test_redacted_database_target_hides_credentials() -> None:
    redacted = _redact_database_url("postgresql://user:secret@host.example.com:5432/railway")
    assert redacted == "postgresql://<redacted>@host.example.com:5432/railway"
    assert "user" not in redacted
    assert "secret" not in redacted


def test_pilot_report_is_safe_and_contains_required_fields(monkeypatch) -> None:
    monkeypatch.setenv(APPROVAL_ENV, APPROVAL_VALUE)
    monkeypatch.setenv(DATABASE_ENV, "postgresql://user:secret@host.example.com:5432/railway")
    monkeypatch.setenv(DATA_BASE_ENV, "http://127.0.0.1:8001")
    monkeypatch.setenv(DATA_TOKEN_ENV, "token-123")
    fake_session = _FakeSession()
    monkeypatch.setattr(pilot_module, "build_market_feature_bundle_session", lambda database_url: fake_session)
    monkeypatch.setattr(
        pilot_module.requests,
        "get",
        lambda url, headers=None, timeout=None: SimpleNamespace(
            status_code=200,
            json=lambda: {
                "market_feature_bundle": {
                    "idempotency_key": "placeholder-idempotency-key",
                    "universe": "SPY",
                    "schema_version": "market_feature_bundle.v1",
                    "dataset_version": "production_pilot.v1",
                    "compact_summary": {"ok": True},
                    "full_bundle_payload": {"ok": True},
                    "validation_status": "PASS",
                    "certification_status": "CERTIFIED",
                    "lineage_refs": [],
                    "quality_result_refs": [],
                }
            },
        ),
    )

    report = _build_pilot_report(observation_date="2026-01-15", timestamp="2026-01-15T18:00:00Z")

    assert report["dry_run"] is False
    assert report["universe"] == "SPY"
    assert report["dataset_version"] == "production_pilot.v1"
    assert report["preserve_policy"] == "PRESERVE_FIRST_PRODUCTION_ROW"
    assert report["idempotency_key_prefix"]
    assert len(report["idempotency_key_prefix"]) <= 12
    assert report["target_table"] == "market_feature_bundle_snapshots"
    assert report["target_repo"] == "ai-market-machine-data"
    assert report["approval_state"] == APPROVAL_VALUE
    assert report["production_target"] == "postgresql://<redacted>@host.example.com:5432/railway"
    assert report["data_route_base_url"] == "http://127.0.0.1:8001"
    assert report["data_route_path"] == "/internal/read/market-feature-bundle/SPY"
    assert report["observability_event"]["idempotency_key_prefix"] == report["idempotency_key_prefix"]
    assert report["observability_summary"]["write_attempt_count"] == 1
    assert report["observability_summary"]["write_success_count"] == 1
    assert report["route_status"] == 200
    assert report["route_read_back"]["idempotency_key"] == "placeholder-idempotency-key"
    assert report["route_read_back"]["universe"] == "SPY"
    assert report["route_read_back"]["dataset_version"] == "production_pilot.v1"
    assert fake_session.added["generated_at"] == "2026-01-15T18:00:00Z"


def test_pilot_report_backfills_generated_at_before_write_attempt(monkeypatch) -> None:
    monkeypatch.setenv(APPROVAL_ENV, APPROVAL_VALUE)
    monkeypatch.setenv(DATABASE_ENV, "postgresql://user:secret@host.example.com:5432/railway")
    monkeypatch.setenv(DATA_BASE_ENV, "http://127.0.0.1:8001")
    monkeypatch.setenv(DATA_TOKEN_ENV, "token-123")
    fake_session = _FakeSession()
    monkeypatch.setattr(pilot_module, "build_market_feature_bundle_session", lambda database_url: fake_session)
    monkeypatch.setattr(
        pilot_module.requests,
        "get",
        lambda url, headers=None, timeout=None: SimpleNamespace(status_code=200, json=lambda: {"market_feature_bundle": {}}),
    )

    _build_pilot_report(observation_date="2026-01-15", timestamp=None)

    assert fake_session.added["generated_at"]
    assert fake_session.added["generated_at"].endswith("+00:00")


def test_pilot_report_returns_structured_failure_without_route_readback(monkeypatch) -> None:
    monkeypatch.setenv(APPROVAL_ENV, APPROVAL_VALUE)
    monkeypatch.setenv(DATABASE_ENV, "postgresql://user:secret@host.example.com:5432/railway")
    monkeypatch.setenv(DATA_BASE_ENV, "http://127.0.0.1:8001")
    monkeypatch.setenv(DATA_TOKEN_ENV, "token-123")
    monkeypatch.setattr(pilot_module, "build_market_feature_bundle_session", lambda database_url: _WriteFailedSession())
    route_called = {"value": False}

    def _unexpected_route_call(*args, **kwargs):
        route_called["value"] = True
        raise AssertionError("route should not be called after WRITE_FAILED")

    monkeypatch.setattr(pilot_module.requests, "get", _unexpected_route_call)

    report = _build_pilot_report(observation_date="2026-01-15", timestamp="2026-01-15T18:00:00Z")

    assert report["pilot_status"] == "WRITE_STOPPED"
    assert report["write_status"] == "WRITE_FAILED"
    assert report["conflict_status"] == "SESSION_FAILURE"
    assert report["scheduler_enabled"] is False
    assert report["backfill_enabled"] is False
    assert report["ai_machine_touched"] is False
    assert report["target_repo"] == "ai-market-machine-data"
    assert report["target_table"] == "market_feature_bundle_snapshots"
    assert report["validation_errors"]
    assert report["error_type"] == "session"
    assert report["error_class"] == "RuntimeError"
    assert report["redacted_target"] == "postgresql://<redacted>@host.example.com:5432/railway"
    assert "INSERT INTO" not in json.dumps(report)
    assert "parameters:" not in json.dumps(report)
    assert "full_bundle_payload" not in json.dumps(report)
    assert "placeholder-idempotency-key" not in json.dumps(report)
    assert "user" not in json.dumps(report)
    assert "secret" not in json.dumps(report)
    assert "token-123" not in json.dumps(report)
    assert len(report["idempotency_key_prefix"]) <= 12
    assert route_called["value"] is False


def test_main_prints_redacted_failure_report(monkeypatch, capsys) -> None:
    monkeypatch.setenv(APPROVAL_ENV, APPROVAL_VALUE)
    monkeypatch.setenv(DATABASE_ENV, "postgresql://user:secret@host.example.com:5432/railway")
    monkeypatch.setenv(DATA_BASE_ENV, "http://127.0.0.1:8001")
    monkeypatch.setenv(DATA_TOKEN_ENV, "token-123")
    monkeypatch.setattr(pilot_module, "build_market_feature_bundle_session", lambda database_url: _WriteFailedSession())
    monkeypatch.setattr(pilot_module.requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("route should not be called")))

    exit_code = main(["--observation-date", "2026-01-15", "--timestamp", "2026-01-15T18:00:00Z"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "INSERT INTO" not in captured.out
    assert "parameters:" not in captured.out
    assert "full_bundle_payload" not in captured.out
    assert "placeholder-idempotency-key" not in captured.out
    assert "user" not in captured.out
    assert "secret" not in captured.out
    assert "token-123" not in captured.out


def test_script_source_has_no_forbidden_markers() -> None:
    source = Path("scripts/run_market_feature_bundle_one_row_production_pilot.py").read_text(encoding="utf-8").lower()
    for marker in [
        "sqlalchemy",
        "app.database",
        "postgresql://",
        "token-123",
        "secret",
        "httpx",
        "aiohttp",
        "alembic",
        "migration",
        "vendor",
        "drop table",
        "truncate",
        "delete(",
    ]:
        assert marker not in source
