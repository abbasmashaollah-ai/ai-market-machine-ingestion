from __future__ import annotations

from app.features.earnings.earnings_builder import build_earnings_observation
from tests.fixtures.earnings_data import build_earnings_fixture_payloads


def test_build_earnings_observation_fields() -> None:
    payload = build_earnings_fixture_payloads()["AAPL"]
    observation = build_earnings_observation("AAPL", payload, "2026-07-20")
    assert observation["symbol"] == "AAPL"
    assert observation["source"] == "fixture_earnings"
    assert observation["source_attribution"] == "manual_fixture"
    assert observation["dataset_version"] == "earnings_dry_run_v1"
    assert observation["created_at"] == "2026-07-20T00:00:00Z"
    assert observation["updated_at"] == "2026-07-20T00:00:00Z"
    assert observation["earnings_regime_label"]
    assert observation["evidence"]["source_payload"]["eps_estimate"] == payload["eps_estimate"]


def test_build_earnings_observation_preserves_metadata() -> None:
    payload = {
        "earnings_date": "2026-07-30",
        "eps_estimate": 1.0,
        "eps_actual": 1.2,
        "source_attribution": "vendor_fixture",
        "dataset_version": "custom_version",
        "created_at": "2026-07-20T09:15:00Z",
        "updated_at": "2026-07-20T10:15:00Z",
    }
    observation = build_earnings_observation("TEST", payload, "2026-07-20")
    assert observation["source_attribution"] == "vendor_fixture"
    assert observation["dataset_version"] == "custom_version"
    assert observation["created_at"] == "2026-07-20T09:15:00Z"
    assert observation["updated_at"] == "2026-07-20T10:15:00Z"


def test_build_earnings_observation_defaults_are_deterministic() -> None:
    payload = build_earnings_fixture_payloads()["MSFT"]
    first = build_earnings_observation("MSFT", payload, "2026-07-20")
    second = build_earnings_observation("MSFT", payload, "2026-07-20")
    assert first["created_at"] == "2026-07-20T00:00:00Z"
    assert first["updated_at"] == "2026-07-20T00:00:00Z"
    assert first["created_at"] == second["created_at"]
    assert first["updated_at"] == second["updated_at"]
