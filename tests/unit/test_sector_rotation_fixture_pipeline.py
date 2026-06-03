from datetime import datetime, timezone

from tests.fixtures.sector_rotation_ohlcv import (
    build_all_sector_rotation_ohlcv_payloads,
    build_fake_data_read_client_for_sector_rotation,
    build_sector_rotation_ohlcv_payload,
)
from app.features.sector_rotation.sector_rotation_reader import run_sector_rotation_certified_ohlcv_dry_run
from app.features.sector_rotation.sector_universe import get_sector_symbols


def test_fixture_payloads_support_full_sector_rotation_pipeline() -> None:
    client = build_fake_data_read_client_for_sector_rotation()
    result = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    assert len(result.dry_run_result.observation_rows) == 11
    assert result.dry_run_result.accepted_observation_count == 11
    assert result.dry_run_result.accepted_summary_count == 1
    assert result.dry_run_result.writer_result.accepted_observation_count == 11
    assert result.dry_run_result.writer_result.accepted_summary_count == 1
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert result.dry_run_result.summary_row["descriptive_rotation_state"]
    assert result.dry_run_result.summary_row["top_sector_symbols"]
    assert result.dry_run_result.summary_row["bottom_sector_symbols"]
    assert [row["sector_symbol"] for row in result.dry_run_result.observation_rows] == list(get_sector_symbols())
    assert len(client.calls) == len(get_sector_symbols()) + 1


def test_fixture_payloads_are_production_shaped_and_complete() -> None:
    payload = build_sector_rotation_ohlcv_payload("XLK")
    assert payload["symbol"] == "XLK"
    assert payload["coverage_status"] == "COMPLETE"
    assert payload["quality_status"] == "PASS"
    assert payload["certification_status"] == "CERTIFIED"
    assert len(payload["historical_ohlcv"]) >= 65
    first_row = payload["historical_ohlcv"][0]
    assert first_row["symbol"] == "XLK"
    assert first_row["source"] == "FIXTURE"
    assert first_row["timeframe"] == "1d"
    assert first_row["adjusted"] is False


def test_fixture_payloads_cover_all_required_symbols() -> None:
    payloads = build_all_sector_rotation_ohlcv_payloads()
    assert set(payloads) == set(get_sector_symbols()) | {"SPY"}
    assert all(len(payload["historical_ohlcv"]) >= 65 for payload in payloads.values())


def test_missing_sector_payload_surfaces_clean_warning() -> None:
    payloads = build_all_sector_rotation_ohlcv_payloads()
    payloads.pop("XLK")

    class MissingSectorClient:
        def __init__(self, payload_by_symbol):
            self.payload_by_symbol = payload_by_symbol
            self.calls: list[str] = []

        def get_symbol_ohlcv_history(self, symbol, start_date=None, end_date=None, limit=None, order="asc"):
            self.calls.append(str(symbol).upper())
            if str(symbol).upper() not in self.payload_by_symbol:
                return {"symbol": str(symbol).upper(), "historical_ohlcv": [], "warnings": ["missing"]}
            return self.payload_by_symbol[str(symbol).upper()]

    client = MissingSectorClient(payloads)
    result = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    assert any("missing_required_symbols:XLK" in warning for warning in result.warnings)
