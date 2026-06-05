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
    monkeypatch.setattr(pilot_module, "build_market_feature_bundle_session", lambda database_url: _FakeSession())
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
        "backfill",
        "drop table",
        "truncate",
        "delete(",
    ]:
        assert marker not in source
