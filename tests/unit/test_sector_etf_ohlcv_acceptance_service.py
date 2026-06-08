from __future__ import annotations

from app.warehouse.sector_etf_ohlcv_acceptance_service import (
    SECTOR_ETF_UNIVERSE,
    accept_sector_etf_ohlcv_handoff_records,
)


def _base_record(symbol: str = "SPY") -> dict[str, object]:
    return {
        "symbol": symbol,
        "timestamp": "2026-01-15T00:00:00+00:00",
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
        "volume": 1_000_000,
        "timeframe": "1d",
        "adjusted": True,
        "source": "synthetic_local",
        "dataset_version": "synthetic.v1",
        "schema_version": "canonical_ohlcv.v1",
        "validation_status": "PASS",
        "certification_status": "APPROVED_CANDIDATE",
        "lineage_id": "lineage-1",
        "source_file_sha256": "abc123",
        "idempotency_key": "abc123prefix-001",
    }


def test_fixture_only_records_are_rejected() -> None:
    record = dict(_base_record(), certification_status="FIXTURE_ONLY")
    result = accept_sector_etf_ohlcv_handoff_records([record])
    assert result.accepted_count == 0
    assert result.rejected_count == 1
    assert result.validation_status == "FAIL"
    assert result.decisions[0].status == "REJECTED"


def test_approved_candidate_shape_is_accepted_in_dry_run_mode() -> None:
    result = accept_sector_etf_ohlcv_handoff_records([_base_record()], approved_candidate_test_mode=True)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.decisions[0].status == "ACCEPTED"
    assert result.symbols_accepted == ("SPY",)


def test_duplicate_idempotency_handling() -> None:
    record = _base_record()
    result = accept_sector_etf_ohlcv_handoff_records([record, dict(record)])
    assert result.accepted_count == 1
    assert result.duplicate_count == 1
    assert result.decisions[1].status == "DUPLICATE"


def test_missing_required_fields_rejected() -> None:
    record = _base_record()
    del record["source_file_sha256"]
    result = accept_sector_etf_ohlcv_handoff_records([record])
    assert result.rejected_count == 1
    assert result.decisions[0].status == "REJECTED"


def test_invalid_symbol_rejected() -> None:
    result = accept_sector_etf_ohlcv_handoff_records([_base_record(symbol="INVALID")])
    assert result.rejected_count == 1
    assert result.decisions[0].status == "REJECTED"


def test_lineage_and_checksum_prefixes_propagate() -> None:
    result = accept_sector_etf_ohlcv_handoff_records([_base_record()])
    assert result.idempotency_key_prefixes == ("abc123prefix",)
    assert result.decisions[0].idempotency_key_prefix == "abc123prefix"


def test_all_sector_symbols_are_allowed() -> None:
    records = [_base_record(symbol=symbol) for symbol in SECTOR_ETF_UNIVERSE]
    result = accept_sector_etf_ohlcv_handoff_records(records, approved_candidate_test_mode=True)
    assert result.accepted_count == 12
    assert result.rejected_count == 0
