from __future__ import annotations

from app.features.earnings.earnings_validator import validate_earnings_observation, validate_earnings_observations
from tests.fixtures.earnings_data import build_earnings_fixture_payloads
from app.features.earnings.earnings_builder import build_earnings_observation


def test_valid_observation_passes() -> None:
    payload = build_earnings_fixture_payloads()["AAPL"]
    row = build_earnings_observation("AAPL", payload, "2026-07-20")
    result = validate_earnings_observation(row)
    assert result.is_valid


def test_invalid_row_fails() -> None:
    result = validate_earnings_observation({"symbol": "", "observation_date": "2026-07-20", "source": "fixture_earnings", "earnings_regime_label": "UNKNOWN"})
    assert not result.is_valid


def test_blank_metadata_fields_fail_when_present() -> None:
    row = {
        "symbol": "AAPL",
        "observation_date": "2026-07-20",
        "source": "fixture_earnings",
        "earnings_regime_label": "MIXED_EARNINGS",
        "source_attribution": "",
        "dataset_version": "",
        "created_at": "",
        "updated_at": "",
    }
    result = validate_earnings_observation(row)
    assert not result.is_valid


def test_duplicate_batch_key_rejected() -> None:
    payload = build_earnings_fixture_payloads()["AAPL"]
    rows = [
        build_earnings_observation("AAPL", payload, "2026-07-20"),
        build_earnings_observation("AAPL", payload, "2026-07-20"),
    ]
    result = validate_earnings_observations(rows)
    assert not result.is_valid

